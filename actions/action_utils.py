from utils.helper import *
import csv

rounds = [
    "configure",
    "new_treatment",
    "wake_up",
    "pre_breakfast",
    "post_breakfast",
    "pre_lunch",
    "post_lunch",
    "pre_workout",
    "post_workout",
    "pre_dinner",
    "post_dinner",
    "bed_time"
    ]


def get_name_phone(tracker):
    name = tracker.get_slot('name')
    phone = tracker.get_slot('phone')
    return name, phone


def _ok_not_ok_buttons():
    return [
        ("Ok", "Ok go ahead"),
        ("not Ok", "No"),
    ]


def _yes_no_buttons():
    return [
        ("Yes", "Yes"),
        ("No", "No"),
    ]


def _yes_no_2_buttons():
    return [
        ("Not at all", "Not at all"),
        ("Moderately", "Moderately"),
        ("Yes to a great extent", "Yes to a great extent"),
        ("Note Sure", "Note Sure"),
    ]


def _feel_better_buttons():
    return [
        ("I feel better", "I feel better"),
        ("I feel worse", "I feel worse"),
    ]


def _ask_doctor_buttons():
    return [
        ("No, there is no need", "No, there is no need"),
        ("No, I want to wait", "No, I want to wait"),
        ("No, I want to wait for couple of hours", "No, I want to wait for couple of hours"),
        ("Yes Please, that'll be great", "Yes Please, that'll be great")
    ]


def _pain_buttons():
    return [
        ("It has subsided", "It has subsided"),
        ("It is same/worse", "It is same/worse"),
    ]


def _sleep_type_buttons():
    return [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Fair", "Fair"),
        ("Terrible", "Terrible")
    ]


def _frequency_buttons():
    return [
        ("Daily", "Daily"),
        ("Frequently", "Frequently"),
        ("Occasionally", "Occasionally")
    ]


def log_tracker_event(tracker, logger):
    for each in tracker.events:
        # logger.info(each)
        if each['event'] in ['slot']:
            logger.info(f"{each['event']} : {each.get('name')} |  {each.get('value')} ")
        elif each['event'] in ['action', 'form']:
            logger.info(f"{each['event']} : {each.get('name')} ")
        elif each['event'] in ['user', 'bot']:
            logger.info(f"{each['event']} : {each.get('text')} ")


def save_conversation(tracker, logger):
    name, phone = get_name_phone(tracker)
    filename = f"{name}_{phone}_{tracker.sender_id}.txt"
    with open(filename, "w") as myfile:
        L = []

        for each in tracker.events:
            # logger.info(each)
            if each['event'] in ['slot']:
                L.append(f"{each['event']} : {each.get('name')} |  {each.get('value')} \n")
            elif each['event'] in ['action', 'form']:
                L.append(f"{each['event']} : {each.get('name')} \n")
            elif each['event'] in ['user', 'bot']:
                L.append(f"{each['event']} : {each.get('text')} \n")

        myfile.writelines(L)


def save_convo(tracker, logger):
    name, phone = get_name_phone(tracker)
    filename = f"{name}_{phone}_{tracker.sender_id}.csv"

    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile, delimiter="|")
        rows = []

        for each in tracker.events:
            # logger.info(each)
            if each['event'] in ['user', 'bot']:
                l = []
                l.append(each['event'])
                l.append(each['text'])
                rows.append(l)

        # writing the data rows
        csvwriter.writerows(rows)



