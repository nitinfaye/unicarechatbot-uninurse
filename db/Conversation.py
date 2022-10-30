from db import DB_utils as DB
from db import baseClass as Base


class Conversation(Base.BaseSerializable):
    def __init__(self, sender_id, **kwargs):
        self.sender_id = sender_id
        self.name = kwargs.get('name')
        self.phone = kwargs.get('phone')
        self.flow = kwargs.get('flow')
        self.convo = kwargs.get('convo')

    def addToDB(self):
        entry = {'name': self.name,
                 'sender_id': self.sender_id,
                 'phone': self.phone,
                 'flow': self.flow,
                 'connvo': self.convo,
                 }
        try:
            ret = DB.addOne(entry, type="convo")
            print('Conversation updated into DB')
            return ret
        except Exception as e:
            print(f"Exception while inserting into db!! {e}")
            return False


if __name__ == '__main__':
    L = []
    L.append({'user': "Hi"} )
    L.append({'bot': "Hello"} )
    L.append({'user': "Hi"} )
    L.append({'bot': "Hello"} )
    L.append({'user': "Hi"} )

    C1 = Conversation(sender_id=12345, name='nitinc', flow="configure", phone=1234678345678, convo=L)
    C1.addToDB()
    print(C1.storeJSON())
    C2 = Conversation(sender_id=435345, name='nitinc', flow="configure", phone=1234678345678, convo=L)
    print(C2.storeJSON())
    C2.addToDB()
    C3 = Conversation(sender_id=3776, name='nitinc', flow="configure", phone=1234678345678, convo=L)
    print(C3.storeJSON())
    C3.addToDB()
