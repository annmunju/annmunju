### 트리 모델의 발전
- Decision Tree
- Random Forest
- AdaBoost
- GBM
- XGBoost
- LightGBM
- Catboost

### Bagging & Boosting
- Bagging : 랜덤포레스트는 배깅의 대표적인 기법
	- 훈련시 데이터셋을 샘플링해 하나하나의 Decision Tree가 생성
	- 생성한 D Tree들을 취합
	- Bootstrap + Aggregation : 데이터를 여러번 샘플링 + 종합
	- 병렬적이며 다양한 트리 생성
- Boosting : LightGBM, XGBoost, Catboost 대표적 기법
	- 초기 랜덤하게 선택된 데이터셋으로 트리를 만들고
	- 다음번에는 잘 맞추도록 weight를 줌
	- 순차적 모델이며 정밀한 Tree 생성

### 대표적 Boosting 모델
- 균형적 구조
	- XGBoost
	- Catboost (카테고리 변수들 잘 함!)
- 비균형적 구조
	- LightGBM

### Boosting 모델 하이퍼 파라미터
- Learning rate
- 모델의 깊이와 잎사귀 
	- 너무 깊으면 overfitting
- Column sampling ratio : 랜덤하게 변수를 선택해서 트리를 생성
- Row sampling ratio : Row를 기준으로 랜덤으로 선택해서 만듦
![[boosting models - hyper params.png]]
