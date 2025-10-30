#!/bin/bash

# 자동 버전 생성 스크립트
# Stock Analysis Agent - Git 기반 자동 버전 생성

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

# Git 상태 확인
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git이 설치되지 않았습니다."
        exit 1
    fi
    
    if ! git rev-parse --git-dir &> /dev/null; then
        print_error "Git 저장소가 아닙니다."
        exit 1
    fi
    
    print_success "Git 저장소 확인 완료"
}

# 현재 브랜치 확인
get_current_branch() {
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    print_info "현재 브랜치: $BRANCH"
    echo "$BRANCH"
}

# 최신 태그 가져오기
get_latest_tag() {
    local tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [ ! -z "$tag" ]; then
        echo "$tag"
    else
        echo ""
    fi
}

# 커밋 수 계산
get_commit_count() {
    if [ -z "$BASE_TAG" ]; then
        echo "0"
    else
        git rev-list --count "$BASE_TAG"..HEAD 2>/dev/null || echo "0"
    fi
}

# 커밋 해시 가져오기
get_commit_hash() {
    echo "$(git rev-parse --short HEAD)"
}

# 날짜 가져오기
get_date() {
    date +%Y%m%d
}

# 개발 버전 생성 (main 브랜치용)
generate_dev_version() {
    local date=$(get_date)
    local hash=$(get_commit_hash)
    local branch=$(get_current_branch)
    
    # unstaged/uncommitted 변경사항 확인
    if ! git diff-index --quiet HEAD -- || ! git diff --quiet HEAD; then
        print_warning "커밋되지 않은 변경사항이 있습니다."
        if [ "$1" = "--force" ]; then
            print_info "강제로 dev 버전 생성"
        else
            read -p "커밋되지 않은 변경사항과 함께 진행하시겠습니까? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_warning "버전 생성을 취소했습니다."
                exit 0
            fi
        fi
    fi
    
    VERSION="dev-$date-$hash"
    print_info "개발 버전 생성: $VERSION"
    echo "$VERSION"
}

# 안정 버전 생성 (Git 태그 기반)
generate_stable_version() {
    local base_version=$1
    
    if [ -z "$base_version" ]; then
        # Semantic Versioning 자동 증가
        local latest_tag=$(get_latest_tag)
        
        if [ -z "$latest_tag" ]; then
            # 첫 번째 버전
            VERSION="v1.0.0"
            print_info "첫 번째 버전 생성: $VERSION"
        else
            # 기존 태그에서 버전 추출
            local clean_tag=$(echo "$latest_tag" | sed 's/^v//')
            local major=$(echo "$clean_tag" | cut -d. -f1)
            local minor=$(echo "$clean_tag" | cut -d. -f2)
            local patch=$(echo "$clean_tag" | cut -d. -f3)
            
            # PATH 업데이트
            if [ "$UPDATE_TYPE" = "patch" ]; then
                patch=$((patch + 1))
                VERSION="v$major.$minor.$patch"
            elif [ "$UPDATE_TYPE" = "minor" ]; then
                minor=$((minor + 1))
                patch=0
                VERSION="v$major.$minor.$patch"
            elif [ "$UPDATE_TYPE" = "major" ]; then
                major=$((major + 1))
                minor=0
                patch=0
                VERSION="v$major.$minor.$patch"
            else
                # 자동 결정 (PATCH 업데이트)
                patch=$((patch + 1))
                VERSION="v$major.$minor.$patch"
            fi
            
            print_info "현재 최신 버전: $latest_tag"
            print_info "새 버전 생성: $VERSION"
        fi
    else
        # 직접 지정된 버전
        if [[ ! "$base_version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            print_error "버전 형식이 올바르지 않습니다. 예: v1.0.0"
            exit 1
        fi
        VERSION="$base_version"
        print_info "지정된 버전 사용: $VERSION"
    fi
    
    echo "$VERSION"
}

# 버전 검증
validate_version() {
    if [ -z "$VERSION" ]; then
        print_error "버전이 설정되지 않았습니다."
        exit 1
    fi
    
    print_success "유효한 버전: $VERSION"
}

# Git 태그 생성 및 푸시
create_git_tag() {
    if [ "$SKIP_TAG" = "true" ]; then
        print_info "Git 태그 생성을 건너뜁니다."
        return
    fi
    
    print_header "Git 태그 생성 및 푸시"
    
    # 태그가 이미 존재하는지 확인
    if git tag -l | grep -q "^$VERSION$"; then
        print_warning "태그 $VERSION가 이미 존재합니다."
        read -p "기존 태그를 덮어쓰시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "태그 생성을 취소했습니다."
            return
        fi
        git tag -d "$VERSION" &>/dev/null || true
    fi
    
    # Annotated 태그 생성
    local message=${1:-"Version $VERSION"}
    git tag -a "$VERSION" -m "$message"
    
    print_success "Git 태그 생성: $VERSION"
    
    # 푸시 확인
    read -p "Git 태그를 원격 저장소에 푸시하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "$VERSION"
        print_success "Git 태그 푸시 완료: $VERSION"
    else
        print_info "로컬에만 태그가 생성되었습니다. 나중에 수동으로 푸시하세요."
        print_info "푸시 명령: git push origin $VERSION"
    fi
}

# 버전 정보 출력
show_version_info() {
    print_header "버전 정보"
    
    print_info "생성된 버전: $VERSION"
    print_info "브랜치: $(get_current_branch)"
    print_info "커밋 해시: $(get_commit_hash)"
    print_info "날짜: $(get_date)"
    
    if [ ! -z "$(get_latest_tag)" ]; then
        print_info "이전 버전: $(get_latest_tag)"
        print_info "커밋 수: $(get_commit_count)"
    fi
    
    echo ""
    print_success "버전이 성공적으로 생성되었습니다: $VERSION"
}

# 도움말 함수
show_help() {
    echo "Stock Analysis Agent - 자동 버전 생성 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0                          개발 버전 자동 생성 (main 브랜치)"
    echo "  $0 --stable [버전]          안정 버전 생성 (Git 태그 기반)"
    echo "  $0 --dev                    개발 버전 강제 생성"
    echo "  $0 --help                   이 도움말 표시"
    echo ""
    echo "안정 버전 옵션:"
    echo "  --major                     Major 버전 업데이트"
    echo "  --minor                     Minor 버전 업데이트"
    echo "  --patch                     Patch 버전 업데이트 (기본값)"
    echo "  --no-tag                    Git 태그 생성하지 않음"
    echo ""
    echo "예제:"
    echo "  $0                          # dev-20251030-abc1234"
    echo "  $0 --dev                    # 강제 개발 버전 생성"
    echo "  $0 --stable v1.2.3          # 지정 버전"
    echo "  $0 --stable --major         # v2.0.0"
    echo "  $0 --stable --minor         # v1.2.0"
    echo "  $0 --stable --patch         # v1.1.1"
    echo "  $0 --stable --no-tag        # 태그 생성하지 않음"
}

# 메인 로직
case "$1" in
    "--help")
        show_help
        exit 0
        ;;
    "--dev")
        SKIP_TAG="true"
        check_git
        VERSION=$(generate_dev_version "--force")
        validate_version
        show_version_info
        exit 0
        ;;
    "--stable")
        shift
        check_git
        
        # 옵션 처리
        UPDATE_TYPE="patch"
        BASE_VERSION=""
        SKIP_TAG="false"
        
        while [[ $# -gt 0 ]]; do
            case $1 in
                --major)
                    UPDATE_TYPE="major"
                    shift
                    ;;
                --minor)
                    UPDATE_TYPE="minor"
                    shift
                    ;;
                --patch)
                    UPDATE_TYPE="patch"
                    shift
                    ;;
                --no-tag)
                    SKIP_TAG="true"
                    shift
                    ;;
                -*)
                    print_error "알 수 없는 옵션: $1"
                    show_help
                    exit 1
                    ;;
                *)
                    if [ -z "$BASE_VERSION" ]; then
                        BASE_VERSION="$1"
                    fi
                    shift
                    ;;
            esac
        done
        
        VERSION=$(generate_stable_version "$BASE_VERSION")
        validate_version
        create_git_tag "Release version $VERSION"
        show_version_info
        exit 0
        ;;
    "")
        check_git
        branch=$(get_current_branch)
        
        if [ "$branch" = "main" ]; then
            VERSION=$(generate_dev_version)
        else
            print_warning "main 브랜치가 아닙니다. 개발 버전으로 생성됩니다."
            VERSION=$(generate_dev_version)
        fi
        
        validate_version
        show_version_info
        exit 0
        ;;
    *)
        print_error "알 수 없는 옵션: $1"
        echo "도움말을 보려면 --help 옵션을 사용하세요."
        exit 1
        ;;
esac