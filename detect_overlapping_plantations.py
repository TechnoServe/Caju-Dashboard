import folium
import geojson
from shapely.geometry import shape

# Load the Benin Plantations shapefile
with open("staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as f:
    alteia_json = geojson.load(f)


def __highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def __get_good_shapfiles_codes():
    temp_geojson_a = folium.GeoJson(data=alteia_json,
                                    name='Alteia Plantation Data 2',
                                    highlight_function=__highlight_function)

    polygons = []
    good_codes = []
    for feature in temp_geojson_a.data['features']:
        code = feature["properties"]["Plantation code"]
        current_polygon = shape(feature['geometry'])
        intersect = False
        for polygon in polygons:
            if current_polygon.intersects(polygon):
                intersect = True
                break
        if intersect is False:
            polygons.append(current_polygon)
            good_codes.append(code)

    return good_codes
