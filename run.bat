@echo off
setlocal

echo [INFO] Starting DingTalk Robot...

if not exist ".venv" (
    echo [ERROR] Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate

REM Optional: Run migration if needed
REM python migrate_db.py

python main.py

if %errorlevel% neq 0 (
    echo [ERROR] Application exited with error code %errorlevel%.
    pause
)
