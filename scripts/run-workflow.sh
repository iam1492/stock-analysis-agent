#!/bin/bash

# 통합 워크플로우 실행 스크립트
# Stock Analysis Agent - 전체 배포 프로세스 통합

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

# 스크립트 디렉토리 확인
SCRIPT_DIR="$(dirname "$0")"

# 필수 파일 확인
check_requirements() {
    print_header "필수 요구사항 확인"
    
    local missing_files=()
    
    if [ ! -f "$SCRIPT_DIR/build-images.sh" ]; then
        missing_files+=("build-images.sh")
    fi
    
    if [ ! -f "$SCRIPT_DIR/push-images.sh" ]; then
        missing_files+=("push-images.sh")
    fi
    
    if [ ! -f "$SCRIPT_DIR/deploy-remote.sh" ]; then
        missing_files+=("deploy-remote.sh")
    fi
    
    if [ ! -f "docker-compose-prod.yml" ]; then
        missing_files+=("docker-compose-prod.yml")
    fi
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        print_error "다음 파일들이 누락되었습니다:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
    
    print_success "모든 필수 파일 확인 완료"
}

# Docker 서비스 확인
check_docker() {
    print_info "Docker 서비스 확인..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker 데몬에 연결할 수 없습니다."
        exit 1
    fi
    
    print_success "Docker 서비스 정상"
}

# Git 상태 확인
check_git() {
    if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
        print_info "Git 저장소 확인됨"
        
        # 변경사항 확인
        if ! git diff-index --quiet HEAD -- || ! git diff --quiet HEAD; then
            print_warning "커밋되지 않은 변경사항이 있습니다."
            return 1
        fi
        return 0
    fi
    return 0
}

# Docker Hub 사용자명 설정
setup_docker_username() {
    if [ -z "$DOCKER_USERNAME" ]; then
        print_warning "DOCKER_USERNAME 환경 변수가 설정되지 않았습니다."
        read -p "Docker Hub 사용자명을 입력하세요: " DOCKER_USERNAME
        
        if [ -z "$DOCKER_USERNAME" ]; then
            print_error "Docker Hub 사용자명이 필요합니다."
            exit 1
        fi
    fi
    
    print_info "Docker Hub 사용자명: $DOCKER_USERNAME"
}

# 버전 설정
setup_version() {
    if [ -z "$VERSION" ]; then
        VERSION="latest"
        print_info "버전 설정: $VERSION"
    else
        print_info "지정된 버전 사용: $VERSION"
    fi
}

# 프로덕션 환경 확인
check_production_readiness() {
    print_header "프로덕션 준비도 확인"
    
    # 환경 파일 확인
    if [ ! -f "app/.env" ]; then
        print_warning "app/.env 파일이 없습니다."
        print_info "새로운 app/.env 파일을 생성하거나 기존 파일을 복사하세요."
    else
        print_success "환경 파일 확인됨: app/.env"
    fi
    
    # 데이터베이스 설정 확인
    if grep -q "POSTGRES_PASSWORD" app/.env 2>/dev/null; then
        print_success "데이터베이스 비밀번호 설정됨"
    else
        print_warning "데이터베이스 비밀번호가 설정되지 않았습니다."
    fi
}

# Docker 이미지 빌드
build_images() {
    print_header "Docker 이미지 빌드"
    
    if [ "$SKIP_BUILD" = "true" ]; then
        print_info "빌드 단계를 건너뜁니다."
        return
    fi
    
    # 스크립트 권한 확인
    if [ ! -x "$SCRIPT_DIR/build-images.sh" ]; then
        print_info "스크립트 권한 설정..."
        chmod +x "$SCRIPT_DIR/build-images.sh"
    fi
    
    # 빌드 실행
    DOCKER_USERNAME="$DOCKER_USERNAME" VERSION="$VERSION" "$SCRIPT_DIR/build-images.sh"
    
    if [ $? -eq 0 ]; then
        print_success "Docker 이미지 빌드 완료"
    else
        print_error "Docker 이미지 빌드 실패"
        exit 1
    fi
}

# Docker Hub에 이미지 업로드
push_images() {
    print_header "Docker Hub 이미지 업로드"
    
    if [ "$SKIP_PUSH" = "true" ]; then
        print_info "업로드 단계를 건너뜁니다."
        return
    fi
    
    # Docker Hub 로그인 확인
    if ! docker info 2>/dev/null | grep -q "Username:"; then
        print_error "Docker Hub에 로그인되어 있지 않습니다."
        print_info "다음 명령으로 로그인하세요: docker login"
        exit 1
    fi
    
    # 업로드 실행
    DOCKER_USERNAME="$DOCKER_USERNAME" VERSION="$VERSION" "$SCRIPT_DIR/push-images.sh"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Hub 이미지 업로드 완료"
    else
        print_error "Docker Hub 이미지 업로드 실패"
        exit 1
    fi
}

# 원격 서버 배포
deploy_remote() {
    print_header "원격 서버 배포"
    
    if [ "$SKIP_DEPLOY" = "true" ]; then
        print_info "배포 단계를 건너뜁니다."
        return
    fi
    
    print_warning "이제 원격 서버에서 배포를 진행합니다."
    print_info "원격 서버에 접속하여 다음 명령을 실행하세요:"
    echo ""
    echo "DOCKER_USERNAME=$DOCKER_USERNAME IMAGE_VERSION=$VERSION bash deploy-remote.sh"
    echo ""
    
    read -p "원격 서버에 접속하여 배포 명령을 실행한 후 Enter를 눌러 계속하세요..."
    
    # 원격 서버 상태 확인
    read -p "배포 후 서비스 상태 확인을 위해 HTTP 응답을 테스트하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_remote_service
    fi
}

# 원격 서비스 테스트
test_remote_service() {
    print_info "원격 서버 서비스 상태 확인"
    
    local server_ip
    server_ip=$(curl -s ifconfig.me 2>/dev/null || echo "remote-server-ip")
    
    print_info "서버 IP: $server_ip"
    
    # HTTP 서비스 테스트
    if curl -s -o /dev/null -w "%{http_code}" "http://$server_ip" | grep -q "200"; then
        print_success "웹사이트 접근 가능: http://$server_ip"
    else
        print_warning "웹사이트 접근 불가 또는 아직 준비되지 않음"
    fi
    
    # 백엔드 API 테스트
    if curl -s -o /dev/null -w "%{http_code}" "http://$server_ip:8000/health" | grep -q "200"; then
        print_success "백엔드 API 접근 가능: http://$server_ip:8000"
    else
        print_warning "백엔드 API 접근 불가"
    fi
}

# 워크플로우 요약
show_workflow_summary() {
    print_header "워크플로우 요약"
    
    print_info "생성된 이미지:"
    echo "  - $DOCKER_USERNAME/stock-analysis-backend:$VERSION"
    echo "  - $DOCKER_USERNAME/stock-analysis-frontend:$VERSION"
    echo "  - $DOCKER_USERNAME/stock-analysis-nginx:$VERSION"
    
    echo ""
    print_info "사용된 파일:"
    echo "  - docker-compose-prod.yml (프로덕션용)"
    echo "  - app/.env (환경 변수)"
    
    echo ""
    print_info "원격 서버 배포:"
    echo "  - docker-compose-prod.yml 사용"
    echo "  - Docker Hub에서 이미지 다운로드"
    echo "  - 기존 컨테이너 자동 교체"
    
    echo ""
    print_success "워크플로우 실행 완료!"
}

# 도움말 함수
show_help() {
    echo "Stock Analysis Agent - 통합 워크플로우 실행 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0                    전체 워크플로우 실행"
    echo "  $0 --help            이 도움말 표시"
    echo "  $0 --check           요구사항만 확인"
    echo "  $0 --build-only      Docker 이미지 빌드만 수행"
    echo "  $0 --push-only       Docker Hub 업로드만 수행"
    echo "  $0 --deploy-only     원격 배포만 수행"
    echo ""
    echo "환경 변수:"
    echo "  DOCKER_USERNAME      Docker Hub 사용자명 (필수)"
    echo "  VERSION              이미지 버전 (기본값: latest)"
    echo "  SKIP_BUILD=true      빌드 단계 건너뛰기"
    echo "  SKIP_PUSH=true       업로드 단계 건너뛰기"
    echo "  SKIP_DEPLOY=true     배포 단계 건너뛰기"
    echo ""
    echo "예제:"
    echo "  DOCKER_USERNAME=myuser VERSION=v1.0.0 $0"
    echo "  DOCKER_USERNAME=myuser $0 --build-only"
    echo "  SKIP_BUILD=true DOCKER_USERNAME=myuser $0 --push-only"
}

# 전체 워크플로우 실행
run_full_workflow() {
    print_header "Stock Analysis Agent - 전체 워크플로우 시작"
    
    # 준비 단계
    check_requirements
    check_docker
    setup_docker_username
    setup_version
    
    # Git 상태 확인 (선택사항)
    if ! check_git; then
        read -p "Git 변경사항이 있습니다. 커밋하고 계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Git 변경사항을 커밋하세요..."
            read -p "커밋 완료 후 Enter를 눌러 계속하세요..."
        fi
    fi
    
    # 프로덕션 준비도 확인
    check_production_readiness
    
    echo ""
    print_warning "이제 다음 단계가 실행됩니다:"
    print_warning "1. Docker 이미지 빌드"
    print_warning "2. Docker Hub 업로드"
    print_warning "3. 원격 서버 배포 가이드"
    echo ""
    
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "워크플로우 실행을 취소했습니다."
        exit 0
    fi
    
    # 워크플로우 단계별 실행
    build_images
    push_images
    deploy_remote
    
    # 최종 요약
    show_workflow_summary
}

# 메인 로직
case "$1" in
    "--help")
        show_help
        exit 0
        ;;
    "--check")
        check_requirements
        check_docker
        print_success "모든 요구사항 확인 완료"
        exit 0
        ;;
    "--build-only")
        check_requirements
        check_docker
        setup_docker_username
        setup_version
        build_images
        exit 0
        ;;
    "--push-only")
        check_requirements
        check_docker
        setup_docker_username
        setup_version
        push_images
        exit 0
        ;;
    "--deploy-only")
        check_requirements
        deploy_remote
        exit 0
        ;;
    "")
        run_full_workflow
        exit 0
        ;;
    *)
        print_error "알 수 없는 옵션: $1"
        echo "도움말을 보려면 --help 옵션을 사용하세요."
        exit 1
        ;;
esac