#!/bin/bash

# Start backend server
echo "Starting FastAPI backend..."
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 &

# Start Rasa server
echo "Starting Rasa server..."
cd rasa_bot
rasa run --enable-api --cors "*" &

echo "Local development servers are running:
- FastAPI: http://localhost:8000
- Rasa: http://localhost:5005"