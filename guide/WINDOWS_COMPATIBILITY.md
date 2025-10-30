# Windows 환경에서 Docker Hub 배포 스크립트 사용 가이드

## 현재 상황
기존 스크립트들은 Unix/Linux bash로 작성되어 Windows PowerShell에서 직접 실행할 수 없습니다.

**문제점:**
- `#!bin/bash` Shebang 사용
- Unix/Linux 명령어 (`chmod`, `curl`, `git` 등) 사용
- Bash 전용 문법 (`$()`, `[[  ]]`, 함수 정의 등)

## Windows 환경에서의 사용 방법

### 방법 1: WSL2 사용 (가장 호환성 좋음) ✅

#### WSL2 설치 및 설정
```powershell
# WSL2 활성화 (관리자 권한 필요)
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# WSL2 업데이트 기능 활성화
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 재부팅 후 Linux 커널 업데이트 패키지 다운로드
# https://aka.ms/wsl2kernel

# WSL2를 기본 버전으로 설정
wsl --set-default-version 2

# Ubuntu 배포판 설치
wsl --install -d Ubuntu-22.04
```

#### WSL2에서 스크립트 실행
```bash
# WSL2 터미널에서
cd /mnt/c/Users/YourUsername/project/stock-analysis

# 스크립트 권한 부여
chmod +x scripts/*.sh

# 스크립트 실행 (기본)
DOCKER_USERNAME=yourusername scripts/run-workflow.sh

# 단계별 실행
DOCKER_USERNAME=yourusername scripts/build-images.sh
DOCKER_USERNAME=yourusername scripts/push-images.sh
```

### 방법 2: Docker Desktop for Windows 사용 ✅

Docker Desktop이 설치되어 있다면 Windows에서 직접 Docker 명령어 실행 가능:

#### Docker 빌드 및 업로드
```powershell
# 환경 변수 설정
$env:DOCKER_USERNAME="yourusername"
$env:VERSION="latest"

# Docker 이미지 빌드
docker build -f Dockerfile.backend -t stock-analysis-backend .
docker build -f nextjs\Dockerfile -t stock-analysis-frontend .
docker build -f Dockerfile.nginx -t stock-analysis-nginx .

# Docker Hub에 태그
docker tag stock-analysis-backend "$env:DOCKER_USERNAME/stock-analysis-backend:$env:VERSION"
docker tag stock-analysis-frontend "$env:DOCKER_USERNAME/stock-analysis-frontend:$env:VERSION"
docker tag stock-analysis-nginx "$env:DOCKER_USERNAME/stock-analysis-nginx:$env:VERSION"

# Docker Hub에 업로드
docker push "$env:DOCKER_USERNAME/stock-analysis-backend:$env:VERSION"
docker push "$env:DOCKER_USERNAME/stock-analysis-frontend:$env:VERSION"
docker push "$env:DOCKER_USERNAME/stock-analysis-nginx:$env:VERSION"
```

#### Docker Compose (PowerShell)
```powershell
# Docker Hub 이미지 기반 컨테이너 실행
$env:DOCKER_USERNAME="yourusername"
$env:IMAGE_VERSION="latest"

docker-compose -f docker-compose-prod.yml up -d

# 서비스 상태 확인
docker-compose -f docker-compose-prod.yml ps

# 로그 확인
docker-compose -f docker-compose-prod.yml logs
```

### 방법 3: Git Bash 사용 ✅

Git for Windows와 함께 설치되는 Git Bash 사용:

#### Git Bash 설치
```powershell
# Git for Windows 다운로드 및 설치
# https://git-scm.com/download/win
```

#### Git Bash에서 실행
```bash
# Git Bash에서
cd /c/Users/YourUsername/project/stock-analysis

# 스크립트 실행
DOCKER_USERNAME=yourusername ./scripts/build-images.sh
DOCKER_USERNAME=yourusername ./scripts/push-images.sh
```

### 방법 4: Windows PowerShell 스크립트로 포팅 (향후 개선)

현재 bash 스크립트를 PowerShell로 변환하는 방안입니다.

#### 단기적 해결책: Docker 명령어 직접 실행

Docker Desktop이 설치된 Windows 환경에서 Docker 명령어로 직접 작업:

```powershell
# 1. Docker Hub 로그인 확인
docker login

# 2. 이미지 빌드
docker build -f Dockerfile.backend -t stock-analysis-backend .
docker build -f nextjs\Dockerfile -t stock-analysis-frontend .

# 3. Docker Hub에 업로드
docker tag stock-analysis-backend yourusername/stock-analysis-backend:latest
docker tag stock-analysis-frontend yourusername/stock-analysis-frontend:latest
docker push yourusername/stock-analysis-backend:latest
docker push yourusername/stock-analysis-frontend:latest

# 4. 원격 서버에서 Docker Hub 이미지 다운로드 및 실행
# (원격 서버에서 실행)
# docker pull yourusername/stock-analysis-backend:latest
# docker-compose -f docker-compose-prod.yml up -d
```

## 🎯 권장 설정 (Windows)

### 1. 필수 설치 항목
- **Docker Desktop for Windows**
- **Git for Windows** (Git Bash 포함)
- **WSL2** (선택사항, 최고의 호환성)

### 2. 개발 워크플로우 (Windows + Docker Desktop)
```powershell
# PowerShell에서
$env:DOCKER_USERNAME="yourusername"

# 이미지 빌드 및 업로드
docker build -f Dockerfile.backend -t stock-analysis-backend .
docker build -f nextjs\Dockerfile -t stock-analysis-frontend .
docker build -f Dockerfile.nginx -t stock-analysis-nginx .

docker tag stock-analysis-backend $env:DOCKER_USERNAME/stock-analysis-backend:latest
docker tag stock-analysis-frontend $env:DOCKER_USERNAME/stock-analysis-frontend:latest
docker tag stock-analysis-nginx $env:DOCKER_USERNAME/stock-analysis-nginx:latest

docker push $env:DOCKER_USERNAME/stock-analysis-backend:latest
docker push $env:DOCKER_USERNAME/stock-analysis-frontend:latest
docker push $env:DOCKER_USERNAME/stock-analysis-nginx:latest
```

### 3. 원격 서버 배포 (Ubuntu 서버)
```bash
# SSH로 원격 서버에 접속
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

## 🚀 빠른 시작 (Windows)

### 즉시 사용 가능한 방법
1. **Docker Desktop 설치**: https://www.docker.com/products/docker-desktop
2. **PowerShell에서 Docker 로그인**: `docker login`
3. **이미지 빌드 및 업로드**: 위의 PowerShell 스크립트 사용
4. **원격 서버에서 배포**: SSH로 접속하여 `docker pull` 및 `docker compose up`

### Bash 스크립트 사용 (WSL2/Git Bash)
1. **WSL2 설치** 또는 **Git Bash 설치**
2. **Linux 환경에서 스크립트 실행**: `DOCKER_USERNAME=yourusername scripts/run-workflow.sh`

## 📋 Windows 특화 팁

### Docker Desktop 설정
```powershell
# Docker Desktop이 WSL2 백엔드 사용하도록 설정
# Docker Desktop Settings > General > Use WSL 2 based engine 체크
```

### PowerShell 환경 변수 설정
```powershell
# 영구 설정
[System.Environment]::SetEnvironmentVariable("DOCKER_USERNAME", "yourusername", "User")

# 세션별 설정
$env:DOCKER_USERNAME = "yourusername"
```

### Git Bash에서 경로 주의사항
```bash
# Windows 경로 접근 (Git Bash)
cd /c/Users/YourUsername/project/stock-analysis

# 스크립트 실행 권한 부여
chmod +x scripts/*.sh
```

## 🔧 향후 개선사항

1. **PowerShell 스크립트 포팅**: bash 스크립트를 PowerShell로 변환
2. **Docker Compose 크로스플랫폼**: 일관된 Docker Compose 파일 사용
3. **Windows-specific CI/CD**: GitHub Actions에서 Windows runner 지원
4. **일괄 처리 스크립트**: .bat 파일로 Windows 배치 명령 생성

## ❓ 문제 해결

### "bash: No such file or directory" 오류
```powershell
# WSL2 또는 Git Bash 사용
wsl # 또는 git bash 실행
```

### "Permission denied" 오류
```bash
# 스크립트 권한 부여
chmod +x scripts/*.sh
```

### Docker 명령어 인식 안됨
```powershell
# Docker Desktop 실행 상태 확인
docker --version

# PowerShell 재시작 또는 PATH 설정 확인
$env:PATH
```

## 💡 결론

**Windows 환경에서 가장 효과적인 접근법:**
1. **Docker Desktop for Windows** 설치
2. **PowerShell에서 Docker 명령어 직접 사용** (즉시 사용 가능)
3. **WSL2 설치** (향후 bash 스크립트 완전 호환)
4. **Git Bash** (간단한 bash 스크립트 실행)

현재 시점에서 **Docker Desktop + PowerShell 조합**이 가장 실용적입니다.