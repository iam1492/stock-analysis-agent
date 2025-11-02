@echo off
:: Development Container Manager
:: Stock Analysis Agent - Windows CMD Version
:: Manages development containers using Docker Hub images (start, stop, restart, status, logs)

echo ========================================
echo Stock Analysis Agent - Development Container Manager
echo ========================================
echo.

:: Check if docker-compose-dev.yml exists
if not exist "docker-compose-dev.yml" (
    echo ERROR: docker-compose-dev.yml not found in current directory
    echo Please run this script from the project root directory
    exit /b 1
)

:: Check parameters
if "%1"=="" (
    echo Usage: dev_container_manager.bat ^<DOCKER_USERNAME^> ^<VERSION^> ^<command^>
    echo.
    echo Commands:
    echo   start    - Start development containers
    echo   stop     - Stop development containers
    echo   restart  - Restart development containers
    echo   status   - Show container status
    echo   logs     - Show container logs
    echo   clean    - Stop and remove containers and volumes
    echo.
    echo Examples:
    echo   dev_container_manager.bat myuser latest start
    echo   dev_container_manager.bat myuser v1.0.0 logs
    exit /b 1
)

if "%2"=="" (
    echo ERROR: VERSION parameter is required
    echo Usage: dev_container_manager.bat ^<DOCKER_USERNAME^> ^<VERSION^> ^<command^>
    exit /b 1
)

if "%3"=="" (
    echo ERROR: COMMAND parameter is required
    echo Usage: dev_container_manager.bat ^<DOCKER_USERNAME^> ^<VERSION^> ^<command^>
    exit /b 1
)

:: Set environment variables for docker-compose
set DOCKER_USERNAME=%1
set IMAGE_VERSION=%2
set COMMAND=%3

:: Docker check
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed.
    exit /b 1
)

:: Docker service check
echo Checking Docker service...
docker info >nul 2>&1
if errorlevel 1 (
    echo Cannot connect to Docker service.
    exit /b 1
)
echo Docker service OK
echo.

goto :%COMMAND%

:start
echo Starting development containers...
echo Using Docker Hub images: %DOCKER_USERNAME%/stock-analysis-*: %IMAGE_VERSION%
docker-compose -f docker-compose-dev.yml up -d
if errorlevel 1 (
    echo Failed to start containers
    exit /b 1
)
echo.
echo Containers started successfully!
echo Access the application at: http://localhost
echo.
goto :status

:stop
echo Stopping development containers...
docker-compose -f docker-compose-dev.yml down
if errorlevel 1 (
    echo Failed to stop containers
    exit /b 1
)
echo Containers stopped successfully!
goto :end

:restart
echo Restarting development containers...
docker-compose -f docker-compose-dev.yml restart
if errorlevel 1 (
    echo Failed to restart containers
    exit /b 1
)
echo Containers restarted successfully!
goto :end

:status
echo.
echo ========================================
echo Container Status
echo ========================================
docker-compose -f docker-compose-dev.yml ps
echo.
echo ========================================
echo Container Health
echo ========================================
docker-compose -f docker-compose-dev.yml exec -T nginx curl -f http://localhost/health 2>nul && echo nginx: healthy || echo nginx: unhealthy
docker-compose -f docker-compose-dev.yml exec -T stock-analysis-frontend python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('localhost', 3000)); s.close()" 2>nul && echo frontend: healthy || echo frontend: unhealthy
docker-compose -f docker-compose-dev.yml exec -T stock-analysis-backend python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('localhost', 8000)); s.close()" 2>nul && echo backend: healthy || echo backend: unhealthy
goto :end

:logs
if "%2"=="" (
    echo Showing logs for all containers...
    docker-compose -f docker-compose-dev.yml logs -f --tail=100
) else (
    echo Showing logs for %2...
    docker-compose -f docker-compose-dev.yml logs -f --tail=100 %2
)
goto :end

:clean
echo WARNING: This will stop containers and remove all data volumes!
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    exit /b 0
)
echo.
echo Cleaning development containers and volumes...
docker-compose -f docker-compose-dev.yml down -v --remove-orphans
if errorlevel 1 (
    echo Failed to clean containers
    exit /b 1
)
echo.
echo Containers and volumes cleaned successfully!
echo Note: Database data has been removed. You may need to restore from backup.
goto :end

:unknown
echo ERROR: Unknown command '%COMMAND%'
echo.
echo Valid commands: start, stop, restart, status, logs, clean
exit /b 1

:end
echo.
echo ========================================
echo Operation Complete!
echo ========================================
echo Batch file execution completed.