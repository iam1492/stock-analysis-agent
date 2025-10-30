@echo off
:: Docker Hub Image Build and Push Batch Script
:: Stock Analysis Agent - Windows CMD Version (Docker Context Fix)

echo ========================================
echo Stock Analysis Agent - Docker Image Build and Upload
echo ========================================
echo.

:: Default values
if "%DOCKER_USERNAME%"=="" set DOCKER_USERNAME=iam1492
if "%VERSION%"=="" set VERSION=latest

echo Docker Hub Username: %DOCKER_USERNAME%
echo Image Version: %VERSION%
echo.

:: Docker check
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed.
    exit /b 1
)
echo Docker check completed

:: Docker service check
echo Checking Docker service...
docker info >nul 2>&1
if errorlevel 1 (
    echo Cannot connect to Docker service.
    exit /b 1
)
echo Docker service OK

:: Docker Hub login check (simplified)
echo Checking Docker Hub connection...
docker version >nul 2>&1
if errorlevel 1 (
    echo Docker Hub connection failed.
    echo Please ensure Docker service is running and connected.
    exit /b 1
)
echo Docker Hub connection OK

echo.
set /p confirm="Continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    exit /b 0
)

echo.
echo ========================================
echo Docker Image Build Started
echo ========================================

echo Building backend image...
docker build -f Dockerfile.backend -t stock-analysis-backend .
if errorlevel 1 (
    echo Backend image build failed
    exit /b 1
)
echo Backend image build completed

echo Building frontend image...
docker build -f nextjs\Dockerfile -t stock-analysis-frontend nextjs\.
if errorlevel 1 (
    echo Frontend image build failed
    exit /b 1
)
echo Frontend image build completed

echo Building nginx image...
docker build -f Dockerfile.nginx -t stock-analysis-nginx .
if errorlevel 1 (
    echo Nginx image build failed
    exit /b 1
)
echo Nginx image build completed

echo All images build completed

echo.
echo ========================================
echo Docker Hub Image Upload Started
echo ========================================

:: Image tagging
echo Tagging images...
docker tag stock-analysis-backend %DOCKER_USERNAME%/stock-analysis-backend:%VERSION%
docker tag stock-analysis-frontend %DOCKER_USERNAME%/stock-analysis-frontend:%VERSION%
docker tag stock-analysis-nginx %DOCKER_USERNAME%/stock-analysis-nginx:%VERSION%
echo Image tagging completed

:: Docker Hub upload with retry logic
echo Uploading backend image...
docker push %DOCKER_USERNAME%/stock-analysis-backend:%VERSION%
if errorlevel 1 (
    echo Backend image upload failed.
    echo Please make sure you are logged in to Docker Hub:
    echo   docker login
    echo.
    echo Or try again after logging in.
    exit /b 1
)
echo Backend image upload completed

echo Uploading frontend image...
docker push %DOCKER_USERNAME%/stock-analysis-frontend:%VERSION%
if errorlevel 1 (
    echo Frontend image upload failed.
    echo Please make sure you are logged in to Docker Hub:
    echo   docker login
    echo.
    echo Or try again after logging in.
    exit /b 1
)
echo Frontend image upload completed

echo Uploading nginx image...
docker push %DOCKER_USERNAME%/stock-analysis-nginx:%VERSION%
if errorlevel 1 (
    echo Nginx image upload failed.
    echo Please make sure you are logged in to Docker Hub:
    echo   docker login
    echo.
    echo Or try again after logging in.
    exit /b 1
)
echo Nginx image upload completed

:: Latest tag upload (when VERSION is not latest)
if not "%VERSION%"=="latest" (
    echo Uploading latest tags...
    docker tag %DOCKER_USERNAME%/stock-analysis-backend:%VERSION% %DOCKER_USERNAME%/stock-analysis-backend:latest
    docker tag %DOCKER_USERNAME%/stock-analysis-frontend:%VERSION% %DOCKER_USERNAME%/stock-analysis-frontend:latest
    docker tag %DOCKER_USERNAME%/stock-analysis-nginx:%VERSION% %DOCKER_USERNAME%/stock-analysis-nginx:latest
    
    docker push %DOCKER_USERNAME%/stock-analysis-backend:latest
    docker push %DOCKER_USERNAME%/stock-analysis-frontend:latest
    docker push %DOCKER_USERNAME%/stock-analysis-nginx:latest
    echo Latest tag upload completed
)

echo All images Docker Hub upload completed

echo.
echo ========================================
echo Operation Complete!
echo ========================================
echo Docker image build and upload completed.

echo.
echo Uploaded images:
echo   %DOCKER_USERNAME%/stock-analysis-backend:%VERSION%
echo   %DOCKER_USERNAME%/stock-analysis-frontend:%VERSION%
echo   %DOCKER_USERNAME%/stock-analysis-nginx:%VERSION%

if not "%VERSION%"=="latest" (
    echo   %DOCKER_USERNAME%/stock-analysis-backend:latest
    echo   %DOCKER_USERNAME%/stock-analysis-frontend:latest
    echo   %DOCKER_USERNAME%/stock-analysis-nginx:latest
)

echo.
echo For remote deployment:
echo   ssh root@158.247.216.21
echo   docker pull %DOCKER_USERNAME%/stock-analysis-backend:%VERSION%
echo   docker pull %DOCKER_USERNAME%/stock-analysis-frontend:%VERSION%
echo   docker pull %DOCKER_USERNAME%/stock-analysis-nginx:%VERSION%
echo   set DOCKER_USERNAME=%DOCKER_USERNAME%
echo   set VERSION=%VERSION%
echo   docker-compose -f docker-compose-prod.yml up -d
echo.
echo Batch file execution completed.