@echo off
REM Health Chatbot Local Development Setup (Windows)

echo 🛠️  Starting Health Chatbot in Development Mode...

REM Check if virtual environment exists
if not exist .venv (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file with your configuration
)

REM Start the backend server
echo 🚀 Starting Health Chatbot Backend...
echo 🌐 Backend will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo ❤️  Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
