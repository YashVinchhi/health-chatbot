@echo off
REM RASA Health Chatbot Startup Script for Windows

echo 🏥 Starting RASA Health Chatbot Integration...

REM Set environment variables
set RASA_URL=http://localhost:5005
set BACKEND_URL=http://localhost:8000

REM Function to check if a port is in use
:check_port
netstat -an | findstr ":%1 " >nul
if %errorlevel%==0 (
    exit /b 0
) else (
    exit /b 1
)

REM Check dependencies
echo 🔍 Checking dependencies...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed
    pause
    exit /b 1
)

where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ pip is not installed
    pause
    exit /b 1
)

where rasa >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ RASA is not installed. Installing...
    pip install rasa
)

echo ✅ Dependencies check completed

REM Start Backend Server
echo 🔧 Starting FastAPI Backend...
cd backend
start "Backend Server" cmd /c "pip install -r requirements.txt && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
timeout /t 5 >nul

call :check_port 8000
if %errorlevel%==0 (
    echo ✅ Backend server is running on http://localhost:8000
) else (
    echo ❌ Failed to start backend server
    pause
    exit /b 1
)

REM Change to RASA directory
cd ..\rasa_bot

REM Train RASA model
echo 📚 Training RASA model...
rasa train --force

if %errorlevel%==0 (
    echo ✅ RASA model trained successfully!
) else (
    echo ❌ Failed to train RASA model
    pause
    exit /b 1
)

REM Start RASA Actions Server
echo ⚡ Starting RASA Actions server...
start "RASA Actions" cmd /c "rasa run actions --port 5055"

REM Wait for actions server to start
timeout /t 5 >nul

call :check_port 5055
if %errorlevel%==0 (
    echo ✅ RASA Actions server is running on http://localhost:5055
) else (
    echo ❌ Failed to start RASA Actions server
    pause
    exit /b 1
)

REM Start RASA Server
echo 🚀 Starting RASA server...
start "RASA Server" cmd /c "rasa run --enable-api --cors * --port 5005"

REM Wait for RASA server to start
timeout /t 10 >nul

call :check_port 5005
if %errorlevel%==0 (
    echo ✅ RASA server is running on http://localhost:5005
) else (
    echo ❌ Failed to start RASA server
    pause
    exit /b 1
)

echo.
echo 🎉 RASA Health Chatbot is now running!
echo =======================================
echo 🌐 Frontend: http://localhost:3001
echo 🤖 RASA API: http://localhost:5005
echo ⚡ Actions: http://localhost:5055
echo 🔧 Backend API: http://localhost:8000/docs
echo.
echo ✨ Your health chatbot now uses RASA for intelligent responses!
echo 💬 Try asking questions like:
echo    • 'I have a fever'
echo    • 'Tell me about COVID vaccines'
echo    • 'Find hospitals near me'
echo    • 'I need emergency help'
echo.
echo Opening web interface...
start http://localhost:3001
echo.
echo Keep this window open to maintain all services.
pause

REM Stop all services
echo 🛑 Stopping all services...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
taskkill /f /im rasa.exe 2>nul

echo ✅ All services stopped
pause
