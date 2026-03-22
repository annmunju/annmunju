- 생성형 AI 애플리케이션 구성 요소
	- 기초 모델 인터페이스
	- 인터페이스 및 프롬프트
	- 추론 파라미터
- 데이터 전처리
	- 벡터 임베딩 변환 후 벡터 데이터베이스 저장
	- OpenSearch 서비스
	- PostgreSQL pgvector 지원
	- 이렇게 처리된 정보는 RAG에 사용
- 프롬프트 기록 저장
	- 챗봇같은 대화형 AI에 사용. 일관성있는 컨텍스트 인식 대화에 도움
- RAG
![[Pasted image 20250413181252.png]]
- 미세 튜닝
	- 프롬프트 기반 학습 > 특정 태스크 기반 데이터를 학습
	- 도메인 적응 > 레이블 무관한 데이터를 파운데이션 모델에 추가 학습
- 아키텍처
![[Pasted image 20250413181618.png]]
![[Pasted image 20250413181629.png]]

---

## 파운데이션 모델
|**회사**|기초 모델|**설명**|
|---|---|---|
|**Amazon**|**Amazon Titan**|대규모 데이터 집합에 대해 사전 훈련된 Amazon에서 구축한 모델 제품군으로 강력한 범용 모델입니다.|
|**AI21 Labs**|**Jurassic-2**|스페인어, 프랑스어, 독일어, 포르투갈어, 이탈리아어, 네덜란드어로 된 텍스트 생성을 위한 다국어 대규모 언어 모델(LLM)입니다.|
|**Anthropic**|**Claude 2**|사려 깊은 대화, 콘텐츠 제작, 복잡한 추론, 창의력, Constitutional AI, 무해성 훈련을 기반으로 한 코딩을 위한 LLM입니다.|
|**Cohere**|**Command and Embed**|비즈니스 애플리케이션을 위한 텍스트 생성 모델과 100개 이상의 언어로 검색, 클러스터링 또는 분류를 위한 임베딩 모델입니다.|
|**Stability AI**|**Stable Diffusion**|독특하고 사실적인 고품질 이미지, 아트, 로고, 디자인 생성을 위한 텍스트-이미지 변환 모델입니다.  <br>  <br>현재 사용 가능: Stable Diffusion XL (SDXL) 1.0|
- [사용 메서드 참고](https://docs.aws.amazon.com/bedrock/latest/APIReference/welcome.html)

## LangChain
- LLM 성능 최적화
	- LangChain을 사용한 LLM 개발 간소화
- 랭체인 구성 요소
	- LLM 모델 설정
	- 채팅 모델 설정
	- 텍스트 임베딩 모델 설정
	- 프롬프트 템플릿 사용
- 인덱스 역할
	- 문서 로더 
	- 검색기
	- 벡터 저장소
- 메모리 사용 `from langchain.memory import ConversationBufferMemory`
	- 채팅 기록을 사용해 후속 질문에 응답하도록 함
- 체인
	- 입력 형식과 출력으로 구성
	- 구조화된 형식으로 데이터를 반환
	- 대량의 데이터 처리에 유용
- 에이전트
	- 검색 엔진, 계산기, API, 데이터베이스와 같은 외부 소스 상호 작용
	- **RouterChain** 복잡한 체인

## 아키텍처 패턴
- 텍스트 생성
- 텍스트 요약
- 질문 답변
- 챗봇 : 대화 인터페이스
	- 아키텍처
![[Pasted image 20250413190854.png]]
- 코딩 및 프로그래밍 작업
- LangChain 에이전트
