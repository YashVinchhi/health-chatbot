from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import Response
from pydantic import BaseModel
import logging
from typing import Dict, Any
from ..services.health_data_service import health_data_service
from ..services.india_health_service import india_health_service
from ..config import settings
from ..routers.health_api import detect_intent, get_response_for_intent
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

class SMSMessage(BaseModel):
    to: str
    message: str

class SMSResponse(BaseModel):
    success: bool
    message: str
    sid: str = None

@router.post("/webhook")
async def sms_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...)
):
    """
    Handle incoming SMS messages via Twilio webhook
    """
    try:
        logger.info(f"Received SMS from {From}: {Body}")

        # Process the health-related message
        response_text = await process_health_sms(Body)

        # Create TwiML response
        resp = MessagingResponse()
        resp.message(response_text)

        return Response(content=str(resp), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        # Return empty TwiML response to avoid Twilio retries
        resp = MessagingResponse()
        return Response(content=str(resp), media_type="application/xml")

async def process_health_sms(message: str) -> str:
    """Process health-related SMS and return appropriate response"""
    try:
        # Use the same intent detection from health_api
        intent, confidence = detect_intent(message)

        # Get response based on intent
        if intent == 'unknown':
            response = "Health Assistant: I can help with symptoms, vaccines, outbreaks, emergencies & health tips. What would you like to know?"
        else:
            response = get_response_for_intent(intent)

        # Truncate for SMS (160 character limit consideration)
        if len(response) > 1500:  # Leave room for multiple SMS parts
            response = response[:1497] + "..."

        # Add SMS-specific footer
        response += "\n\nText STOP to unsubscribe. Emergency? Call 911/108"

        return response

    except Exception as e:
        logger.error(f"Error processing health SMS: {e}")
        return "Health Assistant: Service temporarily unavailable. For emergencies, call 911 (US) or 108 (India)."

@router.post("/send-sms")
async def send_sms(sms_data: SMSMessage) -> SMSResponse:
    """
    Send SMS message via Twilio
    """
    try:
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise HTTPException(status_code=500, detail="Twilio credentials not configured")

        # Initialize Twilio client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        # Send SMS
        message = client.messages.create(
            body=sms_data.message,
            from_=settings.twilio_phone_number,
            to=sms_data.to
        )

        logger.info(f"SMS sent successfully to {sms_data.to}, SID: {message.sid}")

        return SMSResponse(
            success=True,
            message="SMS sent successfully",
            sid=message.sid
        )

    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")

@router.post("/send-health-alert")
async def send_health_alert(phone_number: str, alert_type: str = "general"):
    """
    Send health alerts via SMS
    """
    try:
        # Get appropriate health alert based on type
        if alert_type == "outbreak":
            outbreak_data = await health_data_service.get_covid_data("all")
            if outbreak_data["success"]:
                message = f"Health Alert: COVID-19 Update - Active cases: {outbreak_data['data']['active']:,}. Stay safe, follow guidelines."
            else:
                message = "Health Alert: Stay updated on health guidelines. Wash hands, wear masks when needed."
        elif alert_type == "vaccination":
            message = "Health Reminder: Ensure you're up to date with vaccinations. COVID-19 boosters and annual flu shots recommended."
        elif alert_type == "emergency":
            message = "HEALTH EMERGENCY ALERT: If this is a medical emergency, call 911 (US) or 108 (India) immediately. Do not rely on SMS for emergency care."
        else:
            message = "Health Tip: Stay hydrated, eat balanced meals, exercise regularly, and get adequate sleep for optimal health."

        # Send the SMS
        sms_response = await send_sms(SMSMessage(to=phone_number, message=message))

        return {
            "alert_sent": True,
            "alert_type": alert_type,
            "recipient": phone_number,
            "sms_response": sms_response
        }

    except Exception as e:
        logger.error(f"Error sending health alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to send health alert")

@router.get("/status")
async def sms_status():
    """
    Check SMS gateway status and Twilio configuration
    """
    try:
        config_status = {
            "twilio_account_sid_configured": bool(settings.twilio_account_sid),
            "twilio_auth_token_configured": bool(settings.twilio_auth_token),
            "twilio_phone_number_configured": bool(settings.twilio_phone_number),
            "status": "configured" if all([
                settings.twilio_account_sid,
                settings.twilio_auth_token,
                settings.twilio_phone_number
            ]) else "not_configured"
        }

        # Test Twilio connection if configured
        if config_status["status"] == "configured":
            try:
                client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                # Test API access (this will raise exception if credentials are invalid)
                account = client.api.accounts(settings.twilio_account_sid).fetch()
                config_status["twilio_connection"] = "active"
                config_status["account_status"] = account.status
            except Exception as e:
                logger.error(f"Twilio connection test failed: {e}")
                config_status["twilio_connection"] = "failed"
                config_status["error"] = str(e)

        return {
            "status": "active" if config_status["status"] == "configured" else "needs_configuration",
            "configuration": config_status,
            "message": "SMS service is ready" if config_status["status"] == "configured" else "SMS service needs Twilio configuration"
        }

    except Exception as e:
        logger.error(f"Error checking SMS status: {e}")
        raise HTTPException(status_code=500, detail="Error checking SMS status")

@router.get("/health-alerts-templates")
async def get_health_alert_templates():
    """
    Get SMS templates for health alerts
    """
    try:
        templates = {
            "outbreak_alert": "🚨 Health Alert: {disease} outbreak reported in {location}. Cases: {cases}. Follow safety guidelines.",
            "vaccination_reminder": "💉 Vaccination Reminder: {vaccine} due. Schedule appointment at your healthcare provider.",
            "weather_health": "🌡️ Weather Health Advisory: {condition}. Take precautions: {advice}",
            "emergency_info": "🚨 Emergency: For immediate help call 911 (US) or 108 (India). This is an automated message.",
            "health_tip": "💡 Health Tip: {tip}. Stay healthy!",
            "medication_reminder": "💊 Medication Reminder: Time for {medication}. Take as prescribed."
        }

        return {
            "templates": templates,
            "usage": "Use these templates for consistent health messaging via SMS",
            "character_limits": {
                "single_sms": 160,
                "recommended_max": 1500
            }
        }

    except Exception as e:
        logger.error(f"Error getting SMS templates: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving SMS templates")
