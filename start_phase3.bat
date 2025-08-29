@echo off
echo ========================================
echo AI Study Helper - Phase 3 Startup
echo Quiz & Flashcard System
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

REM Install Phase 3 requirements
echo Installing Phase 3 requirements...
pip install -r requirements_phase3.txt
if errorlevel 1 (
    echo Warning: Some requirements may not have installed correctly
    echo Continuing with startup...
)

REM Check if app_v4.py exists
if not exist "app_v4.py" (
    echo Error: app_v4.py not found!
    echo Please ensure Phase 3 implementation is complete.
    pause
    exit /b 1
)

REM Check if templates/index_v4.html exists
if not exist "templates\index_v4.html" (
    echo Error: templates\index_v4.html not found!
    echo Please ensure Phase 4 frontend template is complete.
    pause
    exit /b 1
)

REM Check if quiz_flashcard_generator.py exists
if not exist "quiz_flashcard_generator.py" (
    echo Error: quiz_flashcard_generator.py not found!
    echo Please ensure Phase 3 quiz generator is complete.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting AI Study Helper Phase 4...
echo Features: OCR + AI + Quiz + Flashcards
echo ========================================
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app_v4.py

REM If we get here, the server stopped
echo.
echo Server stopped.
pause
