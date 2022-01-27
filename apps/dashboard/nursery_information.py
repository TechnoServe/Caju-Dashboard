import folium
from django.utils.translation import gettext

from apps.dashboard.models import Nursery


class NurseryLayer:
    def __init__(self, marker_cluster):
        self.marker_cluster = marker_cluster

    def add_nursery(self):
        # variables for translation
        Commune_Name = gettext('Commune Name')
        Nursery_Owner = gettext("Nursery Owner")
        Nursery_Area = gettext("Nursery Area (ha)")
        Number_of_Plants = gettext("Number of Plants")

        # Loop through every nursery owner and add to the nursery marker popups
        nurseries = Nursery.objects.all()
        for i in range(len(nurseries)):
            current_object = nurseries[i]
            folium.Marker(location=[current_object.latitude, current_object.longitude],
                          rise_on_hover=True,
                          rise_offset=250,
                          icon=folium.Icon(color="red", icon="leaf"),
                          popup=f'''
                                <div style="border: 3px solid #808080">
                                <h4 style="font-family: 'Trebuchet MS', sans-serif">{Commune_Name}: <b>{current_object.commune}</b></h4>
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">{Nursery_Owner}: <i>{current_object.nursery_name}</i></h5>
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">{Nursery_Area}: <b>{current_object.current_area}</b></h5>
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">{Number_of_Plants}: <b>{current_object.number_of_plants}</b></h5>
                                <a href="https://www.technoserve.org/our-work/agriculture/cashew/?_ga=2.159985149.1109250972.1626437600-1387218312.1616379774"target="_blank">click link to website</a>
                                <img src="https://gumlet.assettype.com/deshdoot/import/2019/12/tripXOXO-e1558439144643.jpg?w=1200&h=750&auto=format%2Ccompress&fit=max" width="200" height="70">
                                </div>''').add_to(self.marker_cluster)

        return self.marker_cluster
