#!/usr/bin/env python3
"""
DataSierra Health Check - Root Level
Runs health check from the tests/ folder
"""

import os
import sys
import subprocess

def run_health_check():
    """Run the health check from the tests folder"""
    print("🏥 DataSierra Health Check Runner")
    print("=" * 35)
    
    # Get the path to the tests folder
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if not os.path.exists(tests_dir):
        print("❌ Tests folder not found!")
        return False
    
    print(f"📁 Running health check from: {tests_dir}")
    
    # Run the health check script
    health_script = os.path.join(tests_dir, 'health_check.py')
    
    if os.path.exists(health_script):
        try:
            result = subprocess.run([sys.executable, health_script], 
                                  cwd=os.path.dirname(__file__),
                                  capture_output=False)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running health check: {str(e)}")
            return False
    else:
        print("❌ Health check script not found!")
        return False

if __name__ == "__main__":
    success = run_health_check()
    sys.exit(0 if success else 1)
