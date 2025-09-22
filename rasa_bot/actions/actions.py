from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionCheckVaccineSchedule(Action):
    def name(self) -> Text:
        return "action_check_vaccine_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        age = tracker.get_slot("age")
        # TODO: Implement vaccine schedule lookup
        dispatcher.utter_message(text=f"Let me check the vaccination schedule for age {age}")
        return []

class ActionGetSymptomInfo(Action):
    def name(self) -> Text:
        return "action_get_symptom_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        symptom = tracker.get_slot("symptom")
        # TODO: Implement symptom information lookup
        dispatcher.utter_message(text=f"Here's information about {symptom}")
        return []

class ActionSendOutbreakAlert(Action):
    def name(self) -> Text:
        return "action_send_outbreak_alert"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        # TODO: Implement outbreak alert lookup
        dispatcher.utter_message(text=f"Checking for health alerts in {location}")
        return []

class ActionGetPreventionTips(Action):
    def name(self) -> Text:
        return "action_get_prevention_tips"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # TODO: Implement prevention tips lookup
        dispatcher.utter_message(text="Here are some prevention tips...")
        return []