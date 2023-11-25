"""Module providing a Flask application with endpoints to display a dashboard.

This application uses a PostgreSQL database to fetch and display data related to
environmental measurements such as temperature, pH, oxygen, and pressure.
The data is processed and normalized for display.
"""

import datetime
from collections import defaultdict
import os

from flask import Flask, render_template

from .pgclient import PgClient

app = Flask(__name__)


def parse_datetime(dt_str):
    return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


def aggregate_data(data, interval_minutes=15):
    # Create a dictionary to store aggregated data
    aggregated_data = defaultdict(list)

    # Process each data point
    for dt, value in data:

        # Round down the datetime to the nearest interval
        rounded_dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute - dt.minute % interval_minutes)

        # Add the value to the corresponding time slot
        aggregated_data[rounded_dt].append(value)

    # Calculate average for each time slot
    averaged_data = {dt: sum(values) / len(values) for dt, values in aggregated_data.items()}

    return list(averaged_data.items())


def normalize_data(data):
    # Extract values for normalization
    values = [x[1] for x in data]

    # Compute min and max
    min_val = min(values)
    max_val = max(values)

    # Normalize values and pair them back with their corresponding datetime
    normalized_data = [(x[0], (x[1] - min_val) / (max_val - min_val)) for x in data]
    return normalized_data


def sort_by_index(arr, i):
    arr.sort(key=lambda x: x[i])


def get_handler():
    return PgClient(
        host=os.getenv('POSTGRES_HOST'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        db=os.getenv('POSTGRES_DB'),
        port=os.getenv('POSTGRES_PORT')
    )


def get_temperature_data(pg_handler):
    raw_temperature_data = pg_handler.get_time_value("CM_HAM_DO_AI1/Temp_value")
    sort_by_index(arr=raw_temperature_data, i=0)
    normalized_temperature_data = normalize_data(raw_temperature_data)
    temperature_data_15_mins = aggregate_data(raw_temperature_data, interval_minutes=15)
    temperature_data_30_mins = aggregate_data(raw_temperature_data, interval_minutes=30)
    sort_by_index(arr=normalized_temperature_data, i=0)
    sort_by_index(arr=temperature_data_15_mins, i=0)
    return raw_temperature_data, normalized_temperature_data, temperature_data_15_mins, temperature_data_30_mins


def get_ph_data(pg_handler):
    raw_ph_data = pg_handler.get_time_value("CM_HAM_PH_AI1/pH_value")
    sort_by_index(arr=raw_ph_data, i=0)
    normalized_ph_data = normalize_data(raw_ph_data)
    ph_data_15_mins = aggregate_data(raw_ph_data, interval_minutes=15)
    ph_data_30_mins = aggregate_data(raw_ph_data, interval_minutes=30)
    sort_by_index(arr=normalized_ph_data, i=0)
    sort_by_index(arr=ph_data_15_mins, i=0)
    return raw_ph_data, normalized_ph_data, ph_data_15_mins, ph_data_30_mins


def get_oxygen_data(pg_handler):
    raw_oxygen_data = pg_handler.get_time_value("CM_PID_DO/Process_DO")
    sort_by_index(arr=raw_oxygen_data, i=0)
    normalized_oxygen_data = normalize_data(raw_oxygen_data)
    oxygen_data_15_mins = aggregate_data(raw_oxygen_data, interval_minutes=15)
    oxygen_data_30_mins = aggregate_data(raw_oxygen_data, interval_minutes=30)
    sort_by_index(arr=normalized_oxygen_data, i=0)
    sort_by_index(arr=oxygen_data_15_mins, i=0)
    return raw_oxygen_data, normalized_oxygen_data, oxygen_data_15_mins, oxygen_data_30_mins


def get_pressure_data(pg_handler):
    raw_pressure_data = pg_handler.get_time_value("CM_PRESSURE/Output")
    sort_by_index(arr=raw_pressure_data, i=0)
    normalized_pressure_data = normalize_data(raw_pressure_data)
    pressure_data_15_mins = aggregate_data(raw_pressure_data, interval_minutes=15)
    pressure_data_30_mins = aggregate_data(raw_pressure_data, interval_minutes=30)
    sort_by_index(arr=normalized_pressure_data, i=0)
    sort_by_index(arr=pressure_data_15_mins, i=0)
    return raw_pressure_data, normalized_pressure_data, pressure_data_15_mins, pressure_data_30_mins


@app.route('/')
def dashboard():
    pg_handler = get_handler()
    temperature_data, normalized_temperature_data, temperature_15_data, temperature_30_data = get_temperature_data(pg_handler)
    ph_data, normalized_ph_data, ph_15_data, ph_30_data = get_ph_data(pg_handler)
    oxygen_data, normalized_oxygen_data, oxygen_15_data, oxygen_30_data = get_oxygen_data(pg_handler)
    pressure_data, normalized_pressure_data, pressure_15_data, pressure_30_data = get_pressure_data(pg_handler)

    # get_normalized_data(pg_handler, temperature_data, ph_data, pressure_data)

    # Similarly fetch pH, DO, and pressure data
    return render_template(
        'dashboard.html',

        # raw data
        temperature_data=temperature_data,
        ph_data=ph_data,
        oxygen_data=oxygen_data,
        pressure_data=pressure_data,

        # normalized data
        normalized_temperature_data=normalized_temperature_data,
        normalized_ph_data=normalized_ph_data,
        normalized_oxygen_data=normalized_oxygen_data,
        normalized_pressure_data=normalized_pressure_data,

        # aggregated data
        temperature_15_data=temperature_15_data,
        ph_15_data=ph_15_data,
        oxygen_15_data=oxygen_15_data,
        pressure_15_data=pressure_15_data,

        temperature_30_data=temperature_30_data,
        ph_30_data=ph_30_data,
        oxygen_30_data=oxygen_30_data,
        pressure_30_data=pressure_30_data,
    )


if __name__ == '__main__':
    # The host is set to '0.0.0.0' to make the server externally visible.
    app.run(host='0.0.0.0', port=8000)
