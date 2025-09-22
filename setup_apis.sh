#!/bin/bash

echo "🚀 Setting up Health Chatbot with Real-Time APIs"
echo "=============================================="

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating environment file..."
    cp backend/.env.example backend/.env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit backend/.env with your API keys"
else
    echo "✅ Environment file already exists"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo ""
echo "🔑 API Keys Setup Instructions:"
echo "==============================="
echo "1. FREE APIs (no keys required):"
echo "   - Disease.sh API: Already configured for COVID data"
echo "   - FDA OpenFDA API: Already configured for drug information"
echo ""
echo "2. RECOMMENDED APIs (free tiers available):"
echo "   - NewsAPI: Get key from https://newsapi.org/register"
echo "   - OpenWeatherMap: Get key from https://openweathermap.org/api"
echo "   - CDC API: Get key from https://api.data.gov/signup/"
echo ""
echo "3. Edit backend/.env and add your API keys:"
echo "   NEWS_API_KEY=your_news_api_key"
echo "   OPENWEATHER_API_KEY=your_weather_api_key"
echo "   CDC_API_KEY=your_cdc_api_key"
echo ""
echo "🚀 Your health chatbot now supports:"
echo "   ✅ Real-time COVID-19 data"
echo "   ✅ FDA drug information"
echo "   ✅ Weather health advisories"
echo "   ✅ Health news alerts"
echo "   ✅ Vaccination schedules"
echo ""
echo "🔗 Test the new endpoints:"
echo "   - /api/health/outbreak - Real COVID data"
echo "   - /api/health/vaccination - Vaccine schedules"
echo "   - /api/health/drug-info/aspirin - Drug information"
echo "   - /api/health/weather-health-advisory - Weather advisories"
echo "   - /api/health/health-news - Latest health news"
