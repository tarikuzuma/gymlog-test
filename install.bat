@echo off
echo Installing Gym Logger Dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install pip if not available
python -m ensurepip --upgrade

REM Install requirements
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To run the application:
echo 1. Open command prompt in this directory
echo 2. Run: python main.py
echo 3. Open browser and go to: http://localhost:5001
echo.
pause 