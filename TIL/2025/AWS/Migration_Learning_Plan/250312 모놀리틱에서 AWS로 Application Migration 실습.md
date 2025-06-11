- 온프레미스 환경에서 호스팅되는 2계층 웹 애플리케이션의 모델을 AWS로 마이그레이션
- 과정 요약
	- 기존 웹 애플리케이션 탐색
	- MGN을 이용해 어플리케이션을 호스팅 (리호스팅)
	- DMS를 이용해 데이터베이스를 리플랫포밍
	- 마이그레이션 웹 애플리케이션 테스트하고 성공 확인

### 실습 환경 요약
- EC2 인스턴스에서 호스팅되는 2계층 웹 애플리케이션을 소스 인프라로 표시 (온프레미스라고 가정)
![[src/Pasted image 20250312175254.png]]
- EC2와 RDS로 각각 마이그레이션 후의 타겟 인프라
![[src/Pasted image 20250312175327.png]]

## 태스크 1: 마이그레이션 전에 소스 웹 애플리케이션 탐색 및 확인

## 태스크 2: 소스 애플리케이션 서버(SourceWebApp) 다시 호스팅

### 1) 복제 템플릿 설정 구성
- 타겟 서버에서 MGN를 접속
- AWS Application Migration Service 탭 > Settings > Replication template 
	- 서버 설정 변경해서 서브넷을 퍼블릭으로 수정

### 2) 소스 애플리케이션 서버의 마이그레이션 초기화
- 소스 애플리케이션 서버를 MGN에 추가하기위해 소스 애플리케이션 서버의 쉘에서 복제 설치 프로그램 다운로드
- wget로 설치하고 python으로 실행하면 타겟 리전과 IAM 자격 증명을 입력하라고 나타남
- 입력 후에 disk 선택 (전체 옮기는 경우 Enter) 하고 기다리면 마이그레이션 프로그램 설치 (초기화) 진행됨
- 타겟 RDS 인스턴스 엔드포인트를 캡쳐
	- `aws rds describe-db-instances --region us-east-1 --db-instance-identifier targetdb --query 'DBInstances[*].[Endpoint.Address]' --output text`

### 3) 대상 서버의 시작 설정 구성
- 타겟 서버에서 MGN를 접속
	- 소스 서버가 업데이트 된 것을 확인할 수 있음
	- 이 시점에서 마이그레이션 수명 주기는 **Not ready**여야 합니다. 이것은 서버가 초기 동기화 프로세스를 진행 중이며 아직 테스트할 준비가 되지 않은 경우입니다. 데이터 복제는 모든 초기 동기화 단계가 완료된 후에만 시작할 수 있습니다.
- 소스 서버 페이지에서 Launch setting 탭을 선택
	- 일반 설정 수정 : instance type right sizing 끄기
- ec2 launch template 수정 (타겟 인스턴스 사양 및 설정 정의)
	- instance type 설정
	- subnet 설정 : 복제 템플릿에서 했듯이 퍼블릭으로 지정
	- 보안 그룹 설정
	- 공인 IP 자동 설정
	- 리소스 태그에 이름 수정
	- iam 설정
	- 유저 데이터 입력
```bash
#!/bin/bash
RDS=$(aws rds describe-db-instances --region $(curl -s http://169.254.169.254/latest/meta-data/placement/region) --db-instance-identifier targetdb --query 'DBInstances[*].[Endpoint.Address]' --output text) && echo $RDS
sed -i "1,/^$ep/s/'[^']*'/'$RDS'/" /var/www/html/get-parameters.php
```
- 작성한 탬플릿을 적용하기
	- Modify template 페이지에서 기존 시작 탬플릿 체크하고 Actions에서 기본값 버전을 설정 (가장 높은 버전으로 지정)
- 그동안 라이프사이클이 Not ready 에서 Ready for testing으로 변했는지 확인
![[src/스크린샷 2025-03-12 오후 9.42.36.png]]

### 4) 테스트 인스턴스 시작
- MGN에서 Teat and cutover 드롭다운 메뉴에서 test instance 실행 클릭 -> 팝업 클릭
	- 타겟 EC2 인스턴스를 보면 3개가 만들어져 있는 것을 볼 수 있음
![[src/스크린샷 2025-03-12 오후 9.58.52.png]]

- 만들어진 인스턴스의 DNS 주소로 들어갔을 때 Endpoint가 이전에 조회한 타겟 DB 엔드포인트와 동일한지 확인
	- 연결 되었다면 유저 데이터 스크립트가 잘 실행된 것임
	- 이제 MGN의 Test and cutover 탭에서 **Mark 1 server as “Ready for cutover“** 클릭해 상태 변환

### 5) 전환 인스턴스 시작
- MGN의 Test and cutover 탭에서 Launch cutover instances 선택
	- 최종 인스턴스 생성

## 태스크 3: 데이터베이스 서버 리플랫포밍
> 250312 Database Migration Service 실습 참고

### 1) 소스 및 대상 엔드포인트 구성
- 인스턴스는 이미 만들어진 상태
- 소스 / 대상 엔드포인트 각각 만들기

### 2) 데이터베이스 마이그레이션 태스크 구성
- 이름, 복제 인스턴스, 소스 엔드포인트, 타겟 엔드포인트, 선택 규칙 추가 (원하는 DB 데이터만 옮기기)

## 태스크 4: 마이그레이션된 애플리케이션 테스트
- MGN 프로세스에서 Test and cutover 드롭다운에서 Finalize cutover를 선택 

