### DE가 하는 일
1. 인프라 구축과 관리
2. 데이터 수집
3. 분석을 위해 데이터 정리/변환
4. 데이터 세트를 카탈로그화 및 문서화
5. 정기적인 데이터 워크플로 (처리 자동화)
6. 데이터 품질/보안/규정 준수 보장

### 데이터 분석 시스템 설계를 위한 데이터 검색
- 설계를 위한 질문
	- 어떤 데이터를? 누가 소유? 어떤 변환이? 누가 봐야함? 어떻게 전달?
- 데이터 엔지니어가 데이터를 검색하는 단계
	- 비즈니스 가치 정의
	- 데이터 소비자 식별
	- 데이터 소스 식별
		- 데이터 형식별
		- 데이터 소스별
		- 수집 모드 (스트리밍, 마이크로 배치, 배치)
	- 스토리지, 카탈로그 및 데이터 액세스 요구사항 정의
	- 데이터 처리 요구사항 정의

### 데이터 아키텍처
![[Pasted image 20250324132615.png]]
> 데이터 사일로(부서 또는 개별 사용 사례에 최적화된 격리되고 호환되지 않는 데이터 스토어)를 분해하는 현대적 데이터 아키텍처 구성을 위한 AWS 서비스 (아래)
#### 저장
- S3
#### 수집
- AWS DMS : 관계형 및 비관계형 데이터베이스에서 데이터를 로드
- Firehose : 데이터 스트림 수집. Parquet 또는 ORC 같은 형식으로 변환하거나 데이터 압축 해제, 사용자 지정 데이터 변환 수행
- AWS MSK (managed streaming for kafka): 실시간 스트리밍 데이터 파이프라인 및 애플리케이션을 위한 카프카 클러스터 구축
- AWS IoT Core
- AWS DataSync : 온프렘 파일 공유, 객체 스토리지 시스템, 하둡 클러스터에서 AWS 스토리지 서비스로 전송. 예약 일정에 따라 동기화
- Transfer Family : SFTP, FTPS 프로토콜을 통해 S3 송수신 파일 전송 자동화
- AWS Snowball : 물리적 디바이스로 전송
#### 카탈로그화
- AWS Glue 데이터 카탈로그 : 데이터 레이크 콘텐츠에 대한 단일 정보 소스를 제공하도록 설계. 데이터의 위치와 품질, 사용방법을 추적
#### 처리
- AWS Glue: ETL 
- EMR : 오픈소스 프레임워크, EC2, 클러스터, EKS, EMR 등을 통해 빅데이터 세트 처리. (배치 작업)
- Flink : 실시간 데이터 처리를 위한 SQL 코드 빠르게 작성
#### 전달
- Redshift : 데이터 이동 없이 여러 데이터 베이스와 대규모 정형 데이터 세트 직접 분석 가능
- Athena : S3 에서 SQL로 조회
- EMR : 로그분석 기계학습, DS, 웹 인덱싱 등 수행 가능
- DB
- OpenSearch : 클러스터 배포 운영 및 규모 조정. 대규모 데이터 볼륨 분석
- QuickSight : SQL, 차트, 그래프. 대시보드를 통해 데이터 세트 시각화 및 분석
- SageMaker: 예측, CV, LM, Recommend system 등에 활용할 ML 모델 구축 훈련 및 배포
#### 보안 및 거버넌스
- 개념
	- 보안 : 무단 액세스, 위반 또는 공격으로부터 데이터 보호하기 위한 조치
	- 거버넌스 : 데이터 적절 관리, 품질 및 사용 보장 정책, 절차, 프로세스. 
- AWS Lake Formation: 데이터 엑세스 권한 중앙관리
- IAM
- KMS
- Macie : PII 같은 민감 데이터 검색, 분류, 보호
- DataZone : 데이터 카탈로그화, 검색, 공유 및 관리
- Audit Manager : 사용량 감사하여 위험, 규정 준수, 산업 표준 준수 평가
### 오케스트레이션 및 자동화
- 오케스트레이션 관련 AWS 서비스
	- Step Functions
	- Lambda
	- MWAA
	- EventBridge
	- SNS
	- SQS
- 제로 ETL 통합 : 데이터 이동 / 변환 없이 소스에서 데이터 직접 쿼리
	- Athena
	- Redshift 스트리밍 수집
	- Aurora (redshift 사용)
	- S3에서 redshift로 자동 복사
	- OpenSearch : 로그 분석
- 서버리스 아키텍처
	- Lambda
	- API Gateway
	- DynamoDB
	- S3
	- SNS
	- SQS
	- Redshift serverless
	- EMR serverless: 빅데이터 클러스터로 배치처리
	- Glue: 서버리스 데이터 통합 (ETL)
	- MSK serverless: 카프카 클러스터 실행
	- OpenSearch serverless
### 데이터 엔지니어링 보안 및 모니터링

#### 보안
- 액세스 관리
	- 승인된 사용자와 App만 접근 가능
	- IAM, ACM (AWS Certificate Manager - SSL/TLS)
- 규정 준수 
	- GDPR(일반 데이터 보호 규정), HIPAA 같은 규정 준수
	- Audit Manager, Config
- 민감한 데이터 보호
	- PII, 재무 기록, 건강 기록과 같은 민감 데이터 유출 보호
	- Macie, KMS, Glue (DataBrew)
- 데이터 및 네트워크 보안
	- Control Tower, GuardDuty, WAF, Shield
- 데이터 감사 가능성
	- CloudTrail, Lake Formation, Glue 데이터 카탈로그
#### 모니터링
- 리소스 모니터링
	- 병목현상 식별에 도움을 받을 수 있음
- 분석 작업 
- 데이터 파이프라인
- 데이터 액세스
- AWS 서비스
	- Amazon CloudWatch, CloudTrail, X - Ray, Guard Duty, System Manager

## 관련 도구 및 고려사항

### CI/CD
![[Pasted image 20250324141528.png]]
### IaC
- AWS CloudFormation: 탬플릿으로 프로비저닝
- CDK
- Terraform
- AWS Serverless Application Model : 탬플릿으로 프로비저닝은 거의 유사하나 **서버리스** 애플리케이션의 리소스와 구성을 정의
### 네트워킹 고려사항
- 온프렘과 AWS 연결시에 Site-to-Site VPN 혹은 Direct Connect 사용
- VPC endpoint로 외부 노출(interface endpoint 사용. eni)
- PrivateLink: AWS 서비스나 다른 계정 등에 프라이빗 연결을 제공
### 비용 최적화 도구
- 서버리스 컴퓨팅
- 오토 스케일링
- 데이터 수명 주기 관리
- 쿼리 최적화 (인덱싱, 쿼리 재작성, 데이터 캐싱 등)
- 리소스 모니터링 및 적절한 크기 조정

### 인증 및 권한 부여 도구
- 역할 기반 
- 정책 기반
- 태그 기반
- 속성 기반: 사용자 역할, 엑세스 시간, 위치, 디바이스 특성과 같은 속성을 포함함

