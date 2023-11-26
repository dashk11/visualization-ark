"""
Module providing a Flask application with endpoints to display a dashboard.

This application uses a PostgreSQL database to fetch and display data related to
environmental measurements such as temperature, pH, oxygen, and pressure.
The data is processed and normalized for display.
"""

import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import os


from flask import Flask, render_template

from .pgclient import PgClient
from .utils import sort_by_index

app = Flask(__name__)

sensor_tables = {
    "temperature": "CM_HAM_DO_AI1/Temp_value",
    "ph": "CM_HAM_PH_AI1/pH_value",
    "oxygen": "CM_PID_DO/Process_DO",
    "pressure": "CM_PRESSURE/Output"
}


def aggregate_data(data: List[Tuple[datetime.datetime, Any]], interval_minutes: int = 15) -> List[Tuple[datetime.datetime, float]]:
    """
    Aggregate data points into specified time intervals and compute their averages.

    Args:
        data: A list of tuples containing datetime objects and associated values.
        interval_minutes: The time interval for aggregation in minutes. Defaults to 15.

    Returns:
        A list of tuples containing the averaged values for each time interval.
    """
    aggregated_data = defaultdict(list)

    for dt, value in data:
        rounded_dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute - dt.minute % interval_minutes)
        aggregated_data[rounded_dt].append(value)

    averaged_data = {dt: sum(values) / len(values) for dt, values in aggregated_data.items()}
    return list(averaged_data.items())


def normalize_data(data: List[Tuple[datetime.datetime, float]]) -> List[Tuple[datetime.datetime, float]]:
    """
    Normalize the value part of the data between 0 and 1.

    Args:
        data: A list of tuples containing datetime objects and associated values.

    Returns:
        The normalized data with values scaled between 0 and 1.
    """
    values = [x[1] for x in data]
    min_val = min(values)
    max_val = max(values)

    normalized_data = [(x[0], (x[1] - min_val) / (max_val - min_val)) for x in data]
    return normalized_data


def get_sensor_data(pg_handler: PgClient, table_name: str) -> Tuple[List[Tuple], List[Tuple], List[Tuple], List[Tuple]]:
    """
    Retrieve and process sensor data from a PostgreSQL database.

    Args:
        pg_handler: An instance of the PgClient class for database operations.
        table_name: The name of the table in the database from which to retrieve data.

    Returns:
        A tuple containing the raw data, normalized data, and aggregated data
        for 15 and 30 minutes intervals, each sorted by datetime.
    """
    # Retrieve raw data
    raw_data = pg_handler.get_time_value(table_name)
    sort_by_index(arr=raw_data, i=0)

    # Normalize data
    normalized_data = normalize_data(raw_data)
    sort_by_index(arr=normalized_data, i=0)

    # Aggregate data for different intervals
    data_15_mins = aggregate_data(raw_data, interval_minutes=15)
    sort_by_index(arr=data_15_mins, i=0)
    data_30_mins = aggregate_data(raw_data, interval_minutes=30)
    sort_by_index(arr=data_30_mins, i=0)

    return raw_data, normalized_data, data_15_mins, data_30_mins


def prepare_sensor_data_for_template(pg_handler: PgClient, sensor_tables: Dict[str, str]) -> Dict[str, List[Tuple]]:
    """
    Prepare sensor data for rendering in a template.

    Args:
        pg_handler: An instance of the PgClient class for database operations.
        sensor_tables: A dictionary where keys are sensor names and values are table names.

    Returns:
        dict: A dictionary with keys corresponding to template variable names and values being the processed data.
    """
    sensor_data = {}
    for sensor, table_name in sensor_tables.items():
        try:
            data = get_sensor_data(pg_handler, table_name)
            sensor_data.update({
                f'{sensor}_data': data[0],
                f'normalized_{sensor}_data': data[1],
                f'{sensor}_15_data': data[2],
                f'{sensor}_30_data': data[3],
            })
        except Exception as e:
            print(f"Error processing {sensor}: {e}")
            # Handle the exception or continue to the next sensor
    return sensor_data


@app.route('/')
def dashboard() -> str:
    pg_handler = PgClient(
        host=os.getenv('POSTGRES_HOST'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        db=os.getenv('POSTGRES_DB'),
        port=int(os.getenv('POSTGRES_PORT'))
    )
    sensor_data_for_template = prepare_sensor_data_for_template(pg_handler, sensor_tables)
    return render_template('dashboard.html', **sensor_data_for_template)
