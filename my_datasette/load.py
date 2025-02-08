import contextlib
import csv
from csv import excel
from datetime import date, datetime
from enum import Enum
from importlib import resources
from itertools import zip_longest
from typing import Dict, Iterable, Iterator

from sqlite_utils import Database, recipes
from sqlite_utils.utils import Format
from sqlite_utils.utils import rows_from_file as rows_from_file_implementation

from my_datasette import csv_data

db = Database("data.db")

def load():
    """Main entry point. Load all the inputs"""
    load_landmarks()
    load_bike_ped_vehicle_accidents()

def load_landmarks():
    table = db["landmarks"]
    transformed_rows = transform_landmark_rows(rows_from_file("Landmarks_Points_of_Interest.csv"))
    table.insert_all(
        transformed_rows,
        replace=True,
    )

def load_bike_ped_vehicle_accidents():
    table = db["vehicle_accidents"]
    bike_rows = transform_landmark_rows(rows_from_file("Bicycle_Motor_Vehicle_Accidents.csv"))
    ped_rows = transform_landmark_rows(rows_from_file("Pedestrian_Motor_Vehicle_Accidents.csv"))
    
    table.insert_all(
        bike_rows,
        replace=True,
    ).insert_all(
        ped_rows,
        replace=True,
    ).convert(
        [
            "Date",
        ],
        fn=recipes.parsedate,
        output_type=date,
    )

def transform_landmark_rows(rows: Iterable[Dict]) -> Iterable[Dict]:
    """Transforms rows by splitting 'Location 1' into 'latitude' and 'longitude'."""
    for data in rows:
        if "Location 1" in data and data["Location 1"]:
            try:
                lat, lon = (
                    data["Location 1"]
                    .strip("()")  # Remove parentheses
                    .split(", ")  # Split into lat and lon
                )
                data["latitude"] = float(lat)
                data["longitude"] = float(lon)
            except ValueError:
                data["latitude"] = None
                data["longitude"] = None

            del data["Location 1"]  # Remove original column

        yield data

def rows_from_file(file_name: str) -> Iterable[Dict]:
    """Generates dictionary records from CSV rows."""
    with open_resource(file_name) as resource:
        file = open(resource, "rb")
        row_gen, _ = rows_from_file_implementation(
            file, format=Format.CSV, dialect=excel, encoding="utf-8-sig"
        )
        yield from row_gen

@contextlib.contextmanager
def open_resource(file_name: str):
    """
    Use the recommended 3.11+ method for opening package data.

    I'm not a fan. This reads much worse than the old style!
    """
    # noinspection PyTypeChecker
    with resources.as_file(resources.files(csv_data).joinpath(file_name)) as resource:
        yield resource