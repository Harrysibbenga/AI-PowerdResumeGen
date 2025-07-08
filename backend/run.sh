#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source venv/bin/activate

# Run the FastAPI app with uvicorn
uvicorn app.main:app --reload
