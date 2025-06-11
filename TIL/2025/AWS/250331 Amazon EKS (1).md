
- 컨테이너 개념 소개
	- 베어메탈 -> 가상환경 -> 컨테이너 -> 서버리스
- 도커 
	- 도커 엔진 > 도커파일 > 도커 이미지 > 레지스트리
- Kubernetes
	- 오픈소스 
	1. 클러스터 생성
		1) 컨트롤 플레인: 중앙 관리
			- **API Server** : 여기에 요청 보낼거임
			- etcd : 파드 정보 저장 (저장소). 최소 두대설치하고 동기화.
			- Scheduler : 어디로 배치해야해 
			- Controller Manager 
			- (cloud controller manager : 클라우드 사용시 필요)
		2) 데이터 플레인: 실제 일하는 역할
			- kubelet : 실행
			- kube-proxy : Network
			- container runtime (컨테이너 엔진. 도커)
	2. 파드 구성
		- 파드 : 컨테이너가 독립적으로 실행하면 로그 등을 확인하기 어려움. 동시에 실행해야 하는 컨테이너를 한번에 실행할 수 있는 컨테이너의 그룹.
		1) 주 애플리케이션 + 헬퍼 + 사이드카 ...
		2) IP는 하나만 할당됨
		3) 스토리지 하나를 공유함
		4) 수명주기가 동일함
		5) yaml 파일을 통해 정의함
	3. 서비스 구성
		1) 서비스 만들면 Load balancer 역할을 하게 되는데 기본은 Classic -> ALB 혹은 NLB로 변경해야함.
		2) 

## Pod
### PodSpec으로 Pod 정의
```yaml
apiVersion: v1
kind: Pod
metadata:
	name: webapp
	labels:
		app.kubernetes.io/name: webapp
spec:
	containers:
	- name: nginx
	  image: nginx:1.25.1
	  ports:
	  - containerPort: 80
```

## 서비스
- 하는 일: ELB 역할처럼 쓰임. 중간에서 파드가 다른 파드로 연결할 때 엔드포인트 역할처럼 서비스를 통해서 알맞은 위치로 감.
	- 클러스터가 다를때는 통신 안됨
- 종류 (4가지)
	- Load Balence: CLB로 만들어짐 (기본). NLB / ALB로 바꿔야함. ALB는 추가 제어를 위한 설치가 필요
	- Node Port
- Selector <- 누구에게 갈 것인지. (지정된 label와 동일한 pod로 전달됨)

## 쿠버네티스 내부
- 제어 영역과 데이터 영역으로 구성

### 제어 영역 
- 컨트롤러
	- Auto Scaling을 수행하는 방식과 비슷하게
	- min / desired(원하는 값) / max 사이로 개수가 지정됨. 이 desired를 정하는 역할을 컨트롤러가 수행함
	- 컨트롤러 관리자
	- 클라우드 컨트롤러 (클라우드 사용하면 있음)
- 스케줄러
- etcd (데이터 저장)
> EKS 사용하면 제어 영역은 알아서 관리됨

### 데이터 영역
- 컨테이너 런타임
- kubelet
- kube-proxy: 네트워크 규칙을 유지 관리하고 연결 전달

## Pod 스케줄링
- node 배치를 위한 방법 (어느 node에 위치시킬것이냐)
- 조건자와 우선순위(labels) : 내가 원하는 노드에 pod를 배치하도록 설정
-> 어느 노드에 위치시킬거냐~?

### 조건자: 리소스 요구사항
- 최소 요구사항, 최대 한도를 정의
	- CPU 단위와 Byte 단위로 측정됨.
```yaml
pod resources total
requests:
	cpu: 400m
	memory: 600Mi
limits:
	cpu: 800m
	memory: 800Mi
```
-> 어디에 배포하면 좋을지에 대한 힌트/조건을 줄 수 있는 선행 조건자

### 조건자: 토폴로지 - Taint 및 Toleration
- 해당 노드에는 배치하지 말라는 설정
- Taint
	- 노드에다가 설정하는것.
- Toleration
	- Pod에다가 설정하는 것.
	- 선호도 `affinity:` 해당 조건이 충족해야 적용 (반드시 - 하드 / 보장하지 않음 - 소프트)

### 조건자: 볼륨 요구 사항
- volumeMounts
- volumes

### Lables
- Service Selector에 지정된 키:값과 Pod의 Lables이 동일한 키:값인 곳으로 요청을 전달함
- Node Selector에 지정된 키:값과 Pod의 Lables이 동일한 키:값인 곳으로 요청을 전달함

## Kubernetes 객체
### Pod
### Service
### 네임스페이스
- 클러스터는 물리적(인프라적) / 네임스페이스는 논리적 그룹
- 같은 클러스터에 속하지만 다른 애플리케이션으로 구성되는 경우 이는 네임스페이스로 구별됨
- 파드와 서비스를 묶어주는 개념
### Secrets, ConfigMap
- application에 구성요소들을 별도로 관리하기 위함
### Job, CronJob 
- 배치와 병렬 작업을 위해 사용
### DaemonSets
> 노드 에이전트용 워크로드
- 로그 수집기 Fluent bit와 같은 pod를 노드에 설치
	- 노드에 하나만 설치해도 되는 워크로드
### ReplicaSet
> 스테이트리스 앱 복제본용 워크로드
- pod에 복제본이 여러개 필요한 경우
### Deployment 및 ReplicaSet
- 배포를 위한 (버전 업데이트 등) 워크로드 설정
- deployment에 원하는 상태를 기술하고 원하는 상태로 변경함.
```yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
	name: webapp-deployment 
	labels: 
		app: webapp 
spec: 
	replicas: 4 
	selector: 
	matchLabels: 
		app: webapp 
	template: 
		metadata: 
			labels: 
				app: webapp
		spec:
			containers:
			- name: webapp 
			  image: webapp:22.04
			  command: ["echo"]
			  args: ["..."]
			  ports:
				- containerPort: 80
```
### StatefulSet
- 상태 저장이 필요한 워크로드 설정
```ymal
apiVersion: apps/v1
kind: StatefulSet
metadata:
	name: mysql
spec:
	serviceName: "mysql"
	replicas: 2
	selector:
		matchLabels:
			app: mysql
	template:
		metadata:
			labels:
				app: mysql
		spec:
			containers:
			- name: mysql
			  image: mysql
			  env:
				- name: MYSQL_ALLOW_EMPTY_PASSWORD
				  value: "true"
```

-> 이와 같은 방식들로 yaml 을 정의하고
kubectl apply -f .yaml로 적용하면 됨.

### 관리형 노드그룹 -> Fargate
- 제약사항 많음. 미리 검토후 작업.
- pod 예약이 편리함

## 실습1: Kubernetes Pod 배포
#### 목표
- Kubernetes 애플리케이션을 생성하고 배포합니다.
- 배포, 서비스 및 네임스페이스 리소스를 빌드합니다.
- 네임스페이스에서 리소스를 봅니다.
- 서비스 및 배포의 세부 정보를 분석합니다.
- Pod의 세부 정보를 이해합니다.
- Pod에서 명령을 실행합니다.
- 활성 및 준비 상태 프로브를 구현합니다.
- 애플리케이션을 삭제합니다.

1. 환경 확인
	1. kubectl 설치되었는지 확인하기
	2. 생성된 네임스페이스를 확인하기
	3. 배포된 리소스를 확인하기: `kubectl get deploy,svc,pod -n workshop`
2. 파드를 생성하기 위한 매니페스토 파일 작성
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name:  proddetail
  namespace: workshop
spec:
  replicas: 1 #리플리카 세트를 사용
  selector:
    matchLabels:
      app: proddetail
  template:
    metadata:
      labels:
        app: proddetail
    spec:
      containers:
        - name: proddetail
          image: "public.ecr.aws/u2g6w7p2/eks-workshop-demo/catalog_detail:1.0"
          imagePullPolicy: Always
          ports: #포트 개방
            - name: http
              containerPort: 3000
              protocol: TCP
          resources: {}
```
 - _selector_ 필드는 **ReplicaSet이 관리해야 할 Pod를 식별**하는 데 사용한다. 이 ReplicaSet는 매니페스트에 _app: proddetail_ 레이블이 포함된 모든 Pod에 적용됩니다.

> service 정의 매니페스토 파일
```yaml
# service
apiVersion: v1
kind: Service  #단일 네트워크 엔드포인트 제공
metadata:
  name: proddetail
  namespace: workshop
  labels:
    app: proddetail
  annotations:
    owner: student
spec:
  type: ClusterIP #클러스터 내부에만 접근 가능한 가상 IP 생성
  ports:
    - port: 3000 #클러스터 내부에서 노출하는 포트번호
      name: http
  selector:
    app: proddetail #해당 레이블을 가진 pod를 선택해 트래픽 전달
```
- _spec_ 필드는 서비스 상태를 정의합니다. 이 경우에는 _ClusterIP_ 서비스를 생성합니다. 이는 기본 서비스 유형이며 클러스터 내부에서만 액세스할 수 있습니다. _NodePort_ 또는 _LoadBalancer_ 유형으로 설정된 서비스는 클러스터 외부로부터의 요청을 수락합니다. 또한 이 서비스는 포트 3000에서 HTTP 트래픽을 수락하도록 설정됩니다.
3. 2번에서 작성한 매니페스토 파일을 통해 클러스터에 적용
4. 애플리케이션 리소스 탐색
	- 배포된 서비스의 세부 정보 보기 `kubectl describe service proddetail -n workshop`
	- 배포된 서비스에 가장 최근 생성된 pod를 임의로 하나 지정해서 pod 이름을 환경 변수로 받아둠 `export DETAIL_POD=$(kubectl get pods -n workshop --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[2].metadata.name}') && echo $DETAIL_POD`
	- 임의의 pod에 대한 세부 정보 확인 `kubectl describe pod $DETAIL_POD -n workshop`
	- pod bash에 연결 `kubectl exec -it $DETAIL_POD -n workshop -- /bin/bash`
5. 프로브 구현 (Health check와 비슷)
	1) livenessProbe: Auto-scaling 처럼 실패시 새로 생성
	2) readinessProbe: ELB 처럼 실패시 생성하지 않고 기존 살아 있는 곳으로만 요청 보냄
```ymal
apiVersion: apps/v1
kind: Deployment
metadata:
  name:  proddetail
  namespace: workshop
spec:
  replicas: 1
  selector:
    matchLabels:
      app: proddetail
  template:
    metadata:
      labels:
        app: proddetail
    spec:
      containers:
        - name: proddetail
          image: "public.ecr.aws/u2g6w7p2/eks-workshop-demo/catalog_detail:1.0"
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /ping
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 1
            successThreshold: 1
            failureThreshold: 3
          readinessProbe:
            exec:
              command:
                - /bin/bash
                - -c
                - cat readiness.txt | grep ready
            initialDelaySeconds: 15
            periodSeconds: 3
```
6. 프로브 사용하기
	- livenessProbe 작동 확인을 위한 ping 호출하기
		- `curl http://proddetail.workshop.svc.cluster.local:3000/injectFault && while sleep 5; do printf "\n...Getting detail status... " && curl http://proddetail.workshop.svc.cluster.local:3000/ping; done`
		- 컨테이너 종료 확인 `kubectl get event -n workshop --field-selector involvedObject.name=$DETAIL_POD`
		- 컨테이너 재시작 확인 `kubectl get pod -n workshop -l app=proddetail`
	- readinessProbe 작동 확인을 위한 코드 입력
		- readiness 구성 확인 `kubectl describe pod -l app=proddetail -n workshop | grep Readiness:`
		- replicaset 구성 확인 `kubectl describe replicaset proddetail -n workshop`
		- readiness.txt 파일을 업데이트
		  `kubectl exec -it  $DETAIL_POD -n workshop -c proddetail -- sed -i 's/ready/fail/' readiness.txt` -> 이러면 실패됨
		- readiness.txt 파일 원복
		  `kubectl exec -it  $DETAIL_POD -n workshop -c proddetail -- sed -i 's/fail/ready/' readiness.txt && kubectl get deployment proddetail -n workshop --watch`
7. 애플리케이션 삭제
	- `kubectl delete namespace workshop`