from math import log10, floor

import folium
import geojson
from area import area
from celery import shared_task
from django.db.models import Sum, Avg
from django.utils.translation import gettext

from apps.dashboard.models import BeninYield
from apps.dashboard.models import CommuneSatellite
from apps.dashboard.models import DeptSatellite

heroku = False

# Load the Benin Departments shapefile
with open("staticfiles/json/ben_adm1.json", errors="ignore") as f:
    benin_adm1_json = geojson.load(f)


def highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def get_average_kor(Qars, department):
    _all = list(filter(lambda c: c.department == department, Qars))
    total = 0
    count = len(_all)
    if count == 0:
        count = 1
    for i, x in enumerate(_all):
        total += x.kor
    result = total / count
    return "{:.2f}".format(result) if result != 0 else "NA"


@shared_task(bind=True)
def add_benin_department(self, Qars):
    benin_dept_layer = folium.FeatureGroup(name=gettext('Benin Departments'), show=False, overlay=False)
    temp_geojson = folium.GeoJson(data=benin_adm1_json,
                                  name='Benin-Adm1 Department',
                                  highlight_function=highlight_function)

    dept_yieldHa = {}

    # Variables for departmental translation

    Active_Trees = gettext("Active Trees")
    Sick_Trees = gettext("Sick Trees")
    Dead_Trees = gettext("Dead Trees")
    Out_of_Production = gettext("Out of Production Trees")
    Cashew_Trees_Status = gettext("Cashew Trees Status in")
    is_ranked = gettext("is ranked")

    Satellite_Est = gettext("Satellite Est")
    TNS_Survey = gettext("TNS Survey")

    # All 3 shapefiles share these variables
    Total_Cashew_Yield = gettext("Total Cashew Yield (kg)")
    Total_Area = gettext("Total Area (ha)")
    Cashew_Tree_Cover = gettext("Cashew Tree Cover (ha)")
    Yield_Hectare = gettext("Yield/Hectare (kg/ha)")
    Yield_per_Tree = gettext("Yield per Tree (kg/tree)")
    Number_of_Trees = gettext("Number of Trees")
    Qar_average = gettext("KOR Average")
    Source_TNS = gettext("Source: TNS/BeninCaju Yield Surveys 2020")
    Predicted_Cashew_TreeD = gettext("Predicted Cashew Tree Cover Communes Statistics In")
    among_Benin_departments = gettext(
        "among Benin departments in terms of total cashew yield according to the TNS Yield Survey")

    for feature in temp_geojson.data['features']:
        # GEOJSON layer consisting of a single feature
        name = feature["properties"]["NAME_1"]

        z_list = []
        # looping through all departments in Benin Repubic to get the ranking

        for d in range(len(DeptSatellite.objects.all())):
            y = DeptSatellite.objects.all()[d].department
            x = CommuneSatellite.objects.filter(department=y).aggregate(Sum('cashew_tree_cover'))
            x = x['cashew_tree_cover__sum']
            z_list.append((y, x))

        sorted_by_second = sorted(z_list, reverse=True, key=lambda tup: tup[1])
        list1, _ = zip(*sorted_by_second)

        # A small logic to solve the french symbols name error when viewed on local host
        if heroku:
            position = list1.index(name)
        else:
            position = 1
        my_dict = {'0': "highest", '1': "2nd", '2': "3rd", '3': "4th", '4': "5th", '5': "6th", '6': "7th", '7': "8th",
                   '8': "9th", '9': "10th", '10': "11th", '11': "lowest"}

        pred_dept_data = []
        pred_ground_dept_data = [['Communes', 'Satellite Prediction', 'Ground Data Estimate']]
        for c in CommuneSatellite.objects.filter(department=name):
            y = c.commune
            x = round(c.cashew_tree_cover / 10000, 2)
            pred_dept_data.append([y, x])
            pred_ground_dept_data.append([y, x, x])

        temp_layer1 = folium.GeoJson(feature, zoom_on_click=True, highlight_function=highlight_function)

        # load statistics from the database and formating them for displaying on popups.
        # The try catch is to avoid error that arise when we round null values

        tree_ha_pred_dept = CommuneSatellite.objects.filter(department=name).aggregate(Sum('cashew_tree_cover'))
        try:
            tree_ha_pred_dept = int(round(tree_ha_pred_dept['cashew_tree_cover__sum'] / 10000, 2))
        except Exception as e:
            tree_ha_pred_dept = 0

        try:
            yield_pred_dept = int(390 * tree_ha_pred_dept)
        except Exception as e:
            yield_pred_dept = 0

        surface_areaD = BeninYield.objects.filter(department=name).aggregate(Sum('surface_area'))
        try:
            surface_areaD = int(round(surface_areaD['surface_area__sum'], 2))
        except Exception as e:
            surface_areaD = 0

        total_yieldD = BeninYield.objects.filter(department=name).aggregate(Sum('total_yield_kg'))
        try:
            total_yieldD = int(round(total_yieldD['total_yield_kg__sum'], 2))
        except Exception as e:
            total_yieldD = 0

        yield_haD = BeninYield.objects.filter(department=name).aggregate(Avg('total_yield_per_ha_kg'))
        try:
            yield_haD = int(round(yield_haD['total_yield_per_ha_kg__avg'], 2))
        except Exception as e:
            yield_haD = 0

        # Used only in case of error in the try and except catch
        yield_treeD = BeninYield.objects.filter(department=name).aggregate(Avg('total_yield_per_tree_kg'))
        try:
            yield_treeD = int(round(yield_treeD['total_yield_per_tree_kg__avg'], 2))
        except Exception as e:
            yield_treeD = 0

        num_treeD = BeninYield.objects.filter(department=name).aggregate(Sum('total_number_trees'))
        try:
            num_treeD = int(num_treeD['total_number_trees__sum'])
        except Exception as e:
            num_treeD = 0

        sick_treeD = BeninYield.objects.filter(department=name).aggregate(Sum('total_sick_trees'))
        try:
            sick_treeD = int(sick_treeD['total_sick_trees__sum'])
        except Exception as e:
            sick_treeD = 0

        out_prod_treeD = BeninYield.objects.filter(department=name).aggregate(Sum('total_trees_out_of_prod'))
        try:
            out_prod_treeD = int(out_prod_treeD['total_trees_out_of_prod__sum'])
        except Exception as e:
            out_prod_treeD = 0

        dead_treeD = BeninYield.objects.filter(department=name).aggregate(Sum('total_dead_trees'))
        try:
            dead_treeD = int(round(dead_treeD['total_dead_trees__sum'], 2))
        except Exception as e:
            dead_treeD = 0

        region_sizeD = area(feature['geometry']) / 10000
        try:
            active_treesD = num_treeD - sick_treeD - out_prod_treeD - dead_treeD
        except Exception as e:
            active_treesD = 0

        try:
            r_tree_ha_pred_dept = round(tree_ha_pred_dept, 1 - int(
                floor(log10(abs(tree_ha_pred_dept))))) if tree_ha_pred_dept < 90000 else round(tree_ha_pred_dept,
                                                                                               2 - int(floor(log10(
                                                                                                   abs(tree_ha_pred_dept)))))
        except Exception as e:
            r_tree_ha_pred_dept = tree_ha_pred_dept
        try:
            r_yield_pred_dept = round(yield_pred_dept, 1 - int(
                floor(log10(abs(yield_pred_dept))))) if yield_pred_dept < 90000 else round(yield_pred_dept, 2 - int(
                floor(log10(abs(yield_pred_dept)))))
        except Exception as e:
            r_yield_pred_dept = yield_pred_dept
        try:
            r_surface_areaD = round(surface_areaD,
                                    1 - int(floor(log10(abs(surface_areaD))))) if surface_areaD < 90000 else round(
                surface_areaD, 2 - int(floor(log10(abs(surface_areaD)))))
        except Exception as e:
            r_surface_areaD = surface_areaD
        try:
            r_total_yieldD = round(total_yieldD,
                                   1 - int(floor(log10(abs(total_yieldD))))) if total_yieldD < 90000 else round(
                total_yieldD, 2 - int(floor(log10(abs(total_yieldD)))))
        except Exception as e:
            r_total_yieldD = total_yieldD
        try:
            r_yield_haD = round(yield_haD, 1 - int(floor(log10(abs(yield_haD))))) if yield_haD < 90000 else round(
                yield_haD, 2 - int(floor(log10(abs(yield_haD)))))
        except Exception as e:
            r_yield_haD = yield_haD

        try:
            r_yield_treeD = round(r_total_yieldD / active_treesD)
        except Exception as e:
            r_yield_treeD = yield_treeD
        try:
            r_num_treeD = round(num_treeD, 1 - int(floor(log10(abs(num_treeD))))) if num_treeD < 90000 else round(
                num_treeD, 2 - int(floor(log10(abs(num_treeD)))))
        except Exception as e:
            r_num_treeD = num_treeD

        try:
            r_region_sizeD = round(region_sizeD,
                                   1 - int(floor(log10(abs(region_sizeD))))) if region_sizeD < 90000 else round(
                region_sizeD, 2 - int(floor(log10(abs(region_sizeD)))))
        except Exception as e:
            r_region_sizeD = region_sizeD

        dept_yieldHa[name] = yield_haD

        # html template for the popups
        html3 = f'''
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
                            pie_data.addRows({pred_dept_data});

                            var piechart_options = {{title:'{Predicted_Cashew_TreeD} {name}',
                                                        is3D: true,
                                                    }};
                            var piechart = new google.visualization.PieChart(document.getElementById('piechart_div'));
                            piechart.draw(pie_data, piechart_options);

                            

                            var data_donut = google.visualization.arrayToDataTable([
                            ['Tree Type', 'Number of Trees'],
                            ['Active Trees',      {active_treesD}],
                            ['Sick Trees',      {sick_treeD}],
                            ['Dead Trees',     {dead_treeD}],
                            ['Out of Production Trees',      {out_prod_treeD}],
                            ]);

                            var options_donut = {{
                            title: '{Cashew_Trees_Status} {name}',
                            pieHole: 0.5,
                            colors: ['007f00', '#02a8b1', '9e1a1a', '#242526'],
                            }};

                            var chart_donut = new google.visualization.PieChart(document.getElementById('donutchart'));
                            chart_donut.draw(data_donut, options_donut);

                            }};
                        </script>
                    </head>
                    <body>
                        <h2>{name}</h2>
                        <h4>In 2020, {name} {is_ranked} <b>{my_dict[str(position)]}</b> {among_Benin_departments}.</h4>
                        <table>
                        <tr>
                            <th></th>
                            <th>{Satellite_Est}</th>
                            <th>{TNS_Survey}</th>
                            
                        </tr>
                        <tr>
                            <td>{Total_Cashew_Yield}</td>
                            <td>{r_yield_pred_dept / 1000000:n}M</td>
                            <td>{r_total_yieldD / 1000000:n}M</td>
                            
                        </tr>
                        <tr>
                            <td>{Total_Area}</td>
                            <td>{r_region_sizeD / 1000000:n}M</td>
                            <td>{r_surface_areaD / 1000:n}K</td>
                        </tr>
                        <tr>
                            <td>{Cashew_Tree_Cover}</td>
                            <td>{r_tree_ha_pred_dept / 1000:n}K</td>
                            <td>NA</td>
                            
                        </tr>
                        <tr>
                            <td>{Yield_Hectare}</td>
                            <td>390</td>
                            <td>{r_yield_haD}</td>
                            
                        </tr>
                        <tr>
                            <td>{Yield_per_Tree}</td>
                            <td>NA</td>
                            <td>{r_yield_treeD}</td>
                            
                        </tr>
                        <tr>
                            <td>{Number_of_Trees}</td>
                            <td>NA</td>
                            <td>{r_num_treeD / 1000:n}K</td>
                        </tr>
                        <tr>
                            <td>{Qar_average}</td>
                            <td>NA</td>
                            <td>{get_average_kor(Qars, name)}</td>                        
                        </tr>
                        </table>
                        
                        <table>
                            <td><div id="piechart_div" style="width: 400; height: 350;border: 3px solid #00a5a7"></div></td>
                        </table>                           
                        <table>
                            <td><div id="donutchart" style="width: 400; height: 350;border: 3px solid #00a5a7"></div></td>
                        </table>
                        <table>
                            <td><div style= "text-align: center"><h5>{Source_TNS}</h5></div>
                        </table> 
                    </body>
                    </html>
                '''
        # Popup size and frame declaration
        iframe = folium.IFrame(html=html3, width=450, height=380)

        folium.Popup(iframe, max_width=2000).add_to(temp_layer1)

        # consolidate individual features back into the main layer
        folium.GeoJsonTooltip(fields=["NAME_1"],
                              aliases=["Department:"],
                              labels=True,
                              sticky=False,
                              style=(
                                  "background-color: white; color: black; font-family: sans-serif; font-size: 12px; padding: 4px;")
                              ).add_to(temp_layer1)

        temp_layer1.add_to(benin_dept_layer)

    return benin_dept_layer, dept_yieldHa
