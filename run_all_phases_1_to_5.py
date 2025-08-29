#!/usr/bin/env python3
"""
Comprehensive Test Runner for Phases 1-5
Runs all tests to check implementation completeness
"""

import subprocess
import sys
import os
import time

def run_phase_tests(phase_number, test_file):
    """Run tests for a specific phase"""
    print(f"\nTesting Phase {phase_number}...")
    print("=" * 50)
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    try:
        # Run the test
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=120)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        # Check return code
        if result.returncode == 0:
            print(f"Phase {phase_number} tests completed successfully!")
            return True
        else:
            print(f"Phase {phase_number} tests failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Phase {phase_number} tests timed out")
        return False
    except Exception as e:
        print(f"Error running Phase {phase_number} tests: {e}")
        return False

def check_server_status():
    """Check if the Flask server is running"""
    print("Checking server status...")
    
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("Server is running on http://localhost:5000")
            return True
        else:
            print(f"Server responded with status code: {response.status_code}")
            return False
    except ImportError:
        print("Requests module not available, skipping server check")
        return False
    except Exception as e:
        print(f"Server is not running: {e}")
        return False

def start_server():
    """Start the Flask server"""
    print("Starting Flask server...")
    
    try:
        # Try to start the server in the background
        process = subprocess.Popen([
            sys.executable, "app_v6.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("Server started successfully")
            return True
        else:
            print("Server failed to start")
            return False
            
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def main():
    """Run all Phase 1-5 tests"""
    print("AI Study Helper - Comprehensive Phase Testing (1-5)")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists("app_v6.py"):
        print("app_v6.py not found. Please run this script from the aiStudyHelper directory.")
        return False
    
    # Check server status
    server_running = check_server_status()
    
    if not server_running:
        print("\nAttempting to start server...")
        if not start_server():
            print("Failed to start server. Please start it manually and try again.")
            return False
    
    # Wait a bit more for server to fully start
    time.sleep(3)
    
    # Test all phases
    phases = [
        (1, "tests/test_phase1_ocr.py"),
        (2, "tests/test_phase2_ai.py"),
        (3, "tests/test_phase3_quiz_flashcard.py"),
        (4, "tests/test_phase4_ai_tutor.py"),
        (5, "tests/test_phase5_gamification_pwa_multilingual.py")
    ]
    
    results = {}
    
    for phase_num, test_file in phases:
        success = run_phase_tests(phase_num, test_file)
        results[phase_num] = success
        
        # Brief pause between phases
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print("PHASE TESTING SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for phase_num, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"Phase {phase_num}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("ALL PHASES 1-5 ARE COMPLETELY IMPLEMENTED!")
        print("Ready for Phase 6: Testing & Deployment")
    else:
        print("Some phases have issues that need to be addressed")
        print("Check the test output above for specific problems")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
