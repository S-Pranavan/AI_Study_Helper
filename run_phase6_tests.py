#!/usr/bin/env python3
"""
Phase 6 Test Runner
Runs comprehensive testing for deployment preparation
"""

import subprocess
import sys
import os

def run_phase6_tests():
    """Run Phase 6 comprehensive tests"""
    print("🚀 Running Phase 6: Comprehensive Testing & Deployment Preparation")
    print("=" * 70)
    
    try:
        # Check if we're in the right directory
        if not os.path.exists("tests/test_phase6_comprehensive.py"):
            print("❌ Test file not found. Please run this script from the aiStudyHelper directory.")
            return False
        
        # Run the comprehensive tests
        result = subprocess.run([
            sys.executable, 
            "tests/test_phase6_comprehensive.py"
        ], capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        # Check return code
        if result.returncode == 0:
            print("\n✅ All Phase 6 tests completed successfully!")
            print("🎯 Ready for deployment!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_phase6_tests()
    sys.exit(0 if success else 1)


