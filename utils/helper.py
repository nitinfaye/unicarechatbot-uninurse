from logging import getLogger
from datetime import datetime as dt

logger = getLogger()


def button_it(lists):
    buttons = []
    try:
        if not isinstance(lists[0], tuple):
            for i in lists:
                buttons.append(
                    {
                        "title": i,
                        "payload": i,
                    }
                )
        else:
            for i in lists:
                buttons.append({
                    "title": i[0],
                    "payload": i[1]
                })
        return buttons
    except Exception as e:
        logger.exception(e)


def hour_min_etc(time):
    time = time.split("-")[-1]
    try:
        time = dt.strptime(time, "%H:%M")
    except Exception as e:
        logger.exception("First try")
        logger.exception(e)
        try:
            time = dt.strptime(time, "%H:%M %p")
        except Exception as e:
            logger.exception("Second try")
            logger.exception(e)
    hour = time.strftime("%H")
    minute = time.strftime("%M")

    hour = int(hour)
    minute = int(minute)
    ampm = time.strftime("%p")
    if minute == 0:
        minute = "00"

    return hour, minute, ampm


def get_ampm(hour, context):
    
    """
        Returns AM or PM based on the hour given
    """
    logger.info(f"{__file__} : INSIDE get_ampm")
    logger.info(f"{__file__} : Hour : {hour}")
    logger.info(f"{__file__} : Context : {context}")
    if context == "sleep":
        if 8 <= hour <= 12:
            return "PM"
        elif 1 <= hour <= 12:
            return "AM"
    elif context == "breakfast":
        if hour > 11:
            return "PM"
        return "AM"
    elif context == "lunch":
        return "PM"
    elif context == "dinner":
        if 6 <= hour <= 12:
            return "PM"
        else:
            return "AM"
            

def get_time_diff(start, limit, context):
    """
        :start : start time Ex: wakeup time upper limit for breakfast time
        :limit : limit time Ex: for breakfast limit would be 12 PM
        :return : time difference between start and limit
    """
    logger.info(f"{__file__} : INSIDE get_time_diff")
    logger.info(f"{__file__} : Start : {start}")
    logger.info(f"{__file__} : Limit : {limit}")
    logger.info(f"{__file__} : Context : {context}")

    hour, minute, ampm = hour_min_etc(start)
    if limit < hour:
        limit = limit + 12
    if context == "breakfast":
        if hour < 6:
            hour = 6
    elif context == "lunch":
        if hour < 12:
            hour = 12
    elif context == "dinner":
        if hour < 7:
            hour = 7

    time_ranges = []
    for i in range(hour, limit + 1):
        
        if i == limit:
            break
        # if i == hour:
        
        if i < 12:
            # time_ranges.append(f"{i}:00-{i+1}:00 AM")
            time_ranges.append(f"{i}:{minute}-{i+1}:{minute} {get_ampm(i+1,context)}")
        elif i == 12:
            # time_ranges.append(f"{i}:00-{1}:00 PM")
            time_ranges.append(f"{i}:{minute}-{1}:{minute} {get_ampm(1,context)}")
        else:
            # time_ranges.append(f"{i-12}:00-{i-11}:00 PM")
            time_ranges.append(f"{i-12}:{minute}-{i-11}:{minute} {get_ampm(i-11,context)}")

    return time_ranges


def get_recommendation():
    """
        Returns the recommendation based on the persons health status given by doctor
    """
    logger.info(f"{__file__} : [INSIDE] get_recommendation")
    r = ["Morning Rounds", "Premeal", "Postmeal", "Mid Day Rounds", "Premeal", "Postmeal", "Evening Rounds", "Workout", "Premeal", "Postmeal", "Bedmeal"]
    t = {}
    for i in r:
        t[i] = "9:30"

    print(t)

    tell = "Based on your routine I recommend you following timings for your regular nursing rounds"

    for i, j in t.items():
        tell += f"<br><strong class=\"imp\">{i}</strong> : {j}"
    tell += "<br> Do you want to change the timings of any of your regular nursing rounds?"

    return tell
