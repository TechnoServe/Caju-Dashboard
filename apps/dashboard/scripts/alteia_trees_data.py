import os
from pathlib import Path

import alteia
import folium
import geojson
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

alteia_sdk = alteia.SDK(
    url="https://app.alteia.com/",
    user="sdahissiho@contractor.tns.org",
    password="9tMNaztVkL4MqQ$"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def create_plantatio_dir(plantation_id):
    directory = plantation_id
    parent_dir = BASE_DIR.__str__() + "/media/plantation_data/"
    path = os.path.join(parent_dir, directory)
    if os.path.exists(path.__str__()) is False:
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    return path


def highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def download_tree_crowns_data(dir_path, mission):
    datasets = alteia_sdk.datasets.search(filter={
        'mission': {'$eq': mission.id},
        'name': {'$eq': "Tree Crowns"},
        # 'format': {'$eq': "geojson"},
    })
    tree_crowns = datasets[-1]
    for dataset in datasets:
        if dataset.__dict__["source"]["name"] == 'data-manager':
            tree_crowns = dataset

    created_file = alteia_sdk.datasets.download_component(
        dataset=tree_crowns.id,
        target_path=dir_path.__str__(),
        component=tree_crowns.components[0]["name"],
        overwrite=True
    )
    print(created_file)


def download_tree_tops_density_data(dir_path, mission):
    datasets = alteia_sdk.datasets.search(filter={
        'mission': {'$eq': mission.id},
        'name': {'$eq': "Tree Tops Density"},
        # 'format': {'$eq': "geojson"},
    })
    tree_tops_density = datasets[-1]
    for dataset in datasets:
        if dataset.__dict__["source"]["name"] == 'data-manager':
            tree_tops_density = dataset

    created_file = alteia_sdk.datasets.download_component(
        dataset=tree_tops_density.id,
        target_path=dir_path.__str__(),
        component=tree_tops_density.components[0]["name"],
        overwrite=True
    )
    print(created_file)


def download_trees_data(code):
    dir_path = create_plantatio_dir(code)
    project = alteia_sdk.projects.search(filter={'name': {'$eq': code}})[0]
    mission = alteia_sdk.missions.search(filter={'project': {'$eq': project.id}})[0]
    download_tree_crowns_data(dir_path, mission)
    download_tree_tops_density_data(dir_path, mission)


def get_alteia_data():
    with open("../../../staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as f:
        alteia_json = geojson.load(f)

    temp_geojson_a = folium.GeoJson(data=alteia_json,
                                    name='Alteia Plantation Data 2',
                                    highlight_function=highlight_function)
    for feature in temp_geojson_a.data['features']:
        code = feature["properties"]["Plantation code"]
        dir_path = create_plantatio_dir(code)
        try:
            project = alteia_sdk.projects.search(filter={'name': {'$eq': code}})[0]
            mission = alteia_sdk.missions.search(filter={'project': {'$eq': project.id}})[0]
            download_tree_crowns_data(dir_path, mission)
            download_tree_tops_density_data(dir_path, mission)
        except Exception as e:
            if e.__class__ is IndexError:
                os.rmdir(dir_path)
            pass


scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(weeks=1))
def update_benin_department_layer():
    get_alteia_data()


scheduler.start()
