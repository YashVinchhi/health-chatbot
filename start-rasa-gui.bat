@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo   Health Chatbot with RASA Integration
echo   Starting Multilingual AI System (Fallback Disabled)...
echo ========================================

REM Set environment variables for local development
set DATABASE_URL=sqlite:///health_chatbot.db
REM Explicitly set RASA URLs for backend integration to avoid fallback confusion
set RASA_URL=http://localhost:5005
set RASA_ACTIONS_URL=http://localhost:5055
REM RASA_MODEL will be detected dynamically after training

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/Update dependencies only if rasa not present
python -c "import rasa" 1>nul 2>nul || (
  echo Installing dependencies...
  pip install -r requirements.txt
  pip install rasa rasa-sdk
)

echo.
echo ========================================
echo   Step 0: Training RASA Model (forces new model)
echo ========================================
cd rasa_bot
call rasa train --force

REM Pick latest generated model (.tar.gz) automatically
for /f "delims=" %%F in ('dir /b /a-d /o:-d models\*.tar.gz 2^>nul') do (
  set "RASA_MODEL=models\%%F"
  goto :got_model
)
:got_model
if not defined RASA_MODEL (
  echo WARNING: No model file found in models directory. Training may have failed.
  echo Exiting...
  cd ..
  goto :end
)

echo Selected model: %RASA_MODEL%
cd ..

REM Export for child windows
set RASA_MODEL=%RASA_MODEL%

echo.
echo ========================================
echo   Step 1: Starting RASA Actions Server (port 5055)
echo ========================================
echo Starting custom actions server on port 5055...
start "RASA Actions" cmd /k "cd rasa_bot && rasa run actions --port 5055"
    REM Wait for actions server to start
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   Step 2: Starting RASA Server (No FallbackClassifier)
echo ========================================
echo Using model: %RASA_MODEL%
echo (FallbackClassifier removed; model will always pick top intent.)
start "RASA Server" cmd /k "cd rasa_bot && rasa run --model %RASA_MODEL% --enable-api --cors \"*\" --port 5005"

REM Wait for RASA server to start
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo   Step 3: Starting Backend API (will probe RASA at %RASA_URL%)
echo ========================================
echo Starting FastAPI backend with RASA integration...
start "Backend API" cmd /k "cd backend && set RASA_URL=%RASA_URL% && set RASA_ACTIONS_URL=%RASA_ACTIONS_URL% && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   Step 4: Starting Frontend GUI
echo ========================================
echo Starting web interface...
start "Frontend" cmd /k "cd frontend && python server.py"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   🎉 HEALTH CHATBOT READY (NO FALLBACK)!
echo ========================================

echo 🌐 Web Interface: http://localhost:3001
echo 🤖 RASA Server:   http://localhost:5005
echo ⚙️  Backend API:   http://localhost:8000
echo 🔧 Actions:       http://localhost:5055

echo.
echo To verify no fallback:
echo   1. curl -s http://localhost:5005/status
echo   2. curl -s -X POST http://localhost:5005/model/parse -H "Content-Type: application/json" -d "{^^\"text^^\":^^\"hello^^\"}"
echo   3. Ensure backend returns source=rasa (not fallback_*) on chat requests.

echo.
echo Press any key to run quick status checks...
pause >nul

echo Checking RASA status endpoint...
curl -s http://localhost:5005/status || echo Unable to reach RASA.

echo.
echo Checking a sample parse ("randomtexttest") to show intent chosen:
curl -s -X POST http://localhost:5005/model/parse -H "Content-Type: application/json" -d "{\"text\":\"randomtexttest\"}"

echo.
echo Backend probing RASA (expect status online)...
curl -s http://localhost:8000/api/health/rasa/status

echo.
echo NOTE: If intent seems incorrect, improve training data instead of relying on fallback.

echo Done.
:end
endlocal
