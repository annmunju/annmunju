- Amazon Redshift는 빠른 완전관리형 [데이터 웨어하우스](https://aws.amazon.com/data-warehouse/)로서 표준 SQL과 기존 비즈니스 인텔리전스(BI) 도구를 사용하여 모든 데이터를 간편하고 비용 효과적으로 분석할 수 있습니다.

### Introduction to Amazon Redshift
1. Redshift 에서 클러스터 만들기
	- VPC 설정 및 노드 개수 지정. IAM 규칙 설정 (실습에서는 s3 버킷에서 txt 파일 읽는게 포함되어 있어서 해당 권한이 추가됨)
	- Security groups도 인바운드 규칙(redshift, 동일 vpc 내)이 추가되어 있는 것으로 사용
2. 쿼리 편집기를 통해 테이블 생성 및 샘플 데이터 로드
	- s3 버킷에 있는 text 파일을 사용
```SQL
COPY users FROM 's3://awssampledbuswest2/tickit/allusers_pipe.txt'
CREDENTIALS 'aws_iam_role=YOUR-ROLE'
DELIMITER '|';
```
3. 필요한 쿼리 요청

### Building with Amazon Redshift clusters
- Amazon Redshift는 대용량 병렬 처리와 열 기반 데이터 스토리지, 그리고 매우 효율적인 데이터 압축 인코딩 방식을 조합하여 스토리지 효율성과 쿼리 성능 최적화를 구현
- 행을 테이블에 추가할 때 데이터 값의 열에 적용되는 압축 유형은 압축 인코딩에 따라 결정

- COPY 명령
	- 여러 파일에서 데이터를 병렬 방식으로 로드하여 클러스터의 노드 간에 워크로드를 분할. 하나의 큰 파일에서 모든 데이터를 로드하면 직렬화 해야하는데, 대용량 파일을 압축하고 작은 파일로 분할 하면 로드를 병렬화하여 전체 작업시간이 단축됨

1. 클러스터 엔드포인트로 데이터베이스에 접속
2. 스키마 생성
	1. 압축 되지 않은 형식의 데이터를 수용할 테이블
	2. 압축된 형식의 데이터를 수용할 테이블
3. 압축되지 않은 / 압축된 데이터를 s3로부터 불러오기 : 두 경우의 경과 시간 확인하기
4. 매니페스트 파일 작성 및 이를 통해 s3로 불러오기
```
{
  "entries": [
    {"url":"s3://(LabDataBucket)/title-genres/split-with-gzip/tg_aa.gz", "mandatory":true},
    {"url":"s3://(LabDataBucket)/title-genres/split-with-gzip/tg_ab.gz", "mandatory":true},
    {"url":"s3://(LabDataBucket)/title-genres/split-with-gzip/tg_ac.gz", "mandatory":true}
  ]
}
```

```sql
BEGIN;

COPY imdb.title_genres_mnf FROM 's3://(LabDataBucket)/title_genres.manifest'
iam_role '(RedshiftAccessRoleArn)'
delimiter '\t' timeformat 'YYYY-MM-DD HH:MI:SS' NULL AS 'NULL' region '(Region)' gzip manifest;

COMMIT;
```
- 이후 잘 복사되었는지 확인하기
5. 데이터 아카이브: S3에 언로드하기 (언로드는 작업 시점의 데이터를 텍스트 형태로 받아내는 방법)
	- parallel off 지정시 데이터 단일 파일에 작성됨. 기본이 클러스터 조각 수에 따라 병렬 방식으로 작성됨.
6. redshift 클러스터에서 데이터는 조각화 후 vacuum 명령으로 클러스터를 구성된 상태로 반환해야 함. 이후 analyze 작업으로 통계 메타데이터를 업데이트함.
7. sortkey 및 distkey를 사용한 최적화
	- 테이블 생성시 해당 키를 반영해서 만들기
```sql
	BEGIN;

CREATE TABLE imdb.name_display_dskey (
"nameId" char(10) NOT NULL DISTKEY,
"name" varchar(128) NOT NULL,
"realName" varchar(255) DEFAULT NULL,
"akas" varchar(2000),
"image" varchar(192) DEFAULT NULL,
"imageId" char(12) DEFAULT NULL,
"nicknames" varchar(2000)
);
CREATE TABLE imdb.title_display_dskey(
"titleId" char(9) NOT NULL DISTKEY,
"title" text NOT NULL,
"year" int DEFAULT NULL,
"adult" int DEFAULT NULL,
"runtimeMinutes" int DEFAULT NULL,
"imageUrl" varchar(175) DEFAULT NULL,
"imageId" char(12) DEFAULT NULL,
"type" char(12) DEFAULT NULL,
"originalTitle" text
);
CREATE TABLE imdb.title_cast_dskey (
"titleId" char(9) NOT NULL DISTKEY,
"ordering" int NOT NULL,
"nameId" char(10) NOT NULL,
"category" char(15) NOT NULL,
"role" int DEFAULT NULL,
"characters" varchar(2500),
"characterIds" varchar(250),
"attributes" varchar(64) DEFAULT NULL
)
SORTKEY (titleid, ordering);

COMMIT;

```
8. distkey 및 sortkey로 쿼리를 실행해 시간을 비교했을 때 개선됨을 확인

### Working with Amazon Redshift
- Redshift는 암호화된 Secure Sockets Layer(SSL) 연결을 사용하여 **Amazon S3**에 이러한 스냅샷을 내부적으로 저장
- 데이터 로딩 프로세스
	- 데이터는 소스 시스템으로부터 S3 버킷에 저장되며 (압축)
	- COPY 명령을 통해 Redshift 테이블로 복사됨
	- SQL 클라이언트로 Redshift를 쿼리하고 반환받음

1. redshift 클러스터 생성 및 클라이언트 연결
2. 데이터 로드를 위한 테이블 생성 -> S3에서 불러오기(COPY)
	- 배포 키(DISTKEY) 지정 - 해당 필드와 관련된 데이터는 항상 동일한 슬라이스로 처리됨. 나머지는 노드간 분할됨. 따라서 group py 및 join 작업 등에 대해 해당 필드로 작업하면 처리 속도 개선됨
3. 쿼리 실행
	- `EXPLAIN` 실행시에 논리적 단계를 보여줌. 쿼리 개선해야 할 부분을 파악할 때 사용

- 압축 설정
	- **Byte dictionary:** 단일 바이트에서 최대 256개의 가능한 값을 참조하는 방법입니다. 국가 이름처럼 개수는 적지만 자주 반복되는 값이 있는 필드에 적합합니다.
	- **Delta:** 열에서 서로 인접한 값 간의 차이를 기록하여 데이터를 압축합니다.
	- **LZO:** 높은 압축률과 우수한 성능이 특징입니다. 매우 긴 문자열을 저장하는 열, 특히 제품 설명, 사용자 의견 또는 JSON 문자열과 같은 자유 형식 텍스트에 적합합니다.
	- **Mostly:** 열에 있는 값 대부분을 더 작은 표준 스토리지 크기로 압축합니다.
	- **Run-length:** 연속적으로 반복되는 값을 연속적으로 발생한 횟수(실행 길이)와 값으로 구성된 토큰으로 대체합니다. 예를 들어 테이블이 어떤 값에 따라 정렬될 때처럼 데이터 값이 자주 연속적으로 반복되는 테이블에 가장 적합합니다.
	- **Text:** 같은 단어가 자주 반복되는 VARCHAR 열을 압축합니다.
	- **Zstandard(zstd):** 다양한 데이터 집합에서 높은 압축 비율과 매우 우수한 성능을 발휘합니다. 제품 설명, 사용자 의견, 로그, JSON 문자열 등 길고 짧은 다양한 문자열을 저장하는 CHAR 및 VARCHAR 열에 특히 적합합니다.
	- **AZ64:** Amazon에서 높은 압축률과 개선된 쿼리 처리 성능을 달성하기 위해 고안한 독자 개발 압축 인코딩 알고리즘입니다.
	- **Raw:** 압축되지 않습니다.

4. 디스크 공간 및 데이터 배포 검사
```sql
SELECT
  owner AS node,
  diskno,
  used,
  capacity,
  used/capacity::numeric * 100 as percent_used
FROM stv_partitions
WHERE host = node
ORDER BY 1, 2;
```

