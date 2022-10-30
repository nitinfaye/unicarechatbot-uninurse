import sys
sys.path.append('../')
import os
import json


class Person:
    def __init__(self, sender_id):
        self.sender_id = sender_id
        self.round = ""
        self.data = []
    
    def save(self, round):
        # print("============== save")
        path = os.getcwd()
        files = os.listdir(path + "/db")
        data = {self.sender_id: round}
        self.data.append(data)
        
        if "db.json" not in files:
            # print("could not find any file")
            with open(path + "/db/db.json", "w") as f:
                json.dump({"data":self.data},f)
        else:
            # print("found a file so appending")
            
            self.load()
            with open("db/db.json", "w") as f:
                json.dump({"data":self.data},f)
        
        # print(">>>>>>>>>>> save")
        return 1
                
    def load(self):
        # print("============== load")
        path = os.getcwd()
        files = os.listdir(path)
        data = []
        with open(path + "/db/db.json", "r") as f:
            data = f.read()
            data = json.loads(data)
        self.data.extend(data["data"])
        # print(">>>>>>>>>>> load")
    
    def load_round(self, sender):
        path = os.getcwd()
        files = os.listdir(path)
        with open(path + "/db/db.json", "r") as f:
            
            data = f.read()
            data = json.loads(data)
        
        data = data["data"]
        for each in data:
            if each.get(sender) is not None:
                return each.get(sender)
            else:
                return -1


