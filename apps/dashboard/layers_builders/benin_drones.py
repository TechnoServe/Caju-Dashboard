import os
import time
from pathlib import Path

import folium
import geojson
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from celery import shared_task
from django.utils.translation import gettext
from shapely.geometry import shape

from apps.dashboard.models import SpecialTuple
import alteia
BASE_DIR = Path(__file__).resolve().parent.parent

start_time = time.time()
alteia_sdk = alteia.SDK(
    url="https://app.alteia.com/",
    user=os.getenv("ALTEIA_USER"),
    password=os.getenv("ALTEIA_PASSWORD")
)
print("TOTAL ALTEIA_SDK CONNEXION LOADING TIME--- %s seconds ---" % (time.time() - start_time))

# Load the Benin Plantations shapefile
with open("staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as f:
    alteia_json = geojson.load(f)


def highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


@shared_task(bind=True)
def add_benin_drone(self):
    drone_layer = folium.FeatureGroup(name=gettext('Benin Drone'), show=False, overlay=True)

    temp_geojson_a = folium.GeoJson(data=alteia_json,
                                    name='Alteia Plantation Drones Images',
                                    highlight_function=highlight_function)
    __start_time = time.time()
    datasets = alteia_sdk.datasets.search(filter={'mission': {'$eq': "604a4d805f621a00063999c0"}})
    for dataset in datasets:
        if dataset.type == "image" or dataset.type == "raster":
            try:
                print(alteia_sdk.datasets.download_preview(
                    dataset=dataset.id, kind='small',
                    target_path=BASE_DIR.__str__() + "/assets/",
                    target_name=dataset.id + ".jpg"
                ))
            except Exception as e:
                print(dataset.type, "  ", {e})

    # alteia_sdk.datasets.download_component(dataset=datasets[0].id, target_path=BASE_DIR.__str__())

    print("TOTAL projects.search() LOADING TIME--- %s seconds ---" % (time.time() - __start_time))
    for count, feature in enumerate(temp_geojson_a.data['features']):
        code = feature["properties"]["Plantation code"]

        items = len(SpecialTuple.objects.filter(alteia_id=code))
        if items != 0:
            try:
                s = shape(feature["geometry"])
                centre = s.centroid
                coordinate_xy = [centre.y, centre.x]
                folium.raster_layers.ImageOverlay(
                    image='https://upload.wikimedia.org/wikipedia/commons/f/f4/Mercator_projection_SW.jpg',
                    name=code,
                    bounds=[[centre.y - 10, centre.x - 10], [centre.y + 10, centre.x + 10]],
                    opacity=1,
                    interactive=False,
                    cross_origin=False,
                    zindex=1,
                    alt=code
                ).add_to(drone_layer)
            except Exception as e:
                print({e})
                pass
    # projects = alteia_sdk.projects.search()
    # print("{")
    # for project in projects:
    #     missions = alteia_sdk.missions.search(filter={'project': {'$eq': project.id}})
    #     print("\t", project.id, " : {")
    #     for mission in missions:
    #         print("\t\t", mission.id, " :")
    #         # datasets = alteia_sdk.missions.search(filter={'mission': {'$eq': mission.id}})
    #     print("\t}")
    #     print("")
    # print("}")
    # print("")

    return drone_layer


current_drone_layer = add_benin_drone()

scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(days=1))
def update_drone_layer():
    global current_drone_layer
    current_drone_layer = add_benin_drone()


scheduler.start()
