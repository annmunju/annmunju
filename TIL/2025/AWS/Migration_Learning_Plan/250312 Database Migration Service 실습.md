
## 과제 1: Amazon EC2 인스턴스에 연결
- Fleet Manager에서 RDP를 사용하여 인스턴스에 연결
	- AWS Systems Manager 접속 후 Fleet Manager로 node actions에서 connect 선택해 원격 데스크톱 연결 (키페어로 접속)

## 과제 2: 소스 MySQL 데이터베이스 구성 및 연결
- 원격 데스크톱에 Mysql 설치
	- msi 파일 설치(Connector/Net)
	- server, workbench 설치
- MySQL 서버 구성
	- 루트 비밀번호 입력
	- 관리자 계정 생성
- 워크벤치로 MySQL 서버를 연결해 DB를 만들고 데이터를 불러와 소스 mysql db 구성
	- 데이터 불러오기 : Server > Data Import > Import from Disk 창에서 폴더를 연결해준 후 Import Progress 창에서 > Start Import를 선택
	- 쿼리를 입력해 데이터가 잘 불러와 졌는지 확인
 ![[src/스크린샷 2025-03-12 오후 2.54.06.png]]

## 과제 3: MySQL Workbench를 사용하여 RDS 인스턴스에 연결
- 타겟 데이터베이스의 엔드포인트를 이용해 워크벤치에 connection 등록 후 데이터 없는것 확인

## 과제 4: AWS Database Migration Service를 사용하여 소스 MySQL 데이터베이스를 Aurora 인스턴스로 마이그레이션

### 1) AWS Database Migration Service로 복제 인스턴스 생성
- AWS DMS 복제 인스턴스는 Amazon Elastic Compute Cloud(Amazon EC2) 인스턴스에서 실행됨
	- Multi-AZ 배포를 사용한 고가용성 및 장애 조치 지원을 제공
- DMS -> Replication instances -> Create ... 

### 2) 소스 엔드포인트 생성
- DMS -> Endpoints -> Create ...
	- Source endpoint 
	- Server name은 IP 값을 넣어주면 됨
	- 복제 인스턴스가 활성화 되면 test endpoint connection을 사용해볼 수 있음

### 3) 타겟(Aurora) 엔드포인트 생성
- DMS -> Endpoints -> Create ...
	- Target endpoint
	- 소스 엔드포인트 생성과 동일한 방식으로 만들기

### 4) 데이터베이스 마이그레이션 태스크 생성
- DMS -> Database migration tasks -> Create ...
	- Table mappings에서 add new selection rule를 선택하고
	- Enter a schema 선택  -> Source name에 DB 이름을 넣으면 해당 DB 복제
	- **Premigration assessment** 섹션에서 **Turn on premigration assessment** 선택을 취소
- 태스크 완료 후 워크벤치에서 접속한 타겟 DB에 테이블이 잘 옮겨졌는지 확인