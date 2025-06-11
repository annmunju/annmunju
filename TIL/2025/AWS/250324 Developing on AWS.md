### AWS 서비스 구분
- 가용영역 기반 : 재해 복구 설계가 필요함
- 리전 기반 (S3 등) : 리전 간 복제(필요시)
- 글로벌 기반 (IAM, CloudFront 등)

### 하위 수준 / 상위 수준 API
- 하위 수준 (json 반환)
```python
s3client = boto3.client('s3')
response = s3client.list_objects_v2(...)
response['Contents']
```
- 상위 수준 (추상화된 객체로 반환)
```python
s3resource = boto3.resource('s3')
bucket = s3resource.Bucket(...)
bucket.objects.all()
```

### 동기식 / 비동기식
- 클라이언트가 요청하면 명령이 완료되기 기다리거나(동기) 기다리지 않는 방식(비동기)
- 비동기식으로 API 호출한 경우
	- waiter를 사용하여 현재 상태를 계속 폴링해서 확인해서 후 처리 하는 방식으로 사용할 수 있음

### AWS CLI 사용
- 기본 등록된 프로파일 말고 다른 프로파일 사용하는 방법
	- `--profile` 파라미터 사용

### 임시 보안 인증 정보
- AWS Security Token Service (STS)
- 예시) EC2에 role(역할)설정 == profile 설정. 다른 AWS 서비스에 접속할 때 키가 필요한데 (.config) 파일이 없는 경우에 role의 권한을 사용해 STS에 접속해서 키를 가져와서 S3 접속
	- role을 부여하면 이 역할로 임시 보안 인증 정보를 제공함 -> 이를 통해 s3 버킷에 접근
- 보안 인증 정보의 우선순위
	- CLI 지정
	- 환경 변수 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
	- 보안 인증 정보 파일 (프로파일) ~/.aws/credentials
	- 인스턴스 프로파일 (role을 통한 STS 발급)

### 실습 1: 개발 환경 구성
- CLI 환경에서 S3 버킷 제어
	- 목록 확인
	- 삭제할 S3 버킷 정의 후 삭제 시도
	- 디버깅 (--debug)
	- 권한 문제로 삭제 안됨 확인. IAM 권한이 있는 정책 확인
	- 해당 정책을 notes-application-role 역할에 연결
	- 이 역할을 가진 CLI 환경에서 버킷 삭제함
- AWS Configure 설정시에 access key, secret access key 사용하지 않도록 하는데 EC2에 Role을 사용하기 때문에 그러한 설정을 사용함

### 스토리지 : S3
- 리전 기반 AWS 서비스
- 하위 수준 명령 (s3api) : copy-object 등 / 상위 수준 명령 (s3) : cp 등
- 버킷 권한 확인: HeadBucket API
	- 버킷 존재 여부 확인 후에 버킷 생성 가능
- 버저닝은 활성화하기 전으로 돌릴 수 없음. 시작 혹은 정지 뿐

#### 대용량(5gb 초과) 파일을 업로드하는 방법 : Multipart
- HTTP Request의 body의 타입 : "Content-Type" : "multipart/form-data"
- 하위수준 명령을 이용해 업로드하는 과정
	- 파일을 5gb 이하로 분할
	- create-multipart-upload 명령을 통해 업로드를 실행하고 UploadID 검색
	- upload-part 명령을 통해 각 파트를 업로드하고 ETag 값을 받음
	- list-parts 기능을 이용해 모든 부분이 업로드되었는지 확인하기 위해 업로드된 부분을 모두 나열
	- ETag를 단일 파일로 컴파일
	- complete-multipart-upload 명령을 통해 업로드 완료
- 상위수준 명령을 이용해 업로드하는 방법
	- 그냥 aws s3 cp 사용 (자동으로 멀티파트 진행함)
	- aws a3 sync 사용하면 동기화 (cp와 다르게 생성된 내용과 지운 내용 모두 동기화됨) - 변경된 내용만 업데이트됨

#### 객체 메타데이터 검색
- aws s3api head-object ...

#### Object Lambda
- 데이터를 호출할 때 일부 정보만 가져오고 싶을 때, 앞부분에 필터링을 두는 방식. 
- 가져올 때 프로그래밍 돌면서 처리한 값을 가져오도록 함.
- lambda 코드 참고
```python
def lambda_handler(event, context):
	s3_url = event['getObjectContext']['inputS3Url']
	response = request.get(s3_url)
	original_object = response.content.decode('urf-8')
	original_object.upper() # 데이터 처리...
```

#### 객체에 대한 임시 엑세스 권한 부여
- 그냥 URL은 퍼블릭 액세스 권한이 없어서 공개 안되는 경우
- Object Action > presigned URL 만들기 -> 기한 설정 및 복사 -> 붙여넣기 하면 공개됨
```python
boto3.client('s3').generate_presigned_url( ... )
```


#### 대량 데이터를 관리하는 방법
- 버킷 객체에 대한 반복 요청
	- 한번에 모든 데이터를 가져오기 어려워, 쪼개서 가져오는 방법
	- 페이지네이션 기능을 사용해 객체 나열
```python
paginator = client.get_paginator('list_objects')
page_iterator = paginator.paginate( ... )
```
- 배치 작업을 사용한 대규모 처리
	- S3 Batch Operations를 사용
	- 필요한 목록들은 csv 파일로 정리해서 업로드해 실행할 수 있음

#### S3을 이용한 정적 웹사이트 호스팅
- property > static website hosting 시 별도의 URL을 생성
- aws s3 website (url) ...
- CORS (교차 오리진 리소스 공유) : 한 도메인에서 로드되어 다른 도메인에 있는 리소스와 상호 작용하는 클라이언트 웹 애플리케이션에 대한 방법을 정의 필요 (교차 오리진의 Get 요청 허용 등)

### 실습 2: S3 사용하여 솔루션 개발하기
1. python aws sdk boto3를 이용해 s3 버킷 생성
	- S3.Client.head_bucket 로 버킷 있는지 (권한까지) 확인
	- 실습 리전에 버킷 생성하는 코드 작성 (create_bucket)
	- waiter를 생성한 다음 버킷을 찾을 때 까지 폴링
```python
waiter = s3Client.get_waiter('bucket_exists')
waiter.wait(Bucket=bucket)
```
2. S3에 객체 업로드하기
	- config 파일을 읽고 설정을 변수로 저장
	- upload_file 함수를 이용해 업로드
3. S3에 저장된 객체 처리
	- s3에 업로드된 파일을 객체로 다운로드 download_fileobj
	- 데이터 처리 후 처리된 데이터로 새 객체를 생성 put_object
4. S3 정적 웹사이트 호스팅
	1. CLI 이용하기
		- $mybucket 등록
		- 권한 먼저 발급 `aws s3api put-public-access-block --bucket $mybucket --public-access-block-configuration "BlockPublicPolicy=false,RestrictPublicBuckets=false"`, `aws s3api put-bucket-policy --bucket $mybucket --policy file://~/environment/policy.json`
		- 동기화 하기 `aws s3 sync ~/environment/html/. s3://$mybucket/`
		- 활성화 하기 `aws s3api put-bucket-website --bucket $mybucket --website-configuration file://~/environment/website.json`
	2. SDK 이용하기
		- html 폴더에 있는 모든 파일 업로드
		- 웹 사이트 호스팅 put_bucket_website


## 데이터베이스 
### Amazon DynamoDB
- Document 이면서 동시에 Key-value 
- 엑세스 방식
	- 관리 콘솔에서 접근
	- NoSQL Workbench 설치
	- DynamoDB로컬에서 확인
	- PartiQL 언어 사용
	- SDK
		- 하위 수준 인터페이스 <- 파이썬은 하위만 제공
		- 문서 인터페이스
		- 상위 수준 인터페이스
- 데이터 쓰기
	- batch-write-item 시 배치 단위로 쓰기 요청이 가능
		- 하지만 일부 데이터가 제대로 쓰여지지 않은 경우에는 쓰여지지 않은 값이 반환됨
	- transaction 사용시 해당 단위가 처리 되지 않으면 아예 실패인데 .. batch 보다 2배 비쌈
- 데이터 읽기
	- [최종 일관성과 강력한 일관성 보장](obsidian://open?vault=2025&file=tech-study%2FAWS%2FDatabase_Learning_Plan%2F250321%20Amazon%20DynamoDB%20Serverless%20Architectures) 
	- 쿼리를 지원함 (파티션 키를 통해 멀티 아이템을 가져옴) : RCU 많이 발생함
		- 쿼리 표현식이 너무 어렵다 ㅠㅠ 근데 DynamoDB의 예약어들 때문에 저렇게 쓴다고 함 (:콜론 이런거 넣어서 변수처럼 씀)
	- 스캔을 지원함 (전체 키 아무거나를 통해 멀티 아이템 가져옴) : RCU 더 많이 발생함
	- 페이지네이션
		- 한번에 1mb 이상은 못가져옴
		- 그래서 나눠서 가져와야함
- 캐싱
	- DAX : 사이드 캐시가 아닌 캐시에 요청하고 DB 갔다가 오는 중간다리 역할. 애플리케이션에 캐시를 설계할 필요가 없음(캐시 왔다가 디비 갔다가 할필요 없음).
	- ElastiCache

## 실습 3: DynamoDB를 사용한 솔루션 개발
- 테이블 생성 `create_table`
	- TableName, AttributeDefinitions, KeySchema, ProvisionedThroughput <-RCU, WCU 지정 (int)
- waiter 부르기
	- client.get_waiter('table_exists')
	- 웨이터 이름 어떻게 찾음 ? -> [공식 문서에 Waiters 있음](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#waiters)
- 데이터 넣기 `put_item`
- 파티션키로 쿼리 요청 `query`
	- 변수 **qUserId**
	- KeyConditionExpression='UserId = :userId'
	- ExpressionAttributeValues={':userId': {"S": **qUserId**}},
	- ProjectionExpression="NoteId, Note"
- 항목 속성 업데이트 `update_item`
	- UpdateExpression='SET Is_Incomplete = :incomplete',
	- ExpressionAttributeValues={':incomplete': {'S': 'Yes'}}
	- 특정 조건에 맞는 항목의 속성 업데이트*
- pagenate 하기 (1mb 이상 불러올때 반드시 해야함)
	- pagenator 먼저 호출하기 `get_paginator`

## Lambda
- 이벤트 소스
	- 데이터 스토어
	- 엔드포인트
	- 개발 및 관리도구
	- 이벤트/메시지 서비스
- 구조
	- 트리거로 호출됨
	- 코드 실행됨 (레이어를 사용해 코드 분리할 것)
		- 콜드 스타트
- 함수 호출 방법
	- 동기식 (직접 호출) - 재시도 안 함
		- 비동기식 (푸시, 이벤트 대기열) - 기본 제공 재시도 2회
	- 폴링 기반 (풀) : 실시간 데이터가 쌓이면 N분에 한번 모아서 처리 - 이벤트 소스에 따라서 재시도 처리 달라짐
- 콜드 스타트 최소화 방법
	- lambda 함수 예약 (eventbridge)
	- 프로비저닝된 동시성으로 웜 스타트
	- lambda snapstart :java 관리형 런타임
- 풀 또는 폴링으로 호출
	- 이벤트 소스를 폴링하고
	- 이벤트를 처리함
	- 예시) 다이나모디비에 회원 정보를 업데이트 했을 때, 캐시에 올려놓어려고 할 때. 람다가 dynamodb의 stream(변동이 있는 데이터 하루간 보관하는 서비스)을 폴링해서 캐시로 올려둠. 
		- 왜 어플리케이션이 이 처리를 안하나? 성능 느려짐
- 로그 저장시 CloudWatch 쓰지말고 S3 저장혀 . . . 안지워지고 비용 발생함
- API 사용
	- zip 혹은 컨테이너 이미지로 함수 생성
	- 배포한 코드는 수정 불가. 버전 업데이트는 가능
- 레이어 쌓기가 가능 - 공유 라이브러리와 같은 개념

## 실습 4 - AWS Lambda를 사용하여 솔루션 개발
- Lambda 함수 생성
- cli를 이용해서 환경 변수 추가
- cli를 이용해서 함수 코드 업로드 (zip으로 말아서 올리기)
- polly 사용해서 음성 파일 만들고 s3 업로드
- 함수 생성 후 테스트하기 


## 실습 5 - Amazon API Gateway를 사용한 솔루션 개발
- api GW로 리소스 생성
- GET 메서드 구성
	- 반환된 통합 응답 탬플릿 작성 (중복 데이터 양 줄이기)
```VTL
#set($inputRoot = $input.path('$'))
[
    #foreach($elem in $inputRoot)
    {
    "NoteId" : "$elem.NoteId",
    "Note" : "$elem.Note"
    } 
    #if($foreach.hasNext),#end
    #end
]
```
- POST 메서드 구성
	- 스키마 지정 모델 생성 및 요청 본문에 적용
```json
{
    "title": "Note",
    "type": "object",
    "properties": {
        "UserId": {"type": "string"},
        "NoteId": {"type": "integer"},
        "Note": {"type": "string"}
    },
    "required": ["UserId", "NoteId", "Note"]
}
```
- CORS 구성으로 배포하기


## 인증 : Cognito 
- 인증
	- 사용자 신원 확인 
	- HTTP 인증
	- 로그인 프롬프트
	- 사용자 지정 방법
- 권한 부여
	- 원하는 작업을 사용자가 수행 가능한지 확인
	- 액세스 제어
	- 권한 도구
	- 데이터 및 운영 보호
