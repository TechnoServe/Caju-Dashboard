from math import log10, floor

import folium
import geojson
from area import area
from celery import shared_task
from django.db.models import Sum, Avg
from django.utils.translation import gettext

from apps.dashboard.models import BeninYield
from apps.dashboard.models import CommuneSatellite
from apps.dashboard.models import Qar

heroku = False

# Load the Benin Communes shapefile
with open("staticfiles/json/ben_adm2.json", errors="ignore") as f:
    benin_adm2_json = geojson.load(f)


def highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}


def get_average_kor(commune):
    _all = Qar.objects.all().filter(commune=commune)
    total = 0
    count = _all.count()
    # print(commune, ': ', count)
    if count == 0:
        count = 1
    for i, x in enumerate(_all):
        total += x.kor
    return total / count


@shared_task(bind=True)
def add_benin_commune(self):
    benin_commune_layer = folium.FeatureGroup(name=gettext('Benin Communes'), show=False, overlay=False)
    temp_geojson2 = folium.GeoJson(data=benin_adm2_json,
                                   name='Benin-Adm2 Communes',
                                   highlight_function=highlight_function)

    # Commune translation variable
    Departments_Cashew_Tree = gettext('Departments Cashew Tree Cover Statistics In')
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
    among_Benin_communes = gettext(
        "among Benin communes in terms of total cashew yield according to the TNS Yield Survey")

    for feature in temp_geojson2.data['features']:
        # GEOJSON layer consisting of a single feature
        name = feature["properties"]["NAME_2"]

        # looping through all communes in Benin Repubic to get the ranking
        z_list = []
        for c in range(len(CommuneSatellite.objects.all())):
            y = CommuneSatellite.objects.all()[c].commune
            x = CommuneSatellite.objects.filter(commune=y).aggregate(Sum('cashew_tree_cover'))
            x = x['cashew_tree_cover__sum']
            z_list.append((y, x))

        sorted_by_second = sorted(z_list, reverse=True, key=lambda tup: tup[1])
        list2, _ = zip(*sorted_by_second)

        # A small logic to solve the french symbols name error when viewed on local host
        if heroku:
            position2 = list2.index(name)
        else:
            position2 = 1

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

        temp_layer2 = folium.GeoJson(feature, zoom_on_click=True, highlight_function=highlight_function)

        # load statistics from the database and formating them for displaying on popups

        tree_ha_pred_comm = CommuneSatellite.objects.filter(commune=name).aggregate(Sum('cashew_tree_cover'))
        try:
            tree_ha_pred_comm = int(round(tree_ha_pred_comm['cashew_tree_cover__sum'] / 10000, 2))
        except Exception as e:
            tree_ha_pred_comm = 0

        try:
            yield_pred_comm = int(390 * tree_ha_pred_comm)
        except Exception as e:
            yield_pred_comm = 0

        surface_areaC = BeninYield.objects.filter(commune=name).aggregate(Sum('surface_area'))
        try:
            surface_areaC = int(round(surface_areaC['surface_area__sum'], 2))
        except Exception as e:
            surface_areaC = 0

        total_yieldC = BeninYield.objects.filter(commune=name).aggregate(Sum('total_yield_kg'))
        try:
            total_yieldC = int(round(total_yieldC['total_yield_kg__sum'], 2))
        except Exception as e:
            total_yieldC = 0

        yield_haC = BeninYield.objects.filter(commune=name).aggregate(Avg('total_yield_per_ha_kg'))
        try:
            yield_haC = int(round(yield_haC['total_yield_per_ha_kg__avg'], 2))
        except Exception as e:
            yield_haC = 0

        # Used only in case of error in the try and except catch
        yield_treeC = BeninYield.objects.filter(commune=name).aggregate(Avg('total_yield_per_tree_kg'))
        try:
            yield_treeC = int(round(yield_treeC['total_yield_per_tree_kg__avg'], 2))
        except Exception as e:
            yield_treeC = 0

        num_treeC = BeninYield.objects.filter(commune=name).aggregate(Sum('total_number_trees'))
        try:
            num_treeC = int(num_treeC['total_number_trees__sum'])
        except Exception as e:
            num_treeC = 0

        sick_treeC = BeninYield.objects.filter(commune=name).aggregate(Sum('total_sick_trees'))
        try:
            sick_treeC = int(sick_treeC['total_sick_trees__sum'])
        except Exception as e:
            sick_treeC = 0

        out_prod_treeC = BeninYield.objects.filter(commune=name).aggregate(Sum('total_trees_out_of_prod'))
        try:
            out_prod_treeC = int(out_prod_treeC['total_trees_out_of_prod__sum'])
        except Exception as e:
            out_prod_treeC = 0

        dead_treeC = BeninYield.objects.filter(commune=name).aggregate(Sum('total_dead_trees'))
        try:
            dead_treeC = int(round(dead_treeC['total_dead_trees__sum'], 2))
        except Exception as e:
            dead_treeC = 0

        region_sizeC = area(feature['geometry']) / 10000
        try:
            active_treesC = num_treeC - sick_treeC - out_prod_treeC - dead_treeC
        except Exception as e:
            active_treesC = 0

            # formating numbers greater than 90000 to show 91k

        try:
            r_region_sizeC = round(region_sizeC, 1 - int(floor(log10(abs(region_sizeC))))) \
                if region_sizeC < 90000 \
                else round(region_sizeC, 2 - int(floor(log10(abs(region_sizeC)))))
        except Exception as e:
            r_region_sizeC = region_sizeC

        try:
            r_tree_ha_pred_comm = round(tree_ha_pred_comm, 1 - int(
                floor(log10(abs(tree_ha_pred_comm)))))\
                if tree_ha_pred_comm < 90000 \
                else round(tree_ha_pred_comm, 2 - int(floor(log10(abs(tree_ha_pred_comm)))))
        except Exception as e:
            r_tree_ha_pred_comm = tree_ha_pred_comm
        try:
            r_yield_pred_comm = round(yield_pred_comm, 1 - int(
                floor(log10(abs(yield_pred_comm))))) \
                if yield_pred_comm < 90000 \
                else round(yield_pred_comm, 2 - int(floor(log10(abs(yield_pred_comm)))))
        except Exception as e:
            r_yield_pred_comm = yield_pred_comm
        try:
            r_surface_areaC = round(surface_areaC, 1 - int(floor(log10(abs(surface_areaC))))) \
                if surface_areaC < 90000 \
                else round(surface_areaC, 2 - int(floor(log10(abs(surface_areaC)))))
        except Exception as e:
            r_surface_areaC = surface_areaC
        try:
            r_total_yieldC = round(total_yieldC, 1 - int(floor(log10(abs(total_yieldC))))) \
                if total_yieldC < 90000 \
                else round(total_yieldC, 2 - int(floor(log10(abs(total_yieldC)))))
        except Exception as e:
            r_total_yieldC = total_yieldC
        try:
            r_yield_haC = round(yield_haC, 1 - int(floor(log10(abs(yield_haC))))) \
                if yield_haC < 90000 \
                else round(yield_haC, 2 - int(floor(log10(abs(yield_haC)))))
        except Exception as e:
            r_yield_haC = yield_haC

        # try: r_yield_treeC = round(yield_treeC, 1-int(floor(log10(abs(yield_treeC))))) if yield_treeC < 90000 else
        # round(yield_treeC, 2-int(floor(log10(abs(yield_treeC))))) except Exception as e: r_yield_treeC = yield_treeC

        try:
            r_yield_treeC = round(r_total_yieldC / active_treesC)
        except Exception as e:
            r_yield_treeC = yield_treeC

        try:
            r_num_treeC = round(num_treeC, 1 - int(floor(log10(abs(num_treeC))))) \
                if num_treeC < 90000 \
                else round(num_treeC, 2 - int(floor(log10(abs(num_treeC)))))
        except Exception as e:
            r_num_treeC = num_treeC

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

                            var data_donut = google.visualization.arrayToDataTable([
                            ['Tree Type', 'Number of Trees'],
                            ['Active Trees',      {active_treesC}],
                            ['Sick Trees',      {sick_treeC}],
                            ['Dead Trees',     {dead_treeC}],
                            ['Out of Production Trees',      {out_prod_treeC}],
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
                        <h4>In 2020, {name} {is_ranked} <b>{my_dict_communes[str(position2 + 1)]}</b> {among_Benin_communes}.</h4>
                        <table>
                        <tr>
                            <th></th>
                            <th>{Satellite_Est}</th>
                            <th>{TNS_Survey}</th>
                            
                        </tr>
                        <tr>
                            <td>{Total_Cashew_Yield}</td>
                            <td>{r_yield_pred_comm / 1000000:n}M</td>
                            <td>{r_total_yieldC / 1000000:n}M</td>
                            
                        </tr>
                        <tr>
                            <td>{Total_Area}</td>
                            <td>{r_region_sizeC / 1000:n}K</td>
                            <td>{r_surface_areaC / 1000:n}K</td>
                        </tr>
                        <tr>
                            <td>{Cashew_Tree_Cover}</td>
                            <td>{r_tree_ha_pred_comm / 1000:n}K</td>
                            <td>NA</td>
                            
                        </tr>
                        <tr>
                            <td>{Yield_Hectare}</td>
                            <td>390</td>
                            <td>{r_yield_haC}</td>
                        
                        </tr>
                        <tr>
                            <td>{Yield_per_Tree}</td>
                            <td>NA</td>
                            <td>{r_yield_treeC}</td>
                        
                        </tr>
                        <tr>
                            <td>{Number_of_Trees}</td>
                            <td>NA</td>
                            <td>{r_num_treeC / 1000:n}K</td>                            
                        </tr>
                        <tr>
                            <td>{Qar_average}</td>
                            <td>NA</td>
                            <td>{get_average_kor(name):n}</td>                        
                        </tr>
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
