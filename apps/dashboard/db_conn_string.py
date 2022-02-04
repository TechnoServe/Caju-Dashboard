import logging
import os
import pymysql
import paramiko
import sshtunnel
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

    global tunnel
    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=mypkey,
        remote_bind_address=(sql_hostname, sql_port))

    tunnel.start()


def mysql_connect():
    # Connect to a MySQL server using the SSH tunnel connection

    global connection

    connection = pymysql.connect(host='127.0.0.1', user=sql_username,
                                 passwd=sql_password, db=sql_main_database,
                                 port=tunnel.local_bind_port)
    return connection


def mysql_disconnect():
    connection.close()


def close_ssh_tunnel():
    tunnel.close()


open_ssh_tunnel()
mysql_connect()
cur = mysql_connect().cursor()
