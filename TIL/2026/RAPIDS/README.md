# 모두의 연구소 RAPIDS 기록

NVIDIA RAPIDS를 활용한 GPU 가속 데이터 분석 학습 프로젝트입니다.

## 환경 설정

### Conda 설치 방법

RAPIDS 공식 권장 방식입니다. GPU 가속 기능을 완전히 지원합니다.

```bash
# 전체 자동 설치
cd scripts
chmod +x *.sh
./setup.sh

# 환경 활성화
source ~/.bashrc
conda activate rapids

# 테스트
python -c "import cudf; print(cudf.__version__)"
```

자세한 내용은 [scripts/README.md](scripts/README.md)를 참고하세요.

## 프로젝트 구조

```
RAPIDS/
├── scripts/              # 환경 설정 스크립트
├── 1_RAPIDS_study/       # RAPIDS 기본 학습
├── 2_AutoML_study/       # AutoML 학습
├── 3_AutoML_with_RAPIDS/ # RAPIDS + AutoML 통합
└── data/                 # 데이터 (git 제외)
```

## 설치 패키지

| 패키지 | 버전 | 설명 |
|--------|------|------|
| cuDF | 25.02 | GPU DataFrame (pandas 대체) |
| cuML | 25.02 | GPU 머신러닝 (scikit-learn 대체) |
| Dask-cuDF | 25.02 | 분산 GPU DataFrame |

## 요구사항

- **OS**: WSL2 (Ubuntu 20.04+) 또는 Linux
- **GPU**: NVIDIA GPU (Compute Capability 6.0+)
- **드라이버**: NVIDIA Driver 450.80.02+
- **Python**: 3.11
