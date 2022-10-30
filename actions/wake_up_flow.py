# from db.mongo import Person
# import sys
# sys.path.append("../")
# import logging
from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet, Restarted
# from datetime import datetime as dt, time
from utils.helper import *
from utils import diginurse_utils as dg
from actions.action_utils import get_name_phone, _ask_doctor_buttons, _sleep_type_buttons


class ActionImproveExperience(Action):

    def name(self) -> Text:
        return "action_last_sleep_night"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # sender = tracker.sender_id
        tell = ""
        # for e in tracker.events[::-1]:
        #     logger.info(f"{__file__} : event: {e} ")

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : action_last_sleep_night |  name : {name} | phone : {phone}")

        status = dg.getPatientStatus(name, phone)
        if status == 'Not well':
            tell = f"\n Yesterday you were {status.lower()}. Do you want to connect with your doctor ?"
        else:
            tell = "I'm glad to hear that."
        ask = "\nHow was your sleep last night ?"
        ask = tell + ask
        buttons = button_it(_sleep_type_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)

        return []


class ActionDoctorSupport(Action):
    def name(self) -> Text:
        return "action_ask_doctor_support"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : action_ask_doctor_support |  name : {name} | phone : {phone}")

        tell = "I'm sorry to hear that."
        tell += "\n\nIt is still early days in treatment....."
        ask = tell
        # TODO add remaining utterances till "No there is no need.......Yes please. That'll be great
        # TODO Add some signal in db so that next day we check that signal and ask "yesterday you were not feeling well ....bla bla....
        # For above two TODOS refer Regular Nursing Round right wing.
        dispatcher.utter_message(text=ask)
        return []


class ActionTestsFollowup(Action):
    def name(self) -> Text:
        """Unique identifier of the action"""
        return 'action_remind_test_followup'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender = tracker.sender_id
        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : action_remind_test_followup |  name : {name} | phone : {phone}")

        tests = dg.getTests(name, phone, 'all_day')
        followup = dg.isAnyFollowup(name, phone)
        if len(tests) == 0 and not followup:
            return []
        else:
            m1 = "I want to remind you about your schedule."
            if len(tests) != 0:
                m2 = "\nList of tests for the day."
                for item in tests:
                    m2 += "\n Medical test - " + dg.getMedItemName(item)
            if followup:
                m3 = "\nToday there is a scheduled followup with the doctor."

            ask = m1 + m2 + m3

            dispatcher.utter_message(text=ask)
            return []


class DoctorSupport(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "form_doctor_support"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["ask_doctor"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        return {"ask_doctor": self.from_text()}

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""
        name, phone = get_name_phone(tracker)

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.info(f"[{tracker.sender_id}] {__file__} : form_doctor_support |  name : {name} | phone : {phone} | slot : {slot}")

                # utter template and request slot
                if slot == "ask_doctor":
                    tell1 = "I'm sorry to hear that<br><br>"
                    tell2 = "\nIt is still early days in treatment....."
                    tell3 = "\nIf you are feeling high discomfort......"
                    tell4 = ""
                    ask_doctor = "\nDo you want to get in touch with doctor?"

                    treatment_level = dg.getTreatmentLevel(name, phone)

                    feeling = dg.getPatientStatus(name, phone)
                    if feeling is not None and feeling.lower() == 'not well':
                        logger.info(f"[{tracker.sender_id}] {__file__} :  Last checked status NOT Well !!")
                        tell4 = "\nYesterday, you were not feeling well ?"
                    else:
                        logger.info(f"[{tracker.sender_id}] {__file__} :  Last checked status WAS Well !!")

                    if treatment_level == "20%":
                        tell = tell1 + tell2 + tell3 + tell4
                    else:
                        tell = tell1 + tell3 + tell4

                    ask = tell + ask_doctor

                    buttons = button_it(_ask_doctor_buttons())
                    dispatcher.utter_message(text=ask, buttons=buttons)

                return [SlotSet("requested_slot", slot)]
        return None

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
            dg.updatePatientStatus(name, phone, 'Not well')

            status = "no_need"
            ask = "Sure, please let me know if your discomfort increases.\n"   # TODO save into db so that we can ask about this
            msg = ask
            yesterday_same_issue = False
            # tomorrow
        elif intent == "wait":
            dg.updatePatientStatus(name, phone, 'Not well')

            status = "wait"
            ask = "Sure, please let me know if your discomfort increases.\n"   # TODO save into db so that we can ask about this
            # # TODO patient asked to wait
            # yesterday_same_issue = True     # TODO load from db which is saved in previous if condition for next day
            # if yesterday_same_issue:
            #     ask = "Yesterday you were not feeling well. Do you want to ......"
            #     msg = ask
            # else:
            #     ask = "Sure, please let me know if you feel ...."
            msg = ask
        elif intent == "remind_me":
            # TODO How do we pitch this after an hour or so???

            dg.updatePatientStatus(name, phone, 'Not well')
            status = "wait_for_hour"
            tell = "Sure, I'll ask you again in couple of hours."
            # ask_in_hour = False     # TODO load from db by default this field is false
            # if ask_in_hour:
            #     ask = "Are you feeling any better? Do you want to connect to doctor?"
            #     msg = ask
            # else:
            #     tell = "Sure, I'll ask you again in couple of hours."
            msg = tell
            # TODO save ask_in_hour as true so that when flow comes here it pitches "Are you feeling better..."
        elif intent == 'affirm':
            status = "need_doctor"
            tell = " Sure, please type a message to doctor."
            msg = tell
        else:
            # TODO Unknown response form patient
            msg = "Sorry, I can't get you, please repeat."
            status = None

        dispatcher.utter_message(text=msg)
        return {'ask_doctor': status}

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:

        # we are here because patient is not feeling well. So need to update the DB accordingly.
        # dg.updatePatientStatus(name, phone, 'Not well')
        """Define what the form has to do
            after all required slots are filled"""
        ask_doctor = tracker.get_slot('ask_doctor')
        logger.info(f"[{tracker.sender_id}] {__file__} Submit of DoctorSupport |  ask_doctor : {ask_doctor}")
        if ask_doctor == 'need_doctor':
            return [Restarted()]

        return []
