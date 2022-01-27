import folium
from django.utils.translation import gettext

from apps.dashboard.models import Qar


class QarLayer:
    def __init__(self, marker_cluster):
        self.marker_cluster = marker_cluster

    def add_qar(self):
        # variables for translation
        Qar_Region = gettext('Region')
        Qar_Site = gettext("Site")
        Qar_KOR = gettext("KOR")

        # Loop through every nursery owner and add to the nursery marker popups
        qars = Qar.objects.all()
        for i in range(len(qars)):
            current_object = qars[i]
            folium.Marker(location=[current_object.latitude, current_object.longitude],
                          rise_on_hover=True,
                          rise_offset=250,
                          icon=folium.Icon(color="blue", icon="leaf"),
                          popup=f'''
                                <div style="border: 3px solid #808080">
                                <h4 style="font-family: 'Trebuchet MS', sans-serif">
                                    {Qar_Region}: <b>{current_object.department}</b>
                                </h4> 
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">
                                    {Qar_Site}: <i>{current_object.site}</i>
                                </h5>
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">
                                    {Qar_KOR}: <b>{current_object.kor}</b>
                                </h5>
                                <a href="https://www.technoserve.org/our-work/agriculture/cashew/?_ga=2.159985149.1109250972.1626437600-1387218312.1616379774"target="_blank">click link to website</a>
                                <img src="https://gumlet.assettype.com/deshdoot/import/2019/12/tripXOXO-e1558439144643.jpg?w=1200&h=750&auto=format%2Ccompress&fit=max" width="200" height="70">
                                </div>''').add_to(self.marker_cluster)

        return self.marker_cluster
