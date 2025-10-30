#!/bin/bash

# Docker 이미지 빌드 스크립트
# Stock Analysis Agent - 로컬 Docker 이미지 빌드

set -e

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Docker Hub 사용자명 입력받기
get_docker_username() {
    if [ -z "$DOCKER_USERNAME" ]; then
        echo ""
        print_warning "Docker Hub 사용자명이 설정되지 않았습니다."
        read -p "Docker Hub 사용자명을 입력하세요: " DOCKER_USERNAME
    fi
    
    if [ -z "$DOCKER_USERNAME" ]; then
        print_error "Docker Hub 사용자명이 필요합니다. 스크립트를 중단합니다."
        exit 1
    fi
    
    print_info "Docker Hub 사용자명: $DOCKER_USERNAME"
}

# 버전 정보 입력받기
get_version() {
    if [ -z "$VERSION" ]; then
        VERSION="latest"
        read -p "버전을 입력하세요 (기본값: latest): " input_version
        if [ ! -z "$input_version" ]; then
            VERSION="$input_version"
        fi
    fi
    
    print_info "빌드 버전: $VERSION"
}

# Docker 서비스 확인
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker 데몬에 연결할 수 없습니다."
        exit 1
    fi
    
    print_success "Docker 서비스 확인 완료"
}

# 백엔드 이미지 빌드
build_backend() {
    print_header "백엔드 이미지 빌드 중..."
    
    cd "$(dirname "$0")"
    
    # 백엔드 이미지 태그
    BACKEND_TAG="stock-analysis-backend"
    DOCKER_TAG="$DOCKER_USERNAME/$BACKEND_TAG:$VERSION"
    
    # 이미지 빌드
    docker build -f Dockerfile.backend -t "$BACKEND_TAG" .
    
    # Docker Hub 태그 추가
    docker tag "$BACKEND_TAG" "$DOCKER_TAG"
    
    print_success "백엔드 이미지 빌드 완료: $DOCKER_TAG"
}

# 프론트엔드 이미지 빌드
build_frontend() {
    print_header "프론트엔드 이미지 빌드 중..."
    
    # 프론트엔드 이미지 태그
    FRONTEND_TAG="stock-analysis-frontend"
    DOCKER_TAG="$DOCKER_USERNAME/$FRONTEND_TAG:$VERSION"
    
    # 이미지 빌드
    cd nextjs
    docker build -f Dockerfile -t "$FRONTEND_TAG" .
    cd ..
    
    # Docker Hub 태그 추가
    docker tag "$FRONTEND_TAG" "$DOCKER_TAG"
    
    print_success "프론트엔드 이미지 빌드 완료: $DOCKER_TAG"
}

# Nginx 이미지 빌드
build_nginx() {
    print_header "Nginx 이미지 빌드 중..."
    
    # Nginx 이미지 태그
    NGINX_TAG="stock-analysis-nginx"
    DOCKER_TAG="$DOCKER_USERNAME/$NGINX_TAG:$VERSION"
    
    # 이미지 빌드
    docker build -f Dockerfile.nginx -t "$NGINX_TAG" .
    
    # Docker Hub 태그 추가
    docker tag "$NGINX_TAG" "$DOCKER_TAG"
    
    print_success "Nginx 이미지 빌드 완료: $DOCKER_TAG"
}

# 모든 이미지 빌드
build_all() {
    print_header "Docker 이미지 빌드 시작"
    
    check_docker
    get_docker_username
    get_version
    
    print_info "다음 이미지들을 빌드합니다:"
    print_info "- stock-analysis-backend:$VERSION"
    print_info "- stock-analysis-frontend:$VERSION"
    print_info "- stock-analysis-nginx:$VERSION"
    echo ""
    
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "빌드를 취소했습니다."
        exit 0
    fi
    
    # 이미지 빌드
    build_backend
    build_frontend
    build_nginx
    
    print_header "빌드 완료!"
    print_success "모든 이미지가 성공적으로 빌드되었습니다."
    
    print_info "빌드된 이미지:"
    docker images | grep "$DOCKER_USERNAME"
}

# 도움말 함수
show_help() {
    echo "Stock Analysis Agent - Docker 이미지 빌드 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0                    모든 이미지 빌드"
    echo "  $0 --help            이 도움말 표시"
    echo "  $0 --backend         백엔드 이미지만 빌드"
    echo "  $0 --frontend        프론트엔드 이미지만 빌드"
    echo "  $0 --nginx           Nginx 이미지만 빌드"
    echo ""
    echo "환경 변수:"
    echo "  DOCKER_USERNAME      Docker Hub 사용자명"
    echo "  VERSION              이미지 버전 (기본값: latest)"
    echo ""
    echo "예제:"
    echo "  DOCKER_USERNAME=myuser $0"
    echo "  VERSION=v1.0.0 $0"
}

# 단일 이미지 빌드
build_single() {
    local service=$1
    check_docker
    get_docker_username
    get_version
    
    case $service in
        "backend")
            build_backend
            ;;
        "frontend")
            build_frontend
            ;;
        "nginx")
            build_nginx
            ;;
        *)
            print_error "알 수 없는 서비스: $service"
            exit 1
            ;;
    esac
    
    print_success "$service 이미지 빌드 완료!"
}

# 메인 로직
case "$1" in
    "--help")
        show_help
        exit 0
        ;;
    "--backend")
        build_single "backend"
        exit 0
        ;;
    "--frontend")
        build_single "frontend"
        exit 0
        ;;
    "--nginx")
        build_single "nginx"
        exit 0
        ;;
    "")
        build_all
        exit 0
        ;;
    *)
        print_error "알 수 없는 옵션: $1"
        echo "도움말을 보려면 --help 옵션을 사용하세요."
        exit 1
        ;;
esac