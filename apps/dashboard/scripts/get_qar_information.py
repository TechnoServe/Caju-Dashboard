import logging
import os

import geojson
import paramiko
import pymysql
import sshtunnel
from shapely.geometry import shape, Point
from sshtunnel import SSHTunnelForwarder

from cajulab_remote_sensing_dashboard.settings import BASE_DIR

mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(BASE_DIR, 'apps/dashboard/tns-wiredin-cqna.pem'))

sql_hostname = '127.0.0.1'
sql_username = 'dbuser'
sql_password = '12345678cnqa'
sql_main_database = 'cnqa'
sql_port = 3306
ssh_host = 'ec2-3-22-99-140.us-east-2.compute.amazonaws.com'
ssh_user = 'ec2-user'
ssh_port = 22


def open_ssh_tunnel(verbose=False):
    # Open an SSH tunnel and connect using a username and ssh private key.

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
    tunnel.close()


def mysql_connect(tunnel):
    # Connect to a MySQL server using the SSH tunnel connection

    conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                           passwd=sql_password, db=sql_main_database,
                           port=tunnel.local_bind_port)
    return conn


def mysql_disconnect(conn):
    conn.close()


def get_items(cur):
    # Run a query
    cur.execute('SELECT'
                ' document_id, qar, kor,'
                ' location_altitude, location_lat,'
                ' location_lon, location_country, location_city,'
                ' location_region, location_sub_region'
                ' FROM cnqa.free_qar_result;')

    # Get all the rows for that query
    qart_items = cur.fetchall()
    # Convert the result into a list of dictionaries (useful later)
    return [
        {'document_id': item[0], 'country': item[6], 'department': item[8], 'commune': item[9], 'site': item[7],
         'latitude': item[4], 'longitude': item[5], 'altitude': item[3], 'kor': item[2]}
        for item in qart_items
    ]


def get_department_from_coord(longitude, latitude):
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
    class QarObject:
        def __init__(self, **entries):
            self.latitude = None
            self.longitude = None
            self.department = None
            self.__dict__.update(entries)

    try:
        tunnel = open_ssh_tunnel()
        connection = mysql_connect(tunnel)
    except pymysql.Error as e:
        print(f"Error connecting to MySQL Platform: {e}")
        return []

    items = get_items(connection.cursor())
    qars = [
        QarObject(**item)
        for item in items
    ]

    for i in range(len(qars)):
        qars[i].department = get_department_from_coord(qars[i].longitude, qars[i].latitude)
    mysql_disconnect(connection)
    close_ssh_tunnel(tunnel)
    return qars
