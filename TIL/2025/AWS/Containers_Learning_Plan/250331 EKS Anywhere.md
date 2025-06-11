
- Amazon EKS Anywhere: Amazon EKS용 오픈 소스 **온프레미스** 배포 옵션
	- AWS 서비스와 통합 제공
	- Amazon EKS 서비스에서 사용하는 쿠버 배포 버전 일치

### 기술적 개념
- Amazon EKS Connector
	- 쿠버네티스 클러스터를 EKS 콘솔에서 연결하고 볼 수 있음
- Amazon EKS-Anywhere 큐레이팅된 패키지
	- Amazon 서명 이미지 제공 및 액세스
- 클러스터 구성 (yaml 파일)
- 패키지 컨트롤러
- GitOps : CICD 도구 등의 Devops 모범사례를 가져와 인프라 자동화에 적용하는 운영 프레임워크
- IRSA : Service Account의 IAM 역할. 서비스 액세스 권한 제공 IAM 역할을 생성할 수 있음. 온프렘-AWS 서비스 통합 가능

## 설치
### 사전 조건
1. eksctl cli 도구 설치
2. amazon eks anywhere 플러그인 설치
3. 도커 공급자 설치

### 클러스터 생성
1. 클러스터 구성 정의 
	- eksctl anywhere cli 도구 이용 `eksctl anywhere generate clusterconfig $CLUSTER_NAME --provider docker > $CLUSTER_NAME.yaml`
2. 클러스터 생성
	- `eksctl anywhere create cluster -f $CLUSTER_NAME.yaml`
3. 클러스터 액세스
	- `kubectl get ns`

### 클러스터에 애플리케이션 배포
`kubectl apply -f "https://anywhere.eks.amazonaws.com/manifests/hello-eks-a.yaml"`
