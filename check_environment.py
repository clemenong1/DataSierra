#!/usr/bin/env python3
"""
Python version checker for DataSierra
Run this script to verify your Python version is compatible
"""

import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"📍 Platform: {platform.platform()}")
    
    if version.major == 3 and version.minor >= 11:
        print("✅ Python version is compatible!")
        print("🎉 You can run: python -m streamlit run app.py")
        return True
    elif version.major == 3 and version.minor >= 9:
        print("⚠️  Python version is compatible but not optimal")
        print("💡 Recommended: Use Python 3.11+ for best performance")
        print("🎉 You can run: python -m streamlit run app.py")
        return True
    else:
        print("❌ Python version is incompatible!")
        print("🔧 Required: Python 3.9+ (Recommended: Python 3.11+)")
        print("📥 Install Python 3.11 from: https://python.org/downloads/")
        return False

def check_dependencies():
    """Check if key dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    dependencies = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'matplotlib',
        'openai',
        'firebase-admin',
        'lida'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            missing.append(dep)
    
    if missing:
        print(f"\n🔧 Missing dependencies: {', '.join(missing)}")
        print("📥 Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n🎉 All dependencies are installed!")
        return True

def main():
    """Main function"""
    print("🚀 DataSierra Python Environment Checker")
    print("=" * 50)
    
    version_ok = check_python_version()
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 50)
    if version_ok and deps_ok:
        print("🎉 Everything looks good! You're ready to run DataSierra!")
        print("🚀 Start the app with: python -m streamlit run app.py")
    else:
        print("🔧 Please fix the issues above before running DataSierra")
        if not version_ok:
            print("💡 Use Python 3.11: python3.11 -m streamlit run app.py")

if __name__ == "__main__":
    main()

