#!/bin/bash

# Activate your virtual environment if you have one
# source /path/to/your/venv/bin/activate

# Start the FastAPI application with Uvicorn
uvicorn yolo.db.api:app --host 127.0.0.1 --port 8000 --reload