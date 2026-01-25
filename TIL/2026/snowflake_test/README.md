# [mini project] Snowflake Data Loading Performance Experiment

Snowflake에서 **INSERT** vs **COPY INTO** 방식의 데이터 적재 성능을 비교하는 실험 프로젝트입니다.

## 개요

이 프로젝트는 Observability 데이터(메트릭, 로그)를 Snowflake에 적재할 때 두 가지 방식의 성능 차이를 측정합니다:

| 방식 | 설명 |
|------|------|
| **INSERT** | `executemany()`를 사용한 배치 INSERT |
| **COPY** | 로컬 파일 → PUT → 내부 스테이지 → COPY INTO |

## 프로젝트 구조

```
snowflake_test/
├── src/                          # Python 소스 코드
│   ├── experiment_common.py      # 공통 설정, DB 연결, 데이터 생성 함수
│   ├── experiment_copy.py        # COPY 방식 실험 스크립트
│   ├── experiment_insert.py      # INSERT 방식 실험 스크립트
│   ├── summarize_runs.py         # 실험 결과 요약 및 CSV 출력
│   └── generate_metering_sql.py  # 크레딧 사용량 조회 SQL 생성
├── sql/                          # SQL 파일
│   ├── snowflake_setting.sql     # Snowflake 초기 설정 (테이블, 스테이지, 포맷)
│   └── snowflake_result.sql      # 결과 조회 SQL
├── run_sweep_copy.sh             # COPY 실험 배치 실행 (여러 데이터 크기)
├── run_sweep_insert.sh           # INSERT 실험 배치 실행
├── run_sweep_sequential.sh       # 순차 실험 배치 실행
├── logs/                         # 실험 로그 파일
├── tmp/                          # 임시 파일 (CSV, JSONL, 결과 CSV)
├── .env                          # 환경 변수 (git 제외)
└── README.md
```

## 사전 요구사항

### Python 환경
```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas snowflake-connector-python python-dotenv
```

### 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성합니다:

```env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role  # (선택)
SNOWFLAKE_WAREHOUSE=OBS_EXP_WH
SNOWFLAKE_DATABASE=OBS_EXP_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

### Snowflake 초기 설정
Snowflake에서 `sql/snowflake_setting.sql`을 실행하여 테이블, 스테이지, 파일 포맷을 생성합니다:

```sql
-- sql/snowflake_setting.sql 내용 실행
-- 테이블: METRICS_INSERT, METRICS_COPY, LOGS_INSERT, LOGS_COPY
-- 스테이지: OBS_EXP_STAGE
-- 파일 포맷: FF_METRICS_CSV, FF_LOGS_JSON
```

## 사용법

### 1. 단일 실험 실행

```bash
# COPY 방식 실험
python src/experiment_copy.py \
  --iterations 10 \
  --window-seconds 120 \
  --metric-rows-per-window 200 \
  --log-rows-per-window 10000

# INSERT 방식 실험
python src/experiment_insert.py \
  --iterations 10 \
  --window-seconds 120 \
  --metric-rows-per-window 200 \
  --log-rows-per-window 10000
```

### 2. 배치 스윕 실행 (여러 데이터 크기)

```bash
# COPY 방식 스윕
./run_sweep_copy.sh

# INSERT 방식 스윕
./run_sweep_insert.sh

# 순차 스윕 (INSERT → COPY 순서)
./run_sweep_sequential.sh
```

### 3. 결과 요약

```bash
python src/summarize_runs.py
# 결과: ./tmp/obs_exp/summary.csv
```

### 4. 크레딧 사용량 조회 SQL 생성

```bash
python src/generate_metering_sql.py
# 결과: ./tmp/obs_exp/metering_query_YYYYMMDD_HHMMSS.sql
```

## 실험 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--iterations` | 30 | 반복 횟수 (윈도우 개수) |
| `--window-seconds` | 120 | 윈도우 크기 (초) |
| `--metric-rows-per-window` | 2000 | 윈도우당 메트릭 행 수 |
| `--log-rows-per-window` | 50000 | 윈도우당 로그 행 수 |

## 데이터 구조

### 메트릭 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| window_start | TIMESTAMP_NTZ | 윈도우 시작 시간 |
| window_end | TIMESTAMP_NTZ | 윈도우 종료 시간 |
| source | STRING | 소스 서버 |
| metric_name | STRING | 메트릭 이름 |
| value | DOUBLE | 메트릭 값 |
| labels | VARIANT | JSON 라벨 |

### 로그 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| window_start | TIMESTAMP_NTZ | 윈도우 시작 시간 |
| window_end | TIMESTAMP_NTZ | 윈도우 종료 시간 |
| source | STRING | 소스 서버 |
| service | STRING | 서비스 이름 |
| level | STRING | 로그 레벨 |
| message | STRING | 로그 메시지 |
| payload | VARIANT | JSON 페이로드 |

## 출력 파일

- `logs/experiment_<uuid>_copy.log` - COPY 실험 로그
- `logs/experiment_<uuid>_insert.log` - INSERT 실험 로그
- `tmp/obs_exp/query_history_<uuid>_*.csv` - 쿼리 히스토리
- `tmp/obs_exp/summary.csv` - 실험 결과 요약
- `tmp/obs_exp/metering_query_*.sql` - 크레딧 조회 SQL

## 참고사항

- ACCOUNT_USAGE 뷰의 데이터는 30~90분 지연될 수 있습니다.
- 실험 전 테이블을 TRUNCATE 하므로 기존 데이터가 삭제됩니다.
- 크레딧 사용량 분석을 위해 실험 후 `generate_metering_sql.py`를 실행하세요.
