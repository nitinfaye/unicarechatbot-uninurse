
import datetime
from db import baseClass as Base

class ABC(Base.BaseSerializable):
    def __init__(self, dt):
        self.dt = dt

l = []

def get():
    a1 = ABC(1)
    a2 = ABC(2)
    a3 = ABC(3)

    l.append(a1)
    l.append(a2)
    l.append(a3)
    return l.copy();

def main():

    j = get()

    j.pop()
    j.pop()

    print(j)
    print(l)

import collections
if __name__ == '__main__':
    # main()
    # d = collections.defaultdict(list)
    # d[1].append(2)
    # d[1].append(2)
    # d[1].append(2)
    #
    # dt = datetime.date.today()
    # s = dt.isoformat()
    # dt1 = datetime.date(s)
    # print(dt1)
    fmt = "%m/%d/%Y - %H:%M"

    date_str3 = '06-06-2018'

    # Define dates as datetime objects
    # date_dt3 = datetime.datetime.strptime(date_str3, fmt)

    a1 = ABC(datetime.date.today())
    s = a1.storeJSON()
    data = a1.loadJSON(s)
    print(data)

