import pandas as pd
import numpy as np
import re
import os, sys
import django

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

        MALE = 'male'
        FEMALE = 'female'

        plantation_name = data['ID_Plantation']
        plantation_code = data['Code']
        owner_first_name = data['Given Name']
        owner_last_name = data['Surname']
        owner_gender = FEMALE if data['Sex'] == 'Femme' else MALE
        total_trees = convert_to_float(data['Number of trees'])
        country = 'Benin'
        department = data['Departement']
        commune = data['Commune']
        arrondissement = data['Arrondissement']
        village = data['Village']
        current_area = data['2020 estimated surface (ha)']
        latitude = convert_to_float(data['GPS__Latitude'])
        longitude = convert_to_float(data['GPS__Longitude'])
        altitude = convert_to_float(data['GPS__Altitude'])

        new_plantation = models.Plantation(
            plantation_name=plantation_name,
            plantation_code=plantation_code,
            owner_first_name=owner_first_name,
            owner_last_name=owner_last_name,
            owner_gender=owner_gender,
            total_trees=total_trees,
            country=country,
            department=department,
            commune=commune,
            arrondissement=arrondissement,
            village=village,
            current_area=current_area,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
        )
        try:
            new_plantation.save()
        except Exception as e:
            print("plantation data save error")


def import_dicts_to_yields(dict_list):
    for i, data in enumerate(dict_list):

        plantation_id = models.Plantation.objects.get(plantation_name=data['ID_Plantation'])
        product_id = data['ID_product']
        year = '2020'
        total_plants = convert_to_float(data['Number of trees'])
        total_yield_kg = convert_to_float(data['2020 total yield (kg)'])
        total_yield_per_ha_kg = convert_to_float(data['2020 yield per ha (kg)'])
        total_yield_per_tree_kg = convert_to_float(data['2020 yield per tree (kg)'])
        total_sick_trees = convert_to_float(data['Number of sick trees'])
        total_dead_trees = convert_to_float(data['Number of dead trees'])
        total_trees_out_of_prod = convert_to_float(data['Number of trees out of production'])

        new_yield = models.YieldHistory(
            plantation_id=plantation_id,
            product_id=product_id,
            year=year,
            total_plants=total_plants,
            total_yield_kg=total_yield_kg,
            total_yield_per_ha_kg=total_yield_per_ha_kg,
            total_yield_per_tree_kg=total_yield_per_tree_kg,
            total_sick_trees=total_sick_trees,
            total_dead_trees=total_dead_trees,
            total_trees_out_of_prod=total_trees_out_of_prod,
        )
        try:
            new_yield.save()
        except Exception as e:
            print(e)


def import_dicts_to_benyields(dict_list):
    for i, data in enumerate(dict_list):

        ben_yield = models.BeninYield(
            plantation_name=data['ID_Plantation'],
            plantation_code=data['Code'],
            department=data['Departement'],
            commune=data['Commune'],
            arrondissement=data['Arrondissement'],
            village=data['Village'],
            owner_first_name=data['Given Name'],
            owner_last_name=data['Surname'],
            surface_area=convert_to_float(data['2020 estimated surface (ha)']),
            total_yield_kg=convert_to_float(data['2020 total yield (kg)']),
            total_yield_per_ha_kg=convert_to_float(data['2020 yield per ha (kg)']),
            total_yield_per_tree_kg=convert_to_float(data['2020 yield per tree (kg)']),
            sex=data['Sex'],
            product_id=data['ID_product'],
            total_number_trees=convert_to_float(data['Number of trees']),
            total_sick_trees=convert_to_float(data['Number of sick trees']),
            total_dead_trees=convert_to_float(data['Number of dead trees']),
            total_trees_out_of_prod=convert_to_float(data['Number of trees out of production']),
            plantation_age=convert_to_float(data['Age of plantation']),
            latitude=convert_to_float(data['GPS__Latitude']),
            longitude=convert_to_float(data['GPS__Longitude']),
            year='2020',
        )
        try:
            ben_yield.save()
        except Exception as e:
            print(e)


def create_special_id(ben_yield, alteia_df, ben_yield_GEO):
    list_global = []
    for item in list(ben_yield_GEO['Code']):
        if item in list(ben_yield['Code']):
            list_global.append(item)

    GEO_id_tuple = []
    for unique_id in list_global:
        GEO_id_tuple.append(
            (list(ben_yield_GEO[ben_yield_GEO['Code'] == unique_id]['Local shape ID or coordinates'])[0], unique_id))

    for (id_u, code_u) in GEO_id_tuple:
        if id_u in list(alteia_df['Code']):
            special_id_data = models.SpecialTuple(
                plantation_id=code_u,
                alteia_id=id_u,
            )
        try:
            special_id_data.save()
        except Exception as e:
            print(e)


def clean_yield_data():
    # yie = pd.read_excel("./Data/Yield data_YEARS_master.xlsx", skiprows = 1,engine='openpyxl',)
    ben_yield = pd.read_excel("./staticfiles/new_data/ben_yield.xlsx", engine='openpyxl')
    ben_yield_GEO = pd.read_excel("./staticfiles/new_data/ben_yield_GEO.xlsx", engine='openpyxl')
    alteia_df = pd.read_excel("./staticfiles/new_data/alteia_df.xlsx", engine='openpyxl')

    # colls = list(yie.columns)
    # needed_colls = colls[:19] + colls[-9:]
    # yield_data = yie[needed_colls]
    # yield_data = yield_data.replace('nan', np.nan).fillna("")
    dict_list = convert_to_dict_list(ben_yield)
    import_dicts_to_database(dict_list)
    # import_dicts_to_yields(dict_list)
    import_dicts_to_benyields(dict_list)
    create_special_id(ben_yield, alteia_df, ben_yield_GEO)


if __name__ == '__main__':
    # sys.path.append('/mnt/c/Users/Dami Olawoyin-Yussuf/Documents/Technoserve_Projects/NewRemSensing/Benin-Caju-Web-Dashboard')
    # os.environ['DJANGO_SETTINGS_MODULE'] = 'gettingstarted.settings'
    # django.setup()
    clean_yield_data()
