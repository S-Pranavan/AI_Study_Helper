@echo off
echo ========================================
echo    AI Study Helper - Startup Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if needed
echo Installing/updating requirements...
pip install -r requirements.txt

REM Start the application
echo.
echo Starting AI Study Helper...
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.
python run.py

pause


