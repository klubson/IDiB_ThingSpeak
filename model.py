import datetime
import json
import time
import pandas
import thingspeak
import statistics

import constant_variables


def get_channel():
    return thingspeak.Channel(constant_variables.thingspeak_channel, fmt='csv')


def get_field_info(channel):
    counter = 0
    fields = []
    options = {"results": 0}
    f = channel.get_field(1, options=options)
    all_fields = json.loads(f)['channel']
    all_fields_list = list(all_fields.keys())
    for x in all_fields_list:
        if "field" in x:
            counter += 1
    for i in range(1, counter + 1):
        fields.append(str(i) + ") " + all_fields["field" + str(i)])
    return fields


def convert_date(date, time):
    x = datetime.datetime.combine(date, time)
    return x.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_daily_data(channel, field, start_date, start_time):
    end_date = start_date + datetime.timedelta(days=constant_variables.deltatime_days)
    return get_data_by_date(channel, field, start_date, start_time, end_date, start_time)


def get_data_by_date(channel, field, start_date, start_time, end_date, end_time):
    start = convert_date(start_date, start_time)
    end = convert_date(end_date, end_time)
    return get_data_by_string(channel, field, start, end)


def get_data_for_day(channel, field, start_date, start_time):
    end_date = start_date + datetime.timedelta(days=constant_variables.deltatime_days)
    return get_data_by_date(channel, field, start_date, start_time, end_date, start_time)


def get_data_by_string(channel, field, start, end):
    options = {"start": start, "end": end, "format": "csv", "results": 8000}
    #print("SEND from " + start + " to " + end, end="")
    start = time.time()
    x = channel.get_field(field, options=options)
    end = time.time()
    #print(" took ", round(end - start, 3), "seconds", end="")

    return x


def parse_data(field):
    first_parse = field.split('\n')[1:-1]
    date = []
    value = []
    year = []
    for elem in first_parse:
        if elem == '\r' or elem == '"':
            continue
        elem_list = elem.replace("\r", "").split(',')
        if elem_list[2] != '':
            date.append(elem_list[0][:-7])
            value.append(float(elem_list[2].replace("\"", "")))
            year.append(elem_list[0][:4])
    return date, value, year


def analyze_dataframe_with_many_years(dataframe):
    years = ["2019", "2020", "2021", "2022", "2023"]
    used_years = []
    min_value = []
    max_value = []
    avg_value = []
    median_value = []
    amount = []
    for year in years:
        data_in_year = dataframe[dataframe['rok'] == year].get("y")

        if not data_in_year.empty:
            used_years.append(year)
            min_value.append(min(data_in_year))
            max_value.append(max(data_in_year))
            avg_value.append(round(sum(data_in_year) / len(data_in_year), 2))
            median_value.append(statistics.median(data_in_year))
            amount.append(len(data_in_year))
    return pandas.DataFrame(
        dict(rok=used_years, wartość_minimalna=min_value, wartość_maksymalna=max_value, wartość_średnia=avg_value,
             mediana=median_value, liczba_pomiarów=amount)).round(2)


def analyze_dataframe_with_one_year(dataframe):
    year = dataframe.get("rok")[0]
    min_value = []
    max_value = []
    avg_value = []
    median_value = []
    amount = []
    data = dataframe.get("y")
    min_value.append(min(data))
    max_value.append(max(data))
    avg_value.append(round(sum(data) / len(data), 2))
    median_value.append(statistics.median(data))
    amount.append(len(data))

    return pandas.DataFrame(
        dict(rok=year, wartość_minimalna=min_value, wartość_maksymalna=max_value,
             wartość_średnia=avg_value,
             mediana=median_value, liczba_pomiarów=amount)).round(2)
