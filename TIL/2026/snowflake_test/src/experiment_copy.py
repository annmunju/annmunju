import os
import json
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
    parser = argparse.ArgumentParser(description="Snowflake COPY experiment")
    parser.add_argument("--iterations", type=int, default=None, help="Number of 2-minute windows to run")
    parser.add_argument("--window-seconds", type=int, default=None, help="Window size in seconds (default 120)")
    parser.add_argument("--metric-rows-per-window", type=int, default=None, help="Metric rows per window")
    parser.add_argument("--log-rows-per-window", type=int, default=None, help="Log rows per window")
    return parser.parse_args()


# -------------------------
# Load approach: PUT + COPY INTO (internal stage)
# -------------------------
def write_metrics_csv(df, path: str):
    # labels_json -> keep as string, parse_json in COPY with transform
    df2 = df.copy()
    df2.to_csv(path, index=False)


def write_logs_jsonl(df, path: str):
    # JSON Lines file
    with open(path, "w", encoding="utf-8") as f:
        for row in df.itertuples(index=False):
            obj = {
                "window_start": str(row.window_start),
                "window_end": str(row.window_end),
                "source": row.source,
                "service": row.service,
                "level": row.level,
                "message": row.message,
                "payload": json.loads(row.payload_json),
            }
            f.write(json.dumps(obj) + "\n")


def put_to_stage(conn, local_path: str, stage_path: str):
    cur = conn.cursor()
    try:
        # auto_compress = TRUE keeps storage small
        cur.execute(f"PUT file://{local_path} @{stage_path} AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        return cur.fetchall()
    finally:
        cur.close()


def copy_metrics_from_stage(conn, stage_file: str, table: str):
    cur = conn.cursor()
    try:
        # CSV columns: window_start, window_end, source, metric_name, value, labels_json
        sql = f"""
        COPY INTO {table} (window_start, window_end, source, metric_name, value, labels)
        FROM (
          SELECT
            TO_TIMESTAMP_NTZ(t.$1),
            TO_TIMESTAMP_NTZ(t.$2),
            t.$3,
            t.$4,
            TO_DOUBLE(t.$5),
            PARSE_JSON(t.$6)
          FROM @{stage_file} (FILE_FORMAT => FF_METRICS_CSV) t
        )
        PURGE = TRUE
        """
        cur.execute(sql)
        return cur.fetchall()
    finally:
        cur.close()


def copy_logs_from_stage(conn, stage_file: str, table: str):
    cur = conn.cursor()
    try:
        # JSON lines -> each line is a JSON object
        sql = f"""
        COPY INTO {table}
        FROM (
          SELECT
            TO_TIMESTAMP_NTZ($1:window_start::string),
            TO_TIMESTAMP_NTZ($1:window_end::string),
            $1:source::string,
            $1:service::string,
            $1:level::string,
            $1:message::string,
            $1:payload
          FROM @{stage_file} (FILE_FORMAT => FF_LOGS_JSON)
        )
        PURGE = TRUE
        """
        cur.execute(sql)
        return cur.fetchall()
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
    copy_run_id = f"{exp_id}-copy"

    # Add per-run file logging
    run_log_path = os.path.join(LOG_DIR, f"experiment_{exp_id}_copy.log")
    fh = logging.FileHandler(run_log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    logger.info(f"[LOG] file={run_log_path}")

    logger.info(f"[RUN] exp_id={exp_id}")
    logger.info(f"[RUN] copy_run_id={copy_run_id}")
    logger.info(f"[PARAMS] iterations={iterations}, window_seconds={window_seconds}, metric_rows_per_window={metric_rows_per_window}, log_rows_per_window={log_rows_per_window}")

    # Clear tables to start clean (COPY tables only)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE METRICS_COPY")
    cur.execute("TRUNCATE TABLE LOGS_COPY")
    cur.close()

    base = now_floor_to_window(dt.datetime.utcnow(), window_seconds)

    copy_start_ts = dt.datetime.utcnow()
    logger.info(f"[COPY] start_ts={copy_start_ts.isoformat()}")

    cur = conn.cursor()
    cur.execute(f"ALTER SESSION SET QUERY_TAG = '{copy_run_id}'")
    cur.close()

    # -------------------------
    # PUT + COPY INTO
    # -------------------------
    t1 = time.time()
    for i in range(iterations):
        ws = base + dt.timedelta(seconds=i * window_seconds)
        we = ws + dt.timedelta(seconds=window_seconds)

        m = generate_metrics(ws, we, metric_rows_per_window)
        l = generate_logs(ws, we, log_rows_per_window)

        metrics_file = os.path.join(TMP_DIR, f"metrics_{i}.csv")
        logs_file = os.path.join(TMP_DIR, f"logs_{i}.jsonl")

        write_metrics_csv(m, metrics_file)
        write_logs_jsonl(l, logs_file)

        # Put to internal stage under a folder per run
        stage_metrics = f"OBS_EXP_STAGE/{copy_run_id}/metrics/"
        stage_logs = f"OBS_EXP_STAGE/{copy_run_id}/logs/"

        put_to_stage(conn, metrics_file, stage_metrics)
        put_to_stage(conn, logs_file, stage_logs)

        # Copy from stage (use pattern by pointing to folder - Snowflake will pick the file)
        copy_metrics_from_stage(conn, f"OBS_EXP_STAGE/{copy_run_id}/metrics", "METRICS_COPY")
        copy_logs_from_stage(conn, f"OBS_EXP_STAGE/{copy_run_id}/logs", "LOGS_COPY")

        logger.info(f"[COPY] window {i+1}/{iterations} done")
    copy_sec = time.time() - t1
    logger.info(f"[COPY] total_sec={copy_sec:.1f}")

    copy_end_ts = dt.datetime.utcnow()
    logger.info(f"[COPY] end_ts={copy_end_ts.isoformat()}")

    # Basic sanity check
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM METRICS_COPY")
    mc = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM LOGS_COPY")
    lc = cur.fetchone()[0]
    cur.close()

    logger.info(f"[ROWS] metrics_copy={mc}, logs_copy={lc}")

    logger.info("\n=== EXPERIMENT TIME SUMMARY (UTC) ===")
    logger.info(f"COPY  : {copy_start_ts.isoformat()}  ->  {copy_end_ts.isoformat()}")

    # Query stats snapshot (last 240 minutes)
    dfq = get_query_stats(conn, since_minutes=240)
    out_path = os.path.join(TMP_DIR, f"query_history_{exp_id}_copy.csv")
    dfq.to_csv(out_path, index=False)
    logger.info(f"[QUERY_HISTORY] saved to {out_path}")

    conn.close()


if __name__ == "__main__":
    main()
