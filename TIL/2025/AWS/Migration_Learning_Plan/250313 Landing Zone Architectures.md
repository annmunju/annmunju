- 단일 계정을 사용하지 않아야 하는 이유
	- 워크로드가 프로덕션 워크로드에 영향을 줄 . 수있음
	- 사용 권한과 워크로드 간 액세스 위험
	- 사용 서비스가 다양한 관계로 정책이 복잡
	- 결제 구조 및 운영 지원이 복잡
	-> 다중 계정 아키텍처로의 전환 필요

- 다중 계정에서 고려해야할 사항
	- 계정 구성
	- 보안 및 규정 준수
	- 결제 및 비용 관리 (**Organizations** 및 통합 결제 사용)
	- 기술 관련 사항
		- 영향 범위 및 분리 (위험 노출 줄이기)
		- 민감한 데이터 엑세스 제한
		- 민첩성 강화
		- 할당량 늘리기 (워크로드 분리하기)
- 랜딩 존 == 잘 설계된 다중 계정 AWS 환경
	- 다중 계정 아키텍처, IAM, 거버넌스, 관찰 기능, 데이터 보안, 네트워크 설계, 로깅을 시작할 수 있는 기준점
	- 과제 : AWS 관리 및 거버넌스, 네트워킹, 자격증명 관리, 보안, 로깅

### 랜딩 존 아키텍처 
- Organizations (조직)을 이용해 간편하게 계정 관리하기
	- OU: 조직 구성 단위
	- SCP: 서비스 제어 정책

- OU 구조
![[src/Pasted image 20250313141015.png]]
- SCP: 조직 정책의 일종으로 액세스 제어

- 랜딩 존의 네트워킹
	- 전용 네트워킹 계정 생성해서 허브 역할을 하도록 하여 모든 내부 네트워킹 구성요소를 호스팅
		- Trasit Gateway, route 53, vpn, Direct Connect 연결 종료를 위한 게이트웨이 등
	- 온프레미스 또는 콜로케이션 환경을 AWS 랜딩 존에 연결하는 데 유용한 방법
		- Direct Connect, Site-to-Site VPN
- 네트워킹 계정을 통한 라우팅 방법: Transit Gateway를 사용하여 다른 계정으로 라우팅
![[src/Pasted image 20250313141801.png]]

- 자격 증명 관리 시스템에서 통합 자격 증명 관리 ,SSO, 다중계정 사용자 및 그룹에 따른 세분화된 액세스로 관리 제어
- 로깅 관리
	- 로그 아카이브 계정을 만들어 로그 보관 처리 리포지토리 역할을 하도록 함
	- VPC Flow, CloudTrail, Config, CloudWatch 로그 -> S3로 전송
	- 전용 로그 아카이브 계정으로 통합하거나 서드파티 SIEM에 수집
![[src/Pasted image 20250313142329.png]]

- 감사 계정을 만들어 관리. 모든 계정에 읽기 전용 액세스 권한 부여하여 검토
	- Security Hub, GuardDuty등 보안 서비스에서 취합된 정보를 검토
![[src/Pasted image 20250313142336.png]]

## Control Tower
- 새 랜딩 존 설정하기
- 다중 계정 전략을 사용하기 -> AWS 조직을 이용하면 쉽게 사용 가능 -> 컨트롤 타워를 사용하면 모범 사례 기반 프레임워크 제공

![[src/Pasted image 20250313143008.png]]

- AWS Organizations OU 2개 생성: 조직 루트 구조 내에 포함된 보안 및 샌드박스(선택 사항)    
- 공유 계정 3개 생성: 관리 계정, 로그 아카이브 계정, 감사 계정
- 사전 구성된 그룹 및 Single Sign-On 액세스를 사용해 AWS IAM Identity Center(이전 명칭: AWS Single Sign-On)에서 클라우드 네이티브 디렉터리를 생성
- 감사 계정에서 계정 간 액세스 구성
- 알림 사전 구성 AWS Control Tower는 Amazon Simple Notification Service(SNS)를 사용하여 관리 계정과 감사 계정의 이메일 주소로 프로그래밍 방식의 알림 전송
- 필수 **제어** 기능을 제공하여 AWS Control Tower에서 배포되는 리소스를 보호하고 다중 계정에서 규정이 위반되는 경우 감지
	- 예방 제어, 감지 제어, 사전 예방 제어(규정 비준수 리소스는 프로비저닝 되지 않음)
- 수명 주기 이벤트를 지원하여 사용자가 새 계정 생성의 일환으로 추가 사용자 지정 자동화를 구성할 수 있도록 지원

### 다른 AWS 거버넌스 서비스 통합
- 조직: 컨트롤 타워가 조직을 생성할 때는 루트 / 보안 / 샌드박스(워크로드?) OU가 포함됨
	- SPC로 예방 제어
- IAM: 사용자, 그룹, 권한 집합 자동 배포
- 서비스 카탈로그로 프로비저닝. DB, 개발 리소스, 웹사이트 등 사전 구성된 환경.
	- Account Factory가 생성됨. 단일 위치에서 랜딩 존에 배포하려는 계정을 프로비저닝, 업데이트, 관리
- Config를 이용한 감지 제어 적용
- CloudFormation: 랜딩존 배포할 때 사전 구성된 템플릿 실행됨
![[src/Pasted image 20250313144253.png]]
- CloudFormation Hooks로 사전 예방 제어
- CloudWatch, CloudTrail

## 랜딩 존으로 마이그레이션
- 단계: 평가 > 활용 > 마이그레이션 및 현대화
- 평가
	- 이해관계자 파악, 준비 상태 평가, 렌딩 존 요구 사항 범위 지정
- 랜딩 존 설계
	- 계정 구조 설계: 관리 계정에는 워크로드가 없도록, 프로덕션과 비프로덕션 분리, 계정마다 단일 혹은 관련 워크로드 소규모 세트 유지
	- OU를 사용하여 계정 구성: 기능이 유사한 계정 그룹화, 공통 정책 적용 및 리소스 공유
![[src/Pasted image 20250313150510.png]]
- 필요에 따라 중첩 OU 사용. 워크로드별로 계정을 구성하고 OU별로 관리
- OU당 SCP는 5개로 제한됨
	- AWS Control Tower용 SCP 2개(2개 자동 소비)
	- 루트의 SCP 1개
	- OU용 SCP 1개(사용자 지정된 사용자)
	- SCP 무료 슬롯 1개

- 랜딩 존에 적합한 제어 기능 수립 및 선택
	- AWS 제공 제어 활성화 혹은
	- SCP, AWS Config 규칙, AWS CloudFormation Hooks로 자체 사용자 지정 제어를 생성
	- 제어 관리
		- 컨트롤 라이브러리를 사용하면 사용 가능한 제어를 살펴볼 수 있음
		- 보안 허브에 액세스하면 계정의 보안 상태를 종합하여 보여주고 다른 보안 서비스와 통합할 수 있음

### 절차
- 관리 계정 : IAM 사용자로 로그인. 필수 역할로 범위 지정, 최소 권한 적용
- 컨트롤 타워 배포 준비
	- 공유 계정 이메일 주소 생성
	- 필수 파라미터 문서화
	- 홈 리전 고려 사항
- 홈 리전에서 컨트롤 타워 배포
- AWS Organizations에서 AWS Control Tower로 AWS 멤버 계정 마이그레이션
![[src/Pasted image 20250313160456.png]]


## 랜딩 존 확장
- 추가 기능적 OU
![[src/Pasted image 20250313161045.png]]

### Control Tower 전체 구조
![[src/Pasted image 20250313162424.png]]

## 랜딩 존 사용자 지정
- 사용자 지정 범주
![[src/Pasted image 20250313162702.png]]
= CfCT(Customizations for AWS Control Tower)

- CfCT 배포 워크플로
	- AWS CodePipeline 워크플로
	- AWS Control Tower 수명 주기 이벤트 워크플로
![[src/Pasted image 20250313162800.png]]

- AFT(Account Factory for Terraform)
	- AFT 관리 계정을 만들어서 서비스 기능을 배포
	- 4개의 별도 리포를 사용해 워크플로 관리
		- aft-account-request: 새계정 요청
		- aft-global-customizations: 모든 사용자 지정 관리
		- aft-account-cudtomizations: 특정 계정 사용자 지정 관리
		- aft-account-provisioning-customizations: Step Functions로 사용자 지정 관리
	- AWS Control Tower는 Terraform 파이프라인에서 계정을 요청한 후 계정을 프로비저닝 -> Terraform 파이프라인이 사용자 지정을 수행 -> 새 계정 요청의 GitOps 워크플로, AWS Control Tower Account Factory, 계정 및 전역 사용자 지정을 적용하기 위한 AFT 파이프라인
![[src/Pasted image 20250313170225.png]]

- 클라우드 관리자가 사전 정의된 청사진을 사용하는 예시
![[src/Pasted image 20250313170608.png]]
- Account Factory는 Service Catalog 제품(다른 명칭: **청사진 제품**)을 통해 사용자 지정된 계정을 프로비저닝
### AFC 고려 사항

- AFC는 한 번에 단일 Service Catalog 청사진 제품을 사용하여 사용자 지정을 지원
- Service Catalog 청사진 제품은 허브 계정 및 AWS Control Tower 랜딩 존 홈 리전과 동일한 리전에서 생성
- AWSControlTowerBlueprintAccess IAM 역할은 적절한 이름, 권한, 신뢰할 수 있는 정책을 기반으로 생성
- AWS Control Tower의 동작은 사용자 지정된 계정 또는 사용자 지정되지 않은 계정을 생성하거나 등록하는지에 따라 달라짐.
