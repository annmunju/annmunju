#!/usr/bin/env bash
set -euo pipefail

# 공통 파라미터
ITERATIONS=10
WINDOW_SECONDS=120
METRIC_ROWS=200

# 스윕할 로그량(2분당)
LOG_LEVELS=(1000 5000 10000 20000 50000)

# 실행 간격(초)
SLEEP_BETWEEN_RUNS=20

echo "[START] COPY sweep runs: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "ITERATIONS=${ITERATIONS}, WINDOW_SECONDS=${WINDOW_SECONDS}, METRIC_ROWS=${METRIC_ROWS}"
echo "LOG_LEVELS=${LOG_LEVELS[*]}"
echo "SLEEP_BETWEEN_RUNS=${SLEEP_BETWEEN_RUNS}s"
echo

for LOG_ROWS in "${LOG_LEVELS[@]}"; do
  echo "===================================================="
  echo "[RUN] LOG_ROWS_PER_WINDOW=${LOG_ROWS}  (UTC: $(date -u +"%Y-%m-%dT%H:%M:%SZ"))"
  echo "===================================================="

  python src/experiment_copy.py \
    --iterations "${ITERATIONS}" \
    --window-seconds "${WINDOW_SECONDS}" \
    --metric-rows-per-window "${METRIC_ROWS}" \
    --log-rows-per-window "${LOG_ROWS}"

  echo
  echo "[SLEEP] ${SLEEP_BETWEEN_RUNS}s before next run..."
  sleep "${SLEEP_BETWEEN_RUNS}"
done

echo
echo "[DONE] COPY sweep finished: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

