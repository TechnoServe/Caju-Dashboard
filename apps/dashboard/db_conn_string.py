import logging
import os

import paramiko
import pymysql
import sshtunnel
from sshtunnel import SSHTunnelForwarder

mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.getenv("PKEY")))

sql_hostname = '127.0.0.1'
sql_username = 'dbuser'
sql_password = '12345678cnqa'
sql_main_database = 'cnqa'
sql_port = 3306
ssh_host = 'ec2-3-22-99-140.us-east-2.compute.amazonaws.com'
ssh_user = 'ec2-user'
ssh_port = 22


def __open_ssh_tunnel__(verbose=False):
    """
    Open an SSH tunnel and connect using a username and ssh private key.
    Pass True to display the Verbose.
    Return the tunnel created.
    """
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


def __mysql_connect__():
    """
    Connect to a MySQL server using the SSH tunnel connection.
    Return the connection object.
    """
    # Connect to a MySQL server using the SSH tunnel connection

    global connection

    connection = pymysql.connect(host=sql_hostname, user=sql_username,
                                 passwd=sql_password, db=sql_main_database,
                                 port=tunnel.local_bind_port)
    return connection


def __mysql_disconnect__():
    """
    Close the connection, passed in parameter, to the database
    """
    connection.close()


def __close_ssh_tunnel__():
    """
    Close the SSH tunnel passed as parameter.
    """
    tunnel.close()


__open_ssh_tunnel__()
cur = __mysql_connect__().cursor()
