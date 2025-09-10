#!/bin/bash

# DataSierra - AI-Powered Data Analysis Platform Launch Script

# Check if Python 3.11 virtual environment exists
if [ ! -d "venv_311" ]; then
    echo "🔧 Creating Python 3.11 virtual environment..."
    python3.11 -m venv venv_311
    echo "📦 Installing dependencies..."
    source venv_311/bin/activate
    pip install --upgrade pip
    pip install pandas==1.5.3 numpy==1.24.3 pandasai streamlit streamlit-extras
else
    echo "✅ Using existing Python 3.11 virtual environment"
fi

# Activate virtual environment
source venv_311/bin/activate

# Run the application
streamlit run app.py --server.port 8501 --server.address localhost