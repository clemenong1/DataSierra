#!/bin/bash

# AI Data Analysis Assistant Launch Script

echo "🚀 Starting AI Data Analysis Assistant..."
echo "📊 Installing dependencies..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "�� Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "✅ Dependencies installed!"
echo "🌐 Starting Streamlit application..."
echo "📱 Open your browser to: http://localhost:8501"
echo ""

# Run the application
streamlit run app.py --server.port 8501 --server.address localhost
