import os
import sys

import django
import geojson
import pymysql
from django.core.exceptions import FieldDoesNotExist
from shapely.geometry import shape, Point

BASE_DIR = os.path.dirname(os.path.realpath(__name__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cajulab_remote_sensing_dashboard.settings")
django.setup()

from apps.dashboard import models

with open("staticfiles/json/ben_adm1.json", encoding="utf8", errors="ignore") as f:
    departments_geojson = geojson.load(f)

with open("staticfiles/json/ben_adm2.json", encoding="utf8", errors="ignore") as f:
    communes_geojson = geojson.load(f)

training_dep_comm_objects = []
for obj in models.Training.objects.all():
    training_dep_comm_objects.extend([obj.department, obj.commune])

sql_hostname = os.path.join(os.getenv("HOST"))
sql_username = os.path.join(os.getenv("DBUSER"))
sql_password = os.path.join(os.getenv("PASSWORD"))
sql_main_database = os.path.join(os.getenv("NAME"))
sql_port = 3306


def __mysql_connect__():
    """
    Connect to a MySQL server using the SSH tunnel connection.
    Return the connection object.
    """
    # Connect to a MySQL server using the SSH tunnel connection

    global connection

    connection = pymysql.connect(host=sql_hostname, user=sql_username,
                                 passwd=sql_password, db=sql_main_database,
                                 port=sql_port)
    return connection


def __mysql_disconnect__():
    """
    Close the connection, passed in parameter, to the database
    """
    connection.close()


def execute_scripts_from_file(cnx, cur, filename):
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        try:
            if command.strip() != '':
                cur.execute(command)
                print('Executed')
        except Exception as msg:
            print("Command skipped: ", msg)

    cnx.commit()


def dep_comm_remover(cur):
    try:
        models.Training._meta.get_field('department')
        # first_element = models.Training.objects.filter(id=1)[0]
        if None in training_dep_comm_objects:
            cur.execute("SELECT latitude, longitude, id FROM dashboard_training;")

            # Get all the rows for that query
            training0_items = cur.fetchall()
            # Convert the result into a list of dictionaries (useful later)
            items = [
                {
                    'latitude': item[0],
                    'longitude': item[1],
                    'training_id': item[2]
                }
                for item in training0_items
            ]

            good_datas = []
            for item in items:
                item_id = item['training_id']
                for feature in departments_geojson['features'] and communes_geojson['features']:
                    polygon = shape(feature['geometry'])
                    if polygon.contains(Point(item['longitude'], item['latitude'])):
                        good_datas.append({"id": item_id, "department": feature["properties"]["NAME_1"],
                                           "commune": feature["properties"]["NAME_2"]})

            for item in good_datas:
                models.Training.objects.filter(id=item['id']).update(department=item['department'],
                                                                     commune=item['commune'])

            good_datas_id = [item['id'] for item in good_datas]
            bad_datas = [item['training_id'] for item in items if item['training_id'] not in good_datas_id]

            for item in bad_datas:
                models.Training.objects.filter(id=item).delete()

        else:
            pass

    except FieldDoesNotExist as msg:
        print("Skip adding of communes and departments for trainings:", msg)


def run():
    cnx = __mysql_connect__()
    cur = cnx.cursor()
    execute_scripts_from_file(cnx=cnx, cur=cur,
                              filename=os.path.join(BASE_DIR, 'staticfiles/Data/training_dummy_data.sql'))
    dep_comm_remover(cur=cur)
    __mysql_disconnect__()


if __name__ == '__main__':
    run()
