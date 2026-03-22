# RAPIDS 환경 설정 스크립트

WSL2 (Ubuntu) 환경에서 NVIDIA RAPIDS를 설치하기 위한 자동화 스크립트입니다.

## 요구사항

- **OS**: WSL2 (Ubuntu 20.04 이상)
- **GPU**: NVIDIA GPU (Compute Capability 6.0 이상)
- **드라이버**: Windows에 NVIDIA 드라이버 설치 필요 (WSL2 자동 지원)

## 빠른 시작

```bash
# 1. 스크립트 실행 권한 부여
cd scripts
chmod +x *.sh

# 2. 전체 자동 설치 (권장)
./setup.sh

# 3. 설치 완료 후
source ~/.bashrc
conda activate rapids
```

## 스크립트 구성

| 파일 | 설명 |
|------|------|
| `setup.sh` | 메인 설치 스크립트 (전체 자동화) |
| `01_install_cuda.sh` | CUDA Toolkit 12.4 설치 |
| `02_install_conda.sh` | Miniforge (Conda + Mamba) 설치 |
| `03_create_rapids_env.sh` | RAPIDS conda 환경 생성 |
| `config/rapids_env.yml` | Conda 환경 정의 파일 |

## 개별 실행

전체 설치 대신 개별 스크립트를 실행할 수 있습니다:

```bash
# CUDA Toolkit만 설치
./01_install_cuda.sh

# Conda만 설치
./02_install_conda.sh

# RAPIDS 환경만 생성 (Conda 필요)
./03_create_rapids_env.sh
```

## 설치 패키지

`config/rapids_env.yml`에 정의된 패키지:

### RAPIDS 핵심
- `rapids=25.12` (cuDF, cuML, cuGraph 등 포함)
- `cuda-version=12.4`

### 데이터 분석
- `pandas`, `numpy`
- `scikit-learn`
- `matplotlib`, `seaborn`

### 개발 도구
- `jupyterlab`
- `ipykernel`

## 환경 관리

```bash
# 환경 활성화
conda activate rapids

# 환경 비활성화
conda deactivate

# 환경 삭제
conda env remove -n rapids

# 환경 재생성
./03_create_rapids_env.sh
```

## 테스트

```bash
conda activate rapids

# cuDF 테스트
python -c "import cudf; print(f'cuDF version: {cudf.__version__}')"

# GPU 메모리 확인
python -c "
import cudf
import rmm
rmm.reinitialize(pool_allocator=True)
df = cudf.DataFrame({'a': range(1000000)})
print(f'DataFrame created with {len(df)} rows')
"
```

## Jupyter Lab 사용

```bash
conda activate rapids
jupyter lab
```

Jupyter에서 "Python (RAPIDS)" 커널을 선택하세요.

## 문제 해결

### SSL 인증서 오류 (네트워크)

네트워크에서 SSL 프록시를 사용하는 경우:

```bash
# 방법 1: CA 인증서 설정
conda config --set ssl_verify ~/{키 이름}.pem

# 방법 2: 시스템 CA 번들 사용
conda config --set ssl_verify /etc/ssl/certs/ca-certificates.crt

# 방법 3: SSL 검증 비활성화 (임시, 비권장)
conda config --set ssl_verify false
```

### GPU를 찾을 수 없음
```bash
# Windows 드라이버 확인
nvidia-smi
```
Windows에 최신 NVIDIA 드라이버가 설치되어 있는지 확인하세요.

### CUDA 버전 불일치
```bash
# 설치된 CUDA 버전 확인
nvcc --version

# RAPIDS 호환 CUDA 버전: 12.4
```

### 환경 생성 실패
```bash
# 로그 확인
cat logs/setup_*.log

# 캐시 정리 후 재시도
mamba clean --all
./03_create_rapids_env.sh
```

## 로그

설치 로그는 `scripts/logs/` 디렉토리에 저장됩니다:
```
logs/
└── setup_YYYYMMDD_HHMMSS.log
```

## 참고 자료

- [RAPIDS 공식 문서](https://docs.rapids.ai/)
- [RAPIDS 설치 가이드](https://docs.rapids.ai/install)
- [WSL2 CUDA 설정](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)
