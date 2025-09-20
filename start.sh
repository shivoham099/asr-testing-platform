#!/bin/bash

# ASR Testing Platform Startup Script

echo "Starting ASR Testing Platform..."
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -c "from app import init_db; init_db(); print('Database initialized successfully')"

# Start the application
echo "Starting Flask application on http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo "================================"

python app.py