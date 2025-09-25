#!/bin/bash
# Health Chatbot Startup Script for Docker

echo "🚀 Starting Health Chatbot with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Build and start all services
echo "🔨 Building and starting all services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo "✅ Health Chatbot is starting up!"
echo ""
echo "🌐 Access your services at:"
echo "   • Main Application: http://localhost:3001"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Rasa API: http://localhost:5005"
echo "   • Grafana Dashboard: http://localhost:3000"
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "📱 To stop all services: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo "📊 View logs: docker-compose logs -f [service_name]"
