import locale
import os
from pathlib import Path

import alteia
import ee
import folium
import geojson
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from django.utils.translation import gettext

# Google service account for the GEE geotiff
from .scripts.alteia_trees_data import download_trees_data

BASE_DIR = Path(__file__).resolve().parent.parent.parent

alteia_sdk = alteia.SDK(
    url="https://app.alteia.com/",
    user=os.getenv("ALTEIA_USER"),
    password=os.getenv("ALTEIA_PASSWORD")
)

service_account = 'cajulab@benin-cajulab-web-application.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(
    service_account, os.getenv("PRIVATE_KEY"))
ee.Initialize(credentials)
# Use '' for auto, or force e.g. to 'en_US.UTF-8'
locale.setlocale(locale.LC_ALL, '')
alldept = ee.Image('users/cajusupport/allDepartments_v1')


@login_required(login_url="/")
def drone(request, plant_id, coordinate_xy):
    if request.method != 'GET':
        html_template = loader.get_template('dashboard/page-403.html')
        return HttpResponseBadRequest(html_template.render({"result": 'Invalid request'}, request))

    # if request.user.is_staff is False and request.user.is_superuser is False:
    #     html_template = loader.get_template('dashboard/page-403.html')
    #     return HttpResponseBadRequest(html_template.render({"result": 'Invalid request'}, request))

    def add_ee_layer_drone():
        ee_image_object = ee.Image(f'users/ashamba/{plant_id}')
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

    def add_ee_layer():
        ee_image_object = alldept.eq(1)
        ee_image_object = ee_image_object.updateMask(ee_image_object.neq(0))
        map_id_dict = ee.Image(ee_image_object).getMapId({'palette': "red"})
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=gettext('Satellite Prediction'),
            overlay=True,
            show=True,
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
            show=False,
            zoom_on_click=True
        ).add_to(cashew_map)

    def add_alteia_tree_crows():
        directory = "media/plantation_data/" + plant_id
        with open(directory + "/Tree Crowns.geojson", errors="ignore") as file:
            feature_geojson = geojson.load(file)
        tree_crows = folium.GeoJson(feature_geojson, name=gettext(
            'Tree Crowns'), zoom_on_click=True, embed=False)
        tree_crows.add_to(cashew_map)

    def add_alteia_tree_tops_density():
        directory = "media/plantation_data/" + plant_id
        with open(directory + "/Tree Tops Density.geojson", errors="ignore") as file:
            feature_geojson = geojson.load(file)
        tree_tops_density = folium.GeoJson(
            data=feature_geojson,
            zoom_on_click=True, embed=False,
            name=gettext('Tree Tops Density'),
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

    try:

        cashew_map.add_child(basemaps['Google Satellite'])
        add_ee_layer_drone()
        add_ee_layer()
        parent_dir = BASE_DIR.__str__() + "/media/plantation_data/"
        path = os.path.join(parent_dir, plant_id)
        if os.path.exists(path.__str__()) is False:
            print("download_trees_data")
            download_trees_data(plant_id)
        add_alteia_tree_crows()
        add_alteia_tree_tops_density()
        add_plantation_shape()

    except Exception as e:
        print(e)
        pass

    cashew_map.add_child(folium.LayerControl())
    cashew_map = cashew_map._repr_html_()
    context = {'map': cashew_map, 'segment': 'map'}

    html_template = loader.get_template('dashboard/index.html')
    return HttpResponse(html_template.render(context, request))
