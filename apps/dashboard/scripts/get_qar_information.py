import asyncio
import os

import geojson
import paramiko
from apscheduler.schedulers.background import BackgroundScheduler
from shapely.geometry import shape, Point

from apps.dashboard.db_conn_string import cur
from datetime import datetime

from apscheduler.triggers.interval import IntervalTrigger

"""
Add your path to your pkey perm file
"""
mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.getenv("PKEY")))

sql_hostname = '127.0.0.1'
sql_username = 'dbuser'
sql_password = '12345678cnqa'
sql_main_database = 'cnqa'
sql_port = 3306
ssh_host = 'ec2-3-22-99-140.us-east-2.compute.amazonaws.com'
ssh_user = 'ec2-user'
ssh_port = 22


class QarObject:
    def __init__(self, **entries):
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.department = None
        self.document_id = None
        self.country = None
        self.commune = None
        self.site = None
        self.kor = None
        self.nut_count = None
        self.defective_rate = None
        self.__dict__.update(entries)

    def dump(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'department': self.department,
            'document_id': self.document_id,
            'country': self.country,
            'commune': self.commune,
            'site': self.site,
            'kor': self.kor,
            'nut_count': self.nut_count,
            'defective_rate': self.defective_rate,
        }


def __get_items__():
    """
    Execute an SQL query to get:
            ' document_id, qar, kor,'
            ' location_altitude, location_lat,'
            ' location_lon, location_country, location_city,'
            ' location_region, location_sub_region'
        from the CajuQualityDashbord database.

    Return a list of QarObject
    """

    # Run a query
    cur.execute('SELECT'
                ' document_id, qar, kor,'
                ' location_altitude, location_lat,'
                ' location_lon, location_country, location_city,'
                ' location_region, location_sub_region, defective_rate, nut_count'
                ' FROM cnqa.free_qar_result;')

    # Get all the rows for that query
    qart_items = cur.fetchall()
    # Convert the result into a list of dictionaries (useful later)
    items = [
        {'document_id': item[0], 'country': item[6], 'department': item[8], 'commune': item[9], 'site': item[7],
         'latitude': item[4], 'longitude': item[5], 'altitude': item[3],
         'kor': item[2], 'defective_rate': item[10], 'nut_count': item[11]}
        for item in qart_items
    ]
    return [
        QarObject(**item)
        for item in items
    ]


def __get_department_from_coord__(qars):
    def ___location_finder__(index):
        """
        Read geolocalization data from 'ben_adm1.json' file
        Check whenever a Point defined by the longitude and latitude passed in parameter belongs to a department in Benin
        Return the name of the department found or 'Unknown' otherwise
        """
        with open("staticfiles/json/ben_adm1.json", errors="ignore") as f:
            departments_geojson = geojson.load(f)
        point = Point(qars[index].longitude, qars[index].latitude)
        for feature in departments_geojson['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                print(feature["properties"]["NAME_1"])
                qars[index].department = feature["properties"]["NAME_1"]

    for i in range(len(qars)):
        ___location_finder__(i)
    return qars


def get_qar_data_from_db():
    """
    Retrieves Caju Quality data from the CajuQualityApp database

    Return a list of Qar objects
    """
    try:
        qars = __get_items__()

        __get_department_from_coord__(qars)

    except Exception as e:
        print({e})
        qars = []

    return qars


current_qars = None

scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(days=1))
def update_qars():
    global current_qars
    current_qars = get_qar_data_from_db()


scheduler.start()
