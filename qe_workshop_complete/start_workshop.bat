@echo off
REM =============================================================================
REM Quantum ESPRESSO Workshop Launcher — Windows
REM =============================================================================
REM Usage: Double-click this file, or run from Command Prompt
REM =============================================================================

TITLE Quantum ESPRESSO Workshop

echo ==========================================================
echo   QUANTUM ESPRESSO WORKSHOP ENVIRONMENT
echo ==========================================================
echo.

REM Check Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running.
    echo.
    echo Please install Docker Desktop:
    echo   https://www.docker.com/products/docker-desktop/
    echo.
    echo After installing, open Docker Desktop and wait for
    echo the whale icon to stop animating, then try again.
    echo.
    pause
    exit /b 1
)

REM Check if image exists locally
docker images --format "{{.Repository}}:{{.Tag}}" | findstr /C:"indranilm/qe-workshop:latest" >nul 2>&1
if %errorlevel% neq 0 (
    echo Workshop image not found locally. Downloading...
    echo This may take 20-40 minutes on the first run.
    echo.
    docker pull indranilm/qe-workshop:latest
    echo.
)

REM Stop any existing container
docker stop qe-workshop >nul 2>&1
docker rm qe-workshop >nul 2>&1

echo Starting workshop environment...
echo.
echo ----------------------------------------------------------
echo   Open your browser and go to: http://localhost:8888
echo   Navigate to: notebooks_enhanced/
echo   To stop: press Ctrl+C or close this window
echo ----------------------------------------------------------
echo.

REM Run the container from the directory where this script lives
docker run -it --rm --name qe-workshop -p 8888:8888 -v "%~dp0":/workspace -e OMPI_ALLOW_RUN_AS_ROOT=1 -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 indranilm/qe-workshop:latest

pause
