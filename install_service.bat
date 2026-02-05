@echo off
setlocal

REM 使用英文服务名以避免编码问题
set "SERVICE_NAME=DingRobot"
set "PYTHON_PATH=%~dp0.venv\Scripts\python.exe"
set "MAIN_SCRIPT=%~dp0main.py"
set "APP_DIR=%~dp0"

echo [INFO] Installing Windows Service: %SERVICE_NAME%

REM Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges.
    echo [INFO] Please right-click and select "Run as administrator".
    pause
    exit /b 1
)

REM Check if NSSM is available
where nssm >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%~dp0nssm.exe" (
        echo [INFO] Found nssm.exe in current directory.
    ) else (
        echo [ERROR] nssm.exe not found.
        echo [INFO] Please download NSSM from https://nssm.cc/download
        echo [INFO] and place nssm.exe in this folder or your system PATH.
        pause
        exit /b 1
    )
)

REM Check if virtual environment exists
if not exist "%PYTHON_PATH%" (
    echo [ERROR] Virtual environment not found at %PYTHON_PATH%
    echo [INFO] Please run install.bat first.
    pause
    exit /b 1
)

REM Install Service
echo [INFO] Creating service...
nssm install %SERVICE_NAME% "%PYTHON_PATH%" "%MAIN_SCRIPT%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create service.
    pause
    exit /b 1
)

REM Configure Service
echo [INFO] Configuring service parameters...
nssm set %SERVICE_NAME% AppDirectory "%APP_DIR%"
nssm set %SERVICE_NAME% Description "DingTalk Blood Pressure Assistant Robot"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppStdout "%APP_DIR%service.log"
nssm set %SERVICE_NAME% AppStderr "%APP_DIR%service_error.log"
nssm set %SERVICE_NAME% AppRotateFiles 1
nssm set %SERVICE_NAME% AppRotateOnline 1
nssm set %SERVICE_NAME% AppRotateSeconds 86400
nssm set %SERVICE_NAME% AppRotateBytes 10485760

REM Start Service
echo [INFO] Starting service...
nssm start %SERVICE_NAME%
if %errorlevel% neq 0 (
    echo [WARN] Failed to start service immediately.
    echo [INFO] You can try starting it manually: nssm start %SERVICE_NAME%
) else (
    echo [SUCCESS] Service installed and started successfully!
)

pause
