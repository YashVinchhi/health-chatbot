"""
RASA Integration Service for Health Chatbot
Handles communication with RASA server for intelligent response generation
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class RASAService:
    def __init__(self):
        self.rasa_url = os.getenv("RASA_URL", "http://localhost:5005")
        self.session = None

    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def send_message_to_rasa(self, message: str, sender_id: str = "user") -> Dict[str, Any]:
        """
        Send message to RASA and get response

        Args:
            message: User's message
            sender_id: Unique identifier for the user session

        Returns:
            Dictionary containing RASA response
        """
        try:
            session = await self.get_session()

            # RASA webhook endpoint
            url = f"{self.rasa_url}/webhooks/rest/webhook"

            payload = {
                "sender": sender_id,
                "message": message
            }

            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    rasa_response = await response.json()
                    logger.info(f"RASA response received for message: {message[:50]}...")
                    return self._format_rasa_response(rasa_response, message)
                else:
                    logger.error(f"RASA server error: {response.status}")
                    return self._fallback_response(message)

        except aiohttp.ClientError as e:
            logger.error(f"Connection error to RASA server: {e}")
            return self._fallback_response(message)
        except Exception as e:
            logger.error(f"Unexpected error in RASA communication: {e}")
            return self._fallback_response(message)

    def _format_rasa_response(self, rasa_response: List[Dict], original_message: str) -> Dict[str, Any]:
        """
        Format RASA response for frontend

        Args:
            rasa_response: Raw response from RASA
            original_message: Original user message

        Returns:
            Formatted response dictionary
        """
        if not rasa_response:
            return self._fallback_response(original_message)

        # Combine all text responses from RASA
        responses = []
        buttons = []
        quick_replies = []

        for item in rasa_response:
            if item.get("text"):
                responses.append(item["text"])

            # Handle buttons if present
            if item.get("buttons"):
                buttons.extend(item["buttons"])

            # Handle quick replies if present
            if item.get("quick_replies"):
                quick_replies.extend(item["quick_replies"])

        # Join all text responses
        final_response = "\n\n".join(responses) if responses else self._get_default_response(original_message)

        return {
            "response": final_response,
            "sender": "bot",
            "timestamp": datetime.now().isoformat(),
            "buttons": buttons,
            "quick_replies": quick_replies,
            "source": "rasa"
        }

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """
        Fallback response when RASA is unavailable

        Args:
            message: Original user message

        Returns:
            Fallback response dictionary
        """
        fallback_text = self._get_default_response(message)

        return {
            "response": fallback_text,
            "sender": "bot",
            "timestamp": datetime.now().isoformat(),
            "buttons": [],
            "quick_replies": [],
            "source": "fallback"
        }

    def _get_default_response(self, message: str) -> str:
        """
        Generate basic response based on message content

        Args:
            message: User message

        Returns:
            Default response string
        """
        message_lower = message.lower()

        # Basic pattern matching for fallback
        if any(word in message_lower for word in ["hello", "hi", "hey", "greet"]):
            return "Hello! I'm your health assistant. How can I help you today? 🏥"

        elif any(word in message_lower for word in ["bye", "goodbye", "exit"]):
            return "Goodbye! Take care of your health. Feel free to reach out anytime! 👋"

        elif any(word in message_lower for word in ["fever", "sick", "pain", "hurt", "symptoms"]):
            return """I understand you're experiencing health concerns. Here's what I recommend:

🏥 **Immediate Steps:**
• Monitor your symptoms carefully
• Stay hydrated and get rest  
• Take your temperature if possible
• Seek medical attention if symptoms worsen

⚠️ **Seek immediate medical help if you experience:**
• Severe chest pain or difficulty breathing
• High fever (over 103°F/39.4°C)
• Severe abdominal pain
• Signs of dehydration

For personalized medical advice, please consult with a healthcare professional."""

        elif any(word in message_lower for word in ["vaccine", "vaccination", "immunization"]):
            return """💉 **Vaccination Information:**

**Currently Recommended:**
• COVID-19 vaccines and boosters
• Annual influenza (flu) shots
• Routine adult/childhood immunizations

**For specific vaccine schedules:**
• Consult your healthcare provider
• Check with local health department
• Visit CDC or WHO websites for guidelines

Always discuss vaccination with your healthcare professional for personalized recommendations."""

        elif any(word in message_lower for word in ["emergency", "urgent", "help", "911", "ambulance"]):
            return """🚨 **EMERGENCY INFORMATION:**

**Call Emergency Services Immediately:**
• US: 911
• India: 108  
• UK: 999
• Australia: 000

**Emergency Signs:**
• Chest pain or pressure
• Difficulty breathing
• Severe bleeding
• Loss of consciousness
• Severe allergic reactions

**For non-emergency urgent care:**
• Contact your healthcare provider
• Visit urgent care center
• Use telehealth services

Don't delay seeking help for serious symptoms!"""

        else:
            return """I'm here to help with your health questions! I can assist with:

🩺 **Symptom guidance** - General information about health concerns
💉 **Vaccination info** - Current vaccine recommendations  
🚨 **Emergency guidance** - When to seek immediate care
🏥 **Health tips** - Wellness and prevention advice

⚠️ **Important:** I provide general information only. For medical advice, diagnosis, or treatment, please consult qualified healthcare professionals.

What would you like to know about your health?"""

    async def get_rasa_status(self) -> Dict[str, Any]:
        """
        Check RASA server status

        Returns:
            Status information dictionary
        """
        try:
            session = await self.get_session()
            url = f"{self.rasa_url}/status"

            async with session.get(url) as response:
                if response.status == 200:
                    status_data = await response.json()
                    return {
                        "status": "online",
                        "details": status_data
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"RASA server responded with status {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error checking RASA status: {e}")
            return {
                "status": "offline",
                "message": str(e)
            }

# Global RASA service instance
rasa_service = RASAService()
