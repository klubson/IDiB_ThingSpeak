import datetime
import sqlite3

import pandas
import plotly.express as px
import streamlit as st

import model


def convert_date(date, time):
    converted_date = datetime.datetime.combine(date, time)
    return converted_date.strftime("%Y-%m-%dT%H:%M:%SZ")


def add_year_to_date(date, year):
    return str(year) + date.strftime("-%m-%dT%H:%M:%SZ")


def draw_single_data(dataframe):
    st.write("Data amount:", len(dataframe['x']))
    figure = px.scatter(dataframe, x="x", y="y", color_discrete_map={"y": "red"})
    st.write(figure)


def create_data_frame(constant, xs, ys, years):
    x = []
    y = []
    year = []
    for i in range(len(xs)):
        dates = xs[i]
        for j in range(len(dates)):
            x.append(constant + dates[j][4:])
            y.append(ys[i][j])
            year.append(years[i][j])
    return pandas.DataFrame(dict(x=x, y=y, year=year))


def change_year(date, year):
    return datetime.date(year, date.month, date.day)


def multiple_request_for_years(start, time, days_num):
    years_to_compare = [2019, 2020, 2021, 2022, 2023]
    x_axis_for_year = []
    y_axis_for_year = []
    year_for_year = []
    counter = 0
    for i in years_to_compare:
        counter += 1
        new_start = change_year(start, i)
        x, y, year = multiple_request(new_start, time, days_num)
        x_axis_for_year.append(x)
        y_axis_for_year.append(y)
        year_for_year.append(year)
    return x_axis_for_year, y_axis_for_year, year_for_year


def multiple_request(date, time, days_num):
    x = []
    y = []
    year = []
    for i in range(0, days_num, 3):
        temp_x, temp_y, temp_year = model.parse_data(
            model.get_daily_data(channel, chosen_field, date, time))
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
    connection = sqlite3.connect("thing.db")
    cursor = connection.cursor()
    start_date_time = "'" + str(start_date) + " " + str(start_time) + "'"
    end_date_time = "'" + str(end_date) + " " + str(end_time) + "'"
    res = cursor.execute(
        "Select * from " + table_name + " where datetime(date) between  datetime(" + start_date_time + ") and  datetime(" + end_date_time + ")")
    db_result = res.fetchall()
    print(start_date_time, end_date_time, len(db_result))
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
        figure = px.scatter(dataframe, x="x", y="y", color_discrete_map={"y": "red"})
        st.write(figure)
    else:
        st.write("Data amount:", len(dataframe["x"]))
        figure = px.strip(dataframe, x="x", y="y", color="year")
        st.write(figure)
        dataframe = model.analyze_dataframe(dataframe)
        st.dataframe(dataframe)


tables = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']

# Pobieranie danych modelu
channel = model.get_channel()
fields = model.get_field_info(channel)
option = st.sidebar.selectbox('Field', fields)
chosen_field = int(option.split(")")[0])
chosen_table = tables[chosen_field - 1]
range_option = st.sidebar.selectbox('Comparison range', ["Days", "Custom"])
year_comparison = st.sidebar.checkbox('Year comparison')

if range_option == "Custom":
    start_date = st.sidebar.date_input("Start date", datetime.date(2022, 4, 10))
    start_time = st.sidebar.time_input('Start time', datetime.time(12, 00))
    end_date = st.sidebar.date_input("End date", datetime.date(2022, 4, 17))
    end_time = st.sidebar.time_input('End time', datetime.time(12, 00))
    if start_date < end_date:

        st.warning("No data")

        x, y, year = read_database(chosen_table, start_date, start_time, end_date, end_time)
        dataframe = pandas.DataFrame(dict(x=x, y=y, year=year))
        # draw(model.get_data_by_date(channel, chosen_field, start_date, start_time, end_date, end_time))

        draw_by_dataframe(dataframe)
    else:
        st.error("Wrong timeframe")

elif range_option == "Days":

    start_date = st.sidebar.date_input("Start date", datetime.date(2022, 2, 11))
    start_time = st.sidebar.time_input('Start time', datetime.time(14, 20))
    number_of_days = st.sidebar.number_input('Insert a number of days', min_value=1, value=2, step=1)

    if not year_comparison:
        # x, y, year = multiple_request(start_date, start_time, number_of_days)
        x, y, year = read_database_by_start_date(chosen_table, start_date, start_time, number_of_days)

        dataframe = pandas.DataFrame(dict(x=x, y=y, year=year))
    else:
        x = []
        y = []
        year = []
        for i in [2019, 2020, 2021, 2022, 2023]:
            date = datetime.date(i, start_date.month, start_date.day)
            x_temp, y_temp, year_temp = read_database_by_start_date(chosen_table, date, start_time, number_of_days)
            x.extend(x_temp)
            y.extend(y_temp)
            year.extend(year_temp)
        dataframe = pandas.DataFrame(dict(x=x, y=y, year=year))
    draw_by_dataframe(dataframe)
else:
    st.warning("Nothing to do")
