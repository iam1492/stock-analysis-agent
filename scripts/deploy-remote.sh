#!/bin/bash

# 원격 서버 배포 스크립트
# Stock Analysis Agent - Docker Hub에서 이미지 다운로드 및 실행

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
    if [ -z "$IMAGE_VERSION" ]; then
        IMAGE_VERSION="latest"
        read -p "배포할 이미지 버전을 입력하세요 (기본값: latest): " input_version
        if [ ! -z "$input_version" ]; then
            IMAGE_VERSION="$input_version"
        fi
    fi
    
    print_info "배포 버전: $IMAGE_VERSION"
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

# Docker Hub 로그인 확인
check_docker_login() {
    if ! docker info 2>/dev/null | grep -q "Username:"; then
        print_error "Docker Hub에 로그인되어 있지 않습니다."
        print_info "다음 명령으로 로그인하세요:"
        echo "  docker login"
        exit 1
    fi
    
    print_success "Docker Hub 로그인 확인 완료"
}

# 현재 컨테이너 중지
stop_containers() {
    print_header "기존 컨테이너 중지 중..."
    
    # 기존 컨테이너 중지
    if docker compose -f docker-compose-prod.yml ps | grep -q "Up"; then
        docker compose -f docker-compose-prod.yml down
        print_success "기존 컨테이너 중지 완료"
    else
        print_info "실행 중인 컨테이너가 없습니다."
    fi
}

# 새 이미지 다운로드
pull_images() {
    print_header "Docker Hub에서 이미지 다운로드 중..."
    
    # 이미지 풀
    BACKEND_IMAGE="$DOCKER_USERNAME/stock-analysis-backend:$IMAGE_VERSION"
    FRONTEND_IMAGE="$DOCKER_USERNAME/stock-analysis-frontend:$IMAGE_VERSION"
    NGINX_IMAGE="$DOCKER_USERNAME/stock-analysis-nginx:$IMAGE_VERSION"
    
    print_info "백엔드 이미지 다운로드: $BACKEND_IMAGE"
    docker pull "$BACKEND_IMAGE"
    
    print_info "프론트엔드 이미지 다운로드: $FRONTEND_IMAGE"
    docker pull "$FRONTEND_IMAGE"
    
    print_info "Nginx 이미지 다운로드: $NGINX_IMAGE"
    docker pull "$NGINX_IMAGE"
    
    print_success "모든 이미지 다운로드 완료"
}

# 컨테이너 시작
start_containers() {
    print_header "컨테이너 시작 중..."
    
    # 환경 변수 설정
    export DOCKER_USERNAME="$DOCKER_USERNAME"
    export IMAGE_VERSION="$IMAGE_VERSION"
    
    # 컨테이너 시작
    docker compose -f docker-compose-prod.yml up -d
    
    print_success "컨테이너 시작 완료"
}

# 서비스 상태 확인
check_services() {
    print_header "서비스 상태 확인"
    
    # 컨테이너 상태 확인
    print_info "컨테이너 상태:"
    docker compose -f docker-compose-prod.yml ps
    
    echo ""
    
    # 각 서비스 Health Check
    services=("postgres" "stock-analysis-backend" "stock-analysis-frontend" "nginx")
    
    for service in "${services[@]}"; do
        if docker compose -f docker-compose-prod.yml ps | grep -q "$service.*Up"; then
            # Health check 상태 확인
            health_status=$(docker inspect "$service" --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-healthcheck")
            if [ "$health_status" = "healthy" ]; then
                print_success "$service: Healthy"
            elif [ "$health_status" = "no-healthcheck" ]; then
                print_info "$service: Running"
            else
                print_warning "$service: $health_status"
            fi
        else
            print_error "$service: Down"
        fi
    done
}

# 로그 확인
show_logs() {
    print_header "서비스 로그 확인"
    
    print_info "전체 로그 (마지막 50줄):"
    docker compose -f docker-compose-prod.yml logs --tail=50
    
    echo ""
    
    read -p "특정 서비스 로그를 확인하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "서비스 선택:"
        echo "1) backend"
        echo "2) frontend"
        echo "3) nginx"
        echo "4) postgres"
        echo "5) 모든 로그 추적"
        
        read -p "번호를 입력하세요: " choice
        
        case $choice in
            1)
                print_info "백엔드 로그 추적 중..."
                docker compose -f docker-compose-prod.yml logs -f stock-analysis-backend
                ;;
            2)
                print_info "프론트엔드 로그 추적 중..."
                docker compose -f docker-compose-prod.yml logs -f stock-analysis-frontend
                ;;
            3)
                print_info "Nginx 로그 추적 중..."
                docker compose -f docker-compose-prod.yml logs -f nginx
                ;;
            4)
                print_info "PostgreSQL 로그 추적 중..."
                docker compose -f docker-compose-prod.yml logs -f postgres
                ;;
            5)
                print_info "모든 로그 추적 중..."
                docker compose -f docker-compose-prod.yml logs -f
                ;;
            *)
                print_warning "잘못된 선택입니다."
                ;;
        esac
    fi
}

# 백업 생성
create_backup() {
    print_header "데이터베이스 백업 생성"
    
    backup_dir="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # PostgreSQL 백업
    docker exec stock-analysis-postgres pg_dump -U stock_user stock_analysis > "$backup_dir/stock_analysis_backup.sql"
    
    print_success "데이터베이스 백업 완료: $backup_dir/stock_analysis_backup.sql"
    
    # 환경 파일 백업
    if [ -f "app/.env" ]; then
        cp "app/.env" "$backup_dir/app_env_backup"
        print_success "환경 파일 백업 완료: $backup_dir/app_env_backup"
    fi
}

# 완전 배포
deploy_all() {
    print_header "Stock Analysis Agent 배포 시작"
    
    check_docker
    check_docker_login
    get_docker_username
    get_version
    
    echo ""
    print_warning "이 작업은:"
    print_warning "1. 기존 컨테이너를 중지합니다"
    print_warning "2. Docker Hub에서 새 이미지를 다운로드합니다"
    print_warning "3. 새 컨테이너를 시작합니다"
    print_warning "4. 서비스 상태를 확인합니다"
    echo ""
    
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "배포를 취소했습니다."
        exit 0
    fi
    
    # 배포 프로세스
    create_backup
    stop_containers
    pull_images
    start_containers
    
    echo ""
    sleep 5  # 컨테이너 시작 대기
    
    check_services
    
    print_header "배포 완료!"
    print_success "Stock Analysis Agent 배포가 완료되었습니다."
    
    print_info "서비스 접근:"
    echo "  - 웹사이트: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')"
    echo "  - 백엔드 API: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip'):8000"
    
    echo ""
    show_logs
}

# 도움말 함수
show_help() {
    echo "Stock Analysis Agent - 원격 서버 배포 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0                    전체 배포 프로세스"
    echo "  $0 --help            이 도움말 표시"
    echo "  $0 --check           Docker 및 서비스 상태 확인"
    echo "  $0 --pull            Docker Hub에서 이미지만 다운로드"
    echo "  $0 --start           컨테이너만 시작"
    echo "  $0 --stop            컨테이너만 중지"
    echo "  $0 --restart         컨테이너 재시작"
    echo "  $0 --logs            서비스 로그 확인"
    echo "  $0 --backup          데이터베이스 백업만 수행"
    echo ""
    echo "환경 변수:"
    echo "  DOCKER_USERNAME      Docker Hub 사용자명"
    echo "  IMAGE_VERSION        이미지 버전 (기본값: latest)"
    echo ""
    echo "예제:"
    echo "  DOCKER_USERNAME=myuser IMAGE_VERSION=v1.0.0 $0"
    echo "  $0 --logs"
}

# 상태 확인
check_status() {
    print_header "배포 상태 확인"
    
    check_docker
    get_docker_username
    get_version
    
    print_info "현재 설치된 이미지:"
    docker images | grep "$DOCKER_USERNAME"
    
    echo ""
    check_services
}

# 이미지 다운로드만 수행
pull_only() {
    print_header "이미지 다운로드만 수행"
    
    check_docker
    check_docker_login
    get_docker_username
    get_version
    
    pull_images
    
    print_success "이미지 다운로드 완료!"
}

# 컨테이너 시작만 수행
start_only() {
    print_header "컨테이너 시작만 수행"
    
    check_docker
    get_docker_username
    get_version
    
    start_containers
    
    echo ""
    sleep 3
    check_services
}

# 컨테이너 중지만 수행
stop_only() {
    print_header "컨테이너 중지만 수행"
    
    check_docker
    stop_containers
    
    print_success "컨테이너 중지 완료!"
}

# 컨테이너 재시작
restart_containers() {
    print_header "컨테이너 재시작"
    
    check_docker
    get_docker_username
    get_version
    
    docker compose -f docker-compose-prod.yml restart
    
    print_success "컨테이너 재시작 완료!"
    
    echo ""
    sleep 3
    check_services
}

# 메인 로직
case "$1" in
    "--help")
        show_help
        exit 0
        ;;
    "--check")
        check_status
        exit 0
        ;;
    "--pull")
        pull_only
        exit 0
        ;;
    "--start")
        start_only
        exit 0
        ;;
    "--stop")
        stop_only
        exit 0
        ;;
    "--restart")
        restart_containers
        exit 0
        ;;
    "--logs")
        show_logs
        exit 0
        ;;
    "--backup")
        create_backup
        exit 0
        ;;
    "")
        deploy_all
        exit 0
        ;;
    *)
        print_error "알 수 없는 옵션: $1"
        echo "도움말을 보려면 --help 옵션을 사용하세요."
        exit 1
        ;;
esac