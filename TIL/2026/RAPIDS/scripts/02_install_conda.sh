#!/bin/bash
#
# Miniforge (Conda + Mamba) 설치 스크립트
#

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[CONDA]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[CONDA]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[CONDA]${NC} $1"
}

log_error() {
    echo -e "${RED}[CONDA]${NC} $1"
}

# Miniforge 설치 경로
MINIFORGE_DIR="$HOME/miniforge3"
MINIFORGE_INSTALLER="Miniforge3-Linux-x86_64.sh"

check_existing_conda() {
    if command -v conda &> /dev/null; then
        CONDA_VERSION=$(conda --version 2>/dev/null)
        log_success "Conda 이미 설치됨: $CONDA_VERSION"
        return 0
    fi
    
    if [ -d "$MINIFORGE_DIR" ] && [ -f "$MINIFORGE_DIR/bin/conda" ]; then
        log_success "Miniforge가 이미 설치되어 있습니다: $MINIFORGE_DIR"
        return 0
    fi
    
    return 1
}

install_miniforge() {
    log "Miniforge3 설치 시작..."
    
    # 설치 파일 다운로드
    if [ ! -f "/tmp/$MINIFORGE_INSTALLER" ]; then
        log "Miniforge3 다운로드 중..."
        wget -q --show-progress -O "/tmp/$MINIFORGE_INSTALLER" \
            "https://github.com/conda-forge/miniforge/releases/latest/download/$MINIFORGE_INSTALLER"
    else
        log "기존 설치 파일 사용: /tmp/$MINIFORGE_INSTALLER"
    fi
    
    # 설치 실행 (비대화형)
    log "Miniforge3 설치 중..."
    bash "/tmp/$MINIFORGE_INSTALLER" -b -p "$MINIFORGE_DIR"
    
    log_success "Miniforge3 설치 완료: $MINIFORGE_DIR"
}

setup_conda() {
    log "Conda 초기화 중..."
    
    # conda init 실행
    "$MINIFORGE_DIR/bin/conda" init bash
    
    # 현재 세션에서 conda 활성화
    source "$MINIFORGE_DIR/etc/profile.d/conda.sh"
    
    # mamba 활성화 (이미 포함되어 있음)
    if [ -f "$MINIFORGE_DIR/etc/profile.d/mamba.sh" ]; then
        source "$MINIFORGE_DIR/etc/profile.d/mamba.sh"
    fi
    
    log_success "Conda 초기화 완료"
}

configure_channels() {
    log "채널 설정 중..."
    
    # 채널 우선순위를 flexible로 설정 (RAPIDS 호환성)
    "$MINIFORGE_DIR/bin/conda" config --set channel_priority flexible
    
    # RAPIDS 관련 채널 추가
    "$MINIFORGE_DIR/bin/conda" config --add channels nvidia
    "$MINIFORGE_DIR/bin/conda" config --add channels rapidsai
    "$MINIFORGE_DIR/bin/conda" config --add channels conda-forge
    
    log_success "채널 설정 완료"
}

configure_ssl() {
    # 회사 네트워크 SSL 프록시 인증서 설정
    COMPANY_CA="$HOME/*.pem"
    
    if [ -f "$COMPANY_CA" ]; then
        log "SSL 인증서 설정 중..."
        "$MINIFORGE_DIR/bin/conda" config --set ssl_verify "$COMPANY_CA"
        log_success "SSL 인증서 설정 완료: $COMPANY_CA"
    else
        log_warning "CA 인증서 파일이 없습니다: $COMPANY_CA"
        log_warning "회사 네트워크에서 SSL 오류 발생 시 인증서 파일을 추가하세요."
    fi
}

verify_installation() {
    log "설치 확인 중..."
    
    source "$MINIFORGE_DIR/etc/profile.d/conda.sh"
    
    CONDA_VER=$(conda --version)
    MAMBA_VER=$(mamba --version | head -1)
    
    log_success "Conda: $CONDA_VER"
    log_success "Mamba: $MAMBA_VER"
}

main() {
    echo ""
    log "=== Miniforge (Conda + Mamba) 설치 스크립트 ==="
    echo ""
    
    # 기존 설치 확인
    if check_existing_conda; then
        log "기존 Conda 설치를 사용합니다."
        
        # 채널 설정은 업데이트
        if [ -f "$MINIFORGE_DIR/bin/conda" ]; then
            configure_channels
        fi
        return 0
    fi
    
    # Miniforge 설치
    install_miniforge
    
    # Conda 설정
    setup_conda
    
    # 채널 설정
    configure_channels
    
    # SSL 인증서 설정 (회사 네트워크용)
    configure_ssl
    
    # 설치 확인
    verify_installation
    
    echo ""
    log_success "Miniforge 설치가 완료되었습니다."
    log "새 터미널을 열거나 'source ~/.bashrc'를 실행하세요."
    echo ""
}

main "$@"
