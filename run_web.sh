#!/bin/bash
# Start the Z2 Web Dashboard

echo "🚀 Starting Z2 Web Dashboard..."

# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
python -m uvicorn src.web.main:app --host 0.0.0.0 --port 8000 --reload
