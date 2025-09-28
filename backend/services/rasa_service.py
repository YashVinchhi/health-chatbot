"""
RASA Integration Service for Health Chatbot
Enhanced with multi-port probing, retry logic, and adaptive URL selection.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class RASAService:
    def __init__(self):
        # Primary URL from env
        self.rasa_url = os.getenv("RASA_URL", "http://localhost:5005").rstrip("/")
        # Candidate fallback URLs (include historical port 5775 if earlier used)
        extra = os.getenv("RASA_URL_CANDIDATES", "")
        self.candidate_urls = [self.rasa_url, "http://localhost:5775", "http://127.0.0.1:5005", "http://127.0.0.1:5775"]
        if extra:
            self.candidate_urls.extend([u.strip().rstrip("/") for u in extra.split(",") if u.strip()])
        # De-duplicate preserving order
        seen = set()
        self.candidate_urls = [u for u in self.candidate_urls if not (u in seen or seen.add(u))]
        self.active_rasa_url: Optional[str] = None
        self.rasa_actions_url = os.getenv("RASA_ACTIONS_URL", "http://localhost:5055").rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_available: bool = False
        self.last_status: Dict[str, Any] = {}

    async def get_session(self):
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=20)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def _probe_single(self, base_url: str) -> Optional[Dict[str, Any]]:
        """Try a single base URL, return status dict or None."""
        try:
            session = await self.get_session()
            async with session.get(f"{base_url}/status") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"ok": True, "base_url": base_url, **data}
                else:
                    logger.debug(f"RASA probe {base_url} returned HTTP {resp.status}")
        except Exception as e:
            logger.debug(f"RASA probe failed for {base_url}: {e}")
        return None

    async def _select_active_url(self) -> Optional[str]:
        for url in self.candidate_urls:
            result = await self._probe_single(url)
            if result and result.get("ok"):
                self.active_rasa_url = url
                self.last_status = result
                logger.info(f"RASA reachable at {url}")
                return url
        logger.warning("No reachable RASA base URL found from candidates: %s", self.candidate_urls)
        return None

    async def check_rasa_status(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Check or refresh RASA status with adaptive probing."""
        if not force_refresh and self.is_available and self.active_rasa_url:
            # Light ping
            try:
                session = await self.get_session()
                async with session.get(f"{self.active_rasa_url}/status") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.last_status.update(data)
                        return {"status": "online", **self.last_status}
            except Exception:
                logger.debug("Light ping failed, forcing full probe")

        # Full probe
        chosen = await self._select_active_url()
        if chosen:
            # Actions server optional
            actions_ok = False
            try:
                session = await self.get_session()
                async with session.get(f"{self.rasa_actions_url}/health") as aresp:
                    actions_ok = aresp.status == 200
            except Exception:
                actions_ok = False
            self.is_available = True
            return {
                "status": "online",
                "rasa_server": True,
                "actions_server": actions_ok,
                "model_loaded": bool(self.last_status.get("model_file")),
                "model_file": self.last_status.get("model_file"),
                "version": self.last_status.get("version"),
                "base_url": chosen,
                "candidates": self.candidate_urls
            }
        else:
            self.is_available = False
            return {"status": "offline", "tried": self.candidate_urls}

    async def send_message_to_rasa(self, message: str, sender_id: str = "user", conversation_history: List[Dict] = None) -> Dict[str, Any]:
        # Ensure we have an active URL
        if not self.active_rasa_url:
            await self.check_rasa_status(force_refresh=True)
        if not self.active_rasa_url:
            logger.warning("Falling back: No active RASA URL after probing")
            return await self._fallback_response(message, "no_connection")

        payload = {"sender": sender_id, "message": message}
        if conversation_history:
            payload["metadata"] = {"conversation_history": conversation_history[-3:]}

        session = await self.get_session()
        url = f"{self.active_rasa_url}/webhooks/rest/webhook"

        # Retry strategy
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        responses = await resp.json()
                        if responses:
                            return await self._process_rasa_response(responses, message, sender_id)
                        logger.debug("Empty RASA webhook response, using fallback")
                        return await self._fallback_response(message, "empty")
                    elif resp.status == 404:
                        logger.debug(f"RASA webhook 404 (attempt {attempt}) re-probing")
                        # Possibly wrong endpoint, force re-probe once
                        if attempt == 1:
                            self.active_rasa_url = None
                            await self.check_rasa_status(force_refresh=True)
                            if not self.active_rasa_url:
                                break
                            url = f"{self.active_rasa_url}/webhooks/rest/webhook"
                        else:
                            break
                    else:
                        logger.warning(f"RASA HTTP {resp.status} attempt {attempt}/{attempts}")
            except Exception as e:
                logger.debug(f"RASA send attempt {attempt} failed: {e}")
                if attempt == attempts:
                    logger.warning("Falling back after maximum retry attempts")
                    return await self._fallback_response(message, "exception")
                # Re-probe before next attempt
                self.active_rasa_url = None
                await asyncio.sleep(0.5 * attempt)
                await self.check_rasa_status(force_refresh=True)
                if not self.active_rasa_url:
                    logger.warning("Falling back: RASA offline after retry probe")
                    return await self._fallback_response(message, "offline")
                url = f"{self.active_rasa_url}/webhooks/rest/webhook"
        return await self._fallback_response(message, "unreachable")

    async def _process_rasa_response(self, rasa_responses: List[Dict], original_message: str, sender_id: str) -> Dict[str, Any]:
        """Process and enhance RASA responses (fixed signature to include sender_id)"""
        response_text = ""
        buttons: List[Dict[str, Any]] = []
        quick_replies: List[str] = []
        for response in rasa_responses:
            if "text" in response:
                # Ensure newline separation without duplication
                if response_text:
                    response_text += "\n"
                response_text += response["text"].strip()
            if "buttons" in response:
                buttons.extend(response["buttons"])
            if "quick_replies" in response:
                quick_replies.extend([qr.get("title", qr) for qr in response["quick_replies"]])
        intent_info = await self._get_intent_info(original_message)
        logger.debug(f"RASA intent parse: {intent_info}")
        return {
            "response": response_text or "I'm here to help with your health questions!",
            "intent": intent_info.get("intent", {}).get("name", "unknown"),
            "confidence": intent_info.get("intent", {}).get("confidence", 0.0),
            "entities": intent_info.get("entities", []),
            "buttons": buttons,
            "quick_replies": quick_replies,
            "source": "rasa",
            "timestamp": datetime.now().isoformat()
        }

    async def _get_intent_info(self, message: str, sender_id: str = "user") -> Dict[str, Any]:
        """Parse intent using the ACTIVE RASA URL (not the original env URL)"""
        base = self.active_rasa_url or self.rasa_url
        try:
            session = await self.get_session()
            async with session.post(f"{base}/model/parse", json={"text": message}) as response:
                if response.status == 200:
                    return await response.json()
                logger.debug(f"Intent parse HTTP {response.status} at {base}")
                return {}
        except Exception as e:
            logger.error(f"Error getting intent info from {base}: {e}")
            return {}

    async def _fallback_response(self, message: str, error_type: str = "connection") -> Dict[str, Any]:
        """Generate fallback response when RASA is unavailable"""
        message_lower = message.lower()
        logger.debug(f"Generating fallback response (reason={error_type}) for message='{message_lower[:60]}'")

        # Basic pattern matching for common health queries
        if any(word in message_lower for word in ['fever', 'बुखार', 'జ్వరం', 'காய்ச்சல்', 'জ্বর']):
            response = """🌡️ **Fever Management:**\n• Rest and drink plenty of fluids\n• Take paracetamol as per package instructions\n• Use cool compresses\n• Consult doctor if fever >101°F or lasts >3 days\n• Emergency: Call 108 if fever >104°F"""

        elif any(word in message_lower for word in ['hospital', 'अस्पताल', 'హాస్పిటల్', 'மருத்துவமனை', 'হাসপাতাল']):
            response = """🏥 **Find Hospitals:**\n• Call 108 for emergency ambulance\n• Visit nearest district hospital or PHC\n• Use Google Maps for "hospitals near me"\n• Government hospitals: Free treatment available\n• Emergency: 108 | Health Helpline: 1075"""

        elif any(word in message_lower for word in ['vaccine', 'vaccination', 'टीका', 'టీకా', 'தடுப்பூசி', 'টিকা']):
            response = """💉 **Vaccination Information:**\n• COVID-19: Register on CoWIN portal (cowin.gov.in)\n• Call 1075 for vaccination helpline\n• Visit nearest government health center\n• Carry ID proof for vaccination\n• Free vaccines available at government centers"""

        elif any(word in message_lower for word in ['emergency', 'help', 'urgent', 'आपातकाल', 'అత్యవసరం', 'அவசரம்', 'জরুরি']):
            response = """🚨 **EMERGENCY CONTACTS:**\n• Medical Emergency: 108\n• Ambulance: 102\n• Police: 100\n• Fire: 101\n• Health Helpline: 1075\n• Women Helpline: 1091\n\n**For immediate life-threatening situations, call 108 NOW!**"""

        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'नमस्ते', 'హలో', 'வணக்கம்', 'হ্যালো']):
            response = """👋 **Hello! I'm your Health Assistant**\n\nI can help you with:\n• 🩺 Symptom guidance\n• 💉 Vaccination information  \n• 🏥 Find hospitals\n• 🚨 Emergency contacts\n• 💊 Medicine information\n\nWhat health information do you need today?"""

        else:
            response = """I'm your health assistant! I can help with:\n\n• **Symptoms**: "I have fever" or "मुझे बुखार है"\n• **Hospitals**: "Find hospitals near me" \n• **Vaccines**: "COVID vaccine information"\n• **Emergency**: "Emergency help needed"\n• **Medicine**: "Paracetamol information"\n\n**Emergency: Call 108 for immediate medical help**"""

        return {
            "response": response,
            "intent": "fallback",
            "confidence": 0.0,  # Distinguish clearly from real intent predictions
            "source": f"fallback_{error_type}",
            "timestamp": datetime.now().isoformat(),
            "buttons": [],
            "quick_replies": ["Find Hospitals", "Vaccination Info", "Emergency Help", "Symptom Guidance"]
        }

    async def get_conversation_history(self, sender_id: str) -> Dict[str, Any]:
        """Get conversation history for a user"""
        try:
            session = await self.get_session()
            url = f"{self.rasa_url}/conversations/{sender_id}/tracker"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {"events": []}
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return {"events": []}

    async def train_model(self, training_data_path: str = None) -> Dict[str, Any]:
        """Trigger model training (useful for updates)"""
        try:
            session = await self.get_session()
            url = f"{self.rasa_url}/model/train"
            payload = {}
            if training_data_path:
                payload["training_data"] = training_data_path
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"status": "success", "result": result}
                return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {"status": "error", "message": str(e)}

# Create global instance
rasa_service = RASAService()
