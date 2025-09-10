#!/bin/bash

# DataSierra Firebase Authentication Setup Script
# This script installs the required dependencies for Firebase authentication

echo "🔐 Setting up Firebase Authentication for DataSierra..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv_311" ]; then
    echo "❌ Virtual environment not found. Please run the main setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv_311/bin/activate

# Install Firebase dependencies
echo "📥 Installing Firebase authentication dependencies..."
pip install pyrebase4>=4.7.1
pip install firebase-admin>=6.4.0
pip install python-jose>=3.3.0

# Verify installation
echo "✅ Verifying installation..."
python -c "import pyrebase; print('✅ Pyrebase4 installed successfully')"
python -c "import firebase_admin; print('✅ Firebase Admin installed successfully')"
python -c "import jose; print('✅ Python-JOSE installed successfully')"

echo ""
echo "🎉 Firebase Authentication setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure your Firebase configuration is in .streamlit/secrets.toml"
echo "2. Run the app with: streamlit run app.py"
echo "3. Test the authentication by clicking the Login button"
echo ""
echo "🔧 If you encounter any issues:"
echo "- Check that your Firebase project is properly configured"
echo "- Verify your API keys in secrets.toml"
echo "- Make sure your Firebase project has Authentication enabled"
