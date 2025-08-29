@echo off
echo.
echo ========================================
echo   AI Study Helper - Phase 4 Startup
echo ========================================
echo.
echo Starting Phase 4: AI Tutor & Mind Maps
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo.
echo Installing/updating requirements...
pip install -r requirements_phase4.txt

REM Check if requirements installation was successful
if %errorlevel% neq 0 (
    echo.
    echo Warning: Some requirements may not have installed correctly.
    echo Continuing with startup...
    echo.
)

REM Create uploads directory if it doesn't exist
if not exist "uploads" (
    echo Creating uploads directory...
    mkdir uploads
)

REM Start the Flask application
echo.
echo Starting Flask application...
echo Phase 4 features: OCR + Quiz + Flashcards + AI Tutor + Mind Maps
echo.
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app_v5.py

REM Keep the window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
