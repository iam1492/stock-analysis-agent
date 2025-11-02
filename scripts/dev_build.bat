@echo off
:: Docker Hub Image Build Script for Development
:: Stock Analysis Agent - Windows CMD Version
:: Builds images locally using development nginx configuration

echo ========================================
echo Stock Analysis Agent - Development Docker Image Build
echo ========================================
echo.

:: Check parameters
if "%1"=="" (
    echo ERROR: DOCKER_USERNAME parameter is required
    echo Usage: dev_build.bat ^<DOCKER_USERNAME^> ^<VERSION^>
    echo Example: dev_build.bat myuser v1.0.0
    exit /b 1
)

if "%2"=="" (
    echo ERROR: VERSION parameter is required
    echo Usage: dev_build.bat ^<DOCKER_USERNAME^> ^<VERSION^>
    echo Example: dev_build.bat myuser v1.0.0
    exit /b 1
)

:: Set parameters
set DOCKER_USERNAME=%1
set VERSION=%2

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

echo.
set /p confirm="Continue with build? (y/N): "
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

echo Building nginx development image...
docker build -f Dockerfile.nginx-dev -t stock-analysis-nginx .
if errorlevel 1 (
    echo Nginx development image build failed
    exit /b 1
)
echo Nginx development image build completed

echo All images build completed

echo.
echo ========================================
echo Operation Complete!
echo ========================================
echo Development images built successfully.
echo.
echo Built images:
echo   stock-analysis-backend
echo   stock-analysis-frontend
echo   stock-analysis-nginx (development version)
echo.
echo To run locally: docker-compose -f docker-compose-dev.yml up -d
echo.
echo Batch file execution completed.