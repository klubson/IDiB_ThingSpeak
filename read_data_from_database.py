import datetime

import sqlite3

connection = sqlite3.connect("thing.db")
cursor = connection.cursor()


if True:
    res = cursor.execute("Select * from eight ")
    print(len(res.fetchall()))

#Czas początkowy
start_date = datetime.date(2019, 1, 15)
start_time = datetime.time(15, 20)

#Czas końcowy
end_date = datetime.date(2019, 1, 17)
end_time = datetime.time(15, 20)

#Złączenie daty i czasu
start_date_time = "'" + str(start_date) + " " + str(start_time) + "'"
end_date_time = "'" + str(end_date) + " " + str(end_time) + "'"

#Stworzenie i uruchomienie zapytania
res = cursor.execute("Select * from eight where datetime(date) between  datetime(" + start_date_time + ") and  datetime(" + end_date_time + ")")
db_result = res.fetchall()

print(len(db_result))


