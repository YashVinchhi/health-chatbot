#!/bin/bash
# RASA Health Chatbot Startup Script

echo "🏥 Starting RASA Health Chatbot Integration..."

# Set environment variables
export RASA_URL="http://localhost:5005"
export BACKEND_URL="http://localhost:8000"

# Function to check if a port is in use
check_port() {
    local port=$1
    if netstat -tuln | grep ":$port " > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to start RASA server
start_rasa_server() {
    echo "📚 Training RASA model..."
    cd rasa_bot

    # Train the model
    rasa train --force

    if [ $? -eq 0 ]; then
        echo "✅ RASA model trained successfully!"

        # Start RASA server
        echo "🚀 Starting RASA server on port 5005..."
        rasa run --enable-api --cors "*" --port 5005 &
        RASA_PID=$!
        echo "RASA Server PID: $RASA_PID"

        # Wait for RASA server to start
        sleep 10

        if check_port 5005; then
            echo "✅ RASA server is running on http://localhost:5005"
        else
            echo "❌ Failed to start RASA server"
            return 1
        fi
    else
        echo "❌ Failed to train RASA model"
        return 1
    fi
}

# Function to start RASA actions server
start_rasa_actions() {
    echo "⚡ Starting RASA Actions server..."
    cd rasa_bot

    # Start actions server
    rasa run actions --port 5055 &
    ACTIONS_PID=$!
    echo "RASA Actions PID: $ACTIONS_PID"

    # Wait for actions server to start
    sleep 5

    if check_port 5055; then
        echo "✅ RASA Actions server is running on http://localhost:5055"
    else
        echo "❌ Failed to start RASA Actions server"
        return 1
    fi
}

# Function to start backend
start_backend() {
    echo "🔧 Starting FastAPI Backend..."
    cd ../backend

    # Check if virtual environment exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Install requirements if needed
    pip install -r requirements.txt

    # Start FastAPI backend
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"

    # Wait for backend to start
    sleep 5

    if check_port 8000; then
        echo "✅ Backend server is running on http://localhost:8000"
    else
        echo "❌ Failed to start backend server"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    echo "🔍 Checking dependencies..."

    # Check Python
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed"
        return 1
    fi

    # Check pip
    if ! command -v pip &> /dev/null; then
        echo "❌ pip is not installed"
        return 1
    fi

    # Check RASA
    if ! command -v rasa &> /dev/null; then
        echo "⚠️ RASA is not installed. Installing..."
        pip install rasa
    fi

    echo "✅ Dependencies check completed"
}

# Function to stop all services
stop_services() {
    echo "🛑 Stopping all services..."

    if [ ! -z "$RASA_PID" ]; then
        kill $RASA_PID 2>/dev/null
        echo "Stopped RASA server"
    fi

    if [ ! -z "$ACTIONS_PID" ]; then
        kill $ACTIONS_PID 2>/dev/null
        echo "Stopped RASA Actions server"
    fi

    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Stopped Backend server"
    fi

    # Kill any remaining processes on the ports
    fuser -k 5005/tcp 2>/dev/null || true
    fuser -k 5055/tcp 2>/dev/null || true
    fuser -k 8000/tcp 2>/dev/null || true

    echo "✅ All services stopped"
}

# Trap to stop services on script exit
trap stop_services EXIT INT TERM

# Main execution
main() {
    echo "🏥 RASA Health Chatbot Integration Setup"
    echo "======================================="

    # Check dependencies
    check_dependencies

    if [ $? -ne 0 ]; then
        echo "❌ Dependency check failed"
        exit 1
    fi

    # Start backend first
    start_backend
    if [ $? -ne 0 ]; then
        echo "❌ Failed to start backend"
        exit 1
    fi

    # Start RASA actions server
    start_rasa_actions
    if [ $? -ne 0 ]; then
        echo "❌ Failed to start RASA actions"
        exit 1
    fi

    # Start RASA server
    start_rasa_server
    if [ $? -ne 0 ]; then
        echo "❌ Failed to start RASA server"
        exit 1
    fi

    echo ""
    echo "🎉 RASA Health Chatbot is now running!"
    echo "======================================="
    echo "🌐 Frontend: http://localhost:8000"
    echo "🤖 RASA API: http://localhost:5005"
    echo "⚡ Actions: http://localhost:5055"
    echo "🔧 Backend: http://localhost:8000/docs"
    echo ""
    echo "✨ Your health chatbot now uses RASA for intelligent responses!"
    echo "💬 Try asking questions like:"
    echo "   • 'I have a fever'"
    echo "   • 'Tell me about COVID vaccines'"
    echo "   • 'Find hospitals near me'"
    echo "   • 'I need emergency help'"
    echo ""
    echo "Press Ctrl+C to stop all services"

    # Keep script running
    while true; do
        sleep 1

        # Check if services are still running
        if ! check_port 5005; then
            echo "⚠️ RASA server stopped unexpectedly"
            break
        fi

        if ! check_port 5055; then
            echo "⚠️ RASA Actions server stopped unexpectedly"
            break
        fi

        if ! check_port 8000; then
            echo "⚠️ Backend server stopped unexpectedly"
            break
        fi
    done
}

# Check command line arguments
if [ "$1" = "stop" ]; then
    stop_services
    exit 0
elif [ "$1" = "train" ]; then
    echo "🎓 Training RASA model only..."
    cd rasa_bot
    rasa train --force
    exit 0
elif [ "$1" = "help" ] || [ "$1" = "--help" ]; then
    echo "RASA Health Chatbot Startup Script"
    echo "=================================="
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    Start all services (default)"
    echo "  stop     Stop all running services"
    echo "  train    Train RASA model only"
    echo "  help     Show this help message"
    echo ""
    echo "The script will start:"
    echo "• FastAPI Backend (port 8000)"
    echo "• RASA Server (port 5005)"
    echo "• RASA Actions Server (port 5055)"
    exit 0
fi

# Run main function
main
