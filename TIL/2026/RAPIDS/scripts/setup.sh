#!/bin/bash
#
# RAPIDS 환경 전체 설치 스크립트
# WSL2 (Ubuntu) 전용
#

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/setup_$(date +%Y%m%d_%H%M%S).log"

# 로그 함수
log() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# 헤더 출력
print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "   RAPIDS 환경 설치 스크립트"
    echo "   WSL2 (Ubuntu) + CUDA + Conda"
    echo "=============================================="
    echo -e "${NC}"
}

# 시스템 요구사항 체크
check_requirements() {
    log "시스템 요구사항 확인 중..."
    
    # WSL2 확인
    if grep -qi microsoft /proc/version 2>/dev/null; then
        log_success "WSL2 환경 확인됨"
    else
        log_warning "WSL2 환경이 아닐 수 있습니다. 계속 진행합니다."
    fi
    
    # GPU 확인
    if command -v nvidia-smi &> /dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        if [ -n "$GPU_INFO" ]; then
            log_success "GPU 감지됨: $GPU_INFO"
        else
            log_error "nvidia-smi는 있지만 GPU를 감지할 수 없습니다."
            exit 1
        fi
    else
        log_error "nvidia-smi를 찾을 수 없습니다. NVIDIA 드라이버가 설치되어 있는지 확인하세요."
        exit 1
    fi
    
    # CUDA 드라이버 버전 확인
    CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
    log "NVIDIA 드라이버 버전: $CUDA_VERSION"
}

# 메인 실행
main() {
    print_header
    
    # 로그 디렉토리 생성
    mkdir -p "$LOG_DIR"
    log "로그 파일: $LOG_FILE"
    
    # 시스템 체크
    check_requirements
    
    echo ""
    log "설치를 시작합니다..."
    echo ""
    
    # 1. CUDA Toolkit 설치
    log "Step 1/3: CUDA Toolkit 설치"
    if bash "${SCRIPT_DIR}/01_install_cuda.sh"; then
        log_success "CUDA Toolkit 설치 완료"
    else
        log_error "CUDA Toolkit 설치 실패"
        exit 1
    fi
    
    echo ""
    
    # 2. Miniforge/Conda 설치
    log "Step 2/3: Miniforge 설치"
    if bash "${SCRIPT_DIR}/02_install_conda.sh"; then
        log_success "Miniforge 설치 완료"
    else
        log_error "Miniforge 설치 실패"
        exit 1
    fi
    
    echo ""
    
    # 3. RAPIDS 환경 생성
    log "Step 3/3: RAPIDS 환경 생성"
    if bash "${SCRIPT_DIR}/03_create_rapids_env.sh"; then
        log_success "RAPIDS 환경 생성 완료"
    else
        log_error "RAPIDS 환경 생성 실패"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}"
    echo "=============================================="
    echo "   설치가 완료되었습니다!"
    echo "=============================================="
    echo -e "${NC}"
    echo ""
    echo "다음 명령어로 환경을 활성화하세요:"
    echo ""
    echo "  source ~/.bashrc"
    echo "  conda activate rapids"
    echo ""
    echo "테스트:"
    echo "  python -c \"import cudf; print(cudf.__version__)\""
    echo ""
}

main "$@"
