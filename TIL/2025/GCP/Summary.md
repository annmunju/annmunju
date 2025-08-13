---
marp: true
style: |
  table {
    font-size: 15pt;
    width: 100%;
    table-layout: fixed;
  }
  th, td {
    word-break: break-all;
    text-align: center;
  }
---

<!-- Heading for slide -->
# GCP Data Engineering Summary

> 2025년 7월 학습 내용 정리

---

# 데이터 엔지니어링 기초


### 데이터 엔지니어의 역할
- 데이터 파이프라인 빌드 담당자
- 원시 데이터 → 유용한 상태의 데이터로 변환
- 데이터 사용량을 프로덕션 설정으로 옮기기 위한 프로세스 진행
- **Replicate and migrate → Ingest → Transform → Store** 순서로 진행

---

### 데이터 엔지니어링 도전 과제
- 필요한 데이터 접근하기 (데이터 사일로 문제)
- 필요한 데이터 품질 확보 (ETL 처리)
- 변환에 필요한 컴퓨팅 리소스 확보
- 쿼리 성능 문제 해결

---

# 데이터 복제 및 마이그레이션

### 데이터 복제와 마이그레이션 도구
- **Storage Transfer Service**: 대규모 데이터 세트 이동, 초당 수십기가비트 속도
- **Storage Transfer Appliance**: 오프라인 대규모 데이터 세트 이동 솔루션
- **Datastream**: 온프렘, 멀티클라우드의 RDB에서 GCP로 지속적 복제
  - **Datastream → GCS/PubSub → Dataflow → BigQuery** 형태로 연결
  - CDC 옵션 제공, 스키마/테이블/열 수준에서 선택적 복제 가능

---

# 데이터 파이프라인 패턴

### EL (Extract and Load) 패턴
- **bq 명령줄 도구**로 직접 로드
- **BigQuery Data Transfer Service**로 다양한 소스 데이터 쉽게 로드
- **BigLake 테이블**: 외부 데이터 쿼리 가능, 메타데이터 캐싱으로 성능 향상

---

### ELT (Extract, Load, Transform) 패턴
- 데이터가 올라온 후 여러번 변환 수행 가능
- **Dataform**으로 간소화된 변환
- BigQuery UDF를 통한 SQL/JavaScript 커스텀 변환
- 원격함수로 Cloud Run Functions와 통합

### ETL (Extract, Transform, Load) 패턴
- BigQuery 로드 전에 조정 및 변환
- **Dataprep**: 노코드 솔루션, 레시피 방식의 변환
- **Data Fusion**: 드래그 앤 드롭으로 파이프라인 빌드

---

# 데이터 처리 서비스 비교

| 항목 | **Dataflow** | **Dataproc** | **Composer** |
| --- | --- | --- | --- |
| 서비스 유형 | 스트리밍/배치 데이터 처리 엔진 (Fully Managed) | Spark/Hadoop 클러스터 기반 (Managed YARN) | 워크플로우 오케스트레이션 (Apache Airflow) |
| 기술 기반 | Apache Beam | Apache Spark, Hadoop, Hive | Apache Airflow |
| 주 사용 용도 | 실시간 로그/이벤트 처리, 대용량 ETL | 머신러닝, 대규모 분석, 커스텀 분산 처리 | ETL 순서 조정, 파이프라인 스케줄링 |
| 처리 방식 | 스트리밍 + 배치 모두 지원 | 배치 중심, Spark 스트리밍 가능 | 주기적/이벤트 기반 워크플로우 |
| 관리 방식 | Fully Managed, 자동 스케일링 | Managed Cluster, 수동 튜닝 필요 | Airflow Fully Managed |

---

# 데이터 레이크 구축


### Cloud Storage 기반 데이터 레이크
- 다양한 규모의 다양한 유형 데이터를 안전하게 저장
- 모든 유형의 데이터 수용 가능 (원시 데이터 저장)
- 영구적, 저렴, 전역적 공유 및 비공개 제어

---

### Cloud Storage 클래스

| 클래스 | 용도 | 접근 빈도 | 최소 저장 기간 | 특징 |
| --- | --- | --- | --- | --- |
| **Standard** | 자주 사용하는 데이터 | 매우 자주 | 없음 | 빠르고 낮은 지연시간 |
| **Nearline** | 가끔 사용하는 데이터 | 월 1회 정도 | 30일 | 읽기보다 저장 비용이 비쌈 |
| **Coldline** | 거의 사용 안 하는 데이터 | 분기 1회 이하 | 90일 | 저장 비용 낮고, 읽기 비용 높음 |
| **Archive** | 장기 보관 목적 데이터 | 거의 없음 | 365일 | 저장 비용 가장 낮음, 읽기 비용 가장 비쌈 |

---

### 보안
- **IAM 정책**과 **ACL**을 동시에 이용 가능 (둘 중 하나라도 허용하면 허용됨)
- 다양한 암호화 방법: **GMEK**, **CMEK**, **CSEK**, 클라이언트 측 암호화
- 객체 잠금, 잠금 보존 정책 등

---

# 데이터 웨어하우스 구축 (BigQuery)


### 모던 데이터 웨어하우스 특징
- 기가바이트~페타바이트 확장 가능한 단일 데이터베이스
- 서버리스, no-ops
- 풍부한 시각화, BI 도구 지원
- 최신 상태로 유지된 데이터
- 머신러닝 기능 내장
- 보안과 공동 작업 공유

---

### BigQuery 특징
- 인덱스 사용 안함, 열 지향 테이블
- 스토리지와 분석 엔진(컴퓨팅) 분리
- 필터 먼저 → 계산 분산 실행 → 합치기 순서로 수행

---

### BigQuery 구조 및 기능
- **프로젝트 - 데이터 세트 - 테이블** 계층 구조
- 쿼리비용과 스토리지비용 별도 부과
- 테이블/뷰, 열 수준에서 권한 제어 가능
- **승인된 뷰**: 기본 소스 데이터 접근 권한 없이도 쿼리 결과 공유 가능
- **데이터 마스킹**: 정책 태그로 콘텐츠 난독화/무효화
- **구체화된 뷰**: 쿼리 결과 주기적으로 캐싱

---

### 중첩 및 반복 필드
- 관계형 DB의 조인 연산 비용 절약
- 하나의 행에 세분화된 값들이 더 많은 값들을 가질 수 있도록 함
- 스키마에서 구조체는 record 타입으로 표기
- PostgreSQL 정규화 → BigQuery 비정규화 + 중첩 + 반복 필드 구조

---

### 파티셔닝과 클러스터링
- **파티셔닝**: 데이터 읽기의 양과 비용을 줄이기, 비용 추산 용이
- **클러스터링**: 파티션 내부에서 지정된 컬럼 기준으로 데이터 정렬/그룹화
- BigQuery는 주기적으로 자동 재클러스터링 수행

---

# 자동화 기법

### 파이프라인 자동화 도구
- **Cloud Scheduler**: 지정된 반복주기로 워크로드 호출
- **Cloud Composer (Airflow)**: Python으로 워크플로 개발 및 실행
- **Cloud Run Functions**: AWS Lambda와 유사한 서버리스 함수
- **Eventarc**: AWS EventBridge와 유사한 이벤트 중심 아키텍처

### 워크플로우 관리
- 예약된 작업이나 일회성 작업에 대해 Cloud Scheduler와 Cloud Composer 활용
- Workflows로 깃 액션과 유사한 워크플로 트리거
- 오류 처리, 재시도, 모니터링 기능 통합

---

# 메타데이터 관리 및 거버넌스

### Dataplex
- 통합 메타데이터, 자동 검색, 데이터 수명 주기 관리
- 데이터 품질, 분류, 조직화
- 통합 보안 및 거버넌스

---

### Analytics Hub
- BigQuery 데이터 공유 기능 확장 플랫폼
- 기업/기관/팀 간 데이터 세트 안전하게 공유
- 중복 저장 없이 공유 가능

### Data Catalog
- 태그를 사용해 데이터 세트 분리 및 민감 열 관리
- 데이터 세트 검색, 민감 정보 관리 (분류, 수정 등)

---

# 실무 고려사항

### 성능 최적화
- Dataflow에서 DoFn 메서드 파이프라인 코드가 느려지면 클라우드 프로파일러 사용
- BigQuery에서 동시 쿼리 제한 오류 발생시 보고서를 배치 처리로 변경
- 10GB 미만 테이블은 join 가능하나, 이보다 크면 비정규화 권장

---

### 비용 관리
- 근무 시간 외 Dataproc 자동 확장 구성 고려
- 여러 개의 작은 작업 실행시 일시적인 클러스터 사용
- BigQuery 쿼리 검사기와 가격 계산기 활용

### 데이터 통합
- Cloud SQL의 소량 데이터와 BigQuery 대량 데이터 결합시 주기적 동기화 후 BigQuery에서 조인
- 스트리밍 데이터 처리: Pub/Sub → Dataflow → BigQuery 패턴
- BigTable은 시계열 데이터, IoT, 금융 거래 데이터에 적합

---

# 감사합니다!

https://cloud.google.com/blog/products/data-analytics/building-the-data-engineering-driven-organization?hl=en