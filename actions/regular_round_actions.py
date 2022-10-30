
from db.mongo import Person
import sys
sys.path.append("../")
import logging
from typing import Any, Text, Dict, List, Optional, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import SlotSet, Restarted
from datetime import datetime as dt, time
from utils.helper import *
from utils import diginurse_utils as dg
from actions.action_utils import get_name_phone, _ask_doctor_buttons, _yes_no_buttons


# class ActionImproveExperience(Action):
#
#     def name(self) -> Text:
#         return "action_last_sleep_night"
#
#     def _sleep_type_buttons(self):
#         return [
#             ("Excellent", "Excellent"),
#             ("Good", "Good"),
#             ("Fair", "Fair"),
#             ("Terrible", "Terrible")
#         ]
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         sender = tracker.sender_id
#         tell = ""
#         # for e in tracker.events[::-1]:
#         #     logger.info(f"{__file__} : event: {e} ")
#
#         name, phone = get_name_phone(tracker)
#         logger.info(f"[{sender}] {__file__} : action_last_sleep_night |  name : {name} | phone : {phone}")
#
#         status = dg.getPatientStatus(name, phone)
#         if status == 'Not well':
#             tell = f"\n Yesterday you were {status.lower()}. Do you want to connect with your doctor?"
#         else:
#             tell = "I'm glad to hear that."
#         ask = "\nHow was your sleep last night?"
#         ask = tell + ask
#         buttons = button_it(self._sleep_type_buttons())
#         dispatcher.utter_message(text=ask, buttons=buttons)
#
#         return []
#
#
# class ActionDoctorSupport(Action):
#     def name(self) -> Text:
#         return "action_ask_doctor_support"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         sender = tracker.sender_id
#
#         tell = "I'm sorry to hear that."
#         tell += "\n\nIt is still early days in treatment....."
#         ask = tell
#         # TODO add remaining utterances till "No there is no need.......Yes please. That'll be great
#         # TODO Add some signal in db so that next day we check that signal and ask "yerterday you were not feeling well ....bla bla....
#         # For above two TODOS refer Regular Nursing Round right wing.
#         dispatcher.utter_message(text=ask)
#         return []
#
#
# class PrePostMeal(FormAction):
#     """Example of a custom form action"""
#     _symptoms_value = {}
#     _vitals_value = {}
#     _vitals = []
#     _symptoms = []
#     _vital_name = None
#     _symptom_name = None
#     _current_round = None
#
#     def name(self) -> Text:
#         """Unique identifier of the form"""
#         return "form_pre_post_meal"
#
#     @staticmethod
#     def required_slots(tracker: Tracker) -> List[Text]:
#         """A list of required slots that the form has to fill"""
#         return ["ask_medication", "log_symptoms", 'symptoms', 'vitals']
#
#     def slot_mappings(self):
#         """A dictionary to map required slots to
#             - an extracted entity"""
#
#         return {
#                 "ask_medication": self.from_text(),
#                 "log_symptoms": self.from_text(),
#                 "symptoms": self.from_text(),
#                 "vitals": self.from_text()
#                 }
#
#     def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
#         """Request the next slot and utter template if needed,
#             else return None"""
#
#         intent = tracker.latest_message['intent'].get('name')
#         name, phone = get_name_phone(tracker)
#
#         for slot in self.required_slots(tracker):
#             if self._should_request_slot(tracker, slot):
#                 logger.info(f" request_next_slot of PrePostMeal | slot : {slot} |  intent : {intent}")
#
#                 # utter template and request slot
#                 tell = ""
#                 remind = ""
#                 recommend = ""
#                 if slot == "ask_medication":
#                     if intent == "all_fine":
#                         tell = "Great! lets keep working on your ......"
#                     elif intent == "worse":
#                         tell = "I'm sorry I hope it'll get better ...."
#
#                     self._current_round = 'breakfast'
#                     # self._current_round = dg.getCurrentRound(name, phone)
#
#                     followup_test = dg.getTests(name, phone, self._current_round)
#                     restrictions = dg.getDietRecomendation(name, phone)
#                     if followup_test is not None:
#                         s = ""
#                         for item in followup_test:
#                             s += "\n take " + dg.getMedItemName(item)
#                         remind = f"I want to remind you about your scheduled {s} ..."
#                     if restrictions is not None:
#                         recommend = f"Your doctor has recommended you {restrictions} "
#                     else:
#                         treatment = "body checkup"  # TODO load from db
#                         remind = f"You have {treatment} scheduled for today please do not eat anything ..."
#
#                     msg = tell + remind + recommend
#                     pre_post = self._current_round
#                     medication = f"{pre_post} meal medication "
#
#                     lst = dg.getMedicines(name, phone, self._current_round)
#                     s = "\n"
#                     for item in lst:
#                         s += "\n take " + dg.getMedItemName(item)
#                     lst = dg.getVitals(name, phone, self._current_round)
#                     for item in lst:
#                         s += "\n measure " + dg.getMedItemName(item)
#                     lst = dg.getSymptoms(name, phone, self._current_round)
#                     for item in lst:
#                         s += "\n check your " + dg.getMedItemName(item)
#
#                     medication += s
#                     medication += f"\n\nHave you taken all {pre_post} meal medication ?"
#
#                     remind_after_some_time = False  # TODO load from db
#                     if remind_after_some_time:
#                         tell = "Sure, I'll remind you after some time"
#                         remind = ""
#                         recommend = ""
#                         medication = ""
#                     ask = tell + remind + recommend + medication
#                     buttons = button_it(_yes_no_buttons())
#                     dispatcher.utter_message(text=ask, buttons=buttons)
#
#                 elif slot == "log_symptoms":
#
#                     # TODO load from db
#                     tell = "Are you ready to log your symptoms and vitals ?"
#                     remind_after_some_time = False
#
#                     if remind_after_some_time:
#                         tell = "Sure, I'll remind you after some time"
#                         # TODO :  need to implement the remind later action
#
#                     ask = tell
#                     buttons = button_it(_yes_no_buttons())
#                     dispatcher.utter_message(text=ask, buttons=buttons)
#
#                 elif slot == "symptoms":
#                     ask = f"Are you having/feeling {self._symptom_name} ?"
#                     buttons = button_it(_yes_no_buttons())
#                     dispatcher.utter_message(text=ask, buttons=buttons)
#
#                 elif slot == "vitals":
#                     ask = f'what is the reading of your {self._vital_name} ?'
#                     dispatcher.utter_message(text=ask)
#
#                 return [SlotSet("requested_slot", slot)]
#         return None
#
#     def validate_ask_medication(
#             self,
#             value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#
#         intent = tracker.latest_message['intent'].get('name')
#         name, phone = get_name_phone(tracker)
#
#         logger.info(f"{__file__} : validate_ask_medication :  text : {value} | intent : {intent}")
#         msg = ""
#         if intent in ["remained_me", "deny"]:
#             # TODO Asked to remind after some time but need to extract that time
#             # update remind field to True
#             tell = "Sure, let me know when you are ready"
#             dispatcher.utter_message(text=tell)
#
#             return {"ask_medication": "completed", 'log_symptoms': 'completed', 'symptoms': 'completed', 'vitals': 'completed'}
#         else:
#             # logging status of all med/vital/symptoms are taken/done/checked/completed
#             for item in dg.getMedicines(name, phone, self._current_round):
#                 item[1] = 'taken'
#         return {"ask_medication": "completed"}
#
#     def validate_log_symptoms(
#             self,
#             value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#
#         intent = tracker.latest_message['intent'].get('name')
#         ret_slots = dict()
#         name, phone = get_name_phone(tracker)
#
#         logger.info(f"{__file__} : validate_log_symptoms :  text : {value} | intent : {intent}")
#         msg = ""
#         if intent in ["remained_me", "deny"]:
#             # TODO Asked to remind after some time but need to extract that time
#             # update remind field to True
#             tell = "Sure, let me know when you are ready"
#             dispatcher.utter_message(text=tell)
#
#             return {'log_symptoms': ret_slots,  'symptoms': 'completed', 'vitals': 'completed'}
#
#         elif intent in ["affirm"]:
#             # user is ready to log symptoms and vitals
#
#             # self._current_round = dg.getCurrentRound(name, phone)
#             self._current_round = 'breakfast'       #######  TODO :  currently it is hardcoded need to remove it
#
#             # get the list of symptoms and vitals for logging purpose
#             if self._current_round is not None:
#                 self._symptoms = dg.getSymptoms(name, phone, self._current_round).copy()
#                 self._vitals = dg.getVitals(name, phone, self._current_round).copy()
#
#             if len(self._symptoms) == 0:
#                 # no symptoms left to monitor, so mark the slot as completed
#                 ret_slots['symptoms'] = 'completed'
#             else:
#                 self._symptom_name = dg.getMedItemName(self._symptoms[-1])
#
#             if len(self._vitals) == 0:
#                 # no vitals, so mark the vitals slot as completed
#                 ret_slots['vitals'] = 'completed'
#             else:
#                 self._vital_name = dg.getMedItemName(self._vitals[-1])
#
#         logger.info(f"{__file__} : end of validate_log_symptoms :  symptoms = {self._symptoms} | vitals = {self._vitals} ")
#         logger.info(f"{__file__} : end of validate_log_symptoms :  _symptom_name =  {self._symptom_name} | _vital_name = {self._vital_name}")
#         logger.info(f"{__file__} : end of validate_log_symptoms :  ret_slots =  {ret_slots} ")
#
#         return {'log_symptoms': ret_slots if len(ret_slots) == 0 else None}
#
#     def validate_symptoms(
#             self,
#             value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#
#         intent = tracker.latest_message['intent'].get('name')
#         logger.info(f"{__file__} : validate_symptoms :  text : {value} ")
#
#         # store the value of current symptom and make the next symptom as current symptom
#         # if symptom list is empty then log all the symptoms
#         sym = self._symptoms.pop()
#         # Assigning the input value to the symptom
#         sym[1] = value
#
#         if len(self._symptoms) == 0:
#             # no symptoms left to monitor, so mark the slot as completed
#             logger.info(f"{__file__} : validate_symptoms :  update all symptoms ")
#             return {"symptoms": 'completed'}
#         else:
#             self._symptom_name = self._symptoms[-1]
#             return {"symptoms": None}
#
#     def validate_vitals(
#             self,
#             value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#
#         # intent = tracker.latest_message['intent'].get('name')
#         logger.info(f"{__file__} : validate_vitals :  text : {value}")
#         # store the value of current symptom and make the next symptom as current symptom
#         # if symptom list is empty then log all the symptoms
#         vital = self._vitals.pop()
#         # Assigning the input value to the vital
#         vital[1] = value
#
#         if len(self._vitals) == 0:
#             # no vitals left to monitor, so mark the slot as completed
#             logger.info(f"{__file__} : validate_vitals :  update values for all vitals")
#             return {"vitals": 'completed'}
#         else:
#             self._vital_name = self._vitals[-1]
#             return {"vitals": None}
#
#     def submit(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict]:
#         """Define what the form has to do
#             after all required slots are filled"""
#
#         logger.info(f"{__file__} : submit of  PrePostMeal ")
#         # we are here because patient is not feeling well. So need to update the DB accordingly.
#         name, phone = get_name_phone(tracker)
#         dg.updatePatientStatus(name, phone, 'better')
#
#         ask_medication = tracker.get_slot('ask_medication')
#         log_symptoms = tracker.get_slot('log_symptoms')
#         symptoms = tracker.get_slot('symptoms')
#         vitals = tracker.get_slot('vitals')
#
#         tell = f"Thanks for updating your Vitals and Symptoms !!"
#         # tell += f" symptoms = {symptoms} , vitals = {vitals}"
#         # data = {'symptoms': symptoms, 'vitals': vitals}
#         # update the DB with symptoms and vitals
#         dg.addToDB(name, phone)
#
#         dispatcher.utter_message(text=tell)
#         return [Restarted()]
#
#
# class DoctorSupport(FormAction):
#     """Example of a custom form action"""
#
#     def name(self) -> Text:
#         """Unique identifier of the form"""
#         return "form_doctor_support"
#
#     @staticmethod
#     def required_slots(tracker: Tracker) -> List[Text]:
#         """A list of required slots that the form has to fill"""
#         return ["ask_doctor"]
#
#     def slot_mappings(self):
#         """A dictionary to map required slots to
#             - an extracted entity"""
#         return {"ask_doctor": self.from_text()}
#
#     def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
#         """Request the next slot and utter template if needed,
#             else return None"""
#         name, phone = get_name_phone(tracker)
#
#         for slot in self.required_slots(tracker):
#             if self._should_request_slot(tracker, slot):
#
#                 # utter template and request slot
#                 if slot == "ask_doctor":
#                     tell1 = "I'm sorry to hear that<br><br>"
#                     tell2 = "\nIt is still early days in treatment....."
#                     tell3 = "\nIf you are feeling high discomfort......"
#                     tell4 = ""
#                     ask_doctor = "\nDo you want to get in touch with doctor?"
#
#                     treatment_level = dg.getTreatmentLevel(name, phone)
#
#                     feeling = dg.getPatientStatus(name, phone)
#                     if feeling is not None and feeling.lower() == 'not well':
#                         logger.info(f"{__file__} :  Last checked status NOT Well !!")
#                         tell4 = "\nYesterday, you were not feeling well ?"
#                     else:
#                         logger.info(f"{__file__} :  Last checked status WAS Well !!")
#
#                     if treatment_level == "20%":
#                         tell = tell1 + tell2 + tell3 + tell4
#                     else:
#                         tell = tell1 + tell3 + tell4
#
#                     ask = tell + ask_doctor
#
#                     buttons = button_it(_ask_doctor_buttons())
#                     dispatcher.utter_message(text=ask, buttons=buttons)
#
#                 return [SlotSet("requested_slot", slot)]
#         return None
#
#     def validate_ask_doctor(
#             self,
#             value: Text,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#         """Validate ask_doctor value."""
#         intent = tracker.latest_message['intent'].get('name')
#         logger.info(f" {__file__} Inside validate_ask_doctor ::  text : {value} | intent : {intent}")
#         msg = ""
#         status = None
#         name, phone = get_name_phone(tracker)
#
#         if intent == "deny":
#             dg.updatePatientStatus(name, phone, 'Not well')
#
#             status = "no_need"
#             ask = "Sure, please let me know if your discomfort increases.\n"   # TODO save into db so that we can ask about this
#             msg = ask
#             yesterday_same_issue = False
#             # tomorrow
#         elif intent == "wait":
#             dg.updatePatientStatus(name, phone, 'Not well')
#
#             status = "wait"
#             ask = "Sure, please let me know if your discomfort increases.\n"   # TODO save into db so that we can ask about this
#             # # TODO patient asked to wait
#             # yesterday_same_issue = True     # TODO load from db which is saved in previous if condition for next day
#             # if yesterday_same_issue:
#             #     ask = "Yesterday you were not feeling well. Do you want to ......"
#             #     msg = ask
#             # else:
#             #     ask = "Sure, please let me know if you feel ...."
#             msg = ask
#         elif intent == "remind_me":
#             ## TODO How do we pitch this after an hour or so???
#
#             dg.updatePatientStatus(name, phone, 'Not well')
#             status = "wait_for_hour"
#             tell = "Sure, I'll ask you again in couple of hours."
#             # ask_in_hour = False     # TODO load from db by default this field is false
#             # if ask_in_hour:
#             #     ask = "Are you feeling any better? Do you want to connect to doctor?"
#             #     msg = ask
#             # else:
#             #     tell = "Sure, I'll ask you again in couple of hours."
#             msg = tell
#             # TODO save ask_in_hour as true so that when flow comes here it pitches "Are you feeling better..."
#         elif intent == 'affirm':
#             status = "need_doctor"
#             tell = " Sure, please type a message to doctor."
#             msg = tell
#         else:
#             ## TODO Unknown response form patient
#             msg = "Sorry, I can't get you, please repeat."
#             status = None
#
#         dispatcher.utter_message(text=msg)
#         return {'ask_doctor': status}
#
#     def submit(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict]:
#
#         # we are here because patient is not feeling well. So need to update the DB accordingly.
#         # dg.updatePatientStatus(name, phone, 'Not well')
#         """Define what the form has to do
#             after all required slots are filled"""
#         ask_doctor = tracker.get_slot('ask_doctor')
#         if ask_doctor == 'need_doctor':
#             return [Restarted()]
#
#         return []
