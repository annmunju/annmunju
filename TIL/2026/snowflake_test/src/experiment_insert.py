import os
import time
import datetime as dt
import argparse
import logging

from experiment_common import (
    connect,
    now_floor_to_window,
    generate_metrics,
    generate_logs,
    get_query_stats,
    logger,
    LOG_DIR,
    TMP_DIR,
    ITERATIONS,
    WINDOW_SECONDS,
    METRIC_ROWS_PER_WINDOW,
    LOG_ROWS_PER_WINDOW,
)

import uuid


def parse_args():
    parser = argparse.ArgumentParser(description="Snowflake INSERT experiment")
    parser.add_argument("--iterations", type=int, default=None, help="Number of 2-minute windows to run")
    parser.add_argument("--window-seconds", type=int, default=None, help="Window size in seconds (default 120)")
    parser.add_argument("--metric-rows-per-window", type=int, default=None, help="Metric rows per window")
    parser.add_argument("--log-rows-per-window", type=int, default=None, help="Log rows per window")
    return parser.parse_args()


# -------------------------
# Load approach: batch INSERT
# -------------------------
def load_metrics_insert(conn, df, table: str):
    cur = conn.cursor()
    try:
        # Use executemany for bulk insert
        sql = f"""
            INSERT INTO {table} (window_start, window_end, source, metric_name, value, labels)
            SELECT
              TO_TIMESTAMP_NTZ(v.$1),
              TO_TIMESTAMP_NTZ(v.$2),
              v.$3,
              v.$4,
              TO_DOUBLE(v.$5),
              PARSE_JSON(v.$6)
            FROM VALUES (%s, %s, %s, %s, %s, %s) v
        """
        df2 = df.copy()
        df2["window_start"] = df2["window_start"].astype(str)
        df2["window_end"] = df2["window_end"].astype(str)
        data = list(df2.itertuples(index=False, name=None))
        cur.executemany(sql, data)
    finally:
        cur.close()


def load_logs_insert(conn, df, table: str):
    cur = conn.cursor()
    try:
        sql = f"""
            INSERT INTO {table} (window_start, window_end, source, service, level, message, payload)
            SELECT
              TO_TIMESTAMP_NTZ(v.$1),
              TO_TIMESTAMP_NTZ(v.$2),
              v.$3,
              v.$4,
              v.$5,
              v.$6,
              PARSE_JSON(v.$7)
            FROM VALUES (%s, %s, %s, %s, %s, %s, %s) v
        """
        df2 = df.copy()
        df2["window_start"] = df2["window_start"].astype(str)
        df2["window_end"] = df2["window_end"].astype(str)
        data = list(df2.itertuples(index=False, name=None))
        cur.executemany(sql, data)
    finally:
        cur.close()


def main():
    args = parse_args()
    iterations = args.iterations if args.iterations is not None else ITERATIONS
    window_seconds = args.window_seconds if args.window_seconds is not None else WINDOW_SECONDS
    metric_rows_per_window = args.metric_rows_per_window if args.metric_rows_per_window is not None else METRIC_ROWS_PER_WINDOW
    log_rows_per_window = args.log_rows_per_window if args.log_rows_per_window is not None else LOG_ROWS_PER_WINDOW

    conn = connect()
    exp_id = str(uuid.uuid4())
    insert_run_id = f"{exp_id}-insert"

    # Add per-run file logging
    run_log_path = os.path.join(LOG_DIR, f"experiment_{exp_id}_insert.log")
    fh = logging.FileHandler(run_log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    logger.info(f"[LOG] file={run_log_path}")

    logger.info(f"[RUN] exp_id={exp_id}")
    logger.info(f"[RUN] insert_run_id={insert_run_id}")
    logger.info(f"[PARAMS] iterations={iterations}, window_seconds={window_seconds}, metric_rows_per_window={metric_rows_per_window}, log_rows_per_window={log_rows_per_window}")

    # Clear tables to start clean (INSERT tables only)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE METRICS_INSERT")
    cur.execute("TRUNCATE TABLE LOGS_INSERT")
    cur.close()

    base = now_floor_to_window(dt.datetime.utcnow(), window_seconds)

    insert_start_ts = dt.datetime.utcnow()
    logger.info(f"[INSERT] start_ts={insert_start_ts.isoformat()}")

    cur = conn.cursor()
    cur.execute(f"ALTER SESSION SET QUERY_TAG = '{insert_run_id}'")
    cur.close()

    # -------------------------
    # batch INSERT
    # -------------------------
    t0 = time.time()
    for i in range(iterations):
        ws = base + dt.timedelta(seconds=i * window_seconds)
        we = ws + dt.timedelta(seconds=window_seconds)

        m = generate_metrics(ws, we, metric_rows_per_window)
        l = generate_logs(ws, we, log_rows_per_window)

        load_metrics_insert(conn, m, "METRICS_INSERT")
        load_logs_insert(conn, l, "LOGS_INSERT")

        logger.info(f"[INSERT] window {i+1}/{iterations} done")
    insert_sec = time.time() - t0
    logger.info(f"[INSERT] total_sec={insert_sec:.1f}")

    insert_end_ts = dt.datetime.utcnow()
    logger.info(f"[INSERT] end_ts={insert_end_ts.isoformat()}")

    # Basic sanity check
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM METRICS_INSERT")
    mi = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM LOGS_INSERT")
    li = cur.fetchone()[0]
    cur.close()

    logger.info(f"[ROWS] metrics_insert={mi}, logs_insert={li}")

    logger.info("\n=== EXPERIMENT TIME SUMMARY (UTC) ===")
    logger.info(f"INSERT: {insert_start_ts.isoformat()}  ->  {insert_end_ts.isoformat()}")

    # Query stats snapshot (last 240 minutes)
    dfq = get_query_stats(conn, since_minutes=240)
    out_path = os.path.join(TMP_DIR, f"query_history_{exp_id}_insert.csv")
    dfq.to_csv(out_path, index=False)
    logger.info(f"[QUERY_HISTORY] saved to {out_path}")

    conn.close()


if __name__ == "__main__":
    main()

