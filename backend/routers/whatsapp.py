from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import logging
import json
from typing import Dict, Any
from ..services.health_data_service import health_data_service
from ..services.india_health_service import india_health_service
from ..config import settings
from ..routers.health_api import detect_intent, get_response_for_intent
import httpx

logger = logging.getLogger(__name__)

router = APIRouter()

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
