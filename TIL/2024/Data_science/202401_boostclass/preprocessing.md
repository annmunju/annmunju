
## 변수 전처리

### 연속형 변수 전처리
- Scaling
	- Min-Max ((현재 값-최소값)/최대 최소 차)
	- Standard ((현재 값-평균)/표준편차)
	- Robust ((현재 값-중위값)/(75분위수-25분위수)) <-이상치 영향을 가장 덜 받는다
- Scailing + Distribution
	- Log transformation : 오른쪽 꼬리가 긴 분포-> 정규분포 형태로 변환됨
	- Exponential transformation : 왼쪽 꼬리가 긴 분포 -> 정규분포 형태로 변환됨
	- Quantile transformation 
		- 어떤 분포가 들어와도 정규분포로 바꿔줌
		- 분위수로 변환하는 형태
	- 분포를 바꾸면 좋은 점 : 타겟과 상관관계가 높아짐. 모델 성능도 높아질 수 있음.
- Binning
	- 특정 구간별로 특징이 분명한 경우 구간별로 값을 동일하게 만듦 (범주화함)
	- Tree 모델인 경우에 Overfitting 방지할 수 있음. 해석이 용이해짐.

### 범주형 변수 전처리
> 수치형 변수로 바꿔주어야 함
- One hot encoding
	- 변수를 1과 0으로 변환하여 표기 (해당 열을 추가하여 있는 경우 1, 없는 경우 0)
- Label encoding
	- 컬럼의 수는 하나로 유지하되 각각 다르게 표기 (개는 1 고양이는 2 등)
	- 선형 모델 사용 X (순서가 없는 무관한 라벨의 경우)
- Frequency encoding
	- 해당 변수의 값이 몇번 나왔는지 빈도수로 인코딩
- Target encoding 
	- 타겟값의 평균으로 인코딩
	- 서로 다른 종이지만 값이 같은 경우가 있을 수 있음
	- 장점 : 의미 있는 값을 모델에 줄 수 있다.
- Embedding
	- Word2Vec 등의 방법으로 낮은 차원, 수치형으로 encoding


## 결측치 처리

- 패턴없는 경우
	- 단변량 기법
		- 데이터 포인트 제거 (결측치 값 제거 혹은 변수 제거)
		- 평균값, 중위값, 상수값 삽입 (결측치가 많은 경우 문제 될 수 있음)
	- 다변량 기법
		- 주변 값의 회귀분석을 통해서 결측치를 예측해 채울 수 있음
		- 주변 값의 KNN를 통해 nearest 결측치를 예측해 채울 수 있음
- 규칙이 있는 경우
	- 규칙에 따른 결측치 채우기 가능
	- 합리적인 접근 방법 사용
- (주의) 결측치가 많은 경우에, 아무렇게나 결측치 채운 경우 모델 성능을 저하시킬 수 있음.

## 이상치 처리
### 이상치 탐색
- Z-Score
- IQR

### 이상치 처리 관점
- 정성적인 측면
	- 이상치 발생 이유 : 일반적으로는 벗어난 이상치 값. 특수 케이스인 경우. 
	- 이상치의 의미
- 성능적인 측면
	- Train Test Distribution. 모델 결과를 바탕으로 이상치를 탐색하는 방법.
	