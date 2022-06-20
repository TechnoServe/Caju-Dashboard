import json
import time

import folium
import geojson
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from area import area
from celery import shared_task
from django.db.models import Sum, Avg
from django.utils.translation import gettext
from math import log10, floor

from apps.dashboard.models import BeninYield
from apps.dashboard.models import CommuneSatellite
from apps.dashboard.models import DeptSatellite
from apps.dashboard.scripts.get_qar_information import current_qars

heroku = False

# Load the Benin Departments shapefile
with open("staticfiles/json/ben_adm1.json", errors="ignore") as f:
    benin_adm1_json = geojson.load(f)
statellite_prediction_computed_data_json = open('staticfiles/statellite_prediction_computed_data.json')
data_dictionary = json.load(statellite_prediction_computed_data_json)


def __human_format__(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def __highlight_function__(feature):
    """
    Function to define the layer highlight style
    """
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def __get_average_nut_count__(qars: list, department):
    """
    Get the average of nut_count in the department passed as parameter in the benin republic area
    """

    _all = list(filter(lambda c: c.department == department, qars))
    total = 0
    count = len(_all)
    if count == 0:
        count = 1
    for i, x in enumerate(_all):
        total += x.nut_count
    result = total / count
    return "{:.2f}".format(result) if result != 0 else "NA"


def __get_average_defective_rate__(qars: list, department):
    """
    Get the average of defective_rate in the department passed as parameter in the benin republic area
    """

    _all = list(filter(lambda c: c.department == department, qars))
    total = 0
    count = len(_all)
    if count == 0:
        count = 1
    for i, x in enumerate(_all):
        total += x.defective_rate
    result = total / count
    return "{:.2f}".format(result) if result != 0 else "NA"


def __get_average_kor__(qars: list, department):
    """
    Get the average of kor in the department passed as parameter in the benin republic area
    """

    _all = list(filter(lambda c: c.department == department, qars))
    total = 0
    count = len(_all)
    if count == 0:
        count = 1
    for i, x in enumerate(_all):
        total += x.kor
    result = total / count
    return "{:.2f}".format(result) if result != 0 else "NA"


def __build_caj_q_html_view__(data: object) -> any:
    """
    popup's table for Caju Quality Information
    """

    satellite_est = gettext("Satellite Estimation")
    tns_survey = gettext("TNS Survey")
    nut_count_average = gettext("Nut Count Average")
    defective_rate_average = gettext("Defective Rate Average")
    kor_average = gettext("KOR Average")

    return f'''
                  <h4>Caju Quality Informations</h4>
                  <table>
                    <tr>
                        <th></th>
                        <th>{tns_survey}</th>
                    </tr>
                    <tr>
                        <td>{nut_count_average}</td>
                        <td>{__get_average_nut_count__(data.qars, data.department)}</td>                        
                    </tr>
                    <tr>
                        <td>{defective_rate_average}</td>
                        <td>{__get_average_defective_rate__(data.qars, data.department)}</td>                        
                    </tr>
                    <tr>
                        <td>{kor_average}</td>
                        <td>{__get_average_kor__(data.qars, data.department)}</td>                        
                    </tr>
                </table>
            '''


def __build_html_view__(data: object) -> any:
    """
    Return the HTML view of the Benin Republic departments Layer popup
    """

    # Variables for departmental translation
    active_trees = gettext("Active Trees")
    sick_trees = gettext("Sick Trees")
    dead_trees = gettext("Dead Trees")
    out_of_production = gettext("Out of Production Trees")
    cashew_trees_status = gettext("Cashew Trees Status in")
    is_ranked = gettext(" is ranked")
    year = gettext("In 2020, ")

    satellite_est = gettext("Satellite Estimation")
    tns_survey = gettext("TNS Survey")

    # All 3 shapefiles share these variables
    total_cashew_yield = gettext("Total Cashew Yield (kg)")
    total_area = gettext("Total Area (ha)")
    cashew_tree_cover = gettext("Cashew Tree Cover (ha)")
    protected_area = gettext("Protected Area (ha)")
    cashew_tree_cover_within_protected_area = gettext("Cashew Tree Cover Within Protected Area (ha)")
    yield_hectare = gettext("Yield/Hectare (kg/ha)")
    yield_per_tree = gettext("Yield per Tree (kg/tree)")
    number_of_trees = gettext("Number of Trees")
    source_tns = gettext("Source: TNS/BeninCaju Yield Surveys 2020")
    predicted_cashew_tree_d = gettext("Predicted Cashew Tree Cover Communes Statistics In")
    among_benin_departments = gettext(
        "among Benin departments in terms of total cashew yield according to the TNS Yield Survey")
    among_benin_departments_prediction = gettext(
        "among Benin departments in terms of total cashew yield according to the TNS Prediction Algorithm")

    return f'''
                <html>
                    <head>
                    <style>
                        table {{
                        font-family: arial, sans-serif;
                        border-collapse: collapse;
                        width: 100%;
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
                        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                        <script type="text/javascript">
                        // Load Charts and the corechart and barchart packages.
                        google.charts.load('current', {{'packages':['corechart']}});
                        google.charts.load('current', {{'packages':['bar']}});

                        // Draw the pie chart and bar chart when Charts is loaded.
                        google.charts.setOnLoadCallback(drawChart);

                        function drawChart() {{

                            var pie_data = new google.visualization.DataTable();
                            pie_data.addColumn('string', 'Commune');
                            pie_data.addColumn('number', 'Cashew Tree Cover');
                            pie_data.addRows({data.pred_dept_data});

                            var piechart_options = {{title:'{predicted_cashew_tree_d} {data.department}',
                                                        is3D: true,
                                                    }};
                            var piechart = new google.visualization.PieChart(document.getElementById('piechart_div'));
                            piechart.draw(pie_data, piechart_options);

                            

                            var data_donut = google.visualization.arrayToDataTable([
                            ['Tree Type', 'Number of Trees'],
                            ['{active_trees}',      {data.active_trees_d}],
                            ['{sick_trees}',      {data.sick_tree_d}],
                            ['{dead_trees}',     {data.dead_tree_d}],
                            ['{out_of_production}',      {data.out_prod_tree_d}],
                            ]);

                            var options_donut = {{
                            title: '{cashew_trees_status} {data.department}',
                            pieHole: 0.5,
                            colors: ['007f00', '#02a8b1', '9e1a1a', '#242526'],
                            }};

                            var chart_donut = new google.visualization.PieChart(document.getElementById('donutchart'));
                            chart_donut.draw(data_donut, options_donut);

                            }};
                        </script>
                    </head>
                    <body>
                        <h2>{data.department}</h2>
                        <h4>
                        {year}{data.department}{is_ranked}
                        {data.my_dict[str(data.predictions["rank"] - 1)]}
                        {among_benin_departments}.
                        </h4>

                        <table>
                            <tr>
                                <th></th>
                                <th>{satellite_est}</th>
                                <th>{tns_survey}</th>
                            </tr>
                            <tr>
                                <td>{total_cashew_yield}</td>
                                <td>{__human_format__(data.predictions["total cashew yield"])}</td>
                                <td>{data.r_total_yield_d / 1000000:n}M</td>
                            </tr>
                            <tr>
                                <td>{total_area}</td>
                                <td>{__human_format__(data.predictions["total area"])}</td>
                                <td>{data.r_surface_area_d / 1000:n}K</td>
                            </tr>
                            <tr>
                                <td>{protected_area}</td>
                                <td>{__human_format__(data.predictions["protected area"])}</td>
                                <td>NA</td>                            
                            </tr>
                            <tr>
                                <td>{cashew_tree_cover}</td>
                                <td>{__human_format__(data.predictions["cashew tree cover"])}</td>
                                <td>NA</td>                            
                            </tr>
                            <tr>
                                <td>{cashew_tree_cover_within_protected_area}</td>
                                <td>{__human_format__(data.predictions["cashew tree cover within protected area"])}</td>
                                <td>NA</td>                            
                            </tr>
                            <tr>
                                <td>{yield_hectare}</td>
                                <td>{__human_format__(data.predictions["yield per hectare"])}</td>
                                <td>{data.r_yield_ha_d}</td>
                            </tr>
                            <tr>
                                <td>{yield_per_tree}</td>
                                <td>
                                {__human_format__(data.predictions["yield per tree"]) if data.predictions["yield per tree"] != 0 else "N/A"}
                                </td>
                                <td>{data.r_yield_tree_d}</td>
                            </tr>
                            <tr>
                                <td>{number_of_trees}</td>
                                <td>
                                {__human_format__(data.predictions["number of trees"]) if data.predictions["number of trees"] != 0 else "N/A"}
                                </td>
                                <td>{data.r_num_tree_d / 1000:n}K</td>
                            </tr>
                        </table>
                        
                        &nbsp;&nbsp; 
                        {__build_caj_q_html_view__(data)}
                        &nbsp;&nbsp; 
                        
                        <table>
                            <td><div id="piechart_div" style="width: 400; height: 350;"></div></td>
                        </table>                           
                        <table>
                            <td><div id="donutchart" style="width: 400; height: 350;"></div></td>
                        </table>
                        <table>
                            <td><div style= "text-align: center"><h5>{source_tns}</h5></div>
                        </table> 
                    </body>
                    </html>
                '''


def __build_data__(feature, qars):
    """
    Return all the data needed to build the Benin republic departments Layer
    """

    data = {
        'qars': qars,
    }

    # GEOJSON layer consisting of a single feature
    department_name = feature["properties"]["NAME_1"]
    data["department"] = department_name
    data["predictions"] = data_dictionary[feature["properties"]["NAME_0"]][feature["properties"]["NAME_1"]][
        "properties"]

    z_list = []
    # looping through all departments in Benin Repubic to get the ranking

    for d in range(len(DeptSatellite.objects.all())):
        y = DeptSatellite.objects.all()[d].department
        x = CommuneSatellite.objects.filter(department=y).aggregate(Sum('cashew_tree_cover'))
        x = x['cashew_tree_cover__sum']
        z_list.append((y, x))

    sorted_by_second = sorted(z_list, reverse=True, key=lambda tup: tup[1])
    list1, _ = zip(*sorted_by_second)

    # A small logic to solve the French symbols department error when viewed on local host
    if heroku:
        position = list1.index(department_name)
    else:
        position = 1
    data["position"] = position
    my_dict = {'0': "highest", '1': "2nd", '2': "3rd", '3': "4th", '4': "5th", '5': "6th", '6': "7th", '7': "8th",
               '8': "9th", '9': "10th", '10': "11th", '11': "lowest"}
    data["my_dict"] = my_dict

    pred_dept_data = []
    pred_ground_dept_data = [['Communes', 'Satellite Prediction', 'Ground Data Estimate']]
    for c in CommuneSatellite.objects.filter(department=department_name):
        y = c.commune
        x = round(c.cashew_tree_cover / 10000, 2)
        pred_dept_data.append([y, x])
        pred_ground_dept_data.append([y, x, x])

    data["pred_dept_data"] = pred_dept_data
    data["pred_ground_dept_data"] = pred_ground_dept_data

    # load statistics from the database and formating them for displaying on popups.
    # The try catch is to avoid error that arise when we round null values

    tree_ha_pred_dept = CommuneSatellite.objects.filter(department=department_name).aggregate(Sum('cashew_tree_cover'))
    try:
        tree_ha_pred_dept = int(round(tree_ha_pred_dept['cashew_tree_cover__sum'] / 10000, 2))
    except Exception as e:
        tree_ha_pred_dept = 0
    data["tree_ha_pred_dept"] = tree_ha_pred_dept

    surface_area_d = BeninYield.objects.filter(department=department_name).aggregate(Sum('surface_area'))
    try:
        surface_area_d = int(round(surface_area_d['surface_area__sum'], 2))
    except Exception as e:
        surface_area_d = 0
    data["surface_area_d"] = surface_area_d

    total_yield_d = BeninYield.objects.filter(department=department_name).aggregate(Sum('total_yield_kg'))
    try:
        total_yield_d = int(round(total_yield_d['total_yield_kg__sum'], 2))
    except Exception as e:
        total_yield_d = 0
    data["total_yield_d"] = total_yield_d

    yield_ha_d = BeninYield.objects.filter(department=department_name).aggregate(Avg('total_yield_per_ha_kg'))
    try:
        yield_ha_d = int(round(yield_ha_d['total_yield_per_ha_kg__avg'], 2))
    except Exception as e:
        yield_ha_d = 0
    data["yield_ha_d"] = yield_ha_d

    # Used only in case of error in the try and except catch
    yield_tree_d = BeninYield.objects.filter(department=department_name).aggregate(Avg('total_yield_per_tree_kg'))
    try:
        yield_tree_d = int(round(yield_tree_d['total_yield_per_tree_kg__avg'], 2))
    except Exception as e:
        yield_tree_d = 0
    data["yield_tree_d"] = yield_tree_d

    num_tree_d = BeninYield.objects.filter(department=department_name).aggregate(Sum('total_number_trees'))
    try:
        num_tree_d = int(num_tree_d['total_number_trees__sum'])
    except Exception as e:
        num_tree_d = 0
    data["num_tree_d"] = num_tree_d

    sick_tree_d = BeninYield.objects.filter(department=department_name).aggregate(Sum('total_sick_trees'))
    try:
        sick_tree_d = int(sick_tree_d['total_sick_trees__sum'])
    except Exception as e:
        sick_tree_d = 0
    data["sick_tree_d"] = sick_tree_d

    out_prod_tree_d = BeninYield.objects.filter(department=department_name).aggregate(Sum('total_trees_out_of_prod'))
    try:
        out_prod_tree_d = int(out_prod_tree_d['total_trees_out_of_prod__sum'])
    except Exception as e:
        out_prod_tree_d = 0
    data["out_prod_tree_d"] = out_prod_tree_d

    dead_tree_d = BeninYield.objects.filter(department=department_name).aggregate(Sum('total_dead_trees'))
    try:
        dead_tree_d = int(round(dead_tree_d['total_dead_trees__sum'], 2))
    except Exception as e:
        dead_tree_d = 0
    data["dead_tree_d"] = dead_tree_d

    region_size_d = area(feature['geometry']) / 10000
    try:
        active_trees_d = num_tree_d - sick_tree_d - out_prod_tree_d - dead_tree_d
    except Exception as e:
        active_trees_d = 0
    data["active_trees_d"] = active_trees_d

    try:
        r_tree_ha_pred_dept = round(tree_ha_pred_dept, 1 - int(
            floor(log10(abs(tree_ha_pred_dept))))) if tree_ha_pred_dept < 90000 else round(tree_ha_pred_dept,
                                                                                           2 - int(floor(log10(
                                                                                               abs(tree_ha_pred_dept)))))
    except Exception as e:
        r_tree_ha_pred_dept = tree_ha_pred_dept
    data["r_tree_ha_pred_dept"] = r_tree_ha_pred_dept

    try:
        r_surface_area_d = round(surface_area_d,
                                 1 - int(floor(log10(abs(surface_area_d))))) if surface_area_d < 90000 else round(
            surface_area_d, 2 - int(floor(log10(abs(surface_area_d)))))
    except Exception as e:
        r_surface_area_d = surface_area_d
    data["r_surface_area_d"] = r_surface_area_d

    try:
        r_total_yield_d = round(total_yield_d,
                                1 - int(floor(log10(abs(total_yield_d))))) if total_yield_d < 90000 else round(
            total_yield_d, 2 - int(floor(log10(abs(total_yield_d)))))
    except Exception as e:
        r_total_yield_d = total_yield_d
    data["r_total_yield_d"] = r_total_yield_d

    try:
        r_yield_ha_d = round(yield_ha_d, 1 - int(floor(log10(abs(yield_ha_d))))) if yield_ha_d < 90000 else round(
            yield_ha_d, 2 - int(floor(log10(abs(yield_ha_d)))))
    except Exception as e:
        r_yield_ha_d = yield_ha_d
    data["r_yield_ha_d"] = r_yield_ha_d

    try:
        yield_pred_dept = int(r_yield_ha_d * tree_ha_pred_dept)
    except Exception as e:
        yield_pred_dept = 0
    data["yield_pred_dept"] = yield_pred_dept

    try:
        r_yield_pred_dept = round(yield_pred_dept, 1 - int(
            floor(log10(abs(yield_pred_dept))))) if yield_pred_dept < 90000 else round(yield_pred_dept, 2 - int(
            floor(log10(abs(yield_pred_dept)))))
    except Exception as e:
        r_yield_pred_dept = yield_pred_dept
    data["r_yield_pred_dept"] = r_yield_pred_dept

    try:
        r_yield_tree_d = round(r_total_yield_d / active_trees_d)
    except Exception as e:
        r_yield_tree_d = yield_tree_d
    data["r_yield_tree_d"] = r_yield_tree_d

    try:
        r_num_tree_d = round(num_tree_d, 1 - int(floor(log10(abs(num_tree_d))))) if num_tree_d < 90000 else round(
            num_tree_d, 2 - int(floor(log10(abs(num_tree_d)))))
    except Exception as e:
        r_num_tree_d = num_tree_d
    data["r_num_tree_d"] = r_num_tree_d

    try:
        r_region_size_d = round(region_size_d,
                                1 - int(floor(log10(abs(region_size_d))))) if region_size_d < 90000 else round(
            region_size_d, 2 - int(floor(log10(abs(region_size_d)))))
    except Exception as e:
        r_region_size_d = region_size_d
    data["r_region_size_d"] = r_region_size_d

    return data


@shared_task(bind=True)
def add_benin_department(self, qars):
    """
    Adding the shapefiles with popups for the Benin Republic departments
    Add benin republic departments data to the parent layer
    """
    __start_time = time.time()

    class DataObject:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    # alldept = ee.Image('users/cajusupport/allDepartments_v1')
    # zones = alldept.eq(1)
    # zones = zones.updateMask(zones.neq(0))

    benin_departments_layer = folium.FeatureGroup(name=gettext('Benin Departments'), show=False, overlay=False)
    departments_geojson = folium.GeoJson(data=benin_adm1_json,
                                         name='Benin-Adm1 Department',
                                         highlight_function=__highlight_function__)

    dept_yield_ha = {}

    for feature in departments_geojson.data['features']:
        department_partial_layer = folium.GeoJson(feature, zoom_on_click=False,
                                                  highlight_function=__highlight_function__,
                                                  )
        data = __build_data__(feature, qars)
        dept_yield_ha[data["department"]] = data["yield_ha_d"]

        obj = DataObject(**data)
        # html template for the popups
        html_view = __build_html_view__(obj)
        # Popup size and frame declaration
        iframe = folium.IFrame(html=html_view, width=600, height=400)

        folium.Popup(iframe, max_width=2000).add_to(department_partial_layer)

        # consolidate individual features back into the main layer
        folium.GeoJsonTooltip(fields=["NAME_1"],
                              aliases=["Department:"],
                              labels=True,
                              sticky=False,
                              style=(
                                  "background-color: white; color: black; font-family: sans-serif; font-size: 12px; "
                                  "padding: 4px;")
                              ).add_to(department_partial_layer)

        department_partial_layer.add_to(benin_departments_layer)

    return benin_departments_layer, dept_yield_ha


current_benin_department_layer = add_benin_department(current_qars)

scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(days=1))
def update_benin_department_layer():
    global current_benin_department_layer
    current_benin_department_layer = add_benin_department(current_qars)


scheduler.start()