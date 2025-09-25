@echo off
REM Health Chatbot Startup Script for Docker (Windows)

echo 🚀 Starting Health Chatbot with Docker Compose...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file with your configuration
)

REM Build and start all services
echo 🔨 Building and starting all services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check service status
echo 🔍 Checking service status...
docker-compose ps

echo ✅ Health Chatbot is starting up!
echo.
echo 🌐 Access your services at:
echo    • Main Application: http://localhost:3001
echo    • API Documentation: http://localhost:8000/docs
echo    • Rasa API: http://localhost:5005
echo    • Grafana Dashboard: http://localhost:3000
echo    • Prometheus: http://localhost:9090
echo.
echo 📱 To stop all services: docker-compose down
echo 🔄 To restart: docker-compose restart
echo 📊 View logs: docker-compose logs -f [service_name]
pause
