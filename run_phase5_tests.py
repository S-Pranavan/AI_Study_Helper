#!/usr/bin/env python3
"""
Phase 5 Test Runner
Runs the comprehensive test suite for Phase 5 features
"""

import subprocess
import sys
import os

def run_phase5_tests():
    """Run Phase 5 Playwright tests"""
    print("🚀 Running Phase 5 Tests...")
    print("=" * 50)
    
    try:
        # Check if we're in the right directory
        if not os.path.exists("tests/test_phase5_gamification_pwa_multilingual.py"):
            print("❌ Test file not found. Please run this script from the aiStudyHelper directory.")
            return False
        
        # Run the tests
        result = subprocess.run([
            sys.executable, 
            "tests/test_phase5_gamification_pwa_multilingual.py"
        ], capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        # Check return code
        if result.returncode == 0:
            print("\n✅ All Phase 5 tests completed successfully!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_phase5_tests()
    sys.exit(0 if success else 1)



