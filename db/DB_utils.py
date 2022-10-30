# Here we connect with MONGODB and create a sample DB
from pymongo import MongoClient
from random import randint
from db.Prescription import *
from db.Conversation import *
from functools import lru_cache

client = None
db_name = "business"
MONGODB_URL = 'mongodb://localhost:27017/'


@lru_cache(maxsize=512)
def getDB(db_name="business"):
    global client
    if client is None:
        client = MongoClient(MONGODB_URL)
    db = client.get_database(db_name)
    return db


def closeClient():
    global client

    if client is not None:
        client.close()


def removeAll():
    db = getDB(db_name)
    db.patient.remove({})


def removeOne(mobile_no):
    db = getDB(db_name)
    db.patient.delete_one({'mobile_no': mobile_no})
    print('Deleted Entry from DB')


def findAll():
    ' returns all the records( a dictionary) in the form of a list '
    db = getDB(db_name)

    cursor = db.patient.find({}, {'_id': 0})
    lst = []
    for record in cursor:
        lst.append(record)
    return lst


def findOne(data: dict):

    ' returns a single record if found else None'
    db = getDB(db_name)
    record = db.patient.find(data, {'_id': 0})
    if record.count():
        return record[0]
    else:
        return None


def count(db_name):
    db = getDB(db_name)
    return db.patient.count_documents({})


def addOne(input: dict, type='patient'):
    ret=None
    if type.lower() == "patient":
        ret = addOnePatient(input)
    elif type.lower() == 'convo':
        ret = addOneConvo(input)
    return ret


def addOnePatient(input: dict):
    db = getDB(db_name)
    res = db.patient.update_one({'name': input['name']}, {"$set": input}, upsert=True)
    if res.matched_count or res.modified_count:
        return True
    elif res.upserted_id is not None:
        return True
    else:
        return False


def addOneConvo(input: dict):
    db = getDB(db_name)
    res = db.conversation.update_one({'sender_id': input['sender_id']}, {"$set": input}, upsert=True)
    if res.matched_count or res.modified_count:
        return True
    elif res.upserted_id is not None:
        return True
    else:
        return False


def createSampleDB():
    db = getDB(db_name)

    names = ['Irfan', 'Saba', 'Prasanta', 'Nitin', 'Azra','Ramesh', 'Mahesh', 'Suresh', 'Dinesh', 'Rakesh', 'Rajesh']
    dr_name = ['Dr. Prasanta', 'Dr. Nitin', 'Dr. Khan', 'Dr. Gupta', 'Dr. Dutta']
    diagnosed = ['Diagnosis 1', 'Diagnosis 2', 'Diagnosis 3', 'Diagnosis 4']
    hospital_name = ['Apollo Hospital', 'Nawaz Hospital', 'Pulse Hospital', 'Greater Kailaash Hospital', 'Bombay Hospital']
    rx = createSampleRxDB()
    for x in range(1, 501):
        name = names[randint(0, (len(names)-1))]
        email = name.lower() + "@gmail.com"
        patient = {
            'name': name,
            'dr_name': dr_name[randint(0, (len(dr_name)-1))],
            'hospital_name': hospital_name[randint(0, (len(hospital_name)-1))],
            'diagnosed': diagnosed[randint(0, (len(diagnosed)-1))],
            'date_of_admission': '01-09-2021',
            'wakeup_time': '07:00 - 08:00',
            'bed_time': '22:00 - 23:00',
            'breakfast_time': '10:00 - 10:30',
            'lunch_time': '13:00 - 14:00',
            'dinner_time': '20:00 - 21:00',
            'smoke': False,
            'drink': False,
            'workout': False,
            'mobile_no': int (str( randint(1,9))+str( randint(0,9))+str( randint(0,9))+str( randint(0,9))+str( randint(0,9))+str( randint(0,9))+str( randint(0,9))+str( randint(0,9))+str( randint(0,9))+str( randint(0,9)) ),
            'email_id': email,
            'prescription': rx
        }

        print(patient)
        #Step 3: Insert business object directly into MongoDB via insert_one
        result=db.patient.insert_one(patient)
        #Step 4: Print to the console the ObjectID of the new document
        print('Created {0} of 500 as {1}'.format(x,result.inserted_id))
    #Step 5: Tell us that you are done
    print(f'finished creating {db.patient.count()} patient entries in the DB.')


def createSampleRxDB():
    rx = Prescription(patient_name='Irfan', dr_name='Dr. Mehta', mobile_no=1234556789, diagnosis=' Headache', diet_considerations='no-Alcohol no-Smoke')
    med1 = Medicine(name='Med1', comment=' for fever', timing='breakfast', quantity=1, duration=5)
    med2 = Medicine(name='Med1', comment=' for fever', timing='lunch', quantity=1, duration=5)
    med3 = Medicine(name='Med1', comment=' for fever', timing='dinner', quantity=1, duration=5)
    rx.addMedicines(med1)
    rx.addMedicines(med2)
    rx.addMedicines(med3)

    test1 = Test(name='Sugar Test', comment=' test for Diabetese', timing='breakfast')
    test2 = Test(name='Sugar Test', comment=' test for Diabetese', timing='Lunch')
    rx.addTest(test1)
    rx.addTest(test2)
    v1 = Vital(name='BP', comment=' blood pressure', timing='breakfast', limit='140')
    v2 = Vital(name='Temperature', comment=' feverr', timing='Lunch', limit='98.6 C')
    rx.addVital(v1)
    rx.addVital(v2)

    e1 = Excercise(name='Morning Walk', comment=' walking', timing='breakfast', reps=10)
    e2 = Excercise(name='Evening Walk', comment=' walking', timing='dinner', reps=10)
    rx.addExcercise(e1)
    rx.addExcercise(e2)

    return rx.jsonify()


def findOneConvo(sender_id):
    ' returns a single record if found else None'
    db = getDB("rasa")
    record = db.conversation.find({"sender_id": sender_id}, {'_id': 0})
    if record.count():
        return record[0]
    else:
        return None


def save_convo(sender_id):
    db = getDB("rasa")

    collection = db.get_collection('conversations')
    data = collection.find_one( {"sender_id": sender_id}, {"_id":0 , "events.event" :1, "events.text" :1})
    L = []
    for x in data["events"]:
        if x['event'] in ["user", "bot"]:
            L.append(f"{x['event']} : {x['text']}")
    return L


if __name__ == "__main__":
    # createSampleDB()
    L = save_convo("27189")
    for l in L:
        print(l)
