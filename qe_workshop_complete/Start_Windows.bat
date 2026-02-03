@echo off
REM =============================================================================
REM Quantum ESPRESSO Workshop - Windows Startup Script
REM =============================================================================
REM This script starts the Docker container for the workshop.
REM Prerequisites: Docker Desktop must be installed and running.
REM =============================================================================

echo.
echo ============================================================
echo    Quantum ESPRESSO Workshop - Starting Environment
echo ============================================================
echo.
echo Please wait while the workshop environment starts...
echo (First run may take 5-10 minutes to download ~1GB of data)
echo.

REM Check if Docker is running
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo.
    echo Please start Docker Desktop and wait for it to fully load.
    echo Look for the whale icon in your system tray.
    echo.
    pause
    exit /b 1
)

REM Build and run the container
docker-compose up --build

pause
