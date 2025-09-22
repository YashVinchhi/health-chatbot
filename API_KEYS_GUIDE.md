# API Keys Required for Health Chatbot

## 🔑 Essential API Keys Needed

### 1. **CDC/WHO Health Data APIs**
- **Purpose**: Disease surveillance, outbreak data, vaccination schedules
- **Sources**:
  - **CDC API**: https://data.cdc.gov/
  - **WHO API**: https://covid19.who.int/
  - **Disease.sh API**: https://disease.sh/ (Free, no key required)

### 2. **FDA Drug Information API**
- **Purpose**: Medication information, drug interactions, recalls
- **Source**: https://open.fda.gov/
- **Cost**: Free
- **Registration**: https://open.fda.gov/apis/authentication/

### 3. **News/Health Alert APIs**
- **Purpose**: Real-time health news and alerts
- **Options**:
  - **NewsAPI**: https://newsapi.org/ (Free tier: 1000 requests/day)
  - **MediaStack**: https://mediastack.com/ (Free tier: 1000 requests/month)

### 4. **Geocoding/Location APIs**
- **Purpose**: Location-based health alerts and nearby facilities
- **Options**:
  - **Google Maps API**: https://developers.google.com/maps
  - **OpenCage Geocoding**: https://opencagedata.com/ (Free tier: 2500 requests/day)

### 5. **Medical Information APIs**
- **Purpose**: Symptom checking, medical references
- **Options**:
  - **Infermedica API**: https://infermedica.com/ (Medical AI)
  - **ApiMedic**: https://apimedic.com/ (Symptom checker)

### 6. **Weather APIs** (for health correlations)
- **Purpose**: Weather-related health advisories
- **Options**:
  - **OpenWeatherMap**: https://openweathermap.org/api (Free tier: 1000 calls/day)
  - **WeatherAPI**: https://www.weatherapi.com/ (Free tier: 1M calls/month)

## 🆓 Free APIs (No Key Required)

### 1. **Disease.sh API**
- **URL**: https://disease.sh/v3/covid-19/
- **Features**: COVID-19 data, historical data by country
- **Usage**: No authentication required

### 2. **REST Countries API**
- **URL**: https://restcountries.com/
- **Features**: Country-specific health system information

## 🔧 How to Get API Keys

### CDC Data.gov API
1. Visit: https://api.data.gov/signup/
2. Provide email and organization details
3. Get API key instantly
4. Rate limit: 1000 requests/hour

### FDA OpenFDA API
1. Visit: https://open.fda.gov/apis/authentication/
2. No key required for basic usage
3. Optional API key for higher rate limits

### NewsAPI
1. Visit: https://newsapi.org/register
2. Sign up with email
3. Get API key instantly
4. Free tier: 1000 requests/day

### Google Maps API
1. Visit: https://console.cloud.google.com/
2. Create new project
3. Enable Maps JavaScript API and Geocoding API
4. Create credentials (API key)
5. $200 free credit monthly

### OpenWeatherMap API
1. Visit: https://openweathermap.org/api
2. Sign up for free account
3. Get API key from dashboard
4. Free tier: 1000 calls/day

## 💰 Cost Breakdown

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| Disease.sh | Unlimited | Free only |
| CDC API | 1000 req/hour | Free only |
| FDA API | Unlimited basic | Optional paid |
| NewsAPI | 1000 req/day | $449/month for commercial |
| Google Maps | $200 credit/month | Pay per use |
| OpenWeatherMap | 1000 req/day | $40/month for 100k |
| Infermedica | 100 req/month | $0.10 per request |

## 🔒 Environment Variables Setup

Create a `.env` file in your backend directory:

```env
# Health Data APIs
CDC_API_KEY=your_cdc_api_key_here
FDA_API_KEY=your_fda_api_key_here
NEWS_API_KEY=your_news_api_key_here

# Location Services
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
OPENCAGE_API_KEY=your_opencage_key_here

# Weather Data
OPENWEATHER_API_KEY=your_openweather_key_here

# Medical APIs
INFERMEDICA_APP_ID=your_infermedica_app_id
INFERMEDICA_APP_KEY=your_infermedica_app_key

# Database
DATABASE_URL=postgresql://username:password@localhost/dbname
```

## 🚀 Quick Start (Minimum Required)

For basic functionality, you only need:
1. **Disease.sh API** (Free, no key) - for COVID/outbreak data
2. **CDC API** (Free) - for vaccination schedules
3. **OpenWeatherMap** (Free tier) - for weather-health correlations

This gives you real-time health data without any costs!
