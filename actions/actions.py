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
from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet, Restarted, FollowupAction, AllSlotsReset
# from datetime import datetime as dt, time
from utils.helper import *
from utils import diginurse_utils as dg
from actions.action_utils import _yes_no_buttons, get_name_phone, rounds, log_tracker_event, _frequency_buttons


class FetchRound(Action):

    def name(self) -> Text:
        return "action_round"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender = tracker.sender_id
        # start_round = dg.startingFlow(name, phone)
        start_round = 'invalid_round'
        name = None
        phone = None

        for e in tracker.events[::-1]:
            # logger.info(f"[{tracker.sender_id}] : event: {e} ")
            if e["event"] == "user":
                message_metadata = e["metadata"]
                name = message_metadata['name']
                phone = message_metadata['phone']
                start_round = message_metadata['flow']
                break
        if start_round not in rounds:
            start_round = "invalid_round"
        logger.info(f"[{sender}] {__file__} :  Found starting round ****************** : {start_round} , {name} , {phone}")

        return [SlotSet("round", start_round), SlotSet("name", name), SlotSet("phone", phone)]


class ActionComebackLater(Action):

    def name(self) -> Text:
        return "action_comeback_later"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tell = "Please come back when you have few minutes on your hand"
        dispatcher.utter_message(text=tell)

        return []


class ActionImproveExperience(Action):

    def name(self) -> Text:
        return "action_improve_experience"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        round = tracker.get_slot('round')
        # if round != 'configure':
        #     ask = "Got an Input out of the flow, Please start the flow again"
        #     dispatcher.utter_message(text=ask)
        #     return [Restarted()]

        sender = tracker.sender_id
        for each in tracker.events:
            logger.info(f" event : {each}")
        
        logger.info(f"{tracker.sender_id} {__file__} : Inside action_improve_experience ")
        # name, phone = get_name_phone(tracker)

        op = [("Yes you have", "Yes, you have my consent."), ("No you don't", "No, you don't have my consent.")]
        buttons = button_it(op)
        ask = "Do we have your consent to use this information to improve your experience ?"

        dispatcher.utter_message(text=ask, buttons=buttons)
        return []


class SleepTimeForm(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_sleep_time"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["wakeup_time", "sleep_time"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        return {
                "sleep_time": self.from_text(),
                "wakeup_time": self.from_text()
                }

    def _wakeup_times(self):
        return [
            "7:00-8:00 ",
            "8:00-9:00 ",
            "9:00-10:00 ",
            "10:00-11:00",
        ]

    def _sleep_times(self):
        return [
            "20:00-21:00 ",
            "21:00-22:00 ",
            "22:00-23:00 ",
            # "23:00-00:00 ",
        ]

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.info(f"{tracker.sender_id} {__file__} : Inside request_next_slot of form_sleep_time : slot : {slot}")

                # utter template and request slot
                if slot == "sleep_time":
                    buttons = self._sleep_times()
                    buttons = button_it(buttons)
                    ask = "When do you go to bed everyday?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                elif slot == "wakeup_time":
                    buttons = self._wakeup_times()
                    buttons = button_it(buttons)

                    ask = "When do you wake up in the morning?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                return [SlotSet("requested_slot", slot)]
        return None

    def validate_sleep_time(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate sleep_time value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} :  : text : {value} | intent : {intent}")
        if intent == "times":
            # Irfan
            # update sleep time field in db
            name, phone = get_name_phone(tracker)
            dg.updateSchedule(name, phone, bed_time=value)

            return {"sleep_time": value}
        else:
            return {"sleep_time": None}

    def validate_wakeup_time(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate wakeup_time value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} :  : text : {value} | intent : {intent}")
        if intent == "times":
            # Irfan
            # update wake time field in db
            name, phone = get_name_phone(tracker)
            dg.updateSchedule(name, phone, wakeup_time=value)
            return {"wakeup_time": value}
        else:
            return {"wakeup_time": None}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        sleep_time = tracker.get_slot('sleep_time')
        wakeup_time = tracker.get_slot('wakeup_time')
        logger.info(f"{tracker.sender_id} {__file__} : {sleep_time} and wake-up at {wakeup_time}.")

        # tell = f"\nGreat! I'll remember that you sleep at {sleep_time} and wake-up at {wakeup_time}."
        # tell += "\nNext is your meal timings."
        # dispatcher.utter_message(text=tell)
        return []


class MealTimeForm(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_meal_time"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["breakfast_time", "lunch_time", "dinner_time"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        
        return {"breakfast_time": self.from_text(),
                "lunch_time": self.from_text(),
                "dinner_time": self.from_text()
                }

    def _breakfast_times(self):
        wakeup_time = self.tracker.get_slot('wakeup_time')
        entities = self.tracker.latest_message['entities']
        logger.info(f"{__file__} : entities : {entities}")
        for entity in entities:
            if entity['entity'] == 'time':
                wakeup_time = entity['value']
                if len(wakeup_time) <= 2:
                    wakeup_time = wakeup_time + ":00"
                break
        logger.info(f"{__file__} : wakeup_time : {wakeup_time}")
        limit = 12
        
        # break_fast_times = get_time_diff(wakeup_time,limit,context="breakfast")

        break_fast_times = [
            "7:00-8:00 ",
            "8:00-9:00 ",
            "9:00-10:00 ",
            "10:00-11:00 ",
        ]

        logger.info(f"{__file__} : break_fast_times : {break_fast_times}")
        return break_fast_times

    def _lunch_times(self):
        break_fast_time = self.tracker.get_slot('breakfast_time')

        entities = self.tracker.latest_message['entities']
        logger.info(f"{__file__} : entities : {entities}")
        for entity in entities:
            if entity['entity'] == 'time':
                break_fast_time = entity['value']
                if len(break_fast_time) <= 2:
                    break_fast_time = break_fast_time + ":00"

                break
        limit = 4
        # lunch_times = get_time_diff(break_fast_time,limit,context="lunch")

        lunch_times = [
            "12:00-13:00 ",
            "13:00-14:00 ",
            "14:00-15:00 ",
        ]
        logger.info(f"{__file__} : lunch_times : {lunch_times}")
        return lunch_times

    def _dinner_times(self):
        entities = self.tracker.latest_message['entities']
        logger.info(f"{__file__} : entities : {entities}")
        # for entity in entities:
        #     if entity['entity'] == 'time':
        #         lunch_time = entity['value']
        limit = 11
        # dinner_times = get_time_diff(lunch_time,limit,context="dinner")

        dinner_times = [
            "19:00-20:00 ",
            "20:00-21:00 ",
            "21:00-22:00 ",
            "22:00-23:00 ",
        ]
        logger.info(f"{__file__} : dinner_times : {dinner_times}")

        return dinner_times

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""
        till_now = [{i: tracker.get_slot(i)} for i in self.required_slots(tracker)]
        logger.info(f"{tracker.sender_id} {__file__} : till now : {till_now}")
        self.tracker = tracker
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                # utter template and request slot
                logger.info(f"{tracker.sender_id} {__file__} : request_next_slot of form_meal_time |  sot : {slot}")

                if slot == "breakfast_time":
                    buttons = self._breakfast_times()
                    buttons = button_it(buttons)

                    ask = "<strong class=\"imp\">When do you generally have your breakfast?</strong>"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                elif slot == "lunch_time":
                    buttons = self._lunch_times()
                    buttons = button_it(buttons)

                    ask = "At what time you have your lunch?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                elif slot == "dinner_time":
                    buttons = self._dinner_times()
                    buttons = button_it(buttons)
                    ask = "Finally, when do you generally have your dinner?"
                    dispatcher.utter_message(text=ask, buttons=buttons)

                return [SlotSet("requested_slot", slot)]
        return None

    def validate_breakfast_time(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate breakfast_time value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        if intent == "times":
            # Irfan 
            # update breakfast time field in db
            name, phone = get_name_phone(tracker)
            dg.updateSchedule(name, phone, breakfast_time=value)
            return {"breakfast_time": value}
        else:
            return {"breakfast_time": None}

    def validate_lunch_time(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate lunch_time value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        if intent == "times":
            # Irfan 
            # update lunch time field in db
            name, phone = get_name_phone(tracker)
            dg.updateSchedule(name, phone, lunch_time=value)

            return {"lunch_time": value}
        else:
            return {"lunch_time": None}

    def validate_dinner_time(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate dinner_time value."""
        intent = tracker.latest_message['intent'].get('name')
        if intent == "times":
            # Irfan 
            # update dinner time field in db
            name, phone = get_name_phone(tracker)
            dg.updateSchedule(name, phone, dinner_time=value)

            return {"dinner_time": value}
        else:
            return {"dinner_time": None}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        breakfast_time = tracker.get_slot('breakfast_time')
        lunch_time = tracker.get_slot('lunch_time')
        dinner_time = tracker.get_slot('dinner_time')
        logger.info(f"{tracker.sender_id} {__file__} submit of form_meal_time |  breakfast_time={breakfast_time}, lunch_time={lunch_time} and dinner_time={dinner_time}.")

        # tell = f"Great! I'll remember that you eat at {breakfast_time}, {lunch_time} and {dinner_time}."
        # dispatcher.utter_message(text=tell)
        return []


class AskSmokeForm(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_ask_smoke"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["smoking", "smoke_freq"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        return {"smoking": self.from_text(),
                "smoke_freq": self.from_text()
                }

    def _smoke_freq(self):
        return [
            ("Daily", "Daily"),
            ("Frequently", "Frequently"),
            ("Occasionally", "Occasionally")
        ]

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):

                # utter template and request slot
                if slot == "smoking":
                    buttons = _yes_no_buttons()
                    buttons = button_it(buttons)
                    ask = "Do you smoke?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                elif slot == "smoke_freq":
                    buttons = self._smoke_freq()
                    buttons = button_it(buttons)

                    ask = "How often do you smoke?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                return [SlotSet("requested_slot", slot)]
        return None

    def validate_smoking(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate smoking value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        name, phone = get_name_phone(tracker)

        if intent == "affirm":
            # Irfan 
            # update smoking time field in db
            dg.updateSchedule(name, phone, smoke="Yes")

            return {"smoking": "Yes"}
        else:
            dg.updateSchedule(name, phone, smoke="No")
            return {"smoking": "No", "smoke_freq": "No"}

    def validate_smoke_freq(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate smoke_freq value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        if intent == "how_often":
            # Irfan 
            # update smoke time field in db
            name, phone = get_name_phone(tracker)
            dg.updateSchedule(name, phone, smoke=value)

            return {"smoke_freq": value}
        else:
            return {"smoke_freq": None}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        
        smoking = tracker.get_slot('smoking')
        smoke_freq = tracker.get_slot('smoke_freq')
        logger.info(f"{tracker.sender_id} {__file__} : smoking : {smoking} | smoke_freq : {smoke_freq}")
        return []
        

class AskDrinkForm(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "form_ask_drink"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["drinking", "drink_freq"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        
        return {"drinking": self.from_text(),
                "drink_freq": self.from_text(),
                }

    def _drink_freq(self):
        return [
            ("Daily", "Daily"),
            ("Frequently", "Frequently"),
            ("Occasionally", "Occasionally")
        ]
        
    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):

                # utter template and request slot
                if slot == "drinking":
                    buttons = _yes_no_buttons()
                    buttons = button_it(buttons)
                    ask = "Do you drink alcohol?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                elif slot == "drink_freq":
                    buttons = self._drink_freq()
                    buttons = button_it(buttons)

                    ask = "How often do you drink alcohol?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                return [SlotSet("requested_slot", slot)]
        return None

    def validate_drinking(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate drinking value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        name, phone = get_name_phone(tracker)
        if intent == "affirm":
            # Irfan 
            # update drinking time field in db
            dg.updateSchedule(name, phone, drink=value)
            return {"drinking": value}
        else:
            dg.updateSchedule(name, phone, drink="No")
            return {"drinking": "No", "drink_freq": "No"}

    def validate_drink_freq(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate drink_freq value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        if intent == "how_often":
            # Irfan 
            # update drink time field in db
            name, phone = get_name_phone(tracker)
            dg.updateSchedule(name, phone, drink=value)

            return {"drink_freq": value}
        else:
            return {"drink_freq": None}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        
        drinking = tracker.get_slot('drinking')
        drink_freq = tracker.get_slot('drink_freq')
        logger.info(f"{tracker.sender_id} {__file__} : drinking : {drinking} | drink_freq : {drink_freq}")
        return []
        

class AskWorkOutForm(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_ask_workout"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["workingout", "workout_freq", "intence"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        
        return {"workingout": self.from_text(),
                "workout_freq": self.from_text(),
                "intence": self.from_text()
                }

    def _workout_freq(self):
        return [
            ("Daily", "Daily"),
            ("Frequently", "Frequently"),
            ("Occasionally", "Occasionally")
        ]

    def _how_intence(self):
        return [
            ("No major exertion on body", "No major exertion on body"),
            ("Moderately Intense", "Moderately Intense"),
            ("Very Intense", "Very Intense")
        ]

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""
        till_now = [{i: tracker.get_slot(i)} for i in self.required_slots(tracker)]
        logger.info(f"{tracker.sender_id} {__file__} : till now : {till_now}")
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):

                # utter template and request slot
                if slot == "workingout":
                    buttons = _yes_no_buttons()
                    buttons = button_it(buttons)
                    ask = "Do you workout?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                elif slot == "workout_freq":
                    buttons = self._workout_freq()
                    buttons = button_it(buttons)

                    ask = "How often do you workout?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                elif slot == "intence":
                    buttons = self._how_intence()
                    buttons = button_it(buttons)

                    ask = "How intense is your workout session?"
                    dispatcher.utter_message(text=ask, buttons=buttons)
                return [SlotSet("requested_slot", slot)]
        return None

    def validate_workingout(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate workingout value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        name, phone = get_name_phone(tracker)
        if intent == "affirm":
            # Irfan 
            # update workout time field in db
            dg.updateSchedule(name, phone, workout=value)

            return {"workingout": value}
        else:
            logger.info("Workout No")
            dg.updateSchedule(name, phone, workout="No")
            return {"workingout": "No", "workout_freq": "No", "intence": "No"}

    def validate_workout_freq(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate workout_freq value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        name, phone = get_name_phone(tracker)
        if intent == "how_often":
            # Irfan 
            # update how_often workout field in db
            dg.updateSchedule(name, phone, workout=value)

            return {"workout_freq": value}
        else:
            return {"workout_freq": None}

    def validate_intence(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate intence value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"{tracker.sender_id} {__file__} : text : {value} | intent : {intent}")
        name, phone = get_name_phone(tracker)
        if intent == "how_intense":
            # Irfan 
            # update intence [low,high,medium] field in db
            dg.updateSchedule(name, phone, workout=value)

            return {"intence": value}
        else:
            return {"intence": None}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        name, phone = get_name_phone(tracker)
        workingout = tracker.get_slot('workingout')
        workout_freq = tracker.get_slot('workout_freq')
        intence = tracker.get_slot('intence')

        logger.info(f"{tracker.sender_id} {__file__} : workingout : {workingout} | workout_freq : {workout_freq} | intence : {intence}")
        show = dg.showSchedule(name, phone)
        logger.info(f"\n Schedule \n{show}")

        tell = "\nAwesome! Your diginurse is configured and ready to go. Let's start working to feel you better."
        tell += "\n\nYou can update the changes in your routine and life style just by chatting with me. \nFor example, just type - Change my breakfast time"
        dispatcher.utter_message(text=tell)
        return []
       
       
class ActionThankYou(Action):

    def name(self) -> Text:
        return "action_thank_you"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        ask = "Thank you, talk to me again."
        dispatcher.utter_message(text=ask)
        return []


# class ActionConfigured(Action):
#
#     def name(self) -> Text:
#         return "action_configured"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         # for each in tracker.events:
#         #     logger.info(f"{__file__} : each : {each}")
#
#         tell = "\nAwesome! Your diginurse is configured and ready to go. Let's start working to feel you better"
#         tell += "\n\nYou can update the changes in your routine and life style just by chatting with me. \nFor example, just type - Change my breakfast time"
#         dispatcher.utter_message(text=tell)
#         return []


class ActionRecommend(Action):

    def name(self) -> Text:
        return "action_recommend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside action_recommend")

        tell = "\nBased on your routine I recommend you following timings for your regular nursing rounds"
        tell += "\n\n"+dg.showNursingRounds(name, phone)
        tell += "\n\nDo you want to change timings of any regular nursing round?"

        # update the recommended Nursing round into the DB
        dg.addToDB(name, phone)

        buttons = _yes_no_buttons()
        buttons = button_it(buttons)

        dispatcher.utter_message(text=tell, buttons=buttons)

        return []


class ActionRecommenddeny(Action):

    def name(self) -> Text:
        return "action_deny_recommend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # for each in tracker.events:
        #     logger.info(f"{__file__} : each : {each}")
        name, phone = get_name_phone(tracker)

        tell = "Perfect! Everything is set for your quick recovery."
        dispatcher.utter_message(text=tell)
        dg.setNursingRounds(name, phone)
        dg.addToDB(name, phone)
        return []


class ActionAskChanges(Action):

    def name(self) -> Text:
        return "action_ask_changes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # for each in tracker.events:
        #     logger.info(f"{__file__} : each : {each}")
        # name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside action_ask_changes")

        ask = "Please type the task timings or lifestyle activity you want to change."
        ask += '\nFor example, Change my breakfast time'
        dispatcher.utter_message(text=ask)
        return []


class ActionChangeRoutine(Action):

    def name(self) -> Text:
        return "action_change_routine"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # for each in tracker.events:
        #     logger.info(f"{__file__} : each : {each}")
        # name, phone = get_name_phone(tracker)
        field = tracker.get_slot("routines")
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside action_change_routine |  routine {field}")
        name, phone = get_name_phone(tracker)

        event = None
        if field in ['bed', 'wakeup', 'lunch', 'dinner', 'breakfast']:
            event = FollowupAction('form_changes')
        elif field in ['smoking', 'drinking']:
            event = FollowupAction('form_behavior_changes')
        elif field == 'workout':
            if dg.getWorkoutStatus(name, phone) not in ['No', 'None', None]:
                event = FollowupAction('form_changes')
            else:
                dispatcher.utter_message(text="Sorry!!! There is no entry for your workout with us")
                return[]

        return [event]


class FormChanges(FormAction):
    """Example of a custom form action"""
    _time_clash = 0   # TODO :: create a enum as None , Clashing and Not-Clashing
    _time_clash_name = ""   # TODO :: create a enum as None , Clashing and Not-Clashing

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_changes"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["time"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""
        
        return {
                "time": self.from_text(),
                # "loop": self.from_text(),
                }

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""
        name, phone = get_name_phone(tracker)

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.info(f"[{tracker.sender_id}] {__file__} : Inside request_next_slot of FormChanges | slot = {slot}")
                log_tracker_event(tracker, logger)

                # utter template and request slot
                if slot == "change_field":
                    tell = "Please type the task timings or lifestyle activity you want to change."
                    tell += '\nFor example, Change my breakfast time'
                    dispatcher.utter_message(text=tell)

                elif slot == "time":
                    if self._time_clash == 1:
                        ask = f"\nThere is a clash with {self._time_clash_name} timing in your schedule."
                        ask += "\n\n\nPlease re-enter non conflicting time again."
                        self._time_clash = 0
                        dispatcher.utter_message(text=ask)
                    else:
                        field = tracker.get_slot("routines")
                        ask = f"What is your updated {field} time ?"
                        dispatcher.utter_message(text=ask)

                elif slot == "loop":
                    tell = "\nYour routine has been updated.\n"
                    tell += "\n"+dg.showNursingRounds(name, phone)
                    tell += "\nDo you want to change timings of any regular nursing rounds?"

                    ask = tell
                    buttons = _yes_no_buttons()
                    buttons = button_it(buttons)
                    dispatcher.utter_message(text=ask, buttons=buttons)

                return [SlotSet("requested_slot", slot)]
        return None

    # def validate_change_field(
    #         self,
    #         value: Text,
    #         dispatcher: CollectingDispatcher,
    #         tracker: Tracker,
    #         domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
    #     """Validate change_field value."""
    #     logger.info(f"[{tracker.sender_id}] {__file__} : Inside validate change field")
    #     intent = tracker.latest_message['intent'].get('name')
    #     logger.info(f"[{tracker.sender_id}] {__file__} : text : {value} | intent : {intent}")
    #     field = tracker.get_slot("routines")
    #     time = tracker.get_slot("time")
    #
    #     ret = dg.checkTimeRoutine(field)
    #     if ret is False:
    #         logger.info(f"[{tracker.sender_id}] {__file__} : Incorrect routines = {field} ")
    #         dispatcher.utter_message(f"Incorrect routine was entered")
    #         return {"change_field": None}
    #
    #     if intent == "change_time":
    #         logger.info(f"[{tracker.sender_id}] {__file__} : End of validate change field | change field = {field}, time = {time} ")
    #         return {"change_field": field, "time": time}
    #     else:
    #         logger.info(f"[{tracker.sender_id}] {__file__} : End of validate change field | change_filed = None ")
    #         return {"change_field": None}

    def validate_time(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate time value."""
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside validate time")
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} : text : {value} | intent : {intent}")
        name, phone = get_name_phone(tracker)

        if intent in ["times", "change_time"]:
            field = tracker.get_slot("routines")
            timing = tracker.get_slot("time")
            ret = 'No'
            # Irfan
            # check for clashes and update the time
            #  and return a name of the class timing
            if field is not None:
                ret = dg.checkTimeOverlap(name, phone, field, timing)
            if ret == "incorrect_time":
                logger.info(f"{__file__} : Incorrect input time, Please enter again ")
                dispatcher.utter_message(f"Incorrect input time, please enter in a 24 ht time format eg, 8:00 - 9:00 , 20:00-21:00")

                self._time_clash = 0   # TODO ::  No Clashing
                return {"time": None}
            elif ret == "incorrect_routine":
                logger.info(f"{__file__} : Incorrect input routine, Please enter again ")
                self._time_clash = 0   # TODO ::  No Clashing
                return {"time": None}
            elif ret is not None and ret != 'No':
                logger.info(f"{__file__} : There is an overlap with {ret} timings")
                # There is an overlap, print a message
                self._time_clash = 1   # TODO ::  Clashing
                self._time_clash_name = ret
                return {"time": None}
            else:
                logger.info(f"{__file__} : There is NO overlap with any timings, ret = {ret}")
                # There is no overlap
                self._time_clash = 0   # TODO :: Not-Clashing
                data = {f"{field}_time": timing}
                dg.updateRoundTimings(name, phone, **data)
                return {"time": str(timing)}
        else:
            logger.info(f"{__file__} : End of validate time")
            return {"time": None}

    # def validate_loop(
    #         self,
    #         value: Text,
    #         dispatcher: CollectingDispatcher,
    #         tracker: Tracker,
    #         domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]:
    #     """Define what the form has to do
    #         after all required slots are filled"""
    #     intent = tracker.latest_message['intent'].get('name')
    #     logger.info(f"[{tracker.sender_id}] {__file__} : Inside validate_loop | intent = {intent}")
    #
    #     if intent == "affirm":
    #         return {"change_field": None, "time": None, "loop": None}
    #     else:
    #         return {"loop": "no"}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        field = tracker.get_slot('change_field')
        time = tracker.get_slot('time')
        # loop = tracker.get_slot('loop')
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside submit form_changes | field : {field} | time : {time}")

        tell = "Your routine has been updated."
        dispatcher.utter_message(text=tell)
        return [SlotSet("time", None), FollowupAction('action_recommend')]


class FormBehaviorChanges(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "form_behavior_changes"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["frequency", "recheck", "frequency_again"]

    def slot_mappings(self):
        """A dictionary to map required slots to
            - an extracted entity"""

        return {
                "frequency": self.from_text(),
                "recheck": self.from_text(),
                "frequency_again": self.from_text(),
                }

    def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Dict]]:
        """Request the next slot and utter template if needed,
            else return None"""
        name, phone = get_name_phone(tracker)
        field = tracker.get_slot("routines")
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):

                logger.info(f"[{tracker.sender_id}] {__file__} : Inside request_next_slot of FormBehaviorChanges | routine = {field} | slot = {slot}")
                log_tracker_event(tracker, logger)

                # utter template and request slot
                if slot == "frequency":
                    if field == 'smoking':
                        ask = "How often do you smoke?"
                    elif field == 'drinking':
                        ask = "How often do you drink?"

                    dispatcher.utter_message(text=ask, buttons=button_it(_frequency_buttons()))

                elif slot == "recheck":
                    ask = "Do you want to change response ?"

                    dispatcher.utter_message(text=ask, buttons=button_it(_yes_no_buttons()))

                elif slot == "frequency_again":
                    if field == 'smoking':
                        ask = "How often do you smoke now?"
                    elif field == 'drinking':
                        ask = "How often do you drink now?"

                    dispatcher.utter_message(text=ask, buttons=button_it(_frequency_buttons()))

                return [SlotSet("requested_slot", slot)]
        return None

    def validate_frequency(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate change_field value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside validate frequency : {value} | intent : {intent}")
        field = tracker.get_slot("routines")
        name, phone = get_name_phone(tracker)

        old_value = dg.getRoutineFrequency(name, phone, field)
        if intent == "how_often":
            if value != old_value:
                dispatcher.utter_message(f"Thanks for updating your lifestyle. Your input has been successfully updated.")
                return {"frequency": value, "recheck": "completed", "frequency_again": value}
            else:
                dispatcher.utter_message(f"Seems like there is no change in your behavior.")
                return {"frequency": "recheck", "recheck": "completed", "frequency_again": None}
        else:
            logger.info(f"[{tracker.sender_id}] {__file__} : Incorrect input = {value}")
            return {"frequency": old_value}

    def validate_recheck(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate time value."""
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside validate_recheck | text : {value} | intent : {intent}")
        name, phone = get_name_phone(tracker)
        frequency = tracker.get_slot("frequency")

        if intent in ["affirm"]:
            return {"recheck": "again", "frequency_again": None}
        else:
            return {"recheck": "completed", "frequency_again": frequency}

    def validate_frequency_again(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate change_field value."""
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside validate validate_frequency_again")
        intent = tracker.latest_message['intent'].get('name')
        logger.info(f"[{tracker.sender_id}] {__file__} : text : {value} | intent : {intent}")
        field = tracker.get_slot("routines")
        name, phone = get_name_phone(tracker)

        return {"frequency_again": value}

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        field = tracker.get_slot("routines")
        frequency = tracker.get_slot('frequency_again')
        name, phone = get_name_phone(tracker)
        logger.info(f"[{tracker.sender_id}] {__file__} : Inside submit form_behavior_changes | field : {field} |  frequency : {frequency}")

        dg.setRoutineFrequency(name, phone, field, frequency)
        tell = "Your routine has been updated."
        dispatcher.utter_message(text=tell)

        return [SlotSet("frequency", None),  SlotSet("frequency_again", None), SlotSet("recheck", None), FollowupAction('action_recommend')]
