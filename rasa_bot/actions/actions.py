from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import requests
import logging
import os
from datetime import datetime
import sys
import asyncio

# Add the backend services to the path
sys.path.append('/app/backend')

try:
    from backend.services.vaccination_service import vaccination_service
    from backend.services.symptom_analyzer import symptom_analyzer
    from backend.services.hospital_finder import hospital_finder
except ImportError:
    # Fallback if services are not available
    vaccination_service = None
    symptom_analyzer = None
    hospital_finder = None

logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class ActionCheckVaccineSchedule(Action):
    def name(self) -> Text:
        return "action_check_vaccine_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        age = tracker.get_slot("age")
        vaccine_type = tracker.get_slot("vaccine_type")

        try:
            if vaccination_service:
                # Use the new vaccination service
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    vaccination_service.get_vaccination_schedule(age, vaccine_type)
                )

                if "error" not in result:
                    if vaccine_type and "covid" in vaccine_type.lower():
                        message = f"🦠 **COVID-19 Vaccination Information:**\n\n"
                        message += f"📱 **Registration:** CoWIN Portal (cowin.gov.in)\n"
                        message += f"💉 **Available Vaccines:** Covishield, Covaxin, Sputnik V\n"
                        message += f"🏥 **Centers:** Government & private hospitals\n"
                        message += f"📞 **Helpline:** 1075\n\n"
                        message += f"**Documents Required:** Aadhaar, Voter ID, or other valid ID\n"
                        message += f"**Booster Dose:** Available for 60+ and healthcare workers"
                    else:
                        vaccines = result.get("vaccines", [])
                        if vaccines:
                            message = f"💉 **Vaccination Schedule for Age {age}:**\n\n"
                            for vaccine in vaccines[:5]:  # Show top 5
                                message += f"• **{vaccine.get('vaccine', vaccine.get('name', 'Unknown'))}**\n"
                                message += f"  Age: {vaccine.get('age', vaccine.get('timing', 'As advised'))}\n"
                                message += f"  Prevents: {vaccine.get('disease', 'Multiple diseases')}\n\n"
                        else:
                            message = f"For age {age}, please consult with a healthcare provider for personalized vaccination schedule."
                else:
                    message = "Please provide your age to get vaccination information (e.g., 25 years)"
            else:
                # Fallback to API call
                response = requests.get(f"{BACKEND_URL}/health/vaccine-schedule",
                                     params={"age": age, "vaccine_type": vaccine_type})
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
                    message = "For vaccination information, visit CoWIN portal or contact local health center. Helpline: 1075"

        except Exception as e:
            logger.error(f"Error in vaccine schedule action: {e}")
            message = "For vaccination information:\n• Visit CoWIN portal: cowin.gov.in\n• Call helpline: 1075\n• Contact local health center"

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
        
        # Extract symptoms from the latest message if not in slots
        latest_message = tracker.latest_message.get("text", "")
        symptoms_to_analyze = []

        if symptom:
            symptoms_to_analyze.append(symptom)
        else:
            # Extract common symptoms from message
            symptom_keywords = ["fever", "headache", "cough", "pain", "बुखार", "सिर दर्द", "खांसी"]
            for keyword in symptom_keywords:
                if keyword.lower() in latest_message.lower():
                    symptoms_to_analyze.append(keyword)

        if not symptoms_to_analyze:
            symptoms_to_analyze = ["general symptoms"]

        try:
            if symptom_analyzer:
                # Use the advanced symptom analyzer
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    symptom_analyzer.analyze_symptoms(symptoms_to_analyze, duration, severity)
                )

                if "error" not in result:
                    severity_level = result["severity_assessment"]["level"]

                    message = f"🏥 **Symptom Analysis Results:**\n\n"
                    message += f"**Severity Level:** {severity_level.title()}\n"
                    message += f"**Recommendation:** {result['severity_assessment']['assessment']['action']}\n\n"

                    # Add red flags if any
                    if result["red_flags"]:
                        message += f"🚨 **URGENT:** {result['red_flags'][0]['action']}\n\n"

                    # Add home remedies
                    if result["home_remedies"]:
                        message += f"**Home Care Tips:**\n"
                        for remedy in result["home_remedies"][:3]:
                            message += f"• {remedy}\n"
                        message += "\n"

                    # Add specialist recommendation
                    specialist = result["specialist_recommendation"]
                    message += f"**Consult:** {specialist['specialist']}\n"
                    message += f"**Emergency:** Call 108 if symptoms worsen"

                else:
                    message = "Unable to analyze symptoms. Please consult a healthcare professional."

            else:
                # Fallback to API call
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
                    message = f"For {symptom} symptoms:\n• Rest and stay hydrated\n• Monitor symptoms\n• Consult doctor if severe or persistent\n• Call 108 for emergencies"

        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            message = "For symptom guidance:\n• Monitor your symptoms\n• Stay hydrated and rest\n• Consult healthcare provider if concerned\n• Call 108 for emergencies"

        dispatcher.utter_message(text=message)
        return []

class ActionFindNearestHospital(Action):
    def name(self) -> Text:
        return "action_find_nearest_hospital"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        latest_message = tracker.latest_message.get("text", "")
        
        # Extract location from message if not in slot
        if not location:
            location_keywords = ["delhi", "mumbai", "bangalore", "chennai", "hyderabad", "pune"]
            for keyword in location_keywords:
                if keyword.lower() in latest_message.lower():
                    location = keyword
                    break

        if not location:
            location = "your area"

        try:
            if hospital_finder:
                # Use the hospital finder service
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    hospital_finder.find_nearest_hospitals(location, emergency_only=False)
                )

                if "error" not in result and result.get("hospitals"):
                    hospitals = result["hospitals"]

                    message = f"🏥 **Hospitals near {location}:**\n\n"

                    for i, hospital in enumerate(hospitals[:3], 1):  # Show top 3
                        message += f"**{i}. {hospital['name']}**\n"
                        message += f"📍 {hospital.get('address', 'Contact for address')}\n"
                        message += f"📞 {hospital.get('phone', hospital.get('emergency', 'Contact for number'))}\n"
                        if hospital.get('rating'):
                            message += f"⭐ Rating: {hospital['rating']}\n"
                        if hospital.get('distance_km') != "Contact for exact location":
                            message += f"📏 Distance: {hospital.get('distance_km', 'N/A')} km\n"
                        message += "\n"

                    # Add emergency services
                    emergency = result.get("emergency_services", {})
                    message += f"🚨 **Emergency Numbers:**\n"
                    message += f"• Ambulance: {emergency.get('ambulance', '108')}\n"
                    message += f"• Health Helpline: {emergency.get('health_ministry', '1075')}\n"

                else:
                    message = f"🏥 **Hospital Information for {location}:**\n\n"
                    message += "For nearby hospitals:\n"
                    message += "• Search on Google Maps for 'hospitals near me'\n"
                    message += "• Call 108 for emergency ambulance\n"
                    message += "• Contact local health department\n"
                    message += "• Visit district hospital or PHC\n\n"
                    message += "**Emergency: Call 108**"
            else:
                message = f"🏥 **Hospital Information for {location}:**\n\n"
                message += "**Major Hospitals:**\n"
                message += "• Government hospitals: District Hospital, PHC\n"
                message += "• Private hospitals: Check Google Maps\n\n"
                message += "**Emergency Services:**\n"
                message += "• Ambulance: 108\n"
                message += "• Health Helpline: 1075\n"
                message += "• Police: 100\n\n"
                message += "**Tips:**\n"
                message += "• Call before visiting\n"
                message += "• Carry ID and medical documents\n"
                message += "• For emergencies, call 108 immediately"

        except Exception as e:
            logger.error(f"Error finding hospitals: {e}")
            message = "🏥 **Hospital Information:**\n\n• Call 108 for emergency\n• Contact local health department\n• Visit nearest district hospital\n• Use Google Maps to find nearby hospitals"

        dispatcher.utter_message(text=message)
        return []

class ActionGetMedicineInfo(Action):
    def name(self) -> Text:
        return "action_get_medicine_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        medicine = tracker.get_slot("medicine")
        symptom = tracker.get_slot("symptom")
        latest_message = tracker.latest_message.get("text", "")

        # Extract medicine name from message
        if not medicine:
            medicine_keywords = ["paracetamol", "aspirin", "crocin", "dolo", "fever medicine"]
            for keyword in medicine_keywords:
                if keyword.lower() in latest_message.lower():
                    medicine = keyword
                    break

        try:
            if medicine:
                medicine_info = {
                    "paracetamol": {
                        "uses": "Fever, headache, body ache",
                        "dosage": "Adults: 500-1000mg every 4-6 hours (max 4g/day)",
                        "precautions": "Don't exceed recommended dose, avoid with liver problems",
                        "side_effects": "Generally safe, rare liver problems with overdose"
                    },
                    "aspirin": {
                        "uses": "Pain, fever, inflammation, heart protection",
                        "dosage": "Adults: 300-600mg every 4 hours (max 4g/day)",
                        "precautions": "Avoid in children under 16, stomach ulcers, bleeding disorders",
                        "side_effects": "Stomach irritation, bleeding risk"
                    },
                    "crocin": {
                        "uses": "Fever, headache, body ache (contains paracetamol)",
                        "dosage": "Adults: 1-2 tablets every 4-6 hours (max 8 tablets/day)",
                        "precautions": "Same as paracetamol, don't take with other paracetamol medicines",
                        "side_effects": "Generally safe when used as directed"
                    }
                }

                info = medicine_info.get(medicine.lower())
                if info:
                    message = f"💊 **{medicine.title()} Information:**\n\n"
                    message += f"**Uses:** {info['uses']}\n"
                    message += f"**Dosage:** {info['dosage']}\n"
                    message += f"**Precautions:** {info['precautions']}\n"
                    message += f"**Side Effects:** {info['side_effects']}\n\n"
                    message += "⚠️ **Important:**\n"
                    message += "• Always read package instructions\n"
                    message += "• Consult pharmacist or doctor\n"
                    message += "• Don't exceed recommended dose\n"
                    message += "• Stop if allergic reactions occur"
                else:
                    message = f"💊 **Medicine Information for {medicine}:**\n\n"
                    message += "For specific medicine information:\n"
                    message += "• Consult pharmacist\n"
                    message += "• Read package insert\n"
                    message += "• Check with doctor\n"
                    message += "• Visit Jan Aushadhi store for generic medicines\n\n"
                    message += "**Jan Aushadhi Helpline:** 1800-180-5253"
            else:
                message = "💊 **Medicine Information:**\n\n"
                message += "**For Common Symptoms:**\n"
                message += "• Fever: Paracetamol (Crocin, Dolo)\n"
                message += "• Headache: Paracetamol or Aspirin\n"
                message += "• Body ache: Paracetamol or Ibuprofen\n"
                message += "• Cold: Antihistamines, decongestants\n\n"
                message += "**Important:**\n"
                message += "• Always consult pharmacist/doctor\n"
                message += "• Read medicine labels carefully\n"
                message += "• Don't self-medicate for serious symptoms\n"
                message += "• Keep medicines away from children\n\n"
                message += "**Jan Aushadhi (Generic Medicines):** 1800-180-5253"

        except Exception as e:
            logger.error(f"Error getting medicine info: {e}")
            message = "💊 For medicine information, consult your pharmacist or doctor. Generic medicines available at Jan Aushadhi stores. Helpline: 1800-180-5253"

        dispatcher.utter_message(text=message)
        return []

class ActionCheckHealthStatus(Action):
    def name(self) -> Text:
        return "action_check_health_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location") or "India"

        try:
            response = requests.get(
                f"{BACKEND_URL}/api/health/status",
                params={"location": location},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                message = f"🌍 **Health Status for {location}:**\n\n"

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
            logger.error(f"Error getting health status: {e}")
            message = "Please check official health websites like MoHFW (mohfw.gov.in) for current health alerts and outbreak information."

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

