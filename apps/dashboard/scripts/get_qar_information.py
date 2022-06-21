import logging
import os

import geojson
import paramiko
import pymysql
import sshtunnel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from shapely.geometry import shape, Point
from sshtunnel import SSHTunnelForwarder

"""
Add your path to your pkey perm file
"""
mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.getenv("PKEY")))

sql_hostname = os.path.join(os.getenv("SQL_HOSTNAME"))
sql_username = os.path.join(os.getenv("SQL_USERNAME"))
sql_password = os.path.join(os.getenv("SQL_PASSWORD"))
sql_main_database = os.path.join(os.getenv("SQL_DATABASE"))
sql_port = 3306
ssh_host = os.path.join(os.getenv("SSH_HOSTNAME"))
ssh_user = os.path.join(os.getenv("SSH_USER"))
ssh_port = 22

with open("staticfiles/json/ben_adm1.json", errors="ignore") as f:
    departments_geojson = geojson.load(f)


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


def open_ssh_tunnel(verbose=False):
    """
    Open an SSH tunnel and connect using a username and ssh private key.
    Pass True to display the Verbose.
    Return the tunnel created.
    """

    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG

    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=mypkey,
        remote_bind_address=(sql_hostname, sql_port))

    tunnel.start()
    return tunnel


def close_ssh_tunnel(tunnel):
    """
    Close the SSH tunnel passed as parameter.
    """
    tunnel.close()


def mysql_connect(tunnel):
    """
    Connect to a MySQL server using the SSH tunnel connection.
    Return the connection object.
    """

    conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                           passwd=sql_password, db=sql_main_database,
                           port=tunnel.local_bind_port)
    return conn


def mysql_disconnect(conn):
    """
    Close the connection, passed in parameter, to the database
    """
    conn.close()


def __get_items__(cur):
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
        Check whenever a Point defined by the longitude and latitude passed in parameter belongs to a department in
        Benin
        Return the name of the department found or 'Unknown' otherwise
        """
        point = Point(qars[index].longitude, qars[index].latitude)
        for feature in departments_geojson['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
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

        tunnel = open_ssh_tunnel()
        connection = mysql_connect(tunnel)

        qars = __get_items__(connection.cursor())
        __get_department_from_coord__(qars)

        mysql_disconnect(connection)
        close_ssh_tunnel(tunnel)
    except Exception as e:
        print({e})
        qars = []

    return qars


current_qars = get_qar_data_from_db()

scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(days=1))
def update_qars():
    global current_qars
    current_qars = get_qar_data_from_db()


scheduler.start()
