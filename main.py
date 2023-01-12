import datetime
import sqlite3
import time

import pandas as pd
import plotly.express as px
import streamlit as st

import model as model


def convert_date(date, time):
    x = datetime.datetime.combine(date, time)
    return x.strftime("%Y-%m-%dT%H:%M:%SZ")


def convert_date_(date, year):
    return str(year) + date.strftime("-%m-%dT%H:%M:%SZ")


def draw_single_data(df):
    st.write("Data amount:", len(df['x']))
    fig = px.scatter(df, x="x", y="y", color_discrete_map={"y": "red"})
    st.write(fig)


def create_data_frame(const, xs, ys, roks):
    x = []
    y = []
    rok = []
    for i in range(len(xs)):
        dates = xs[i]
        for j in range(len(dates)):
            x.append(const + dates[j][4:])
            y.append(ys[i][j])
            rok.append(roks[i][j])
    return pd.DataFrame(dict(x=x, y=y, rok=rok))


def change_year(date, year):
    return datetime.date(year, date.month, date.day)


def multiple_request_for_years(start, time, days_num):
    years_to_compare = [2019, 2020, 2021, 2022, 2023]
    x_for_year = []
    y_for_year = []
    rok_for_year = []
    counter = 0
    for i in years_to_compare:
        counter += 1
        new_start = change_year(start, i)
        x, y, rok = multiple_request(new_start, time, days_num)
        x_for_year.append(x)
        y_for_year.append(y)
        rok_for_year.append(rok)
    return x_for_year, y_for_year, rok_for_year


def multiple_request(date, time, days_num, my_bar):
    x = []
    y = []
    year = []
    for i in range(0, days_num, 3):
        temp_x, temp_y, temp_year = model.parse_data(
            model.get_data_for_day(channel, chosen_field, date, time))
        print(" retrieved ", len(temp_x[0]), "elements")
        x += temp_x
        y += temp_y
        year += temp_year
        date += datetime.timedelta(days=3)
    return x, y, year


def read_database_by_start_date(table_name, date, time, days_num):
    start_date = date
    start_time = time
    end_date = start_date + datetime.timedelta(days=days_num)
    end_time = time
    return read_database(table_name, start_date, start_time, end_date, end_time)


def read_database(table_name, start_date, start_time, end_date, end_time):
    con = sqlite3.connect("thing.db")
    cur = con.cursor()
    a = "'" + str(start_date) + " " + str(start_time) + "'"
    b = "'" + str(end_date) + " " + str(end_time) + "'"
    res = cur.execute(
        "Select * from "+table_name+" where datetime(date) between  datetime(" + a + ") and  datetime(" + b + ")")
    db_result = res.fetchall()
    print(a, b, len(db_result))
    x = []
    y = []
    year = []
    for i in db_result:
        x.append(i[0][5:])
        y.append(i[1])
        year.append(i[0][:4])
    return x, y, year


def draw_by_dataframe(dataframe):
    if not year_comparison:
        st.write("Data amount:", len(dataframe['x']))
        fig = px.scatter(dataframe, x="x", y="y", color_discrete_map={"y": "red"})
        st.write(fig)
    else:
        st.write("Data amount:", len(df["x"]))
        fig = px.strip(df, x="x", y="y", color="rok")
        st.write(fig)
        dataframe = model.analyze_dataframe(df)
        st.dataframe(dataframe)


tables = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
channel = model.get_channel()
fields = model.get_field_info(channel)
option = st.sidebar.selectbox('Field', fields)
chosen_field = int(option.split(")")[0])
chosen_table = tables[chosen_field-1]
range_option = st.sidebar.selectbox('Comparison range', ["Days", "Custom"])
year_comparison = st.sidebar.checkbox('Year comparison')

if range_option == "Custom":
    start_date = st.sidebar.date_input("Start date", datetime.date(2022, 2, 11))
    start_time = st.sidebar.time_input('Start time', datetime.time(14, 20))
    end_date = st.sidebar.date_input("End date", datetime.date(2022, 2, 16))
    end_time = st.sidebar.time_input('End time', datetime.time(15, 20))
    if start_date < end_date:

        st.warning("Nothing")

        x, y, year = read_database(chosen_table, start_date, start_time, end_date, end_time)
        df = pd.DataFrame(dict(x=x, y=y, rok=year))
        # draw(model.get_data_by_date(channel, chosen_field, start_date, start_time, end_date, end_time))

        draw_by_dataframe(df)
    else:
        st.error("Bad dates")

elif range_option == "Days":

    start_date = st.sidebar.date_input("Start date", datetime.date(2022, 2, 11))
    start_time = st.sidebar.time_input('Start time', datetime.time(14, 20))
    number_of_days = st.sidebar.number_input('Insert a number', min_value=1, value=2, step=1)

    if not year_comparison:
        # x, y, year = multiple_request(start_date, start_time, number_of_days)
        x, y, year = read_database_by_start_date(chosen_table, start_date, start_time, number_of_days)

        df = pd.DataFrame(dict(x=x, y=y, rok=year))
    else:
        x = []
        y = []
        year = []
        for i in [2019, 2020, 2021, 2022, 2023]:
            date = datetime.date(i, start_date.month, start_date.day)
            # x, y, year = multiple_request_for_years(start_date, start_time, number_of_days)
            x_temp, y_temp, year_temp = read_database_by_start_date(chosen_table, date, start_time, number_of_days)
            x.extend(x_temp)
            y.extend(y_temp)
            year.extend(year_temp)
        df = pd.DataFrame(dict(x=x, y=y, rok=year))
    draw_by_dataframe(df)
else:
    st.warning("Nothing to do")
