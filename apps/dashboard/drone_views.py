import json
import os
from pathlib import Path

import alteia
import ee
import folium
import geojson
import math
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from django.utils.translation import gettext
# Google service account for the GEE geotiff
from shapely.geometry import Point, shape

from apps.dashboard.scripts.alteia_trees_data import download_trees_data

BASE_DIR = Path(__file__).resolve().parent.parent.parent

try:
    alteia_sdk = alteia.SDK(
        url="https://app.alteia.com/",
        user=os.getenv("ALTEIA_USER"),
        password=os.getenv("ALTEIA_PASSWORD")
    )
except Exception as e:
    print(e)
    pass


def __highlight_function__(feature):
    """
    Function to define the layer highlight style
    """
    try:
        RGBint = math.ceil(feature["extra"]["properties"]["mean_tree_crown_distance"])
    except Exception:
        RGBint = 0
    if RGBint < 1.5:
        Red = 255 & 255
        Green = (255 >> 8) & 255
        Blue = (255 >> 16) & 255
    elif 1.5 <= RGBint < 5:
        Blue = 255 & 255
        Red = (255 >> 8) & 255
        Green = (255 >> 16) & 255
    else:
        Green = 255 & 255
        Blue = (255 >> 8) & 255
        Red = (255 >> 16) & 255
    color = '#%02x%02x%02x' % (Red, Green, Blue)
    border = "black"
    return {
        "fillColor": color,
        "color": border,
        "weight": 1.25,
        "dashArray": "1, 1",
        "opacity": 0.35,
        "fillOpacity": 1,
    }


def get_feature_of_point_cointained_in_geometry(geometry, features):
    polygon = shape(geometry)
    good_feature = None
    for feature in features:
        point = Point(feature["geometry"]["coordinates"][0], feature["geometry"]["coordinates"][1])
        if polygon.contains(point):
            good_feature = feature
            break
    return good_feature


@login_required(login_url="/")
def drone(request, plant_id, coordinate_xy):
    if request.method != 'GET':
        html_template = loader.get_template('dashboard/page-403.html')
        return HttpResponseBadRequest(html_template.render({"result": 'Invalid request'}, request))

    # if request.user.is_staff is False and request.user.is_superuser is False:
    #     html_template = loader.get_template('dashboard/page-403.html')
    #     return HttpResponseBadRequest(html_template.render({"result": 'Invalid request'}, request))

    def add_drone_image_layer():
        ee_image_object = ee.Image(f'users/cajusupport/drones_geotiff/{plant_id}')
        map_id_dict = ee.Image(ee_image_object).getMapId({})
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=gettext('Drone Image'),
            overlay=True,
            show=True,
            control=True,
            max_zoom=100
        ).add_to(cashew_map)

    def add_predictions_layer():
        alldept = ee.Image('users/cajusupport/allDepartments_v1')
        ee_image_object = alldept.eq(1)
        ee_image_object = ee_image_object.updateMask(ee_image_object.neq(0))
        map_id_dict = ee.Image(ee_image_object).getMapId({'palette': "red"})
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=gettext('Satellite Prediction'),
            overlay=True,
            show=False,
            control=True
        ).add_to(cashew_map)

    def add_plantation_shape():
        with open("staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as f:
            plantation_json = geojson.load(f)
        plantation_geojson = folium.GeoJson(data=plantation_json)
        features = plantation_geojson.data['features']
        feature = next(filter(
            lambda x: x["properties"]["Plantation code"] == plant_id, features), None)
        folium.GeoJson(
            data=feature,
            name=gettext('Plantation Shape'),
            show=True,
            zoom_on_click=True
        ).add_to(cashew_map)

    def add_alteia_tree_crows():
        directory = "media/plantation_data/" + plant_id
        with open(directory + "/Tree Crowns.geojson", errors="ignore") as file:
            feature_geojson = geojson.load(file)
        with open(directory + "/Tree Tops Density.geojson", errors="ignore") as file:
            tree_tops_density_feature_geojson = geojson.load(file)

        tree_crows_layer = folium.FeatureGroup(name=gettext('Tree Crows'),
                                               show=True,
                                               overlay=True)

        for feature in feature_geojson['features']:
            feature["extra"] = get_feature_of_point_cointained_in_geometry(
                feature["geometry"],
                tree_tops_density_feature_geojson["features"]
            )
            tree_crows_partial_layer = folium.GeoJson(
                data=feature,
                zoom_on_click=False, embed=False,
                name=gettext('Tree Crow Colored'),
                show=True,
                style_function=__highlight_function__
            )
            tree_crows_partial_layer.add_to(tree_crows_layer)
        tree_crows_layer.add_to(cashew_map)

        tree_crows = folium.GeoJson(feature_geojson, name=gettext(
            'Tree Crowns'), zoom_on_click=True, embed=False, show=False)
        tree_crows.add_to(cashew_map)

    def add_alteia_tree_tops_density():
        directory = "media/plantation_data/" + plant_id
        with open(directory + "/Tree Tops Density.geojson", errors="ignore") as file:
            feature_geojson = geojson.load(file)

        # tree_tops_density_layer = folium.FeatureGroup(name=gettext('Tree Tops Density'),
        #                                               show=False,
        #                                               overlay=True)
        # for feature in feature_geojson['features']:
        #     radius = 1.5
        #     # try:
        #     #     value = feature["properties"]["mean_tree_crown_distance"]
        #     #     radius = (1 / value) * 10
        #     #     radius = 10 if radius > 11 else radius
        #     # except Exception:
        #     #     radius = 10.99
        #     tree_tops_density_partial_layer = folium.GeoJson(
        #         data=feature,
        #         zoom_on_click=False, embed=False,
        #         name=gettext('Tree Tops Density'),
        #         show=False,
        #         marker=folium.Circle(
        #             color="#FFFFFF", opacity=0.8, weight=1,
        #             fill=True, fill_color="#FF0000", fill_opacity=0.9,
        #             radius=radius
        #         ),
        #     )
        #     tree_tops_density_partial_layer.add_to(tree_tops_density_layer)
        # tree_tops_density_layer.add_to(cashew_map)

        tree_tops_density = folium.GeoJson(
            data=feature_geojson,
            zoom_on_click=True, embed=False,
            name=gettext('Tree Tops Density'),
            show=False,
            marker=folium.Circle(
                color="#FFFFFF", opacity=0.9, weight=1,
                fill=True, fill_color="#FF0000", fill_opacity=1,
                radius=1.5
            ),
        )
        tree_tops_density.add_to(cashew_map)

    basemaps = {
        'Google Satellite': folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name=gettext('Satellite'),
            max_zoom=100,
            overlay=True,
            show=False,
            control=False
        ),
    }

    coordinate_xy = coordinate_xy.replace(
        '[', "").replace(']', "").replace(' ', "").split(',')
    coordinate_xy = [float(coordinate_xy[0]), float(coordinate_xy[1])]

    cashew_map = folium.Map(
        location=coordinate_xy,
        zoom_start=18,
        prefer_canvas=True,
        tiles=None
    )
    cashew_map.add_child(basemaps['Google Satellite'])
    for i in range(0, 60):
        try:

            add_drone_image_layer()
            add_predictions_layer()
            parent_dir = BASE_DIR.__str__() + "/media/plantation_data/"
            path = os.path.join(parent_dir, plant_id)
            tree_crowns_path = os.path.join(path, "Tree Crowns.geojson")
            tree_tops_path = os.path.join(path, "Tree Tops Density.geojson")
            if os.path.exists(tree_crowns_path.__str__()) is False or os.path.exists(tree_tops_path.__str__()) is False:
                print("download_trees_data")
                try:
                    download_trees_data(plant_id)
                except Exception as e:
                    print(e)
            add_alteia_tree_crows()
            add_alteia_tree_tops_density()
            add_plantation_shape()
        except Exception as e:
            print("Error: " + e.__str__())

        break

    cashew_map.add_child(folium.LayerControl(collapsed=False))
    cashew_map = cashew_map._repr_html_()
    context = {"map": json.dumps(cashew_map), "segment": "map"}
    html_template = loader.get_template("dashboard/index.html")
    render = html_template.render(context, request)
    return HttpResponse(render)
