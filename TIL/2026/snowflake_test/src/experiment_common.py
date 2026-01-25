import os
import json
import uuid
import random
import datetime as dt
from typing import List, Tuple

import pandas as pd
import snowflake.connector

from dotenv import load_dotenv

import logging

# 프로젝트 루트 경로 (src/ 의 상위 디렉토리)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
TMP_DIR = os.path.join(PROJECT_ROOT, "tmp", "obs_exp")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# -------------------------
# Config
# -------------------------
ACCOUNT = os.environ["SNOWFLAKE_ACCOUNT"]
USER = os.environ["SNOWFLAKE_USER"]
PASSWORD = os.environ["SNOWFLAKE_PASSWORD"]
ROLE = os.environ.get("SNOWFLAKE_ROLE", "")
WAREHOUSE = os.environ.get("SNOWFLAKE_WAREHOUSE", "OBS_EXP_WH")
DATABASE = os.environ.get("SNOWFLAKE_DATABASE", "OBS_EXP_DB")
SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC")

# Defaults (can be overridden by CLI args; env vars are optional fallbacks)
ITERATIONS = int(os.environ.get("ITERATIONS", "30"))
WINDOW_SECONDS = int(os.environ.get("WINDOW_SECONDS", "120"))
SOURCES = ["gpu-server-1"]
SERVICES = ["api", "worker", "redis"]
LEVELS = ["INFO", "WARN", "ERROR"]

# scale knobs
METRIC_ROWS_PER_WINDOW = int(os.environ.get("METRIC_ROWS_PER_WINDOW", "2000"))
LOG_ROWS_PER_WINDOW = int(os.environ.get("LOG_ROWS_PER_WINDOW", "50000"))


def connect():
    conn = snowflake.connector.connect(
        account=ACCOUNT,
        user=USER,
        password=PASSWORD,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
        role=ROLE if ROLE else None,
    )
    return conn


def now_floor_to_window(ts: dt.datetime, window_seconds: int) -> dt.datetime:
    epoch = int(ts.timestamp())
    floored = epoch - (epoch % window_seconds)
    return dt.datetime.fromtimestamp(floored)


# -------------------------
# Data generation
# -------------------------
def generate_metrics(window_start: dt.datetime, window_end: dt.datetime, metric_rows_per_window: int) -> pd.DataFrame:
    rows = []
    for _ in range(metric_rows_per_window):
        source = random.choice(SOURCES)
        metric_name = random.choice([
            "gpu_util_pct",
            "gpu_mem_used_pct",
            "cpu_util_pct",
            "mem_used_pct",
            "queue_length",
            "api_5xx_rate",
            "api_p95_ms",
        ])
        value = random.random() * 100.0
        labels = {
            "host": source,
            "service": random.choice(SERVICES),
        }
        rows.append((window_start, window_end, source, metric_name, value, json.dumps(labels)))
    df = pd.DataFrame(rows, columns=[
        "window_start", "window_end", "source", "metric_name", "value", "labels_json"
    ])
    return df


def generate_logs(window_start: dt.datetime, window_end: dt.datetime, log_rows_per_window: int) -> pd.DataFrame:
    rows = []
    for i in range(log_rows_per_window):
        source = random.choice(SOURCES)
        service = random.choice(SERVICES)
        level = random.choices(LEVELS, weights=[0.9, 0.08, 0.02])[0]
        message = f"sample log {i}"
        payload = {
            "request_id": str(uuid.uuid4()),
            "job_id": str(uuid.uuid4()),
            "extra": {"k": random.randint(1, 1000)},
        }
        rows.append((window_start, window_end, source, service, level, message, json.dumps(payload)))
    df = pd.DataFrame(rows, columns=[
        "window_start", "window_end", "source", "service", "level", "message", "payload_json"
    ])
    return df


# -------------------------
# Measurement helpers
# -------------------------
def get_query_stats(conn, since_minutes: int = 120) -> pd.DataFrame:
    cur = conn.cursor()
    try:
        cur.execute(f"""
            SELECT
              query_id,
              query_tag,
              start_time,
              end_time,
              total_elapsed_time/1000 as elapsed_sec,
              credits_used_cloud_services,
              query_type,
              query_text
            FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY(
              END_TIME_RANGE_START => DATEADD('minute', -{since_minutes}, CURRENT_TIMESTAMP()),
              END_TIME_RANGE_END   => CURRENT_TIMESTAMP()
            ))
            WHERE query_text ILIKE '%OBS_EXP_DB%'
            ORDER BY start_time DESC
        """)
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
        return pd.DataFrame(rows, columns=cols)
    finally:
        cur.close()

