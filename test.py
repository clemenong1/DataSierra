#!/usr/bin/env python3
"""
DataSierra Test Runner - Root Level
Runs tests from the tests/ folder
"""

import os
import sys
import subprocess

def run_tests():
    """Run the integration tests from the tests folder"""
    print("🧪 DataSierra Test Runner")
    print("=" * 30)
    
    # Get the path to the tests folder
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if not os.path.exists(tests_dir):
        print("❌ Tests folder not found!")
        return False
    
    print(f"📁 Running tests from: {tests_dir}")
    
    # Run the main test runner
    test_script = os.path.join(tests_dir, 'run_tests.py')
    
    if os.path.exists(test_script):
        try:
            result = subprocess.run([sys.executable, test_script], 
                                  cwd=os.path.dirname(__file__),
                                  capture_output=False)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running tests: {str(e)}")
            return False
    else:
        print("❌ Test runner script not found!")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
