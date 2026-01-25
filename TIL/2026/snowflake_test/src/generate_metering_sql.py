import os
import re
import glob
from datetime import datetime, timezone
from typing import List, Optional, Tuple

# 프로젝트 루트 경로 (src/ 의 상위 디렉토리)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
OUT_DIR = os.path.join(PROJECT_ROOT, "tmp", "obs_exp")
os.makedirs(OUT_DIR, exist_ok=True)

# 더 엄격한 정규식 패턴: ISO 8601 형식 (마이크로초 포함/미포함 모두 지원)
RE_INSERT_START = re.compile(r"\[INSERT\] start_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")
RE_INSERT_END   = re.compile(r"\[INSERT\] end_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")
RE_COPY_START   = re.compile(r"\[COPY\] start_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")
RE_COPY_END     = re.compile(r"\[COPY\] end_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")

def parse_iso(ts: str) -> datetime:
    """Parse ISO format timestamp (timezone-naive assumed as UTC)"""
    try:
        # fromisoformat can handle both with and without microseconds
        dt = datetime.fromisoformat(ts)
        # If timezone-naive, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError as e:
        raise ValueError(f"Failed to parse timestamp: {ts}") from e

def collect_phase_range(files: List[str], start_re, end_re) -> Optional[Tuple[datetime, datetime]]:
    starts, ends = [], []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            # Extract all matches
            found_starts = [parse_iso(x) for x in start_re.findall(text)]
            found_ends = [parse_iso(x) for x in end_re.findall(text)]
            starts.extend(found_starts)
            ends.extend(found_ends)
        except Exception as e:
            print(f"Warning: Failed to process {fp}: {e}")
            continue
    
    if not starts or not ends:
        return None
    return min(starts), max(ends)

def fmt(dt: datetime) -> str:
    """Format datetime for Snowflake timestamp_ltz (preserve microseconds)"""
    # Convert to UTC if needed
    dt_utc = dt.astimezone(timezone.utc)
    # Format with microseconds if present, otherwise without
    if dt_utc.microsecond:
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S")

def main():
    warehouse = os.getenv("WAREHOUSE_NAME", "COMPUTE_WH")
    pattern = os.getenv("LOG_GLOB", os.path.join(LOG_DIR, "experiment_*.log"))
    files = sorted(glob.glob(pattern))

    if not files:
        raise SystemExit(f"No logs found: {pattern}")

    insert_range = collect_phase_range(files, RE_INSERT_START, RE_INSERT_END)
    copy_range   = collect_phase_range(files, RE_COPY_START, RE_COPY_END)

    if not insert_range and not copy_range:
        raise SystemExit("No INSERT or COPY phase timestamps found in logs")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUT_DIR, f"metering_query_{ts}.sql")

    with open(out_path, "w", encoding="utf-8") as f:
        w = f.write

        w("-- Auto-generated Snowflake metering queries\n")
        w(f"-- warehouse: {warehouse}\n")
        w(f"-- logs: {pattern}\n")
        w(f"-- files processed: {len(files)}\n\n")

        w("ALTER SESSION SET TIMEZONE = 'UTC';\n\n")

        if copy_range:
            s, e = copy_range
            w("-- ===== COPY sweep =====\n")
            w(f"SET START_TS = '{fmt(s)}'::timestamp_ltz;\n")
            w(f"SET END_TS   = '{fmt(e)}'::timestamp_ltz;\n\n")
            w("""SELECT
  warehouse_name,
  SUM(credits_used) AS credits_used_total,
  SUM(credits_used_cloud_services) AS credits_used_cloud_services,
  MIN(start_time) AS min_start_time,
  MAX(end_time)   AS max_end_time
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE warehouse_name = '""" + warehouse + """'
  AND start_time < $END_TS
  AND end_time   > $START_TS
GROUP BY 1;

""")

        if insert_range:
            s, e = insert_range
            w("-- ===== INSERT sweep =====\n")
            w(f"SET START_TS = '{fmt(s)}'::timestamp_ltz;\n")
            w(f"SET END_TS   = '{fmt(e)}'::timestamp_ltz;\n\n")
            w("""SELECT
  warehouse_name,
  SUM(credits_used) AS credits_used_total,
  SUM(credits_used_cloud_services) AS credits_used_cloud_services,
  MIN(start_time) AS min_start_time,
  MAX(end_time)   AS max_end_time
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE warehouse_name = '""" + warehouse + """'
  AND start_time < $END_TS
  AND end_time   > $START_TS
GROUP BY 1;

""")

    print(f"[OK] Metering SQL written to: {out_path}")
    print(f"[INFO] Processed {len(files)} log file(s)")
    if insert_range:
        print(f"[INFO] INSERT range: {fmt(insert_range[0])} -> {fmt(insert_range[1])}")
    if copy_range:
        print(f"[INFO] COPY range: {fmt(copy_range[0])} -> {fmt(copy_range[1])}")
    print("NOTE: ACCOUNT_USAGE may lag by 30~90+ minutes.")

if __name__ == "__main__":
    main()