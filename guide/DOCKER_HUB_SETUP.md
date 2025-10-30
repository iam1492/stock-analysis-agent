# Docker Hub 레포지토리 설정 가이드

## 준비물
- Docker Hub 계정 (이미 보유)
- Docker CLI 로그인 완료

## Docker Hub 레포지토리 생성

### 1. 백엔드 이미지 레포지토리 생성
- Repository Name: `stock-analysis-backend`
- Description: "Stock Analysis Backend - Python FastAPI"
- Visibility: Private (권장)
- Docker Hub에서 수동 생성 필요

### 2. 프론트엔드 이미지 레포지토리 생성
- Repository Name: `stock-analysis-frontend`
- Description: "Stock Analysis Frontend - Next.js"
- Visibility: Private (권장)
- Docker Hub에서 수동 생성 필요

### 3. Nginx 이미지 레포지토리 생성
- Repository Name: `stock-analysis-nginx`
- Description: "Stock Analysis Nginx - Custom Configuration"
- Visibility: Private (권장)
- Docker Hub에서 수동 생성 필요

## Docker 이미지 태깅 전략

### 버전 체계
- `latest`: 최신 개발 버전
- `v1.0.0`: 안정 버전 (Git 태그 기반)
- `v1.1.0`: 기능 업데이트
- `v1.1.1`: 버그 수정

### 이미지 태깅 예시
```bash
# 개발용 latest 태그
docker tag stock-analysis-backend:latest your-dockerhub-username/stock-analysis-backend:latest

# 버전별 태그
docker tag stock-analysis-backend:latest your-dockerhub-username/stock-analysis-backend:v1.0.0
```

## Docker Hub 로그인 확인

```bash
# 현재 로그인 상태 확인
docker login

# 로그아웃 (필요시)
docker logout
```

## 레포지토리별 Docker 태그 포맷

### 백엔드 이미지
```
your-dockerhub-username/stock-analysis-backend:{version}
```

### 프론트엔드 이미지  
```
your-dockerhub-username/stock-analysis-frontend:{version}
```

### Nginx 이미지
```
your-dockerhub-username/stock-analysis-nginx:{version}
```

**참고**: `your-dockerhub-username`을 실제 Docker Hub 사용자명으로 교체해야 합니다.