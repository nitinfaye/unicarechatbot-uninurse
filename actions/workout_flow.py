# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"
# from db.mongo import Person
# import sys
# sys.path.append("../")
# import logging
from typing import Any, Text, Dict, List, Optional, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import SlotSet, Restarted, FollowupAction
# from datetime import datetime as dt, time
from utils.helper import *
from utils import diginurse_utils as dg
from actions.action_utils import _yes_no_buttons, get_name_phone


class ActionExperiencePain(Action):

    def name(self) -> Text:
        return "action_experience_pain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : Exercise |  name : {name} | phone : {phone}")

        message = "Did you experience any pain during workout session ?"
        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=message, buttons=buttons)
        return []


class ActionFirstPain(Action):

    def name(self) -> Text:
        return "action_first_pain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        first_pain = dg.getWorkoutPain(name, phone)
        if first_pain is None:
            first_pain = "yes"
        else:
            first_pain = 'no'

        logger.info(f"[{tracker.sender_id}] {__file__} : action_first_pain |  name : {name} | phone : {phone}, first_pain = {first_pain}")
        return [SlotSet("first_pain", first_pain)]


class FormAboutPain(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_about_pain"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["pain"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""

        return {"pain": self.from_text()}

    def request_next_slot(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):

                # utter template and request slot
                if slot == "pain":
                    message = "Please specify the pain."
                    dispatcher.utter_message(text=message)

                return [SlotSet("requested_slot", slot)]
        return None

    def validate_pain(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate drinking value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} : text : {value} | intent : {intent}")
        return {"pain": value}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        name, phone = get_name_phone(tracker)
        user_pain = tracker.get_slot('pain')
        logger.info(f"[{tracker.sender_id}] {__file__} : user_pain : {user_pain}")
        dg.updateWorkoutPain(name, phone, pain=user_pain)
        return [FollowupAction('action_report_about_pain')]


class ActionRockTomorrow(Action):
    def name(self) -> Text:
        return "action_rock_tomorrow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : Exercise |  name : {name} | phone : {phone}")

        dg.updateWorkoutPain(name, phone, pain="No")
        dg.addToDB(name, phone)
        message = "That's great lets crush it tomorrow as well"
        dispatcher.utter_message(text=message)
        return [Restarted()]


class ActionSamePain(Action):

    def name(self) -> Text:
        return "action_same_pain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}]  {__file__} : Round : Exercise |  name : {name} | phone : {phone}")

        message = "Is it occurring like last time?"
        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=message, buttons=buttons)
        return []


class ActionReportAboutPain(Action):

    def name(self) -> Text:
        return "action_report_about_pain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} | action_report_about_pain |  name : {name} | phone : {phone}")

        message = "I have reported that in your medical log."
        dg.addToDB(name, phone)

        dispatcher.utter_message(text=message)
        return [Restarted()]


class ActionBecauseOfPain(Action):

    def name(self) -> Text:
        return "action_because_of_pain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : Exercise |  name : {name} | phone : {phone}")

        message = "Was it because of the pain during workout?"
        buttons = button_it(_yes_no_buttons())

        dispatcher.utter_message(text=message, buttons=buttons)
        return []
