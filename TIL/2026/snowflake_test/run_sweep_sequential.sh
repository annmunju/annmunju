#!/usr/bin/env bash
set -euo pipefail

# 스크립트 디렉토리 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 첫 번째 스크립트 시작 시간 기록
START_TIME=$(date +%s)
START_TIME_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "===================================================="
echo "[SCHEDULER] Sequential sweep execution"
echo "===================================================="
echo "[START] First script (INSERT) will start now: ${START_TIME_UTC}"
echo "[SCHEDULED] Second script (COPY) will start in 1 hour"
echo

# 첫 번째 스크립트를 포그라운드로 실행 (겹침 방지)
echo "[RUNNING] Starting run_sweep_insert.sh (foreground)..."
bash "${SCRIPT_DIR}/run_sweep_insert.sh" > "${SCRIPT_DIR}/insert_sweep.log" 2>&1
INSERT_EXIT_CODE=$?
INSERT_END_TIME=$(date +%s)
INSERT_END_TIME_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "[DONE] INSERT sweep finished at: ${INSERT_END_TIME_UTC}"
echo "[INFO] INSERT sweep exit code: ${INSERT_EXIT_CODE}"
echo "[INFO] INSERT sweep logs: ${SCRIPT_DIR}/insert_sweep.log"
echo

# 다음 UTC 1시간 버킷으로 넘어간 뒤 COPY 시작 (버킷 분리 목적)
# next_hour = (now//3600 + 1) * 3600
# target = next_hour + 120s (버퍼)
NOW_UTC_EPOCH=$(date -u +%s)
NEXT_HOUR_UTC_EPOCH=$(( (NOW_UTC_EPOCH / 3600 + 1) * 3600 ))
TARGET_UTC_EPOCH=$(( NEXT_HOUR_UTC_EPOCH + 120 ))
SLEEP_SECS=$(( TARGET_UTC_EPOCH - NOW_UTC_EPOCH ))

if [ ${SLEEP_SECS} -lt 0 ]; then
  SLEEP_SECS=0
fi

TARGET_UTC_STR=$(date -u -r "${TARGET_UTC_EPOCH}" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "@${TARGET_UTC_EPOCH}" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "(next UTC hour + 120s)")

echo "[WAITING] Waiting ${SLEEP_SECS}s to start COPY at next UTC hour + 120s buffer"
echo "[INFO] Current time (UTC): $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "[INFO] COPY scheduled time (UTC): ${TARGET_UTC_STR}"
echo

sleep "${SLEEP_SECS}"

# 두 번째 스크립트 실행
COPY_START_TIME=$(date +%s)
COPY_START_TIME_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "===================================================="
echo "[SCHEDULER] Starting COPY sweep"
echo "===================================================="
echo "[START] COPY sweep started at: ${COPY_START_TIME_UTC}"
echo "[INFO] Time elapsed since INSERT start: $((COPY_START_TIME - START_TIME)) seconds"
echo

echo "[RUNNING] Starting run_sweep_copy.sh (foreground)..."
bash "${SCRIPT_DIR}/run_sweep_copy.sh" > "${SCRIPT_DIR}/copy_sweep.log" 2>&1
COPY_EXIT_CODE=$?

COPY_END_TIME=$(date +%s)
COPY_END_TIME_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo
echo "===================================================="
echo "[SCHEDULER] Sequential sweep execution completed"
echo "===================================================="
echo "[DONE] COPY sweep finished at: ${COPY_END_TIME_UTC}"
echo "[INFO] COPY sweep exit code: ${COPY_EXIT_CODE}"
echo "[INFO] COPY sweep logs: ${SCRIPT_DIR}/copy_sweep.log"
echo

echo "[DONE] All sweeps completed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
