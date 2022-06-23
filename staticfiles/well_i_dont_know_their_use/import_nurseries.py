import os
import re
import sys

import django
import numpy as np
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


def convert_to_float(data):
    if data == "" or data == 'No data':
        return float(0)
    else:
        return float(data)


def import_dicts_to_database(dict_list):
    for i, data in enumerate(dict_list):

        if data['owner_first_name'] == "":
            first_name = str(i)
        else:
            first_name = data['owner_first_name']
        nursery_name = first_name + "'s nursery"
        owner_first_name = first_name
        owner_last_name = data['owner_last_name']
        nursery_address = data['Provenance']
        country = "Benin"
        commune = data['Commune']
        current_area = convert_to_float(data['Area (ha)'])
        latitude = convert_to_float(data['Latitude'])
        longitude = convert_to_float(data['Longitude'])
        altitude = convert_to_float(data['Altitude'])
        partner = data['Partenaire']
        number_of_plants = int(convert_to_float(data['Numebr of Plants']))

        new_nursery = models.Nursery(
            nursery_name=nursery_name,
            owner_first_name=owner_first_name,
            owner_last_name=owner_last_name,
            nursery_address=nursery_address,
            country=country,
            commune=commune,
            current_area=current_area,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            partner=partner,
            number_of_plants=number_of_plants,
        )
        try:
            new_nursery.save()
        except Exception as e:
            print("nursery data save error")


def clean_nursery_data():
    nur = pd.read_excel("./staticfiles/Data/Nurseries.xlsx", engine='openpyxl', )
    nur = nur.replace('nan', np.nan).fillna("")
    s = nur['Owner'].apply(lambda x: x.split(' '))
    nur['owner_last_name'] = s.apply(lambda x: x[0])
    nur['owner_first_name'] = s.apply(lambda x: " ".join(x[1:]) if len(x) > 0 else "")
    import_dicts_to_database(convert_to_dict_list(nur))


if __name__ == '__main__':
    clean_nursery_data()
