import os
import re
import glob
import csv
from pathlib import Path
from typing import Dict, Any, Optional

# 프로젝트 루트 경로 (src/ 의 상위 디렉토리)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
QH_DIR = os.path.join(PROJECT_ROOT, "tmp", "obs_exp")
OUT_CSV = os.path.join(PROJECT_ROOT, "tmp", "obs_exp", "summary.csv")

# --- regex patterns ---
# 더 엄격한 정규식 패턴: ISO 8601 형식 (마이크로초 포함/미포함 모두 지원)
re_exp_id = re.compile(r"\[RUN\] exp_id=([0-9a-fA-F-]{36})")
re_params = re.compile(
    r"\[PARAMS\] iterations=(\d+), window_seconds=(\d+), metric_rows_per_window=(\d+), log_rows_per_window=(\d+)"
)
re_insert_total = re.compile(r"\[INSERT\] total_sec=([0-9.]+)")
re_copy_total = re.compile(r"\[COPY\] total_sec=([0-9.]+)")
re_insert_start = re.compile(r"\[INSERT\] start_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")
re_insert_end = re.compile(r"\[INSERT\] end_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")
re_copy_start = re.compile(r"\[COPY\] start_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")
re_copy_end = re.compile(r"\[COPY\] end_ts=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)")


def parse_log_file(path: str) -> Optional[Dict[str, Any]]:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")

    m = re_exp_id.search(text)
    if not m:
        return None
    exp_id = m.group(1)

    params = re_params.search(text)
    if not params:
        return None

    iterations, window_seconds, metric_rows, log_rows = params.groups()

    def find_last(pattern):
        matches = pattern.findall(text)
        return matches[-1] if matches else None

    insert_total = find_last(re_insert_total)
    copy_total = find_last(re_copy_total)

    insert_start = find_last(re_insert_start)
    insert_end = find_last(re_insert_end)
    copy_start = find_last(re_copy_start)
    copy_end = find_last(re_copy_end)

    return {
        "exp_id": exp_id,
        "log_file": os.path.basename(path),
        "iterations": int(iterations),
        "window_seconds": int(window_seconds),
        "metric_rows_per_window": int(metric_rows),
        "log_rows_per_window": int(log_rows),
        "insert_total_sec": float(insert_total) if insert_total else None,
        "copy_total_sec": float(copy_total) if copy_total else None,
        "ratio_insert_over_copy": (float(insert_total) / float(copy_total))
        if insert_total and copy_total and float(copy_total) != 0 else None,
        "insert_start_ts": insert_start,
        "insert_end_ts": insert_end,
        "copy_start_ts": copy_start,
        "copy_end_ts": copy_end,
    }


def summarize_query_history(exp_id: str) -> Dict[str, Any]:
    """
    query_history_<exp_id>_copy.csv 와 query_history_<exp_id>_insert.csv 를 읽어서
    query_tag별( insert/copy ) 쿼리수와 elapsed 합계를 요약.
    exp_id와 일치하는 태그만 카운트합니다.
    """
    qh_copy_path = os.path.join(QH_DIR, f"query_history_{exp_id}_copy.csv")
    qh_insert_path = os.path.join(QH_DIR, f"query_history_{exp_id}_insert.csv")

    insert_cnt = 0
    copy_cnt = 0
    insert_elapsed = 0.0
    copy_elapsed = 0.0
    qh_files = []

    # exp_id로 끝나는 태그 패턴 (대소문자 무시)
    exp_id_lower = exp_id.lower()
    copy_tag_pattern = f"{exp_id_lower}-copy"
    insert_tag_pattern = f"{exp_id_lower}-insert"

    # Copy 파일 처리
    if os.path.exists(qh_copy_path):
        qh_files.append(os.path.basename(qh_copy_path))
        with open(qh_copy_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tag = (row.get("QUERY_TAG") or row.get("query_tag") or "").lower()
                elapsed = row.get("ELAPSED_SEC") or row.get("elapsed_sec")
                try:
                    elapsed = float(elapsed) if elapsed is not None else 0.0
                except (ValueError, TypeError):
                    elapsed = 0.0

                # exp_id로 끝나는 copy 태그만 카운트
                if tag == copy_tag_pattern:
                    copy_cnt += 1
                    copy_elapsed += elapsed

    # Insert 파일 처리
    if os.path.exists(qh_insert_path):
        qh_files.append(os.path.basename(qh_insert_path))
        with open(qh_insert_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tag = (row.get("QUERY_TAG") or row.get("query_tag") or "").lower()
                elapsed = row.get("ELAPSED_SEC") or row.get("elapsed_sec")
                try:
                    elapsed = float(elapsed) if elapsed is not None else 0.0
                except (ValueError, TypeError):
                    elapsed = 0.0

                # exp_id로 끝나는 insert 태그만 카운트
                if tag == insert_tag_pattern:
                    insert_cnt += 1
                    insert_elapsed += elapsed

    if not qh_files:
        return {
            "qh_file": None,
            "insert_q_cnt": None,
            "insert_elapsed_sum": None,
            "copy_q_cnt": None,
            "copy_elapsed_sum": None,
        }

    return {
        "qh_file": ", ".join(qh_files),
        "insert_q_cnt": insert_cnt,
        "insert_elapsed_sum": round(insert_elapsed, 3) if insert_elapsed > 0 else None,
        "copy_q_cnt": copy_cnt,
        "copy_elapsed_sum": round(copy_elapsed, 3) if copy_elapsed > 0 else None,
    }


def main():
    os.makedirs(QH_DIR, exist_ok=True)

    # 개별 실험 데이터 수집
    all_experiments = []
    for log_path in sorted(glob.glob(os.path.join(LOG_DIR, "experiment_*.log"))):
        info = parse_log_file(log_path)
        if not info:
            continue

        qh = summarize_query_history(info["exp_id"])
        info.update(qh)
        all_experiments.append(info)

    # log_rows_per_window를 키로 그룹화하여 INSERT와 COPY 결과 병합
    grouped = {}
    for exp in all_experiments:
        log_rows = exp["log_rows_per_window"]
        if log_rows not in grouped:
            grouped[log_rows] = {
                "log_rows_per_window": log_rows,
                "metric_rows_per_window": exp["metric_rows_per_window"],
                "iterations": exp["iterations"],
                "window_seconds": exp["window_seconds"],
                "insert_total_sec": None,
                "copy_total_sec": None,
                "insert_q_cnt": None,
                "insert_elapsed_sum": None,
                "copy_q_cnt": None,
                "copy_elapsed_sum": None,
                "insert_start_ts": None,
                "insert_end_ts": None,
                "copy_start_ts": None,
                "copy_end_ts": None,
                "insert_exp_id": None,
                "copy_exp_id": None,
                "insert_log_file": None,
                "copy_log_file": None,
            }

        # INSERT 데이터 병합
        if exp["insert_total_sec"] is not None:
            grouped[log_rows]["insert_total_sec"] = exp["insert_total_sec"]
            grouped[log_rows]["insert_q_cnt"] = exp.get("insert_q_cnt")
            grouped[log_rows]["insert_elapsed_sum"] = exp.get("insert_elapsed_sum")
            grouped[log_rows]["insert_start_ts"] = exp.get("insert_start_ts")
            grouped[log_rows]["insert_end_ts"] = exp.get("insert_end_ts")
            grouped[log_rows]["insert_exp_id"] = exp["exp_id"]
            grouped[log_rows]["insert_log_file"] = exp["log_file"]

        # COPY 데이터 병합
        if exp["copy_total_sec"] is not None:
            grouped[log_rows]["copy_total_sec"] = exp["copy_total_sec"]
            grouped[log_rows]["copy_q_cnt"] = exp.get("copy_q_cnt")
            grouped[log_rows]["copy_elapsed_sum"] = exp.get("copy_elapsed_sum")
            grouped[log_rows]["copy_start_ts"] = exp.get("copy_start_ts")
            grouped[log_rows]["copy_end_ts"] = exp.get("copy_end_ts")
            grouped[log_rows]["copy_exp_id"] = exp["exp_id"]
            grouped[log_rows]["copy_log_file"] = exp["log_file"]

    # ratio 계산 및 정렬
    merged_rows = []
    for log_rows in sorted(grouped.keys()):
        row = grouped[log_rows]
        # ratio 계산
        if row["insert_total_sec"] and row["copy_total_sec"] and row["copy_total_sec"] != 0:
            row["ratio_insert_over_copy"] = round(row["insert_total_sec"] / row["copy_total_sec"], 3)
        else:
            row["ratio_insert_over_copy"] = None
        merged_rows.append(row)

    # 출력 CSV
    fieldnames = [
        "log_rows_per_window",
        "metric_rows_per_window",
        "iterations",
        "window_seconds",
        "insert_total_sec",
        "copy_total_sec",
        "ratio_insert_over_copy",
        "insert_q_cnt",
        "insert_elapsed_sum",
        "copy_q_cnt",
        "copy_elapsed_sum",
        "insert_start_ts",
        "insert_end_ts",
        "copy_start_ts",
        "copy_end_ts",
        "insert_exp_id",
        "copy_exp_id",
        "insert_log_file",
        "copy_log_file",
    ]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in merged_rows:
            writer.writerow({k: r.get(k) for k in fieldnames})

    # 콘솔 요약(가독성)
    print(f"[OK] Wrote summary: {OUT_CSV}")
    print()
    print("log_rows | insert_sec | copy_sec | ratio | insert_q | copy_q")
    print("-------- | ---------- | -------- | ----- | -------- | ------")
    for r in merged_rows:
        lr = r["log_rows_per_window"]
        ins = r["insert_total_sec"]
        cp = r["copy_total_sec"]
        ratio = r["ratio_insert_over_copy"]
        iq = r.get("insert_q_cnt")
        cq = r.get("copy_q_cnt")
        print(f"{lr:7} | {ins!s:10} | {cp!s:8} | {ratio!s:5} | {iq!s:8} | {cq!s:6}")


if __name__ == "__main__":
    main()