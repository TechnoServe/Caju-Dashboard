import json
import time

import folium
import geojson
import math
import unidecode
from django.utils.translation import gettext

heroku = False

# Load the Benin Departments shapefile
with open("staticfiles/json/ben_adm1.json", errors="ignore") as f:
    benin_adm1_json = geojson.load(f)
with open("staticfiles/satellite_prediction_computed_data.json") as satellite_prediction_computed_data_json:
    data_dictionary = json.load(satellite_prediction_computed_data_json)
with open("staticfiles/plantation_recommendation.json") as plantation_recommendation_json:
    plantation_recommendations = json.load(plantation_recommendation_json)


def __highlight_function__(feature):
    """
    Function to define the layer highlight style
    """

    department = unidecode.unidecode(feature["properties"]["NAME_1"]).lower()
    RGBint = math.floor(plantation_recommendations["properties"]["training"]["department"][department] / 4)
    color = "transparent"
    border = "transparent"
    if RGBint != 0:
        Red = RGBint & 255
        Green = (RGBint >> 8) & 255
        Blue = (RGBint >> 16) & 255
        color = '#%02x%02x%02x' % (Red, Green, Blue)
        border = "black"

    return {
        "fillColor": color,
        "color": border,
        "weight": 3,
        "dashArray": "1, 1",
        "opacity": 0.35,
        "fillOpacity": 0.8,
        'interactive': False
    }


def add_benin_colored_department():
    """
    Adding the shapefiles with popups for the Benin Republic departments
    Add benin republic departments data to the parent layer
    """
    __start_time = time.time()

    benin_colored_departments_layer = folium.FeatureGroup(name=gettext('Departments Training Recommandations'),
                                                          show=False,
                                                          overlay=True, z_index_offset=10)

    for feature in benin_adm1_json['features']:
        department_partial_layer = folium.GeoJson(feature, zoom_on_click=False,
                                                  style_function=__highlight_function__,
                                                  )
        # consolidate individual features back into the main layer
        folium.GeoJsonTooltip(fields=["NAME_1"],
                              aliases=["Department:"],
                              labels=True,
                              sticky=False,
                              style=(
                                  "background-color: white; color: black; font-family: sans-serif; font-size: 12px; "
                                  "padding: 4px;")
                              ).add_to(department_partial_layer)

        department_partial_layer.add_to(benin_colored_departments_layer)
    return benin_colored_departments_layer


current_benin_colored_department_layer = add_benin_colored_department()
