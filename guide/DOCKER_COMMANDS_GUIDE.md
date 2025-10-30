# Docker 명령어로 직접 실행 가이드

## Docker 사용자명: iam1492

PowerShell 스크립트 대신 단순 Docker 명령어로 Docker 이미지 빌드 및 업로드를 진행합니다.

## 1단계: Docker Hub 로그인 확인

```powershell
# Docker Hub 로그인 확인
docker login
```

## 2단계: Docker 이미지 빌드

```powershell
# 백엔드 이미지 빌드
docker build -f Dockerfile.backend -t stock-analysis-backend .

# 프론트엔드 이미지 빌드
docker build -f nextjs\Dockerfile -t stock-analysis-frontend .

# Nginx 이미지 빌드
docker build -f Dockerfile.nginx -t stock-analysis-nginx .
```

## 3단계: Docker Hub에 업로드

```powershell
# Docker Hub 태깅 및 업로드
docker tag stock-analysis-backend iam1492/stock-analysis-backend:latest
docker tag stock-analysis-frontend iam1492/stock-analysis-frontend:latest
docker tag stock-analysis-nginx iam1492/stock-analysis-nginx:latest

docker push iam1492/stock-analysis-backend:latest
docker push iam1492/stock-analysis-frontend:latest
docker push iam1492/stock-analysis-nginx:latest
```

## 4단계: 원격 서버 배포

원격 서버에서 다음 명령어 실행:

```bash
# SSH로 원격 서버 접속
ssh root@158.247.216.21

# Docker Hub에서 이미지 다운로드
docker pull iam1492/stock-analysis-backend:latest
docker pull iam1492/stock-analysis-frontend:latest
docker pull iam1492/stock-analysis-nginx:latest

# 환경 변수 설정
export DOCKER_USERNAME="iam1492"
export IMAGE_VERSION="latest"

# 기존 컨테이너 중지
docker-compose -f docker-compose-prod.yml down

# Docker Hub 이미지 사용해서 컨테이너 시작
export DOCKER_USERNAME=iam1492
export IMAGE_VERSION=latest
docker-compose -f docker-compose-prod.yml up -d

# 상태 확인
docker-compose -f docker-compose-prod.yml ps
```

## 출력 확인

### 성공 시 표시되는 메시지
```powershell
Successfully tagged iam1492/stock-analysis-backend:latest
Successfully pushed iam1492/stock-analysis-backend:latest
Successfully tagged iam1492/stock-analysis-frontend:latest
Successfully pushed iam1492/stock-analysis-frontend:latest
Successfully tagged iam1492/stock-analysis-nginx:latest
Successfully pushed iam1492/stock-analysis-nginx:latest
```

### 원격 서버 상태 확인
```bash
# 서비스 상태
docker-compose -f docker-compose-prod.yml ps

# 컨테이너 로그
docker-compose -f docker-compose-prod.yml logs

# 웹사이트 확인
curl http://158.247.216.21
```

## 문제 해결

### Docker Hub 업로드 실패 시
1. Docker 로그인 상태 확인
2. 레포지토리 권한 확인
3. 네트워크 연결 상태 확인

### 원격 서버 배포 실패 시
1. 기존 컨테이너 중지 확인
2. 디스크 공간 확인
3. 포트 충돌 확인

## 성공 확인

### 로컬에서 확인
```powershell
# 업로드된 이미지 확인
docker images | findstr iam1492
```

### 원격 서버에서 확인
```bash
# 서비스 상태 확인
curl http://158.247.216.21/health

# 백엔드 API 확인
curl http://158.247.216.21:8000/health
```

## 전체 명령어 요약

### 로컬에서 (PowerShell)
```powershell
docker build -f Dockerfile.backend -t stock-analysis-backend .
docker build -f nextjs\Dockerfile -t stock-analysis-frontend .
docker build -f Dockerfile.nginx -t stock-analysis-nginx .

docker tag stock-analysis-backend iam1492/stock-analysis-backend:latest
docker tag stock-analysis-frontend iam1492/stock-analysis-frontend:latest
docker tag stock-analysis-nginx iam1492/stock-analysis-nginx:latest

docker push iam1492/stock-analysis-backend:latest
docker push iam1492/stock-analysis-frontend:latest
docker push iam1492/stock-analysis-nginx:latest
```

### 원격 서버에서 (Ubuntu)
```bash
ssh root@158.247.216.21

docker pull iam1492/stock-analysis-backend:latest
docker pull iam1492/stock-analysis-frontend:latest
docker pull iam1492/stock-analysis-nginx:latest

export DOCKER_USERNAME=iam1492
export IMAGE_VERSION=latest
docker-compose -f docker-compose-prod.yml up -d

curl http://localhost
```

이 가이드대로 실행하면 Docker Hub 기반 배포가 완료됩니다!