import asyncio
import locale
import os
import time
from concurrent.futures import ThreadPoolExecutor

import ee
import folium
from django.utils.translation import gettext
from folium import plugins
from folium.plugins import MarkerCluster

from apps.dashboard.layer_control_modifier import macro_toggler
from apps.dashboard.layers_builders.benin_colored_communes import current_benin_colored_commune_layer
from apps.dashboard.layers_builders.benin_colored_departments import current_benin_colored_department_layer
from apps.dashboard.layers_builders.benin_commune import current_benin_commune_layer
from apps.dashboard.layers_builders.benin_department import current_benin_department_layer
from apps.dashboard.layers_builders.benin_plantations import create_benin_plantation
from apps.dashboard.layers_builders.benin_protected_areas import current_benin_protected_area_layer
from apps.dashboard.layers_builders.benin_republic import current_benin_republic_layer
from apps.dashboard.layers_builders.nursery_information import NurseryLayer
from apps.dashboard.layers_builders.qar_informations import QarLayer
from apps.dashboard.layers_builders.training_informations import TrainingLayer
from apps.dashboard.map_legend import macro_en, macro_fr
# Google service account for the GEE geotiff
from apps.dashboard.scripts.get_qar_information import current_qars
from apps.dashboard.scripts.get_training_information import current_trainings

service_account = os.getenv("EE_SERVICE_ACCOUNT")
credentials = ee.ServiceAccountCredentials(service_account, os.getenv("PRIVATE_KEY"))
ee.Initialize(credentials)
# Use '' for auto, or force e.g. to 'en_US.UTF-8'
locale.setlocale(locale.LC_ALL, '')


def __task2_func__(path_link):
    benin_dept_layer, dept_yield_ha = current_benin_department_layer
    benin_plantation_layer = create_benin_plantation(path_link, dept_yield_ha)
    return benin_dept_layer, benin_plantation_layer


def __task1_func__():
    marker_cluster = MarkerCluster(name=gettext("Nursery Information"), show=True)
    nursery_layer = NurseryLayer(marker_cluster).add_nursery()
    return nursery_layer


def __task3_func__():
    def build_predictions_layer(ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        return folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=name,
            overlay=True,
            control=True,
            show=True,
            zIndex=-10,
        )

    alldept = ee.Image('users/cajusupport/V3_2021_onlyCashew')
    zones = alldept.eq(1)
    zones = zones.updateMask(zones.neq(0))
    predictions_layer = build_predictions_layer(
        zones, {'palette': "red"}, gettext('Satellite Prediction'))
    return predictions_layer


def __task4_func__():
    qars = current_qars
    marker_cluster = MarkerCluster(name=gettext("Warehouse Location"), show=True)
    qar_layer = QarLayer(marker_cluster, qars).add_qar()
    return qar_layer


def __task5_func__():
    trainings = current_trainings
    marker_cluster = MarkerCluster(name=gettext("Training Information"), show=False)
    training_layer = TrainingLayer(marker_cluster, trainings).add_training()
    return training_layer


def ordering_layers(cashew_map, layers):
    cashew_map.keep_in_front(layers["benin_border_layer"])
    cashew_map.keep_in_front(layers["benin_layer"])
    cashew_map.keep_in_front(layers["benin_dept_layer"])
    cashew_map.keep_in_front(layers["benin_commune_layer"])

    cashew_map.keep_in_front(layers["benin_colored_dept_layer"])
    cashew_map.keep_in_front(layers["benin_colored_commune_layer"])

    cashew_map.keep_in_front(layers["benin_protected_layer"])
    cashew_map.keep_in_front(layers["benin_plantation_layer"])

    cashew_map.keep_in_front(layers["training_layer"])
    cashew_map.keep_in_front(layers["qar_layer"])
    cashew_map.keep_in_front(layers["nursery_layer"])

    cashew_map.keep_in_front(layers["predictions_layer"])
    return cashew_map


def add_layers_to_map(cashew_map, layers):
    layers["benin_border_layer"].add_to(cashew_map)
    layers["benin_layer"].add_to(cashew_map)
    layers["benin_dept_layer"].add_to(cashew_map)
    layers["benin_commune_layer"].add_to(cashew_map)

    layers["benin_colored_dept_layer"].add_to(cashew_map)
    layers["benin_colored_commune_layer"].add_to(cashew_map)

    layers["benin_protected_layer"].add_to(cashew_map)
    layers["benin_plantation_layer"].add_to(cashew_map)

    layers["qar_layer"].add_to(cashew_map)
    layers["training_layer"].add_to(cashew_map)
    layers["nursery_layer"].add_to(cashew_map)
    layers["predictions_layer"].add_to(cashew_map)
    return cashew_map


def get_base_map(path_link):
    cashew_map = None
    try:
        # Basemap dictionary
        basemaps = {
            'Google Maps': folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                attr=gettext('Google'),
                name='Google Maps',
                max_zoom=25,
                overlay=False,
                control=True,
                show=True,
            ),
            'Google Satellite': folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                attr='Google',
                name=gettext('Google Satellite'),
                max_zoom=25,
                overlay=False,
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
                overlay=False,
                show=False,
                control=True
            )
        }

        # Initialize map object

        cashew_map = folium.Map(
            location=[9.0, 2.4],
            zoom_start=8,
            prefer_canvas=True,
            tiles=None,
            max_zoom=200,
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

    except Exception as e:
        print({e})
        pass

    return cashew_map


def full_map(lang):
    start_time = time.time()

    try:
        server_url = os.getenv("SERVER_URL")
        if server_url[-1] is not "/":
            server_url += "/"
        path_link = server_url + lang + "/dashboard/"
        cashew_map = get_base_map(path_link=path_link)
        layers = {}

        async def __get_context_data__():
            try:
                __loop = asyncio.get_event_loop()

                executor = ThreadPoolExecutor(max_workers=2)
                future1 = __loop.run_in_executor(
                    executor, __task1_func__)
                future2 = __loop.run_in_executor(
                    executor, __task2_func__, path_link)
                future3 = __loop.run_in_executor(
                    executor, __task3_func__)
                future4 = __loop.run_in_executor(
                    executor, __task4_func__)
                future5 = __loop.run_in_executor(
                    executor, __task5_func__)

                layers["benin_layer"], layers["benin_border_layer"] = current_benin_republic_layer

                layers["benin_dept_layer"], layers["benin_plantation_layer"] = await future2
                layers["benin_colored_dept_layer"] = current_benin_colored_department_layer

                layers["benin_commune_layer"] = current_benin_commune_layer
                layers["benin_colored_commune_layer"] = current_benin_colored_commune_layer

                layers["benin_protected_layer"] = current_benin_protected_area_layer

                layers["nursery_layer"] = await future1
                layers["qar_layer"] = await future4
                layers["training_layer"] = await future5

                layers["predictions_layer"] = await future3

            except Exception as e:
                print(e)
                pass

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(__get_context_data__())
        loop.close()

        cashew_map = add_layers_to_map(cashew_map, layers)
        cashew_map = ordering_layers(cashew_map, layers)

        cashew_map.add_child(folium.LayerControl(collapsed=False))

        cashew_map.get_root().add_child(macro_toggler)
        cashew_map = cashew_map._repr_html_()
        with open(("staticfiles/cashew_map_" + lang + ".html"), 'w') as f:
            print(f.name)
            f.write(cashew_map)
        print("TOTAL LOADING TIME--- %s seconds ---" %
              (time.time() - start_time))
        return cashew_map
    except Exception as e:
        print(e)
        return None
