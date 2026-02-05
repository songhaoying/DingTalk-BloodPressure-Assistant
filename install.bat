@echo off
setlocal

echo [INFO] Starting DingTalk Robot Installation...

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Create virtual environment
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment already exists.
)

REM Activate venv and install dependencies
echo [INFO] Installing dependencies...
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Config setup
if not exist ".env" (
    echo [INFO] Creating .env file from .env.example...
    copy .env.example .env
    echo [WARN] Please edit .env file to configure your API keys and Database settings.
    notepad .env
) else (
    echo [INFO] .env file already exists.
)

echo.
echo [SUCCESS] Installation completed successfully!
echo.
echo To run the robot, execute: run.bat
echo.
pause
