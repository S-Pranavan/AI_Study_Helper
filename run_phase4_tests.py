#!/usr/bin/env python3
"""
Phase 4 Test Runner for AI Study Helper
Runs the AI Tutor and Mind Maps tests using Playwright
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import playwright
        print("✅ Playwright is installed")
    except ImportError:
        print("❌ Playwright not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
        print("✅ Playwright installed successfully")
    
    try:
        import pytest
        print("✅ Pytest is installed")
    except ImportError:
        print("❌ Pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
        print("✅ Pytest installed successfully")

def run_playwright_tests():
    """Run the Phase 4 Playwright tests"""
    print("\n🚀 Running Phase 4: AI Tutor & Mind Maps Tests")
    print("=" * 60)
    
    # Check if tests directory exists
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ Tests directory not found. Creating...")
        tests_dir.mkdir(exist_ok=True)
    
    # Check if test file exists
    test_file = tests_dir / "test_phase4_ai_tutor.py"
    if not test_file.exists():
        print("❌ Phase 4 test file not found!")
        return False
    
    try:
        # Run the tests using pytest
        print("🧪 Executing Phase 4 tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(test_file), 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        # Print test output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        # Check if tests passed
        if result.returncode == 0:
            print("✅ All Phase 4 tests passed!")
            return True
        else:
            print("❌ Some Phase 4 tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_manual_tests():
    """Run manual tests for Phase 4 functionality"""
    print("\n🔧 Running Manual Phase 4 Tests")
    print("=" * 60)
    
    try:
        # Import the test module
        sys.path.append("tests")
        from test_phase4_ai_tutor import run_phase4_tests
        
        # Run the manual tests
        passed, failed = run_phase4_tests()
        
        if failed == 0:
            print("✅ All manual Phase 4 tests passed!")
            return True
        else:
            print(f"⚠️  {failed} manual Phase 4 tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running manual tests: {e}")
        return False

def check_server_status():
    """Check if the Flask server is running"""
    print("\n🌐 Checking server status...")

    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running - Phase {data.get('phase', 'Unknown')}")
            print(f"   Features: {', '.join(data.get('features', []))}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except ImportError:
        print("⚠️  Requests library not available. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        return check_server_status()
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

def main():
    """Main test runner function"""
    print("🎯 AI Study Helper - Phase 4 Test Runner")
    print("=" * 60)

    # Check dependencies
    check_dependencies()

    # Check server status
    server_running = check_server_status()

    if not server_running:
        print("\n⚠️  Server is not running. Please start the Flask application first:")
        print("   python app_v5.py")
        print("\n   Or use the startup script:")
        print("   .\\start_phase4.bat")
        return False

    # Run tests
    print("\n" + "=" * 60)
    print("🧪 TESTING PHASE 4: AI TUTOR & MIND MAPS")
    print("=" * 60)
    
    # Run Playwright tests
    playwright_success = run_playwright_tests()
    
    # Run manual tests
    manual_success = run_manual_tests()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PHASE 4 TEST SUMMARY")
    print("=" * 60)
    
    if playwright_success:
        print("✅ Playwright Tests: PASSED")
    else:
        print("❌ Playwright Tests: FAILED")
    
    if manual_success:
        print("✅ Manual Tests: PASSED")
    else:
        print("❌ Manual Tests: FAILED")
    
    overall_success = playwright_success and manual_success
    
    if overall_success:
        print("\n🎉 PHASE 4 IMPLEMENTATION COMPLETE!")
        print("   AI Tutor and Mind Maps System is working correctly!")
        print("\n   Next steps:")
        print("   - Test with real conversations and content")
        print("   - Customize AI Tutor responses and knowledge base")
        print("   - Enhance mind map visualization and interactions")
        print("   - Prepare for Phase 5: Gamification & Offline Support")
    else:
        print("\n⚠️  PHASE 4 HAS ISSUES")
        print("   Please review the test failures above")
        print("   Check server logs for more details")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
