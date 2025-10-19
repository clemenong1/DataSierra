#!/usr/bin/env python3
"""
DataSierra Health Check
Quick verification that all core features are working
"""

import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add project root to path (go up one level from tests folder)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def health_check():
    """Quick health check of DataSierra features"""
    print("🏥 DataSierra Health Check")
    print("=" * 30)
    
    checks = []
    
    # Check Firebase
    try:
        from src.services.firebase_config import FirebaseConfig
        if FirebaseConfig.initialize():
            print("✅ Firebase: Connected")
            checks.append(True)
        else:
            print("❌ Firebase: Connection failed")
            checks.append(False)
    except Exception as e:
        print(f"❌ Firebase: Error - {str(e)}")
        checks.append(False)
    
    # Check Services
    try:
        from src.services.auth_service import AuthService
        from src.services.file_service import FileService
        from src.services.ai_service import AIService
        from src.services.visualization_service import VisualizationService
        
        print("✅ Services: All loaded")
        checks.append(True)
    except Exception as e:
        print(f"❌ Services: Error - {str(e)}")
        checks.append(False)
    
    # Check Components
    try:
        from src.ui.components.history import HistoryComponent
        from src.ui.components.lida_visualization import LidaVisualizationComponent
        
        print("✅ Components: All loaded")
        checks.append(True)
    except Exception as e:
        print(f"❌ Components: Error - {str(e)}")
        checks.append(False)
    
    # Check Visualization Service
    try:
        from src.services.lida_visualization_service import LidaVisualizationService
        lida_service = LidaVisualizationService()
        if lida_service.is_available():
            print("✅ LIDA: Available")
            checks.append(True)
        else:
            print("⚠️  LIDA: Not available (requires Python 3.9+ and OpenAI key)")
            checks.append(False)
    except Exception as e:
        print(f"❌ LIDA: Error - {str(e)}")
        checks.append(False)
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 30)
    print(f"Health Score: {passed}/{total}")
    
    if passed == total:
        print("🎉 All systems healthy!")
        return True
    elif passed >= total - 1:
        print("✅ Mostly healthy (minor issues)")
        return True
    else:
        print("⚠️  Health issues detected")
        return False

if __name__ == "__main__":
    healthy = health_check()
    sys.exit(0 if healthy else 1)
