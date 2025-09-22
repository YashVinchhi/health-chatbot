from typing import Any, Text, Dict, List
import requests
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

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