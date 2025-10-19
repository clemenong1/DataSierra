#!/usr/bin/env python3
"""
Simple Test Runner for DataSierra Integration Tests
Suppresses Streamlit warnings and runs tests cleanly
"""

import os
import sys
import warnings

# Suppress Streamlit warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*Session state does not function.*")

# Add the project root to the Python path (go up one level from tests folder)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Run the integration tests"""
    print("🧪 DataSierra Integration Test Runner")
    print("=" * 50)
    
    try:
        # Import and run the quick tests
        from tests.quick_integration_tests import run_quick_tests
        
        success = run_quick_tests()
        
        if success:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("Your DataSierra application is working correctly.")
            print("\n✅ Features verified:")
            print("   • Authentication system")
            print("   • File upload and processing")
            print("   • AI query functionality")
            print("   • Visualization generation")
            print("   • History management")
            print("   • Feedback system")
            return True
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("Please check the output above for details.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test runner error: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
