- 개념/용어
	- Node: 컨테이너를 파드에 그룹화하고 워크로드 실행. 노드는 VM (EC2) 일 수 있음.
	- Pod: 하나 이상의 컨테이너로 구성된 그룹. 배포 크기 조정 및 복제를 위한 kubernetes 기본 빌딩 블록. 배포 기본단위.
	- 휘발성 볼륨 / 영구 볼륨
	- 서비스: 파드의 논리적 컬렉션. 파드 세트를 바탕으로 구성됨
	- 네임 스페이스: 동일한 물리적 클러스터에서 지원되는 가상 클러스터. 여러 팀이나 프로젝트가 동일한 클러스터를 사용할 때 유용
	- ReplicaSet: 주어진 시간에 특정 개수의 파드 복제본이 실행되도록 함
	- 배포: ReplicaSet 또는 개별 포드를 소유하고 관리
	- ConfigMap: 파드에서 사용하는 키-값 쌍 데이터 저장 API 객체
	- 보안 정보: 민감 정보 액세스 제한

### 파드 예약
![[Pasted image 20250331135320.png]]

### EKS 클러스터 구조
![[Pasted image 20250331135919.png]]
- 제어 영역(control plain)
- 데이터 영역(data plain)

- 관련 사항
	- 사용자 지정 리소스
		- CRD 를 사용해 생성됨
		- 사용자 지정 컨트롤러로 사용자 지정 리소스를 제어할 수 있음. 작업자 노드에 있는 파드에서 실행됨.
		- 객체를 수동으로 업데이트 하는 대신 운영자 사용하기
	- kubectl : CLI 도구

## EKS
- 제어 영역을 관리함
- 가용성 및 API 
	- 3개 가용영역에 걸친 최소 2개의 API 서버 노드와 3개의 etcd 노드로 구성
![[Pasted image 20250331152020.png]]
### eksctl vs kubectl
- eksclt
	- 제어 영역
	- AWS 서비스를 활용한 데이터 영역(노드 배포) 관리
- kubectl
	- 파드 목록 확인 등
	- 네임스페이스, 배포와 같은 쿠버네티스 객체 관리에 사용

### 관리 정도에 따른 서비스 구분
1. (고객 관리 영역이 가장 큼) 제어 영역만 EKS에서 관리. 데이터 영역 노드 (프로비저닝, 업데이트, 모니터링 및 기타 작업) 완전 제어해야함
2. (AWS가 일부 관리) 관리형 노드 그룹: EC2의 일부 서비스를 제공. 프로비저닝(AMI, Auto Scaling 그룹), 관리(CloudWatch 로그 등), 업데이트, 크기 조정 제공
3. (AWS가 많은 부분 관리) AWS Fargate: 데이터 영역 전체 인프라를 관리함. 파드 실행에만 신경쓰면 됨 
-> 공동 책임 모델 적용하여 AWS 많은 부분 관리할수록 . 더많은 부분을 책임짐

### 인증 및 권한 부여
- AWS API를 사용하는 경우 IAM 서비스를 이용해 인증과 권한을 부여함
- kubernetes api 사용하는 경우, 
	- 클러스터에는 IAM 사용자 인증을 사용하지만
	- 권한 부여에는 기본 Kubernetes RBAC(역할 기반 엑세스 제어)에 의존함
![[Pasted image 20250401113425.png]]
1) kubectl 요청 
2) kube api에서 iam 인증으로 요청. 요청 확인 후 토큰을 보내줌
3) kube api에서 토큰을 이용해 RBAC 확인 후 허용되면
4) kubectl로 반환

### 권한 구성
- 클러스터 IAM 역할: eks에서 클러스터 관리(클러스터 생성 및 삭제 등)를 위한 aws api를 호출할 권한
- 노드 IAM 역할: eks에서 kubelet을 이용해(ecr 접근 등) aws api를 호출할 권한
- RBAC 사용자: kube api 호출 권한은 iam 역할을 rbac 사용자에 매핑하여 이뤄짐

### 네트워크 구성
- 퍼블릭 서브넷만
- 프라이빗 서브넷만
- 퍼블릭 & 프라이빗 서브넷 동시에 사용
![[Pasted image 20250401114910.png]]

### 클러스터 생성
- AWS CLI
- eksctl(선택)

### 오토 스케일링
- 파드 수를 조정
	- HPA
- 파드 리소스를 조정
	- VPA
- 노드 수를 조정
	- CA
- Karpenter

## EKS의 통신 관리
### 1. 파드 간 통신
- 모든 컨테이너는 파드 내 다른 모든 컨테이너와 통신할 수 있음
- 파드 하나당 IP 하나 부여
### 2. 호스트 간 통신
- 파드와 호스트는 독립된 네임스페이스를 가짐
	- 파드 네임스페이스: 고유 IP, 라우팅 테이블, 네트워크 인터페이스를 가짐
	- 호스트 네임스페이스: 노드 기본 네트워크 설정을 관리
- 파드와 호스트 네임스페이스를 연결하는 가상 터널 역할 : veth 쌍
	- 한쪽은 pod 내부에, 다른쪽은 호스트 브릿지에 연결해서 파드의 트래픽이 호스트브릿지를 통해 외부로 전달됨
- 각 노드에 컨테이너 네트워크 범위가 할당되고 각 파드는 동일한 호스트에 있는 컨테이너들이 통신할 수 있도록 해당 범위의 IP 주소를 가져옴

![[Pasted image 20250401125153.png]]
- vpc cni를 이용해서 노드와 파드가 서로 통신하는 방식을 단순화함
	- CNI: 네트워크 관리자. 파드에게 IP 주고 통신 경로 설정
	- 파드가 실제 VPC의 IP 주소를 그대로 사용할 수 있게 함
1. 노드에 가상 네트워크 카드 장착 (ENI)
2. 새 파드가 생성되면 CNI 플러그인이 ENI 보조 IP 중 하나를 파드에게 줌
3. 파드가 해당 IP로 다른 파드나 AWS 서비스에 직접 통신하게 함.

### EKS의 서비스 객체
1. ClusterIP
	- 적절한 파드에 매핑되는 정적 혹은 동적 IP 주소 할당
2. NodePort
	- 정적 포트로 각 노드에 노출되며 클러스터 **외부에서 액세스 할 수 있음** - clusterip와 연결
3. LoadBalancer
	- 클라우드의 로드벨런서와 함께 노드 간 로드 균형. 모든 노드 앞에 로드벨런서를 추가하여 Nodeport 서비스 확장 - nodeport, nodeip와 연결
4. ExternalName
	- 내부 IP 주소인 클러스터IP를 외부 DNS 이름과 연결. 클러스터 내부에 있는걸로 보이는데 실제론 외부에 있는거.
	- 외부 데이터베이스 등에 사용

### 수신 Ingress 인그레스
- 클러스터 외부에 있는 HTTP 및 HTTPS 경로를 서비스에 노출하고 트래픽 규칙을 정의

- 로드벨런서 컨트롤러 : 클러스터용 LB 컨트롤러
	- 로드벨런서 유형은 ALB, NLB
	- Application Load Balancer는 노드 또는 Fargate에 배포된 포드와 함께 사용, 퍼블릭 또는 프라이빗 서브넷에 배포될 수 있음
	- Network Load Balancer는 Amazon EC2 IP및 인스턴스 대상에 배포된 포드나 Fargate IP 대상에 네트워크 트래픽을 로드 밸런싱할 수 있음


## EKS에서 스토리지 관리
- 영구 볼륨(PV) 및 영구 볼륨 클레임(PVC)
- 사용하고자 하는 스토리지에 맞는 CSI (Container Storage Interface) 드라이버 설치
- EBS 사용
![[Pasted image 20250401142556.png]]
- EFS 사용
![[Pasted image 20250401142611.png]]
### Fargate - 스토리지
- CSI 드라이버 구성 없이도 EFS 파일시스템을 자동으로 탑재

## EKS에 애플리케이션 배포
- CI/CD
- 관련 서비스
	- Github repo
	- Jenkins
	- Harbor: 컨테이너 이미지에 스캔을 실행하여 취약성 보안문제 없음을 확인
	- Spinnaker: 배포 자동화 / ArgoCD
	- Helm
![[Pasted image 20250401153646.png]]

## 모니터링
### CloudWatch와 Container Insight
![[Pasted image 20250401153753.png]]
### 오픈소스 이용한 모니터링
![[Pasted image 20250401154032.png]]

## AWS App Mesh
- 서비스 메시
	- 서비스 간 통신을 원할하게 함
- App Mesh: 통신 관리자와 Envoy 프록시. 서비스 프록시를 붙여 중계.
	- 서비스가 어디로 통신할지 메시지 경로 설정
	- 트래픽 제어
	- 문제 감지
	- 메시지 암호화
	- 실시간 모니터링

## 추가 기능
- Amazon VPC CNI
- kube-proxy
- CoreDNS
-> 파드로 실행됨

## 비용
- 컴퓨팅 리소스 (EC2 / Fargate 등...)
- 네트워킹 서비스 (로드밸런서, NAT 등)
- EKS 클러스터
---


- kubectl cli
```bash
# 실행중인 파드
kubectl get pod

# 실행중이 아닌 파드
kubectl describe pod <pod name> -n <namespace of the pod>
kubectl get pod <pod name> -n <namespace of the pod> -o yaml
kubectl logs <pod name> -n <namespace of the pod>
# 파드 이름이나 네임스페이스를 모르는 경우, 등록된 파드 목록
kubectl get pods -A -o wide

# DNS 엔드포인트 확인
kubectl get pod -n kube-system -l k8s-app=kube-dns -o wide
kubectl -n kube-system get endpoints kube-dns

# 서비스 상태 표시
kubectl get services -A

# 서비스 엔드포인트 확인 및 서비스 시작하지 않은 이유
kubectl describe service  -n 

# 노드 목록
kubectl get nodes

# 노드 실행 중이 아닌 이유 확인
kubectl describe nodes
```
