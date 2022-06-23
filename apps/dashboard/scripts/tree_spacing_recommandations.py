import json
import os
from pathlib import Path

import alteia
import ee
import geojson
import math
import shapely
import unidecode as unidecode
from alteia import SDK
from dotenv import load_dotenv
from shapely.geometry import shape, Point

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cajulab_remote_sensing_dashboard.settings')

service_account = os.getenv("EE_SERVICE_ACCOUNT")
credentials = ee.ServiceAccountCredentials(service_account, os.getenv("PRIVATE_KEY"))
ee.Initialize(credentials)

nl2012 = ee.Image('users/cajusupport/allDepartments_v1')
zones = nl2012.eq(1)
zones = zones.updateMask(zones.neq(0))

prediction_vectors = zones.reduceToVectors(**{
    'scale': 30,
    'geometryType': 'polygon',
    'reducer': ee.Reducer.countEvery(),
    'bestEffort': True,
})
prediction_polygon = shape(prediction_vectors.geometry().getInfo())

with open("staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as file:
    plantations_json = geojson.load(file)

img = ee.Image.pixelArea().divide(1000000)

try:
    alteia_sdk: SDK = alteia.SDK(
        url="https://app.alteia.com/",
        user=os.getenv("ALTEIA_USER"),
        password=os.getenv("ALTEIA_PASSWORD")
    )
except Exception as e:
    print(e)
    exit(84)
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

with open("staticfiles/json/ben_adm0.json", errors="ignore") as f:
    benin_adm0_json = geojson.load(f)
    benin_shape = shape(benin_adm0_json["features"][0]["geometry"])

with open("staticfiles/json/ben_adm2.json", errors="ignore") as f:
    benin_adm2_json = geojson.load(f)
    communes_shapes = [
        [shape(feature["geometry"]), feature["properties"]["NAME_2"], feature["properties"]["NAME_1"]]
        for feature in benin_adm2_json["features"]
    ]
    training_need_communes = dict.fromkeys(
        [unidecode.unidecode(feature["properties"]["NAME_2"].lower()) for feature in benin_adm2_json["features"]], 0
    )
    training_need_departments = dict.fromkeys(
        [unidecode.unidecode(feature["properties"]["NAME_1"].lower()) for feature in benin_adm2_json["features"]], 0
    )


def create_plantatio_dir(plantation_id):
    directory = plantation_id
    parent_dir = BASE_DIR.__str__() + "/media/plantation_data/"
    path = os.path.join(parent_dir, directory)
    if os.path.exists(path.__str__()) is False:
        os.mkdir(path)
    return path


def download_tree_tops_density_data(code, path):
    if os.path.exists(path.__str__()) is True:
        return True
    try:
        dir_path = create_plantatio_dir(code)
        project = alteia_sdk.projects.search(filter={'name': {'$eq': code}})[0]
        mission = alteia_sdk.missions.search(filter={'project': {'$eq': project.id}})[0]
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
        return True
    except Exception as e:
        print(e)
        return False


def download_tree_crowns_data(code, path):
    if os.path.exists(path.__str__()) is True:
        return True
    try:
        dir_path = create_plantatio_dir(code)
        project = alteia_sdk.projects.search(filter={'name': {'$eq': code}})[0]
        mission = alteia_sdk.missions.search(filter={'project': {'$eq': project.id}})[0]
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
        return True
    except Exception as e:
        print(e)
        return False


def calculate_plantation_surface_ha(plantation, feature):
    area = img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=feature['geometry'],
        scale=30,
    )
    plantation_surface_km = ee.Number(area.get('area')).getInfo()
    plantation["plantation_surface_ha"] = plantation_surface_km * 100
    return plantation


def calculate_cashew_tree_surface_ha(plantation):
    if not plantation_polygon.intersects(prediction_polygon):
        plantation["nursery_needed"] = True
        plantation["training_needed"] = True
        cashew_tree_surface_ha = 0
    else:
        geometry = shapely.geometry.mapping(intersection_polygon)
        area = img.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=30,
        )
        cashew_tree_surface_ha = ee.Number(area.get('area')).getInfo() * 100

    plantation["cashew_tree_surface_ha"] = cashew_tree_surface_ha
    return plantation


def calculate_min_and_max(plantation):
    min_recommended_number_of_cashew_trees = round(plantation["plantation_surface_ha"], 2) * 100
    plantation["min_recommended_number_of_cashew_trees"] = min_recommended_number_of_cashew_trees

    max_recommended_number_of_cashew_trees = round(plantation["plantation_surface_ha"], 2) * 177
    plantation["max_recommended_number_of_cashew_trees"] = max_recommended_number_of_cashew_trees
    return plantation


def calculate_trees_cover(plantation, tree_crowns_json):
    area = 0
    for feature in tree_crowns_json["features"]:
        area += feature["properties"]["tree_crown_surface"]
    plantation["total_trees_cover"] = area
    return plantation


def calculate_cashew_trees_cover(plantation, tree_crowns_json, intersection_polygon):
    area = 0
    for feature in tree_crowns_json["features"]:
        if intersection_polygon.contains(shape(feature["geometry"])):
            area += feature["properties"]["tree_crown_surface"]
    plantation["total_cashew_trees_cover"] = area
    return plantation


def calculate_total_number_of_trees(plantation, tree_tops_density_json):
    total_number_of_trees = len(tree_tops_density_json["features"])
    plantation["total_number_of_trees"] = total_number_of_trees
    return plantation


def calculate_total_number_of_cashew_trees(plantation, tree_tops_density_json):
    total_number_of_cashew_trees = len(list(filter(
        lambda feature:
        intersection_polygon.contains(
            Point(feature["geometry"]["coordinates"][0], feature["geometry"]["coordinates"][1])),
        tree_tops_density_json["features"]
    )))
    plantation["total_number_of_cashew_trees"] = total_number_of_cashew_trees
    return plantation


def find_location(plantation, feature, plantation_polygon):
    for commune_shape, commune, department in communes_shapes:
        intersection = plantation_polygon.intersection(commune_shape)
        percentage = (intersection.area / plantation_polygon.area)
        inside = percentage > 0.5
        if inside:
            plantation["commune"] = unidecode.unidecode(commune).lower()
            plantation["department"] = unidecode.unidecode(department).lower()
            return plantation
    commune = unidecode.unidecode(feature["properties"]["Commune"]).lower()
    department = ""
    for f in benin_adm2_json["features"]:
        if unidecode.unidecode(f["properties"]["NAME_2"].lower()) == commune:
            department = unidecode.unidecode(f["properties"]["NAME_1"].lower())
            break
    plantation["commune"] = unidecode.unidecode(commune).lower()
    plantation["department"] = department
    return plantation


def is_training_needed(plantation):
    total_cashew_trees = plantation["total_number_of_trees"]
    max_trees = plantation["max_recommended_number_of_cashew_trees"]
    min_trees = plantation["min_recommended_number_of_cashew_trees"]
    plantation["training_needed"] = plantation['tree_spacing'] > 10 or plantation['tree_spacing'] < 7
    plantation["number_of_trees_to_plant"] = [
        0 if (total_cashew_trees > min_trees) else int(min_trees - total_cashew_trees),
        0 if (total_cashew_trees > max_trees) else int(max_trees - total_cashew_trees),
    ]
    plantation["number_of_trees_to_remove"] = 0 if (total_cashew_trees < max_trees) else int(
        total_cashew_trees - max_trees)
    print(plantation["number_of_trees_to_plant"])
    if plantation["training_needed"]:
        training_need_communes[plantation["commune"]] += 1
        training_need_departments[plantation["department"]] += 1

    return plantation


def calculate_tree_spacing(plantation, tree_tops_density_json):
    total = sum([feature["properties"]["mean_tree_top_distance"] for feature in tree_tops_density_json["features"]])
    average = total / len(tree_tops_density_json["features"])
    total_trees = plantation["total_number_of_trees"]
    total_trees_cover = plantation["total_trees_cover"]
    total_trees = (total_trees if total_trees != 0 else 1)
    plantation['tree_spacing'] = round(math.sqrt(total_trees_cover / total_trees), 0)
    plantation['tree_spacing2'] = average
    return plantation


def calculate_pruning_needs(plantation, tree_tops_density_json):
    count = 0
    for feature in tree_tops_density_json["features"]:
        if feature["properties"]["mean_tree_crown_distance"] < 2:
            count += 1
    plantation['pruning_needs'] = count
    return plantation


def calculate_opposite_of_pruning_needs(plantation, tree_tops_density_json):
    count = 0
    for feature in tree_tops_density_json["features"]:
        if feature["properties"]["mean_tree_crown_distance"] > 4:
            count += 1
    plantation['opposite_of_pruning_needs'] = count
    return plantation


def generate_recommendations(plantation):
    def practice_type():
        if plantation['tree_spacing'] > 10:
            return "bigger than the recommended tree spacing which is between 7 x 7 m and 10 x 10 m"
        elif plantation['tree_spacing'] < 7:
            return "smaller than the recommended tree spacing which is between 7 x 7 m and 10 x 10 m"
        else:
            return "a good practice"

    spacing = plantation['tree_spacing']
    recommendations = f"""The tree spacing in this plantation is {spacing} x {spacing}"""
    recommendations += f""", which is {practice_type()}"""
    plantation["recommendations"] = recommendations
    return plantation


# codes = ["04-03-03-03-ALL-JAC", "04-03-03-03-ALL-JAC",
#          "04-03-03-03-BIO-MAI",
#          "04-03-03-03-BON-YO",
#          "04-03-03-03-CHA-GOU",
#          "04-03-03-03-DAM-SOG",
#          "04-03-03-03-ORO-DAM-01",
#          "04-03-03-03-ORO-DAM-02",
#          "04-03-03-03-ORO-MOU",
#          "04-03-03-03-ORO-YER",
#          "04-03-03-03-WAN-BAK",
#          "04-03-04-03-DOU-SAO",
#          "04-03-04-03-ASS-ALI",
#          "04-03-04-03-KOT-ZIM",
#          "04-03-04-03-ASS-ALI-02",
#          "04-03-04-03-KOT-ISS",
#          "04-03-04-03-MAN-DAM",
#          "04-03-04-03-OUR-ABD",
#          "04-03-04-03-SAB-GOM",
#          "04-03-04-03-SAB-GOM-03",
#          ]
# plantation_recommendation = {}
f = open('staticfiles/plantation_recommendation.json')
plantation_recommendation = json.load(f)

for feature in plantations_json['features']:
    code = feature["properties"]["Plantation code"]
    parent_dir = BASE_DIR.__str__() + "/media/plantation_data/"
    path = os.path.join(parent_dir, code)
    tree_tops_density_path = os.path.join(path, "Tree Tops Density.geojson")
    tree_crowns_path = os.path.join(path, "Tree Crowns.geojson")
    if os.path.exists(tree_crowns_path.__str__()) is False:
        continue

    # if code not in codes:
    #     continue

    # if download_tree_tops_density_data(code, tree_tops_density_path) is False:
    #     continue
    # if download_tree_crowns_data(code, tree_crowns_path) is False:
    #     continue
    #
    with open(tree_tops_density_path.__str__()) as file:
        tree_tops_density_json = geojson.load(file)
    #
    # with open(tree_crowns_path.__str__()) as file:
    #     tree_crowns_json = geojson.load(file)
    #
    # plantation_recommendation[code] = {}
    # plantation_polygon = shape(feature['geometry'])
    # intersection_polygon: shapely.geometry.geo = plantation_polygon.intersection(prediction_polygon)
    #
    # plantation_recommendation[code] = find_location(plantation_recommendation[code], feature, plantation_polygon)

    # plantation_recommendation[code] = calculate_cashew_tree_surface_ha(plantation_recommendation[code])
    # plantation_recommendation[code] = calculate_cashew_trees_cover(plantation_recommendation[code], tree_crowns_json,
    #                                                                intersection_polygon)
    # plantation_recommendation[code] = calculate_total_number_of_cashew_trees(plantation_recommendation[code],
    #                                                                          tree_tops_density_json)

    # plantation_recommendation[code] = calculate_plantation_surface_ha(plantation_recommendation[code], feature)
    # plantation_recommendation[code] = calculate_min_and_max(plantation_recommendation[code])
    # plantation_recommendation[code] = calculate_trees_cover(plantation_recommendation[code], tree_crowns_json)
    # plantation_recommendation[code] = calculate_total_number_of_trees(plantation_recommendation[code],
    #                                                                   tree_tops_density_json)
    plantation_recommendation[code] = calculate_tree_spacing(plantation_recommendation[code], tree_tops_density_json)
    # plantation_recommendation[code] = calculate_pruning_needs(plantation_recommendation[code], tree_tops_density_json)
    # plantation_recommendation[code] = calculate_opposite_of_pruning_needs(plantation_recommendation[code],
    #                                                                       tree_tops_density_json)
    # plantation_recommendation[code] = is_training_needed(plantation_recommendation[code])
    # plantation_recommendation[code] = generate_recommendations(plantation_recommendation[code])

plantation_recommendation["properties"] = {"training": {
    "department": training_need_departments,
    "commune": training_need_communes,
}}

json_object = json.dumps(plantation_recommendation, indent=4, sort_keys=True, ensure_ascii=False)

# Writing to sample.json
with open("staticfiles/plantation_recommendation.json", "w") as outfile:
    outfile.write(json_object)
    print("New json file is created")
