import asyncio
import locale
import os
import socket
import time
from concurrent.futures import ThreadPoolExecutor

import ee
import folium
from django.utils.translation import gettext
from folium import plugins
from folium.plugins import MarkerCluster

from apps.dashboard.custom_layer_control import CustomLayerControl
from apps.dashboard.layer_control_modifier import macro_toggler
from apps.dashboard.layers_builders.benin_commune import current_benin_commune_layer
from apps.dashboard.layers_builders.benin_department import current_benin_department_layer
from apps.dashboard.layers_builders.benin_plantations import add_benin_plantation
from apps.dashboard.layers_builders.benin_republic import current_benin_republic_layer
from apps.dashboard.layers_builders.nursery_information import NurseryLayer
from apps.dashboard.layers_builders.qar_informations import QarLayer
from apps.dashboard.layers_builders.training_informations import TrainingLayer
from apps.dashboard.map_legend import macro_en, macro_fr
# Google service account for the GEE geotiff
from apps.dashboard.scripts.get_qar_information import current_qars
from apps.dashboard.scripts.get_training_information import current_trainings

service_account = 'tnslabs@solar-fuze-338810.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, os.getenv("PRIVATE_KEY"))
ee.Initialize(credentials)
# Use '' for auto, or force e.g. to 'en_US.UTF-8'
locale.setlocale(locale.LC_ALL, '')


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
    marker_cluster = MarkerCluster(name=gettext("Warehouse Location"))
    qar_layer = QarLayer(marker_cluster, qars).add_qar()
    qar_layer.add_to(cashew_map)


def __task5_func__(cashew_map):
    trainings = current_trainings
    # Adding the qar layer from the class QarLayer
    marker_cluster = MarkerCluster(name=gettext("Training Information"), show=False)
    training_layer = TrainingLayer(marker_cluster, trainings).add_training()
    training_layer.add_to(cashew_map)


def get_base_map(path_link):
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

        if "/en/" in path_link.__str__():
            cashew_map.get_root().add_child(macro_en)
        elif "/fr/" in path_link.__str__():
            cashew_map.get_root().add_child(macro_fr)

        cashew_map.add_child(basemaps['Google Maps'])
        cashew_map.add_child(basemaps['Google Satellite'])
        cashew_map.add_child(basemaps['Mapbox Satellite'])

        plugins.Fullscreen(
            position='topright',
            title='Full Screen',
            title_cancel='Exit Full Screen',
            force_separate_button=False
        ).add_to(cashew_map)

        marker_cluster = MarkerCluster(name=gettext("Nursery Information"))
        nursery_layer = NurseryLayer(marker_cluster).add_nursery()
        nursery_layer.add_to(cashew_map)

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

        alldept = ee.Image('users/cajusupport/allDepartments_v1')
        zones = alldept.eq(1)
        zones = zones.updateMask(zones.neq(0))
        cashew_map.add_ee_layer(
            zones, {'palette': "red"}, gettext('Satellite Prediction'))

        no_boundary_layer = folium.FeatureGroup(
            name=gettext('No Boundary'), show=False, overlay=False)
        no_boundary_layer.add_to(cashew_map)

    except Exception as e:
        print({e})
        pass

    return cashew_map


print(socket.gethostname())
print(socket.gethostbyname(socket.gethostname()))


def full_map(lang):
    start_time = time.time()

    try:
        path_link = os.getenv("SERVER_URL") + lang + "/dashboard/"
        cashew_map = get_base_map(path_link=path_link)

        async def __get_context_data__():
            try:
                __loop = asyncio.get_event_loop()

                executor = ThreadPoolExecutor(max_workers=5)
                future1 = __loop.run_in_executor(
                    executor, __task1_func__, cashew_map)
                future2 = __loop.run_in_executor(
                    executor, __task2_func__, cashew_map, path_link)
                future3 = __loop.run_in_executor(
                    executor, __task3_func__, cashew_map)
                future4 = __loop.run_in_executor(
                    executor, __task4_func__, cashew_map)
                future5 = __loop.run_in_executor(
                    executor, __task5_func__, cashew_map)

                await future1
                await future2
                await future3
                await future4
                await future5

            except Exception as e:
                print(e)
                pass

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(__get_context_data__())
        loop.close()

        cashew_map.add_child(CustomLayerControl(collapsed=False))
        cashew_map.get_root().add_child(macro_toggler)
        cashew_map = cashew_map._repr_html_()
        with open(("staticfiles/cashew_map_" + lang + ".html"), 'w') as f:
            f.write(cashew_map)
        print("TOTAL LOADING TIME--- %s seconds ---" %
              (time.time() - start_time))
        return cashew_map
    except Exception:
        return None
        pass
