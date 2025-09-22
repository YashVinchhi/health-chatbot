from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import logging
import os

logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

class ActionCheckVaccineSchedule(Action):
    def name(self) -> Text:
        return "action_check_vaccine_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        age = tracker.get_slot("age")
        
        try:
            response = requests.get(f"{BACKEND_URL}/health/vaccine-schedule", 
                                 params={"age": age})
            if response.status_code == 200:
                data = response.json()
                vaccines = data.get("vaccines", [])
                if vaccines:
                    message = f"For age {age}, the following vaccines are recommended:\n"
                    for vaccine in vaccines:
                        message += f"- {vaccine['name']}: {vaccine['description']}\n"
                else:
                    message = "No specific vaccines are scheduled for this age."
            else:
                message = "Sorry, I couldn't fetch the vaccine schedule at the moment."
        except Exception as e:
            message = "Sorry, I'm having trouble connecting to the health service."
            
        dispatcher.utter_message(text=message)
        return []

class ActionGetSymptomInfo(Action):
    def name(self) -> Text:
        return "action_get_symptom_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        symptom = tracker.get_slot("symptom")
        duration = tracker.get_slot("duration")
        severity = tracker.get_slot("severity")
        
        try:
            response = requests.get(f"{BACKEND_URL}/health/symptoms",
                                 params={"symptom": symptom,
                                       "duration": duration,
                                       "severity": severity})
            if response.status_code == 200:
                data = response.json()
                info = data.get("information", "")
                recommendations = data.get("recommendations", [])
                
                message = f"About {symptom}:\n{info}\n\nRecommendations:\n"
                for rec in recommendations:
                    message += f"- {rec}\n"
            else:
                message = f"Sorry, I couldn't find detailed information about {symptom}."
        except Exception as e:
            message = "Sorry, I'm having trouble accessing the health information service."
        
        dispatcher.utter_message(text=message)
        return []

class ActionSendOutbreakAlert(Action):
    def name(self) -> Text:
        return "action_send_outbreak_alert"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        
        try:
            response = requests.get(f"{BACKEND_URL}/health/outbreaks",
                                 params={"location": location})
            if response.status_code == 200:
                data = response.json()
                alerts = data.get("alerts", [])
                if alerts:
                    message = f"Current health alerts for {location}:\n"
                    for alert in alerts:
                        message += f"- {alert['disease']}: {alert['details']}\n"
                        message += f"  Risk Level: {alert['risk_level']}\n"
                else:
                    message = f"Good news! No current disease outbreaks reported in {location}."
            else:
                message = f"Sorry, I couldn't fetch outbreak information for {location}."
        except Exception as e:
            message = "Sorry, I'm having trouble connecting to the health alert service."
        
        dispatcher.utter_message(text=message)
        return []

class ActionGetPreventionTips(Action):
    def name(self) -> Text:
        return "action_get_prevention_tips"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        latest_message = tracker.latest_message.get("text", "")
        
        try:
            response = requests.get(f"{BACKEND_URL}/health/prevention-tips",
                                 params={"query": latest_message})
            if response.status_code == 200:
                data = response.json()
                tips = data.get("tips", [])
                if tips:
                    message = "Here are some prevention tips:\n"
                    for tip in tips:
                        message += f"- {tip}\n"
                else:
                    message = "I don't have specific prevention tips for this situation."
            else:
                message = "Sorry, I couldn't retrieve prevention tips at the moment."
        except Exception as e:
            message = "Sorry, I'm having trouble accessing the prevention tips service."
        
        dispatcher.utter_message(text=message)
        return []

class ActionGetVaccinationInfo(Action):
    def name(self) -> Text:
        return "action_get_vaccination_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            # Call the vaccination service
            response = requests.get("http://backend:8000/api/health/vaccination")
            if response.status_code == 200:
                data = response.json()
                message = f"Vaccination Information:\n{data.get('message', 'Information retrieved successfully')}"
            else:
                message = "I'm having trouble accessing vaccination information right now. Please try again later."
        except Exception as e:
            logger.error(f"Error getting vaccination info: {e}")
            message = "I'm having trouble accessing vaccination information right now. Please try again later."

        dispatcher.utter_message(text=message)
        return []

class ActionGetOutbreakInfo(Action):
    def name(self) -> Text:
        return "action_get_outbreak_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            # Call the outbreak service
            response = requests.get("http://backend:8000/api/health/outbreak")
            if response.status_code == 200:
                data = response.json()
                message = f"Outbreak Information:\n{data.get('message', 'Information retrieved successfully')}"
            else:
                message = "I'm having trouble accessing outbreak information right now. Please try again later."
        except Exception as e:
            logger.error(f"Error getting outbreak info: {e}")
            message = "I'm having trouble accessing outbreak information right now. Please try again later."

        dispatcher.utter_message(text=message)
        return []

class ActionSymptomAnalysis(Action):
    def name(self) -> Text:
        return "action_symptom_analysis"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the user's message
        user_message = tracker.latest_message.get('text', '')

        # Basic symptom analysis
        emergency_symptoms = ['chest pain', 'difficulty breathing', 'severe pain', 'unconscious', 'bleeding']
        serious_symptoms = ['fever', 'vomiting', 'severe headache', 'dizzy']

        message = ""

        # Check for emergency symptoms
        if any(symptom in user_message.lower() for symptom in emergency_symptoms):
            message = "🚨 URGENT: You mentioned symptoms that could be serious. Please seek immediate medical attention or call emergency services (911 in US, 108 in India)."
        elif any(symptom in user_message.lower() for symptom in serious_symptoms):
            message = "I understand you're experiencing concerning symptoms. While I can provide general information, it's important to consult with a healthcare professional for proper diagnosis and treatment. Consider contacting your doctor or visiting a clinic."
        else:
            message = "I hear that you're not feeling well. For any health concerns, it's always best to consult with a healthcare professional who can properly assess your symptoms and provide appropriate care."

        # Add general advice
        message += "\n\nIn the meantime, make sure to:\n• Stay hydrated\n• Get plenty of rest\n• Monitor your symptoms\n• Seek medical help if symptoms worsen"

        dispatcher.utter_message(text=message)
        return []
