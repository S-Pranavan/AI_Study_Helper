@echo off
echo ========================================
echo    AI Study Helper - Phase 1 Startup
echo    OCR Foundation Implementation
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

REM Install Phase 1 requirements
echo Installing Phase 1 requirements...
pip install -r requirements_phase1.txt

REM Check if Tesseract is available
echo.
echo Checking Tesseract OCR installation...
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())" 2>nul
if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Tesseract OCR not found!
    echo Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
    echo After installation, ensure it's added to your PATH
    echo.
    pause
    exit /b 1
)

REM Create necessary directories
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "tests" mkdir tests

REM Start the Phase 1 application
echo.
echo Starting AI Study Helper - Phase 1...
echo Open your browser and go to: http://localhost:5000
echo.
echo Available endpoints:
echo - Homepage: http://localhost:5000
echo - Health Check: http://localhost:5000/api/health
echo - OCR Info: http://localhost:5000/api/ocr/info
echo - OCR Results: http://localhost:5000/api/ocr/results
echo.
echo Press Ctrl+C to stop the application
echo.

python app_v2.py

pause
