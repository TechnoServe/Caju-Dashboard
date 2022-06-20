import os
import sqlite3

import geojson
import paramiko
import pymysql
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.core.exceptions import FieldDoesNotExist
from shapely.geometry import shape, Point

from apps.dashboard import models

with open("staticfiles/json/ben_adm1.json", encoding="utf8", errors="ignore") as f:
    departments_geojson = geojson.load(f)

with open("staticfiles/json/ben_adm2.json", encoding="utf8", errors="ignore") as f:
    communes_geojson = geojson.load(f)

"""
Add your path to your pkey perm file
"""
mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.getenv("PKEY")))

sql_hostname = os.path.join(os.getenv("HOST"))
sql_username = os.path.join(os.getenv("USER"))
sql_password = os.path.join(os.getenv("PASSWORD"))
sql_main_database = os.path.join(os.getenv("NAME"))
sql_port = int(os.path.join(os.getenv("PORT")))


class TrainingObject:
    def __init__(self, **entries):
        self.latitude = None
        self.longitude = None
        self.number_of_participant = None
        self.datetime = None
        self.module = None
        self.trainer = None
        self.department = None
        self.commune = None
        self.__dict__.update(entries)

    def dump(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'number_of_participant': self.number_of_participant,
            'datetime': self.datetime,
            'module': self.module,
            'trainer': self.trainer,
            'department': self.department,
            'commune': self.commune,
        }


def mysql_connect():
    """
    Connect to a MySQL server using the SSH tunnel connection.
    Return the connection object.
    """

    conn = pymysql.connect(host=sql_hostname, user=sql_username,
                           passwd=sql_password, db=sql_main_database,
                           port=sql_port)
    return conn


def sqlite_connect():
    """
    Connect to a MySQL server using the SSH tunnel connection.
    Return the connection object.
    """

    conn = sqlite3.connect('my_db.db')
    return conn


def mysql_disconnect(conn):
    """
    Close the connection, passed in parameter, to the database
    """
    conn.close()


def sqlite_disconnect(conn):
    """
    Close the connection, passed in parameter, to the database
    """
    conn.close()


# Delete the data outside of Benin and add department and commune to models
try:
    models.Training._meta.get_field('department')
    # first_element = models.Training.objects.filter(id=1)[0]
    if models.Training.objects.filter(id=1)[0].department != '' and models.Training.objects.filter(id=1)[
        0].commune != '':
        pass
    else:
        connection = sqlite_connect()
        cur = connection.cursor()
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
            models.Training.objects.filter(id=item['id']).update(department=item['department'], commune=item['commune'])

        good_datas_id = [item['id'] for item in good_datas]
        bad_datas = [item['training_id'] for item in items if item['training_id'] not in good_datas_id]

        for item in bad_datas:
            models.Training.objects.filter(id=item).delete()

        sqlite_disconnect(connection)

except FieldDoesNotExist:
    print("Skip adding of communes and departments for trainings")
    pass


def __get_department_from_coord__(latitude, longitude):
    def ___location_finder__():
        """
        Read geolocalization data from 'ben_adm1.json' file
        Check whenever a Point defined by the longitude and latitude passed in parameter belongs to a department in
        Benin
        Return the name of the department found or 'Unknown' otherwise
        """
        point = Point(longitude, latitude)
        for feature in departments_geojson['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                return feature["properties"]["NAME_1"]

        return "Unknown"

    return ___location_finder__()


def __get_commune_from_coord__(latitude, longitude):
    def ___location_finder__():
        """
        Read geolocalization data from 'ben_adm1.json' file
        Check whenever a Point defined by the longitude and latitude passed in parameter belongs to a commune in
        Benin
        Return the name of the commune found or 'Unknown' otherwise
        """
        point = Point(longitude, latitude)
        for feature in communes_geojson['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                return feature["properties"]["NAME_2"]

        return "Unknown"

    return ___location_finder__()


def __get_module__(cursor, module_id):
    # MySQL query
    # cursor.execute("SELECT"
    #                " module_name, category"
    #                " FROM dashboard_trainingmodule WHERE id = %s;", module_id)

    # Sqlite query
    cursor.execute("SELECT"
                   " module_name, category"
                   " FROM dashboard_trainingmodule WHERE id=?;", (module_id,))

    # Get all the rows for that query
    modules_items = cursor.fetchall()
    try:
        return [
            {
                "title": module[0],
                "category": module[1],
            }
            for module in modules_items
        ][-1]
    except Exception:
        return {
            "title": "Unknown",
            "category": "Unknown",
        }


def __get_trainer__(cursor, trainer_id):
    # MySQL query
    # cursor.execute("SELECT"
    #                " firstname, lastname, institution"
    #                " FROM dashboard_trainer WHERE id = %s;", trainer_id)

    # Sqlite query
    cursor.execute("SELECT"
                   " firstname, lastname, institution"
                   " FROM dashboard_trainer WHERE id=?;", (trainer_id,))

    # Get all the rows for that query
    trainers_items = cursor.fetchall()
    try:
        return [
            {
                "firstname": trainer[0],
                "lastname": trainer[1],
                "institution": trainer[2],
            }
            for trainer in trainers_items
        ][-1]
    except Exception:
        return {
            "firstname": "Unknown",
            "lastname": "Unknown",
            "institution": "Unknown",
        }


def __get_items__(cur):
    """
    Execute an SQL query to get:
            ' document_id, training, kor,'
            ' location_altitude, location_lat,'
            ' location_lon, location_country, location_city,'
            ' location_region, location_sub_region'
        from the CajuQualityDashbord database.

    Return a list of TrainingObject
    """

    # Run a query
    cur.execute('SELECT'
                ' latitude, longitude,'
                ' number_of_participant, module_id_id, trainer_id_id, datetime'
                ' FROM dashboard_training;')

    # Get all the rows for that query
    training_items = cur.fetchall()
    # Convert the result into a list of dictionaries (useful later)
    items = [
        {
            'latitude': item[0],
            'longitude': item[1],
            'number_of_participant': item[2],
            'department': __get_department_from_coord__(latitude=item[0], longitude=item[1]),
            'commune': __get_commune_from_coord__(latitude=item[0], longitude=item[1]),
            'module': __get_module__(cursor=cur, module_id=item[3]),
            'trainer': __get_trainer__(cursor=cur, trainer_id=item[4]),
            'datetime': item[5],
        }
        for item in training_items
    ]

    items = [item for item in items if item["department"] != "Unknown" and item["commune"] != "Unknown"]

    return [
        TrainingObject(**item)
        for item in items
    ]


def get_training_data_from_db():
    """
    Retrieves Trainings data from the CommCare and AppSheet database

    Return a list of Training objects
    """
    try:

        connection = sqlite_connect()

        trainings = __get_items__(connection.cursor())

        sqlite_disconnect(connection)
    except Exception as e:
        print({e})
        trainings = []

    return trainings


current_trainings = get_training_data_from_db()
scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(days=1))
def update_trainings():
    global current_trainings
    current_trainings = get_training_data_from_db()


scheduler.start()