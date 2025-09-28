from fastapi import APIRouter
from pydantic import BaseModel
import logging
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Add new imports for external APIs (converted to direct imports)
from services.health_data_service import health_data_service
from services.india_health_service import india_health_service
from services.rasa_service import rasa_service
from services.session_service import session_service
from services.llm_service import llm_service  # NEW
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    sender: str = "user"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    sender: str = "bot"
    timestamp: str
    buttons: Optional[List[Dict[str, Any]]] = []
    quick_replies: Optional[List[str]] = []
    source: str = "rasa"
    entities: Optional[List[Dict[str, Any]]] = []
    session_id: str
    language: str

@router.get("/rasa/status")
async def rasa_status():
    """Expose RASA server status for frontend connectivity check"""
    try:
        status = await rasa_service.check_rasa_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get RASA status: {e}")
        return {"status": "offline", "error": str(e)}

@router.get("/rasa/model/info")
async def rasa_model_info():
    """Return currently loaded model and minimal metadata"""
    try:
        status = await rasa_service.check_rasa_status()
        return {
            "model_file": status.get("model_file"),
            "model_loaded": status.get("model_loaded"),
            "actions_server": status.get("actions_server"),
            "version": status.get("version"),
            "status": status.get("status")
        }
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        return {"status": "offline", "error": str(e)}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_rasa(message: ChatMessage):
    """Unified chat endpoint. If USE_LLM=true, use local Ollama model instead of RASA."""
    try:
        session_id = message.session_id or str(uuid.uuid4())
        logger.info(f"Processing message: '{message.message}' for session: {session_id} (LLM Mode={settings.use_llm})")

        # Session + history
        session_data = await session_service.get_or_create_session(session_id, message.message)
        user_language = session_data['language']
        conversation_history = await session_service.get_conversation_history(session_id, limit=8)

        # LLM path
        if settings.use_llm:
            llm_raw = await llm_service.generate(message.message, session_id, conversation_history)
            response = ChatResponse(
                response=llm_raw.get('response', ''),
                intent=llm_raw.get('intent', 'unknown'),
                confidence=llm_raw.get('confidence', 0.0),
                timestamp=llm_raw.get('timestamp', datetime.now().isoformat()),
                buttons=llm_raw.get('buttons', []),
                quick_replies=llm_raw.get('quick_replies', []),
                source=llm_raw.get('source', 'llm'),
                entities=llm_raw.get('entities', []),
                session_id=session_id,
                language=user_language
            )
            # Persist
            await session_service.save_message(
                session_id=session_id,
                message=message.message,
                response=response.response,
                intent=response.intent or 'unknown',
                confidence=response.confidence or 0.0,
                language=user_language
            )
            return response

        # --- RASA path (unchanged below) ---
        rasa_available = False
        rasa_response = None
        fallback_reason = None

        try:
            if hasattr(rasa_service, 'is_available') and rasa_service.is_available:
                logger.debug("Attempting RASA response (service flagged available)")
                rasa_response = await rasa_service.send_message_to_rasa(
                    message=message.message,
                    sender_id=session_id,
                    conversation_history=conversation_history
                )
                if rasa_response and rasa_response.get("source") == "rasa" and rasa_response.get("response"):
                    rasa_available = True
                else:
                    fallback_reason = f"Empty or non-rasa response (source={rasa_response.get('source') if rasa_response else 'none'})"
            else:
                logger.debug("RASA not yet marked available - probing status")
                status = await rasa_service.check_rasa_status()
                if status.get("status") == "online":
                    rasa_response = await rasa_service.send_message_to_rasa(
                        message=message.message,
                        sender_id=session_id,
                        conversation_history=conversation_history
                    )
                    if rasa_response and rasa_response.get("source") == "rasa" and rasa_response.get("response"):
                        rasa_available = True
                    else:
                        fallback_reason = f"Online but empty/non-rasa response (source={rasa_response.get('source') if rasa_response else 'none'})"
                else:
                    fallback_reason = f"RASA status offline ({status.get('tried', [])})"
        except Exception as rasa_error:
            logger.warning(f"RASA service exception: {rasa_error}")
            fallback_reason = f"exception: {rasa_error}";
            rasa_available = False

        # Use enhanced fallback system if RASA is not available or doesn't provide good response
        if not rasa_available:
            logger.info(f"Using enhanced fallback system. Reason: {fallback_reason}")

            # Use our enhanced intent detection
            intent, confidence = detect_intent(message.message)
            response_text = get_response_for_intent(intent, user_language)

            # Extract context from current message
            message_context = session_service.extract_context_from_message(message.message, intent)

            # Build contextual response using session memory
            contextual_response = session_service.build_contextual_response(
                response_text, session_data, conversation_history
            )

            # Create structured response
            response = ChatResponse(
                response=contextual_response,
                intent=intent,
                confidence=confidence,
                timestamp=datetime.now().isoformat(),
                buttons=[],
                quick_replies=_get_quick_replies_for_intent(intent, user_language),
                source="enhanced_fallback",
                entities=[],
                session_id=session_id,
                language=user_language
            )
        else:
            # Use RASA response but enhance with session context
            base_response = rasa_response.get("response", "I'm here to help with your health questions!")

            # Extract context from current message
            message_context = session_service.extract_context_from_message(
                message.message, rasa_response.get("intent", "unknown")
            )

            # Build contextual response
            contextual_response = session_service.build_contextual_response(
                base_response, session_data, conversation_history
            )

            response = ChatResponse(
                response=contextual_response,
                intent=rasa_response.get("intent"),
                confidence=rasa_response.get("confidence"),
                timestamp=datetime.now().isoformat(),
                buttons=rasa_response.get("buttons", []),
                quick_replies=rasa_response.get("quick_replies", []),
                source="rasa",
                entities=rasa_response.get("entities", []),
                session_id=session_id,
                language=user_language
            )

        # Save the conversation to history
        await session_service.save_message(
            session_id=session_id,
            message=message.message,
            response=response.response,
            intent=response.intent or "unknown",
            confidence=response.confidence or 0.0,
            language=user_language
        )

        # Update session context if we extracted new information
        message_context = session_service.extract_context_from_message(
            message.message, response.intent or "unknown"
        )
        if message_context:
            await session_service.update_session_context(session_id, message_context)

        logger.info(f"Response generated: intent={response.intent}, confidence={response.confidence}, source={response.source}, language={user_language}")
        return response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        # Emergency fallback response
        session_id = message.session_id or str(uuid.uuid4())
        return ChatResponse(
            response="I'm experiencing technical difficulties. For medical emergencies, please call 108 (India) or 911 (US) immediately. Otherwise, please try rephrasing your question.",
            intent="error",
            confidence=0.0,
            timestamp=datetime.now().isoformat(),
            source="error_fallback",
            quick_replies=["Emergency help", "Find hospital", "Health tips"],
            session_id=session_id,
            language="en"
        )

def _get_quick_replies_for_intent(intent: str, language: str = "en") -> List[str]:
    """Get appropriate quick reply suggestions based on intent and language"""
    quick_replies_multilingual = {
        'en': {
            'greet': ["I have symptoms", "Find hospital", "Vaccine info", "Health tips", "Emergency help"],
            'fever_symptoms': ["How to reduce fever", "When to see doctor", "Emergency signs", "Find hospital"],
            'headache_symptoms': ["Pain relief", "When to worry", "Find doctor", "Emergency help"],
            'cough_symptoms': ["Cough remedies", "When to see doctor", "Find hospital", "Emergency signs"],
            'stomach_symptoms': ["Stomach remedies", "Dehydration signs", "Find doctor", "Emergency help"],
            'find_hospital': ["Emergency numbers", "Nearby clinics", "AIIMS locations", "Private hospitals"],
            'covid_vaccination': ["Book appointment", "Vaccine centers", "Side effects", "Booster info"],
            'medicine_info': ["Drug interactions", "Side effects", "Dosage info", "Consult pharmacist"],
            'health_tips': ["Exercise tips", "Diet advice", "Sleep hygiene", "Stress management"],
            'emergency_help': ["Call 108", "First aid", "Find hospital", "Emergency signs"],
            'general_symptoms': ["Describe symptoms", "Pain scale", "Duration", "Severity"],
            'unknown': ["I have fever", "Find hospital", "Vaccine info", "Health tips", "Emergency help"]
        },
        'hi': {
            'greet': ["मुझे लक्षण हैं", "अस्पताल खोजें", "टीका जानकारी", "स्वास्थ्य सुझाव", "आपातकालीन सहायता"],
            'fever_symptoms': ["बुखार कम करने के तरीके", "डॉक्टर से कब मिलें", "आपातकालीन संकेत", "अस्पताल खोजें"],
            'headache_symptoms': ["दर्द से राहत", "कब चिंता करें", "डॉक्टर खोजें", "आपातकालीन सहायता"],
            'cough_symptoms': ["खांसी के उपाय", "डॉक्टर से कब मिलें", "अस्पताल खोजें", "आपातकालीन संकेत"],
            'stomach_symptoms': ["पेट के उपाय", "निर्जलीकरण के संकेत", "डॉक्टर खोजें", "आपातकालीन सहायता"],
            'find_hospital': ["आपातकालीन नंबर", "पास के क्लिनिक", "एम्स स्थान", "निजी अस्पताल"],
            'covid_vaccination': ["अपॉइंटमेंट बुक करें", "टीकाकरण केंद्र", "साइड इफेक्ट्स", "बूस्टर जानकारी"],
            'medicine_info': ["दवा इंटरैक्शन", "साइड इफेक्ट्स", "डोज़ जानकारी", "फार्मासिस्ट से सलाह"],
            'health_tips': ["व्यायाम सुझाव", "आहार सलाह", "नींद की स्वच्छता", "तनाव प्रबंधन"],
            'emergency_help': ["108 कॉल करें", "प्राथमिक चिकित्सा", "अस्पताल खोजें", "आपातकालीन संकेत"],
            'general_symptoms': ["लक्षण बताएं", "दर्द का स्तर", "अवधि", "गंभीरता"],
            'unknown': ["मुझे बुखार है", "अस्पताल खोजें", "टीका जानकारी", "स्वास्थ्य सुझाव", "आपातकालीन सहायता"]
        },
        'te': {
            'greet': ["నాకు లక్షణాలు ఉన్నాయి", "హాస్పిటల్ కనుగొనండి", "వ్యాక్సిన్ సమాచారం", "ఆరోగ్య చిట్కాలు", "అత్యవసర సహాయం"],
            'fever_symptoms': ["జ్వరం తగ్గించే మార్గాలు", "వైద్యుడిని ఎప్పుడు కలవాలి", "అత్యవసర సంకేతాలు", "హాస్పిటల్ కనుగొనండి"],
            'headache_symptoms': ["నొప్పి ఉపశమనం", "ఎప్పుడు ఆందోళన చెందాలి", "వైద్యుడిని కనుగొనండి", "అత్యవసర సహాయం"],
            'cough_symptoms': ["దగ్గు నివారణలు", "వైద్యుడిని ఎప్పుడు కలవాలి", "హాస్పిటల్ కనుగొనండి", "అత్యవసర సంకేతాలు"],
            'stomach_symptoms': ["కడుపు నివారణలు", "నిర్జలీకరణ సంకేతాలు", "వైద్యుడిని కనుగొనండి", "అత్యవసర సహాయం"],
            'find_hospital': ["అత్యవసర నంబర్లు", "సమీప క్లినిక్లు", "ఎయిమ్స్ స్థానాలు", "ప్రైవేట్ హాస్పిటల్లు"],
            'covid_vaccination': ["అపాయింట్మెంట్ బుక్ చేయండి", "వ్యాక్సిన్ కేంద్రాలు", "దుష్ప్రభావాలు", "బూస్టర్ సమాచారం"],
            'medicine_info': ["మందుల పరస్పర ప్రభావం", "దుష్ప్రభావాలు", "మోతాదు సమాచారం", "ఫార్మాసిస్ట్ సలహా"],
            'health_tips': ["వ్యాయామ చిట్కాలు", "ఆహార సలహా", "నిద్ర పరిశుభ్రత", "ఒత్తిడి నిర్వహణ"],
            'emergency_help': ["108కి కాల్ చేయండి", "ప్రథమ చికిత్స", "హాస్పిటల్ కనుగొనండి", "అత్యవసర సంకేతాలు"],
            'general_symptoms': ["లక్షణాలు వివరించండి", "నొప్పి స్థాయి", "వ్యవధి", "తీవ్రత"],
            'unknown': ["నాకు జ్వరం ఉంది", "హాస్పిటల్ కనుగొనండి", "వ్యాక్సిన్ సమాచారం", "ఆరోగ్య చిట్కాలు", "అత్యవసర సహాయం"]
        },
        'ta': {
            'greet': ["எனக்கு அறிகுறிகள் உள்ளன", "மருத்துவமனையைக் கண்டறியவும்", "தடுப்பூசி தகவல்", "சுகாதார குறிப்புகள்", "அவசர உதவி"],
            'fever_symptoms': ["காய்ச்சலைக் குறைக்கும் வழிகள்", "மருத்துவரை எப்போது பார்க்கவும்", "அவசர அறிகுறிகள்", "மருத்துவமனையைக் கண்டறியவும்"],
            'headache_symptoms': ["வலி நிவாரணம்", "எப்போது கவலைப்பட வேண்டும்", "மருத்துவரைக் கண்டறியவும்", "அவசர உதவி"],
            'cough_symptoms': ["இருமல் தீர்வுகள்", "மருத்துவரை எப்போது பார்க்கவும்", "மருத்துவமனையைக் கண்டறியவும்", "அவசர அறிகுறிகள்"],
            'stomach_symptoms': ["வயிற்று தீர்வுகள்", "நீரிழப்பு அறிகுறிகள்", "மருத்துவரைக் கண்டறியவும்", "அவசர உதவி"],
            'find_hospital': ["அவசர எண்கள்", "அருகிலுள்ள கிளினிக்குகள்", "எய்ம்ஸ் இடங்கள்", "தனியார் மருத்துவமனைகள்"],
            'covid_vaccination': ["சந்திப்பு பதிவு செய்யவும்", "தடுப்பூசி மையங்கள்", "பக்க விளைவுகள்", "பூஸ்டர் தகவல்"],
            'medicine_info': ["மருந்து தொடர்புகள்", "பக்க விளைவுகள்", "அளவு தகவல்", "மருந்தாளர் ஆலோசனை"],
            'health_tips': ["உடற்பயிற்சி குறிப்புகள்", "உணவு ஆலோசனை", "தூக்க சுகாதாரம்", "மன அழுத்த மேலாண்மை"],
            'emergency_help': ["108க்கு அழைக்கவும்", "முதலுதவி", "மருத்துவமனையைக் கண்டறியவும்", "அவசர அறிகுறிகள்"],
            'general_symptoms': ["அறிகுறிகளை விவரிக்கவும்", "வலி அளவு", "கால அளவு", "தீவிரம்"],
            'unknown': ["எனக்கு காய்ச்சல் உள்ளது", "மருத்துவமனையைக் கண்டறியவும்", "தடுப்பூசி தகவல்", "சுகாதார குறிப்புகள்", "அவசர உதவி"]
        },
        'bn': {
            'greet': ["আমার উপসর্গ আছে", "হাসপাতাল খুঁজুন", "টিকার তথ্য", "স্বাস্থ্য টিপস", "জরুরি সাহায্য"],
            'fever_symptoms': ["জ্বর কমানোর উপায়", "কখন ডাক্তার দেখাবেন", "জরুরি লক্ষণ", "হাসপাতাল খুঁজুন"],
            'headache_symptoms': ["ব্যথা উপশম", "কখন চিন্তিত হবেন", "ডাক্তার খুঁজুন", "জরুরি সাহায্য"],
            'cough_symptoms': ["কাশির প্রতিকার", "কখন ডাক্তার দেখাবেন", "হাসপাতাল খুঁজুন", "জরুরি লক্ষণ"],
            'stomach_symptoms': ["পেটের প্রতিকার", "পানিশূন্যতার লক্ষণ", "ডাক্তার খুঁজুন", "জরুরি সাহায্য"],
            'find_hospital': ["জরুরি নম্বর", "কাছের ক্লিনিক", "এইমস অবস্থান", "বেসরকারি হাসপাতাল"],
            'covid_vaccination': ["অ্যাপয়েন্টমেন্ট বুক করুন", "টিকা কেন্দ্র", "পার্শ্ব প্রতিক্রিয়া", "বুস্টার তথ্য"],
            'medicine_info': ["ওষুধের মিথস্ক্রিয়া", "পার্শ্ব প্রতিক্রিয়া", "ডোজ তথ্য", "ফার্মাসিস্ট পরামর্শ"],
            'health_tips': ["ব্যায়াম টিপস", "খাবার পরামর্শ", "ঘুমের স্বাস্থ্যবিধি", "মানসিক চাপ ব্যবস্থাপনা"],
            'emergency_help': ["১০৮ এ কল করুন", "প্রাথমিক চিকিৎসা", "হাসপাতাল খুঁজুন", "জরুরি লক্ষণ"],
            'general_symptoms': ["উপসর্গ বর্ণনা করুন", "ব্যথার মাত্রা", "সময়কাল", "তীব্রতা"],
            'unknown': ["আমার জ্বর আছে", "হাসপাতাল খুঁজুন", "টিকার তথ্য", "স্বাস্থ্য টিপস", "জরুরি সাহায্য"]
        }
    }

    language_replies = quick_replies_multilingual.get(language, quick_replies_multilingual['en'])
    return language_replies.get(intent, language_replies['unknown'])

def get_response_for_intent(intent: str, language: str = "en") -> str:
    """
    Get comprehensive, helpful responses based on detected intent and language
    """
    responses_multilingual = {
        'en': {
            'greet': """Hello! I'm your AI Health Assistant. I can help you with:

🌡️ **Symptom Analysis** - Describe your symptoms for guidance
💉 **Vaccination Information** - COVID, flu, and routine vaccines
🏥 **Find Medical Care** - Locate nearby hospitals and clinics
💊 **Medicine Information** - Drug details and interactions
🚨 **Emergency Guidance** - When and how to seek immediate help
💡 **Health Tips** - Prevention and wellness advice

What can I help you with today?""",

            'fever_symptoms': """**FEVER GUIDANCE**

🌡️ **Normal Response for Fever:**
• **Adults**: Take fever if 100.4°F (38°C) or higher
• **Rest** and stay hydrated with water, clear broths
• **Medications**: Acetaminophen or ibuprofen as directed
• **Cool compresses** on forehead and wrists

⚠️ **Seek Medical Attention If:**
• Fever above 103°F (39.4°C)
• Fever lasts more than 3 days
• Difficulty breathing or chest pain
• Severe headache or neck stiffness

🚨 **Emergency Signs:**
• Temperature above 105°F (40.5°C)
• Seizures
• Difficulty breathing

**Call 108 (India) or 911 (US) for emergencies**""",
        },
        'hi': {
            'greet': """नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं। मैं आपकी मदद कर सकता हूं:

🌡️ **लक्षण विश्लेषण** - मार्गदर्शन के लिए अपने लक्षण बताएं
💉 **टीकाकरण जानकारी** - COVID, फ्लू, और नियमित टीके
🏥 **चिकित्सा देखभाल खोजें** - पास के अस्पताल और क्लिनिक
💊 **दवा की जानकारी** - दवा विवरण और इंटरैक्शन
🚨 **आपातकालीन मार्गदर्शन** - कब और कैसे तत्काल सहायता लें
💡 **स्वास्थ्य सुझाव** - रोकथाम और कल्याण सलाह

आज मैं आपकी कैसे मदद कर सकता हूं?""",

            'fever_symptoms': """**बुखार मार्गदर्शन**

🌡️ **बुखार के लिए सामान्य प्रतिक्रिया:**
• **वयस्क**: 100.4°F (38°C) या उससे अधिक पर बुखार लें
• **आराम करें** और पानी, साफ शोरबा से हाइड्रेटेड रहें
• **दवाएं**: Acetaminophen या ibuprofen जैसा निर्देशित
• माथे और कलाई पर **ठंडी सिकाई**

⚠️ **चिकित्सा सहायता लें यदि:**
• बुखार 103°F (39.4°C) से अधिक हो
• बुखार 3 दिन से अधिक रहे
• सांस लेने में कठिनाई या सीने में दर्द
• गंभीर सिरदर्द या गर्दन में अकड़न

🚨 **आपातकालीन संकेत:**
• तापमान 105°F (40.5°C) से अधिक
• दौरे पड़ना
• सांस लेने में कठिनाई

**आपातकाल के लिए 108 (भारत) पर कॉल करें**""",
        },
        'te': {
            'greet': """నమస్తే! నేను మీ AI ఆరోగ్య సహాయకుడిని। నేను మీకు సహాయం చేయగలను:

🌡️ **లక్షణ విశ్లేషణ** - మార్గదర్శనం కోసం మీ లక్షణాలను వివరించండి
💉 **వ్యాక్సినేషన్ సమాచారం** - COVID, ఫ్లూ, మరియు రొటిన్ వ్యాక్సిన్లు
🏥 **వైద్య సంరక్షణను కనుగొనండి** - సమీప హాస్పిటల్లు మరియు క్లినిక్లు
💊 **మందుల సమాచారం** - మందుల వివరాలు మరియు పరస్పర ప్రభావాలు
🚨 **అత్యవసర మార్గదర్శనం** - ఎప్పుడు మరియు ఎలా తక్షణ సహాయం తీసుకోవాలి
💡 **ఆరోగ్య చిట్కాలు** - నివారణ మరియు సంక్షేమ సలహా

ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?""",

            'fever_symptoms': """**జ్వర మార్గదర్శనం**

🌡️ **జ్వరానికి సాధారణ ప్రతిస్పందన:**
• **పెద్దలు**: 100.4°F (38°C) లేదా అంతకంటే ఎక్కువ ఉంటే జ్వరం తీసుకోండి
• **విశ్రాంతి తీసుకోండి** మరియు నీరు, క్లియర్ బ్రాత్‌తో హైడ్రేటెడ్‌గా ఉండండి
• **మందులు**: సూచించిన విధానం ప్రకారం పారాసిటమాల్ లేదా ఇబుప్రోఫెన్
• నుదిటి మరియు మణికట్టుపై **చల్లని కంప్రెస్‌లు**

⚠️ **వైద్య సహాయం తీసుకోండి:**
• జ్వరం 103°F (39.4°C) కంటే ఎక్కువ ఉంటే
• జ్వరం 3 రోజులకు మించి ఉంటే
• శ్వాస తీసుకోవడంలో కష్టం లేదా ఛాతీ నొప్పి
• తీవ్రమైన తలనొప్పి లేదా మెడ దృఢత్వం

🚨 **అత్యవసర సంకేతాలు:**
• ఉష్ణోగ్రత 105°F (40.5°C) కంటే ఎక్కువ
• మూర్ఛలు
• శ్వాస తీసుకోవడంలో కష్టం

**అవసర పరిస్థితుల కోసం 108కి కాల్ చేయండి**""",
        },
        'ta': {
            'greet': """வணக்கம்! நான் உங்கள் AI சுகாதார உதவியாளர். நான் உங்களுக்கு உதவ முடியும்:

🌡️ **அறிகுறி பகுப்பாய்வு** - வழிகாட்டுதலுக்காக உங்கள் அறிகுறிகளை விவரிக்கவும்
💉 **தடுப்பூசி தகவல்** - COVID, காய்ச்சல், மற்றும் வழக்கமான தடுப்பூசிகள்
🏥 **மருத்துவ பராமரிப்பைக் கண்டறியவும்** - அருகிலுள்ள மருத்துவமனைகள் மற்றும் கிளினிக்குகள்
💊 **மருந்து தகவல்** - மருந்து விவரங்கள் மற்றும் தொடர்புகள்
🚨 **அவசர வழிகாட்டுதல்** - எப்போது மற்றும் எப்படி உடனடி உதவி பெறுவது
💡 **சுகாதார குறிப்புகள்** - தடுப்பு மற்றும் நல்வாழ்வு ஆலோசனை

இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?""",

            'fever_symptoms': """**காய்ச்சல் வழிகாட்டுதல்**

🌡️ **காய்ச்சலுக்கான சாதாரண பதில்:**
• **பெரியவர்கள்**: 100.4°F (38°C) அல்லது அதற்கும் அதிகமாக இருந்தால் காய்ச்சல் எடுக்கவும்
• **ஓய்வு எடுத்துக்கொள்ளுங்கள்** மற்றும் நீர், தெளிவான குழம்புகளுடன் நீரேற்றமாக இருங்கள்
• **மருந்துகள்**: வழிகாட்டியபடி பாராசிடமால் அல்லது இப்யூபுரூஃபென்
• நெற்றி மற்றும் மணிக்கட்டில் **குளிர் கம்ப்ரஸ்கள்**

⚠️ **மருத்துவ உதவி பெறவும்:**
• காய்ச்சல் 103°F (39.4°C) க்கு மேல் இருந்தால்
• காய்ச்சல் 3 நாட்களுக்கு மேல் நீடித்தால்
• மூச்சுத் திணறல் அல்லது மார்பு வலி
• கடுமையான தலைவலி அல்லது கழுத்து விறைப்பு

🚨 **அவசர அறிகுறிகள்:**
• வெப்பநிலை 105°F (40.5°C) க்கு மேல்
• வலிப்புகள்
• மூச்சுத் திணறல்

**அவசரநிலைகளுக்கு 108 க்கு அழைக்கவும்**""",
        },
        'bn': {
            'greet': """নমস্কার! আমি আপনার AI স্বাস্থ্য সহায়ক। আমি আপনাকে সাহায্য করতে পারি:

🌡️ **উপসর্গ বিশ্লেষণ** - নির্দেশনার জন্য আপনার উপসর্গ বর্ণনা করুন
💉 **টিকাদান তথ্য** - COVID, ফ্লু, এবং নিয়মিত টিকা
🏥 **চিকিৎসা সেবা খুঁজুন** - কাছাকাছি হাসপাতাল এবং ক্লিনিক
💊 **ওষুধের তথ্য** - ওষুধের বিবরণ এবং মিথস্ক্রিয়া
🚨 **জরুরি নির্দেশনা** - কখন এবং কীভাবে তাৎক্ষণিক সাহায্য নিতে হবে
💡 **স্বাস্থ্য টিপস** - প্রতিরোধ এবং সুস্থতার পরামর্শ

আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?""",

            'fever_symptoms': """**জ্বরের নির্দেশনা**

🌡️ **জ্বরের জন্য স্বাভাবিক প্রতিক্রিয়া:**
• **প্রাপ্তবয়স্করা**: 100.4°F (38°C) বা তার বেশি হলে জ্বর নিন
• **বিশ্রাম নিন** এবং পানি, পরিষ্কার ঝোল দিয়ে হাইড্রেটেড থাকুন
• **ওষুধ**: নির্দেশানুযায়ী প্যারাসিটামল বা আইবুপ্রফেন
• কপাল এবং কব্জিতে **ঠান্ডা কম্প্রেস**

⚠️ **চিকিৎসা সহায়তা নিন যদি:**
• জ্বর 103°F (39.4°C) এর বেশি হয়
• জ্বর 3 দিনের বেশি থাকে
• শ্বাস নিতে অসুবিধা বা বুকে ব্যথা
• গুরুতর মাথাব্যথা বা ঘাড় শক্ত হওয়া

🚨 **জরুরি লক্ষণ:**
• তাপমাত্রা 105°F (40.5°C) এর বেশি
• খিঁচুনি
• শ্বাস নিতে অসুবিধা

**জরুরি অবস্থার জন্য 108 এ কল করুন**""",
        }
    }

    # Get responses for the specific language, fallback to English if not available
    language_responses = responses_multilingual.get(language, responses_multilingual['en'])

    # Add other intent responses here for all languages
    # For brevity, I'm showing the pattern - you can extend this for all intents
    if intent not in language_responses:
        # Fallback to English if intent not found in the language
        return responses_multilingual['en'].get(intent, responses_multilingual['en'].get('unknown',
            "I'm here to help with your health questions. Please tell me about your symptoms or what you need assistance with."))

    return language_responses[intent]


# Keep existing endpoints but enhance them with RASA integration
@router.get("/symptoms")
async def get_symptom_info(symptom: str, duration: Optional[str] = None, severity: Optional[str] = None):
    """Enhanced symptom endpoint that can work with or without RASA"""
    try:
        # Try to use RASA first for intelligent response
        if rasa_service.is_available:
            message = f"I have {symptom}"
            if duration:
                message += f" for {duration}"
            if severity:
                message += f" and it's {severity}"

            rasa_response = await rasa_service.send_message_to_rasa(message)
            return {
                "symptom": symptom,
                "information": rasa_response.get("response"),
                "source": "rasa",
                "recommendations": rasa_response.get("quick_replies", [])
            }
        else:
            # Fallback to original logic
            return await get_symptom_info_fallback(symptom, duration, severity)

    except Exception as e:
        logger.error(f"Error in symptom endpoint: {e}")
        return await get_symptom_info_fallback(symptom, duration, severity)

async def get_symptom_info_fallback(symptom: str, duration: Optional[str] = None, severity: Optional[str] = None):
    """Fallback symptom information when RASA is not available"""
    symptom_info = {
        "fever": {
            "information": "Fever is a temporary increase in body temperature, often due to an illness.",
            "recommendations": [
                "Rest and drink plenty of fluids",
                "Take paracetamol as directed",
                "Use cool compresses",
                "Seek medical attention if fever exceeds 101°F"
            ]
        },
        "headache": {
            "information": "Headaches can be caused by various factors including stress, dehydration, or underlying conditions.",
            "recommendations": [
                "Rest in a quiet, dark room",
                "Stay hydrated",
                "Apply cold or warm compress",
                "Take over-the-counter pain relief if needed"
            ]
        },
        "cough": {
            "information": "Cough is a common symptom that can be dry or productive, often indicating respiratory issues.",
            "recommendations": [
                "Stay hydrated with warm fluids",
                "Use honey (not for children under 1 year)",
                "Humidify the air",
                "Avoid irritants like smoke"
            ]
        }
    }

    info = symptom_info.get(symptom.lower(), {
        "information": f"Information about {symptom} symptoms.",
        "recommendations": [
            "Monitor your symptoms",
            "Stay hydrated and rest",
            "Consult a healthcare provider if symptoms worsen",
            "Call 108 for emergencies"
        ]
    })

    return {
        "symptom": symptom,
        "information": info["information"],
        "recommendations": info["recommendations"],
        "source": "fallback"
    }

@router.get("/vaccine-schedule")
async def get_vaccine_schedule(age: Optional[str] = None, vaccine_type: Optional[str] = None):
    """Enhanced vaccination endpoint with RASA integration"""
    try:
        if rasa_service.is_available:
            message = f"vaccination information"
            if age:
                message = f"vaccination schedule for age {age}"
            if vaccine_type:
                message += f" {vaccine_type} vaccine"

            rasa_response = await rasa_service.send_message_to_rasa(message)
            return {
                "vaccines": rasa_response.get("response"),
                "source": "rasa"
            }
        else:
            return await get_vaccine_schedule_fallback(age, vaccine_type)

    except Exception as e:
        logger.error(f"Error in vaccine schedule endpoint: {e}")
        return await get_vaccine_schedule_fallback(age, vaccine_type)

async def get_vaccine_schedule_fallback(age: Optional[str] = None, vaccine_type: Optional[str] = None):
    """Fallback vaccination information"""
    if vaccine_type and vaccine_type.lower() in ['covid', 'covid-19']:
        return {
            "vaccines": [
                {
                    "name": "COVID-19 Vaccination",
                    "description": "Register on CoWIN portal at cowin.gov.in. Available vaccines: Covishield, Covaxin. Free at government centers.",
                    "age_group": "18+",
                    "helpline": "1075"
                }
            ],
            "source": "fallback"
        }

    return {
        "vaccines": [
            {
                "name": "General Vaccination Information",
                "description": "Visit CoWIN portal for COVID vaccines. Contact local health center for routine immunization.",
                "helpline": "1075"
            }
        ],
        "source": "fallback"
    }

@router.get("/health-tips")
async def get_health_tips():
    """
    Get general health tips for display in the frontend
    """
    try:
        tips = {
            "daily_tips": [
                "💧 **Stay Hydrated**: Drink 8-10 glasses of water daily",
                "🏃 **Exercise Regularly**: 150 minutes of moderate activity per week",
                "😴 **Get Quality Sleep**: 7-9 hours of sleep for adults",
                "🥗 **Eat Balanced Diet**: Include fruits, vegetables, and whole grains",
                "🧼 **Practice Good Hygiene**: Wash hands frequently for 20 seconds",
                "🧘 **Manage Stress**: Practice meditation or deep breathing exercises",
                "🚭 **Avoid Smoking**: Stay away from tobacco and excessive alcohol"
            ],
            "emergency_numbers": {
                "india": {
                    "medical_emergency": "108",
                    "ambulance": "102",
                    "police": "100",
                    "fire": "101",
                    "health_helpline": "1075"
                },
                "us": {
                    "emergency": "911",
                    "poison_control": "1-800-222-1222"
                }
            },
            "quick_health_checks": [
                "Check your blood pressure regularly",
                "Monitor your weight weekly",
                "Get annual health screenings",
                "Keep track of your medications",
                "Stay up to date with vaccinations"
            ]
        }

        return {
            "status": "success",
            "data": tips,
            "message": "Health tips retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Error getting health tips: {e}")
        return {
            "status": "error",
            "message": "Unable to retrieve health tips",
            "error": str(e)
        }

@router.get("/llm/status")
async def llm_status():
    """Return whether LLM mode is active and model info."""
    return {
        "mode": "llm" if settings.use_llm else "rasa",
        "use_llm": settings.use_llm,
        "model": settings.ollama_model if settings.use_llm else None,
        "base_url": settings.ollama_base_url if settings.use_llm else None
    }

# --- Local intent detection helpers (mirrors SMS/WhatsApp simple heuristic) ---
def detect_intent(message: str) -> tuple[str, float]:
    """Lightweight heuristic intent detection used ONLY when RASA unavailable.
    Returns (intent_name, confidence).
    """
    msg = message.lower().strip()

    fever_keywords = ['fever', 'temperature', 'hot', 'chills', 'शिवर', 'बुखार', 'জ্বর', 'జ్వరం', 'காய்ச்சல்']
    if any(k in msg for k in fever_keywords):
        return ('fever_symptoms', 0.9)

    headache_keywords = ['headache', 'head pain', 'migraine', 'सिर', '头痛', 'মাথা', 'head hurts']
    if any(k in msg for k in headache_keywords):
        return ('headache_symptoms', 0.85)

    cough_keywords = ['cough', 'throat', 'sore throat', 'खांसी', 'কাশি', 'దగ్గు']
    if any(k in msg for k in cough_keywords):
        return ('cough_symptoms', 0.85)

    stomach_keywords = ['stomach', 'nausea', 'vomit', 'vomiting', 'diarrhea', 'abdomen', 'abdominal', 'belly', 'tummy', 'पेट', 'उल्टी']
    if any(k in msg for k in stomach_keywords):
        return ('stomach_symptoms', 0.85)

    hospital_keywords = ['hospital', 'clinic', 'doctor', 'medical center', 'emergency room', 'find hospital', 'अस्पताल']
    if any(k in msg for k in hospital_keywords):
        return ('find_hospital', 0.8)

    emergency_keywords = ['emergency', 'urgent', 'critical', 'ambulance', 'heart attack', 'stroke', 'unconscious', 'help now']
    if any(k in msg for k in emergency_keywords):
        return ('emergency_help', 0.9)

    greet_keywords = ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste', 'नमस्ते', 'hola', 'bonjour']
    if any(k in msg for k in greet_keywords):
        return ('greet', 0.7)

    vaccine_keywords = ['vaccine', 'vaccination', 'टीका', 'dose', 'booster', 'covid shot']
    if any(k in msg for k in vaccine_keywords):
        return ('covid_vaccination', 0.8)

    return ('unknown', 0.2)

# NOTE: get_response_for_intent already declared above (partial multilingual). Fallback mapping handled there.
