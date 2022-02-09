from math import log10, floor

import folium
import geojson
from area import area
from celery import shared_task
from django.db.models import Sum, Avg
from django.utils.translation import gettext

from apps.dashboard.models import BeninYield
from apps.dashboard.models import CommuneSatellite
from apps.dashboard.scripts.get_qar_information import QarObject

heroku = False

# Load the Benin Communes shapefile
with open("staticfiles/json/ben_adm2.json", errors="ignore") as f:
    benin_adm2_json = geojson.load(f)


def __highlight_function__(feature):
    """
    Function to define the layer highlight style
    """
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def __get_average_nut_count__(qars: list[QarObject], commune):
    """
      Get the average of nut_count in the commune passed as parameter in the benin republic area
    """

    _all = list(filter(lambda c: c.commune == commune, qars))
    total = 0
    count = len(_all)
    if count == 0:
        count = 1
    for i, x in enumerate(_all):
        total += x.nut_count
    result = total / count
    return "{:.2f}".format(result) if result != 0 else "NA"


def __get_average_defective_rate__(qars: list[QarObject], commune):
    """
    Get the average of defective_rate in the commune passed as parameter in the benin republic area
    """

    _all = list(filter(lambda c: c.commune == commune, qars))
    total = 0
    count = len(_all)
    if count == 0:
        count = 1
    for i, x in enumerate(_all):
        total += x.defective_rate
    result = total / count
    return "{:.2f}".format(result) if result != 0 else "NA"


def __get_average_kor__(qars: list[QarObject], commune):
    """
    Get the average of kor in the commune passed as parameter in the benin republic area
    """

    _all = list(filter(lambda c: c.commune == commune, qars))
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

    satellite_est = gettext("Satellite Est")
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
                        <td>{__get_average_nut_count__(data.qars, data.commune)}</td>                        
                    </tr>
                    <tr>
                        <td>{defective_rate_average}</td>
                        <td>{__get_average_defective_rate__(data.qars, data.commune)}</td>                        
                    </tr>
                    <tr>
                        <td>{kor_average}</td>
                        <td>{__get_average_kor__(data.qars, data.commune)}</td>                        
                    </tr>
                </table>
            '''


def __build_html_view__(data: object) -> any:
    """
    Return the HTML view of the Benin Republic communes Layer popup
    """
    # Commune translation variable
    departments_cashew_tree = gettext('Departments Cashew Tree Cover Statistics In')
    active_trees = gettext("Active Trees")
    sick_trees = gettext("Sick Trees")
    dead_trees = gettext("Dead Trees")
    out_of_production = gettext("Out of Production Trees")
    cashew_trees_status = gettext("Cashew Trees Status in")
    is_ranked = gettext("is ranked")
    satellite_est = gettext("Satellite Est")
    tns_survey = gettext("TNS Survey")

    # All 3 shapefiles share these variables
    total_cashew_yield = gettext("Total Cashew Yield (kg)")
    total_area = gettext("Total Area (ha)")
    cashew_tree_cover = gettext("Cashew Tree Cover (ha)")
    yield_hectare = gettext("Yield/Hectare (kg/ha)")
    yield_per_tree = gettext("Yield per Tree (kg/tree)")
    number_of_trees = gettext("Number of Trees")
    source_tns = gettext("Source: TNS/BeninCaju Yield Surveys 2020")
    among_benin_communes = gettext(
        "among Benin communes in terms of total cashew yield according to the TNS Yield Survey")

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

                            var data_donut = google.visualization.arrayToDataTable([
                            ['Tree Type', 'Number of Trees'],
                            ['{active_trees}',      {data.active_treesC}],
                            ['{sick_trees}',      {data.sick_treeC}],
                            ['{dead_trees}',     {data.dead_treeC}],
                            ['{out_of_production}',      {data.out_prod_treeC}],
                            ]);

                            var options_donut = {{
                            title: '{cashew_trees_status} {data.commune}',
                            pieHole: 0.5,
                            colors: ['007f00', '#02a8b1', '9e1a1a', '#242526'],
                            }};

                            var chart_donut = new google.visualization.PieChart(document.getElementById('donutchart'));
                            chart_donut.draw(data_donut, options_donut);

                            }};
                        </script>
                    </head>
                    <body>

                        <h2>{data.commune}</h2>
                        <h4>In 2020, {data.commune} {is_ranked} <b>{data.my_dict_communes[str(data.position2 + 1)]}</b>
                         {among_benin_communes}.</h4> 
                        <table>
                        <tr>
                            <th></th>
                            <th>{satellite_est}</th>
                            <th>{tns_survey}</th>
                            
                        </tr>
                        <tr>
                            <td>{total_cashew_yield}</td>
                            <td>{data.r_yield_pred_comm / 1000000:n}M</td>
                            <td>{data.r_total_yieldC / 1000000:n}M</td>
                            
                        </tr>
                        <tr>
                            <td>{total_area}</td>
                            <td>{data.r_region_sizeC / 1000:n}K</td>
                            <td>{data.r_surface_areaC / 1000:n}K</td>
                        </tr>
                        <tr>
                            <td>{cashew_tree_cover}</td>
                            <td>{data.r_tree_ha_pred_comm / 1000:n}K</td>
                            <td>NA</td>
                            
                        </tr>
                        <tr>
                            <td>{yield_hectare}</td>
                            <td>390</td>
                            <td>{data.r_yield_haC}</td>
                        
                        </tr>
                        <tr>
                            <td>{yield_per_tree}</td>
                            <td>NA</td>
                            <td>{data.r_yield_treeC}</td>
                        
                        </tr>
                        <tr>
                            <td>{number_of_trees}</td>
                            <td>NA</td>
                            <td>{data.r_num_treeC / 1000:n}K</td>                            
                        </tr>
                        </table>
                                                
                        &nbsp;&nbsp; 
                        {__build_caj_q_html_view__(data)}
                        &nbsp;&nbsp; 
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
    Return all the data needed to build the Benin republic communes Layer
    """
    data = {"qars": qars}

    # GEOJSON layer consisting of a single feature
    commune = feature["properties"]["NAME_2"]
    data["commune"] = commune

    # looping through all communes in Benin Repubic to get the ranking
    z_list = []
    for c in range(len(CommuneSatellite.objects.all())):
        y = CommuneSatellite.objects.all()[c].commune
        x = CommuneSatellite.objects.filter(commune=y).aggregate(Sum('cashew_tree_cover'))
        x = x['cashew_tree_cover__sum']
        z_list.append((y, x))

    sorted_by_second = sorted(z_list, reverse=True, key=lambda tup: tup[1])
    list2, _ = zip(*sorted_by_second)

    # A small logic to solve the French symbols name error when viewed on local host
    if heroku:
        position2 = list2.index(commune)
    else:
        position2 = 1
    data["position2"] = position2

    # formatted rankings in dictionary format
    my_dict_communes = {'1': 'highest', '2': '2nd', '3': '3rd', '4': '4th', '5': '5th', '6': '6th', '7': '7th',
                        '8': '8th', '9': '9th', '10': '10th',
                        '11': '11th', '12': '12th', '13': '13th', '14': '14th', '15': '15th', '16': '16th',
                        '17': '17th', '18': '18th', '19': '19th', '20': '20th',
                        '21': '21st', '22': '22nd', '23': '23rd', '24': '24th', '25': '25th', '26': '26th',
                        '27': '27th', '28': '28th', '29': '29th', '30': '30th',
                        '31': '31st', '32': '32nd', '33': '33rd', '34': '34th', '35': '35th', '36': '36th',
                        '37': '37th', '38': '38th', '39': '39th', '40': '40th',
                        '41': '41st', '42': '42nd', '43': '43rd', '44': '44th', '45': '45th', '46': '46th',
                        '47': '47th', '48': '48th', '49': '49th', '50': '50th',
                        '51': '51st', '52': '52nd', '53': '53rd', '54': '54th', '55': '55th', '56': '56th',
                        '57': '57th', '58': '58th', '59': '59th', '60': '60th',
                        '61': '61st', '62': '62nd', '63': '63rd', '64': '64th', '65': '65th', '66': '66th',
                        '67': '67th', '68': '68th', '69': '69th', '70': '70th',
                        '71': '71st', '72': '72nd', '73': '73rd', '74': '74th', '75': '75th', '76': 'lowest'}
    data["my_dict_communes"] = my_dict_communes

    # load statistics from the database and formating them for displaying on popups

    tree_ha_pred_comm = CommuneSatellite.objects.filter(commune=commune).aggregate(Sum('cashew_tree_cover'))
    try:
        tree_ha_pred_comm = int(round(tree_ha_pred_comm['cashew_tree_cover__sum'] / 10000, 2))
    except Exception as e:
        tree_ha_pred_comm = 0
    data["tree_ha_pred_comm"] = tree_ha_pred_comm

    try:
        yield_pred_comm = int(390 * tree_ha_pred_comm)
    except Exception as e:
        yield_pred_comm = 0
    data["yield_pred_comm"] = yield_pred_comm

    surface_areaC = BeninYield.objects.filter(commune=commune).aggregate(Sum('surface_area'))
    try:
        surface_areaC = int(round(surface_areaC['surface_area__sum'], 2))
    except Exception as e:
        surface_areaC = 0
    data["surface_areaC"] = surface_areaC

    total_yieldC = BeninYield.objects.filter(commune=commune).aggregate(Sum('total_yield_kg'))
    try:
        total_yieldC = int(round(total_yieldC['total_yield_kg__sum'], 2))
    except Exception as e:
        total_yieldC = 0
    data["total_yieldC"] = total_yieldC

    yield_haC = BeninYield.objects.filter(commune=commune).aggregate(Avg('total_yield_per_ha_kg'))
    try:
        yield_haC = int(round(yield_haC['total_yield_per_ha_kg__avg'], 2))
    except Exception as e:
        yield_haC = 0
    data["yield_haC"] = yield_haC

    # Used only in case of error in the try and except catch
    yield_treeC = BeninYield.objects.filter(commune=commune).aggregate(Avg('total_yield_per_tree_kg'))
    try:
        yield_treeC = int(round(yield_treeC['total_yield_per_tree_kg__avg'], 2))
    except Exception as e:
        yield_treeC = 0
    data["yield_treeC"] = yield_treeC

    num_treeC = BeninYield.objects.filter(commune=commune).aggregate(Sum('total_number_trees'))
    try:
        num_treeC = int(num_treeC['total_number_trees__sum'])
    except Exception as e:
        num_treeC = 0
    data["num_treeC"] = num_treeC

    sick_treeC = BeninYield.objects.filter(commune=commune).aggregate(Sum('total_sick_trees'))
    try:
        sick_treeC = int(sick_treeC['total_sick_trees__sum'])
    except Exception as e:
        sick_treeC = 0
    data["sick_treeC"] = sick_treeC

    out_prod_treeC = BeninYield.objects.filter(commune=commune).aggregate(Sum('total_trees_out_of_prod'))
    try:
        out_prod_treeC = int(out_prod_treeC['total_trees_out_of_prod__sum'])
    except Exception as e:
        out_prod_treeC = 0
    data["out_prod_treeC"] = out_prod_treeC

    dead_treeC = BeninYield.objects.filter(commune=commune).aggregate(Sum('total_dead_trees'))
    try:
        dead_treeC = int(round(dead_treeC['total_dead_trees__sum'], 2))
    except Exception as e:
        dead_treeC = 0
    data["dead_treeC"] = dead_treeC

    region_sizeC = area(feature['geometry']) / 10000
    try:
        active_treesC = num_treeC - sick_treeC - out_prod_treeC - dead_treeC
    except Exception as e:
        active_treesC = 0
    data["active_treesC"] = active_treesC

    # formating numbers greater than 90000 to show 91k
    try:
        r_region_sizeC = round(region_sizeC, 1 - int(floor(log10(abs(region_sizeC))))) \
            if region_sizeC < 90000 \
            else round(region_sizeC, 2 - int(floor(log10(abs(region_sizeC)))))
    except Exception as e:
        r_region_sizeC = region_sizeC
    data["r_region_sizeC"] = r_region_sizeC

    try:
        r_tree_ha_pred_comm = round(tree_ha_pred_comm, 1 - int(
            floor(log10(abs(tree_ha_pred_comm))))) \
            if tree_ha_pred_comm < 90000 \
            else round(tree_ha_pred_comm, 2 - int(floor(log10(abs(tree_ha_pred_comm)))))
    except Exception as e:
        r_tree_ha_pred_comm = tree_ha_pred_comm
    data["r_tree_ha_pred_comm"] = r_tree_ha_pred_comm

    try:
        r_yield_pred_comm = round(yield_pred_comm, 1 - int(
            floor(log10(abs(yield_pred_comm))))) \
            if yield_pred_comm < 90000 \
            else round(yield_pred_comm, 2 - int(floor(log10(abs(yield_pred_comm)))))
    except Exception as e:
        r_yield_pred_comm = yield_pred_comm
    data["r_yield_pred_comm"] = r_yield_pred_comm

    try:
        r_surface_areaC = round(surface_areaC, 1 - int(floor(log10(abs(surface_areaC))))) \
            if surface_areaC < 90000 \
            else round(surface_areaC, 2 - int(floor(log10(abs(surface_areaC)))))
    except Exception as e:
        r_surface_areaC = surface_areaC
    data["r_surface_areaC"] = r_surface_areaC

    try:
        r_total_yieldC = round(total_yieldC, 1 - int(floor(log10(abs(total_yieldC))))) \
            if total_yieldC < 90000 \
            else round(total_yieldC, 2 - int(floor(log10(abs(total_yieldC)))))
    except Exception as e:
        r_total_yieldC = total_yieldC
    data["r_total_yieldC"] = r_total_yieldC

    try:
        r_yield_haC = round(yield_haC, 1 - int(floor(log10(abs(yield_haC))))) \
            if yield_haC < 90000 \
            else round(yield_haC, 2 - int(floor(log10(abs(yield_haC)))))
    except Exception as e:
        r_yield_haC = yield_haC
    data["r_yield_haC"] = r_yield_haC

    # try: r_yield_treeC = round(yield_treeC, 1-int(floor(log10(abs(yield_treeC))))) if yield_treeC < 90000 else
    # round(yield_treeC, 2-int(floor(log10(abs(yield_treeC))))) except Exception as e: r_yield_treeC = yield_treeC

    try:
        r_yield_treeC = round(r_total_yieldC / active_treesC)
    except Exception as e:
        r_yield_treeC = yield_treeC
    data["r_yield_treeC"] = r_yield_treeC

    try:
        r_num_treeC = round(num_treeC, 1 - int(floor(log10(abs(num_treeC))))) \
            if num_treeC < 90000 \
            else round(num_treeC, 2 - int(floor(log10(abs(num_treeC)))))
    except Exception as e:
        r_num_treeC = num_treeC
    data["r_num_treeC"] = r_num_treeC

    return data


@shared_task(bind=True)
def add_benin_commune(self, qars):
    """
    Adding the shapefiles with popups for the Benin Republic communes
    Add benin republic communes data to the parent layer
    """
    class DataObject:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    benin_commune_layer = folium.FeatureGroup(name=gettext('Benin Communes'), show=False, overlay=False)
    temp_geojson2 = folium.GeoJson(data=benin_adm2_json,
                                   name='Benin-Adm2 Communes',
                                   highlight_function=__highlight_function__)

    for feature in temp_geojson2.data['features']:
        temp_layer2 = folium.GeoJson(feature, zoom_on_click=False, highlight_function=__highlight_function__)

        data = __build_data__(feature, qars)

        # html template for the popups
        html3 = __build_html_view__(DataObject(**data))

        iframe = folium.IFrame(html=html3, width=450, height=380)

        folium.Popup(iframe, max_width=2000).add_to(temp_layer2)

        # consolidate individual features back into the main layer
        folium.GeoJsonTooltip(fields=["NAME_2"],
                              aliases=["Commune:"],
                              labels=True,
                              sticky=False,
                              style=(
                                  "background-color: white; color: black;"
                                  " font-family: sans-serif; font-size: 12px; padding: 4px;")
                              ).add_to(temp_layer2)

        temp_layer2.add_to(benin_commune_layer)

    return benin_commune_layer
