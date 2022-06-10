import json
import os
import time

import django
import ee
import folium
import geojson
import math
import shapely
from django.db.models import Avg
from dotenv import load_dotenv
from math import floor, log10
from shapely.geometry import shape
from shapely.ops import unary_union

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cajulab_remote_sensing_dashboard.settings')
django.setup()

from apps.dashboard.models import BeninYield

load_dotenv()

with open("staticfiles/json/ben_adm2.json", errors="ignore") as f:
    benin_adm2_json = geojson.load(f)
with open("staticfiles/json/ben_adm1.json", errors="ignore") as f:
    benin_adm1_json = geojson.load(f)
with open("staticfiles/json/ben_adm0.json", errors="ignore") as f:
    benin_adm0_json = geojson.load(f)

# Load the Benin Protected_areas shapefile
with open("staticfiles/WDPA_WDOECM_May2022_Public_BEN_shp-po/WDPA_WDOECM_May2022_Public_BEN_shp-polygons_1.json",
          errors="ignore") as f:
    protected_area_1 = geojson.load(f)
with open("staticfiles/WDPA_WDOECM_May2022_Public_BEN_shp-po/WDPA_WDOECM_May2022_Public_BEN_shp-polygons_2.json",
          errors="ignore") as f:
    protected_area_2 = geojson.load(f)
with open("staticfiles/WDPA_WDOECM_May2022_Public_BEN_shp-po/WDPA_WDOECM_May2022_Public_BEN_shp-polygons_3.json",
          errors="ignore") as f:
    protected_area_3 = geojson.load(f)

service_account = os.getenv("EE_SERVICE_ACCOUNT")
credentials = ee.ServiceAccountCredentials(service_account, os.getenv("PRIVATE_KEY"))
ee.Initialize(credentials)

nl2012 = ee.Image('users/cajusupport/allDepartments_v1')
zones = nl2012.eq(1)
zones = zones.updateMask(zones.neq(0))

benin_adm2 = ee.FeatureCollection(benin_adm2_json)

dist_stats = zones.multiply(ee.Image.pixelArea()).reduceRegions(
    collection=benin_adm2,
    reducer=ee.Reducer.sum(),
    scale=30,
)

dist_stats = dist_stats.select(['NAME_0', 'NAME_1', 'NAME_2', 'sum'],
                               ['Country', 'Districts', 'Communes', 'Cashew Tree Cover'],
                               retainGeometry=False).getInfo()

temp_geojson_1 = folium.GeoJson(data=protected_area_1,
                                name='Benin Protected Area 1',
                                )
temp_geojson_2 = folium.GeoJson(data=protected_area_2,
                                name='Benin Protected Area 2',
                                )
temp_geojson_3 = folium.GeoJson(data=protected_area_3,
                                name='Benin Protected Area 3',
                                )

geojsons = [temp_geojson_1, temp_geojson_2, temp_geojson_3]

protected_area_features = []
for geo in geojsons:
    for feature in geo.data['features']:
        protected_area_features.append(feature)

temp_geojson_4 = folium.GeoJson(data=benin_adm0_json,
                                name='Benin Republic',
                                )

temp_geojson_5 = folium.GeoJson(data=benin_adm1_json,
                                name='Benin Department',
                                )

temp_geojson_6 = folium.GeoJson(data=benin_adm2_json,
                                name='Benin Communes',
                                )

data_dictionary = {}

benin_republic_features = temp_geojson_4.data['features']

for feature in benin_republic_features:
    data_dictionary[(feature['properties']['NAME_0'])] = {}

departments_features = temp_geojson_5.data['features']

for feature in departments_features:
    current_state = data_dictionary[(feature['properties']['NAME_0'])]
    current_state.update({feature['properties']['NAME_1']: {}})
    data_dictionary[(feature['properties']['NAME_0'])] = current_state

communes_features = temp_geojson_6.data['features']


def __get_cashew_tree_cover_within_protected_areas__(protected_area_features):
    protected_area_data_dictionary = {}
    for protected_area_feature in protected_area_features:
        protected_area_polygon = shape(protected_area_feature['geometry'])
        features = [{'type': 'Feature', 'properties': {}, 'geometry': shapely.geometry.mapping(protected_area_polygon)}]
        protected_area_ftcollection = ee.FeatureCollection(features)

        dist_stats = zones.multiply(ee.Image.pixelArea()).reduceRegions(
            collection=protected_area_ftcollection,
            reducer=ee.Reducer.sum(),
            scale=30,
        )
        dist_stats = dist_stats.select(['sum'],
                                       ['Cashew Tree Cover'],
                                       retainGeometry=False).getInfo()
        protected_area_data_dictionary[protected_area_feature["properties"]["NAME"]] = {
            "name": protected_area_feature["properties"]["NAME"],
            "area_ha": math.ceil(protected_area_feature["properties"]["REP_AREA"] * 100),
            "cashew_tree_cover": float(dist_stats["features"][0]["properties"]["Cashew Tree Cover"]) / 10000,
        }
    json_object = json.dumps(protected_area_data_dictionary, indent=4, sort_keys=True, ensure_ascii=False)

    # Writing to sample.json
    with open("staticfiles/protected_area_data.json", "w") as outfile:
        outfile.write(json_object)
        print("New json file is created")


def __get_cashew_tree_cover_within_protected_areas_within_zone__(zone_feature):
    zone_polygon = shape(zone_feature['geometry'])
    intersection_total_area = 0.0
    protected_total_area_km = 0.0
    interstice_total_area = 0.0

    shape_list = []
    for feature in protected_area_features:
        current_protected_area_polygon = shape(feature['geometry'])
        if zone_polygon.intersects(current_protected_area_polygon):
            try:
                intersection = zone_polygon.intersection(current_protected_area_polygon)
                shape_list.append(intersection)
                # intersection_total_area += intersection.area
                #
                # var1 = intersection.area
                # var2 = current_protected_area_polygon.area
                # protected_total_area_km += (var1 / var2) * feature["properties"]["REP_AREA"]
                #
                # interstice = intersection.intersection(prediction_polygon)
                # interstice_total_area += interstice.area

            except Exception as e:
                print("ERROR: ", e)

    union = unary_union([s for s in shape_list])
    features = [{'type': 'Feature', 'properties': {}, 'geometry': shapely.geometry.mapping(union)}]

    dist_stats = zones.multiply(ee.Image.pixelArea()).reduceRegions(
        collection=ee.FeatureCollection(features),
        reducer=ee.Reducer.sum(),
        scale=30,
    )
    dist_stats = dist_stats.select(['sum'],
                                   ['Cashew Tree Cover'],
                                   retainGeometry=False).getInfo()

    return float(dist_stats["features"][0]["properties"]["Cashew Tree Cover"]) / 10000
    try:
        area_percentage = (interstice_total_area / intersection_total_area)
    except Exception:
        area_percentage = 0.0
    return area_percentage * protected_total_area_km * 100


def __get_protected_areas_within_zone__(zone_feature):
    zone_polygon = shape(zone_feature['geometry'])
    protected_total_area_km = 0.0

    for feature in protected_area_features:
        current_protected_area_polygon = shape(feature['geometry'])
        if zone_polygon.intersects(current_protected_area_polygon):
            try:
                intersection = zone_polygon.intersection(current_protected_area_polygon)

                intersection_area_pixel = intersection.area
                protected_area_pixel = current_protected_area_polygon.area
                protected_total_area_km += (
                        (intersection_area_pixel / protected_area_pixel)
                        * feature["properties"]["REP_AREA"]
                )

            except Exception as e:
                print("ERROR: ", e)
    return protected_total_area_km * 100


def __get_cashew_tree_cover_within_zone__(zone_feature):
    zone_polygon = shape(zone_feature['geometry'])

    area_dictionary = {
        "Banikoara": 26242,
        "Gogounou": 26242,
        "Kandi": 26242,
        "Karimama": 26242,
        "Malanville": 26242,
        "Segbana": 26242,
        "Boukoumbé": 20499,
        "Cobly": 20499,
        "Kérou": 20499,
        "Kouandé": 20499,
        "Matéri": 20499,
        "Natitingou": 20499,
        "Péhunco": 20499,
        "Tanguiéta": 20499,
        "Toucountouna": 20499,
        "Abomey-Calavi": 3233,
        "Allada": 3233,
        "Kpomassè": 3233,
        "Ouidah": 3233,
        "Sô-Ava": 3233,
        "Toffo": 3233,
        "Tori-Bossito": 3233,
        "Zè": 3233,
        "Bembéréké": 25856,
        "Kalalé": 25856,
        "N'Dali": 25856,
        "Nikki": 25856,
        "Parakou": 25856,
        "Pèrèrè": 25856,
        "Sinendé": 25856,
        "Tchaourou": 25856,
        "Bantè": 13931,
        "Dassa-Zoumè": 13931,
        "Glazoué": 13931,
        "Ouèssè": 13931,
        "Savalou": 13931,
        "Savè": 13931,
        "Aplahoué": 2404,
        "Djakotomey": 2404,
        "Dogbo": 2404,
        "Klouékanmè": 2404,
        "Lalo": 2404,
        "Toviklin": 2404,
        "Bassila": 11126,
        "Copargo": 11126,
        "Djougou": 11126,
        "Ouaké": 11126,
        "Cotonou": 79,
        "Athiémé": 1605,
        "Bopa": 1605,
        "Comè": 1605,
        "Grand-Popo": 1605,
        "Houéyogbé": 1605,
        "Lokossa": 1605,
        "Adjarra": 1281,
        "Adjohoun": 1281,
        "Aguégués": 1281,
        "Akpro-Missérété": 1281,
        "Avrankou": 1281,
        "Bonou": 1281,
        "Dangbo": 1281,
        "Porto-Novo": 1281,
        "Sèmè-Kpodji": 1281,
        "Adja-Ouèrè": 3264,
        "Ifangni": 3264,
        "Kétou": 3264,
        "Pobè": 3264,
        "Sakété": 3264,
        "Abomey": 5243,
        "Agbangnizoun": 5243,
        "Bohicon": 5243,
        "Covè": 5243,
        "Djidja": 5243,
        "Ouinhi": 5243,
        "Zagnanado": 5243,
        "Za-Kpota": 5243,
        "Zogbodomey": 5243,
    }
    department_polygon = None
    for feature in departments_features:
        if zone_feature["properties"]["NAME_1"] == feature["properties"]["NAME_1"]:
            department_polygon = shape(feature['geometry'])
            break

    commune_area_pixel = zone_polygon.area
    department_area_pixel = department_polygon.area
    department_area_km = area_dictionary[zone_feature["properties"]["NAME_2"]]
    zone_total_area_km = (commune_area_pixel / department_area_pixel) * department_area_km

    for dist in dist_stats['features']:
        if dist["properties"]["Communes"] == zone_feature["properties"]["NAME_2"]:
            return dist["properties"]["Cashew Tree Cover"] / 10000, zone_total_area_km * 100

    intersection_area_pixel = 0.0
    # Convert the zones of the thresholded predictions to vectors.
    prediction_vectors = zones.reduceToVectors(**{
        'scale': 25,
        'geometryType': 'polygon',
        'reducer': ee.Reducer.countEvery(),
        'bestEffort': True,
    })
    prediction_polygon = shape(prediction_vectors.geometry().getInfo())
    if zone_polygon.intersects(prediction_polygon):
        try:
            intersection_polygon = zone_polygon.intersection(prediction_polygon)
            intersection_area_pixel = intersection_polygon.area
        except Exception as e:
            print("ERROR: ", e)
    try:
        area_percentage = (intersection_area_pixel / commune_area_pixel)
    except Exception as e:
        print("ERROR: ", e)
        area_percentage = 0.0

    return area_percentage * zone_total_area_km * 100, zone_total_area_km * 100


def __get_number_of_trees_within_zone__(feature):
    number_of_trees = 0
    zone_prediction_vectors = zones.reduceToVectors(**{
        'geometry': feature['geometry'],
        'scale': 50,
        'geometryType': 'polygon',
        'reducer': ee.Reducer.countEvery(),
        'bestEffort': True,
        'maxPixels': 1e50,
    })
    zone_prediction_polygon = shape(zone_prediction_vectors.geometry().getInfo())
    if zone_prediction_polygon.type == "MultiPolygon":
        number_of_trees += len(list(zone_prediction_polygon.geoms))
    return round(number_of_trees * 12.308816780102923)


def __get_commune_yield_per_hectare_from_survey(feature):
    commune = feature["properties"]["NAME_2"]
    yield_haC = BeninYield.objects.filter(commune=commune).aggregate(Avg('total_yield_per_ha_kg'))
    try:
        yield_haC = int(round(yield_haC['total_yield_per_ha_kg__avg'], 2))
    except Exception:
        yield_haC = 0
    try:
        r_yield_haC = round(yield_haC, 1 - int(floor(log10(abs(yield_haC))))) \
            if yield_haC < 90000 \
            else round(yield_haC, 2 - int(floor(log10(abs(yield_haC)))))
    except Exception:
        r_yield_haC = yield_haC
    yield_per_hectare = r_yield_haC
    return yield_per_hectare


def __get_department_yield_per_hectare_from_survey(department):
    yield_per_hectare = BeninYield.objects.filter(department=department).aggregate(Avg('total_yield_per_ha_kg'))
    try:
        yield_per_hectare = int(round(yield_per_hectare['total_yield_per_ha_kg__avg'], 2))
    except Exception:
        yield_per_hectare = 0
    return yield_per_hectare


def __get_benin_yield_per_hectare_from_survey():
    yield_haC = BeninYield.objects.aggregate(Avg('total_yield_per_ha_kg'))
    try:
        yield_haC = int(round(yield_haC['total_yield_per_ha_kg__avg'], 2))
    except Exception:
        yield_haC = 0
    try:
        r_yield_haC = round(yield_haC, 1 - int(floor(log10(abs(yield_haC))))) \
            if yield_haC < 90000 \
            else round(yield_haC, 2 - int(floor(log10(abs(yield_haC)))))
    except Exception:
        r_yield_haC = yield_haC
    yield_per_hectare = r_yield_haC
    return yield_per_hectare


def __add_communes_properties__():
    for feature in communes_features:
        current_state = data_dictionary[(feature['properties']['NAME_0'])][(feature['properties']['NAME_1'])]
        cashew_tree_cover, total_area = __get_cashew_tree_cover_within_zone__(feature)
        # number_of_trees = __get_number_of_trees_within_zone__(feature)
        number_of_trees = 0
        yield_per_tree = 0 if number_of_trees == 0 else 8
        try:
            # yield_per_hectare = (number_of_trees / cashew_tree_cover) * yield_per_tree
            yield_per_hectare = __get_commune_yield_per_hectare_from_survey(feature)
        except Exception:
            yield_per_hectare = 0
        total_cashew_yield = cashew_tree_cover * yield_per_hectare
        protected_area = __get_protected_areas_within_zone__(feature)
        cashew_tree_cover_within_protected_area = __get_cashew_tree_cover_within_protected_areas_within_zone__(
            feature)
        current_state.update(
            {
                feature['properties']['NAME_2']: {
                    "total area": total_area,
                    "total cashew yield": total_cashew_yield,
                    "cashew tree cover": cashew_tree_cover,
                    "protected area": protected_area,
                    "cashew tree cover within protected area": cashew_tree_cover_within_protected_area,
                    "yield per hectare": yield_per_hectare,
                    "yield per tree": yield_per_tree,
                    "number of trees": number_of_trees,
                },
            })
        data_dictionary[(feature['properties']['NAME_0'])][(feature['properties']['NAME_1'])] = current_state


def __add_departments_properties__():
    for department in data_dictionary['Benin']:
        data = data_dictionary['Benin'][department]
        total_area = sum([data[commune]["total area"] for commune in data])
        cashew_tree_cover = sum([data[commune]["cashew tree cover"] for commune in data])
        total_cashew_yield = sum([data[commune]["total cashew yield"] for commune in data])
        protected_area = sum([data[commune]["protected area"] for commune in data])
        cashew_tree_cover_within_protected_area = sum(
            [data[commune]["cashew tree cover within protected area"] for commune in data])
        yield_per_hectare = __get_department_yield_per_hectare_from_survey(feature)
        print(department, end=": ")
        print(__get_department_yield_per_hectare_from_survey(department))
        number_of_trees = sum([data[commune]["number of trees"] for commune in data])
        yield_per_tree = 0 if number_of_trees == 0 else 8
        data.update({"properties": {
            "total area": total_area,
            "total cashew yield": total_cashew_yield,
            "cashew tree cover": cashew_tree_cover,
            "protected area": protected_area,
            "cashew tree cover within protected area": cashew_tree_cover_within_protected_area,
            "yield per hectare": yield_per_hectare,
            "yield per tree": yield_per_tree,
            "number of trees": number_of_trees,
        }})


def __add_benin_republic_properties__():
    data = data_dictionary['Benin']
    total_area = sum([data[department]["properties"]["total area"] for department in data])
    cashew_tree_cover = sum([data[department]["properties"]["cashew tree cover"] for department in data])
    total_cashew_yield = sum([data[department]["properties"]["total cashew yield"] for department in data])
    protected_area = sum([data[department]["properties"]["protected area"] for department in data])
    cashew_tree_cover_within_protected_area = sum(
        [data[department]["properties"]["cashew tree cover within protected area"] for department in data])
    yield_per_hectare = __get_benin_yield_per_hectare_from_survey()

    number_of_trees = sum([data[department]["properties"]["number of trees"] for department in data])
    yield_per_tree = 0 if number_of_trees == 0 else 8
    data.update({"properties": {
        "total area": total_area,
        "total cashew yield": total_cashew_yield,
        "cashew tree cover": cashew_tree_cover,
        "protected area": protected_area,
        "cashew tree cover within protected area": cashew_tree_cover_within_protected_area,
        "yield per hectare": yield_per_hectare,
        "yield per tree": yield_per_tree,
        "number of trees": number_of_trees,
    }})


def __rank_department_by_production_level():
    dictionary = {}
    for department in data_dictionary['Benin']:
        if department == "properties":
            continue
        dictionary[department] = data_dictionary['Benin'][department]["properties"]["total cashew yield"]
    ranked = [s for s in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)]
    current_rank = 1
    previous_value = ranked[0][1]
    for index in range(len(ranked)):
        if previous_value > ranked[index][1]:
            current_rank += 1
        item = ranked[index][0]
        data_dictionary["Benin"][item]["properties"].update({"rank": current_rank})
        previous_value = ranked[index][1]


def __rank_commune_by_production_level():
    dictionary = {}
    for department in data_dictionary['Benin']:
        if department == "properties":
            continue
        for commune in data_dictionary['Benin'][department]:
            if commune == "properties":
                continue
            dictionary[department + "|" + commune] = data_dictionary['Benin'][department][commune]["total cashew yield"]
    ranked = [s for s in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)]
    current_rank = 1
    previous_value = ranked[0][1]

    for index in range(len(ranked)):
        if previous_value > ranked[index][1]:
            current_rank += 1
        item = ranked[index][0]
        department_name = item.split("|")[0]
        commune_name = item.split("|")[1]
        data_dictionary["Benin"][department_name][commune_name].update({"rank": current_rank})
        previous_value = ranked[index][1]


# f = open('staticfiles/satellite_prediction_computed_data.json')
# data_dictionary = json.load(f)
start_time = time.time()
__add_communes_properties__()
print("TOTAL LOADING TIME __add_communes_properties__ --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
__add_departments_properties__()
print("TOTAL LOADING TIME __add_departments_properties__ --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
__add_benin_republic_properties__()
print("TOTAL LOADING TIME __add_benin_republic_properties__ --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
__rank_department_by_production_level()
print("TOTAL LOADING TIME __rank_department_by_production_level --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
__rank_commune_by_production_level()
print("TOTAL LOADING TIME __rank_commune_by_production_level --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
__get_cashew_tree_cover_within_protected_areas__(protected_area_features)
print("TOTAL LOADING TIME __get_cashew_tree_cover_within_protected_areas__ --- %s seconds ---" % (
        time.time() - start_time))
# print(json.dumps(data_dictionary, indent=4, sort_keys=True, ensure_ascii=False))

# Serializing json
json_object = json.dumps(data_dictionary, indent=4, sort_keys=True, ensure_ascii=False)

# Writing to sample.json
with open("staticfiles/satellite_prediction_computed_data.json", "w") as outfile:
    outfile.write(json_object)
    print("New json file is created")
