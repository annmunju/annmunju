#!/bin/bash
#
# CUDA Toolkit 12.4 설치 스크립트
# WSL2 (Ubuntu) 전용
#

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[CUDA]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[CUDA]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[CUDA]${NC} $1"
}

log_error() {
    echo -e "${RED}[CUDA]${NC} $1"
}

# CUDA 버전 설정 (RAPIDS 25.12 호환)
CUDA_VERSION="12-4"
CUDA_VERSION_DOT="12.4"

check_existing_cuda() {
    if command -v nvcc &> /dev/null; then
        CURRENT_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]*\.[0-9]*\).*/\1/')
        log "기존 CUDA Toolkit 발견: $CURRENT_VERSION"
        
        if [[ "$CURRENT_VERSION" == "$CUDA_VERSION_DOT"* ]]; then
            log_success "CUDA $CUDA_VERSION_DOT 이미 설치됨. 건너뜁니다."
            return 0
        else
            log_warning "다른 버전의 CUDA가 설치되어 있습니다. CUDA $CUDA_VERSION_DOT 설치를 진행합니다."
        fi
    fi
    return 1
}

install_cuda() {
    log "CUDA Toolkit $CUDA_VERSION_DOT 설치 시작..."
    
    # 기존 keyring 제거 (있는 경우)
    sudo rm -f /etc/apt/sources.list.d/cuda*.list 2>/dev/null || true
    
    # WSL-Ubuntu용 CUDA keyring 설치
    log "CUDA keyring 설치 중..."
    KEYRING_FILE="cuda-keyring_1.1-1_all.deb"
    
    if [ ! -f "/tmp/$KEYRING_FILE" ]; then
        wget -q -O "/tmp/$KEYRING_FILE" \
            "https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/$KEYRING_FILE"
    fi
    
    sudo dpkg -i "/tmp/$KEYRING_FILE"
    
    # 패키지 목록 업데이트
    log "패키지 목록 업데이트 중..."
    sudo apt-get update -qq
    
    # CUDA Toolkit 설치
    log "CUDA Toolkit $CUDA_VERSION_DOT 설치 중... (시간이 걸릴 수 있습니다)"
    sudo apt-get install -y cuda-toolkit-${CUDA_VERSION}
    
    log_success "CUDA Toolkit 설치 완료"
}

setup_environment() {
    log "환경 변수 설정 중..."
    
    CUDA_PATH="/usr/local/cuda-${CUDA_VERSION_DOT}"
    
    # bashrc에 환경 변수 추가 (중복 방지)
    if ! grep -q "CUDA_HOME" ~/.bashrc; then
        cat >> ~/.bashrc << EOF

# CUDA Toolkit 환경 변수
export CUDA_HOME=${CUDA_PATH}
export PATH=\${CUDA_HOME}/bin:\${PATH}
export LD_LIBRARY_PATH=\${CUDA_HOME}/lib64:\${LD_LIBRARY_PATH}
EOF
        log_success "환경 변수가 ~/.bashrc에 추가되었습니다."
    else
        log_warning "CUDA 환경 변수가 이미 ~/.bashrc에 존재합니다."
    fi
    
    # WSL2인 경우 wsl 라이브러리 경로 추가
    if grep -qi microsoft /proc/version 2>/dev/null; then
        if ! grep -q "/usr/lib/wsl/lib" ~/.bashrc; then
            cat >> ~/.bashrc << EOF

# WSL2 CUDA 라이브러리 경로
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:\${LD_LIBRARY_PATH}
EOF
            log_success "WSL2 CUDA 경로가 ~/.bashrc에 추가되었습니다."
        fi
    fi
    
    # 현재 세션에도 적용
    export CUDA_HOME=${CUDA_PATH}
    export PATH=${CUDA_HOME}/bin:${PATH}
    export LD_LIBRARY_PATH=/usr/lib/wsl/lib:${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
}

verify_installation() {
    log "설치 확인 중..."
    
    if [ -f "/usr/local/cuda-${CUDA_VERSION_DOT}/bin/nvcc" ]; then
        NVCC_VERSION=$(/usr/local/cuda-${CUDA_VERSION_DOT}/bin/nvcc --version | grep "release" | sed 's/.*release \([0-9]*\.[0-9]*\).*/\1/')
        log_success "CUDA Toolkit $NVCC_VERSION 설치 확인됨"
    else
        log_error "CUDA Toolkit 설치 확인 실패"
        exit 1
    fi
}

main() {
    echo ""
    log "=== CUDA Toolkit 설치 스크립트 ==="
    echo ""
    
    # 기존 설치 확인
    if check_existing_cuda; then
        return 0
    fi
    
    # CUDA 설치
    install_cuda
    
    # 환경 변수 설정
    setup_environment
    
    # 설치 확인
    verify_installation
    
    echo ""
    log_success "CUDA Toolkit 설치가 완료되었습니다."
    echo ""
}

main "$@"
