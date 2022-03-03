import folium
from django.utils.translation import gettext


def __build_popup__(current_object):
    # variables for translation
    qar_region = gettext('Region')
    qar_site = gettext("Site")
    qar_kor = gettext("KOR")
    qar_nut_count = gettext("Nut Count")
    qar_defective_rate = gettext("Defective Rate")

    return f'''
            <div style="">
            <h4 style="font-family: 'Trebuchet MS', sans-serif">
                {qar_region}: <b>{current_object.department}</b>
            </h4> 
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {qar_site}: <i>{current_object.site}</i>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {qar_kor}: <b>{current_object.kor}</b>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {qar_nut_count}: <b>{current_object.nut_count}</b>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {qar_defective_rate}: <b>{current_object.defective_rate}</b>
            </h5>
            <a href="https://www.technoserve.org/our-work/agriculture/cashew/?_ga=2.159985149.1109250972.1626437600-1387218312.1616379774"target="_blank">click link to website</a>
            <img src="https://images.squarespace-cdn.com/content/v1/5e1197fe8aa5803c29b6b711/1580400113932-60TBXUG8S0NEZ8R4CQ1Y/08.jpg" width="200" height="133">
            </div>
        '''


class QarLayer:
    def __init__(self, marker_cluster, qars, base_url):
        self.base_url = base_url
        self.qars = qars
        self.marker_cluster = marker_cluster

    def add_qar(self):
        # Loop through every nursery owner and add to the nursery marker popups
        iconprefix = 'fa'
        iconname = 'f494'
        iconcolor = 'white'
        markercolor = "blue"
        iconurl = self.base_url + '/apps/static/assets/img/warehouse_icon.png'
        iconurl = "https://cdn.mapmarker.io/api/v1/font-awesome/v5/pin?icon=fa-warehouse&size=50&hoffset=0&voffset=-1&background=1167b1"
        for i in range(len(self.qars)):
            current_object = self.qars[i]
            # icon = folium.Icon(
            #     color=markercolor,
            #     icon=iconname,
            #     icon_color=iconcolor,
            #     prefix=iconprefix,
            # )
            icon = folium.features.CustomIcon(
                iconurl,
                icon_size=(45, 45),
            )
            folium.Marker(
                location=[current_object.latitude, current_object.longitude],
                rise_on_hover=True,
                rise_offset=500,
                icon=icon,
                popup=__build_popup__(current_object),
            ).add_to(self.marker_cluster)

        return self.marker_cluster
