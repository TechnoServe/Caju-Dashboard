import os
import re
import sys

import django
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.realpath(__name__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cajulab_remote_sensing_dashboard.settings")
django.setup()

from apps.dashboard import models


def nursery_row_converter(row, listy):
    # convert pandas row to a dictionary
    # requires a list of columns and a row as a tuple
    count = 1
    pictionary = {'Index': row[0]}
    for item in listy:
        if item == 'Provenance':
            word = re.sub('N°', '', row[count])
            pictionary[item] = re.sub('[\W\_]', '', word)
        else:
            pictionary[item] = row[count]
        count += 1
    return pictionary


def convert_to_dict_list(table):
    dict_list = []
    listy = table.columns
    for i, row in enumerate(table.itertuples()):
        dict_list.append(nursery_row_converter(row, listy))

    return dict_list


def dept_satellite_data_db(dept_list):
    for i, data in enumerate(dept_list):

        dept_data = models.DeptSatellite(
            country=data['Country'],
            department=data['Districts'],
            cashew_tree_cover=data['Cashew_Yield'],
        )
        try:
            dept_data.save()
        except Exception as e:
            print(e)


def commune_satellite_data_db(commune_list):
    for i, data in enumerate(commune_list):
        commune_data = models.CommuneSatellite(
            country=data['Country'],
            department=data['Districts'],
            commune=data['Communes'],
            cashew_tree_cover=data['Cashew_Yield'],
        )
        try:
            commune_data.save()
        except Exception as e:
            print(e)


def clean_satellite_data():
    commune_df = pd.read_excel("./staticfiles/new_data/dtstats_df_2.xlsx", engine='openpyxl')
    dept_df = pd.read_excel("./staticfiles/new_data/dtstats_df1_2.xlsx", engine='openpyxl')

    commune_list = convert_to_dict_list(commune_df)
    dept_list = convert_to_dict_list(dept_df)

    commune_satellite_data_db(commune_list)
    dept_satellite_data_db(dept_list)


if __name__ == '__main__':
    clean_satellite_data()
