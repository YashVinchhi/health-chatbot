from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import Dict, Any, List, Optional
import re
import json

# Add new imports for external APIs
from services.health_data_service import health_data_service
from services.india_health_service import india_health_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    sender: str = "user"

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None  # Allow None values
    confidence: Optional[float] = None  # Allow None values

# Improved NLP patterns for better intent detection
INTENT_PATTERNS = {
    'greet': [
        r'\b(hello|hi|hey|good morning|good evening|greetings|hola|namaste)\b',
        r'^(hi|hello|hey)$',
    ],
    'goodbye': [
        r'\b(bye|goodbye|see you|farewell|talk to you later|good night)\b',
        r'^(bye|goodbye)$',
    ],
    'ask_symptoms': [
        r'\b(fever|sick|headache|cold|cough|sore throat|nauseous|body aches|chest pain|difficulty breathing|stomach pain|dizzy|rash|vomiting|diarrhea|pain|hurt|ache|symptoms|unwell|ill)\b',
        r'\bi have\b.*\b(fever|headache|cold|cough|pain|symptoms|temperature|ache|hurt)\b',
        r'\bi feel\b.*\b(sick|nauseous|dizzy|unwell|ill|bad|terrible|awful|weak)\b',
        r'\bi\'m\b.*\b(sick|coughing|feeling|having|ill|unwell|experiencing)\b',
        r'\bi think i.*\b(have|am having|feel|am|might have)\b.*\b(fever|sick|ill|unwell|symptoms)\b',
        r'\bfeeling.*\b(sick|unwell|bad|ill|terrible|awful|weak|dizzy)\b',
        r'\bhaving.*\b(fever|headache|pain|symptoms|trouble|difficulty)\b',
        r'\bmy.*\b(head|stomach|throat|chest|body).*\b(hurts|aches|pains|feels)\b',
        r'\bi.*\b(hurt|ache|pain)\b.*\b(all over|everywhere|badly)\b',
        r'\bnot feeling.*\b(well|good|right|normal)\b',
        r'\bsomething.*wrong.*\b(with me|health)\b',
        r'\bI have symptoms\b',
        r'\bsymptoms.*\b(of|include|are)\b',
    ],
    'ask_vaccination': [
        r'\b(vaccin|immuniz|shot|jab|covid|flu|hepatitis|pfizer|moderna|booster)\b',
        r'\bwhen should i get vaccinated\b',
        r'\bvaccine schedule\b',
        r'\bside effects\b',
        r'\btell me about.*vaccin\b',
        r'\bvaccination.*info\b',
        r'\bimmunization\b',
    ],
    'ask_outbreak_info': [
        r'\b(outbreak|epidemic|disease|covid cases|health alert|flu outbreak|pandemic)\b',
        r'\bany.*outbreak\b',
        r'\bhealth.*alert\b',
        r'\bdisease.*nearby\b',
        r'\bany.*health.*alert\b',
        r'\bcurrent.*outbreak\b',
        r'\bdisease.*surveillance\b',
    ],
    'ask_emergency': [
        r'\b(emergency|urgent|ambulance|hospital|critical|help|911|108)\b',
        r'\bemergency help\b',
        r'\bcall ambulance\b',
        r'\bimmediate help\b',
        r'\bmedical emergency\b',
        r'\bneed help.*urgent\b',
    ],
    'ask_general_health': [
        r'\b(health tips|stay healthy|preventive|lifestyle|diet|exercise|wellness|nutrition)\b',
        r'\bhow to.*healthy\b',
        r'\bhealth advice\b',
        r'\bpreventive measures\b',
        r'\bwellness.*tips\b',
        r'\bhealthy.*lifestyle\b',
        r'\bfitness.*advice\b',
    ],
    'ask_medication': [
        r'\b(medicine|medication|drug|dosage|prescription|pill|tablet|treatment)\b',
        r'\bwhat medicine\b',
        r'\bside effects\b',
        r'\bover the counter\b',
        r'\bdrug.*interaction\b',
        r'\bmedication.*advice\b',
    ],
    'bot_challenge': [
        r'\bare you.*bot\b',
        r'\bare you.*human\b',
        r'\bam i talking to.*bot\b',
        r'\bwhat are you\b',
        r'\bwho are you\b',
    ]
}

# Responses for each intent
INTENT_RESPONSES = {
    'greet': [
        "Hello! I'm your health assistant. How can I help you today?",
        "Hi there! I'm here to help with your health questions. What would you like to know?",
        "Good day! I'm your AI health assistant. How may I assist you with your health concerns?"
    ],
    'goodbye': [
        "Goodbye! Take care of your health. Feel free to ask if you need help again.",
        "Bye! Stay healthy and don't hesitate to reach out if you have health concerns.",
        "Take care! Remember to prioritize your health and wellness."
    ],
    'ask_symptoms': [
        "I understand you're experiencing symptoms. Can you describe them in more detail? For serious symptoms like chest pain, difficulty breathing, or severe pain, please seek immediate medical attention.\n\nIn the meantime:\n• Stay hydrated\n• Get plenty of rest\n• Monitor your symptoms\n• Seek medical help if symptoms worsen",
        "I hear that you're not feeling well. For any health concerns, it's always best to consult with a healthcare professional who can properly assess your symptoms.\n\nGeneral advice:\n• Rest and stay hydrated\n• Take your temperature regularly\n• Note when symptoms started\n• Contact your doctor if symptoms persist"
    ],
    'ask_vaccination': [
        "I can help with vaccination information. Here are current recommendations:\n\n💉 **COVID-19**: Recommended for all adults and children 6 months and older\n💉 **Influenza (Flu)**: Annual vaccination for everyone 6 months and older\n💉 **Hepatitis B**: Recommended for all infants and high-risk adults\n\nFor specific vaccine schedules, please consult your healthcare provider.",
        "Vaccination is crucial for preventing diseases. Key vaccines include:\n\n• COVID-19 vaccines and boosters\n• Annual flu shots\n• Routine childhood immunizations\n• Travel vaccines if needed\n\nAlways consult with your healthcare provider for personalized vaccination advice."
    ],
    'ask_outbreak_info': [
        "Here's current health alert information:\n\n🦠 **Seasonal Influenza**: Moderate activity level - vaccination recommended\n🦠 **COVID-19**: Low-moderate risk - follow local health guidelines\n\nStay informed through:\n• Local health department updates\n• CDC or WHO websites\n• Healthcare provider communications",
        "Current disease surveillance shows:\n\n• Seasonal flu activity is present\n• COVID-19 continues with variants\n• No major outbreak alerts in most areas\n\nFor local specific information, check with your local health department."
    ],
    'ask_emergency': [
        "🚨 **For medical emergencies, please:**\n\n• Call emergency services immediately:\n  - US: 911\n  - India: 108\n  - UK: 999\n  - Australia: 000\n\n• If this is urgent but not life-threatening, contact your healthcare provider or visit the nearest emergency room.\n\n• For poison emergencies: US 1-800-222-1222",
        "🚨 **URGENT**: For any medical emergency, call your local emergency number immediately!\n\nEmergency signs include:\n• Chest pain or pressure\n• Difficulty breathing\n• Severe bleeding\n• Loss of consciousness\n• Severe allergic reactions\n\nDon't delay - seek immediate medical attention!"
    ],
    'ask_general_health': [
        "Here are essential health tips for wellness:\n\n🍎 **Nutrition**: Eat a balanced diet with fruits, vegetables, whole grains\n🏃 **Exercise**: 150 minutes of moderate activity per week\n😴 **Sleep**: 7-9 hours per night for adults\n💧 **Hydration**: Drink plenty of water throughout the day\n🧼 **Hygiene**: Wash hands frequently\n🩺 **Checkups**: Regular health screenings and vaccinations",
        "Maintaining good health involves:\n\n• Balanced nutrition and regular meals\n• Regular physical activity\n• Adequate sleep and stress management\n• Preventive healthcare (checkups, screenings)\n• Avoiding tobacco and limiting alcohol\n• Mental health care and social connections\n\nSmall daily choices make a big difference in long-term health!"
    ],
    'ask_medication': [
        "⚠️ **Important**: I cannot provide specific medication advice. Please consult with:\n\n• Your healthcare provider\n• Licensed pharmacist\n• Telehealth services\n\n**General medication safety**:\n• Take as prescribed\n• Check for drug interactions\n• Store properly\n• Don't share medications\n• Report side effects to your doctor",
        "For medication questions, always consult healthcare professionals:\n\n• **Prescription drugs**: Talk to your doctor or pharmacist\n• **Over-the-counter**: Read labels carefully, follow dosing instructions\n• **Side effects**: Contact your healthcare provider\n• **Drug interactions**: Use pharmacy consultation services\n\nNever self-medicate for serious conditions."
    ],
    'bot_challenge': [
        "I am a health assistant AI designed to provide general health information and guidance. For specific medical advice, please consult with healthcare professionals.",
        "Yes, I'm an AI health assistant! I can provide general health information, but I'm not a replacement for professional medical advice."
    ]
}

def detect_intent(message: str) -> tuple[str, float]:
    """
    Improved intent detection using pattern matching
    Returns (intent, confidence_score)
    """
    message_lower = message.lower().strip()
    best_intent = None
    best_confidence = 0.0

    for intent, patterns in INTENT_PATTERNS.items():
        confidence = 0.0
        matches = 0

        for pattern in patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                matches += 1
                # Weight patterns differently - exact matches get higher confidence
                if pattern.startswith('^') and pattern.endswith('$'):
                    confidence += 0.9  # Exact match patterns
                else:
                    confidence += 0.7  # Partial match patterns

        # Normalize confidence based on number of patterns
        if matches > 0:
            confidence = confidence / len(patterns)

            # Boost confidence for multiple pattern matches
            if matches > 1:
                confidence += 0.3

            # Special handling for emergency keywords
            if intent == 'ask_emergency':
                emergency_keywords = ['emergency', 'urgent', 'help', 'ambulance', 'critical', '911', '108']
                for keyword in emergency_keywords:
                    if keyword in message_lower:
                        confidence += 0.4

            # Special handling for symptom keywords
            if intent == 'ask_symptoms':
                symptom_keywords = ['fever', 'sick', 'pain', 'hurt', 'ache', 'ill', 'unwell', 'feeling', 'having']
                symptom_count = sum(1 for keyword in symptom_keywords if keyword in message_lower)
                confidence += symptom_count * 0.1

            # Special handling for vaccination keywords
            if intent == 'ask_vaccination':
                vacc_keywords = ['vaccine', 'vaccination', 'immuniz', 'shot', 'jab', 'covid', 'flu']
                vacc_count = sum(1 for keyword in vacc_keywords if keyword in message_lower)
                confidence += vacc_count * 0.2

        if confidence > best_confidence:
            best_confidence = confidence
            best_intent = intent

    # Lower the confidence threshold to catch more intents
    if best_confidence < 0.2:
        return 'unknown', 0.0

    return best_intent, min(best_confidence, 1.0)

def get_response_for_intent(intent: str) -> str:
    """Get a response for the detected intent"""
    if intent in INTENT_RESPONSES:
        import random
        return random.choice(INTENT_RESPONSES[intent])
    else:
        return "I understand you have a health question. Could you please provide more details? For specific medical concerns, I recommend consulting with a healthcare professional."

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(chat_message: ChatMessage):
    """
    Process chat message and return response using improved NLP
    """
    try:
        # Detect intent
        intent, confidence = detect_intent(chat_message.message)

        # Get response
        if intent == 'unknown':
            response_text = "I want to help with your health question, but I'm not sure what you're asking about. Could you please rephrase or be more specific? For urgent medical concerns, please contact a healthcare professional."
        else:
            response_text = get_response_for_intent(intent)

        # Log for debugging
        logger.info(f"Message: '{chat_message.message}' -> Intent: {intent} (confidence: {confidence:.2f})")

        return ChatResponse(
            response=response_text,
            intent=intent,  # This can now be None or a string
            confidence=confidence
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Error processing your message")

@router.get("/vaccination")
async def get_vaccination_info(age_group: str = "adult"):
    """Get real vaccination information from external APIs"""
    try:
        # Get real data from health data service
        result = await health_data_service.get_vaccination_schedule(age_group)

        if result["success"]:
            return {
                "message": f"Current vaccination recommendations for {age_group}",
                "vaccines": result["data"],
                "source": "CDC/Health Data Service",
                "last_updated": "Real-time data"
            }
        else:
            # Fallback to existing mock data
            return {
                "message": "Current vaccination recommendations (cached data)",
                "vaccines": [
                    {
                        "name": "COVID-19",
                        "description": "Recommended for all adults and children 6 months and older",
                        "schedule": "Initial series plus annual boosters"
                    },
                    {
                        "name": "Influenza (Flu)",
                        "description": "Annual vaccination recommended for everyone 6 months and older",
                        "schedule": "Annually, preferably in early fall"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting vaccination info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving vaccination information")

@router.get("/outbreak")
async def get_outbreak_info(country: str = "all"):
    """Get real disease outbreak information"""
    try:
        # Get COVID data from Disease.sh API (free)
        covid_result = await health_data_service.get_covid_data(country)

        # Get health news for additional outbreak info
        news_result = await health_data_service.get_health_news("disease outbreak")

        alerts = []

        if covid_result["success"]:
            covid_data = covid_result["data"]
            alerts.append({
                "disease": "COVID-19",
                "location": covid_data["country"],
                "active_cases": covid_data["active"],
                "critical_cases": covid_data["critical"],
                "risk_level": "Moderate" if covid_data["active"] > 1000 else "Low",
                "details": f"Active cases: {covid_data['active']:,}, Critical: {covid_data['critical']:,}",
                "last_updated": covid_data["updated"]
            })

        # Add seasonal flu info
        alerts.append({
            "disease": "Seasonal Influenza",
            "location": "National",
            "risk_level": "Moderate",
            "details": "Seasonal flu activity is increasing. Vaccination recommended."
        })

        return {
            "message": "Current disease outbreak status",
            "alerts": alerts,
            "news": news_result.get("data", []) if news_result["success"] else [],
            "source": "Disease.sh API + Health News",
            "last_updated": "Real-time data"
        }

    except Exception as e:
        logger.error(f"Error getting outbreak info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving outbreak information")

@router.get("/drug-info/{drug_name}")
async def get_drug_info(drug_name: str):
    """Get drug information from FDA API"""
    try:
        result = await health_data_service.get_drug_information(drug_name)

        if result["success"]:
            return {
                "message": f"Drug information for {drug_name}",
                "drug_info": result["data"],
                "source": "FDA OpenFDA API",
                "disclaimer": "This information is for educational purposes only. Consult healthcare professionals for medical advice."
            }
        else:
            return {
                "message": f"Unable to find information for {drug_name}",
                "error": result["error"],
                "recommendation": "Please consult a healthcare professional or pharmacist for detailed drug information."
            }
    except Exception as e:
        logger.error(f"Error getting drug info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving drug information")

@router.get("/weather-health-advisory")
async def get_weather_health_advisory(location: str = "global"):
    """Get weather-related health advisories"""
    try:
        result = await health_data_service.get_weather_health_advisory(location)

        if result["success"]:
            return {
                "message": f"Weather health advisory for {result['data']['location']}",
                "advisory": result["data"],
                "source": "OpenWeatherMap API" if settings.openweather_api_key else "General Advisory"
            }
        else:
            return {
                "message": "General weather health advisory",
                "advisory": {"advisory": ["Stay hydrated and dress appropriately for the weather"]}
            }
    except Exception as e:
        logger.error(f"Error getting weather advisory: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving weather advisory")

@router.get("/health-news")
async def get_health_news(query: str = "health"):
    """Get latest health news and alerts"""
    try:
        result = await health_data_service.get_health_news(query)

        return {
            "message": f"Latest health news for: {query}",
            "articles": result["data"],
            "source": "NewsAPI" if settings.news_api_key else "Curated Health News"
        }
    except Exception as e:
        logger.error(f"Error getting health news: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving health news")

@router.get("/india/covid-data")
async def get_india_covid_data(state: str = "India"):
    """Get COVID-19 data specific to India or Indian states"""
    try:
        result = await india_health_service.get_covid_india_data(state)

        if result["success"]:
            covid_data = result["data"]
            return {
                "message": f"COVID-19 data for {covid_data['state']}",
                "data": covid_data,
                "source": "covid19india.org API",
                "helpline": "1075 (COVID Helpline India)",
                "last_updated": covid_data.get("last_updated", "Real-time")
            }
        else:
            return {
                "message": "Unable to fetch COVID-19 data",
                "error": result["error"],
                "helpline": "1075 (COVID Helpline India)"
            }
    except Exception as e:
        logger.error(f"Error getting India COVID data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving COVID-19 data for India")

@router.get("/india/vaccination-stats")
async def get_india_vaccination_stats():
    """Get real-time vaccination statistics for India"""
    try:
        result = await india_health_service.get_vaccination_india_data()

        if result["success"]:
            vacc_data = result["data"]
            return {
                "message": "India vaccination statistics",
                "data": {
                    "total_doses_administered": vacc_data["total_doses"],
                    "people_vaccinated_first_dose": vacc_data["first_dose"],
                    "people_fully_vaccinated": vacc_data["second_dose"],
                    "precaution_doses": vacc_data["precaution_dose"],
                    "vaccinated_today": vacc_data["today_vaccinated"]
                },
                "source": "COVID19 India API",
                "cowin_portal": "https://www.cowin.gov.in/",
                "helpline": "1075"
            }
        else:
            return {
                "message": "Unable to fetch vaccination statistics",
                "error": result["error"]
            }
    except Exception as e:
        logger.error(f"Error getting vaccination stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving vaccination statistics")

@router.get("/india/health-schemes")
async def get_indian_health_schemes():
    """Get information about Indian government health schemes"""
    try:
        result = await india_health_service.get_indian_health_schemes()

        return {
            "message": "Indian Government Health Schemes",
            "schemes": result["data"],
            "portal": "https://pmjay.gov.in/",
            "note": "Contact scheme helplines for enrollment and benefits"
        }
    except Exception as e:
        logger.error(f"Error getting health schemes: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving health schemes information")

@router.get("/india/emergency-contacts")
async def get_india_emergency_contacts(state: str = "national"):
    """Get India-specific emergency contacts"""
    try:
        result = await india_health_service.get_indian_emergency_contacts(state)

        return {
            "message": f"Emergency contacts for {state}",
            "contacts": result["data"],
            "important_note": "For immediate medical emergencies, call 102 (Ambulance) or 108 (Emergency Response)"
        }
    except Exception as e:
        logger.error(f"Error getting emergency contacts: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving emergency contacts")

@router.get("/india/hospitals")
async def get_indian_hospitals(city: str = "delhi"):
    """Get list of major hospitals in Indian cities"""
    try:
        result = await india_health_service.get_indian_hospitals_nearby(city)

        return {
            "message": f"Major hospitals in {result['data'][0]['city'] if result['data'] else city}",
            "hospitals": result["data"],
            "city": result["city"],
            "note": "Call hospitals directly for appointments and emergency services"
        }
    except Exception as e:
        logger.error(f"Error getting hospitals: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving hospital information")

@router.get("/india/weather-health")
async def get_india_weather_health(city: str = "delhi"):
    """Get weather-based health advisory for Indian cities"""
    try:
        result = await india_health_service.get_indian_weather_health_advisory(city)

        if result["success"]:
            return {
                "message": f"Weather health advisory for {result['data']['city']}",
                "advisory": result["data"],
                "source": "OpenWeatherMap + India Health Guidelines"
            }
        else:
            return {
                "message": "General health advisory for India",
                "advisory": result["data"]
            }
    except Exception as e:
        logger.error(f"Error getting weather health advisory: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving weather health advisory")

# Update existing chat function to include India-specific responses
INDIA_INTENT_RESPONSES = {
    'ask_emergency': [
        "🚨 **भारतीय आपातकालीन सेवाएं / Indian Emergency Services:**\n\n• **मेडिकल इमरजेंसी**: 102 (एम्बुलेंस)\n• **पुलिस**: 100\n• **फायर**: 101\n• **COVID हेल्पलाइन**: 1075\n• **महिला हेल्पलाइन**: 1091\n\n**तुरंत चिकित्सा सहायता के लिए 102 डायल करें!**",
        "🚨 **URGENT - Indian Emergency Numbers:**\n\n• **Medical Emergency**: 102 (Ambulance)\n• **Police**: 100\n• **Fire**: 101\n• **COVID Helpline**: 1075\n• **Mental Health**: 9152987821 (AASRA)\n\n**For immediate medical help, dial 102!**"
    ],
    'ask_vaccination': [
        "💉 **भारत में टीकाकरण / Vaccination in India:**\n\n• **COVID-19**: CoWIN पोर्टल पर रजिस्टर करें\n• **बच्चों के लिए**: Mission Indradhanush के तहत मुफ्त टीके\n• **गर्भवती महिलाओं के लिए**: Janani Suraksha Yojana\n\n**CoWIN Portal**: https://www.cowin.gov.in/\n**हेल्पलाइन**: 1075",
        "💉 **Indian Vaccination Information:**\n\n• **COVID-19**: Register on CoWIN portal for free vaccines\n• **Routine Immunization**: Free vaccines under Mission Indradhanush\n• **Adult Vaccines**: Available at government and private centers\n\n**Portal**: https://www.cowin.gov.in/\n**Helpline**: 1075"
    ],
    'ask_outbreak_info': [
        "🦠 **भारत में बीमारी की स्थिति / Disease Status in India:**\n\n• **COVID-19**: राज्यवार डेटा उपलब्ध\n• **डेंगू**: मानसून के दौरान सावधानी बरतें\n• **मलेरिया**: मच्छरदानी का उपयोग करें\n\n**अपडेट के लिए**: https://www.mohfw.gov.in/\n**हेल्पलाइन**: 1075",
        "🦠 **Current Health Alerts for India:**\n\n• **COVID-19**: State-wise data available\n• **Dengue**: Monsoon season precautions needed\n• **Malaria**: Use mosquito nets and repellents\n\n**Updates**: https://www.mohfw.gov.in/\n**Helpline**: 1075"
    ]
}

# Update the get_response_for_intent function to include India-specific responses
def get_response_for_intent_india(intent: str) -> str:
    """Get India-specific response for the detected intent"""
    if intent in INDIA_INTENT_RESPONSES:
        import random
        return random.choice(INDIA_INTENT_RESPONSES[intent])
    elif intent in INTENT_RESPONSES:
        import random
        return random.choice(INTENT_RESPONSES[intent])
    else:
        return "मैं आपकी स्वास्थ्य संबंधी मदद करना चाहता हूं। कृपया अधिक विवरण दें। / I want to help with your health question. Please provide more details. For medical emergencies, call 102."

