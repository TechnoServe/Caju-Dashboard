import folium
from django.utils.translation import gettext


def __build_popup__(current_object):
    # variables for translation
    training_region = gettext('Department')
    training_commune = gettext('Commune')
    trainer = gettext("Trainer")
    trainer_org = gettext("Organization")
    module_title = gettext("Topic")
    module_category = gettext("Category")
    participants = gettext("Number of Participants")
    time = gettext("Training DateTime")

    return f'''
            <div style="">
            <h4 style="font-family: 'Trebuchet MS', sans-serif">
                {training_region}: <b>{current_object.department}</b>
            </h4> 
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {training_commune}: <b>{current_object.commune}</b>
            </h5> 
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {trainer}: <i>{current_object.trainer['firstname'] + " " + current_object.trainer['lastname']}</i>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {trainer_org}: <i>{current_object.trainer['institution']}</i>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {module_title}: <i>{current_object.module["title"]}</i>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {module_category}: <i>{current_object.module['category']}</i>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {participants}: <i>{current_object.number_of_participant}</i>
            </h5>
            <h5 style="font-family: 'Trebuchet MS', sans-serif">
                {time}: <i>{current_object.datetime}</i>
            </h5>
            <img src="https://www.tnsbenin.org/uploads/1/0/9/8/109816790/p-pi_orig.png" width="200" height="133">
            </div>
        '''


class TrainingLayer:
    def __init__(self, marker_cluster, trainings):
        self.trainings = trainings
        self.marker_cluster = marker_cluster

    def add_training(self):
        # Loop through every nursery owner and add to the nursery marker popups
        iconurl = "https://cdn.mapmarker.io/api/v1/font-awesome/v5/pin?icon=fa-warehouse&size=50&hoffset=0&voffset=-1" \
                  "&background=DBA800"
        for i in range(len(self.trainings)):
            current_object = self.trainings[i]
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
