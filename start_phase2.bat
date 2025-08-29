@echo off
echo ========================================
echo    AI Study Helper - Phase 2 Startup
echo    AI Content Generation
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

REM Install Phase 2 requirements
echo.
echo Installing Phase 2 requirements...
echo This may take several minutes for AI models...
pip install -r requirements_phase2.txt

REM Check if AI models are available
echo.
echo Checking AI models availability...
python -c "import transformers; print('Transformers:', transformers.__version__)" 2>nul
if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Transformers library not found!
    echo Please ensure requirements_phase2.txt is installed correctly
    echo.
    pause
    exit /b 1
)

REM Check if PyTorch is available
python -c "import torch; print('PyTorch:', torch.__version__)" 2>nul
if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: PyTorch not found!
    echo Please ensure requirements_phase2.txt is installed correctly
    echo.
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "tests" mkdir tests
if not exist "model_cache" mkdir model_cache

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

echo.
echo ========================================
echo    Phase 2 Setup Complete!
echo ========================================
echo.
echo Features Available:
echo ✅ OCR Pipeline (Phase 1)
echo ✅ AI Content Generation (Phase 2)
echo ✅ BART Summarization Model
echo ✅ T5 Explanation Model
echo ✅ DistilBERT Keyword Extraction
echo ✅ Study Session Management
echo ✅ Enhanced Frontend Interface
echo.
echo Starting AI Study Helper Phase 2...
echo.
echo 🌐 Open your browser and go to: http://localhost:5000
echo ⏹️  Press Ctrl+C to stop the application
echo.
echo ========================================

REM Start the Phase 2 application
python app_v3.py

pause




