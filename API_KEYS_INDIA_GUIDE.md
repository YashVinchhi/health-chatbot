# India-Specific API Keys for Health Chatbot

## 🇮🇳 Essential India-Specific APIs

### 1. **Government of India Health APIs**
- **Ministry of Health & Family Welfare (MoHFW)**
  - **URL**: https://www.mohfw.gov.in/
  - **COVID Dashboard API**: https://api.covid19india.org/
  - **Cost**: Free
  - **Features**: COVID-19 state-wise data, vaccination stats

- **National Health Portal API**
  - **URL**: https://www.nhp.gov.in/
  - **Features**: Health schemes, disease information
  - **Cost**: Free (government portal)

### 2. **COVID-19 India Specific APIs**
- **covid19india.org API** (Community-driven)
  - **URL**: https://api.covid19india.org/
  - **Features**: State-wise COVID data, vaccination stats
  - **Cost**: Free, no authentication required
  - **Endpoints**:
    - `/data.json` - Overall India stats
    - `/v4/min/data.min.json` - Minimal state data
    - `/vaccine_tracker.json` - Vaccination data

### 3. **ICMR (Indian Council of Medical Research)**
- **Purpose**: Testing guidelines, research data
- **URL**: https://www.icmr.gov.in/
- **API Access**: Contact for research purposes
- **Cost**: Free for research/educational use

### 4. **Aarogya Setu APIs**
- **Purpose**: Contact tracing, self-assessment
- **URL**: https://www.aarogyasetu.gov.in/
- **Note**: Limited public API access

### 5. **Indian Weather APIs**
- **India Meteorological Department (IMD)**
  - **URL**: https://mausam.imd.gov.in/
  - **Features**: Weather warnings, monsoon updates
  - **API**: Contact IMD for access

- **OpenWeatherMap (India locations)**
  - **URL**: https://openweathermap.org/api
  - **Free tier**: 1000 calls/day
  - **Indian cities**: Mumbai, Delhi, Bangalore, etc.

### 6. **Indian Healthcare Directories**
- **Practo API**
  - **URL**: https://www.practo.com/
  - **Features**: Doctor directory, hospital listings
  - **Contact**: Practo for API access

- **Apollo Hospitals API**
  - **URL**: https://www.apollohospitals.com/
  - **Features**: Hospital services, doctor availability
  - **Contact**: Apollo for partnership

### 7. **Indian Pharmaceutical APIs**
- **Central Drugs Standard Control Organization (CDSCO)**
  - **URL**: https://cdsco.gov.in/
  - **Features**: Drug approvals, recalls
  - **API**: Government portal data

- **Indian Drug Database**
  - **MIMS India**: https://www.mims.com/india
  - **Features**: Drug information, interactions
  - **Cost**: Subscription required

## 🆓 Free Indian Health APIs (No Key Required)

### 1. **COVID19 India API**
```
Base URL: https://api.covid19india.org/
Endpoints:
- /data.json - National and state data
- /state_district_wise.json - District-wise data
- /deaths_recoveries.json - Detailed statistics
- /vaccine_tracker.json - Vaccination progress
```

### 2. **Indian Public Health Data**
```
Base URL: https://data.gov.in/
Features: 
- Health scheme data
- Hospital directories
- Disease surveillance
```

## 🏥 Emergency Numbers for India

### Medical Emergency
- **National Emergency**: 102 (Ambulance)
- **Police**: 100
- **Fire**: 101
- **COVID Helpline**: 1075

### State-wise Health Helplines
- **Delhi**: 011-22307145
- **Maharashtra**: 020-26127394
- **Karnataka**: 080-23212757
- **Tamil Nadu**: 044-24335253
- **Gujarat**: 079-26301400

## 🔧 India-Specific Environment Variables

```env
# Indian Government APIs
MOHFW_API_KEY=your_mohfw_key_here
COVID19_INDIA_BASE_URL=https://api.covid19india.org
NHP_API_KEY=your_nhp_key_here

# Indian Healthcare Services
PRACTO_API_KEY=your_practo_key_here
APOLLO_API_KEY=your_apollo_key_here

# Indian Weather
IMD_API_KEY=your_imd_key_here
OPENWEATHER_API_KEY=your_openweather_key_here

# Indian Location Services
MAPBOX_INDIA_API_KEY=your_mapbox_key_here
GOOGLE_MAPS_INDIA_API_KEY=your_google_maps_key_here

# Indian Language Support
GOOGLE_TRANSLATE_API_KEY=your_translate_key_here
```

## 💰 Cost Breakdown (India-Specific)

| Service | Free Tier | Paid Plans (INR) |
|---------|-----------|------------------|
| COVID19 India API | Unlimited | Free only |
| Gov.in Data Portal | Unlimited | Free only |
| OpenWeatherMap | 1000 calls/day | ₹3,000/month for 100k |
| Google Maps India | $200 credit/month | ₹0.40 per request |
| Practo API | Contact for pricing | Enterprise only |
| MIMS India | Trial available | ₹10,000+/year |

## 🌐 Indian Language Support

### Translation APIs for Regional Languages
- **Google Translate API**
  - **Languages**: Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Oriya
  - **Cost**: ₹1,600 per million characters

- **Microsoft Translator**
  - **Languages**: Major Indian languages
  - **Cost**: Free tier available

### Voice APIs for Indian Languages
- **Google Speech-to-Text**
  - **Languages**: Hindi, Bengali, Tamil, Telugu
  - **Cost**: ₹1,200 per hour of audio

## 🚀 Quick Start for India

### Minimum Required (Free):
1. **COVID19 India API** - Real-time COVID data
2. **Data.gov.in** - Government health data
3. **OpenWeatherMap** - Weather health advisories

### Recommended (Enhanced Features):
1. **Google Maps India** - Hospital/clinic locations
2. **Google Translate** - Regional language support
3. **News API** - Indian health news sources

## 📱 Indian Health Apps Integration

### Government Apps
- **Aarogya Setu**: Contact tracing
- **UMANG**: Government services
- **e-Sanjeevani**: Telemedicine

### Private Healthcare Apps
- **Practo**: Doctor consultations
- **Apollo 24/7**: Healthcare services
- **PharmEasy**: Medicine delivery
- **1mg**: Health information and medicines

## 🏛️ Regulatory Compliance

### Data Protection
- **Digital Personal Data Protection Act 2023**
- **IT Rules 2021**
- **Medical Device Rules 2017**

### Healthcare Regulations
- **Telemedicine Practice Guidelines 2020**
- **Clinical Establishments Act**
- **Drugs and Cosmetics Act 1940**

This setup provides comprehensive India-specific health data integration while ensuring compliance with local regulations!
