#!/bin/bash
#
# RAPIDS Conda 환경 생성 스크립트
#

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[RAPIDS]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[RAPIDS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[RAPIDS]${NC} $1"
}

log_error() {
    echo -e "${RED}[RAPIDS]${NC} $1"
}

# 스크립트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/config/rapids_env.yml"
ENV_NAME="rapids"

# Miniforge 경로
MINIFORGE_DIR="$HOME/miniforge3"

init_conda() {
    log "Conda 환경 초기화 중..."
    
    # conda가 PATH에 없으면 직접 로드
    if ! command -v conda &> /dev/null; then
        if [ -f "$MINIFORGE_DIR/etc/profile.d/conda.sh" ]; then
            source "$MINIFORGE_DIR/etc/profile.d/conda.sh"
        else
            log_error "Conda를 찾을 수 없습니다. 02_install_conda.sh를 먼저 실행하세요."
            exit 1
        fi
    fi
    
    # mamba 로드
    if [ -f "$MINIFORGE_DIR/etc/profile.d/mamba.sh" ]; then
        source "$MINIFORGE_DIR/etc/profile.d/mamba.sh"
    fi
}

check_existing_env() {
    if conda env list | grep -q "^${ENV_NAME} "; then
        log_warning "환경 '${ENV_NAME}'이 이미 존재합니다."
        
        read -p "기존 환경을 삭제하고 재생성하시겠습니까? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "기존 환경 삭제 중..."
            conda env remove -n "$ENV_NAME" -y
            return 1
        else
            log "기존 환경을 유지합니다."
            return 0
        fi
    fi
    return 1
}

create_environment() {
    log "RAPIDS 환경 생성 중..."
    log "환경 파일: $ENV_FILE"
    log "이 작업은 시간이 오래 걸릴 수 있습니다 (10-30분)..."
    echo ""
    
    # mamba가 있으면 mamba 사용 (더 빠름)
    if command -v mamba &> /dev/null; then
        log "mamba를 사용하여 환경 생성..."
        mamba env create -f "$ENV_FILE" -y
    else
        log "conda를 사용하여 환경 생성..."
        conda env create -f "$ENV_FILE" -y
    fi
    
    log_success "환경 생성 완료"
}

verify_environment() {
    log "환경 확인 중..."
    
    # RAPIDS 버전 확인 (mamba run 사용)
    echo ""
    log "설치된 RAPIDS 패키지:"
    mamba run -n "$ENV_NAME" python -c "
import sys
print(f'Python: {sys.version}')

try:
    import cudf
    print(f'cuDF: {cudf.__version__}')
except ImportError as e:
    print(f'cuDF: 설치 안됨 ({e})')

try:
    import cuml
    print(f'cuML: {cuml.__version__}')
except ImportError as e:
    print(f'cuML: 설치 안됨 ({e})')

try:
    import dask_cudf
    print(f'Dask-cuDF: {dask_cudf.__version__}')
except ImportError as e:
    print(f'Dask-cuDF: 설치 안됨 ({e})')
" 2>/dev/null || log_warning "일부 패키지 확인 실패 (GPU 환경에서 확인 필요)"
}

register_jupyter_kernel() {
    log "Jupyter 커널 등록 중..."
    
    # mamba run을 사용하여 환경 내에서 실행
    mamba run -n "$ENV_NAME" python -m ipykernel install --user --name "$ENV_NAME" --display-name "Python (RAPIDS)" 2>/dev/null || \
    conda run -n "$ENV_NAME" python -m ipykernel install --user --name "$ENV_NAME" --display-name "Python (RAPIDS)"
    
    log_success "Jupyter 커널 등록 완료: Python (RAPIDS)"
}

main() {
    echo ""
    log "=== RAPIDS Conda 환경 생성 스크립트 ==="
    echo ""
    
    # 환경 파일 확인
    if [ ! -f "$ENV_FILE" ]; then
        log_error "환경 파일을 찾을 수 없습니다: $ENV_FILE"
        exit 1
    fi
    
    # Conda 초기화
    init_conda
    
    # 기존 환경 확인
    if check_existing_env; then
        log "기존 환경을 사용합니다."
    else
        # 환경 생성
        create_environment
    fi
    
    # Jupyter 커널 등록
    register_jupyter_kernel
    
    # 환경 확인
    verify_environment
    
    echo ""
    log_success "RAPIDS 환경 설정이 완료되었습니다."
    echo ""
    echo "환경 활성화:"
    echo "  conda activate $ENV_NAME"
    echo ""
    echo "Jupyter Lab 실행:"
    echo "  jupyter lab"
    echo ""
}

main "$@"
