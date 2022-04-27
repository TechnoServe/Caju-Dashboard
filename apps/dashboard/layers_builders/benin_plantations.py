import os

import ee
import folium
import geojson
from area import area
from celery import shared_task
from django.utils.translation import gettext
from folium.plugins import MarkerCluster
from math import log10, floor
from shapely.geometry import shape, Point

from apps.dashboard.models import AlteiaData
from apps.dashboard.models import BeninYield
from apps.dashboard.models import SpecialTuple

# Load the Benin Plantations shapefile
with open("staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as f:
    alteia_json = geojson.load(f)
with open('staticfiles/liste_code_in_both_with_rgb_file.txt') as myfile:
    valid_codes = myfile.read()
with open("staticfiles/json/ben_adm1.json", errors="ignore") as dep_file:
    departments_geojson = geojson.load(dep_file)

service_account = 'tnslabs@solar-fuze-338810.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, os.getenv("PRIVATE_KEY"))
ee.Initialize(credentials)

assets_list = ee.data.getList(params={'id': "users/cajusupport/drones_geotiff"})
drones_images_ids = [
    (asset['id'].replace("projects/earthengine-legacy/assets/users/cajusupport/drones_geotiff/", ""))
    for asset in assets_list
]


class BeninPlantationStatsObject:
    def __init__(self, **entries):
        self.r_total_grand_pred_yield = None
        self.r_total_grand_ground_yield = None
        self.grand_plantation_size = None
        self.total_grand_ground_surface = None
        self.total_grand_pred_surface = None
        self.average_pred_yield_ha = None
        self.average_ground_yield_ha = None
        self.r_total_grand_num_tree = None
        self.total_grand_yield_tree = None
        self.counter = None
        self.__dict__.update(entries)


def __highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def __get_department_name(code, coordinates):
    def ___location_finder__():
        """
        Read geolocalization data from 'ben_adm1.json' file
        Check whenever a Point defined by the longitude and latitude passed in parameter belongs to a department in
        Benin
        Return the name of the department found or 'Unknown' otherwise
        """
        point = Point(coordinates[1], coordinates[0])
        for feature_dep in departments_geojson['features']:
            polygon = shape(feature_dep['geometry'])
            if polygon.contains(point):
                return feature_dep["properties"]["NAME_1"]
        return None

    departments = {
        "ALI": "Alibori",
        "ATA": "Atacora",
        "ATL": "Atlantique",
        "BOR": "Borgou",
        "COL": "Collines",
        "KOU": "Kouffo",
        "DON": "Donga",
        "LIT": "Littoral",
        "MON": "Mono",
        "OUE": "Oueme",
        "PLA": "Plateau",
        "ZOU": "Zou",
    }
    try:
        name = departments[(code[0:3].upper())]
    except Exception:
        name = ___location_finder__()
    return name


def __get_satellite_estimation_data(feature, dept_yield_ha, code, code_2, coordinate_xy):
    plantation_size = area(feature['geometry']) / 10000
    plantation_size = round(plantation_size, 1)

    tree_ha_pred_plant = round(
        round(AlteiaData.objects.filter(plantation_code=code)[0].cashew_tree_cover / 10000, 2), 1)
    department_name = __get_department_name(code_2, coordinate_xy)

    yield_pred_plant = int(tree_ha_pred_plant * dept_yield_ha[department_name])
    try:
        r_yield_pred_plant = round(yield_pred_plant, 1 - int(
            floor(log10(abs(yield_pred_plant))))) if yield_pred_plant < 90000 \
            else round(yield_pred_plant, 2 - int(floor(log10(abs(yield_pred_plant)))))
    except Exception:
        r_yield_pred_plant = yield_pred_plant

    return {
        "plantation_size": plantation_size,
        "cashew_yield": r_yield_pred_plant / 1000,
        "tree_ha_pred_plant": tree_ha_pred_plant,
        "department_name": department_name,
        "yield_pred_plant": yield_pred_plant,
        "r_yield_pred_plant": r_yield_pred_plant,
        "cashew_surface_area": tree_ha_pred_plant,
        "yield_per_hectare": dept_yield_ha[department_name],
        "number_of_trees_p": "N/A",
        "yield_per_tree_p": "N/A",
    }


def __get_tns_survey_data(code_2):
    benin_yield = BeninYield.objects.filter(plantation_code=code_2)[0]
    surface_area_p = round(benin_yield.surface_area, 1)
    total_yield_p = int(round(benin_yield.total_yield_kg))
    yield_ha_p = int(total_yield_p / surface_area_p)
    num_tree_p = int(benin_yield.total_number_trees)
    yield_tree_p = int(round(total_yield_p / num_tree_p))
    name_p = benin_yield.owner_first_name + ' ' + benin_yield.owner_last_name
    village = benin_yield.village

    try:
        r_total_yield_p = round(total_yield_p,
                                1 - int(floor(log10(abs(total_yield_p))))) if total_yield_p < 90000 else round(
            total_yield_p, 2 - int(floor(log10(abs(total_yield_p)))))
    except Exception:
        r_total_yield_p = total_yield_p

    return {
        "plantation_owner": name_p,
        "village": village,
        "cashew_yield": r_total_yield_p / 1000,
        "plantation_size": surface_area_p,
        "cashew_surface_area": "N/A",
        "yield_per_hectare": yield_ha_p,
        "number_of_trees_p": num_tree_p,
        "yield_per_tree_p": yield_tree_p,
    }


def __check_if_plantation_has_drone_image(code):
    try:
        if code in drones_images_ids:
            return True
    except Exception:
        return False


def __build_popup(feature, temp_layer_a, dept_yield_ha, path_link, code, statistics_obj, coordinate_xy):
    # Plantation translation variables
    plantation_owner = gettext("Plantation Owner")
    plantation_id = gettext("Plantation ID")
    village_text = gettext("Village")
    satellite_estimate = gettext("Satellite Estimate")
    yield_survey = gettext("2020 Yield Survey")
    cashew_yield = gettext("Cashew Yield (kg)")
    plantation_size = gettext("Plantation Size (ha)")
    cashew_surface_area = gettext("Cashew Surface Area (ha)")
    yield_per_hectare = gettext("Yield Per Hectare (kg/ha)")
    number_of_trees_p = gettext("Number of Trees")
    yield_per_tree_p = gettext("Yield per Tree (kg/tree)")
    average_surface_area_p = gettext(
        "Average Surface Area and Cashew Yield Information for Plantations in Benin Republic")
    number_of_farms = gettext("Number of Farms")
    total_plantation_yield = gettext("Total Plantation Yield (kg)")
    total_plantation_area = gettext("Total Plantation Area (ha)")
    cashew_surface_area = gettext("Cashew Surface Area (ha)")
    average_yield_per = gettext("Average Yield Per Hectare (kg/ha)")
    total_number_of = gettext("Total Number of Trees")
    average_yield_per = gettext("Average Yield per Tree (kg/tree)")
    source_tns = gettext("Source: TNS/BeninCaju Yield Surveys 2020")
    view_drone_image = gettext("View Drone Image")
    unknown = gettext("Unknown")
    has_survey_data = True
    survey_data = {}
    code_2 = ""
    try:
        code_2 = SpecialTuple.objects.filter(alteia_id=code)[0].plantation_id
        survey_data = __get_tns_survey_data(code_2)
    except Exception:
        has_survey_data = False
    satellite_data = __get_satellite_estimation_data(feature, dept_yield_ha, code, code_2, coordinate_xy)
    has_drone_image = __check_if_plantation_has_drone_image(code)
    drone_image_button = f'''
    <div style= "text-align: center">
        <button class="btn" style="border: none;
        background: none;background-color: #FFFFFF; padding: 0;
        color: "black";" onclick= "window.open('{path_link}drone/{code}/{coordinate_xy}','_blank')" role="button"> 
        <i class="fab fa-accusoft me-2"></i>{view_drone_image}
        </button>
    </div>
    '''
    drone_image_button_bottom = f'''
    <div style= "text-align: center">
        <button class="btn btn-outline-light" style="background-color: #004b55;"
        onclick= "window.open('{path_link}drone/{code}/{coordinate_xy}','_blank')" role="button"> 
        <i class="fab fa-accusoft me-2"></i>{view_drone_image}
        </button>
    </div>
    '''

    try:
        html_a = f'''
        <html>
        <head>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <link rel="icon" href="img/mdb-favicon.ico" type="image/x-icon" />
            <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.15.2/css/all.css" />
            <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900
            &display=swap" />
            <link rel="stylesheet" href="css/mdb.min.css" />
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>

            <style>
                table {{
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 99%;
                }}


                table th {{
                background-color: #004b55;
                text-align: left;
                color: #FFF;
                padding: 4px 30px 4px 8px;
                }}


                table td {{
                border: 1px solid #e3e3e3;
                padding: 4px 8px;
                }}


                table tr:nth-child(odd) td{{
                background-color: #e7edf0;
                }}
            </style>

            </head>
            <body>


                <h6>{plantation_owner}: {survey_data["plantation_owner"] if has_survey_data else unknown}</h3>
                <h6>{plantation_id}: {code}</h4>
                <h6>{village_text}: {survey_data["village"] if has_survey_data else unknown}</h4>
                {drone_image_button if has_drone_image else ""}
                <table>
                <tr>
                    <th></th>
                    <th>{satellite_estimate}</th>
                    <th>{yield_survey}</th>
                </tr>
                <tr>
                    <td>{cashew_yield}</td>
                    <td>{satellite_data["cashew_yield"]}K</td>
                    <td>{(survey_data["cashew_yield"].__str__() + "K") if has_survey_data else "N/A"}</td>       
                </tr>
                <tr>
                    <td>{plantation_size}</td>
                    <td>{satellite_data["plantation_size"]}</td>
                    <td>{survey_data["plantation_size"] if has_survey_data else "N/A"}</td>
                </tr>
                <tr>
                    <td>{cashew_surface_area}</td>
                    <td>{satellite_data["cashew_surface_area"]}</td>
                    <td>{survey_data["cashew_surface_area"] if has_survey_data else "N/A"}</td>
                </tr>
                <tr>
                    <td>{yield_per_hectare}</td>
                    <td>{satellite_data["yield_per_hectare"]}</td>
                    <td>{survey_data["yield_per_hectare"] if has_survey_data else "N/A"}</td>  
                </tr>
                <tr>
                    <td>{number_of_trees_p}</td>
                    <td>{satellite_data["number_of_trees_p"]}</td>
                    <td>{survey_data["number_of_trees_p"] if has_survey_data else "N/A"}</td>
                </tr>
                <tr>
                    <td>{yield_per_tree_p}</td>
                    <td>{satellite_data["yield_per_tree_p"]}</td>
                    <td>{survey_data["yield_per_tree_p"] if has_survey_data else "N/A"}</td>
                </tr>

                </table>

                <h6>
                {average_surface_area_p}
                </h6>
                <table>
                <tr>
                    <th></th>
                    <th>{satellite_estimate}</th>
                    <th>{yield_survey}</th>
                </tr>
                <tr>
                    <td>{number_of_farms}</td>
                    <td>{statistics_obj.counter}</td>
                    <td>{statistics_obj.counter}</td>

                </tr>
                <tr>
                    <td>{total_plantation_yield}</td>
                    <td>{statistics_obj.r_total_grand_pred_yield / 1000:n}K</td>
                    <td>{statistics_obj.r_total_grand_ground_yield / 1000:n}K</td>

                </tr>
                <tr>
                    <td>{total_plantation_area}</td>
                    <td>{statistics_obj.grand_plantation_size}</td>
                    <td>{statistics_obj.total_grand_ground_surface}</td>

                </tr>
                <tr>
                    <td>{cashew_surface_area}</td>
                    <td>{statistics_obj.total_grand_pred_surface}</td>
                    <td>N/A</td>

                </tr>

                <tr>
                    <td>{average_yield_per}</td>
                    <td>{statistics_obj.average_pred_yield_ha}</td>
                    <td>{statistics_obj.average_ground_yield_ha}</td>

                </tr>
                <tr>
                    <td>{total_number_of}</td>
                    <td>N/A</td>
                    <td>{statistics_obj.r_total_grand_num_tree / 1000:n}K</td>
                </tr>
                <tr>
                    <td>{average_yield_per}</td>
                    <td>N/A</td>
                    <td>{statistics_obj.total_grand_yield_tree}</td>
                </tr>

                </table>
                <table>
                    <td> {drone_image_button_bottom if has_drone_image else ""} </td>
                </table>
                <table>
                    <div style= "text-align: center"><h6>{source_tns}</h6></div>
                </table>
                <script>
                window.open(
                    {path_link}/drone/{code}/{coordinate_xy}/',
                    '_blank'
                    );
                <script>

            </body>
            </html>
        '''
        iframe = folium.IFrame(html=html_a, width=365, height=380)

        folium.Popup(iframe, max_width=1000).add_to(temp_layer_a)
    except Exception as e:
        pass


def __build_stats(temp_geojson_a):
    # Computing the total statistics of all 1694 plantations
    grand_pred_surface = 0
    grand_ground_surface = 0
    grand_total_yield = 0
    grand_plantation_size = 0
    counter = 0
    grand_num_tree = 0
    for feature in temp_geojson_a.data['features']:
        # GEOJSON layer consisting of a single feature
        code_sum = feature["properties"]["Plantation code"]
        # items = len(SpecialTuple.objects.filter(alteia_id=code_sum))
        try:
            # if items != 0:
            counter += 1
            code_2_sum = SpecialTuple.objects.filter(
                alteia_id=code_sum)[0].plantation_id

            benin_yield_sum = BeninYield.objects.filter(plantation_code=code_2_sum)[0]
            # load statistics from the database and
            grand_pred_surface += round(
                AlteiaData.objects.filter(plantation_code=code_sum)[0].cashew_tree_cover / 10000, 2)
            grand_ground_surface += benin_yield_sum.surface_area
            grand_total_yield += benin_yield_sum.total_yield_kg
            grand_plantation_size += area(feature['geometry']) / 10000
            grand_num_tree += benin_yield_sum.total_number_trees
        except Exception as e:
            if type(e) is not IndexError:
                print(e)
            pass

    # formating statistics for displaying on popups

    average_pred_yield_ha = 390
    total_grand_pred_surface = int(round(grand_pred_surface))
    total_grand_ground_surface = int(round(grand_ground_surface))
    total_grand_pred_yield = int(round(390 * grand_pred_surface))
    total_grand_ground_yield = int(round(grand_total_yield))
    grand_plantation_size = int(round(grand_plantation_size))
    average_ground_yield_ha = int(
        total_grand_ground_yield / total_grand_ground_surface)
    total_grand_num_tree = int(round(grand_num_tree))
    total_grand_yield_tree = int(
        round(total_grand_ground_yield / total_grand_num_tree))

    # formating numbers greater than 90000 to show 91k

    r_total_grand_num_tree = round(total_grand_num_tree, 1 - int(
        floor(log10(abs(total_grand_num_tree))))) if total_grand_num_tree < 90000 \
        else round(total_grand_num_tree, 2 - int(floor(log10(abs(total_grand_num_tree)))))

    r_total_grand_pred_yield = round(total_grand_pred_yield, 1 - int(
        floor(log10(abs(total_grand_pred_yield))))) if total_grand_pred_yield < 90000 \
        else round(total_grand_pred_yield, 2 - int(floor(log10(abs(total_grand_pred_yield)))))

    r_total_grand_ground_yield = round(total_grand_ground_yield, 1 - int(
        floor(log10(abs(total_grand_ground_yield))))) if total_grand_ground_yield < 90000 \
        else round(total_grand_ground_yield, 2 - int(floor(log10(abs(total_grand_ground_yield)))))

    statistics_dict = {
        "r_total_grand_pred_yield": r_total_grand_pred_yield,
        "r_total_grand_ground_yield": r_total_grand_ground_yield,
        "grand_plantation_size": grand_plantation_size,
        "total_grand_ground_surface": total_grand_ground_surface,
        "total_grand_pred_surface": total_grand_pred_surface,
        "average_pred_yield_ha": average_pred_yield_ha,
        "average_ground_yield_ha": average_ground_yield_ha,
        "r_total_grand_num_tree": r_total_grand_num_tree,
        "total_grand_yield_tree": total_grand_yield_tree,
        "counter": counter,
    }

    return BeninPlantationStatsObject(**statistics_dict)


def __get_good_shapfiles_codes(temp_geojson_a):
    polygons = []
    good_codes = []
    for feature in temp_geojson_a.data['features']:
        code = feature["properties"]["Plantation code"]
        current_polygon = shape(feature['geometry'])
        intersect = False
        for polygon in polygons:
            if current_polygon.intersects(polygon):
                intersect = True
                break
        if intersect is False:
            polygons.append(current_polygon)
            good_codes.append(code)

    return good_codes


@shared_task(bind=True)
def add_benin_plantation(self, path_link, dept_yield_ha):
    benin_plantation_layer = folium.FeatureGroup(
        name=gettext('Plantation Locations'), show=True, overlay=True)

    # Adding Benin Plantation to the map
    plantation_cluster = MarkerCluster(name=gettext("Benin Plantations"))
    temp_geojson_a = folium.GeoJson(data=alteia_json,
                                    name='Alteia Plantation Data 2',
                                    highlight_function=__highlight_function)
    not_overlapping_plantation_codes = __get_good_shapfiles_codes(temp_geojson_a)
    statistics_obj = __build_stats(temp_geojson_a)
    nb = 0
    nb_failed = 0
    for feature in temp_geojson_a.data['features']:
        code = feature["properties"]["Plantation code"]
        if code not in not_overlapping_plantation_codes:
            nb_failed += 1
            continue
        # items = len(SpecialTuple.objects.filter(alteia_id=code))
        try:
            temp_layer_a = folium.GeoJson(feature, zoom_on_click=True)
            # if items != 0:

            # Getting the centroid of the plantation shapefile for use by the drone map and placing markers on the
            # plantation midpoint
            s = shape(feature["geometry"])
            centre = s.centroid
            coordinate_xy = [centre.y, centre.x]
            has_popup = True
            try:
                __build_popup(feature, temp_layer_a, dept_yield_ha, path_link, code, statistics_obj, coordinate_xy)
            except Exception:
                has_popup = False
                pass
            # consolidate individual features back into the main layer
            folium.Marker(location=coordinate_xy,
                          rise_on_hover=True,
                          rise_offset=250,
                          icon=folium.Icon(color="green" if has_popup else "black", icon="globe"),
                          popup=None).add_to(plantation_cluster)

            nb += 1
            temp_layer_a.add_to(benin_plantation_layer)
        except Exception as e:
            nb_failed += 1
            if type(e) is not IndexError:
                print(e)
            pass
    print(nb.__str__() + " + " + nb_failed.__str__() + " = " + (nb_failed + nb).__str__())
    plantation_cluster.add_to(benin_plantation_layer)
    return benin_plantation_layer
