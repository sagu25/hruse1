@echo off
echo ============================================
echo Recruitment Agent System - Quick Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Step 1: Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Check if .env exists
if not exist .env (
    echo Step 2: Creating .env file...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env and add your GOOGLE_API_KEY
    echo Get your key from: https://makersuite.google.com/app/apikey
    echo.
    pause
) else (
    echo Step 2: .env file already exists
)
echo.

echo Step 3: Initializing database and running example...
python main.py example
echo.

echo ============================================
echo Setup complete!
echo ============================================
echo.
echo To run again:
echo   python main.py example     - Run example workflow
echo   python main.py interactive - Interactive mode
echo.
pause
