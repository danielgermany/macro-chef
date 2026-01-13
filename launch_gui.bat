@echo off
REM Launcher script for Macro Chef GUI (Windows)

echo  Starting Macro Chef GUI...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if database exists
if not exist "database\meal_planner.db" (
    echo   Database not found. Initializing...
    python scripts\db_setup.py
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo   Warning: .env file not found
    echo    API features may not work. Copy .env.example to .env and add your API keys.
    echo.
)

REM Launch GUI
echo  Launching Macro Chef GUI...
python gui_app.py

REM If GUI exits with error
if errorlevel 1 (
    echo.
    echo  GUI exited with an error
    echo    Check the error message above for details
    pause
    exit /b 1
)
