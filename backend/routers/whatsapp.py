from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import logging
import json
from typing import Dict, Any
from services.health_data_service import health_data_service
from services.india_health_service import india_health_service
from services.session_service import session_service
from config import settings
import httpx
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

# Import the functions directly from health_api module
def detect_intent(message: str) -> tuple[str, float]:
    """
    Enhanced intent detection with specific health analysis
    Returns (intent, confidence)
    """
    message_lower = message.lower()

    # Specific symptom analysis
    fever_keywords = ['fever', 'temperature', 'hot', 'burning up', 'chills', 'shivering']
    if any(keyword in message_lower for keyword in fever_keywords):
        return ('fever_symptoms', 0.9)

    headache_keywords = ['headache', 'head pain', 'migraine', 'head hurts', 'head ache']
    if any(keyword in message_lower for keyword in headache_keywords):
        return ('headache_symptoms', 0.9)

    cough_keywords = ['cough', 'coughing', 'throat', 'sore throat', 'dry cough', 'wet cough']
    if any(keyword in message_lower for keyword in cough_keywords):
        return ('cough_symptoms', 0.9)

    stomach_keywords = ['stomach', 'nausea', 'vomiting', 'diarrhea', 'abdominal', 'belly', 'tummy']
    if any(keyword in message_lower for keyword in stomach_keywords):
        return ('stomach_symptoms', 0.9)

    # Hospital/medical facility search
    hospital_keywords = ['hospital', 'clinic', 'doctor', 'medical center', 'emergency room', 'find hospital']
    if any(keyword in message_lower for keyword in hospital_keywords):
        return ('find_hospital', 0.8)

    # Emergency situations
    emergency_keywords = ['emergency', 'urgent', 'critical', 'ambulance', 'heart attack', 'stroke', 'unconscious']
    if any(keyword in message_lower for keyword in emergency_keywords):
        return ('emergency_help', 0.9)

    # Greeting detection
    greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste', 'start', 'begin']
    if any(keyword in message_lower for keyword in greeting_keywords):
        return ('greet', 0.7)

    return ('unknown', 0.3)

def get_response_for_intent(intent: str, language: str = "en") -> str:
    """
    Get comprehensive, helpful responses based on detected intent and language
    """
    # Basic responses - this can be expanded with full multilingual support
    responses = {
        'greet': "Hello! I'm your health assistant. How can I help you today?",
        'fever_symptoms': "For fever management: Rest, stay hydrated, take paracetamol as directed. Seek medical help if fever is above 103°F or lasts more than 3 days. Emergency: Call 108.",
        'headache_symptoms': "For headaches: Rest in a quiet room, stay hydrated, apply cold/warm compress. Take over-the-counter pain relief if needed. See a doctor for severe or persistent headaches.",
        'emergency_help': "🚨 EMERGENCY: Call 108 (India) immediately for medical emergencies. For immediate help: Medical Emergency: 108, Ambulance: 102, Police: 100",
        'find_hospital': "To find hospitals: Call 108 for emergency, use Google Maps for 'hospitals near me', or visit your nearest district hospital/PHC for treatment.",
        'unknown': "I can help with health questions. Try asking about symptoms, finding hospitals, or emergency help."
    }

    return responses.get(intent, responses['unknown'])

class WhatsAppMessage(BaseModel):
    from_number: str
    message_body: str
    message_id: str

class WhatsAppResponse(BaseModel):
    success: bool
    message: str

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp messages via webhook (Meta WhatsApp Business API)
    """
    try:
        data = await request.json()

        # Validate webhook signature if configured
        if settings.whatsapp_token:
            # In production, validate the webhook signature here
            pass

        # Extract message data from Meta WhatsApp webhook format
        if "messages" in data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
            messages = data["entry"][0]["changes"][0]["value"]["messages"]

            for message in messages:
                from_number = message["from"]
                message_body = message.get("text", {}).get("body", "")
                message_id = message["id"]

                # Process the health-related message
                response_text = await process_health_message(message_body)

                # Send response back via WhatsApp
                await send_whatsapp_message(from_number, response_text)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail="Error processing WhatsApp message")

@router.get("/webhook")
async def whatsapp_webhook_verification(request: Request):
    """
    Verify WhatsApp webhook (required by Meta)
    """
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if mode == "subscribe" and token == settings.whatsapp_token:
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")

    except Exception as e:
        logger.error(f"Error verifying WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

async def process_health_message(message: str) -> str:
    """Process health-related message and return appropriate response"""
    try:
        # Use the same intent detection from health_api
        intent, confidence = detect_intent(message)

        # Get response based on intent
        if intent == 'unknown':
            response = "I'm here to help with your health questions! You can ask me about:\n• Symptoms and health concerns\n• Vaccination information\n• Disease outbreaks\n• Emergency contacts\n• General health tips"
        else:
            response = get_response_for_intent(intent)

        # Add WhatsApp-specific formatting
        response += "\n\n📱 Reply to continue our conversation or type 'emergency' for urgent help."

        return response

    except Exception as e:
        logger.error(f"Error processing health message: {e}")
        return "I'm having trouble processing your message right now. For urgent health matters, please contact emergency services."

async def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Send message via WhatsApp Business API"""
    try:
        if not settings.whatsapp_phone_number_id or not settings.whatsapp_token:
            logger.warning("WhatsApp credentials not configured")
            return False

        url = f"https://graph.facebook.com/v17.0/{settings.whatsapp_phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "text": {"body": message}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            logger.info(f"WhatsApp message sent successfully to {to_number}")
            return True
        else:
            logger.error(f"Failed to send WhatsApp message: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False

@router.post("/send-message")
async def send_message(message_data: WhatsAppMessage) -> WhatsAppResponse:
    """
    Send a message via WhatsApp (for testing or admin use)
    """
    try:
        success = await send_whatsapp_message(
            message_data.from_number,
            message_data.message_body
        )

        return WhatsAppResponse(
            success=success,
            message="Message sent successfully" if success else "Failed to send message"
        )

    except Exception as e:
        logger.error(f"Error in send_message endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error sending message")

@router.get("/status")
async def whatsapp_status():
    """
    Check WhatsApp connection status and configuration
    """
    try:
        config_status = {
            "whatsapp_token_configured": bool(settings.whatsapp_token),
            "phone_number_id_configured": bool(settings.whatsapp_phone_number_id),
            "status": "configured" if (settings.whatsapp_token and settings.whatsapp_phone_number_id) else "not_configured"
        }

        return {
            "status": "active",
            "configuration": config_status,
            "message": "WhatsApp integration is ready" if config_status["status"] == "configured" else "WhatsApp needs configuration"
        }

    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {e}")
        raise HTTPException(status_code=500, detail="Error checking status")

@router.get("/health-tips")
async def get_whatsapp_health_tips():
    """
    Get formatted health tips for WhatsApp sharing
    """
    try:
        tips = [
            "💧 *Stay Hydrated*\nDrink 8-10 glasses of water daily",
            "🏃 *Exercise Regularly*\n150 minutes of moderate activity per week",
            "😴 *Get Quality Sleep*\n7-9 hours of sleep for adults",
            "🥗 *Eat Balanced Diet*\nInclude fruits, vegetables, and whole grains",
            "🧼 *Practice Good Hygiene*\nWash hands frequently for 20 seconds"
        ]

        return {
            "tips": tips,
            "format": "whatsapp_ready",
            "usage": "Send these tips via WhatsApp to promote health awareness"
        }

    except Exception as e:
        logger.error(f"Error getting health tips: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving health tips")
