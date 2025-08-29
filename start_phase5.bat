@echo off
echo ========================================
echo AI Study Helper - Phase 5 Setup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install Phase 5 requirements
echo Installing Phase 5 requirements...
pip install -r requirements_phase5.txt
if errorlevel 1 (
    echo Failed to install requirements
    pause
    exit /b 1
)

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install
if errorlevel 1 (
    echo Failed to install Playwright browsers
    pause
    exit /b 1
)

echo.
echo ========================================
echo Phase 5 Setup Complete!
echo ========================================
echo.
echo Starting AI Study Helper Phase 5...
echo.
echo Features available:
echo - OCR Image Processing
echo - AI Content Generation
echo - Quiz and Flashcard System
echo - AI Tutor and Mind Maps
echo - Gamification System (XP, Levels, Badges)
echo - PWA and Offline Support
echo - Multilingual Support
echo.
echo Server will start at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app_v6.py

pause



