import json
import operator
import time

import folium
import geojson
import math
import unidecode
from django.utils.translation import gettext

heroku = False

# Load the Benin Communes shapefile
with open("staticfiles/json/ben_adm2.json", errors="ignore") as f:
    benin_adm2_json = geojson.load(f)
satellite_prediction_computed_data_json = open('staticfiles/satellite_prediction_computed_data.json')
data_dictionary = json.load(satellite_prediction_computed_data_json)
with open("staticfiles/plantation_recommendation.json") as plantation_recommendation_json:
    plantation_recommendations = json.load(plantation_recommendation_json)


def __define_rgb_ints__():
    communes = plantation_recommendations["properties"]["training"]["commune"]
    communes = dict(sorted(communes.items(), key=operator.itemgetter(1), reverse=True))
    count = 0
    for key, value in communes.items():
        if value != 0:
            count += 1
    try:
        step = 255 / count
    except Exception:
        step = 255
    max_int = 255
    for key in communes.keys():
        communes[key] = max_int
        max_int = math.ceil(max_int - step)
        count = count - 1
        if count <= 0:
            break
    return communes


color_values = __define_rgb_ints__()


def __highlight_function__(feature):
    """
    Function to define the layer highlight style
    """
    commune = unidecode.unidecode(feature["properties"]["NAME_2"]).lower()
    RGBint = color_values[commune]
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
    }


def create_benin_colored_commune():
    """
    Adding the shapefiles with popups for the Benin Republic communes
    Add benin republic communes data to the parent layer
    """
    __start_time = time.time()

    benin_colored_communes_layer = folium.FeatureGroup(name=gettext('Communes Training Recommandations'), show=False,
                                                       overlay=True)
    for feature in benin_adm2_json['features']:
        commune = unidecode.unidecode(feature["properties"]["NAME_2"]).lower()
        value = color_values[commune]
        if value == 0:
            continue
        commune_partial_layer = folium.GeoJson(feature, zoom_on_click=False,
                                               style_function=__highlight_function__,
                                               )
        # consolidate individual features back into the main layer
        folium.GeoJsonTooltip(fields=["NAME_2"],
                              aliases=["Commune:"],
                              labels=True,
                              sticky=False,
                              style=(
                                  "background-color: white; color: black; font-family: sans-serif; font-size: 12px; "
                                  "padding: 4px;")
                              ).add_to(commune_partial_layer)

        commune_partial_layer.add_to(benin_colored_communes_layer)

    return benin_colored_communes_layer


current_benin_colored_commune_layer = create_benin_colored_commune()
