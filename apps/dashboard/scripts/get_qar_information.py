import logging
import os

import geojson
import paramiko
import pymysql
import sshtunnel
from shapely.geometry import shape, Point
from sshtunnel import SSHTunnelForwarder
from apps.dashboard.db_conn_string import cur

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


def get_items(cur):
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


def get_department_from_coord(longitude, latitude):
    """
    Read geolocalization data from 'ben_adm1.json' file
    Check whenever a Point defined by the longitude and latitude passed in parameter belongs to a department in Benin
    Return the name of the department found or 'Unknown' otherwise
    """
    with open("staticfiles/json/ben_adm1.json", errors="ignore") as f:
        departments_geojson = geojson.load(f)
    point = Point(longitude, latitude)
    name = "Unknown"
    for feature in departments_geojson['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            name = feature["properties"]["NAME_1"]
    return name


def get_qar_data_from_db():
    """
    Retrieves Caju Quality data from the CajuQualityApp database

    Return a list of Qar objects
    """
    try:
        qars = get_items(cur)

        for i in range(len(qars)):
            qars[i].department = get_department_from_coord(qars[i].longitude, qars[i].latitude)
    except Exception as e:
        print({e})
        qars = []

    return qars
