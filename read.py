import datetime

import sqlite3

con = sqlite3.connect("thing.db")
cur = con.cursor()


if True:
    res = cur.execute("Select * from eight ")
    print(len(res.fetchall()))


#z
# cur.execute("CREATE TABLE IF NOT EXISTS  eight(date PRIMARY KEY, value) ")


start_date = datetime.date(2019, 1, 15)
start_time = datetime.time(15, 20)
end_date = datetime.date(2019, 1, 17)
end_time = datetime.time(15, 20)
a = "'"+str(start_date)+" "+str(start_time)+"'"
b = "'"+str(end_date)+" "+str(end_time)+"'"
res = cur.execute("Select * from eight where datetime(date) between  datetime("+a+") and  datetime("+b+")")
db_result = res.fetchall()
print(len(db_result))


