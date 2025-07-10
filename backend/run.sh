#!/bin/bash

# Exit on error
set -e

# Check for virtual environment
if [ ! -d "venv" ]; then
  echo "📁 venv not found. Creating virtual environment..."
  python3 -m venv venv
fi

echo "🔁 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

echo "📦 Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

echo "🚀 Starting FastAPI app on http://0.0.0.0:8000 ..."
python application.py
