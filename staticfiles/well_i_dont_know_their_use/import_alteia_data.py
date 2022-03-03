import os
import re

import django
import pandas as pd

os.environ['DJANGO_SETTINGS_MODULE'] = 'cajulab_remote_sensing_dashboard.settings'
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
            pictionary[item] = re.sub('[\W_]', '', word)
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


def alteia_data_to_db(alteia_list):
    for i, data in enumerate(alteia_list):
        alteia_data = models.AlteiaData(
            plantation_code=data['Code'],
            cashew_tree_cover=data['Cashew_Tree'],
        )
        try:
            alteia_data.save()
        except Exception as e:
            print(e)


def clean_alteia_data():
    alteia_df = pd.read_excel(
        "./staticfiles/new_data/alteia_df.xlsx", engine='openpyxl')
    alteia_list = convert_to_dict_list(alteia_df)
    alteia_data_to_db(alteia_list)


if __name__ == '__main__':
    clean_alteia_data()