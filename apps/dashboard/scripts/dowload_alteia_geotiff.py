import os
from pathlib import Path
import alteia
import folium
import geojson

alteia_sdk = alteia.SDK(
    url="https://app.alteia.com/",
    user="ucodjia@contractor.tns.org",
    password="LDUj:NJMn27UNGn"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


def download_rgb_geotiff(dir_path, mission, code):
    datasets = alteia_sdk.datasets.search(filter={
        'mission': {'$eq': mission.id},
        'name': {'$eq': "RGB"},
    })
    rgb = datasets[-1]

    created_file = alteia_sdk.datasets.download_component(
        dataset=rgb.id,
        target_path=dir_path.__str__(),
        component=rgb.components[0]["name"],
        overwrite=False,
        target_name=code + ".tif"
    )
    print(created_file)


def download():
    dir_path = BASE_DIR.__str__() + "/media/drone_images/"
    if os.path.exists(dir_path.__str__()) is False:
        os.mkdir(dir_path)
        print("Directory '% s' created" % dir_path)
    with open(BASE_DIR.__str__() + "/Caju-Dashboard-v2/staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as file:
        alteia_json = geojson.load(file)

    temp_geojson_a = folium.GeoJson(data=alteia_json,)
    for feature in temp_geojson_a.data['features']:
        try:
            code = feature["properties"]["Plantation code"]
            project = alteia_sdk.projects.search(
                filter={'name': {'$eq': code}})[0]
            mission = alteia_sdk.missions.search(
                filter={'project': {'$eq': project.id}})[0]
            download_rgb_geotiff(dir_path, mission, code)
        except Exception as e:
            print(e)
            pass


if __name__ == "__main__":
    download()
