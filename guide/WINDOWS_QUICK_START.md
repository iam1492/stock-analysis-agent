# Windows 환경 사용 가이드 - 간단한 시작

## 🚀 즉시 사용 가능 (Windows + Docker Desktop)

### 1단계: Docker Hub 로그인
```powershell
docker login
```

### 2단계: PowerShell 스크립트 실행
```powershell
# 프로젝트 디렉토리로 이동
cd C:\path\to\your\stock-analysis

# 전체 빌드 및 업로드
.\scripts\build-and-push.ps1 -DockerUsername yourusername

# 또는 특정 버전으로
.\scripts\build-and-push.ps1 -DockerUsername yourusername -Version v1.0.0
```

### 3단계: 원격 서버 배포
```bash
# SSH로 원격 서버 접속
ssh root@158.247.216.21

# 원격에서 배포
export DOCKER_USERNAME="yourusername"
export IMAGE_VERSION="latest"

# 기존 컨테이너 중지
docker compose -f docker-compose-prod.yml down

# Docker Hub에서 이미지 다운로드
docker pull $DOCKER_USERNAME/stock-analysis-backend:$IMAGE_VERSION
docker pull $DOCKER_USERNAME/stock-analysis-frontend:$IMAGE_VERSION
docker pull $DOCKER_USERNAME/stock-analysis-nginx:$IMAGE_VERSION

# 컨테이너 시작
docker compose -f docker-compose-prod.yml up -d

# 상태 확인
docker compose -f docker-compose-prod.yml ps
```

## 📁 현재 제공된 파일들

### Windows 특화 파일
- **`WINDOWS_COMPATIBILITY.md`** - Windows 호환성 가이드
- **`scripts\build-and-push.ps1`** - PowerShell 이미지 빌드/업로드 스크립트

### Bash 스크립트 (WSL2/Git Bash에서 사용)
- **`scripts\build-images.sh`** - 이미지 빌드 스크립트
- **`scripts\push-images.sh`** - Docker Hub 업로드 스크립트  
- **`scripts\deploy-remote.sh`** - 원격 서버 배포 스크립트
- **`scripts\generate-version.sh`** - 자동 버전 생성 스크립트
- **`scripts\run-workflow.sh`** - 전체 워크플로우 통합 스크립트

### Docker 설정 파일
- **`docker-compose-prod.yml`** - Docker Hub 이미지 기반 프로덕션 설정
- **`docker-compose.yml`** - 로컬 개발용 설정 (기존)

### 문서화
- **`DOCKER_HUB_SETUP.md`** - Docker Hub 설정 가이드
- **`VERSION_MANAGEMENT.md`** - 버전 관리 전략
- **`DEPLOYMENT_GUIDE.md`** - 완전한 배포 가이드

## 💡 Windows 사용 권장 순서

### 권장 방법 1: PowerShell + Docker Desktop
```powershell
.\scripts\build-and-push.ps1 -DockerUsername yourusername
```

### 권장 방법 2: WSL2에서 Bash 스크립트 사용
```bash
DOCKER_USERNAME=yourusername ./scripts/run-workflow.sh
```

### 권장 방법 3: Git Bash에서 Bash 스크립트 사용
```bash
./scripts/build-images.sh
./scripts/push-images.sh
```

## 🎯 핵심 기능 비교

| 기능 | PowerShell 스크립트 | Bash 스크립트 |
|------|---------------------|---------------|
| Docker 이미지 빌드 | ✅ | ✅ |
| Docker Hub 업로드 | ✅ | ✅ |
| 버전 관리 | ❌ | ✅ |
| 로깅/ 모니터링 | ❌ | ✅ |
| 자동화 워크플로우 | ❌ | ✅ |

**결론**: PowerShell 스크립트로 기본 기능(이미지 빌드/업로드) 사용 가능, Bash 스크립트로 고급 기능(버전 관리, 전체 워크플로우) 사용 가능