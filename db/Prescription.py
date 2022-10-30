import enum
import json
import datetime
import collections
from datetime import timedelta

from db import medicalLogger as ML
from db import baseClass as Base


class Med_Time(enum.Enum):
    unknown = 0
    breakfast = 1
    lunch = 2
    dinner = 3
    SOS = 4


class MedRounds(Base.BaseSerializable):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.comment = kwargs.get('comment')
        self.frequency = kwargs.get('frequency') if kwargs.get('frequency') else 1
        self.duration = kwargs.get('duration') if kwargs.get('duration') else 1
        self.timing = kwargs.get('timing').strip().lower() if kwargs.get('timing') else None
        self.dt = kwargs.get('dt') if kwargs.get('dt') else datetime.date.today()
        self.status = kwargs.get('status') if kwargs.get('dt') else None

    def get(self):
        # s = f"{self.name} ({self.comment}) @ {self.timing.name}"
        s = f"{self.name} ({self.comment}) @ {self.timing}  with frequency {self.frequency} day(s)"
        return s

    def __str__(self):
        return self.get()

    def checkRoundType(self, round_type):
        if self.timing == round_type:
            return True
        else:
            return False

    def typeName(self):
        return "MedRounds"

    def setStatus(self,  status):
        self.status = status

    def getStatus(self):
        return self.status


class Medicine(MedRounds):
    def __init__(self, **kwargs):
        self.quantity = kwargs.get('quantity')
        # self.duration = kwargs.get('duration')
        # self.frequency = kwargs.get('frequency')
        super().__init__(**kwargs)

    def isMedicine(self):
        return True

    def get(self):
        s = f"{MedRounds.get(self)}  Quantity : {self.quantity} for {self.duration} days"
        return s

    def typeName(self):
        return "Medicine"


class SOSMedicine(Medicine):
    def __init__(self, **kwargs):
        # self.quantity = kwargs.get('quantity')
        self.timing = 'SOS'
        # self.duration = kwargs.get('duration')
        # self.frequency = kwargs.get('frequency')
        super().__init__(**kwargs)

    def isSOSMedicine(self):
        return True

    def get(self):
        s = f"{MedRounds.get(self)}  Quantity : {self.quantity} for {self.duration} days"
        return s

    def typeName(self):
        return "SOSMedicine"


class Test(MedRounds):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def isTest(self):
        return True

    def typeName(self):
        return "Test"


class Vital(MedRounds):
    def __init__(self, **kwargs):
        self.limit = kwargs.get('limit')
        super().__init__(**kwargs)

    def isVital(self):
        return True

    def get(self):
        s = f"{MedRounds.get(self)}  Limit : {self.limit}"
        return s

    def typeName(self):
        return "Vital"


class Symptom(MedRounds):
    def __init__(self, **kwargs):
        self.limit = kwargs.get('limit')
        super().__init__(**kwargs)

    def isSymptom(self):
        return True

    def typeName(self):
        return "Symptom"


class Excercise(MedRounds):
    def __init__(self, **kwargs):
        self.reps = kwargs.get('reps')
        self.gif = ["file:///F:/Projects/giphy.gif", "file:///F:/Projects/giphy.gif"]
        super().__init__(**kwargs)

    def isExcercise(self):
        return True

    def get(self):
        str_gif = ' '.join(self.gif)
        s = f"{MedRounds.get(self)}  Reps : {self.reps} Gif : {str_gif}"
        return s

    def typeName(self):
        return "Excercise"

    def getGIF(self):
        return self.gif


class Prescription(Base.BaseSerializable):
    def __init__(self, **kwargs):
        self.patient_name = kwargs.get('patient_name')
        self.dt = datetime.date.today()
        self.followup_dt = self.dt + timedelta(days=0)
        self.mobile_no = kwargs.get('mobile_no')
        self.dr_name = kwargs.get('dr_name')
        self.diagnosis = kwargs.get('diagnosis')
        self.diet_considerations = kwargs.get('diet_considerations')
        self.vitals = []              # List of vitals
        self.symptoms = []            # List of symptoms
        self.medicines = []             # List of medicines
        self.tests = []                 # List of Tests
        self.excersises = []            # List of Excercise
        self.medical_log = None         # Medical Data Logger
        self.feeling = kwargs.get('feeling')      # current overall condition of a patient, input by the patient
        self.workout_pain = kwargs.get('workout_pain')      # current overall condition of a patient, input by the patient
        self.plan = collections.defaultdict(list)

        if kwargs.get('medicines'):
            for l in kwargs.get('medicines'):
                # m = Medicine(**l)
                self.addMedicines(l)
        else:
            self.medicines = []     # List of medicine

        if kwargs.get('tests'):
            for l in kwargs.get('tests'):
                # m = Test(**l)
                self.addTest(l)
        else:
            self.tests = []         # List of test

        if kwargs.get('excersises'):
            for l in kwargs.get('excersises'):
                # m = Excercise(**l)
                self.addExcercise(l)
        else:
            self.excersises = []         # List of excersises

        if kwargs.get('vitals'):
            for l in kwargs.get('vitals'):
                # m = Vital(**l)
                self.addVital(l)
        else:
            self.vitals = []         # List of vitals

        if kwargs.get('symptoms'):
            for l in kwargs.get('symptoms'):
                # m = Symptom(**l)
                self.addSymptoms(l)
        else:
            self.symptoms = []         # List of symptoms

        if kwargs.get('medical_log'):
            self.medical_log = kwargs.get("medical_log")

        if kwargs.get('plan'):
            self.plan = kwargs.get('plan')

    def getFollowupDate(self):
        return self.followup_dt

    def updateFollowupDate(self, d):
        self.followup_dt = d

    def getWorkoutPain(self):
        return self.workout_pain

    def updateWorkoutPain(self, pain):
        self.workout_pain = pain

    def addFeeling(self, f):
        self.feeling = f

    def getFeeling(self):
        return self.feeling

    def addVital(self, v):
        self.vitals.append(v)
        self.addToPlan(v)

    def addSymptoms(self, s):
        self.symptoms.append(s)
        self.addToPlan(s)

    def addTest(self, t):
        self.tests.append(t)
        self.addToPlan(t)

    def addMedicines(self, d):
        self.medicines.append(d)
        self.addToPlan(d)

    def addExcercise(self, e):
        self.excersises.append(e)
        self.addToPlan(e)

    def addMedicalLog(self, ml: ML.MedicalLogs):
        self.medical_log = ml

    def getMedicalLog(self):
        return str(self.medical_log)

    # @staticmethod
    def getPrints(self, L):
        s = ""
        for i in L:
            s += i.get() + "\n"
        return s

    # @staticmethod
    def selectMedRounds(self, lst: [MedRounds], round_type=None) -> [MedRounds]:
        """
        :param lst:  List of Medical rounds of type Medicine/Test/Excersice/Vitals/Symptoms
        :param round_type:  Optional, it is the timing of MedRounds present in the list
                            if None then return all MedRounds in the list
        :return: List of Med rounds whose timing matche with 'round_type'
        """
        L = []
        if round_type is None:
            return lst
        else:
            for l in lst:
                if l.checkRoundType(round_type):
                    L.append(l)

        return L

    def getDietRecomendation(self):
        return self.diet_considerations

    def getMedDose(self):
        s = self.getPrints(self.medicines)
        return s

    def getMedDoseList(self, round_type=None):
        l = self.selectMedRounds(self.medicines, round_type)
        return l

    def getExcercise(self):
        s = self.getPrints(self.excersises)
        return s

    def getExcerciseList(self, round_type=None):
        l = self.selectMedRounds(self.excersises, round_type)
        return l

    def getVitals(self):
        s = self.getPrints(self.vitals)
        return s

    def getVitalsList(self, round_type=None):
        l = self.selectMedRounds(self.vitals, round_type)
        return l

    def getTests(self):
        s = self.getPrints(self.tests)
        return s

    def getTestsList(self, round_type=None):
        l = self.selectMedRounds(self.tests, round_type)
        return l

    def getSymptoms(self):
        s = self.getPrints(self.symptoms)
        return s

    def getSymptomsList(self, round_type=None):
        l = self.selectMedRounds(self.symptoms, round_type)
        return l

    def get(self):
        s = "Rx\n"
        s += f'Patient : {self.patient_name}  [{self.mobile_no}] diagnosed by {self.dr_name}\n'
        s += f'Diagnosis : {self.diagnosis}\n'
        s += self.getMedDose() + "\n"
        s += self.getTests() + "\n"
        s += self.getVitals() + "\n"
        s += self.getSymptoms() + "\n"
        s += self.getExcercise() + "\n"
        s += f"Pain during workout :  {str(self.getWorkoutPain())} \n"
        s += f'Diet suggestions : {str(self.diet_considerations)} \n'
        s += f'Follow Up Date :   {str(self.followup_dt)} \n'

        return s

    def __str__(self):
        return self.get()

    def jsonify(self):
        # json_data = json.dumps(self.__dict__, lambda o: o.__dict__, indent=4)
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)

    @staticmethod
    def loadRx(json_data):
        if json_data is not None:
            return Prescription(**json.loads(json_data))
        return None

    # def createPlan(self):
    #     for item in self.medicines:
    #         for i in range(1, item.duration+1):
    #             if i % item.frequency == 0:
    #                 self.plan[i].append(item)

    def addToPlan(self, item):
        offset = abs((item.dt - self.dt).days)
        for i in range(1, item.duration+1):
            if item.frequency == 1 or i % item.frequency == 1:
                lst = [item, None]
                self.plan[str(i+offset)].append(lst)

    def showPlan(self):
        for k in self.plan:
            for i in self.plan[k]:
                print(f"Day {k} : {str(i[0])} --> Status : {str(i[1])}")

    def getPlan(self, dt):
        """
        Function to get the schedule for a particular date. The difference will be taken from the date of Prescription

        :param date:
        :return:
        """
        offset = abs((dt - self.dt).days)
        offset = str(offset+1)
        if self.plan.get(offset):
            # for k in self.plan[offset]:
            #     print(f"Day {offset} : {str(k)}")
            return self.plan[offset]
        return []  # return empty list


if __name__ == '__main__':

    rx = Prescription(patient_name='Irfan124678', dr_name='Dr. Mehta', mobile_no=1234556789, diagnosis=' Headache', diet_considerations='no-Alcohol no-Smoke')
    med1 = Medicine(name='Med1', comment=' for fever', timing='breakfast', quantity=1, duration=5, frequency=1)
    med2 = Medicine(name='Med1', comment=' for fever', timing='lunch', quantity=1, duration=5, frequency=1)
    med3 = Medicine(name='Med2', comment=' for fever', timing='dinner', quantity=1, duration=5)
    med4 = Medicine(name='Med3', comment=' for fever', timing='dinner', quantity=1, duration=30, frequency=7)
    rx.addMedicines(med1)
    rx.addMedicines(med2)
    rx.addMedicines(med3)
    rx.addMedicines(med4)

    test1 = Test(name='Sugar Test', comment=' test for Diabetese', timing='breakfast')
    test2 = Test(name='Sugar Test', comment=' test for Diabetese', timing='Lunch')
    rx.addTest(test1)
    rx.addTest(test2)

    v1 = Vital(name='BP', comment=' blood pressure', timing='breakfast', limit='140')
    v2 = Vital(name='Temperature', comment=' fever', timing='Lunch', limit='98.6 C')
    rx.addVital(v1)
    rx.addVital(v2)

    s1 = Symptom(name='Nausea', comment=' feel like vomiting', timing='breakfast')
    s2 = Symptom(name='Weakness', comment=' feeling low', timing='Lunch')
    rx.addSymptoms(s1)
    rx.addSymptoms(s2)

    e1 = Excercise(name='Morning Walk', comment=' walking', timing='breakfast', reps=10)
    e2 = Excercise(name='Evening Walk', comment=' walking', timing='dinner', reps=10)
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

    # rx.addMedicalLog(m)
    # print(rx.medical_log.get())

    rx.showPlan()

    json_data = rx.storeJSON()
    print(json_data)

    data = Prescription.loadJSON(json_data)
    rx1 = Prescription(**data)
    rx1.showPlan()
    # print(rx1.medical_log.get())
    dt = datetime.date.today()

    for i in range(35):
        lst = rx1.getPlan(dt + datetime.timedelta(days=i))
        print(f" Got medication for Day {i}")
        for item in lst:
            item[1] = "Taken"
            print(item[0])

    json_data = rx1.storeJSON()
    print(json_data)

    data = Prescription.loadJSON(json_data)
    rx2 = Prescription(**data)
    rx2.showPlan()

    # get medicine to be taken during dinner
    lst = rx1.getPlan(dt + datetime.timedelta(days=1))
    for i in lst:
        item = i[0]     # 0th element is Medicine/Test/Vital/Symptom/Excercise
        if item.typeName() == 'Medicine' and item.timing == 'dinner':
            print(i[0])
