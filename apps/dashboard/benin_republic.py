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
from apps.dashboard.models import Qar

with open("staticfiles/json/ben_adm0.json", errors="ignore") as f:
    benin_adm0_json = geojson.load(f)


def highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def get_average_kor():
    total = 0
    count = Qar.objects.all().count()
    if count == 0:
        count = 1
    for i, x in enumerate(Qar.objects.all()):
        total += x.kor
    return total / count


@shared_task(bind=True)
def add_benin_republic(self):
    benin_layer = folium.FeatureGroup(name=gettext('Benin Republic'), show=False, overlay=False)
    temp_geojson0 = folium.GeoJson(data=benin_adm0_json,
                                   name='Benin-Adm0 Department',
                                   highlight_function=highlight_function)

    # Variables for translation
    Departments_Cashew_Tree = gettext('Departments Cashew Tree Cover Statistics In')
    Active_Trees = gettext("Active Trees")
    Sick_Trees = gettext("Sick Trees")
    Dead_Trees = gettext("Dead Trees")
    Out_of_Production = gettext("Out of Production Trees")
    Cashew_Trees_Status = gettext("Cashew Trees Status in")
    is_ranked = gettext("is ranked")
    globally_in_terms = gettext("globally in terms of total cashew yield")
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
    nine_9 = gettext('9th')
    Source_TNS = gettext("Source: TNS/BeninCaju Yield Surveys 2020")

    for feature in temp_geojson0.data['features']:

        pred_ben_data = []
        pred_ground_ben_data = [['Departments', 'Satellite Prediction', 'Ground Data Estimate']]
        for d in range(len(DeptSatellite.objects.all())):
            y = DeptSatellite.objects.all()[d].department
            x = CommuneSatellite.objects.filter(department=y).aggregate(Sum('cashew_tree_cover'))
            x = round(x['cashew_tree_cover__sum'] / 10000, 2)
            pred_ben_data.append([y, x])
            pred_ground_ben_data.append([y, x, x])

        temp_layer0 = folium.GeoJson(feature, zoom_on_click=True, highlight_function=highlight_function)

        name = gettext('Benin Republic')
        surface_area = BeninYield.objects.all().aggregate(Sum('surface_area'))
        surface_area = int(round(surface_area['surface_area__sum'], 2))

        total_yield = BeninYield.objects.all().aggregate(Sum('total_yield_kg'))
        total_yield = int(round(total_yield['total_yield_kg__sum'], 2))

        yield_ha = BeninYield.objects.all().aggregate(Avg('total_yield_per_ha_kg'))
        yield_ha = int(round(yield_ha['total_yield_per_ha_kg__avg'], 2))

        num_tree = BeninYield.objects.all().aggregate(Sum('total_number_trees'))
        num_tree = int(num_tree['total_number_trees__sum'])

        sick_tree = BeninYield.objects.all().aggregate(Sum('total_sick_trees'))
        sick_tree = int(sick_tree['total_sick_trees__sum'])

        out_prod_tree = BeninYield.objects.all().aggregate(Sum('total_trees_out_of_prod'))
        out_prod_tree = int(out_prod_tree['total_trees_out_of_prod__sum'])

        dead_tree = BeninYield.objects.all().aggregate(Sum('total_dead_trees'))
        dead_tree = int(round(dead_tree['total_dead_trees__sum'], 2))

        tree_ha_pred = CommuneSatellite.objects.all().aggregate(Sum('cashew_tree_cover'))
        tree_ha_pred = int(round(tree_ha_pred['cashew_tree_cover__sum'] / 10000, 2))

        yield_pred = 390 * tree_ha_pred

        region_size = area(feature['geometry']) / 10000
        active_trees = num_tree - sick_tree - out_prod_tree - dead_tree

        r_surface_area = round(surface_area,
                               1 - int(floor(log10(abs(surface_area))))) if surface_area < 90000 else round(
            surface_area, 2 - int(floor(log10(abs(surface_area)))))
        r_total_yield = round(total_yield, 1 - int(floor(log10(abs(total_yield))))) if total_yield < 90000 else round(
            total_yield, 2 - int(floor(log10(abs(total_yield)))))
        r_yield_ha = round(yield_ha, 1 - int(floor(log10(abs(yield_ha))))) if yield_ha < 90000 else round(yield_ha,
                                                                                                          2 - int(floor(
                                                                                                              log10(
                                                                                                                  abs(yield_ha)))))
        r_tree_ha_pred = round(tree_ha_pred,
                               1 - int(floor(log10(abs(tree_ha_pred))))) if tree_ha_pred < 90000 else round(
            tree_ha_pred, 2 - int(floor(log10(abs(tree_ha_pred)))))
        r_yield_pred = round(yield_pred, 1 - int(floor(log10(abs(yield_pred))))) if yield_pred < 90000 else round(
            yield_pred, 2 - int(floor(log10(abs(yield_pred)))))
        r_num_tree = round(num_tree, 1 - int(floor(log10(abs(num_tree))))) if num_tree < 90000 else round(num_tree,
                                                                                                          2 - int(floor(
                                                                                                              log10(
                                                                                                                  abs(num_tree)))))
        r_region_size = round(region_size, 1 - int(floor(log10(abs(region_size))))) if region_size < 90000 else round(
            region_size, 2 - int(floor(log10(abs(region_size)))))
        r_yield_tree = round(r_total_yield / active_trees)

        html4 = f'''
                <html>
                    <head>
                        <style>
                        table {{
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
                            pie_data.addColumn('number', 'Cashew Tree Cover (ha)');
                            pie_data.addRows({pred_ben_data});

                            var piechart_options = {{title:'{Departments_Cashew_Tree} {name}',
                                                        is3D: true,
                                                    }};
                            var piechart = new google.visualization.PieChart(document.getElementById('piechart_div'));
                            piechart.draw(pie_data, piechart_options);

                            


                            var data_donut = google.visualization.arrayToDataTable([
                            ['Tree Type', 'Number of Trees'],
                            ["Active Trees",      {active_trees}],
                            ["Sick Trees",      {sick_tree}],
                            ["Dead Trees",     {dead_tree}],
                            ["Out of Production Trees",      {out_prod_tree}],
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
                        <h4>{name} {is_ranked} <b>{nine_9}</b> {globally_in_terms}.</h4>
                        <table>
                        <tr>
                            <th></th>
                            <th>{Satellite_Est}</th>
                            <th>{TNS_Survey}</th>
                        </tr>
                        <tr>
                            <td>{Total_Cashew_Yield}</td>
                            <td>{r_yield_pred / 1000000:n}M</td>
                            <td>{r_total_yield / 1000000:n}M</td>
                            
                        </tr>
                        <tr>
                            <td>{Total_Area}</td>
                            <td>{r_region_size / 1000000:n}M</td>
                            <td>{r_surface_area / 1000:n}K</td>
                        </tr>
                        <tr>
                            <td>{Cashew_Tree_Cover}</td>
                            <td>{r_tree_ha_pred / 1000:n}K</td>
                            <td>NA</td>
                            
                        </tr>
                        <tr>
                            <td>{Yield_Hectare}</td>
                            <td>390</td>
                            <td>{r_yield_ha}</td>
                            
                        </tr>
                        <tr>
                            <td>{Yield_per_Tree}</td>
                            <td>NA</td>
                            <td>{r_yield_tree}</td>
                            
                        </tr>
                        <tr>
                            <td>{Number_of_Trees}</td>
                            <td>NA</td>
                            <td>{r_num_tree / 1000:n}K</td>
                            
                        </tr>
                        <tr>
                            <td>{Qar_average}</td>
                            <td>NA</td>
                            <td>{get_average_kor():n}</td>                        
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
                    </html>'''

        iframe = folium.IFrame(html=html4, width=450, height=380)

        folium.Popup(iframe, max_width=2000).add_to(temp_layer0)
        temp_layer0.add_to(benin_layer)

    return benin_layer
