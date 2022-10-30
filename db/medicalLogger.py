# Here we have the Patient object that interacts with the database for updating and getting the patient data
# import pandas as pd
import sys
import datetime
import json
from db import baseClass as Base


class Log(Base.BaseSerializable):
    def __init__(self, **kwargs):
        fmt = "%m/%d/%Y - %H:%M"
        self.dt = kwargs.get('dt') if kwargs.get('dt') else datetime.datetime.now().strftime(fmt)
        self.item = kwargs.get('item')              # name of the item
        self.item_type = kwargs.get('item_type')    # Medicine , Test , Vital , Symptom , Excercise
        self.round_type = kwargs.get('round_type')  # pre_breakfast, post_breakfast, pre_lunch , post_lunch, pre_dinner, post_dinner etc.
        self.status = kwargs.get('status')       # comments about te item taken/done/completed/No

    def get(self):
        s = f"{self.item} | {self.item_type} | {self.dt} | {self.round_type} |  {self.status}"
        return s


class MedicalLogs(Base.BaseSerializable):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')                   # name of the patient
        self.mobile_no = kwargs.get('mobile_no')         # mobile no of the patient
        self.logs = []              # list of logs

        if kwargs.get('logs'):
            lst = kwargs.get('logs')
            for l in lst:
                m = Log(**l)
                self.addLog(m)

    def addLog(self, log: Log):
        self.logs.append(log)

    def get(self):
        s = ""
        for l in self.logs:
           s += l.get() + "\n"
        return s

    def jsonify(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @staticmethod
    def loadML(json_data):
        if json_data is not None:
            return MedicalLogs(**json.loads(json_data))
        return None


if __name__ == '__main__':
    m = MedicalLogs(name='Irfan', mobile_no=123467890)
    data = {'item': 'Medicine1', 'item_type': 'Medicine', 'round_tpe': 'pre_lunch', 'status': 'Taken'}
    log = Log(**data)
    m.addLog(log)
    data = {'item': 'Medicine1', 'item_type': 'Medicine', 'round_tpe': 'pre_dinner', 'status': 'Taken'}
    log = Log(**data)
    m.addLog(log)

    s = m.get()
    print(s)

    json_data = m.jsonify()
    m1 = MedicalLogs.loadML(json_data)
    s = m1.get()
    print(s)
