import datetime
import time

import constant_variables
import model as model

import sqlite3


def insert_all(table, dates, values):
    for index in range(len(dates)):
        insert_one(table, dates[index], str(values[index]))


def insert_one(table, date, value):
    command = "INSERT INTO " + table + " VALUES ('" + date + "', " + value + ")"
    try:
        cursor.execute(command)
        connection.commit()
    except sqlite3.IntegrityError:
        print("Date '" + date + "' is already in the database")
    except:
        print(command)
        raise


connection = sqlite3.connect("thing.db")
cursor = connection.cursor()

tables = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']

channel = model.get_channel()
base_start_date = datetime.date(2022, 1, 1)
for i in range(1, 9):
    chosen_field = i
    start_date = base_start_date
    table_name = tables[chosen_field - 1]
    cursor.execute("CREATE TABLE IF NOT EXISTS " + table_name + " (date PRIMARY KEY, value) ")
    print(table_name)
    while start_date <= datetime.date(2023, 1, 5):
        start = time.time()
        temp_x, temp_y, temp_year = model.parse_data(
            model.get_daily_data(channel, chosen_field, start_date, datetime.time(0, 0)))
        try:
            print(" retrieved ", len(temp_x), " elements", end="")
        except:
            print(" retrieved 0 elements", end="")
        insert_all(table_name, temp_x, temp_y)
        end = time.time()
        start_date += datetime.timedelta(days=constant_variables.deltatime_days)
        print(" processed in ", round(end - start, 3), "seconds", end="\n")
