- Amazon S3에서 데이터세트를 업로드하고 검토합니다.
- AWS Command Line Interface(AWS CLI)를 사용하여 EMR 클러스터에 연결합니다.
- Spark를 사용하여 데이터를 처리합니다.

---

1. S3 버킷에 처리할 csv 넣어두기
2. 파이썬 파일 작성 (args를 data_source, output_uri로 설정)
3. AWS CLI 콘솔로 emr 클러스터 ID 가져오기
	- `aws emr list-clusters`
4. emr cluster id를 사용하여 emr cluster의 publicDNS 이름을 가져오기
	- `aws emr describe-cluster`
5. emr 터미널에 접속하기
	- ssh로 접속. 사용자는 hadoop에 호스트 주소는 4번의 publicDNS
6. emr 내부에서 단계를 제출해서 emr cluster 단계를 완성하기
	- `aws emr add-steps --cluster-id ...`
	- `--steps Type=Spark,Name='SparkApp',ActionOnFailure=CONTINUE,Args=[s3://labstack-6eefe2ec-f037-4f9a-8ba4-d81-labdatabucket-fd6mnqegsdc3/iris_data.py,--data_source,s3://labstack-6eefe2ec-f037-4f9a-8ba4-d81-labdatabucket-fd6mnqegsdc3/iris_data.csv,--output_uri,s3://labstack-6eefe2ec-f037-4f9a-8ba4-d81-labdatabucket-fd6mnqegsdc3/output]`
	- https://docs.aws.amazon.com/cli/latest/reference/emr/add-steps.html
7. 상태 확인을 위한 describe-step 조회
	- 다되면 S3 버킷 output/ 조회
