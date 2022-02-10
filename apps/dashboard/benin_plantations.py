import asyncio
import time
from math import log10, floor

import folium
import geojson
from area import area
from celery import shared_task
from django.utils.translation import gettext
from folium.plugins import MarkerCluster
from shapely.geometry import shape

from apps.dashboard.models import AlteiaData
from apps.dashboard.models import BeninYield
from apps.dashboard.models import SpecialTuple
from joblib import Parallel, delayed


# Load the Benin Plantations shapefile
class DataObject:
    def __init__(self, **entries):
        self.coordinate_xy = None
        self.path_link = None
        self.counter = None
        self.yield_treeP = None
        self.department_name = None
        self.num_treeP = None
        self.yield_haP = None
        self.tree_ha_pred_plant = None
        self.surface_areaP = None
        self.plantation_size = None
        self.r_total_yieldP = None
        self.r_yield_pred_plant = None
        self.village = None
        self.code = None
        self.nameP = None
        self.dept_yield_ha = None
        self.feature = None
        self.temp_geojson_a = None
        self.benin_plantation_layer = None
        self.plantation_cluster = None
        self.__dict__.update(entries)

    def __str__(self):
        return {
            "coordinate_xy": self.coordinate_xy,
            "path_link": self.path_link,
            "counter": self.counter,
            "yield_treeP": self.yield_treeP,
            "department_name": self.department_name,
            "num_treeP": self.num_treeP,
            "yield_haP": self.yield_haP,
            "tree_ha_pred_plant": self.tree_ha_pred_plant,
            "surface_areaP": self.surface_areaP,
            "plantation_size": self.plantation_size,
            "r_total_yieldP": self.r_total_yieldP,
            "r_yield_pred_plant": self.r_yield_pred_plant,
            "village": self.village,
            "code": self.code,
            "nameP": self.nameP,
            "dept_yield_ha": self.dept_yield_ha,
            "feature": self.feature,
            "temp_geojson_a": self.temp_geojson_a,
            "benin_plantation_layer": self.benin_plantation_layer,
            "plantation_cluster": self.plantation_cluster,
        }.__str__()


with open("staticfiles/Data/CajuLab_Plantations.geojson", errors="ignore") as f:
    alteia_json = geojson.load(f)


def __highlight_function__(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def __build_html__view(data: DataObject):
    base_url = "http://127.0.0.1:8000"

    # Plantation translation variables
    Plantation_Owner = gettext("Plantation Owner")
    Plantation_ID = gettext("Plantation ID")
    Village = gettext("Village")
    Satellite_Estimate = gettext("Satellite Estimate")
    Yield_Survey = gettext("2020 Yield Survey")
    Cashew_Yield = gettext("Cashew Yield (kg)")
    Plantation_Size = gettext("Plantation Size (ha)")
    Cashew_Surface_Area = gettext("Cashew Surface Area (ha)")
    Yield_Per_Hectare = gettext("Yield Per Hectare (kg/ha)")
    Number_of_TreesP = gettext("Number of Trees")
    Yield_per_TreeP = gettext("Yield per Tree (kg/tree)")
    Average_Surface_AreaP = gettext(
        "Average Surface Area and Cashew Yield Information for Plantations in Benin Republic")

    Number_of_Farms = gettext("Number of Farms")
    Total_Plantation_Yield = gettext("Total Plantation Yield (kg)")
    Total_Plantation_Area = gettext("Total Plantation Area (ha)")
    Cashew_Surface_Area = gettext("Cashew Surface Area (ha)")
    Average_Yield_Per = gettext("Average Yield Per Hectare (kg/ha)")
    Total_Number_of = gettext("Total Number of Trees")
    Average_Yield_per = gettext("Average Yield per Tree (kg/tree)")
    Source_TNS = gettext("Source: TNS/BeninCaju Yield Surveys 2020")
    View_Drone_Image = gettext("View Drone Image")

    return f''' <html> <head> <link rel="stylesheet" 
    href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"> <link rel="icon" 
    href="img/mdb-favicon.ico" type="image/x-icon" /> <link rel="stylesheet" 
    href="https://use.fontawesome.com/releases/v5.15.2/css/all.css" /> <link rel="stylesheet" 
    href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap"/> <link 
    rel="stylesheet" href="css/mdb.min.css" /> <script 
    src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script> <script 
    src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script> 

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


                    <h6>{Plantation_Owner}: {data.nameP}</h3>
                    <h6>{Plantation_ID}: {data.code}</h4>
                    <h6>{Village}: {data.village}</h4>
                    <table>
                    <tr>
                        <th></th>
                        <th>{Satellite_Estimate}</th>
                        <th>{Yield_Survey}</th>
                    </tr>
                    <tr>
                        <td>{Cashew_Yield}</td>
                        <td>{data.r_yield_pred_plant / 1000:n}K</td>
                        <td>{data.r_total_yieldP / 1000:n}K</td>       
                    </tr>
                    <tr>
                        <td>{Plantation_Size}</td>
                        <td>{data.plantation_size}</td>
                        <td>{data.surface_areaP}</td>
                    </tr>
                    <tr>
                        <td>{Cashew_Surface_Area}</td>
                        <td>{data.tree_ha_pred_plant}</td>
                        <td>NA</td>
                    </tr>
                    <tr>
                        <td>{Yield_Per_Hectare}</td>
                        <td>{data.dept_yield_ha[data.department_name]}</td>
                        <td>{data.yield_haP}</td>  
                    </tr>
                    <tr>
                        <td>{Number_of_TreesP}</td>
                        <td>NA</td>
                        <td>{data.num_treeP}</td>
                    </tr>
                    <tr>
                        <td>{Yield_per_TreeP}</td>
                        <td>NA</td>
                        <td>{data.yield_treeP}</td>
                    </tr>

                    </table>

                    <h6>
                    {Average_Surface_AreaP}
                    </h6>
                    <table>
                    <tr>
                        <th></th>
                        <th>{Satellite_Estimate}</th>
                        <th>{Yield_Survey}</th>
                    </tr>
                    <tr>
                        <td>{Number_of_Farms}</td>
                        <td>{data.counter}</td>
                            <td>{data.counter}</td>

                    </tr>
                    <tr>
                        <td>{Total_Plantation_Yield}</td>
                        <td>{data.r_total_grand_pred_yield / 1000:n}K</td>
                        <td>{data.r_total_grand_ground_yield / 1000:n}K</td>

                    </tr>
                    <tr>
                        <td>{Total_Plantation_Area}</td>
                        <td>{data.grand_plantation_size}</td>
                        <td>{data.total_grand_ground_surface}</td>

                    </tr>
                    <tr>
                        <td>{Cashew_Surface_Area}</td>
                        <td>{data.total_grand_pred_surface}</td>
                        <td>NA</td>

                    </tr>

                    <tr>
                        <td>{Average_Yield_Per}</td>
                        <td>{data.average_pred_yield_ha}</td>
                        <td>{data.average_ground_yield_ha}</td>

                    </tr>
                    <tr>
                        <td>{Total_Number_of}</td>
                        <td>NA</td>
                        <td>{data.r_total_grand_num_tree / 1000:n}K</td>
                    </tr>
                    <tr>
                        <td>{Average_Yield_per}</td>
                        <td>NA</td>
                        <td>{data.total_grand_yield_tree}</td>
                    </tr>

                    </table>
                    <table>
                        <td><div style= "text-align: center">
                                <button class="btn btn-outline-light" style="background-color: #004b55;
                                " onclick= 
                                "window.open('{base_url}{data.path_link}drone/{data.code}/{data.coordinate_xy}/',
                                '_blank')" role="button"> <i class="fab fa-accusoft me-2"></i>
                                {View_Drone_Image}</button> 
                        </div></td>
                    </table>
                    <table>
                        <div style= "text-align: center"><h6>{Source_TNS}</h6></div>
                    </table>
                    <script>
                    window.open(
                        '{base_url}{data.path_link}/drone/{data.code}/{data.coordinate_xy}/',
                        '_blank'
                        );
                    <script>

                </body>
                </html>
            '''


def __task__(data: DataObject):
    # GEOJSON layer consisting of a single feature

    # if count > 463:
    #     break
    code = data.feature["properties"]["Plantation code"]
    data.code = code
    __items = len(SpecialTuple.objects.filter(alteia_id=code))
    if __items != 0:
        plantation_size = area(data.feature['geometry']) / 10000
        plantation_size = round(plantation_size, 1)
        data.plantation_size = plantation_size
        code_2 = SpecialTuple.objects.filter(alteia_id=code)[0].plantation_id
        temp_layer_a = folium.GeoJson(data.feature, zoom_on_click=True)
        department_name = BeninYield.objects.filter(plantation_code=code_2)[0].department
        data.department_name = department_name

        tree_ha_pred_plant = round(
            round(AlteiaData.objects.filter(plantation_code=code)[0].cashew_tree_cover / 10000, 2), 1)
        data.tree_ha_pred_plant = tree_ha_pred_plant

        yield_pred_plant = int(tree_ha_pred_plant * data.dept_yield_ha[department_name])
        surface_areaP = round(BeninYield.objects.filter(plantation_code=code_2)[0].surface_area, 1)
        data.surface_areaP = surface_areaP

        total_yieldP = int(round(BeninYield.objects.filter(plantation_code=code_2)[0].total_yield_kg))
        yield_haP = int(total_yieldP / surface_areaP)
        data.yield_haP = yield_haP

        num_treeP = int(BeninYield.objects.filter(plantation_code=code_2)[0].total_number_trees)
        data.num_treeP = num_treeP

        yield_treeP = int(round(total_yieldP / num_treeP))
        data.yield_treeP = yield_treeP

        nameP = BeninYield.objects.filter(plantation_code=code_2)[0].owner_first_name \
                + ' ' + \
                BeninYield.objects.filter(plantation_code=code_2)[0].owner_last_name
        data.nameP = nameP

        village = BeninYield.objects.filter(plantation_code=code_2)[0].village
        data.village = village

        try:
            r_total_yieldP = round(total_yieldP, 1 - int(floor(log10(abs(total_yieldP))))) \
                if total_yieldP < 90000 \
                else round(total_yieldP, 2 - int(floor(log10(abs(total_yieldP)))))
        except Exception:
            r_total_yieldP = total_yieldP
        data.r_total_yieldP = r_total_yieldP

        try:
            r_yield_pred_plant = round(yield_pred_plant, 1 - int(floor(log10(abs(yield_pred_plant))))) \
                if yield_pred_plant < 90000 \
                else round(yield_pred_plant, 2 - int(floor(log10(abs(yield_pred_plant)))))
        except Exception:
            r_yield_pred_plant = yield_pred_plant
        data.r_yield_pred_plant = r_yield_pred_plant

        # Getting the centroid of the plantation shapefile for use by the drone map and placing markers on the
        # plantation midpoint
        s = shape(data.feature["geometry"])
        data.s = s
        centre = s.centroid
        data.centre = centre
        coordinate_xy = [centre.y, centre.x]
        data.coordinate_xy = coordinate_xy

        # html template for the popups

        html_a = __build_html__view(data)

        iframe = folium.IFrame(html=html_a, width=365, height=380)

        folium.Popup(iframe, max_width=1000).add_to(temp_layer_a)

        # consolidate individual features back into the main layer

        folium.Marker(location=coordinate_xy,
                      rise_on_hover=True,
                      rise_offset=250,
                      icon=folium.Icon(color="green", icon="globe"),
                      popup=None).add_to(data.plantation_cluster)

        temp_layer_a.add_to(data.benin_plantation_layer)


def __build_data__(path_link, dept_yield_ha):
    data = {"path_link": path_link, "dept_yield_ha": dept_yield_ha}
    benin_plantation_layer = folium.FeatureGroup(name=gettext('Plantation Locations'), show=True, overlay=True)
    data["benin_plantation_layer"] = benin_plantation_layer
    # Adding Benin Plantation to the map
    plantation_cluster = MarkerCluster(name=gettext("Benin Plantations"))
    data["plantation_cluster"] = plantation_cluster

    temp_geojson_a = folium.GeoJson(data=alteia_json,
                                    name='Alteia Plantation Data 2',
                                    highlight_function=__highlight_function__)
    data["temp_geojson_a"] = temp_geojson_a

    # Computing the total statistics of all 171 plantations
    grand_pred_surface = 0
    grand_ground_surface = 0
    grand_total_yield = 0
    grand_plantation_size = 0
    counter = 0
    grand_num_tree = 0
    for feature in temp_geojson_a.data['features']:

        # GEOJSON layer consisting of a single feature
        code_sum = feature["properties"]["Plantation code"]
        items = len(SpecialTuple.objects.filter(alteia_id=code_sum))
        if items != 0:
            counter += 1
            code_2_sum = SpecialTuple.objects.filter(alteia_id=code_sum)[0].plantation_id

            # load statistics from the database and
            grand_pred_surface += round(
                AlteiaData.objects.filter(plantation_code=code_sum)[0].cashew_tree_cover / 10000, 2)
            grand_ground_surface += BeninYield.objects.filter(plantation_code=code_2_sum)[0].surface_area
            grand_total_yield += BeninYield.objects.filter(plantation_code=code_2_sum)[0].total_yield_kg
            grand_plantation_size += area(feature['geometry']) / 10000
            grand_num_tree += BeninYield.objects.filter(plantation_code=code_2_sum)[0].total_number_trees
    data["counter"] = counter
    data["grand_pred_surface"] = grand_pred_surface
    data["grand_ground_surface"] = grand_ground_surface
    data["grand_total_yield"] = grand_total_yield
    data["grand_plantation_size"] = grand_plantation_size
    data["grand_num_tree"] = grand_num_tree

    # formating statistics for displaying on popups

    average_pred_yield_ha = 390
    data["average_pred_yield_ha"] = average_pred_yield_ha
    total_grand_pred_surface = int(round(grand_pred_surface))
    data["total_grand_pred_surface"] = total_grand_pred_surface
    total_grand_ground_surface = int(round(grand_ground_surface))
    data["total_grand_ground_surface"] = total_grand_ground_surface
    total_grand_pred_yield = int(round(390 * grand_pred_surface))
    data["total_grand_pred_yield"] = total_grand_pred_yield
    total_grand_ground_yield = int(round(grand_total_yield))
    data["total_grand_ground_yield ="] = total_grand_ground_yield
    grand_plantation_size = int(round(grand_plantation_size))
    data["grand_plantation_size"] = grand_plantation_size
    average_ground_yield_ha = int(total_grand_ground_yield / total_grand_ground_surface)
    data["average_ground_yield_ha"] = average_ground_yield_ha
    total_grand_num_tree = int(round(grand_num_tree))
    data["total_grand_num_tree"] = total_grand_num_tree
    total_grand_yield_tree = int(round(total_grand_ground_yield / total_grand_num_tree))
    data["total_grand_yield_tree"] = total_grand_yield_tree

    # formating numbers greater than 90000 to show 91k

    r_total_grand_num_tree = round(total_grand_num_tree, 1 - int(floor(log10(abs(total_grand_num_tree))))) \
        if total_grand_num_tree < 90000 \
        else round(total_grand_num_tree, 2 - int(floor(log10(abs(total_grand_num_tree)))))
    data["r_total_grand_num_tree"] = r_total_grand_num_tree

    r_total_grand_pred_yield = round(total_grand_pred_yield, 1 - int(floor(log10(abs(total_grand_pred_yield))))) \
        if total_grand_pred_yield < 90000 \
        else round(total_grand_pred_yield, 2 - int(floor(log10(abs(total_grand_pred_yield)))))
    data["r_total_grand_pred_yield"] = r_total_grand_pred_yield

    r_total_grand_ground_yield = round(total_grand_ground_yield, 1 - int(floor(log10(abs(total_grand_ground_yield))))) \
        if total_grand_ground_yield < 90000 \
        else round(total_grand_ground_yield, 2 - int(floor(log10(abs(total_grand_ground_yield)))))
    data["r_total_grand_ground_yield"] = r_total_grand_ground_yield

    data["count"] = None
    data["feature"] = None

    return DataObject(**data)


@shared_task(bind=True)
def add_benin_plantation(self, path_link, dept_yield_ha):
    __start_time = time.time()
    data = __build_data__(path_link, dept_yield_ha)

    async def __main__():
        __loop = asyncio.get_event_loop()
        tasks = [
            __loop.run_in_executor(None, __task__, data)
            for data.count, data.feature in enumerate(data.temp_geojson_a.data['features'])
        ]
        await asyncio.gather(*tasks)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(__main__())
    loop.close()

    data.plantation_cluster.add_to(data.benin_plantation_layer)
    print("add_benin_plantation --- %s seconds ---" % (time.time() - __start_time))
    return data.benin_plantation_layer

# current_benin_plantation_layer = add_benin_plantation(current_benin_department_layer)
#
# scheduler = BackgroundScheduler()
#
#
# @scheduler.scheduled_job(IntervalTrigger(days=1))
# def update_benin_plantation_layer():
#     global current_benin_plantation_layer
#     current_benin_plantation_layer = add_benin_plantation(current_qars)
#
#
# scheduler.start()
