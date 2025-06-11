- Amazon S3에서 DynamoDB로 데이터를 가져옵니다.
- AWS Glue 크롤러를 생성합니다.
- DynamoDB에서 데이터를 추출하고 S3 버킷에 데이터를 저장하는 AWS Glue ETL(추출, 변환, 로드) 작업을 생성하고 실행합니다.

---

1. dynamoDB 콘솔에 위치한 "S3에서 가져오기"로 데이터 불러오기
2. Glue에서 Data Catalog > Crawler 선택해서 크롤러 생성
	- Data Catalog에 Databases > Table에 새로운 카탈로그가 추가됨. 컬럼 이름과 data 타입에 대한 정보가 나타남
3. 작업 생성 : Glue를 이용해서 DynamoDB에서 S3로 데이터 내보내기
	- ETL jobs > Visual ETL 선택. Create job 섹션에서 Visual ETL 선택.
	- Visual 탭의 캔버스에서 Source 및 Target 데이터 소스 생성. 예시에는 DynamoDB가 소스고 S3이 타겟임.
4. 결과 파일 확인
	- run-... Parquet 파일로 저장됨.