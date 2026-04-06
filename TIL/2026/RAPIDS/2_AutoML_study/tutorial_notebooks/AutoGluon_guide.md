# AutoGluon 정리

이 문서는 학습용 노트입니다.

## 1. AutoML과 AutoGluon

### AutoML이란?

AutoML(Automated Machine Learning)은 머신러닝 모델을 만들 때 반복적으로 수행하는 작업을 자동화해 주는 접근입니다.

- 어떤 모델을 쓸지 선택
- 하이퍼파라미터 탐색
- 전처리 일부 자동화
- 여러 모델 비교 및 앙상블

즉, 사람이 모든 실험을 손으로 다 하지 않아도, 강한 베이스라인을 빠르게 만들 수 있게 도와줍니다.

### AutoGluon이란?

AutoGluon은 AWS가 주도하는 오픈소스 AutoML 라이브러리입니다. 핵심 특징은 다음과 같습니다.

- 적은 코드로 높은 성능의 베이스라인을 빠르게 구축할 수 있음
- 단일 모델 하나보다 여러 모델을 조합한 앙상블에 강함
- 표 데이터뿐 아니라 시계열, 텍스트, 이미지, 문서 등 다양한 입력을 지원함

요약하자면
> AutoGluon은 좋은 머신러닝 기본 성능을 아주 적은 코드로 빠르게 만드는 도구입니다.

## 2. 왜 AutoGluon을 쓰는가

핵심적인 AutoGluon의 장점은 아래와 같습니다.

### 2.1 한 번의 `fit()`으로 많은 일을 처리

`fit()` 한 번으로 AutoGluon은 보통 다음을 자동으로 수행합니다.

- 문제 유형 추론: 분류 / 회귀
- 컬럼 타입 추론: 숫자형 / 범주형 / 텍스트 / 날짜 등
- 결측치 처리, 인코딩 등 기본 전처리
- 여러 후보 모델 학습
- 검증 점수 비교
- 가중 앙상블 또는 스태킹

### 2.2 스태킹과 앙상블에 강함

AutoGluon의 대표 강점은 `WeightedEnsemble`과 다층 스태킹입니다. 단일 모델 하나를 고르는 것보다 여러 모델의 장점을 결합해 더 강한 예측 성능을 내는 데 초점이 있습니다.

### 2.3 빠른 베이스라인 구축에 유리

대회, PoC, 사내 초기 검토 단계에서 "일단 잘 되는 기준선"을 만드는 데 특히 강합니다. 복잡한 튜닝을 하기 전에 먼저 AutoGluon으로 기준 성능을 잡아 놓으면 이후 비교가 쉬워집니다.

## 3. AutoGluon의 주요 모듈

AutoGluon은 크게 아래 세 모듈을 중심으로 많이 사용합니다.

| 모듈 | 핵심 클래스 | 대표 문제 |
| --- | --- | --- |
| Tabular | `TabularPredictor` | 이탈 예측, 신용평가, 가격 예측 같은 정형 데이터 |
| Time Series | `TimeSeriesPredictor` | 수요 예측, 매출 예측, 센서 시계열 예측 |
| Multimodal | `MultiModalPredictor` | 텍스트 + 표 + 이미지가 섞인 문제 |

## 4. Tabular 정리

표 형태 데이터에서 가장 먼저 공부하기 좋은 파트입니다.

### 4.1 어떤 문제에 쓰나

- 고객 이탈 예측
- 부도 / 승인 여부 분류
- 매출 / 가격 / 수요 회귀
- CSV, Parquet, pandas DataFrame 기반 일반적인 지도학습

### 4.2 핵심 흐름

```python
import pandas as pd
from autogluon.tabular import TabularPredictor

train_data = pd.read_csv("train.csv")
test_data = pd.read_csv("test.csv")

predictor = TabularPredictor(label="target", eval_metric="roc_auc").fit(
    train_data,
    presets="best",
    time_limit=600,
)

pred = predictor.predict(test_data)
leaderboard = predictor.leaderboard()
```

### 4.3 AutoGluon Tabular이 자동으로 해주는 것

- 분류 / 회귀 문제 자동 추론
- 컬럼 타입 추론
- 범주형 인코딩
- 날짜 컬럼 분해
- 텍스트 컬럼 처리
- 여러 모델 학습 및 비교
- 내부 검증 분할과 앙상블

참고로 날짜 컬럼은 연/월/일/요일 같은 파생 특성으로 변환될 수 있고, 텍스트 컬럼은 상황에 따라 n-gram 기반 처리 또는 멀티모달 모델과의 결합으로 다뤄질 수 있습니다.

### 4.4 자주 쓰는 파라미터

| 파라미터 | 의미 |
| --- | --- |
| `label` | 예측할 정답 컬럼 |
| `eval_metric` | 최적화할 평가 지표 |
| `presets` | 속도와 성능의 균형을 잡는 사전 설정 |
| `time_limit` | 학습 허용 시간(초) |
| `hyperparameters` | 사용할 모델군과 탐색 범위 지정 |
| `num_bag_folds` | 배깅 fold 수 |
| `num_stack_levels` | 스태킹 수준 |

### 4.5 `presets`는 어떻게 고르나

- `medium`: 빠른 프로토타입
- `good`, `high`: 속도와 정확도의 균형
- `best`: 대부분 사용자에게 추천되는 고성능 설정
- `extreme`: 최신 고성능 설정. GPU와 추가 의존성이 필요할 수 있음

### 4.6 학습 후 자주 쓰는 메서드

| 메서드 | 용도 |
| --- | --- |
| `predict()` | 예측값 생성 |
| `predict_proba()` | 분류 확률 예측 |
| `leaderboard()` | 모델별 성능 비교 |
| `feature_importance()` | 피처 영향도 확인 |
| `fit_summary()` | 학습 요약 확인 |
| `refit_full()` | 전체 데이터로 다시 학습해 배포용 모델 강화 |
| `save_space()` | 디스크 사용량 줄이기 |
| `distill()` | 앙상블을 더 가벼운 모델로 증류 |
| `clone_for_deployment()` | 추론에 필요한 최소 아티팩트만 포함한 복제본 생성 |

### 4.7 Tabular를 공부할 때 기억할 점

- AutoGluon이 강한 건 맞지만, 데이터 누수 방지는 여전히 사람이 해야 합니다.
- `best` 프리셋은 성능이 좋지만 학습 시간이 길어질 수 있습니다.
- 빠른 실험은 `medium`, 최종 성능은 `best` 또는 더 강한 설정으로 가는 식이 좋습니다.

## 5. Time Series 정리

### 5.1 무엇을 푸는 모듈인가

Time Series는 미래 시점의 값을 예측하는 모듈입니다.

- 향후 7일 판매량 예측
- 다음 48시간 전력 수요 예측
- 주가, 센서, 트래픽, 서버 부하 예측

핵심은 시간 순서를 가진 연속 데이터의 미래 구간을 예측한다는 점입니다.

### 5.2 핵심 클래스

- `TimeSeriesDataFrame`: 시계열 데이터를 다루는 전용 자료구조
- `TimeSeriesPredictor`: 학습, 예측, 평가를 담당하는 클래스

### 5.3 기본 데이터 형식

AutoGluon Time Series는 보통 아래 세 컬럼을 중심으로 데이터를 받습니다.

- `item_id`: 각 시계열을 구분하는 ID
- `timestamp`: 시점
- `target`: 예측할 값

예를 들면 "상품별 일별 판매량" 데이터라면:

- 상품 A의 시계열
- 상품 B의 시계열
- 상품 C의 시계열

이런 여러 시계열이 `item_id`로 구분되어 하나의 표에 들어갑니다.

### 5.4 가장 중요한 개념: `prediction_length`

`prediction_length`는 앞으로 몇 시점을 예측할지 정하는 값입니다.

- 시간 단위 데이터에서 `48`이면 앞으로 48시간
- 일 단위 데이터에서 `7`이면 앞으로 7일

즉, 모델의 목표를 정의하는 가장 중요한 파라미터 중 하나입니다.

### 5.5 기본 흐름

```python
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

df = pd.read_csv("train.csv")

train_data = TimeSeriesDataFrame.from_data_frame(
    df,
    id_column="item_id",
    timestamp_column="timestamp",
)

predictor = TimeSeriesPredictor(
    prediction_length=48,
    target="target",
    eval_metric="MASE",
).fit(
    train_data,
    presets="medium_quality",
    time_limit=600,
)

predictions = predictor.predict(train_data)
```

### 5.6 Time Series에서 주목할 점

- 여러 개의 시계열을 한꺼번에 학습할 수 있음
- 예측 평균뿐 아니라 분위수 기반 불확실성 예측도 가능
- `leaderboard()`, `plot()`, `evaluate()`로 비교와 해석 가능
- 최신 버전에서는 `Chronos-2` 같은 시계열 foundation model도 `TimeSeriesPredictor` 흐름 안에 통합됨

### 5.7 어떤 모델이 내부적으로 쓰일 수 있나

상황에 따라 고전 통계 모델, 트리 기반 모델, 딥러닝 모델, foundation model이 함께 비교될 수 있습니다. 최신 문서 예시에서는 `SeasonalNaive`, `ETS`, `Theta`, `RecursiveTabular`, `DirectTabular`, `Chronos2`, `WeightedEnsemble` 같은 모델들이 함께 등장합니다.

### 5.8 Time Series 팁

- 무작위 train/test split 대신 시간 순서를 지키는 분할이 중요합니다.
- 미래 정보를 현재 피처에 섞지 않도록 누수를 특히 조심해야 합니다.
- 예측 길이(`prediction_length`)와 평가 지표(`MASE`, `WQL`, `RMSE` 등)를 문제에 맞게 정해야 합니다.

## 6. Multimodal 정리

AutoGluon의 차별점이 잘 드러나는 영역입니다.

### 6.1 멀티모달이란?

멀티모달은 서로 다른 형태의 데이터를 함께 사용하는 문제입니다.

- 상품 설명 텍스트 + 가격/카테고리 표 데이터
- 리뷰 텍스트 + 상품 이미지
- 문서 이미지 + OCR 텍스트
- 프로필 이미지 + 유저 속성 테이블

### 6.2 핵심 클래스

- `MultiModalPredictor`

이 클래스는 텍스트, 이미지, 범주형, 수치형, 문서 데이터를 단독 또는 조합 형태로 처리할 수 있게 설계되어 있습니다.

### 6.3 지원 범위

공식 문서 기준으로 AutoMM(AutoGluon Multimodal)은 아래 같은 문제를 지원합니다.

- 분류
- 회귀
- 객체 탐지
- 개체명 인식(NER)
- 텍스트 / 이미지 / 문서 기반 예측
- 시맨틱 매칭
- 이미지 세그멘테이션

### 6.4 왜 중요한가

기존의 표 데이터 AutoML 도구는 수치형과 범주형에는 강하지만, 텍스트나 이미지가 섞이면 별도 파이프라인이 필요했습니다. AutoGluon Multimodal은 foundation model을 활용해 이 과정을 하나의 인터페이스로 묶어 주는 점이 강점입니다.

### 6.5 기본 흐름 예시

```python
import pandas as pd
from autogluon.multimodal import MultiModalPredictor

train_data = pd.read_csv("train.csv")

predictor = MultiModalPredictor(label="label")
predictor.fit(train_data, time_limit=600)

pred = predictor.predict(train_data)
```

텍스트 컬럼, 이미지 경로 컬럼, 숫자형 컬럼이 함께 있어도 같은 인터페이스에서 처리할 수 있습니다.

### 6.6 어떤 상황에 특히 유용한가

- 고객 리뷰 텍스트와 별점 / 메타데이터를 함께 쓰고 싶을 때
- 상품 이미지와 텍스트 설명을 같이 반영하고 싶을 때
- 문서 분류나 OCR 연계 작업을 빠르게 시작하고 싶을 때

### 6.7 멀티모달 공부 포인트

- 단순 표 데이터면 우선 `TabularPredictor`부터 익히는 것이 좋습니다.
- 텍스트나 이미지가 포함될 때 `MultiModalPredictor`로 넘어가면 차이를 체감하기 쉽습니다.
- foundation model을 쓴다는 뜻이므로, Tabular보다 자원 요구량이 커질 수 있습니다.

## 7. 설치와 환경 정리

발표 자료에는 Python 3.8~3.11 기준 설명이 있었지만, 최신 공식 릴리스 노트 기준으로 AutoGluon 1.5.0은 Python `3.10`, `3.11`, `3.12`, `3.13`을 지원하며 `3.13`은 일부 환경에서 실험적입니다.

### 7.1 `uv` 기준 CPU 설치 예시

```bash
python -m uv pip install autogluon --extra-index-url https://download.pytorch.org/whl/cpu
```

### 7.2 모듈별 설치 예시

```bash
python -m uv pip install "autogluon.tabular[all]"
python -m uv pip install autogluon.timeseries
python -m uv pip install autogluon.multimodal
```

### 7.3 설치 관련 메모

- macOS에서는 GPU 사용이 아직 제한적일 수 있어 공식 문서 확인이 필요합니다.
- Windows는 문서에서 Anaconda 기반 설치를 권장하는 구간이 있습니다.
- 최신 버전에서 학습한 모델을 예전 버전으로 그대로 로드하는 것은 지원되지 않을 수 있으니 버전 고정이 중요합니다.

## 8. 다른 라이브러리와 비교

라이브러리 별 실험 결과는 아래 조건에 크게 좌우됩니다.

- 데이터셋 종류
- 런타임 제한
- GPU 사용 여부
- 평가 지표
- 프레임워크 버전
- 전처리 방식

하지만 AutoGluon이 다른 라이브러리에 비해서 강점이 있다면

- 성능 최우선이면 AutoGluon이 강한 편
- 짧은 시간 안에 빠른 베이스라인이 필요하면 다른 도구가 더 효율적일 수 있음

정도로 이해하는 것이 좋습니다.

## 9. 공부 순서 추천

AutoGluon을 처음 공부한다면 아래 순서가 좋습니다.

1. `AutoML` 개념 이해
2. `TabularPredictor`로 분류 / 회귀 한 번 돌려 보기
3. `leaderboard()`, `feature_importance()` 읽는 법 익히기
4. `presets`와 `time_limit` 차이 체감하기
5. `TimeSeriesPredictor`로 `prediction_length` 개념 익히기
6. 텍스트 / 이미지가 섞인 데이터에서 `MultiModalPredictor` 써 보기
7. 마지막에 `distill()`, `save_space()`, `clone_for_deployment()` 같은 배포 최적화 기능 보기

## 10. 참고 자료

- AutoGluon Install: https://auto.gluon.ai/stable/install.html
- Tabular Essentials: https://auto.gluon.ai/stable/tutorials/tabular/tabular-essentials.html
- Tabular Feature Engineering: https://auto.gluon.ai/stable/tutorials/tabular/tabular-feature-engineering.html
- Time Series Quick Start: https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-quick-start.html
- Multimodal Overview: https://auto.gluon.ai/stable/tutorials/multimodal/index.html
- AutoGluon 1.5.0 Release Notes: https://auto.gluon.ai/dev/whats_new/v1.5.0.html
