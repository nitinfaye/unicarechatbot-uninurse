# Here we have the Patient object that interacts with the database for updating and getting the patient data
import pandas as pd
import sys
import datetime
sys.path.append('../')
from db import DB_utils as DB
from db import Prescription as RX
from db import medicalLogger as ML


class Timing:
    def __init__(self, s):
        self.fmt = '%H:%M'
        if s is None or s == 'None':
            self.timing = None
        else:
            self.timing = self.set_time(s)

    def left(self):
        return self.timing.left.strftime(self.fmt) if self.timing else None

    def right(self):
        return self.timing.right.strftime(self.fmt) if self.timing else None

    def set_time(self, s):
        """
        :param s: is expected in the format as :  <start time H:M> - <end time H:M>
        :return:  object of Timestamp
        """
        lst = s.split("-")
        T = pd.Interval(pd.Timestamp(lst[0].strip()), pd.Timestamp(lst[1].strip()), closed='neither')
        return T

    def get_time(self):
        """
        :return: returns the Timestamp in string format or None
        """
        if self.timing is None:
            return 'None'
        T = self.timing
        s = T.left.strftime(self.fmt) + " - " + T.right.strftime(self.fmt)
        return s

    def __str__(self):
        s = self.get_time()
        return s

    def checkOverlap(self, other):
        if self.timing is None:
            return True
        if other.timing is None:
            return False
        return self.timing.overlaps(other.timing)


class Patient:
    def __init__(self, name, mobile_no, **kwargs):
        self.name = name
        self.mobile_no = mobile_no
        self.dr_name = None
        self.hospital_name = None
        self.diagnosed = None
        self.date_of_admission = None
        self.wakeup_time = None
        self.breakfast_time = None
        self.lunch_time = None
        self.dinner_time = None
        self.bed_time = None
        self.workout_time = None
        self.smoke = None
        self.drink = None
        self.workout = None
        self.email_id = None
        self.prescription = None

        # Nursing rounds timings of the day
        self.wakeup_round = None
        self.mid_day_round = None
        self.evening_round = None
        self.workout_round = None
        self.bed_round = None
        self.pre_breakfast_round = None
        self.post_breakfast_round = None
        self.pre_lunch_round = None
        self.post_lunch_round = None
        self.pre_dinner_round = None
        self.post_dinner_round = None

        # Search the DB with the name and mobile no.
        # if found then fetch up all the members from DB
        # else create a new object and add it to DB
        entry = DB.findOne({'name': name, 'mobile_no': mobile_no})
        if entry is not None:
            print(f'{name} and {mobile_no} exists in DB, fetch it !')
            self.name = name
            self.mobile_no = entry.get('mobile_no')
            self.dr_name = entry.get('dr_name')
            self.hospital_name = entry.get('hospital_name')
            self.diagnosed = entry.get('diagnosed')
            self.date_of_admission = entry.get('date_of_admission')
            self.email_id = entry.get('email_id')
            self.updateSchedule(wakeup_time=entry.get("wakeup_time"),
                                breakfast_time=entry.get("breakfast_time"),
                                lunch_time=entry.get("lunch_time"),
                                dinner_time=entry.get("dinner_time"),
                                bed_time=entry.get("bed_time"),
                                workout_time=entry.get("workout_time"),
                                smoke=entry.get("smoke"),
                                drink=entry.get("drink"),
                                workout=entry.get("workout"),
                                )
            rx_data = DB.Prescription.loadJSON(entry.get("rx"))
            self.prescription = DB.Prescription(**rx_data)
            # self.medical_log = DB.MedicalLogs.loadML(entry.get("medical_log"))

        else:
            print(f'{name} and {mobile_no} do not exists in DB, so create an entry')
            self.name = name
            self.mobile_no = mobile_no
            self.dr_name = kwargs.get('dr_name')
            self.hospital_name = kwargs.get('hospital_name')
            self.diagnosed = kwargs.get('diagnosed')
            self.date_of_admission = kwargs.get('date_of_admission')
            self.wakeup_time = Timing(kwargs.get('wakeup_time')) if kwargs.get('wakeup_time') is not None else None
            self.breakfast_time = Timing(kwargs.get('breakfast_time')) if kwargs.get('breakfast_time') is not None else None
            self.lunch_time = Timing(kwargs.get('lunch_time')) if kwargs.get('lunch_time') is not None else None
            self.dinner_time = Timing(kwargs.get('dinner_time')) if kwargs.get('dinner_time') is not None else None
            self.bed_time = Timing(kwargs.get('bed_time')) if kwargs.get('bed_time') is not None else None
            self.workout_time = Timing(kwargs.get('workout_time')) if kwargs.get('workout_time') is not None else None
            self.smoke = kwargs.get('smoke')
            self.drink = kwargs.get('drink')
            self.workout = kwargs.get('workout')
            self.email_id = kwargs.get('email_id')
            self.prescription = kwargs.get('rx')
            # self.medical_log = kwargs.get('ml')

            self.addToDB()

        # self.setNursingRounds()

    def showTimings(self):
        s = self.name + " \n"
        s += "Wakeup     @ " + str(self.wakeup_time) + " \n"
        s += "Breakfast  @ " + str(self.breakfast_time) + " \n"
        s += "Lunch      @ " + str(self.lunch_time) + " \n"
        s += "WorkOut    - " + str(self.workout_time) + " \n"
        s += "Dinner     @ " + str(self.dinner_time) + " \n"
        s += "Bed Time   @ " + str(self.bed_time) + " \n"
        s += "Smokes     - " + str(self.smoke) + " \n"
        s += "Alcohol    - " + str(self.drink) + " \n"
        return s

    def setNursingRounds(self):
        fmt = '%H:%M'
        round_duration = 30

        self.wakeup_round = self.wakeup_time.left() if self.wakeup_time else '8:00'
        self.bed_round = self.bed_time.left() if self.bed_time else '22:00'

        self.mid_day_round = "12:00"
        self.evening_round = '17:00'

        if self.breakfast_time is not None:
            t1 = self.breakfast_time.timing.left.to_pydatetime()
            t2 = t1 - datetime.timedelta(minutes=round_duration)
            t3 = self.breakfast_time.timing.right.to_pydatetime()
            t4 = t3 + datetime.timedelta(minutes=round_duration)
            t5 = t4 + datetime.timedelta(minutes=round_duration)

            t = f" {t2.strftime(fmt)} - {t1.strftime(fmt)  }"
            self.pre_breakfast_round = Timing(t)
            t = f" {t4.strftime(fmt)} - {t5.strftime(fmt)  }"
            self.post_breakfast_round = Timing(t)
        else:
            self.pre_breakfast_round = Timing("8:00 - 8:30")
            self.post_breakfast_round = Timing("9:30 - 10:00")

        if self.lunch_time is not None:
            t1 = self.lunch_time.timing.left.to_pydatetime()
            t2 = t1 - datetime.timedelta(minutes=round_duration)
            t3 = self.lunch_time.timing.right.to_pydatetime()
            t4 = t3 + datetime.timedelta(minutes=round_duration)
            t5 = t4 + datetime.timedelta(minutes=round_duration)

            t = f" {t2.strftime(fmt)} - {t1.strftime(fmt)  }"
            self.pre_lunch_round = Timing(t)
            t = f" {t4.strftime(fmt)} - {t5.strftime(fmt)  }"
            self.post_lunch_round = Timing(t)
        else:
            self.pre_lunch_round = Timing('12:30 - 13:00')
            self.post_lunch_round = Timing('14:00 - 14:30')

        if self.dinner_time is not None:
            t1 = self.dinner_time.timing.left.to_pydatetime()
            t2 = t1 - datetime.timedelta(minutes=round_duration)
            t3 = self.dinner_time.timing.right.to_pydatetime()
            t4 = t3 + datetime.timedelta(minutes=round_duration)
            t5 = t4 + datetime.timedelta(minutes=round_duration)

            t = f" {t2.strftime(fmt)} - {t1.strftime(fmt)  }"
            self.pre_dinner_round = Timing(t)
            t = f" {t4.strftime(fmt)} - {t5.strftime(fmt)  }"
            self.post_dinner_round = Timing(t)
        else:
            self.pre_dinner_round = Timing('19:50 - 20:00')
            self.post_dinner_round = Timing('21:00 - 21:30')

        if self.workout_time is not None:
            t1 = self.workout_time.timing.left.to_pydatetime()
            t2 = self.workout_time.timing.right.to_pydatetime()

            t = f" {t1.strftime(fmt)} - {t2.strftime(fmt)}"
            self.workout_round = Timing(t)
        else:
            self.workout_round = None

    def showNursingRounds(self):
        # Nursing rounds timings of the day
        s = "\nNursing Round Timings: \n"
        s += "\n Morning Round :"
        s += "\n\t Wakeup    @ " + str(self.wakeup_round)
        s += "\n\t Premeal   @ " + str(self.pre_breakfast_round.left())
        s += "\n\t Postmeal  @ " + str(self.post_breakfast_round.left())
        s += "\n Mid Day Round :"
        s += "\n\t Premeal   @ " + str(self.pre_lunch_round.left())
        s += "\n\t Postmeal  @ " + str(self.post_lunch_round.left())
        s += "\n Evening Round :"
        s += "\n\t Workout   @ " + str(self.workout_round.left()) if self.workout_round is not None else "None"
        s += "\n\t Premeal   @ " + str(self.pre_dinner_round.left())
        s += "\n\t Postmeal  @ " + str(self.post_dinner_round.left())
        s += "\n\t Bedtime   @ " + str(self.bed_round) + ' \n'

        return s

    def __str__(self):
        s = self.showTimings()
        return s

    def updateSchedule(self, **kwargs):
        if kwargs.get('wakeup_time') is not None and kwargs.get('wakeup_time') != 'None':
            self.wakeup_time = Timing(kwargs.get('wakeup_time'))
        if kwargs.get('breakfast_time') is not None and kwargs.get('breakfast_time') != 'None':
            self.breakfast_time = Timing(kwargs.get('breakfast_time'))
        if kwargs.get('lunch_time') is not None and kwargs.get('lunch_time') != 'None':
            self.lunch_time = Timing(kwargs.get('lunch_time'))
        if kwargs.get('bed_time') is not None and kwargs.get('bed_time') != 'None':
            self.bed_time = Timing(kwargs.get('bed_time'))
        if kwargs.get('dinner_time') is not None and kwargs.get('dinner_time') != 'None':
            self.dinner_time = Timing(kwargs.get('dinner_time'))
        if kwargs.get('smoke') is not None and kwargs.get('smoke') != 'None':
            self.smoke = kwargs.get('smoke')
        if kwargs.get('drink') is not None and kwargs.get('drink') != 'None':
            self.drink = kwargs.get('drink')
        if kwargs.get('workout') is not None and kwargs.get('workout') != 'None':
            self.workout = kwargs.get('workout')
        if kwargs.get('workout_time') is not None and kwargs.get('workout_time') != 'None':
            self.workout_time = Timing(kwargs.get('workout_time'))
        # self.setNursingRounds()

    def getWorkoutStatus(self):
        return self.workout, self.workout_time

    def updatePrescription(self, rx):
        if rx is not None:
            self.prescription = rx

    def addToDB(self):
        entry = {'name': self.name, 'dr_name': self.dr_name,
                 'hospital_name': self.hospital_name,
                 'diagnosed': self.diagnosed,
                 'date_of_admission': self.date_of_admission,
                 'wakeup_time': str(self.wakeup_time),
                 'breakfast_time': str(self.breakfast_time),
                 'lunch_time': str(self.lunch_time),
                 'dinner_time': str(self.dinner_time),
                 'bed_time': str(self.bed_time),
                 'workout': str(self.workout),
                 'smoke': self.smoke,
                 'drink': self.drink,
                 'mobile_no': self.mobile_no,
                 'rx': self.prescription.storeJSON(),
                 'email_id': self.email_id,
                 'wakeup_round': self.wakeup_round,
                 'mid_day_round': self.mid_day_round,
                 'evening_round': self.evening_round,
                 'workout_round': self.workout_round,
                 'bed_round': self.bed_round,
                 'pre_breakfast_round': str(self.pre_breakfast_round),
                 'post_breakfast_round': str(self.post_breakfast_round),
                 'pre_lunch_round': str(self.pre_lunch_round),
                 'post_lunch_round': str(self.post_lunch_round),
                 'pre_dinner_round': str(self.pre_dinner_round),
                 'post_dinner_round': str(self.post_dinner_round),
                 }
        try:
            ret = DB.addOne(entry)
            print('Patient updated into DB')
            return ret
        except Exception as e:
            print(f"Exception while inserting into db!! {e}")
            return False

    def checkOverlap(self, time1, time2):
        t1 = Timing(time1)
        t2 = Timing(time2)

        ret = t1.Timing(t2)
        return ret

    def showPrescription(self):
        return self.prescription.get()

    def getCurrentRound(self):
        # datetime object containing current date and time
        now = datetime.datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%H:%M")
        s = f"{dt_string} - {dt_string}"
        now = Timing(s)

        if self.pre_breakfast_round and self.pre_breakfast_round.checkOverlap(now):
            return 'pre_breakfast'
        elif self.breakfast_time and self.breakfast_time.checkOverlap(now):
            return 'breakfast'
        elif self.post_breakfast_round and self.post_breakfast_round.checkOverlap(now):
            return 'post_breakfast_round'
        elif self.pre_lunch_round and self.pre_lunch_round.checkOverlap(now):
            return 'pre_lunch_round'
        elif self.lunch_time and self.lunch_time.checkOverlap(now):
            return 'lunch_time'
        elif self.post_lunch_round and self.post_lunch_round.checkOverlap(now):
            return 'post_lunch_round'
        elif self.pre_dinner_round and self.pre_dinner_round.checkOverlap(now):
            return 'pre_dinner_round'
        elif self.dinner_time and self.dinner_time.checkOverlap(now):
            return 'dinner_round'
        elif self.post_dinner_round and self.post_dinner_round.checkOverlap(now):
            return 'post_dinner_round'
        elif self.bed_round and self.bed_round < now.left():
            return 'bed_time'

        return None


if __name__ == "__main__":
    # try:
    name = 'Saba'
###  Prescription
    rx = RX.Prescription(patient_name=name, dr_name='Dr. Mehta', mobile_no=1234556789, diagnosis=' Headache', diet_considerations='no-Alcohol no-Smoke')
    med1 = RX.Medicine(name='Med1', comment=' for fever', timing='breakfast', quantity=1, duration=5)
    med2 = RX.Medicine(name='Med1', comment=' for fever', timing='lunch', quantity=1, duration=5)
    med3 = RX.Medicine(name='Med1', comment=' for fever', timing='dinner', quantity=1, duration=5)
    rx.addMedicines(med1)
    rx.addMedicines(med2)
    rx.addMedicines(med3)

    test1 = RX.Test(name='Sugar Test', comment=' test for Diabetese', timing='breakfast')
    test2 = RX.Test(name='Sugar Test', comment=' test for Diabetese', timing='Lunch')
    rx.addTest(test1)
    rx.addTest(test2)

    s1 = RX.Symptom(name='Nausea', comment=' feel like vomiting', timing='breakfast')
    s2 = RX.Symptom(name='Weakness', comment=' feeling low', timing='Lunch')
    rx.addSymptoms(s1)
    rx.addSymptoms(s2)

    v1 = RX.Vital(name='BP', comment=' blood pressure', timing='breakfast', limit='140')
    v2 = RX.Vital(name='Temperature', comment=' feverr', timing='Lunch', limit='98.6 C')
    rx.addVital(v1)
    rx.addVital(v2)

    e1 = RX.Excercise(name='Morning Walk', comment=' walking', timing='breakfast', reps=10)
    e2 = RX.Excercise(name='Evening Walk', comment=' walking', timing='dinner', reps=10)
    rx.addExcercise(e1)
    rx.addExcercise(e2)


    ### Create Medical Logs
    m = ML.MedicalLogs(name=rx.patient_name, mobile_no=rx.mobile_no)
    data = {'item': rx.medicines[0].name, 'item_type': rx.medicines[0].typeName(), 'round_type': rx.medicines[0].timing, 'status': 'Taken'}
    log = ML.Log(**data)
    m.addLog(log)
    data = {'item': rx.medicines[1].name, 'item_type': rx.medicines[1].typeName(), 'round_type': rx.medicines[1].timing, 'status': 'Taken'}
    log = ML.Log(**data)
    m.addLog(log)

    rx.addMedicalLog(m)
###

    P = Patient(rx.patient_name, rx.mobile_no, rx=rx)
    print(P.showPrescription())

    P.updatePrescription(rx)
    # P.updateSchedule(breakfast_time='8:30 - 9:30', dinner_time='19:00 - 19:30')
    d = {'breakfast_time': '8:30 - 9:30', 'dinner_time': '19:00 - 19:30'}
    P.updateSchedule(**d)
    P.setNursingRounds()
    print(P.showNursingRounds())
    P.addToDB()
    print(P.showTimings())
    print(f'Total entries in DB = {DB.count()}')

    data = {'name': name, 'mobile_no': 1234567890}
    P1 = Patient(data['name'], data['mobile_no'], bed_time='20:00 - 21:00', rx=rx)
    # P1.updatePrescription(rx)

    print(P1.showTimings())
    P1.addToDB()
    print(f'Total entries in DB = {DB.count()}')

    # db = DB.getDB()
    # DB.removeAll(db)
    # DB.createDB(db)

    # DB.findAll(db)

    record = DB.findOne(data)
    if record is not None:
        print('Record found !!')
    else:
        print('Record not found')
    # except Exception as e:
    #     print(e)

    s = P.getCurrentRound()
    print(s)

    print(P.prescription.medical_log.get())
    DB.closeClient()
