@echo off
REM Restart Backend Server Script (Windows Batch)
REM This script stops any running backend processes and restarts the server

echo ========================================
echo    RESTARTING BACKEND SERVER
echo ========================================
echo.

echo Stopping existing backend processes...
REM Find and kill processes using port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process ID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo Starting backend server...
echo.

cd backend
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

cd ..

echo.
echo Backend server starting in new window...
echo Server will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo ========================================
echo    BACKEND RESTART COMPLETE
echo ========================================
echo.

pause
