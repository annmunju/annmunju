
- 딥러닝 하이퍼파라미터
	- model algorithm
		- cnn
		- rnn
		- seq2seq + Attention
		- transformer
	- activate fuction
		- sigmoid <- 기울기 소실 문제, 0.5 이하인 경우 weight 진폭이 크게 변이하는 문제
		- tanh <- 기울기 소실 문제
		- ReLU
		- Leaky Relu
	- Loss function
		- classification
			- BCE(Binary Cross Entropy)
			- Cross Entropy
		- regression
			- MLE (절대값 편차 평균)
			- MSE (편차 제곱 평균)
			- RMSE (편차 제곱->제곱근 평균)
	- learning rate optimization : w를 얼마나 바꿀지, 어떻게 로스를 가장 줄이는 방향으로 찾아갈지(방법론)
		- Gradient Decent
		- SGD
		- Mini-batch GD
		- Momentum : 가장 로스가 낮다고 추정하는 지점에 더 추정해봄
		- Adagrad : 로스가 낮아질 수록 기울기를 더 천천히 낮춤 (러닝레이트를 점차 줄임)
		- 
		- Adam (Adagrad + Momentum)
- training
	1. 알고리즘 선택 / 아키텍처 구성
	2. 하이퍼 파라미터 초기화
		- weight
		- learning late
		- batch size
		- 최적화 알고리즘
	3. Training : forward, backward
	4. Loss function으로 손실 계산
	5. 최적화 알고리즘을 통해 weight 계산
- 경사 하강법 

|               | 경사 하강법            | 확률적 경사 하강법(SGD)          | 미니 배치 경사 하강법               |
| ------------- | ----------------- | ------------------------ | -------------------------- |
| 가중치 업데이트      | 모든 Epoch          | 모든 데이터 포인트               | 모든 배치                      |
| 각 Epoch 계산 속도 | 가장 느림             | 빠름                       | 느림                         |
| 경사            | 최저치를 향한 업데이트가 완만함 | 최저치를 향한 업데이트가 불규칙하고 잡음있음 | 최저치를 향한 업데이트가 불규칙하고 잡음이 적음 |

---

### CNN
- 하이퍼파라미터
	- 필터 사이즈 n\*n
	- Stride (필터 이동 간격)
	- padding (레이어 크기를 감소시키지 않기 위한 이미지 바깥 패딩)
- 활성화 함수 + pooling 사용
	- 이미지는 바로 옆에 있는 픽셀 값은 거의 유사하기 때문에 속도 향상을 위해서 활성화 함수 사용

## NLP 
1. RNN : 자신의 값을 뒤에 넘겨줌
2. LSTM
3. Seq2Seq : encoder + decoder 등장
4. Attention
5. Transformer : 병렬처리가 가능해지면서 속도를 개선

### Seq2Seq + Attention
- attention
	- 컨텍스트 벡터와 원본 데이터 자체를 함께 결과에 반영

### Transform
- positional encoding -> multi-head attention (각자 따로 계산해서 위에서 한번 묶는 형태) 

## AWS에서 모델 훈련
- 모델 병렬 vs 데이터 병렬
	- 데이터 병렬로 훈련하고 모델의 w, b의 평균으로 사용

### SageMaker
- 데이터 처리
	- Data Wrangler : 머신러닝을 위한 UI를 이용한 ERD 작업
	- Feature Store : 데이터 피처 저장, 공유 등
	- Clairfy : 데이터 편향을 탐지하고 추정
	- Ground Truth : 레이블 지정
- 모델 개발
	- Studio Notebook
	- Studio Lab : 머신러닝 개발 환경 (notebook 기반으로 학습 까지)
	- Local Mode : 로컬 시스템으로 옮기기 가능
	- Autopilot : 모델 자동 생성
	- JumpStart : 사전 구축된 다양한 모델 검색 및 테스팅
- 모델 훈련 및 튜닝
	- automatic model tuning: 자동 하이퍼파라미터 최적화를 통한 모델 튜닝
	- Managed spot training: 스팟 인스턴스로 훈련 비용 절감
- 배포 및 관리
	- Real-time Inference : 안정적 트래픽
	- Asynchronous Inference : 대용량 패이로드 또는 긴 추론시간 (비동기식)
	- Batch Transform : 대규모 데이터 세트 배치에 대한 오프라인 추론
	- Multi-Model Endpoints :  여러 모델을 하나의 엔드포인트로 요청
	- Shadow Testing: 배포 모델과 테스팅 모델 동시에 보내서 테스팅은 로그만 쌓아서 성능 비교해볼 수 있도록

### 도메인
- EC2 인스턴스 두개가 뜸
	- 하나는 노트북 서버
	- 하나는 모델 훈련 서버
- 모델은 ECR에 이미지로 업로드

### Canvas 
> 만들어진 모델 가져다 쓰기
- 지도학습에서 주로 사용

---

### 실습 1: Amazon SageMaker Data Wrangler로 데이터 준비

![[Pasted image 20250407150011.png]]
1. 데이터 구조와 품질에 대한 인사이트 얻기
2. 데이터 분석 및 시각화 
	- 예측 능력이 없는 features
	- 누락된 값이 있는 열 확인
3. 열 삭제 및 누락 값과 중복 값 처리
	- 열 삭제 (manage columns > drop column)
	- 누락 값을 포함하는 열 지우기 (handle missing > drop missing)
	- 중복값 삭제 (manage rows > drop duplicates)
	- 문자열 앞뒤 띄어쓰기 정리 (format string > strip left and right)
4. 특성 공학 (one hot encoding, class로 변환 등)
	- class 변환 (Search and edit)
	- 이상치 처리 (handle outliers > min-max numberic outliers)
	- 서수 인코딩 - 0에서 순서가 있는 범주화 (encode categorical > ordinal encoding)
	- 원-핫 인코딩 수행 (encode categorical > one-hot encode)
5. XGBoost 모델 훈련을 위해 column 이동시키기 (첫번째 열에 y값에 해당하는 열 옮기기) : Manage columns > move column > move to start > "원하는 행"
6. 데이터 내보내기 (Export)

### Generative AI
- 생성형 AI의 정의 
	1. 무조건 생성함
	2. 방대한 데이터 사용 (목적의식 없이 수집)
- 문제점
	- 환각현상
	- 두루두루 잘하나 하나를 특정 잘하지 않음
	- 훈련한 지식에 대해서만 알고 있음 (최신 지식 부재)
- 구조
	- 파운데이션 모델
	- 그 위에 커스터마이징 (아래로 내려갈수록 어려움)
		- 프롬프트 엔지니어링
		- RAG
		- Agentic AI
		- Fine Tuning
		- 모델 직접 만들기
- RAG
	- 저장 : 문서를 청크 단위로 쪼개서 (청킹) 임베딩 모델을 거쳐 Vector DB에 저장함
	- 검색 : 임베딩 거리가 가까운 (retrival) 결과를 VectorDB에서 가져옴
	- 임베딩 모델 - Solar 추천
	- 검색 기능은 VectorDB에서 제공
- Advanced RAG
	- 청킹 단계에서 의미상 유사한 단락을 기준으로 할 수 있게 
	- Small to Big : 자식 - 부모 구조. 큰 청크 아래 작은 청크. 검색은 작은 청크로 하고, 검색 결과 제공시 큰 청크를 제공
	- Sentence Window : 맥락 이해를 위해 검색 후 해당 문장의 주변 문장을 함께 검색 반환
	- Query Rewrite, Query Expansion : 유사정보를 추가하거나, 문장형태 쿼리로 재생성
	- Hypothetical Question
		- 청킹으로 들어올 질문을 미리 생성하고
		- 질문이 오면 가까운 질문을 찾고 그에 해당한 원 답변을 반환
	- HyDE
		- 질문을 받았을 때 이에 대한 답변을 미리 생성하고
		- 해당 답변을 벡터 디비와 비교해서 반환
	- Rerank : 청크를 여러개 가져와서 해당 청크들을 파운데이션 모델에 적합한 답인지 일일이 물어봄
	- 캐시 붙여서 같은 질문은 동일한 답변을 나가게 함
- Agent
	- 서드파티 에이전트를 붙이는 방식
	- 파운데이션을 가운데로 두고 RAG + 에이전트 ... 를 붙임
- Cloude sonet?


### 실습 : AI application 개발 for KOSA

![[Pasted image 20250407163746.png]]

#### 모듈 1 - Amazon S3 버킷 및 knowledge base 설정
1. 도메인 데이터 버킷 생성
	- 지식 베이스 (RAG 문서)용 버킷 생성
	- artifact 용 버킷 생성 
2. 베드락에서 모델 접근권한 부여 및 knowledge base 생성
	- Bedrock > 모델 엑세스
	- Builder tools > knowledge base 생성
		- 모델 지정해주고
		- 데이터 소스 지정해주고 (S3) 생성

#### 모듈 2 - AWS Lambda 함수 설정
1. 람다 함수 생성 : 베드락 지식 베이스에 저장된 내용을 조회 등등 하기 위한 함수 포함됨

#### 모듈 3 - 에이전트와 액션 그룹 구성
1. Amazon Bedrock 에이전트 생성
	- 모델 선택
	- 에이전트 지침 넣기
```
You are an investment analyst who creates portfolios of companies based on the number of companies, and industry in the {question}. An example of a portfolio looks like this template {portfolio_example}. You also research companies, and summarize documents. When requested, you format emails like this template {email_format}, then use the provided tools to send an email that has the company portfolio created, and summary of the FOMC report searched.
```
	- 액션 그룹 추가하기
		- 에이전트가 실행할 내용의 스키마를 업로드

#### 모듈 4 - Amazon Bedrock의 에이전트와 기술 자료 동기화
1. Amazon Bedrock 에이전트와 Knowledge base 연동
	- Knowledge bases 섹션의 지침 추가하기 `This knowledge base has data about economic trends, company financial statements, and the outcomes of the Federal Open Market Committee meetings.`
	- Orchestration 내용 추가하기  \#prompt_session_attributes
```
Additionally, use the following examples as references when generating company portfolios and formatted emails:

<portfolio_example>

Here is a portfolio of the top 3 real estate companies:
Example of a company portfolio:

  1. NextGenPast Residences with revenue of $180,000, expenses of $22,000 and profit of $158,000 employing 260 people.
  
  2. GlobalRegional Properties Alliance with revenue of $170,000, expenses of $21,000 and profit of $149,000 employing 11 people.
  
  1. InnovativeModernLiving Spaces with revenue of $160,000, expenses of $20,000 and profit of $140,000 employing 10 people.

</portfolio_example>

Here is an example of a formatted email. Double check that the FOMC report is a summary of the knowledge base responses.

<email_format>

Company Portfolio:

  1. NextGenPast Residences with revenue of $180,000, expenses of $22,000 and profit of $158,000 employing 260 people.
  
  2. GlobalRegional Properties Alliance with revenue of $170,000, expenses of $21,000 and profit of $149,000 employing 11 people.
  
  1. InnovativeModernLiving Spaces with revenue of $160,000, expenses of $20,000 and profit of $140,000 employing 10 people.  

FOMC Report:

  Participants noted that recent indicators pointed to modest growth in spending and production. Nonetheless, job gains had been robust in recent months, and the unemployment rate remained low. Inflation had eased somewhat but remained elevated.

  Participants recognized that Russia’s war against Ukraine was causing tremendous human and economic hardship and was contributing to elevated global uncertainty. Against this background, participants continued to be highly attentive to inflation risks.
</email_format>

When asked to generate company portfolios or formatted emails, use these examples as a guide for structure and content.
```
2. Alias 만들기
3. 람다함수에서 리소스 정책에 에이전트 ARN 추가하기

#### 모듈 5 - 설정 테스트
1. Knowledge base에서 데이터 소스와 동기화 Sync
2. 동기화 후 모델 선택 인터페이스에서 모델 선택
3. 사용자 인터페이스 (테스트) 창에서 한글로 테스트

#### 모듈 6 - Cloud9 환경 셋업
1. Coud9 환경 생성
2. Streamlit 앱 받아서 업로드 
3. **업데이트 구성 (매우 중요):**
	- `InvokeAgent.py` 파일을 엽니다.
	- `agentId` 및 `agentAliasId` 변수를 적절한 값으로 업데이트한 후 저장합니다.
	- 다른 지역을 선호하는 경우 `InvokeAgent.py` 파일의 코드 라인 22에서 region을 업데이트하세요.
	- `File -> Save All`으로 이동하여 모든 변경 사항을 저장하세요.
4. 스트림릿 설치 `pip install streamlit boto3 pandas`
5. 스트림릿 앱 실행 `streamlit run app.py --server.address=0.0.0.0 --server.port=8080`
