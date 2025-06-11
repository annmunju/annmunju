- EC2의 역할
	- 컨테이너 예약
	- 컨테이너 수명 주기 관리
	- 컨테이너 런타임 요구 사항 
		- 로드벨런서, 서비스 검색, 오토 스케일링, 시크릿 관리 등
- 기술적 개념
	- 클러스터
	- 컨테이너, 이미지
	- 태스크 정의
	- 태스크
	- 서비스
![[Pasted image 20250404154749.png]]

1. 클러스터 생성
2. 태스크 정의 생성 
	- 태스크 역할 설정
	- ECR 이미지 사용하여 컨테이너 정의 저장
3. 태스크 시작
	- 클러스터명, 태스크 수 선택
4. 서비스 로드밸런싱 구성
	- EC2 > 로드밸런서 생성
	- EC2 보안그룹 선택
	- 타겟 그룹 생성
	- ECS 콘솔에서 태스크 정의 선택하고 서비스 생성
	- 서비스에서 태스크 수 설정하고 로드발란서 붙이기
	- 로드벨런서의 DNS로 접속
- ---

## Managing the Application Lifecycle in Amazon ECS

- 클러스터 > 서비스 > 태스크 (노드와 같은 역할)
- 인프라 배포 도구
	- 클라우드포메이션
	- AWS CDK
	- AWS Copilot
	- AWS Proton
	- AWS App2Container(A2C)
- cloud formation 템플릿
```yaml
ECSCluster:
  Type: 'AWS::ECS::Cluster'
  Properties:
    ClusterName: MyFargateCluster
    CapacityProviders:
      - FARGATE
      - FARGATE_SPOT
    DefaultCapacityProviderStrategy:
      - CapacityProvider: FARGATE
        Weight: 1
      - CapacityProvider: FARGATE_SPOT
        Weight: 1
```

```json
"ECSCluster": {
    "Type": "AWS: : ECS: : Cluster",
    "Properties": {
        "ClusterName": "MyFargateCluster",
        "CapacityProviders": [
            "FARGATE",
            "FARGATE_SPOT"
        ],
        "DefaultCapacityProviderStrategy": [
            {
                "CapacityProvider": "FARGATE",
                "Weight": 1
            },
            {
                "CapacityProvider": "FARGATE_SPOT",
                "Weight": 1
            }
        ]
    }
}
```


- CDK python
```python
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    core,
)


class BonjourFargate(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC and Fargate Cluster
        # NOTE: Limit AZs to avoid reaching resource quotas
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2
        )

        cluster = ecs.Cluster(
            self, 'Ec2Cluster',
            vpc=vpc
        )

        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options={
                'image': ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
            }
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )

        core.CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )

app = core.App()
BonjourFargate(app, "Bonjour")
app.synth()
```


### CICD

- 태그 지정시 latest 사용하지 않기
	- 고유한 태그 생성하기
- **DevSecOps** 구현
	- 이미지 보안을 검증하는 도구 사용하기 (ECR 이미지 스캐닝)
- 구축과 배포 도구
	- 오케스트레이션 : CodePipeline 사용 등
	- 서드파티 도구: Github Action 사용시
		- configure-aws-credentials: AWS 자격 증명을 GitHub Actions 비밀로 저장하고 AWS 액세스 권한을 사용하여 GitHub Actions 환경 구성
		- amazon-deploy-ecs-deploy-task-definition: 태스크 정의 JSON 파일을 가져오고 Amazon ECS 서비스에 태스크를 등록 및 배포
		- [AWS for GitHub Actions](https://github.com/aws-actions/)
	- 서드파티 도구 Jenkins 사용시 
```jenkinsfile
stage('Deploy to ECS Test Service') {
   steps {
      script {
         sh '''#!/bin/bash -ex
	     sed -i s/BUILD/${BUILD_NUMBER}/g taskdef.json
	     REV=$(aws ecs register-task-definition \
                  --cli-input-json file://taskdef.json | \
		   jq '.taskDefinition.taskDefinitionArn')
	     aws ecs update-service --cluster ${CLUSTER}  \
                  --service ${APP} \
		  --task-definition ${REV}
             aws ecs wait services-stable \
                  --cluster ${ECS_CLUSTER} \
                  --services ${ECS_SERVICE}
	    '''			
      }
   }
}
```


- 배포 패턴
	- 롤링 : 이전버전 하나 삭제하고 새버전 올리고, 이전버전 삭제하고 또 새버전 올리는 식 **minimumHealthyPercent**, **maximumPercent** 두 지표로 태스크 수 조절
	- 블루/그린 배포 : 블루 트래픽을 일괄적으로 그린 트래픽으로 전환. 다 올려놓고 전환
	- 카나리 : 라우팅을 블루 -> 그린으로 순차적으로 이동. 10, 20... 차차 늘려가서 이상 없으면 완전히 전환하는 방법
