#!/usr/bin/env python3
"""
Phase 1 Test Runner for AI Study Helper
Executes Playwright tests for OCR Foundation
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'playwright',
        'pytest',
        'pillow',
        'opencv-python',
        'pytesseract'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_flask_server():
    """Check if Flask server is running."""
    print("\n🔍 Checking Flask server status...")
    
    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running")
            return True
        else:
            print("❌ Flask server responded with error")
            return False
    except:
        print("❌ Flask server is not running")
        print("Please start the server with: python app_v2.py")
        return False

def install_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    print("\n🔍 Checking Playwright browsers...")
    
    try:
        result = subprocess.run(
            ["playwright", "install", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "No browsers to install" in result.stdout:
            print("✅ Playwright browsers are already installed")
            return True
        else:
            print("📥 Installing Playwright browsers...")
            subprocess.run(["playwright", "install"], check=True, timeout=300)
            print("✅ Playwright browsers installed successfully")
            return True
            
    except subprocess.TimeoutExpired:
        print("❌ Browser installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Browser installation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Playwright not found. Please install with: pip install playwright")
        return False

def run_tests():
    """Run the Phase 1 tests."""
    print("\n🚀 Starting Phase 1 Tests...")
    print("=" * 60)
    
    # Change to tests directory
    tests_dir = Path(__file__).parent / "tests"
    os.chdir(tests_dir)
    
    try:
        # Run tests with pytest
        print("🧪 Running tests with pytest...")
        result = subprocess.run([
            "python", "-m", "pytest", 
            "test_phase1_ocr.py", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True, timeout=600)
        
        # Print test output
        if result.stdout:
            print("\n" + "=" * 60)
            print("📋 Test Output:")
            print(result.stdout)
        
        if result.stderr:
            print("\n" + "=" * 60)
            print("⚠️  Test Errors/Warnings:")
            print(result.stderr)
        
        # Return to original directory
        os.chdir(Path(__file__).parent)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 10 minutes")
        os.chdir(Path(__file__).parent)
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        os.chdir(Path(__file__).parent)
        return False

def run_manual_tests():
    """Run tests manually if pytest fails."""
    print("\n🔄 Attempting manual test execution...")
    
    try:
        # Import and run manual tests
        sys.path.append(str(Path(__file__).parent))
        from tests.test_phase1_ocr import run_phase1_tests
        
        print("🧪 Running manual test suite...")
        passed, failed = run_phase1_tests()
        
        return failed == 0
        
    except Exception as e:
        print(f"❌ Manual test execution failed: {e}")
        return False

def main():
    """Main test runner function."""
    print("🎯 AI Study Helper - Phase 1 Test Runner")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing packages.")
        return 1
    
    # Check Flask server
    if not check_flask_server():
        print("\n❌ Flask server check failed. Please start the server.")
        return 1
    
    # Install Playwright browsers
    if not install_playwright_browsers():
        print("\n❌ Playwright browser installation failed.")
        return 1
    
    # Run tests with pytest first
    print("\n" + "=" * 60)
    print("🧪 PHASE 1 TEST EXECUTION")
    print("=" * 60)
    
    tests_passed = run_tests()
    
    if not tests_passed:
        print("\n⚠️  Pytest execution failed, trying manual tests...")
        tests_passed = run_manual_tests()
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    if tests_passed:
        print("🎉 SUCCESS: All Phase 1 tests passed!")
        print("✅ OCR Foundation is working correctly")
        print("🚀 Ready to proceed to Phase 2: AI Content Generation")
        return 0
    else:
        print("❌ FAILURE: Some Phase 1 tests failed")
        print("⚠️  Please review and fix issues before proceeding")
        print("🔧 Check the test output above for specific failures")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


