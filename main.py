import datetime
import time
import pandas
import plotly.express
import streamlit

import constant_variables
import model


def create_data_frame(const, xs, ys, years):
    time = []
    value = []
    rok = []
    for i in range(len(xs)):
        dates = xs[i]
        for j in range(len(dates)):
            time.append(const + dates[j][4:])
            value.append(ys[i][j])
            rok.append(years[i][j])
    return pandas.DataFrame(dict(x=time, y=value, rok=rok))


def change_year(date, year):
    return datetime.date(year, date.month, date.day)


def multiple_request_for_years(start, time, days_num):
    years_to_compare = [2019, 2020, 2021, 2022]
    my_bar1 = streamlit.progress(0)
    x_for_year = []
    y_for_year = []
    rok_for_year = []
    counter = 0
    for i in years_to_compare:
        counter += 1
        new_start = change_year(start, i)

        my_bar0.progress(1.0)
        x, y, rok = multiple_request(new_start, time, days_num, my_bar0)
        x_for_year.append(x)
        y_for_year.append(y)
        rok_for_year.append(rok)

        my_bar1.progress(counter / len(years_to_compare))
    my_bar1.progress(1.0)
    return x_for_year, y_for_year, rok_for_year


def multiple_request(date, time, days_num, my_bar):
    x = []
    y = []
    year = []
    for i in range(0, days_num, constant_variables.deltatime_days):
        temp_x, temp_y, temp_year = model.parse_data(
            model.get_data_for_day(channel, chosen_field, date, time))
        x += temp_x
        y += temp_y
        year += temp_year
        date += datetime.timedelta(days=constant_variables.deltatime_days)
        my_bar.progress(i / days_num)
    my_bar.progress(1.0)

    return x, y, year


def draw_by_dataframe(dataframe):
    if not year_comparison:
        streamlit.write("Number of measurements:", len(dataframe['x']))
        figure = plotly.express.scatter(dataframe, x="x", y="y", color_discrete_map={"y": "red"})
        streamlit.write(figure)

        dataframe = model.analyze_dataframe_with_one_year(df)
        streamlit.dataframe(dataframe)
    else:
        streamlit.write("Number of measurements:", len(df["x"]))
        figure = plotly.express.strip(df, x="x", y="y", color="rok")
        streamlit.write(figure)
        dataframe = model.analyze_dataframe_with_many_years(df)
        streamlit.dataframe(dataframe)


channel = model.get_channel()
fields = model.get_field_info(channel)
option = streamlit.sidebar.selectbox('Field', fields)
chosen_field = int(option.split(")")[0])
year_comparison = streamlit.sidebar.checkbox('Year comparison')

start = time.time()
start_date = streamlit.sidebar.date_input("Measurement start date", constant_variables.measurement_start_date)
start_time = streamlit.sidebar.time_input('Measurement start time', constant_variables.measurement_start_time)
number_of_days = streamlit.sidebar.number_input('Measurement days', min_value=1,
                                                value=constant_variables.deltatime_days, step=1)

my_bar0 = streamlit.progress(0)

if not year_comparison:
    x, y, year = multiple_request(start_date, start_time, number_of_days, my_bar0)

    df = pandas.DataFrame(dict(x=x, y=y, rok=year))

else:
    x, y, year = multiple_request_for_years(start_date, start_time, number_of_days)
    df = create_data_frame(str(start_date.year), x, y, year)

end = time.time()
streamlit.write("Processing time: ", round(end - start, 3), "seconds")

draw_by_dataframe(df)
