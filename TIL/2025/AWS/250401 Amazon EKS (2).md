### eksctl로 클러스터 생성
- `eksctl create cluster ...` 파라미터 하나씩 다 추가하고 실행하기 (아니면 기본값)
- 혹은 cluster.yaml 파일 생성 후 `eksctl create cluster -f cluster.yaml`
```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: MySecondEKScluster
  region: us-east-1
vpc:
  subnets:
    private:
      us-east-1b: { id: subnet-0fdd9b15cb2da9ce6 }
      us-east-1c: { id: subnet-061bff24d18088fd5 }
nodeGroups:
  - name: ClusterTwoNodes
    instanceType: m5.xlarge
    desiredCapacity: 3
    privateNetworking: true
```

### 업그레이드
- 컨트롤 플레인은 AWS가 알아서
- 데이터 플레인은 알아서 업그레이드 하거나, eksctl을 통해서 무중단으로 업그레이드

## EKS 클러스터에 애플리케이션 배포

- 배포 크기 조정 방법
	1. 컨테이너 이미지 리포지토리를 선택한다
	2. 패키지 관리자 또는 애플리케이션 배포 도구를 선택한다
	3. CI/CD 파이프라인 자동화
### Helm
- 패키지 관리자 Helm
	- 애플리케이션 설치, 제거, 버전 관리 등등
- 차트 분석: 애플리케이션에 필요한 모든 객체를 패키징
	- /charts/myapp/
		- chart.yaml
		- templates/ <- 동작하고자 하는 어플리케이션의 pod 매니페스토
			- deployment.yaml
			- secrets.yaml
			- service.yaml
		- values.yaml <- 변수를 제어하는 파일

## 대규모 어플리케이션 
### 자동 크기 조정
- HPA (Pod 수 축소 또는 확장) 
	- `kubectl autoscale deployment myapp --cpu-percent=50 --min=3 --max=10`
- VPA (Pod의 리소스를 확장 또는 축소)
- Cluster Autoscaler (Auto Scaling 그룹을 이용해 노드를 확장 또는 축소 -> 느림)
- Karpenter (AS와 무관하게 노드를 확장 또는 축소)

#### VPA
- yaml 파일로 pod에 작성해둔 spec에서 request의 메모리, cpu가 남는 경우 고려
- 모드
	- Off (기본값) : 권장되는 크기만 게시하며 변경되지 않음
	- Initial : Pod 생성될 때만 크기를 조정
	- Auto : 기존 Pod를 재시작하여 크기를 조정
- 클러스터에 3개 배포로 실행된다
	- 확인하는 파드 (총괄)
	- 용량 변경을 추천하는 파드
	- 업데이트 하는 파드

#### Cluster Autoscaler
- Auto Scaling 그룹의 최대 최소 노드 크기를 기반으로 필요에 맞게 증가, 감소함
- Auto Scaling
	- Launch Template : EC2 어떻게 만들건지 미리 설정
	- ASG : min / max / desired 설정
	- 언제? 

#### Karpenter
- 아래 두 종류의 매니페스토 파일 정의 필요
- EC2NodeClass: EC2 인스턴스를 생성할 때 사용할 공통 설정을 정의하는 리소스. Karpenter가 관리할 노드 그룹을 정의
```yaml
apiVersion: karpenter.k8s.aws/v1beta1
kind: EC2NodeClass #ec2에 대한 조건
metadata:
  name: example-ec2nodeclass
spec:
  amiFamily: AL2
  blockDeviceMappings:
  - deviceName: /dev/xvda
	ebs:
	  deleteOnTermination: true
	  encrypted: true
	  ...
  subnetSelector:
    karpenter.k8s.aws/subnet-name: "my-subnet"
  securityGroupSelector:
    karpenter.k8s.aws/security-group-name: "my-sg"
  role: "arn:aws:iam::123456789012:role/KarpenterNodeRole"
```

- Nodepool: EC2 인스턴스 그룹을 정의하는 리소스. 노드를 언제 얼마나 만들지 결정하는 정책
```yaml
apiVersion: karpenter.k8s.aws/v1beta1
kind: NodePool #일반적인 노드에 대한 조건
metadata:
  name: example-nodepool
spec:
  template:
    spec:
      nodeClassRef:
        name: example-ec2nodeclass #위에 정의한 노드 클래스 이름을 넣음
      requirements:
        - key: "karpenter.k8s.aws/instance-category"
          operator: In #아래 안에 포함되면 된다
          values: ["c", "m"]
  limits:
    cpu: "1000"
  disruption:
    consolidationPolicy: WhenUnderutilized
```
-> Deployment 파일에서의 requests 참고 + 위 두파일 참고해서 가장 알맞는 노드를 자동 배포
- requests에 `maxSkew`(차이 최대 수) 이 있는 경우 쏠림 없이 분배시키도록 함. (/hostname이면 같은 노드에 쏠리지 않게 파드 분배. /zone이면 같은 가용영역에 쏠리지 않게 노드 분배)

### CI/CD
- CI
	- 코드 > 빌드 > (테스트)
	- 컨테이너 이미지로 만드는 과정까지
- CD
	- (코드 > 빌드 > 테스트 >) 프로비저닝 > 배포 > 모니터링
	- 이미지를 만든 다음


## 실습 2. Helm 및 S3를 사용한 애플리케이션 배포
- Helm 차트의 기본 구조를 정의합니다.
- Helm 리포지토리로 사용할 Amazon S3 버킷을 설정합니다.
- 차트를 생성하고 S3 리포지토리에 업로드합니다.
- S3 리포지토리에서 Helm 차트를 패키징 및 설치합니다.

1. helm 설치, helm-s3 플러그인 설치 `helm plugin install https://github.com/hypnoglow/helm-s3.git`
	- helm 리포로 사용할 s3 초기화 `helm s3 init s3://$S3_BUCKET_NAME`
	- 초기화 확인 `aws s3 ls $S3_BUCKET_NAME` <- index.yaml 만 있음
	- 버킷을 helm 클라이언트용 차트 리포로 추가 `helm repo add productcatalog s3://$S3_BUCKET_NAME`
2. 애플리케이션 차트를 패키징하고 S3로 푸시
	- https://github.com/aws-containers/eks-app-mesh-polyglot-demo 해당 레포에 예제 가져와서 패키징한다...
	- 패키징 명령어 `helm package (폴더명)`
	- s3로 푸쉬 `helm s3 push ./productcatalog_workshop-1.0.0.tgz productcatalog`
3. helm 차트 검색 및 설치
	- 차트 버전 확인 (검색) `helm search repo`
	- 리소스 설치 테스트 `helm install productcatalog s3://$S3_BUCKET_NAME/productcatalog_workshop-1.0.0.tgz --version 1.0.0 --dry-run --debug`
		- _–dry-run_: Helm에게 차트를 검증하고 실제로 배포하지 않고 리소스 매니페스트를 생성하도록 지시합니다. -> 잘 성공하면..
	- 이제 설치 `helm install productcatalog s3://$S3_BUCKET_NAME/productcatalog_workshop-1.0.0.tgz --version 1.0.0`
	- 리소스 확인 `kubectl get pod,svc,deploy -n workshop -o name`
4. Helm 차트 편집 및 재배포
	- 내용 수정하고
	- 업그레이드 `helm upgrade productcatalog (폴더명)
	- 롤백 `helm rollback productcatalog 1`


## GitOps 및 EKS
- 개발자 애플리케이션 코드와 운영 인프라 코드 모두 Git으로 관리
- 시나리오
	1. 애플리케이션 코드 변경
	2. 젠킨스가 컨테이너 이미지를 빌드해서 ECR로 푸시
	3. argocd에 매니페스토 파일에 있는 이미지 태그 업데이트
	4. argocd가 변경 사항을 감지하고 eks를 원하는 상태로 업데이트
	5. eks가 새 이미지를 가져오고 pod를 배포
		- rolling 혹은 blue/green 혹은 canary 방식

## EKS에서의 네트워킹 관리

### 컨테이너 간 통신
- 파드 내부에서 (동일한 IP 안에서) 127.0.0.1 (local 통신. 루프백) 로 포트번호만 다르게 구성되어 통신 가능
- 스토리지도 공유

### 파드 간 통신
- IP가 다른 두 파드 간 통신
- **VPC CNI** 설치하면 같은 클러스터 내에서는 알아서 통신 가능. 마치 라우팅 테이블이 각각 있는 것 처럼
- 서비스로 통신 (ClusterIP, NodePort)

### 클러스터로 수신
- 서비스로 통신


### Pod 수준 보안 개선
- VPC CNI
	- 파드에 보안그룹을 만들어주는 것처럼 해줌
- kind NetworkPolicy 적용하면
	- 파드에 IP 범위를 제한하고 달리 사용해서 각각의 파드들이 보안그룹을 가지는 것 처럼 작동
1. 전체 거부 만들기 
2. 백엔드의 정책 만들기 (프론트에서 접근할 수 있는 허용 규칙)
3. 프론트의 정책 만들기 (외부에서 접근할 수 있는 허용 규칙)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: web
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: web
spec:
  podSelector:
    matchLabels:
      app: webapp
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nginx
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nginx-allow-external
  namespace: web
spec:
  podSelector:
    matchLabels:
      app: nginx
  ingress:
  - ports:
    - port: 80
    from: []
```