#!/bin/bash

# Docker Hub 이미지 업로드 스크립트
# Stock Analysis Agent - Docker Hub에 이미지 업로드

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
    
    print_info "업로드 버전: $VERSION"
}

# Docker 로그인 확인
check_docker_login() {
    if ! docker info 2>/dev/null | grep -q "Username:"; then
        print_error "Docker Hub에 로그인되어 있지 않습니다."
        print_info "다음 명령으로 로그인하세요:"
        echo "  docker login"
        exit 1
    fi
    
    print_success "Docker Hub 로그인 확인 완료"
}

# 백엔드 이미지 업로드
push_backend() {
    print_header "백엔드 이미지 Docker Hub 업로드 중..."
    
    BACKEND_TAG="stock-analysis-backend"
    DOCKER_TAG="$DOCKER_USERNAME/$BACKEND_TAG:$VERSION"
    
    # 로컬 이미지 확인
    if ! docker images | grep -q "$BACKEND_TAG"; then
        print_error "로컬에 백엔드 이미지가 없습니다. 먼저 빌드하세요."
        exit 1
    fi
    
    # Docker Hub에 업로드
    print_info "업로드 중: $DOCKER_TAG"
    docker push "$DOCKER_TAG"
    
    # latest 태그도 업로드 (현재 버전이 latest가 아닐 때)
    if [ "$VERSION" != "latest" ]; then
        LATEST_TAG="$DOCKER_USERNAME/$BACKEND_TAG:latest"
        docker tag "$DOCKER_TAG" "$LATEST_TAG"
        docker push "$LATEST_TAG"
        print_success "latest 태그 업로드 완료: $LATEST_TAG"
    fi
    
    print_success "백엔드 이미지 업로드 완료: $DOCKER_TAG"
}

# 프론트엔드 이미지 업로드
push_frontend() {
    print_header "프론트엔드 이미지 Docker Hub 업로드 중..."
    
    FRONTEND_TAG="stock-analysis-frontend"
    DOCKER_TAG="$DOCKER_USERNAME/$FRONTEND_TAG:$VERSION"
    
    # 로컬 이미지 확인
    if ! docker images | grep -q "$FRONTEND_TAG"; then
        print_error "로컬에 프론트엔드 이미지가 없습니다. 먼저 빌드하세요."
        exit 1
    fi
    
    # Docker Hub에 업로드
    print_info "업로드 중: $DOCKER_TAG"
    docker push "$DOCKER_TAG"
    
    # latest 태그도 업로드 (현재 버전이 latest가 아닐 때)
    if [ "$VERSION" != "latest" ]; then
        LATEST_TAG="$DOCKER_USERNAME/$FRONTEND_TAG:latest"
        docker tag "$DOCKER_TAG" "$LATEST_TAG"
        docker push "$LATEST_TAG"
        print_success "latest 태그 업로드 완료: $LATEST_TAG"
    fi
    
    print_success "프론트엔드 이미지 업로드 완료: $DOCKER_TAG"
}

# Nginx 이미지 업로드
push_nginx() {
    print_header "Nginx 이미지 Docker Hub 업로드 중..."
    
    NGINX_TAG="stock-analysis-nginx"
    DOCKER_TAG="$DOCKER_USERNAME/$NGINX_TAG:$VERSION"
    
    # 로컬 이미지 확인
    if ! docker images | grep -q "$NGINX_TAG"; then
        print_error "로컬에 Nginx 이미지가 없습니다. 먼저 빌드하세요."
        exit 1
    fi
    
    # Docker Hub에 업로드
    print_info "업로드 중: $DOCKER_TAG"
    docker push "$DOCKER_TAG"
    
    # latest 태그도 업로드 (현재 버전이 latest가 아닐 때)
    if [ "$VERSION" != "latest" ]; then
        LATEST_TAG="$DOCKER_USERNAME/$NGINX_TAG:latest"
        docker tag "$DOCKER_TAG" "$LATEST_TAG"
        docker push "$LATEST_TAG"
        print_success "latest 태그 업로드 완료: $LATEST_TAG"
    fi
    
    print_success "Nginx 이미지 업로드 완료: $DOCKER_TAG"
}

# 모든 이미지 업로드
push_all() {
    print_header "Docker Hub 이미지 업로드 시작"
    
    check_docker_login
    get_docker_username
    get_version
    
    print_info "다음 이미지들을 Docker Hub에 업로드합니다:"
    print_info "- $DOCKER_USERNAME/stock-analysis-backend:$VERSION"
    print_info "- $DOCKER_USERNAME/stock-analysis-frontend:$VERSION"
    print_info "- $DOCKER_USERNAME/stock-analysis-nginx:$VERSION"
    echo ""
    
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "업로드를 취소했습니다."
        exit 0
    fi
    
    # 이미지 업로드
    push_backend
    push_frontend
    push_nginx
    
    print_header "업로드 완료!"
    print_success "모든 이미지가 성공적으로 Docker Hub에 업로드되었습니다."
    
    print_info "업로드된 이미지:"
    echo "  $DOCKER_USERNAME/stock-analysis-backend:$VERSION"
    echo "  $DOCKER_USERNAME/stock-analysis-frontend:$VERSION"
    echo "  $DOCKER_USERNAME/stock-analysis-nginx:$VERSION"
}

# Docker Hub 상태 확인
check_docker_hub() {
    print_header "Docker Hub 상태 확인"
    
    if [ -z "$DOCKER_USERNAME" ]; then
        get_docker_username
    fi
    
    print_info "Docker Hub 사용자명: $DOCKER_USERNAME"
    
    # Docker Hub 연결 상태 확인
    if docker info &>/dev/null; then
        print_success "Docker Hub 연결 상태 정상"
        
        # 레포지토리 존재 확인
        print_info "레포지토리 확인 중..."
        for repo in stock-analysis-backend stock-analysis-frontend stock-analysis-nginx; do
            if curl -s "https://hub.docker.com/v2/repositories/$DOCKER_USERNAME/$repo/" &>/dev/null; then
                print_success "레포지토리 존재: $repo"
            else
                print_warning "레포지토리 없음 또는 비공개: $repo"
            fi
        done
    else
        print_error "Docker 서비스 연결 실패"
        exit 1
    fi
}

# 도움말 함수
show_help() {
    echo "Stock Analysis Agent - Docker Hub 이미지 업로드 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0                    모든 이미지 업로드"
    echo "  $0 --help            이 도움말 표시"
    echo "  $0 --check           Docker Hub 상태 확인"
    echo "  $0 --backend         백엔드 이미지만 업로드"
    echo "  $0 --frontend        프론트엔드 이미지만 업로드"
    echo "  $0 --nginx           Nginx 이미지만 업로드"
    echo ""
    echo "환경 변수:"
    echo "  DOCKER_USERNAME      Docker Hub 사용자명"
    echo "  VERSION              이미지 버전 (기본값: latest)"
    echo ""
    echo "예제:"
    echo "  DOCKER_USERNAME=myuser $0"
    echo "  VERSION=v1.0.0 $0 --backend"
}

# 단일 이미지 업로드
push_single() {
    local service=$1
    check_docker_login
    get_docker_username
    get_version
    
    case $service in
        "backend")
            push_backend
            ;;
        "frontend")
            push_frontend
            ;;
        "nginx")
            push_nginx
            ;;
        *)
            print_error "알 수 없는 서비스: $service"
            exit 1
            ;;
    esac
    
    print_success "$service 이미지 업로드 완료!"
}

# 메인 로직
case "$1" in
    "--help")
        show_help
        exit 0
        ;;
    "--check")
        check_docker_hub
        exit 0
        ;;
    "--backend")
        push_single "backend"
        exit 0
        ;;
    "--frontend")
        push_single "frontend"
        exit 0
        ;;
    "--nginx")
        push_single "nginx"
        exit 0
        ;;
    "")
        push_all
        exit 0
        ;;
    *)
        print_error "알 수 없는 옵션: $1"
        echo "도움말을 보려면 --help 옵션을 사용하세요."
        exit 1
        ;;
esac