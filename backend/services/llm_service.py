import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a multilingual Indian Health Assistant. Provide concise, factual, non-diagnostic guidance. "
    "ALWAYS respond with a JSON object with keys: intent (string), confidence (0-1 float), entities (list), answer (markdown string). "
    "Entities list items should have keys: type, value. If uncertain, intent='unknown' and confidence<=0.3."
)

INTENT_GUIDANCE = (
    "Typical intents: greet, ask_symptoms, ask_vaccination, ask_outbreak_info, ask_emergency, ask_general_health, "
    "ask_medication, ask_hospitals, ask_location, ask_cost, ask_prevention, ask_exercise, ask_diet, ask_mental_health, "
    "ask_medicine_info, ask_hospital_info, ask_health_scheme, emergency_help, thank, out_of_scope."
)

EXTRA_RULES = (
    "Never fabricate emergency instructions. For emergencies instruct to call 108 (India). "
    "Do not provide diagnosis. Suggest consulting a doctor for specific medical concerns."
)

DEFAULT_RESPONSE = {
    "intent": "unknown",
    "confidence": 0.0,
    "entities": [],
    "answer": "I'm your health assistant. Please describe your health question, symptoms, vaccination info, or hospital needs. For emergencies call 108."}

class OllamaLLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip('/')
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout

    async def generate(self, message: str, session_id: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a response using Ollama local model.
        History: list of previous messages (we only include last few to keep prompt small)."""
        # Build conversation context (take last 6 exchanges)
        recent = history[-6:] if history else []
        history_lines = []
        for item in recent:
            role = 'User' if item.get('sender') == 'user' else 'Assistant'
            history_lines.append(f"{role}: {item.get('message') or item.get('response')}")
        history_block = '\n'.join(history_lines)

        prompt = (
            f"{SYSTEM_PROMPT}\n{INTENT_GUIDANCE}\n{EXTRA_RULES}\n"\
            f"Conversation History (most recent last):\n{history_block}\n---\n"\
            f"User: {message}\n"\
            "Respond ONLY with compact JSON (no backticks). Example: {\"intent\":\"greet\",\"confidence\":0.92,\"entities\":[],\"answer\":\"Hello! ...\"}"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code != 200:
                    logger.warning(f"Ollama non-200 status: {resp.status_code} body={resp.text[:200]}")
                    return self._fallback_response(message, reason=f"http_{resp.status_code}")
                data = resp.json()
                raw_output = data.get('response') or data.get('output') or ''
                parsed = self._parse_json(raw_output)
                return {
                    "response": parsed['answer'],
                    "intent": parsed['intent'],
                    "confidence": parsed['confidence'],
                    "entities": parsed['entities'],
                    "source": "llm",
                    "timestamp": datetime.now().isoformat(),
                    "buttons": [],
                    "quick_replies": self._quick_replies(parsed['intent'])
                }
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return self._fallback_response(message, reason="exception")

    def _parse_json(self, text: str) -> Dict[str, Any]:
        # Attempt direct parse, else extract first JSON object substring
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            try:
                return self._validate(json.loads(text))
            except Exception:
                pass
        # Fallback: find first { .. }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            snippet = text[start:end+1]
            try:
                return self._validate(json.loads(snippet))
            except Exception:
                logger.debug("Failed to parse extracted JSON snippet")
        return DEFAULT_RESPONSE

    def _validate(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        intent = str(obj.get('intent', 'unknown'))[:64]
        confidence = obj.get('confidence', 0.0)
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.0
        if not (0.0 <= confidence <= 1.0):
            confidence = 0.0
        entities = obj.get('entities') or []
        if not isinstance(entities, list):
            entities = []
        answer = obj.get('answer') or DEFAULT_RESPONSE['answer']
        if len(answer) > 4000:
            answer = answer[:3997] + '...'
        return {"intent": intent, "confidence": confidence, "entities": entities, "answer": answer}

    def _fallback_response(self, message: str, reason: str) -> Dict[str, Any]:
        base = DEFAULT_RESPONSE.copy()
        base['answer'] += f" (LLM fallback: {reason})"
        return {
            "response": base['answer'],
            "intent": base['intent'],
            "confidence": base['confidence'],
            "entities": base['entities'],
            "source": f"llm_fallback_{reason}",
            "timestamp": datetime.now().isoformat(),
            "buttons": [],
            "quick_replies": self._quick_replies(base['intent'])
        }

    def _quick_replies(self, intent: str) -> List[str]:
        base = ["Symptom Help", "Find Hospitals", "Vaccination Info", "Emergency Help"]
        if intent == 'greet':
            return ["I have fever", "Find hospitals", "COVID vaccine", "Health tips"]
        if intent == 'ask_symptoms':
            return ["Moderate", "Severe", "Since 3 days", "Emergency signs"]
        return base

llm_service = OllamaLLMService()

