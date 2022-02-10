import asyncio
import json
import locale
import time
from concurrent.futures import ThreadPoolExecutor

import ee
import folium
import geojson
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template import loader
from django.utils.translation import gettext
from folium import plugins
from folium.plugins import MarkerCluster

from apps.dashboard.benin_commune import add_benin_commune, current_benin_commune_layer
from apps.dashboard.benin_department import add_benin_department, current_benin_department_layer
from apps.dashboard.benin_plantations import add_benin_plantation
from apps.dashboard.benin_republic import add_benin_republic, current_benin_republic_layer
from apps.dashboard.nursery_information import NurseryLayer
from apps.dashboard.qar_informations import QarLayer
# Google service account for the GEE geotiff
from apps.dashboard.scripts.get_qar_information import current_qars

service_account = 'cajulab@benin-cajulab-web-application.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'privatekey.json')
ee.Initialize(credentials)
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
# alldept = ee.Image('users/ashamba/allDepartments_v0')
alldept = ee.Image('users/cajusupport/allDepartments_v1')


def __task1_func__(cashew_map):
    benin_layer = current_benin_republic_layer
    benin_layer.add_to(cashew_map)
    return cashew_map


def __task2_func__(cashew_map, path_link):
    benin_dept_layer, dept_yield_ha = current_benin_department_layer
    benin_dept_layer.add_to(cashew_map)
    benin_plantation_layer = add_benin_plantation(path_link, dept_yield_ha)
    benin_plantation_layer.add_to(cashew_map)
    return cashew_map


def __task3_func__(cashew_map):
    benin_commune_layer = current_benin_commune_layer
    benin_commune_layer.add_to(cashew_map)
    return cashew_map


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
        path_link = request.path
        cashew_map = get_base_map()

        async def __get_context_data__():
            try:
                __loop = asyncio.get_event_loop()

                qars = current_qars
                # Adding the qar layer from the class QarLayer
                marker_cluster = MarkerCluster(name=gettext("QAR Information"))
                qar_layer = QarLayer(marker_cluster, qars).add_qar()
                qar_layer.add_to(cashew_map)

                executor = ThreadPoolExecutor(max_workers=3)
                future1 = __loop.run_in_executor(executor, __task1_func__, cashew_map)
                future2 = __loop.run_in_executor(executor, __task2_func__, cashew_map, path_link)
                future3 = __loop.run_in_executor(executor, __task3_func__, cashew_map)

                await future1
                await future2
                await future3

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

        print("--- %s seconds ---" % (time.time() - start_time))
        return HttpResponse(
            json.dumps(data),
            content_type='application/javascript; charset=utf8'
        )
    except Exception:
        return JsonResponse({'status': 'Invalid request'}, status=400)


@login_required(login_url="/")
def drone(request, plant_id, coordinate_xy):
    basemaps = {
        'Google Maps': folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr=gettext('Google'),
            name='Maps',
            max_zoom=18,
            overlay=True,
            control=False
        ),
        'Google Satellite': folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name=gettext('Satellite'),
            max_zoom=25,
            overlay=True,
            show=True,
            control=False
        ),
        'Mapbox Satellite': folium.TileLayer(
            tiles='https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{'
                  'y}.png?access_token=pk.eyJ1Ijoic2hha2F6IiwiYSI6ImNrczMzNTl3ejB6eTYydnBlNzR0dHUwcnUifQ'
                  '.vHqPio3Pe0PehWpIuf5QUg',
            attr='Mapbox',
            name=gettext('Satellite View'),
            max_zoom=30,
            overlay=True,
            show=True,
            control=True
        )
    }

    # alldept = ee.Image('users/ashamba/allDepartments_v0')

    coordinate_xy = coordinate_xy.replace('[', "").replace(']', "").replace(' ', "").split(',')
    coordinate_xy = [float(coordinate_xy[0]), float(coordinate_xy[1])]

    # coordinate_xy = [9.45720800, 2.64348809]

    m = folium.Map(
        location=coordinate_xy,
        zoom_start=18,
        prefer_canvas=True,
        tiles=None
    )

    m.add_child(basemaps['Google Satellite'])

    def add_ee_layer_drone(self, ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=name,
            overlay=True,
            show=True,
            control=True
        ).add_to(self)

    def add_ee_layer(self, ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=name,
            overlay=True,
            show=False,
            control=True
        ).add_to(self)

    folium.Map.add_ee_layer_drone = add_ee_layer_drone

    zones = alldept.eq(1)
    zones = zones.updateMask(zones.neq(0))
    folium.Map.add_ee_layer = add_ee_layer

    try:
        with open(f"staticfiles/tree_crown_geojson/{plant_id}.geojson") as f:
            crown_json = geojson.load(f)
        crown_geojson = folium.GeoJson(data=crown_json,
                                       name='Tree Tops',
                                       show=False,
                                       zoom_on_click=True)
        crown_geojson.add_to(m)
        rgb = ee.Image(f'users/ashamba/{plant_id}')
        m.add_ee_layer_drone(rgb, {}, 'Drone Image')
    except Exception as e:
        print(e)
        pass

    m.add_ee_layer(zones, {'palette': "red"}, gettext('Satellite Prediction'))
    m.add_child(folium.LayerControl())
    m = m._repr_html_()
    context = {'map': m, 'segment': 'map'}

    html_template = loader.get_template('dashboard/index.html')
    return HttpResponse(html_template.render(context, request))
