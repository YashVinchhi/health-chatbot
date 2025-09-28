"""
Session Management Service for Health Chatbot
Handles conversation memory and language consistency
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ChatSession, ChatMessage
import re
import json

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.language_patterns = {
            'hi': {
                'keywords': ['क्या', 'कैसे', 'मुझे', 'है', 'हूं', 'बुखार', 'सिरदर्द', 'पेट', 'दर्द', 'अस्पताल', 'डॉक्टर'],
                'greeting': ['नमस्ते', 'हैलो', 'हाय']
            },
            'te': {
                'keywords': ['ఎలా', 'ఏమిటి', 'నాకు', 'ఉంది', 'జ్వరం', 'తలనొప్पి', 'కడుపు', 'నొప్పి', 'హాస్పిటల్', 'వైద్యుడు'],
                'greeting': ['నమస్తే', 'హలో', 'హాయ్']
            },
            'ta': {
                'keywords': ['எப்படி', 'என்ன', 'எனக்கு', 'இருக்கிறது', 'காய்ச்சல்', 'தலைவலி', 'வயிறு', 'வலி', 'மருத்துவமனை', 'மருத்துவர்'],
                'greeting': ['வணக்கம்', 'ஹலோ', 'ஹாய்']
            },
            'bn': {
                'keywords': ['কিভাবে', 'কি', 'আমার', 'আছে', 'জ্বর', 'মাথাব্যথা', 'পেট', 'ব্যথা', 'হাসপাতাল', 'ডাক্তার'],
                'greeting': ['নমস্কার', 'হ্যালো', 'হাই']
            },
            'en': {
                'keywords': ['how', 'what', 'i', 'have', 'fever', 'headache', 'pain', 'hospital', 'doctor'],
                'greeting': ['hello', 'hi', 'hey', 'good morning', 'good evening']
            }
        }

        self.response_templates = {
            'en': {
                'memory_greeting': "Hello again! I remember we were discussing {context}. How can I help you further?",
                'first_greeting': "Hello! I'm your health assistant. How can I help you today?",
                'context_reference': "Based on our previous conversation about {context}, ",
                'no_memory': "I don't have any previous context for this conversation."
            },
            'hi': {
                'memory_greeting': "नमस्ते! मुझे याद है हमने {context} के बारे में बात की थी। मैं आपकी और कैसे मदद कर सकता हूं?",
                'first_greeting': "नमस्ते! मैं आपका स्वास्थ्य सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
                'context_reference': "{context} के बारे में हमारी पिछली बातचीत के आधार पर, ",
                'no_memory': "इस बातचीत के लिए मेरे पास कोई पिछला संदर्भ नहीं है।"
            },
            'te': {
                'memory_greeting': "నమస్తే! మనం {context} గురించి మాట్లాడుకున్నామని నాకు గుర్తుంది। మరింత ఎలా సహాయం చేయగలను?",
                'first_greeting': "నమస్తే! నేను మీ ఆరోగ్య సహాయకుడిని। ఈరోజు మీకు ఎలా సహాయం చేయగలను?",
                'context_reference': "{context} గురించి మా మునుపటి సంభాషణ ఆధారంగా, ",
                'no_memory': "ఈ సంభాషణకు నా దగ్గర మునుపటి సందర్భం లేదు।"
            },
            'ta': {
                'memory_greeting': "வணக்கம்! நாம் {context} பற்றி பேசினோம் என்று எனக்கு நினைவிருக்கிறது। மேலும் எப்படி உதவ முடியும்?",
                'first_greeting': "வணக்கம்! நான் உங்கள் சுகாதார உதவியாளர். இன்று எப்படி உதவ முடியும்?",
                'context_reference': "{context} பற்றிய நமது முந்தைய உரையாடலின் அடிப்படையில், ",
                'no_memory': "இந்த உரையாடலுக்கு என்னிடம் முந்தைய சூழல் இல்லை।"
            },
            'bn': {
                'memory_greeting': "নমস্কার! আমার মনে আছে আমরা {context} নিয়ে কথা বলেছিলাম। আরও কিভাবে সাহায্য করতে পারি?",
                'first_greeting': "নমস্কার! আমি আপনার স্বাস্থ্য সহায়ক। আজ কিভাবে সাহায্য করতে পারি?",
                'context_reference': "{context} নিয়ে আমাদের আগের আলোচনার ভিত্তিতে, ",
                'no_memory': "এই কথোপকথনের জন্য আমার কাছে কোন পূর্ববর্তী প্রসঙ্গ নেই।"
            }
        }

    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        text_lower = text.lower()

        # Score each language based on keyword matches
        language_scores = {}

        for lang, patterns in self.language_patterns.items():
            score = 0
            for keyword in patterns['keywords']:
                if keyword.lower() in text_lower:
                    score += 1
            for greeting in patterns['greeting']:
                if greeting.lower() in text_lower:
                    score += 2  # Greetings get higher weight

            language_scores[lang] = score

        # Return the language with highest score, default to English
        if max(language_scores.values()) > 0:
            return max(language_scores, key=language_scores.get)

        # Fallback: check for non-ASCII characters to detect non-English
        if any(ord(char) > 127 for char in text):
            # Try to identify script-based languages
            if any('\u0900' <= char <= '\u097F' for char in text):  # Devanagari
                return 'hi'
            elif any('\u0C00' <= char <= '\u0C7F' for char in text):  # Telugu
                return 'te'
            elif any('\u0B80' <= char <= '\u0BFF' for char in text):  # Tamil
                return 'ta'
            elif any('\u0980' <= char <= '\u09FF' for char in text):  # Bengali
                return 'bn'

        return 'en'  # Default to English

    async def get_or_create_session(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Get existing session or create new one with language detection"""
        db = next(get_db())

        try:
            # Try to get existing session
            existing_session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()

            detected_language = self.detect_language(user_message)

            if existing_session:
                # Update language if different
                if existing_session.user_language != detected_language:
                    existing_session.user_language = detected_language
                    existing_session.updated_at = datetime.now()
                    db.commit()

                return {
                    'session_id': existing_session.session_id,
                    'language': existing_session.user_language,
                    'context': existing_session.context or {},
                    'is_new': False
                }
            else:
                # Create new session
                new_session = ChatSession(
                    session_id=session_id,
                    user_language=detected_language,
                    context={}
                )
                db.add(new_session)
                db.commit()
                db.refresh(new_session)

                return {
                    'session_id': new_session.session_id,
                    'language': new_session.user_language,
                    'context': {},
                    'is_new': True
                }

        except Exception as e:
            logger.error(f"Error managing session: {e}")
            db.rollback()
            return {
                'session_id': session_id,
                'language': self.detect_language(user_message),
                'context': {},
                'is_new': True
            }
        finally:
            db.close()

    async def get_conversation_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history for context"""
        db = next(get_db())

        try:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()

            return [
                {
                    'message': msg.message,
                    'response': msg.response,
                    'intent': msg.intent,
                    'timestamp': msg.timestamp.isoformat(),
                    'language': msg.language
                }
                for msg in reversed(messages)  # Oldest first
            ]

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
        finally:
            db.close()

    async def save_message(self, session_id: str, message: str, response: str,
                          intent: str, confidence: float, language: str):
        """Save message and response to conversation history"""
        db = next(get_db())

        try:
            chat_message = ChatMessage(
                session_id=session_id,
                message=message,
                response=response,
                intent=intent,
                confidence=confidence,
                language=language
            )
            db.add(chat_message)
            db.commit()

        except Exception as e:
            logger.error(f"Error saving message: {e}")
            db.rollback()
        finally:
            db.close()

    async def update_session_context(self, session_id: str, new_context: Dict[str, Any]):
        """Update session context with new information"""
        db = next(get_db())

        try:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()

            if session:
                # Merge new context with existing
                current_context = session.context or {}
                current_context.update(new_context)
                session.context = current_context
                session.updated_at = datetime.now()
                db.commit()

        except Exception as e:
            logger.error(f"Error updating session context: {e}")
            db.rollback()
        finally:
            db.close()

    def build_contextual_response(self, base_response: str, session_data: Dict[str, Any],
                                 conversation_history: List[Dict[str, Any]]) -> str:
        """Build response with conversation context"""
        language = session_data.get('language', 'en')
        context = session_data.get('context', {})
        is_new = session_data.get('is_new', True)

        templates = self.response_templates.get(language, self.response_templates['en'])

        # If this is a greeting and we have conversation history
        if (any(word in base_response.lower() for word in ['hello', 'hi', 'नमस्ते', 'నమస్తే', 'வணக்கம்', 'নমস্কার'])
            and not is_new and conversation_history):

            # Get the most recent topic from context
            recent_topic = context.get('last_topic', 'your health concerns')
            return templates['memory_greeting'].format(context=recent_topic)

        # Add context reference for relevant responses
        if context and not is_new:
            last_topic = context.get('last_topic')
            if last_topic and len(conversation_history) > 0:
                context_prefix = templates['context_reference'].format(context=last_topic)
                return context_prefix + base_response

        return base_response

    def extract_context_from_message(self, message: str, intent: str) -> Dict[str, Any]:
        """Extract context information from user message"""
        context = {}

        # Map intents to topics
        topic_mapping = {
            'fever_symptoms': 'fever',
            'headache_symptoms': 'headache',
            'cough_symptoms': 'cough',
            'stomach_symptoms': 'stomach problems',
            'find_hospital': 'finding hospitals',
            'covid_vaccination': 'vaccination',
            'medicine_info': 'medicines',
            'emergency_help': 'emergency help'
        }

        if intent in topic_mapping:
            context['last_topic'] = topic_mapping[intent]
            context['last_intent'] = intent
            context['last_message_time'] = datetime.now().isoformat()

        # Extract specific entities from message
        message_lower = message.lower()

        # Extract symptoms
        symptoms = []
        symptom_keywords = ['fever', 'headache', 'cough', 'pain', 'nausea', 'vomiting', 'diarrhea']
        for symptom in symptom_keywords:
            if symptom in message_lower:
                symptoms.append(symptom)

        if symptoms:
            context['mentioned_symptoms'] = symptoms

        # Extract severity indicators
        if any(word in message_lower for word in ['severe', 'very', 'extremely', 'bad', 'terrible']):
            context['severity'] = 'high'
        elif any(word in message_lower for word in ['mild', 'little', 'slight']):
            context['severity'] = 'low'

        return context

# Global instance
session_service = SessionService()
