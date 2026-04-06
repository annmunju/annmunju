# GPU 기반 AutoGluon Time Series 정리

이 문서는 AutoGluon Time Series의 GPU 활용 방식과 NVIDIA RAPIDS를 어디에 붙이는 것이 현실적인지 정리한 학습용 노트입니다.

핵심은 아래 세 질문을 구분해서 보는 것입니다.

- AutoGluon Time Series는 GPU를 실제로 어디에서 쓰는가
- Chronos-2 같은 시계열 foundation model은 실무에서 어떤 의미가 있는가
- RAPIDS는 학습 자체를 가속하는가, 아니면 데이터 준비 단계를 가속하는가

## 1. 먼저 결론부터

### 1.1 핵심 결론

- AutoGluon Time Series의 GPU 활용은 현재 딥러닝 계열 모델과 Chronos 계열 모델 중심으로 이해하는 것이 맞습니다.
- 공식 FAQ 기준으로 `autogluon.timeseries`의 딥러닝 모델은 GPU 학습을 지원하며, CUDA가 가능한 PyTorch 환경이면 자동으로 GPU를 사용합니다.
- 다만 멀티 GPU 학습은 아직 공식 지원 대상이 아닙니다.
- RAPIDS는 AutoGluon Time Series의 학습 엔진을 바꾸기보다, pandas 기반 전처리와 대용량 데이터 핸들링을 GPU로 가속하는 역할에 더 잘 맞습니다.

### 1.2 왜 이렇게 해석하나

`cudf.pandas`는 pandas API를 GPU에서 가속하고, 지원되지 않는 연산은 pandas로 자동 fallback합니다. 또한 AutoGluon Time Series는 `pandas.DataFrame`을 입력으로 받아 내부에서 `TimeSeriesDataFrame`으로 변환할 수 있습니다.

즉 실무적으로는 아래 구조가 가장 자연스럽습니다.

- 전처리: RAPIDS
- 학습, 백테스트, 앙상블, leaderboard: AutoGluon

이 부분은 AutoGluon이 RAPIDS를 공식 통합 대상으로 명시했다기보다, 문서의 입력 구조와 호환성을 종합한 해석입니다.

### 1.3 한 문장 요약

> AutoGluon Time Series에서는 Chronos-2와 딥러닝 모델이 GPU 활용의 중심이고, RAPIDS는 그 앞단의 pandas 기반 전처리를 가속하는 보완 계층으로 보는 것이 가장 현실적입니다.

## 2. AutoGluon Time Series에서 GPU가 쓰이는 지점

### 2.1 핵심 인터페이스

AutoGluon Time Series는 단일 모델 도구가 아니라, 여러 예측 모델을 학습하고 비교하는 AutoML 인터페이스입니다.

- `TimeSeriesDataFrame`: 시계열 데이터를 다루는 핵심 자료구조
- `TimeSeriesPredictor`: 학습, 예측, 평가를 담당하는 핵심 클래스

입력이 `pandas.DataFrame`이어도 내부에서 `TimeSeriesDataFrame`으로 변환할 수 있기 때문에, 기존 pandas 기반 파이프라인과 연결하기가 비교적 쉽습니다.

### 2.2 GPU 관점에서 중요한 포인트

공식 문서 기준으로 GPU와 관련해 특히 중요한 축은 두 가지입니다.

- 딥러닝 모델은 GPU 학습을 지원함
- `Chronos-2` 같은 시계열 foundation model이 `TimeSeriesPredictor` 흐름 안에 통합되어 있음

즉 AutoGluon Time Series의 GPU 활용은 "트리 모델을 GPU로 돌린다"보다는 "딥러닝 모델과 foundation model을 AutoGluon 안에서 활용한다"는 쪽이 중심입니다.

## 3. Preset으로 보는 GPU 활용 전략

`TimeSeriesPredictor.fit()` 기준으로 `presets="medium_quality"`는 빠른 통계/트리 모델에 더해 `TemporalFusionTransformer`와 `Chronos-2 (small)`를 포함합니다. `high_quality`는 더 다양한 DL/ML/통계 모델을 섞고, `best_quality`는 여기에 다중 backtest 검증까지 수행합니다.

또한 Chronos 전용 preset도 별도로 제공됩니다.

- `chronos2`
- `chronos2_small`
- `chronos2_ensemble`
- `bolt_{model_size}`

### 3.1 발표나 실험에서 설명하기 쉬운 3단계 전략

| 단계 | 대표 preset | 설명 |
| --- | --- | --- |
| 빠른 baseline 확보 | `chronos2`, `chronos2_small` | zero-shot 기반으로 빠르게 기준 성능 확인 |
| 혼합 AutoML 비교 | `medium_quality` | Chronos + 딥러닝 + 전통 모델을 함께 비교 |
| 정확도 중심 탐색 | `high_quality`, `best_quality` | 더 넓은 모델 탐색과 강화된 backtest 수행 |

이 구조는 모두 공식 preset 설계를 바탕으로 정리한 흐름입니다.

## 4. Chronos-2를 따로 봐야 하는 이유

### 4.1 왜 중요한가

AutoGluon 1.5 계열 문서에서는 `Chronos-2`를 Time Series 영역의 핵심 변화로 다룹니다.

- zero-shot forecasting 지원
- custom data fine-tuning 지원
- backtest, 비교, 앙상블 흐름 안에 자연스럽게 포함

즉 별도 프레임워크를 쓰지 않고도 foundation model 기반 시계열 예측을 AutoGluon 문법 안에서 다룰 수 있습니다.

### 4.2 실무에서 가지는 의미

`Chronos-2`는 단순 데모 모델이 아니라, 기존 통계 모델과 task-specific 딥러닝 모델과 함께 비교되는 운영 후보입니다. 문서에서는 zero-shot 모델과 fine-tuned 모델을 함께 넣고 `leaderboard`로 비교하는 흐름도 제시합니다.

요약하면 `Chronos-2`는 "부가 기능"이 아니라, 현재 AutoGluon Time Series의 GPU 활용을 대표하는 공식 경로라고 볼 수 있습니다.

## 5. Fine-tuning은 언제 고려할까

### 5.1 기본 방향

`Chronos-2`는 zero-shot만으로도 사용할 수 있지만, 공식 튜토리얼은 fine-tuning도 지원합니다. 기본 fine-tuning 설정에서는 LoRA를 사용해 메모리와 디스크 사용량을 줄입니다.

### 5.2 언제 하는 게 좋은가

문서에서는 아무 데이터셋에나 fine-tuning을 권장하지 않습니다. 예시로는 아래와 같은 조건이 제시됩니다.

- 대략 100개 이상의 시계열
- 중앙값 기준 `3 * prediction_length`보다 긴 히스토리

데이터가 부족하면 과적합이나 성능 저하가 발생할 수 있다는 점도 함께 안내합니다.

### 5.3 GPU 장비 관점에서 기억할 점

- 멀티 GPU 머신이 있어도 `CUDA_VISIBLE_DEVICES`로 단일 GPU만 보이게 두는 구성이 권장됨
- Time Series FAQ도 멀티 GPU 학습은 아직 지원하지 않는다고 명시함

따라서 "GPU 사용 가능"과 "분산/멀티 GPU 최적화"를 같은 의미로 보면 안 됩니다. 현재 공식 권장 경로는 단일 GPU 중심 운영입니다.

## 6. Covariates를 같이 봐야 하는 이유

시계열 문제를 GPU 이야기만으로 풀면 자원 관점으로 좁아지기 쉽지만, 실제 성능 차이를 크게 만드는 경우는 covariates 설계인 경우가 많습니다.

### 6.1 `known_covariates_names`란

`TimeSeriesPredictor` 문서에서 `known_covariates_names`는 예측 구간에서도 미리 알 수 있는 동적 특성으로 설명됩니다.

예시는 아래와 같습니다.

- 휴일
- 프로모션
- 날씨 예보

또한 `fit()` 문서에서는 이 컬럼들이 `train_data`에 포함되어야 하며, `target`과 `known_covariates`를 제외한 나머지 컬럼은 `past_covariates`로 해석된다고 설명합니다. `predict()`에서도 `known_covariates_names`를 지정한 경우, 예측 시점의 covariates를 함께 제공해야 합니다.

### 6.2 왜 중요한가

발표에서는 아래처럼 메시지를 잡는 편이 좋습니다.

> GPU는 딥러닝과 Chronos 학습을 가능하게 하고, covariates는 예측 문제를 더 현실적으로 만든다.

특히 판매량, 트래픽, 센서, 에너지 수요처럼 외생 변수의 영향이 큰 문제에서는 이 포인트가 중요합니다.

## 7. RAPIDS는 어디에 붙이는 것이 맞을까

### 7.1 먼저 볼 기능: `cudf.pandas`

`cudf.pandas`는 pandas 코드를 GPU에서 가속하고, 지원하지 않는 연산은 CPU로 자동 fallback합니다. 문서에서는 다음처럼 활성화 방법을 안내합니다.

- Jupyter: `%load_ext cudf.pandas`
- 스크립트: `import cudf.pandas; cudf.pandas.install()`

중요한 점은 이 호출이 반드시 `pandas` import 전에 와야 한다는 것입니다.

```python
import cudf.pandas
cudf.pandas.install()

import pandas as pd
```

### 7.2 AutoGluon과 결합할 때 가장 자연스러운 위치

RAPIDS는 전처리 가속층으로 쓰는 것이 가장 자연스럽습니다. 예를 들면 아래 같은 구간입니다.

- 대용량 CSV / Parquet 로딩
- 조인
- `groupby`
- `rolling`
- calendar feature 생성
- item별 집계
- lag / rolling feature 초안 생성

반면 최종 학습, 백테스트, 앙상블, leaderboard는 AutoGluon이 맡는 구조가 더 적합합니다.

이 역시 공식 문서가 직접 "이렇게 통합하라"고 말하는 것은 아니지만, pandas 호환성과 AutoGluon의 pandas 입력 구조를 합치면 가장 실용적인 결합점으로 볼 수 있습니다.

## 8. `cuml.accel`과 Dask-cuDF는 어디까지 기대할까

### 8.1 `cuml.accel`

이름 때문에 "AutoGluon도 그냥 GPU 가속되겠지"라고 오해하기 쉽지만, 공식 FAQ 기준 대상 범위는 아래에 가깝습니다.

- Scikit-Learn
- UMAP-Learn
- HDBSCAN

또한 구현되지 않은 부분은 CPU로 fallback하고, 기능 자체도 beta라고 명시돼 있습니다.

그래서 `cuml.accel`은 AutoGluon Time Series 본체의 직접 가속 도구라기보다, 보조 전처리 또는 보조 분석 계층으로 소개하는 편이 안전합니다.

예를 들면 아래 정도에는 의미가 있습니다.

- item clustering
- sklearn 기반 회귀 / 군집 / 특징 축소 실험
- 기존 sklearn 코드의 빠른 GPU 검토

하지만 AutoGluon Time Series의 핵심 학습 루프를 공식적으로 대체하는 경로로 보기는 어렵습니다.

### 8.2 Dask-cuDF

대용량 시계열 데이터에서는 단일 GPU pandas 가속만으로 부족할 수 있습니다. 이때 RAPIDS는 `dask-cudf`를 통해 Dask DataFrame의 `"cudf"` backend를 제공하며, `read_parquet`, `read_csv` 단계부터 GPU-backed dataframe을 만들 수 있습니다.

다만 문서 기준으로 Dask cuDF만으로 멀티 GPU나 멀티 노드가 완성되는 것은 아닙니다. 이를 위해서는 아래 구성이 필요합니다.

- `dask.distributed` 클러스터
- Dask-CUDA

또한 Best Practices 문서는 Parquet를 권장 포맷으로 제시하고, `read_parquet()`의 `blocksize`, `aggregate_files` 같은 파라미터가 성능에 중요하다고 설명합니다.

결국 대용량 환경에서는 아래처럼 역할을 나눠서 설명하는 것이 깔끔합니다.

- 학습: AutoGluon 단일 GPU
- 데이터 준비: Dask-cuDF 기반 멀티 GPU

핵심은 AutoGluon 자체가 멀티 GPU 학습을 지원하는 것은 아니라는 점입니다.

## 9. 설치와 환경에서 기억할 점

### 9.1 버전과 하드웨어

| 항목 | 내용 |
| --- | --- |
| AutoGluon | Python `3.10`, `3.11`, `3.12`, `3.13` 지원 |
| RAPIDS GPU 요구사항 | NVIDIA Volta 이상, compute capability `7.0+` |
| CUDA | 현재 릴리스 기준 `12` 또는 `13` 계열 요구 |

### 9.2 운영체제 관점

- RAPIDS는 Linux가 기본 축
- Windows는 WSL2 기반 설치 지원
- WSL2 문서에는 single GPU only 제한이 명시됨

따라서 macOS 로컬에서는 AutoGluon 자체 실험은 가능할 수 있어도, RAPIDS를 포함한 GPU 실험은 사실상 원격 Linux 또는 Windows + WSL2 GPU 환경에서 수행하는 것이 현실적입니다.

## 10. 발표에서 강조하면 좋은 메시지

- AutoGluon Time Series의 GPU 활용에는 이미 공식 경로가 있습니다. 딥러닝 모델과 Chronos-2 계열은 `TimeSeriesPredictor` 안에서 zero-shot, fine-tuning, backtest, ensemble 흐름으로 연결됩니다.
- RAPIDS의 역할은 "학습 엔진 교체"보다 "데이터 준비 가속"에 가깝습니다. 특히 `cudf.pandas`는 pandas 워크플로를 크게 바꾸지 않고 GPU 가속을 도입할 수 있다는 점이 강점입니다.
- 단일 GPU 학습과 멀티 GPU 전처리를 구분해서 봐야 합니다. AutoGluon Time Series 학습은 현재 단일 GPU 중심이고, 멀티 GPU가 필요하면 주로 RAPIDS/Dask 기반 전처리 확장 문제로 보는 편이 맞습니다.
- 성능 향상의 핵심은 GPU 자체만이 아니라 covariates 설계와 평가 전략입니다. `prediction_length`, `eval_metric`, `known_covariates`, backtest 설정 같은 문제 정의가 먼저 정교해야 합니다.

## 11. 발표용 최종 정리 문장

한 문장으로 요약하면 아래와 같습니다.

> AutoGluon Time Series에서 GPU는 Chronos-2와 딥러닝 계열 모델을 중심으로 공식 지원되며, NVIDIA RAPIDS는 그 앞단의 pandas 기반 대용량 전처리를 GPU로 가속하는 보완 계층으로 보는 것이 가장 현실적입니다.

## 12. 참고한 공식 문서

- AutoGluon Install
- AutoGluon Time Series Quick Start
- AutoGluon `TimeSeriesPredictor.fit` API
- AutoGluon Time Series FAQ
- Forecasting with Chronos-2
- Forecasting Metrics
- RAPIDS Installation Guide
- cuDF pandas (`cudf.pandas`)
- Dask cuDF documentation
- cuML `cuml.accel` FAQ / Limitations
