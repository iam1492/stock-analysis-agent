# Docker 이미지 버전 관리 가이드

## 개요
Stock Analysis Agent의 Docker 이미지 버전 관리를 위한 가이드입니다.

## 버전 체계

### Semantic Versioning (SemVer)
형식: `MAJOR.MINOR.PATCH`
- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 새로운 기능 추가 (호환성 유지)
- **PATCH**: 버그 수정 (호환성 유지)

### 베타 및 개발 버전
- **latest**: 최신 개발 버전
- **beta**: 베타 테스트 버전
- **stable**: 안정화 버전
- **rc**: 릴리스 후보 버전

## 버전 생성 전략

### 1. Git 기반 자동 버전
Git 태그에서 버전 추출:
```bash
# 현재 커밋에서 버전 추출
git describe --tags --abbrev=0  # 가장 최근 태그
git rev-list --count HEAD       # 커밋 수
```

### 2. 개발용 버전
날짜 + 커밋 해시 기반:
```
dev-20251030-abc1234
```

### 3. 배포용 버전
Semantic Versioning 적용:
```
v1.0.0    # 첫 번째 릴리스
v1.1.0    # 기능 추가
v1.1.1    # 버그 수정
```

## Docker 이미지 태깅 전략

### 백엔드 이미지
```
stock-analysis-backend:latest      # 최신 개발 버전
stock-analysis-backend:v1.0.0      # 안정 버전
stock-analysis-backend:dev-YYYYMMDD-HASH  # 개발 버전
```

### 프론트엔드 이미지
```
stock-analysis-frontend:latest
stock-analysis-frontend:v1.0.0
stock-analysis-frontend:dev-YYYYMMDD-HASH
```

### Nginx 이미지
```
stock-analysis-nginx:latest
stock-analysis-nginx:v1.0.0
stock-analysis-nginx:dev-YYYYMMDD-HASH
```

## 배포 워크플로우

### 1. 개발 모드
```bash
# 로컬에서 개발용 이미지 빌드 및 배포
VERSION=dev-$(date +%Y%m%d)-$(git rev-parse --short HEAD)
DOCKER_USERNAME=yourusername scripts/build-images.sh
DOCKER_USERNAME=yourusername VERSION=$VERSION scripts/push-images.sh
```

### 2. 프로덕션 모드
```bash
# 안정 버전 배포
VERSION=v1.0.0
DOCKER_USERNAME=yourusername scripts/build-images.sh
DOCKER_USERNAME=yourusername VERSION=$VERSION scripts/push-images.sh

# 원격 서버 배포
DOCKER_USERNAME=yourusername IMAGE_VERSION=$VERSION scripts/deploy-remote.sh
```

## 버전 관리 명령어

### Git 태그 생성
```bash
# 새로운 버전 태그 생성
git tag v1.0.0
git push origin v1.0.0

# 또는 Annotated 태그 (추천)
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Docker 이미지 버전 확인
```bash
# 로컬 이미지 버전 확인
docker images | grep stock-analysis

# Docker Hub 이미지 버전 확인
curl "https://hub.docker.com/v2/repositories/YOUR_USERNAME/stock-analysis-backend/tags/"
```

## 롤백 전략

### 1. 빠른 롤백
```bash
# 이전 버전으로 롤백
IMAGE_VERSION=v0.9.0 DOCKER_USERNAME=yourusername scripts/deploy-remote.sh
```

### 2. 번호 기준 롤백
```bash
# 사용 가능한 버전 목록 확인
docker pull yourusername/stock-analysis-backend:v1.0.0
docker pull yourusername/stock-analysis-backend:v0.9.0
docker pull yourusername/stock-analysis-backend:v0.8.0

# 테스트 후 안정 버전 선택
IMAGE_VERSION=v0.9.0 DOCKER_USERNAME=yourusername scripts/deploy-remote.sh
```

## 브랜치별 배포 전략

### main 브랜치
- 안정 버전 (`latest`)
- 버전 태그 기반 배포
- `v1.0.0`, `v1.1.0` 등

### develop 브랜치
- 개발 버전 (`dev-YYYYMMDD-HASH`)
- 일일 빌드
- 테스트 및 검증

### feature 브랜치
- 기능별 임시 이미지
- 피어 리뷰 후 develop 브랜치로 병합

## 이미지 정리

### Docker Hub 정리
```bash
# 오래된 이미지 삭제 (예: 30일 이전)
docker images yourusername/stock-analysis-backend --format "{{.CreatedAt}}" | \
xargs -I{} bash -c 'if [ $(($(date +%s) - $(date -d "{}" +%s))) -gt 2592000 ]; then echo "{}"; fi'
```

### 로컬 정리
```bash
# 빌드 캐시 정리
docker system prune -f

# 사용하지 않는 이미지 삭제
docker image prune -f
```

## 모니터링 및 알림

### 이미지 상태 확인 스크립트
```bash
#!/bin/bash
# 이미지 상태 정기 확인
VERSION=$1
DOCKER_USERNAME=$2

IMAGES=("stock-analysis-backend" "stock-analysis-frontend" "stock-analysis-nginx")

for image in "${IMAGES[@]}"; do
    if docker pull "$DOCKER_USERNAME/$image:$VERSION" &>/dev/null; then
        echo "✅ $image:$VERSION 다운로드 가능"
    else
        echo "❌ $image:$VERSION 다운로드 실패"
    fi
done
```

## 모범 사례

1. **일관성**: 모든 이미지에 동일한 버전 태그 사용
2. **설명성**: 태그 이름이 의미 있도록 설정
3. **테스트**: 프로덕션 배포 전 개발 환경에서 테스트
4. **백업**: 중요한 버전은 별도로 보관
5. **문서화**: 버전 변경 내역 기록 유지

## 문제 해결

### 일반적인 문제

1. **이미지Pull실패**
   - Docker Hub 로그인 상태 확인
   - 레포지토리 접근 권한 확인

2. **버전 불일치**
   - 모든 이미지가 동일한 버전인지 확인
   - docker-compose-prod.yml의 이미지 버전 일치 확인

3. **배포 실패**
   - 기존 컨테이너 중지 확인
   - 포트 충돌 확인
   - 환경 변수 설정 확인