from db.mongo import Person
import sys
sys.path.append("../")
import logging
from typing import Any, Text, Dict, List, Optional, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import SlotSet, Restarted, AllSlotsReset, UserUtteranceReverted
from rasa_sdk.events import FollowupAction
from datetime import datetime as dt, time
from utils.helper import *
from utils import diginurse_utils as dg
from actions.action_utils import get_name_phone, _yes_no_buttons, _feel_better_buttons, log_tracker_event, save_conversation, save_convo


class ActionConfigureFlow(Action):

    def name(self) -> Text:
        return "action_configure_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} | Round : Configure |  name : {name} | phone : {phone}")
        dict = dg.getPatientDictionary(name, phone)
        for each in tracker.events:
            logger.info(f" event : {each}")

        dr_name = dict['dr_name']
        diagnosed = dict['diagnosed']

        m1 = f"Hello! {name}! {dr_name} has diagnosed you with {diagnosed}. Your DigiNurse will be with you through out the treatment period overseeing your recovery."
        m2 = "\n\nDuring your treatment period I'll assist you with keep track of your medications, logging your vitals and symptoms and provide you with recommendations on your diet and lifestyle"
        m3 = "\n\nAre you ready to setup your personalized nursing plan? It’ll only take few minutes."

        ask = m1 + m2 + m3

        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)

        return []


class ActionNewTreatmentFlow(Action):

    def name(self) -> Text:
        return "action_new_treatment_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} | Round : New Treatment |  name : {name} | phone : {phone}")
        dict = dg.getPatientDictionary(name, phone)
        for each in tracker.events:
            logger.info(f" event : {each}")

        hospital = dict['hospital_name']
        dr_name = dict['dr_name']
        diagnosed = dict['diagnosed']

        m1 = f"Dear {name}! during visit to {hospital}, {dr_name} has diagnosed with {diagnosed}"
        m2 = "\nDuring your treatment period I will help you to get recovered. I will assist you in keeping track of your medication, logging your vitals and symptoms and provide you with recommendations on your diet and lifestyle"
        m3 = "\nHere is the routine and lifestyle you have shared with me last time"
        m3 += "\n" + dg.showSchedule(name, phone)
        m3 += "\nHave you changed anything in your routine or lifestyle from last time?"

        ask = m1 + m2 + m3

        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)

        return []


class ActionWakeUpFlow(Action):

    def name(self) -> Text:
        return "action_wakeup_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} | Round : Wake Up |  name : {name} | phone : {phone}")
        for each in tracker.events:
            logger.info(f" event : {each}")

        m1 = f"Good Morning {name}! How are you feeling today ?"

        ask = m1

        buttons = button_it(_feel_better_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)

        return []


class ActionPREBreakFast(Action):
    def name(self) -> Text:
        return "action_pre_breakfast_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_pre_breakfast_flow |  name : {name} | phone : {phone}")
        for each in tracker.events:
            logger.info(f" event : {each}")

        m0 = "Your doctor has recommended " + dg.getDietRecomendation(name, phone)
        m1 = f"\nMorning Round: Pre-meal tasks. Please make sure that before your meal you."

        lst = dg.getMedicines(name, phone, 'pre_breakfast')
        s = "\n"
        for item in lst:
            s += "\n - take " + dg.getMedItemName(item)
        lst = dg.getVitals(name, phone, 'pre_breakfast')
        for item in lst:
            s += "\n - measure " + dg.getMedItemName(item)
        lst = dg.getSymptoms(name, phone, 'pre_breakfast')
        for item in lst:
            s += "\n - check your " + dg.getMedItemName(item)

        m2 = s + "\n"

        m3 = "\nYou can report your symptoms and vitals whenever you are ready.\n"

        ask = m0 + m1 + m2 + m3

        dispatcher.utter_message(text=ask)

        return []


class ActionPOSTBreakFast(Action):
    def name(self) -> Text:
        return "action_post_breakfast_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_post_breakfast_flow |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)

        m1 = "Morning Round: Post-meal medication "
        m2 = "\nHope you have taken your breakfast by now?"

        ask = m1 + m2
        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)
        return []


class ActionPRELunch(Action):
    def name(self) -> Text:
        return "action_pre_lunch_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_pre_lunch_flow |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)


        m0 = "Your doctor has recommended " + dg.getDietRecomendation()

        m1 = f"\nMidday Round: Pre-meal tasks. Please make sure that before your meal you."

        lst = dg.getMedicines(name, phone, 'pre_lunch')
        s = "\n"
        for item in lst:
            s += "\n take " + dg.getMedItemName(item)
        lst = dg.getVitals(name, phone, 'pre_lunch')
        for item in lst:
            s += "\n measure " + dg.getMedItemName(item)
        lst = dg.getSymptoms(name, phone, 'pre_lunch')
        for item in lst:
            s += "\n check your " + dg.getMedItemName(item)

        m2 = s + "\n"

        m3 = "You can report your symptoms and vitals whenever you are ready.\n"

        ask = m0 + m1 + m2 + m3

        dispatcher.utter_message(text=ask)

        return []


class ActionPOSTLunch(Action):
    def name(self) -> Text:
        return "action_post_lunch_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_post_lunch_flow |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)


        m1 = "Midday Round: Post-meal medication "
        m2 = "\nHope you have taken your lunch by now?"

        ask = m1 + m2
        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)
        return []


class ActionPREDinner(Action):
    def name(self) -> Text:
        return "action_pre_dinner_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_pre_dinner_flow |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)


        m0 = "Your doctor has recommended " + dg.getDietRecomendation()
        m1 = f"\nDinner Round: Pre-meal tasks. Please make sure that before your meal you."

        lst = dg.getMedicines(name, phone, 'pre_dinner')
        s = "\n"
        for item in lst:
            s += "\n take " + dg.getMedItemName(item)
        lst = dg.getVitals(name, phone, 'pre_dinner')
        for item in lst:
            s += "\n measure " + dg.getMedItemName(item)
        lst = dg.getSymptoms(name, phone, 'pre_dinner')
        for item in lst:
            s += "\n check your " + dg.getMedItemName(item)

        m2 = s + "\n"

        m3 = "You can report your symptoms and vitals whenever you are ready.\n"

        ask = m0 + m1 + m2 + m3

        dispatcher.utter_message(text=ask)

        return []


class ActionPOSTDinner(Action):
    def name(self) -> Text:
        return "action_post_dinner_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_post_dinner_flow |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)

        m1 = "Dinner Round: Post-meal medication "
        m2 = "\nHope you have taken your dinner by now?"

        ask = m1 + m2
        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)

        return []


class ActionPREWorkoutFlow(Action):
    def name(self) -> Text:
        return "action_pre_workout_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_pre_workout_flow |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)


        ask = "You must me gearing up for your workout session. Make sure you do not put high exertion on your body. 'Here are the GIfs of the exercises recommended by your doctor.' Try to follow these Gifs as much as possible while exercising."
        # gifs = dg.getWorkoutGIFs(name, phone)
        # s = ""
        # if len(gifs) != 0:
        #     for g in gifs:
        #         s += "\n" + g
        # else:
        #     s = "\nNo GIFs found"
        # ask += gifs
        dispatcher.utter_message(text=ask)

        return []


class ActionPOSTWorkoutFlow(Action):

    def name(self) -> Text:
        return "action_post_workout_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Round : action_post_workout_flow |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)

        ask = "Were you able to complete all the exercises in the prescribed by doctor?"

        buttons = button_it(_yes_no_buttons())
        dispatcher.utter_message(text=ask, buttons=buttons)

        return []


class ActionBedtimeFlow(Action):

    def name(self) -> Text:
        return "action_bed_time_flow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} | Round : Bedtime Round |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)

        m1 = f"Before going to bed, i want to have one last check on your symptoms."

        ask = m1

        dispatcher.utter_message(text=ask)

        return [SlotSet('bt_sub_flow', 'bed_time'), SlotSet("log_symptoms", None), SlotSet("symptoms", None), SlotSet("vitals", None), FollowupAction('form_sos')]


class ActionEndOfFlow(Action):

    def name(self) -> Text:
        return "action_restart"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} | End Of Flow  |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)
        save_conversation(tracker, logger)
        save_convo(tracker, logger)
        dispatcher.utter_message(text="EOC")
        return [Restarted(), AllSlotsReset()]
        # return []


class ActionOutOfContext(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} | Out-of-Context action  |  name : {name} | phone : {phone}")
        log_tracker_event(tracker, logger)

        ask = "Sorry !! I didn't get your input. Please re-try or start again"
        dispatcher.utter_message(text=ask)

        return [UserUtteranceReverted()]


# class ActionSessionStart(Action):
#     def name(self) -> Text:
#         return "action_session_start"
#
#     async def run(
#       self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:
#         metadata = tracker.get_slot("session_started_metadata")
#
#         # Do something with the metadata
#         print(metadata)
#
#         # the session should begin with a `session_started` event and an `action_listen`
#         # as a user message follows
#         return [SessionStarted(), ActionExecuted("action_listen")]
