#!/bin/bash

# ASR Testing Platform Startup Script
echo "🚀 Starting ASR Testing Platform..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Start the Flask application
echo "🌐 Starting Flask application..."
echo "📍 Platform will be available at: http://localhost:5001"
echo "🔑 Make sure you're logged in with Google OAuth"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

python3 app.py
