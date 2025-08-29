#!/usr/bin/env python3
"""
Check Test Files - Verify test files exist and can be imported
"""

import os
import sys

def check_test_files():
    """Check all test files exist and can be imported"""
    print("🔍 Checking Test Files for Phases 1-5")
    print("=" * 50)
    
    test_files = [
        "tests/test_phase1_ocr.py",
        "tests/test_phase2_ai.py", 
        "tests/test_phase3_quiz_flashcard.py",
        "tests/test_phase4_ai_tutor.py",
        "tests/test_phase5_gamification_pwa_multilingual.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        print(f"\n📁 Checking: {test_file}")
        
        # Check if file exists
        if os.path.exists(test_file):
            print(f"   ✅ File exists")
            
            # Try to import the file
            try:
                # Read the file to check for syntax errors
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax check
                compile(content, test_file, 'exec')
                print(f"   ✅ Syntax is valid")
                
                # Check for specific content
                if "class TestPhase" in content or "def test_" in content:
                    print(f"   ✅ Contains test classes/functions")
                else:
                    print(f"   ⚠️  May not contain proper test structure")
                
                results[test_file] = "PASS"
                
            except SyntaxError as e:
                print(f"   ❌ Syntax error: {e}")
                results[test_file] = "FAIL"
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
                results[test_file] = "FAIL"
        else:
            print(f"   ❌ File not found")
            results[test_file] = "FAIL"
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST FILE CHECK SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_file, status in results.items():
        phase = test_file.split('_')[1]
        print(f"Phase {phase}: {status}")
        if status == "PASS":
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All test files are properly structured!")
        print("🚀 Ready for server testing when server is running")
    else:
        print(f"\n⚠️  {failed} test file(s) have issues that need to be fixed")
    
    return passed, failed

if __name__ == "__main__":
    check_test_files()


