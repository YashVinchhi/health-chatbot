from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import requests
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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

        vaccine_type = tracker.get_slot("vaccine_type") or "general"
        location = tracker.get_slot("location") or "India"

        try:
            response = requests.get(
                f"{BACKEND_URL}/api/health/vaccination",
                params={"type": vaccine_type, "location": location},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if vaccine_type.lower() in ["covid", "covid-19", "covishield", "covaxin"]:
                    message = "🦠 **COVID-19 Vaccination in India:**\n\n"
                    message += "📱 **Booking**: CoWIN portal (https://www.cowin.gov.in/) or Aarogya Setu app\n"
                    message += "💉 **Available Vaccines**: Covishield, Covaxin, Sputnik V\n"
                    message += "🏥 **Centers**: Government hospitals, PHCs, private hospitals\n"
                    message += "💰 **Cost**: Free at government centers\n"
                    message += "📞 **Helpline**: 1075\n"
                    message += "🎫 **Certificate**: Download from CoWIN after vaccination\n\n"
                    message += "**Eligibility**: All adults and children 12+ years\n"
                    message += "**Booster**: Recommended for 60+ and healthcare workers"
                else:
                    message = "💉 **Vaccination Information for India:**\n\n"
                    message += "**Government Programs:**\n"
                    message += "• Mission Indradhanush (childhood vaccines)\n"
                    message += "• Free COVID-19 vaccination\n"
                    message += "• Pulse Polio campaigns\n\n"
                    message += "**Common Vaccines:**\n"
                    message += "• COVID-19: CoWIN registration\n"
                    message += "• Influenza: Annual shot recommended\n"
                    message += "• Hepatitis B: For high-risk groups\n"
                    message += "• Travel vaccines: Consult travel clinics\n\n"
                    message += "📞 **Universal Immunization Helpline**: 1075"

            else:
                message = "💉 **Vaccination Information:**\n\n"
                message += "For the most current vaccination information:\n"
                message += "• Visit CoWIN portal: https://www.cowin.gov.in/\n"
                message += "• Contact local health centers\n"
                message += "• Call helpline: 1075\n\n"
                message += "Always consult healthcare providers for personalized vaccination advice."

        except Exception as e:
            logger.error(f"Error getting vaccination info: {e}")
            message = "For vaccination information, please visit CoWIN portal or contact your local health center. Helpline: 1075"

        dispatcher.utter_message(text=message)
        return []

class ActionGetOutbreakInfo(Action):
    def name(self) -> Text:
        return "action_get_outbreak_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location = tracker.get_slot("location") or "India"

        try:
            response = requests.get(
                f"{BACKEND_URL}/api/health/outbreak",
                params={"location": location},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                message = f"🦠 **Current Health Status for {location}:**\n\n"

                # Add current alerts if available
                if "alerts" in data and data["alerts"]:
                    for alert in data["alerts"][:3]:  # Limit to 3 alerts
                        risk_emoji = "🔴" if alert.get("risk_level") == "High" else "🟡" if alert.get("risk_level") == "Moderate" else "🟢"
                        message += f"{risk_emoji} **{alert.get('disease', 'Unknown')}**: {alert.get('details', 'Monitoring ongoing')}\n"
                    message += "\n"

                message += "**General Precautions:**\n"
                message += "• Maintain good hygiene\n"
                message += "• Follow local health guidelines\n"
                message += "• Get vaccinated as recommended\n"
                message += "• Use mosquito protection during monsoon\n\n"

                message += "**Stay Updated:**\n"
                message += "• MoHFW website: https://www.mohfw.gov.in/\n"
                message += "• Aarogya Setu app\n"
                message += "• Local health department notifications\n"
                message += "• WHO updates for global health\n\n"

                message += "📞 **Health Helpline**: 1075"

            else:
                message = "🦠 **Health Alert System:**\n\n"
                message += "For current health alerts and disease surveillance:\n"
                message += "• Check MoHFW website: https://www.mohfw.gov.in/\n"
                message += "• Download Aarogya Setu app\n"
                message += "• Follow local health department updates\n"
                message += "• Monitor WHO global health alerts\n\n"
                message += "📞 **Health Information**: 1075"

        except Exception as e:
            logger.error(f"Error getting outbreak info: {e}")
            message = "Please check official health websites like MoHFW (mohfw.gov.in) for current health alerts and outbreak information."

        dispatcher.utter_message(text=message)
        return []

class ActionSymptomAnalysis(Action):
    def name(self) -> Text:
        return "action_symptom_analysis"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        symptom = tracker.get_slot("symptom")
        severity = tracker.get_slot("severity")
        location = tracker.get_slot("location")

        try:
            # Get symptom information from backend
            response = requests.get(
                f"{BACKEND_URL}/api/health/symptoms",
                params={
                    "symptom": symptom,
                    "severity": severity,
                    "location": location or "India"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                message = f"📋 **Symptom Analysis for {symptom}:**\n\n"

                if severity:
                    message += f"**Severity**: {severity.title()}\n\n"

                message += "**General Information:**\n"
                message += "• Monitor your symptoms carefully\n"
                message += "• Stay hydrated and get adequate rest\n"
                message += "• Take your temperature if you have fever\n\n"

                if severity == "severe":
                    message += "🚨 **URGENT**: For severe symptoms, please:\n"
                    message += "• Seek immediate medical attention\n"
                    message += "• Call emergency services: 102 (Medical) or 108 (Ambulance)\n"
                    message += "• Visit the nearest emergency room\n\n"
                elif severity == "moderate":
                    message += "⚠️ **Recommendation**: Consider consulting a healthcare provider if symptoms:\n"
                    message += "• Persist for more than 2-3 days\n"
                    message += "• Worsen over time\n"
                    message += "• Are accompanied by high fever\n\n"
                else:
                    message += "💡 **Self-Care Tips**:\n"
                    message += "• Rest and maintain good hydration\n"
                    message += "• Monitor symptoms for any changes\n"
                    message += "• Consider over-the-counter remedies if appropriate\n\n"

                message += "**When to seek medical help:**\n"
                message += "• High fever (>101°F/38.3°C)\n"
                message += "• Difficulty breathing\n"
                message += "• Persistent or worsening symptoms\n"
                message += "• Signs of dehydration\n\n"
                message += "⚠️ **Disclaimer**: This is general guidance only. For medical diagnosis and treatment, please consult qualified healthcare professionals."

            else:
                message = f"I understand you're experiencing {symptom}. Here's general guidance:\n\n"
                message += "• Monitor your symptoms\n"
                message += "• Stay hydrated and rest\n"
                message += "• Seek medical attention if symptoms worsen\n\n"
                message += "For severe symptoms, please call 102 or 108 immediately."

        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            message = f"I understand you're experiencing {symptom}. Please monitor your symptoms and consult a healthcare professional if they persist or worsen. For emergencies, call 102 or 108."

        dispatcher.utter_message(text=message)
        return []

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_user_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate user name."""
        if len(slot_value) <= 2:
            dispatcher.utter_message(text="Please provide a valid name with more than 2 characters.")
            return {"user_name": None}
        else:
            return {"user_name": slot_value}

# Additional action for emergency contacts
class ActionGetEmergencyContacts(Action):
    def name(self) -> Text:
        return "action_get_emergency_contacts"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location = tracker.get_slot("location") or "India"

        message = "🚨 **Emergency Contacts for India:**\n\n"
        message += "**Medical Emergency:**\n"
        message += "• 🏥 Medical Emergency: 102\n"
        message += "• 🚑 Ambulance: 108\n"
        message += "• 🦠 COVID Helpline: 1075\n\n"

        message += "**Other Emergency Services:**\n"
        message += "• 👮 Police: 100\n"
        message += "• 🔥 Fire: 101\n"
        message += "• 👩 Women Helpline: 1091\n"
        message += "• 👶 Child Helpline: 1098\n"
        message += "• 🧠 Mental Health: 9152987821 (AASRA)\n\n"

        message += "**Poison Control:**\n"
        message += "• All India Institute of Medical Sciences (AIIMS)\n"
        message += "• Contact nearest government hospital\n\n"

        message += "**Important Notes:**\n"
        message += "• Keep these numbers handy\n"
        message += "• Most services are available 24x7\n"
        message += "• Call the most appropriate number for your emergency\n"
        message += "• For immediate life-threatening situations, call 102 or 108"

        dispatcher.utter_message(text=message)
        return []

class ActionCheckMedicineInfo(Action):
    def name(self) -> Text:
        return "action_check_medicine_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = "💊 **Medicine Safety & Information:**\n\n"
        message += "⚠️ **Important Disclaimer**: I cannot provide specific medicine recommendations. Always consult:\n"
        message += "• Qualified doctors (MBBS/MD/specialists)\n"
        message += "• Licensed pharmacists\n"
        message += "• Government healthcare centers\n\n"

        message += "💡 **General Medicine Safety:**\n"
        message += "• Take medicines exactly as prescribed\n"
        message += "• Complete full course of antibiotics\n"
        message += "• Store medicines in cool, dry places\n"
        message += "• Check expiry dates before use\n"
        message += "• Don't share prescription medicines\n"
        message += "• Report side effects to your doctor\n\n"

        message += "🏪 **Affordable Medicine Options:**\n"
        message += "• Jan Aushadhi stores (generic medicines)\n"
        message += "• Government hospital pharmacies\n"
        message += "• Ask for generic alternatives\n\n"

        message += "📞 **For Medicine Queries:**\n"
        message += "• Consult your prescribing doctor\n"
        message += "• Ask pharmacist for guidance\n"
        message += "• Contact hospital helplines\n"
        message += "• Use telemedicine consultations"

        dispatcher.utter_message(text=message)
        return []
