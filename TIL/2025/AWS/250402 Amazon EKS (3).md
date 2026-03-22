# EKS 네트워킹 관리

## 서비스 타입 4종류
### ClusterIP
- 내부에서 트래픽을 전송하기 위한 서비스의 종류
- cluster internal ip address 전송

### NodePort
- 노드의 포트를 열어줌
	- 노드는 EC2  (IP가 제한적임)

### LoadBalancer
- 트레픽 분산을 클러스터 밖에서 수행
- 클라우드의 로드밸런서를 함께 써야함

### ExternalName
- 도메인 이름 만들어서 제공할 때 사용

## Observability : 관찰 가능성
> 데이터 또는 프로세스를 분석하고 볼 수 있는 기능
- 지표 수집 (리소스 관련 상태, 성능 모니터링 할 수 있도록 정의 및 수집) - prometheus, cloudwatch
- 로그 수집 (인사이트를 위한 필터링) - opensearch, cloudwatch
- 추적 (요청 경로 추적) - x-ray, openserch

## 실습 4) ...


---

# EKS 스토리지 관리

- 컨트롤 플레인에 있는 컨트롤러 매니저가 관리하는 컨트롤러 오브젝트 종류 중 Set 
	- DeamonSet
	- Deployment -> ReplicaSet (pod 생성)
	- **StatefulSet**

### StatefulSet
- 상태 저장해야하는 파드
- DB 등
- PV, PVC가 붙음

## 스토리지 옵션
- 볼륨 스토리지 
	- 길이가 정해져 있는 블록
	- 저장할 때 블록 길이를 초과하면 여러 블록으로 쪼갬
	- 읽어올 때 블록 여러개를 한번에 가져와서 돌려줌
	- 볼륨 서버와 EC2 서버 둘이 붙여서 쓰는거. 볼륨은 하나의 EC2에 여러개를 붙일 수 있음
	- AZ 단위. 서브넷 내부에 만들어야함
- 파일 스토리지
	- 네트워크 스토리지
	- 운영체제 별로 파일 형식이 상이함
	- 파일 시스템이 정해져 있는 스토리지
	- EFS는 nfs4 형식만 사용
	- 리전 단위. VPC 내부에 만들어야함. 다만 어느 리전에나 마운트할 타겟이 존재해야함.

### EKS에서 스토리지
1. 볼륨 스토리지 (EBS)
	- 임시 볼륨으로 사용
	- `volume > > entryDir: {}`
2. 파일 스토리지 (EFS)
	- 영구 볼륨으로 사용

### 영구 볼륨 수명 주기
1. PV를 프로비저닝
2. PVC(클레임. 요청하는 것)에 바인딩
3. pod에 볼륨에서 pvc로 요청해서 pv에 요청함
4. 필요 없으면 영구 볼륨에서 삭제 (회수)

### 매니페스토 작성
1. 영구 볼륨 종류로 작성 (kind PersistentVolume)
	- accessModes, csi 드라이버, 볼륨 id 기록
	- 얼만큼 쓸건지 기록
2. 영구 볼륨 클레임 작성 (kind PersistentVolumeClaim)
	- 영구 볼륨과 동일한 스펙으로 작성
	- 쓰기 요청을 보냄
	- 프로비저닝 됨. (스토리지 클레스를 사용하면 동적 할당)
3. PVC를 볼륨으로 사용
	- pod 설정 (kind Deployment 혹은 pod)에서 volume을 pvc로 요청
	- `persistentvolumeClaim: claimName: my-pvc`
![[스크린샷 2025-04-02 오후 3.18.47.png]]

#### 스토리지 클래스를 사용해서 동적 할당하기
- Storage class를 사용하면 PV를 자동 생성함
- 그래서 pvc만 생성시 바인딩
- 스토리지를 자동 생성하고(프로비저닝) 바인딩 됨 (용량 설정을 안함)

![[스크린샷 2025-04-02 오후 3.45.25.png]]

- 해당 기능 사용하려면 CSI 드라이버 필요
- CSI 드라이버가 파드에서 AWS 서비스를 이용하고자 할 때 역할이 필요. 이는 CSI 드라이버의 Service Account를 사용

### EFS를 영구 볼륨으로 사용
- 가용영역과 무관하게 다양한 node, pod 복제본에서 같은 경로로 마운트해서 사용

## Secret 관리
- pod의 환경 변수로 사용
- env: secretKeyRef ...

### AWS Secrets Manager and Configuration Provider(ASCP)
- eks에서 실행되는 pod가 secret에 액세스할 수 있음
- IRSA를 사용(OIDC 인증)하는 IAM 정책으로 Secret 액세스를 특정 Pod로 제한

# EKS 보안 관리
- IAM : AWS꺼
- RBAC (Role based account control) : k8s꺼
	- RBAC Service Account를 사용한 pod 권한 관리
![[스크린샷 2025-04-02 오후 4.08.13.png]]

- k8s에서 role은 권한

### 권한
![[스크린샷 2025-04-02 오후 4.12.00.png]]
- k8s api로 요청하고 인증은 IAM 통해 받고 권한은 RBAC으로 받음
- Kubernetes용 IAM Authentication
	- 콘솔에서 eks > cluster > Configuration > Authentication > OIDC 인증 사용할 수 있음
	- OIDC 인증
		- JWT 토큰 발급해주는거.
		- IAM 권한 사용하려면 역할 필요

### IAM 
- AWS 서비스 외부의 (페더레이션 서비스) 인증과 권한
	- STS : accesskeyid, security access key, session token(ak, sak가 유효한지 확인해주는게 세션 토큰) 발급 <- 인증
	- Role (Policy 설정됨) <- 권한

### RBAC 
- 주체 : 주로 Service Account
- 리소스 + 작업 <= Role (clusterRole) : AWS IAM에서는 정책과 같은 역할.
![[스크린샷 2025-04-02 오후 4.48.50.png]]

- cluster-admin의 RBAC 역할 관리
	- 자동 생성되는 그룹
- RBAC Service Account를 사용한 Pod 권한 관리
	- 같은 노드(EC2) 안에서 파드 별로 다른 권한을 주고 싶을 때 IRSA(Service Account에 권한주기) 해야함

#### k8s -> k8s 사용할 때 순서
- rbac으로 역할을 만들기
- service account 생성. 일반적으로 name space에서 하나 사용
- 그리고 바인딩하기

#### k8s -> AWS api 사용할 때 순서
> IRSA 사용. k8s 서비스 어키운트가 jwt를 발급해 사용할 수 있게 oidc에 권한 부여
1. aws IAM OIDC 공급자 생성
2. iam 역할 생성

