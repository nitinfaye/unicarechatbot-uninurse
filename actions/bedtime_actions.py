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
from rasa_sdk.events import SlotSet, Restarted
from rasa_sdk.events import FollowupAction
# from datetime import datetime as dt, time
from utils.helper import *
from utils import diginurse_utils as dg
from actions.action_utils import get_name_phone, _yes_no_buttons, _ask_doctor_buttons, _pain_buttons, _yes_no_2_buttons, _ok_not_ok_buttons


class ActionSOSTaken(Action):
    def name(self) -> Text:
        return "action_sos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.info(f"[{tracker.sender_id}] {__file__} : action_sos ")

        return [FollowupAction('form_sos')]


class ActionMissingWorkoutInfo(Action):
    def name(self) -> Text:
        return "action_missing_workout_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender = tracker.sender_id
        name, phone = get_name_phone(tracker)
        pain = dg.getWorkoutPain(name, phone)
        logger.info(f"[{tracker.sender_id}] {__file__} : action_missing_workout_info |  pain= {str(pain)} ")

        if pain is None or pain == 'No':
            return [SlotSet('bt_sub_flow', 'pre_breakfast'), FollowupAction('action_missing_pre_breakfast_info')]
        else:
            return [SlotSet('bt_sub_flow', 'workout'), FollowupAction('form_missing_workout_info')]


class FormMissingWorkoutInfo(FormAction):
    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_missing_workout_info"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ['pain', 'ask_doctor']

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        return {
                "pain":  self.from_text(),
                "ask_doctor": self.from_text(),
                }

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        intent = tracker.latest_message['intent'].get('name')
        name, phone = get_name_phone(tracker)

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.info(f"[{tracker.sender_id}] {__file__} request_next_slot of FormMissingWorkoutInfo | slot : {slot} |  intent : {intent}")

                # utter template and request slot
                tell = ""
                remind = ""
                recommend = ""
                if slot == "pain":
                    pain = dg.getWorkoutPain(name, phone)
                    ask = f"During your workout session you reported \'{pain}\' ? How is that pain ?"
                    buttons = button_it(_pain_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "ask_doctor":
                    ask = f'Do you want to get in touch with the doctor ?'
                    buttons = button_it(_ask_doctor_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                return [SlotSet("requested_slot", slot)]
        return None

    def validate_pain(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        intent = tracker.latest_message['intent'].get('name')
        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : validate_pain |  text : {value} | intent : {intent}")
        ret = None
        if intent == 'better':
            ret = 'Yes'
            # updated the DB that there is no pain now
            dg.updateWorkoutPain(name, phone, 'No')
            return {'pain': intent, 'ask_doctor': 'No'}

        elif intent == 'worse' or intent == 'not_better':
            ret = 'No'
            return {'pain': intent}

    def validate_ask_doctor(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate ask_doctor value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} Inside validate_ask_doctor ::  text : {value} | intent : {intent}")
        msg = ""
        status = None
        name, phone = get_name_phone(tracker)

        if intent == "deny":
            dg.updatePatientStatus(name, phone, 'better')
            status = "no_need"
            ask = "Sure, please let me know if your discomfort increases.\n"   # TODO save into db so that we can ask about this
            msg = ask

        elif intent == "wait":
            dg.updatePatientStatus(name, phone, 'better')
            status = "wait"
            ask = "Sure, please let me know if your discomfort increases.\n"   # TODO save into db so that we can ask about this
            msg = ask

        elif intent == "remind_me":
            # TODO How do we pitch this after an hour or so???

            dg.updatePatientStatus(name, phone, 'Not well')
            status = "wait_for_hour"
            tell = "Sure, I'll ask you again in couple of hours. In the mean time let me know if discomfort increases."
            # ask_in_hour = False     # TODO load from db by default this field is false
            # if ask_in_hour:
            #     ask = "Are you feeling any better? Do you want to connect to doctor?"
            #     msg = ask
            # else:
            #     tell = "Sure, I'll ask you again in couple of hours."
            msg = tell
            # TODO save ask_in_hour as true so that when flow comes here it pitches "Are you feeling better..."

        elif intent == 'affirm':
            dg.updatePatientStatus(name, phone, 'Not well')
            status = "need_doctor"
            tell = " Sure, please type a message to doctor."
            msg = tell

        else:
            # Unknown response form patient
            msg = "Sorry, I can't get you, please repeat."
            status = None

        dispatcher.utter_message(text=msg)
        return {'ask_doctor': status}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        logger.info(f"[{tracker.sender_id}] {__file__} : submit of  FormMissingWorkoutInfo ")
        name, phone = get_name_phone(tracker)
        # we are here because patient is not feeling well. So need to update the DB accordingly.
        dg.addToDB(name, phone)

        return [FollowupAction('action_missing_pre_breakfast_info')]


class FormMissingDayInfo(FormAction):
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
        return "form_missing_day_info"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["log_symptoms", 'symptoms', 'vitals']

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        return {
                "log_symptoms": self.from_text(),
                "symptoms": self.from_text(),
                "vitals": self.from_text()
                }

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        intent = tracker.latest_message['intent'].get('name')
        name, phone = get_name_phone(tracker)
        log_symptoms = tracker.get_slot('log_symptoms')
        symptoms = tracker.get_slot('symptoms')
        vitals = tracker.get_slot('vitals')
        bt_sub_flow = tracker.get_slot('bt_sub_flow')
        logger.info(f"[{tracker.sender_id}] {__file__}request_next_slot of FormMissingDayInfo | log_symptoms : {log_symptoms} |  symptoms : {symptoms} |  vitals : {vitals}")

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.info(f"[{tracker.sender_id}] {__file__} request_next_slot of FormMissingDayInfo | slot : {slot} |  bt_sub_flow: {bt_sub_flow} |intent : {intent}")

                # utter template and request slot
                tell = ""
                remind = ""
                recommend = ""

                if slot == "log_symptoms":
                    self._current_round = bt_sub_flow

                    ask = f"Please enter your symptoms and vitals for {bt_sub_flow}."
                    buttons = button_it(_ok_not_ok_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "symptoms":
                    ask = f"Are you having/feeling {self._symptom_name} ?"
                    buttons = button_it(_yes_no_2_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "vitals":
                    ask = f'What is the reading of your {self._vital_name} ?'
                    dispatcher.utter_message(text=ask)

                return [SlotSet("requested_slot", slot)]
        return None

    def validate_log_symptoms(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        intent = tracker.latest_message['intent'].get('name')
        ret_slots = {'log_symptoms': 'complete'}
        bt_sub_flow = tracker.get_slot('bt_sub_flow')
        name, phone = get_name_phone(tracker)

        logger.info(f"[{tracker.sender_id}] {__file__} : validate_log_symptoms :  text : {value} | missing flow : {bt_sub_flow} | intent : {intent}")
        msg = ""

        if intent == 'deny':
            ret_slots['symptoms'] = 'completed'
            ret_slots['vitals'] = 'completed'
            ret_slots['symptoms'] = 'completed'
        else:
            self._current_round = bt_sub_flow
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
        logger.info(f"{__file__} : validate_symptoms :  text : {value} ")

        # store the value of current symptom and make the next symptom as current symptom
        # if symptom list is empty then log all the symptoms
        sym = self._symptoms.pop()
        # Assigning the input value to the symptom
        sym[1] = value

        if len(self._symptoms) == 0:
            # no symptoms left to monitor, so mark the slot as completed
            logger.info(f"{__file__} : validate_symptoms :  updated all symptoms ")
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
        logger.info(f"{__file__} : validate_vitals :  text : {value}")
        # store the value of current symptom and make the next symptom as current symptom
        # if symptom list is empty then log all the symptoms
        vital = self._vitals.pop()
        # Assigning the input value to the vital
        vital[1] = value

        if len(self._vitals) == 0:
            # no vitals left to monitor, so mark the slot as completed
            # logger.info(f"{__file__} : validate_vitals :  update values for all vitals")
            return {"vitals": 'completed'}
        else:
            self._vital_name = dg.getMedItemName(self._vitals[-1])
            return {"vitals": None}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        bt_sub_flow = tracker.get_slot('bt_sub_flow')
        logger.info(f"{__file__} : submit of FormMissingDayInfo |  bt_sub_flow : {bt_sub_flow}  completed")

        name, phone = get_name_phone(tracker)
        dg.addToDB(name, phone)

        # tell = f"Thanks for updating your missing Vitals and Symptoms !!\n\n"
        # # tell += f" symptoms = {symptoms} , vitals = {vitals}"
        # # data = {'symptoms': symptoms, 'vitals': vitals}
        # # update the DB with symptoms and vitals
        #
        # dispatcher.utter_message(text=tell)

        # decide the next action to be executed
        if bt_sub_flow == 'workout':
            return [FollowupAction('action_missing_pre_breakfast_info')]
        if bt_sub_flow == 'pre_breakfast':
            return [FollowupAction('action_missing_post_breakfast_info')]
        if bt_sub_flow == 'post_breakfast':
            return [FollowupAction('action_missing_pre_lunch_info')]
        if bt_sub_flow == 'pre_lunch':
            return [FollowupAction('action_missing_post_lunch_info')]
        if bt_sub_flow == 'post_lunch':
            return [FollowupAction('action_missing_pre_dinner_info')]
        if bt_sub_flow == 'pre_dinner':
            return [FollowupAction('action_missing_post_dinner_info')]
        if bt_sub_flow == 'post_dinner':
            return [FollowupAction('action_good_night')]
        if bt_sub_flow == 'bed_time':
            return []
        return []


class FormSOS(FormMissingDayInfo):

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_sos"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["log_symptoms", 'symptoms', 'vitals', 'sos_medicine']

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        return {
                "log_symptoms": self.from_text(),
                "symptoms": self.from_text(),
                "vitals": self.from_text(),
                "sos_medicine": self.from_text()
                }

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        intent = tracker.latest_message['intent'].get('name')
        name, phone = get_name_phone(tracker)

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.info(f" {tracker.sender_id} request_next_slot of FormSOS | slot : {slot} |  intent : {intent}")
                bt_sub_flow = tracker.get_slot('bt_sub_flow')

                # utter template and request slot
                tell = ""
                remind = ""
                recommend = ""
                if slot == "log_symptoms":
                    self._current_round = bt_sub_flow

                    ask = f"Please enter your symptoms and vitals for {bt_sub_flow}."
                    buttons = button_it(_ok_not_ok_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "symptoms":
                    ask = f"Are you having/feeling {self._symptom_name} ?"
                    buttons = button_it(_yes_no_2_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                elif slot == "vitals":
                    ask = f'what is the reading of your {self._vital_name} ?'
                    dispatcher.utter_message(text=ask)

                elif slot == "sos_medicine":
                    ask = f'Did you take SOS medicine today ?'
                    buttons = button_it(_yes_no_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                return [SlotSet("requested_slot", slot)]
        return None

    def validate_sos_medicine(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        intent = tracker.latest_message['intent'].get('name')
        ret = None
        name, phone = get_name_phone(tracker)
        if intent == 'affirm':
            ret = 'Yes'
            # update SOS when it is given to the patient
            sos = dg.getSOSMedicines(name, phone)
            if sos is not None:
                sos[1] = ret
        elif intent == 'deny':
            ret = 'No'

        return {'sos_medicine': ret}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        logger.info(f"[{tracker.sender_id}] {__file__} : submit of  form_sos ")
        # we are here because patient is not feeling well. So need to update the DB accordingly.
        name, phone = get_name_phone(tracker)
        dg.addToDB(name, phone)

        # symptoms = tracker.get_slot('symptoms')
        # vitals = tracker.get_slot('vitals')
        # sos_medicine = tracker.get_slot('sos_medicine')

        # dispatcher.utter_message(text=tell)
        return [FollowupAction('action_missing_workout_info')]


class ActionMissingPreBreakfastInfo(Action):
    def name(self) -> Text:
        return "action_missing_pre_breakfast_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name, phone = get_name_phone(tracker)

        sender = tracker.sender_id
        logger.info(f"[{tracker.sender_id}] {__file__} : action_missing_pre_breakfast_info ")

        s = dg.getSymptoms(name, phone, round_type='pre_breakfast')
        v = dg.getVitals(name, phone, round_type='pre_breakfast')
        # check if any missing info is thee in symptoms ot vitals
        if not dg.isInfoMissing(name, phone, s) and not dg.isInfoMissing(name, phone, v):
            # call the next action in the flow, i.e post breakfast
            return [SlotSet('bt_sub_flow', 'post_breakfast'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('action_missing_post_breakfast_info')]
        else:
            tell = "During the morning pre-meal you missed out on reporting your medicine, symptoms and vitals. Please share the information so that we can plan your treatment in a better way.\n"
            dispatcher.utter_message(text=tell)

            return [SlotSet('bt_sub_flow', 'pre_breakfast'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('form_missing_day_info')]


class ActionMissingPostBreakfastInfo(Action):
    def name(self) -> Text:
        return "action_missing_post_breakfast_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name, phone = get_name_phone(tracker)

        sender = tracker.sender_id
        logger.info(f"[{tracker.sender_id}] {__file__} : action_missing_post_breakfast_info ")
        s = dg.getSymptoms(name, phone, round_type='post_breakfast')
        v = dg.getVitals(name, phone, round_type='post_breakfast')
        # check if any missing info is thee in symptoms ot vitals
        if not dg.isInfoMissing(name, phone, s) and not dg.isInfoMissing(name, phone, v):
            # call the next action in the flow, i.e pre lunch
            return [SlotSet('bt_sub_flow', 'pre_lunch'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('action_missing_pre_lunch_info')]
        else:
            tell = "During the morning post-meal you missed out on reporting your medicine, symptoms and vitals. Please share the information so that we can plan your treatment in a better way.\n"
            dispatcher.utter_message(text=tell)
            return [SlotSet('bt_sub_flow', 'post_breakfast'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('form_missing_day_info')]


class ActionMissingPreLunchInfo(Action):
    def name(self) -> Text:
        return "action_missing_pre_lunch_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name, phone = get_name_phone(tracker)

        sender = tracker.sender_id
        logger.info(f"[{tracker.sender_id}] {__file__} : action_missing_pre_lunch_info ")
        s = dg.getSymptoms(name, phone, round_type='pre_lunch')
        v = dg.getVitals(name, phone, round_type='pre_lunch')
        # check if any missing info is thee in symptoms ot vitals
        if not dg.isInfoMissing(name, phone, s) and not dg.isInfoMissing(name, phone, v):
            # call the next action in the flow, i.e post lunch
            return [SlotSet('bt_sub_flow', 'post_lunch'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('action_missing_post_lunch_info')]
        else:
            tell = "During the Midday pre-meal you missed out on reporting your medicine, symptoms and vitals. Please share the information so that we can plan your treatment in a better way.\n"
            dispatcher.utter_message(text=tell)
            return [SlotSet('bt_sub_flow', 'pre_lunch'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('form_missing_day_info')]


class ActionMissingPostLunchInfo(Action):
    def name(self) -> Text:
        return "action_missing_post_lunch_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name, phone = get_name_phone(tracker)

        sender = tracker.sender_id
        logger.info(f"[{tracker.sender_id}] {__file__} : action_missing_post_lunch_info ")
        s = dg.getSymptoms(name, phone, round_type='post_lunch')
        v = dg.getVitals(name, phone, round_type='post_lunch')
        # check if any missing info is thee in symptoms ot vitals
        if not dg.isInfoMissing(name, phone, s) and not dg.isInfoMissing(name, phone, v):
            # call the next action in the flow, i.e pre dinner
            return [SlotSet('bt_sub_flow', 'pre_dinner'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('action_missing_pre_dinner_info')]
        else:
            tell = "During the Midday pot-meal you missed out on reporting your medicine, symptoms and vitals. Please share the information so that we can plan your treatment in a better way.\n"
            dispatcher.utter_message(text=tell)
            return [SlotSet('bt_sub_flow', 'post_lunch'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('form_missing_day_info')]


class ActionMissingPreDinnerInfo(Action):
    def name(self) -> Text:
        return "action_missing_pre_dinner_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name, phone = get_name_phone(tracker)

        sender = tracker.sender_id
        logger.info(f"[{tracker.sender_id}] {__file__} : action_missing_pre_dinner_info ")
        s = dg.getSymptoms(name, phone, round_type='pre_dinner')
        v = dg.getVitals(name, phone, round_type='pre_dinner')
        # check if any missing info is thee in symptoms ot vitals
        if not dg.isInfoMissing(name, phone, s) and not dg.isInfoMissing(name, phone, v):
            # call the next action in the flow, i.e post dinner
            return [SlotSet('bt_sub_flow', 'post_dinner'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('action_missing_post_dinner_info')]
        else:
            tell = "During the Pre-Dinner you missed out on reporting your medicine, symptoms and vitals. Please share the information so that we can plan your treatment in a better way.\n"
            dispatcher.utter_message(text=tell)
            return [SlotSet('bt_sub_flow', 'pre_dinner'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('form_missing_day_info')]


class ActionMissingPostDinnerInfo(Action):
    def name(self) -> Text:
        return "action_missing_post_dinner_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name, phone = get_name_phone(tracker)

        sender = tracker.sender_id
        logger.info(f"[{tracker.sender_id}] {__file__} : action_missing_post_dinner_info ")
        s = dg.getSymptoms(name, phone, round_type='post_dinner')
        v = dg.getVitals(name, phone, round_type='post_dinner')
        # check if any missing info is thee in symptoms ot vitals
        if not dg.isInfoMissing(name, phone, s) and not dg.isInfoMissing(name, phone, v):
            # call the next action in the flow, i.e good night
            return [SlotSet('bt_sub_flow', 'good_night'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('action_good_night')]
        else:
            tell = "During the Post-Dinner you missed out on reporting your medicine, symptoms and vitals. Please share the information so that we can plan your treatment in a better way.\n"
            dispatcher.utter_message(text=tell)
            return [SlotSet('bt_sub_flow', 'post_dinner'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('form_missing_day_info')]


class ActionGoodNight(Action):
    def name(self) -> Text:
        return "action_good_night"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name, phone = get_name_phone(tracker)
        plan = dg.showTodaysPlan(name, phone)
        logger.info(f"[{tracker.sender_id}] {__file__} :  action_good_night \n {plan}")

        sender = tracker.sender_id
        name, phone = get_name_phone(tracker)
        tell = f"Thanks {name}! I have recorded your responses in your medical data logger.\n"
        tell += f"Good Night {name}! Sleep tight. I'll see you in the morning."
        dispatcher.utter_message(text=tell)
        return [Restarted()]
