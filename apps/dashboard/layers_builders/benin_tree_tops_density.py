import os
import time
from gettext import gettext

import folium
import geojson
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from celery import shared_task


def highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


@shared_task(bind=True)
def create_benin_tree_tops_density_layer(self):
    benin_tree_tops_density_layer = folium.FeatureGroup(name=gettext('Tree Tops Density'), show=False, overlay=True)

    dirs = []
    start_time = time.time()
    print("START--- %s seconds ---" % (time.time() - start_time))
    for (dirpath, dirnames, filenames) in os.walk("media/plantation_data"):
        dirs.append(dirpath)
    dirs.pop(0)

    def add_tree_tops_density_geojson_to_layer(directory):
        with open(directory + "/Tree Tops Density.geojson", errors="ignore") as file:
            feature_geojson = geojson.load(file)
        tree_tops_density = folium.GeoJson(
            data=feature_geojson,
            zoom_on_click=True, embed=False,
            name='Tree Tops Density',
            marker=folium.Circle(
                color="#FFFFFF", opacity=0.9, weight=1,
                fill=True, fill_color="#FF0000", fill_opacity=1,
                radius=1.5
            ),
        )
        tree_tops_density.add_to(benin_tree_tops_density_layer)

    for index, current_dir in enumerate(dirs):
        if index == 5:
            break
        add_tree_tops_density_geojson_to_layer(current_dir)

    print("TOTAL add_tree_tops_density_geojson_to_layer LOADING TIME--- %s seconds ---" % (time.time() - start_time))
    return benin_tree_tops_density_layer


current_tree_tops_density_layer = None  # create_benin_tree_tops_density_layer()

scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(days=1))
def update_benin_republic_layer():
    global current_tree_tops_density_layer
    current_tree_tops_density_layer = create_benin_tree_tops_density_layer()


scheduler.start()
