import asyncio
import json
import locale
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import alteia
import ee
import folium
import geojson
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template import loader
from django.utils.translation import gettext
from folium import plugins
from folium.plugins import MarkerCluster

from apps.dashboard.layers_builders.benin_commune import current_benin_commune_layer
from apps.dashboard.layers_builders.benin_department import current_benin_department_layer
from apps.dashboard.layers_builders.benin_plantations import add_benin_plantation
from apps.dashboard.layers_builders.benin_republic import current_benin_republic_layer
from apps.dashboard.layers_builders.nursery_information import NurseryLayer
from apps.dashboard.layers_builders.qar_informations import QarLayer
# Google service account for the GEE geotiff
from apps.dashboard.scripts.get_qar_information import current_qars
from .map_legend import macro
from .scripts.alteia_trees_data import download_trees_data

BASE_DIR = Path(__file__).resolve().parent.parent.parent

alteia_sdk = alteia.SDK(
    url="https://app.alteia.com/",
    user=os.getenv("ALTEIA_USER"),
    password=os.getenv("ALTEIA_PASSWORD")
)

service_account = 'cajulab@benin-cajulab-web-application.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, os.getenv("PRIVATE_KEY"))
ee.Initialize(credentials)
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
# alldept = ee.Image('users/ashamba/allDepartments_v0')
alldept = ee.Image('users/cajusupport/allDepartments_v1')


def __task1_func__(cashew_map):
    benin_layer = current_benin_republic_layer
    benin_layer.add_to(cashew_map)


def __task2_func__(cashew_map, path_link):
    benin_dept_layer, dept_yield_ha = current_benin_department_layer
    benin_dept_layer.add_to(cashew_map)
    benin_plantation_layer = add_benin_plantation(path_link, dept_yield_ha)
    benin_plantation_layer.add_to(cashew_map)


def __task3_func__(cashew_map):
    benin_commune_layer = current_benin_commune_layer
    benin_commune_layer.add_to(cashew_map)


def __task4_func__(cashew_map):
    qars = current_qars
    # Adding the qar layer from the class QarLayer
    marker_cluster = MarkerCluster(name=gettext("QAR Information"))
    qar_layer = QarLayer(marker_cluster, qars).add_qar()
    qar_layer.add_to(cashew_map)


def __task5_func__(cashew_map):
    # benin_tree_crowns_layer = current_tree_crowns_layer
    # benin_tree_crowns_layer.add_to(cashew_map)
    pass


def __task6_func__(cashew_map):
    # benin_tree_tops_density_layer = current_tree_tops_density_layer
    # benin_tree_tops_density_layer.add_to(cashew_map)
    pass


def get_base_map():
    cashew_map = None
    try:
        # Basemap dictionary
        basemaps = {
            'Google Maps': folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                attr=gettext('Google'),
                name='Maps',
                max_zoom=25,
                overlay=True,
                control=False
            ),
            'Google Satellite': folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                attr='Google',
                name=gettext('Google Satellite'),
                max_zoom=25,
                overlay=True,
                show=False,
                control=True
            ),
            'Mapbox Satellite': folium.TileLayer(
                tiles='https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{'
                      'y}.png?access_token=pk.eyJ1Ijoic2hha2F6IiwiYSI6ImNrczMzNTl3ejB6eTYydnBlNzR0dHUwcnUifQ'
                      '.vHqPio3Pe0PehWpIuf5QUg',
                attr='Mapbox',
                name=gettext('Mapbox Satellite'),
                max_zoom=25,
                overlay=True,
                show=False,
                control=True
            )
        }

        # Initialize map object

        cashew_map = folium.Map(
            location=[9.0, 2.4],
            zoom_start=8,
            prefer_canvas=True,
            tiles=None
        )

        cashew_map.get_root().add_child(macro)

        cashew_map.add_child(basemaps['Google Maps'])
        cashew_map.add_child(basemaps['Google Satellite'])
        cashew_map.add_child(basemaps['Mapbox Satellite'])

        plugins.Fullscreen(
            position='topright',
            title='Full Screen',
            title_cancel='Exit Full Screen',
            force_separate_button=False
        ).add_to(cashew_map)

        # Adding the nursery layer from the class Nursery_LAYER
        marker_cluster = MarkerCluster(name=gettext("Nursery Information"))
        nursery_layer = NurseryLayer(marker_cluster).add_nursery()
        nursery_layer.add_to(cashew_map)

        # print('')
        # print('Define a method for displaying Earth Engine image tiles on a folium map.')
        # start_time = time.time()

        def add_ee_layer(self, ee_image_object, vis_params, name):
            map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
            folium.raster_layers.TileLayer(
                tiles=map_id_dict['tile_fetcher'].url_format,
                attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
                name=name,
                overlay=True,
                control=True
            ).add_to(self)

        folium.Map.add_ee_layer = add_ee_layer
        folium.map.FeatureGroup.add_ee_layer = add_ee_layer
        zones = alldept.eq(1)
        zones = zones.updateMask(zones.neq(0))
        cashew_map.add_ee_layer(zones, {'palette': "red"}, gettext('Satellite Prediction'))
        # print("--- %s seconds ---" % (time.time() - start_time))

        # print('')
        # print('The no boundary layer to remove shapefiles on the Benin region')
        # start_time = time.time()
        no_boundary_layer = folium.FeatureGroup(name=gettext('No Boundary'), show=False, overlay=False)
        no_boundary_layer.add_to(cashew_map)
        # print("--- %s seconds ---" % (time.time() - start_time))

    except Exception as e:
        print({e})
        pass

    return cashew_map


@login_required(login_url="/")
def index(request):
    cashew_map = get_base_map()

    # adding folium layer control for the previously added shapefiles
    cashew_map.add_child(folium.LayerControl())
    cashew_map = cashew_map._repr_html_()

    context = {'map': cashew_map, 'segment': 'map'}
    html_template = loader.get_template('dashboard/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/")
def full_map(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax is False or request.method != 'GET':
        return HttpResponseBadRequest('Invalid request')
    start_time = time.time()

    try:
        path_link = request.build_absolute_uri(request.path)
        cashew_map = get_base_map()

        async def __get_context_data__():
            try:
                __loop = asyncio.get_event_loop()

                executor = ThreadPoolExecutor(max_workers=5)
                # future5 = __loop.run_in_executor(executor, __task5_func__, cashew_map)
                # future6 = __loop.run_in_executor(executor, __task6_func__, cashew_map)
                future1 = __loop.run_in_executor(executor, __task1_func__, cashew_map)
                future2 = __loop.run_in_executor(executor, __task2_func__, cashew_map, path_link)
                future3 = __loop.run_in_executor(executor, __task3_func__, cashew_map)
                future4 = __loop.run_in_executor(executor, __task4_func__, cashew_map)

                # await future5
                # await future6
                await future1
                await future2
                await future3
                await future4

            except Exception as e:
                print(e)
                pass

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(__get_context_data__())
        loop.close()

        # adding folium layer control for the previously added shapefiles
        cashew_map.add_child(folium.LayerControl())
        cashew_map = cashew_map._repr_html_()
        data = {'map': cashew_map, 'segment': 'map'}

        print("TOTAL LOADING TIME--- %s seconds ---" % (time.time() - start_time))
        return HttpResponse(
            json.dumps(data),
            content_type='application/javascript; charset=utf8'
        )
    except Exception:
        return JsonResponse({'status': 'Invalid request'}, status=400)


@login_required(login_url="/")
def drone(request, plant_id, coordinate_xy):
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
        feature = next(filter(lambda x: x["properties"]["Plantation code"] == plant_id, features), None)
        folium.GeoJson(
            data=feature,
            name=gettext('Plantation Shape'),
            # style_function=lambda x: {
            #     'fillOpacity': 0
            #     # if x['properties']['name'] == 'Alabama'
            #     # else '#00ff00'
            # },
            show=False,
            zoom_on_click=True
        ).add_to(cashew_map)

    def add_alteia_tree_crows():
        directory = "static/plantation_data/" + plant_id
        with open(directory + "/Tree Crowns.geojson", errors="ignore") as file:
            feature_geojson = geojson.load(file)
        tree_crows = folium.GeoJson(feature_geojson, name=gettext('Tree Crowns'), zoom_on_click=True, embed=False)
        tree_crows.add_to(cashew_map)

    def add_alteia_tree_tops_density():
        directory = "static/plantation_data/" + plant_id
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

    coordinate_xy = coordinate_xy.replace('[', "").replace(']', "").replace(' ', "").split(',')
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
        parent_dir = BASE_DIR.__str__() + "/static/plantation_data/"
        path = os.path.join(parent_dir, plant_id)
        if os.path.exists(path.__str__()) is False:
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
