
from db.mongo import Person
import sys
sys.path.append("../")
import logging
from typing import Any, Text, Dict, List, Optional, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import SlotSet, Restarted, AllSlotsReset
from datetime import datetime as dt, time
from utils.helper import *
from utils import diginurse_utils as dg
from actions.action_utils import get_name_phone, _ask_doctor_buttons, _yes_no_buttons, log_tracker_event


class PrePostMeal(FormAction):
    """Example of a custom form action"""
    _symptoms_value = {}
    _vitals_value = {}
    _vitals = []
    _symptoms = []
    _vital_name = None
    _symptom_name = None
    _current_round = None

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_pre_post_meal"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["ask_medication", "log_symptoms", 'symptoms', 'vitals']

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""

        return {
                "ask_medication": self.from_text(),
                "log_symptoms": self.from_text(),
                "symptoms": self.from_text(),
                "vitals": self.from_text()
                }

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        intent = tracker.latest_message['intent'].get('name')
        name, phone = get_name_phone(tracker)
        self._current_round = tracker.get_slot('round')

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.info(f"[{tracker.sender_id}] {__file__} request_next_slot of PrePostMeal | round : {self._current_round} | slot : {slot} ")
                log_tracker_event(tracker, logger)

                # utter template and request slot
                tell = ""
                remind = ""
                recommend = ""
                if slot == "ask_medication":

                    medication = f"Have you taken all pre-meal medication ?"

                    remind_after_some_time = False  # TODO load from db
                    if remind_after_some_time:
                        tell = "Sure, I'll remind you after some time"
                        remind = ""
                        recommend = ""
                        medication = ""
                    ask = medication
                    buttons = button_it(_yes_no_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "log_symptoms":

                    # TODO load from db
                    tell = "Nice! Are you ready to log your symptoms and vitals ?"
                    remind_after_some_time = False

                    if remind_after_some_time:
                        tell = "Sure, I'll remind you after some time"
                        # TODO :  need to implement the remind later action

                    ask = tell
                    buttons = button_it(_yes_no_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "symptoms":
                    ask = f"Are you having/feeling {self._symptom_name} ?"
                    buttons = button_it(_yes_no_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "vitals":
                    ask = f'what is the reading of your {self._vital_name} ?'
                    dispatcher.utter_message(text=ask)

                return [SlotSet("requested_slot", slot)]
        return None

    def validate_ask_medication(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        intent = tracker.latest_message['intent'].get('name')
        name, phone = get_name_phone(tracker)

        logger.info(f"[{tracker.sender_id}] {__file__} : validate_ask_medication :  text : {value} | intent : {intent}")
        msg = ""
        if intent in ["remained_me", "deny"]:
            # TODO Asked to remind after some time but need to extract that time
            # update remind field to True
            tell = "Sure, let me know when you are ready"
            dispatcher.utter_message(text=tell)

            return {"ask_medication": "completed", 'log_symptoms': 'completed', 'symptoms': 'completed', 'vitals': 'completed'}
        else:
            # logging status of all med/vital/symptoms are taken/done/checked/completed
            for item in dg.getMedicines(name, phone, self._current_round):
                item[1] = 'taken'
        return {"ask_medication": "completed"}

    def validate_log_symptoms(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        intent = tracker.latest_message['intent'].get('name')
        ret_slots = {'log_symptoms' : 'completed'}
        name, phone = get_name_phone(tracker)

        logger.info(f"[{tracker.sender_id}] {__file__} : validate_log_symptoms :  text : {value} | intent : {intent}")
        msg = ""
        if intent in ["remained_me", "deny"]:
            # TODO Asked to remind after some time but need to extract that time
            # update remind field to True
            tell = "Sure, let me know when you are ready"
            dispatcher.utter_message(text=tell)

            return {'log_symptoms': ret_slots,  'symptoms': 'completed', 'vitals': 'completed'}

        elif intent in ["affirm"]:
            # user is ready to log symptoms and vitals

            # get the list of symptoms and vitals for logging purpose
            if self._current_round is not None:
                self._symptoms = dg.getSymptoms(name, phone, self._current_round).copy()
                self._vitals = dg.getVitals(name, phone, self._current_round).copy()

            if len(self._symptoms) == 0:
                # no symptoms left to monitor, so mark the slot as completed
                ret_slots['symptoms'] = 'completed'
            else:
                self._symptom_name = dg.getMedItemName(self._symptoms[-1])

            if len(self._vitals) == 0:
                # no vitals, so mark the vitals slot as completed
                ret_slots['vitals'] = 'completed'
            else:
                self._vital_name = dg.getMedItemName(self._vitals[-1])

        logger.info(f"{__file__} : end of validate_log_symptoms :  symptoms = {self._symptoms} | vitals = {self._vitals} ")
        logger.info(f"{__file__} : end of validate_log_symptoms :  _symptom_name =  {self._symptom_name} | _vital_name = {self._vital_name}")
        logger.info(f"{__file__} : end of validate_log_symptoms :  ret_slots =  {ret_slots} ")

        return ret_slots

    def validate_symptoms(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} : validate_symptoms :  text : {value} ")

        # store the value of current symptom and make the next symptom as current symptom
        # if symptom list is empty then log all the symptoms
        sym = self._symptoms.pop()
        # Assigning the input value to the symptom
        sym[1] = value

        if len(self._symptoms) == 0:
            # no symptoms left to monitor, so mark the slot as completed
            logger.info(f"{__file__} : validate_symptoms :  update all symptoms ")
            return {"symptoms": 'completed'}
        else:
            self._symptom_name = dg.getMedItemName(self._symptoms[-1])
            return {"symptoms": None}

    def validate_vitals(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        # intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} : validate_vitals :  text : {value}")
        # store the value of current symptom and make the next symptom as current symptom
        # if symptom list is empty then log all the symptoms
        vital = self._vitals.pop()
        # Assigning the input value to the vital
        vital[1] = value

        if len(self._vitals) == 0:
            # no vitals left to monitor, so mark the slot as completed
            logger.info(f"[{tracker.sender_id}] {__file__} : validate_vitals :  update values for all vitals")
            return {"vitals": 'completed'}
        else:
            self._vital_name = dg.getMedItemName(self._vitals[-1])
            return {"vitals": None}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        logger.info(f"[{tracker.sender_id}] {__file__} : submit of  PrePostMeal ")
        log_tracker_event(tracker, logger)

        # we are here because patient is not feeling well. So need to update the DB accordingly.
        name, phone = get_name_phone(tracker)
        dg.updatePatientStatus(name, phone, 'better')

        ask_medication = tracker.get_slot('ask_medication')
        log_symptoms = tracker.get_slot('log_symptoms')
        symptoms = tracker.get_slot('symptoms')
        vitals = tracker.get_slot('vitals')

        tell = f"Thanks for updating your Vitals and Symptoms !!"
        # tell += f" symptoms = {symptoms} , vitals = {vitals}"
        # data = {'symptoms': symptoms, 'vitals': vitals}
        # update the DB with symptoms and vitals
        dg.addToDB(name, phone)

        dispatcher.utter_message(text=tell)
        return []
