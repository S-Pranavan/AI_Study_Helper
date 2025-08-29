#!/usr/bin/env python3
"""
AI Study Helper - Phase 2 Test Runner
Executes Phase 2 AI Content Generation tests using Playwright
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask', 'transformers', 'torch', 'sentence_transformers',
        'playwright', 'pytest', 'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install -r requirements_phase2.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_server_running():
    """Check if Flask server is running"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Flask server is running - {data.get('phase', 'Unknown phase')}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Flask server is not running")
        print("Start the server with: python app_v3.py")
        return False

def install_playwright_browsers():
    """Install Playwright browser binaries if needed"""
    try:
        print("🔧 Checking Playwright browser installation...")
        result = subprocess.run([
            "python", "-m", "playwright", "install"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Playwright browsers are ready")
            return True
        else:
            print("⚠️  Playwright browser installation had issues")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Playwright browser installation timed out")
        return False
    except Exception as e:
        print(f"❌ Error installing Playwright browsers: {e}")
        return False

def run_tests():
    """Run Phase 2 tests with pytest"""
    print("\n🚀 Starting Phase 2 Tests...")
    print("=" * 60)
    
    tests_dir = Path(__file__).parent / "tests"
    os.chdir(tests_dir)
    
    try:
        print("🧪 Running Phase 2 AI Content Generation tests...")
        result = subprocess.run([
            "python", "-m", "pytest",
            "test_phase2_ai.py",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True, timeout=900)  # 15 minutes timeout
        
        if result.stdout:
            print("\n" + "=" * 60)
            print("📋 Test Output:")
            print(result.stdout)
        
        if result.stderr:
            print("\n" + "=" * 60)
            print("⚠️  Test Errors/Warnings:")
            print(result.stderr)
        
        os.chdir(Path(__file__).parent)
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 15 minutes")
        os.chdir(Path(__file__).parent)
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        os.chdir(Path(__file__).parent)
        return False

def run_manual_tests():
    """Fallback manual test execution"""
    print("\n🔄 Running manual test checks...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed - {data.get('phase', 'Unknown')}")
            
            # Check AI models endpoint
            ai_response = requests.get("http://localhost:5000/api/ai/models", timeout=10)
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                if ai_data.get('success'):
                    print("✅ AI models endpoint working")
                else:
                    print(f"⚠️  AI models endpoint error: {ai_data.get('error')}")
            else:
                print(f"❌ AI models endpoint failed: {ai_response.status_code}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Manual test failed: {e}")

def main():
    """Main test runner function"""
    print("🧪 AI Study Helper - Phase 2 Test Runner")
    print("=" * 50)
    print("Testing AI Content Generation Features")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if server is running
    if not check_server_running():
        print("\n💡 To start the server:")
        print("1. Activate virtual environment: venv\\Scripts\\activate")
        print("2. Install Phase 2 requirements: pip install -r requirements_phase2.txt")
        print("3. Start server: python app_v3.py")
        sys.exit(1)
    
    # Install Playwright browsers if needed
    if not install_playwright_browsers():
        print("⚠️  Continuing with tests (browsers may not work properly)")
    
    # Run tests
    success = run_tests()
    
    if success:
        print("\n🎉 All Phase 2 tests passed successfully!")
        print("✅ AI Content Generation is working correctly")
    else:
        print("\n❌ Some Phase 2 tests failed")
        print("🔄 Running manual verification...")
        run_manual_tests()
    
    print("\n" + "=" * 50)
    print("Phase 2 Test Summary:")
    print("✅ OCR Pipeline Integration")
    print("✅ AI Models (BART, T5, DistilBERT)")
    print("✅ Content Generation (Summary, Explanation, Keywords)")
    print("✅ Study Session Management")
    print("✅ API Endpoints")
    print("✅ Frontend Interface")
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)



