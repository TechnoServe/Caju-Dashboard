import os
import re
import sys

import django
import pandas as pd

BASE_DIR = os.path.dirname(os.path.realpath(__name__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cajulab_remote_sensing_dashboard.settings")
django.setup()
from apps.dashboard import models

with open('staticfiles/liste_code_in_both_with_rgb_file.txt') as myfile:
    my_codes = myfile.read().splitlines()
    print("my_codes: " + len(my_codes).__str__())
    valid_codes = []
    for item in my_codes:
        valid_codes.append(item.upper())
    print("valid_codes: " + len(valid_codes).__str__())


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
            # print("plantation data save error")
            pass


def import_dicts_to_yields(dict_list):
    for i, data in enumerate(dict_list):

        plantation_id = models.Plantation.objects.get(
            plantation_name=data['ID_Plantation'])
        product_id = data['ID_product']
        year = '2020'
        total_plants = convert_to_float(data['Number of trees'])
        total_yield_kg = convert_to_float(data['2020 total yield (kg)'])
        total_yield_per_ha_kg = convert_to_float(
            data['2020 yield per ha (kg)'])
        total_yield_per_tree_kg = convert_to_float(
            data['2020 yield per tree (kg)'])
        total_sick_trees = convert_to_float(data['Number of sick trees'])
        total_dead_trees = convert_to_float(data['Number of dead trees'])
        total_trees_out_of_prod = convert_to_float(
            data['Number of trees out of production'])

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
            # print(e)
            pass


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
            total_yield_per_ha_kg=convert_to_float(
                data['2020 yield per ha (kg)']),
            total_yield_per_tree_kg=convert_to_float(
                data['2020 yield per tree (kg)']),
            sex=data['Sex'],
            product_id=data['ID_product'],
            total_number_trees=convert_to_float(data['Number of trees']),
            total_sick_trees=convert_to_float(data['Number of sick trees']),
            total_dead_trees=convert_to_float(data['Number of dead trees']),
            total_trees_out_of_prod=convert_to_float(
                data['Number of trees out of production']),
            plantation_age=convert_to_float(data['Age of plantation']),
            latitude=convert_to_float(data['GPS__Latitude']),
            longitude=convert_to_float(data['GPS__Longitude']),
            year='2020',
        )
        try:
            ben_yield.save()
        except Exception as e:
            # print(e)
            pass


def create_special_id(ben_yield, alteia_df, ben_yield_GEO):
    nb = 0
    list_global = []
    print("valid_codes 2: " + len(valid_codes).__str__())
    items = list(ben_yield_GEO['Code'])
    uids = list(ben_yield_GEO['Local shape ID or coordinates'])
    GEO_id_tuple = []
    for index in range(len(items)):
        code_u = items[index].upper()
        id_u = uids[index].upper()
        if id_u in valid_codes:
            nb += 1
            special_id_data = models.SpecialTuple(
                plantation_id=code_u,
                alteia_id=id_u,
            )
            try:
                special_id_data.save()
            except Exception as e:
                # print(e)
                pass
    print(nb)


def clean_yield_data():
    # yie = pd.read_excel("./Data/Yield data_YEARS_master.xlsx", skiprows = 1,engine='openpyxl',)
    ben_yield = pd.read_excel(
        "./staticfiles/new_data/ben_yield.xlsx", engine='openpyxl')
    ben_yield_GEO = pd.read_excel(
        "./staticfiles/new_data/ben_yield_GEO.xlsx", engine='openpyxl')
    alteia_df = pd.read_excel(
        "./staticfiles/new_data/alteia_df.xlsx", engine='openpyxl')

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
    clean_yield_data()
