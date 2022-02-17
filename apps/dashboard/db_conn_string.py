import logging
import os

import paramiko
import pymysql
import sshtunnel
from sshtunnel import SSHTunnelForwarder

mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.getenv("PKEY")))

sql_hostname = os.path.join(os.getenv("SQL_HOSTNAME"))
sql_username = os.path.join(os.getenv("SQL_USERNAME"))
sql_password = os.path.join(os.getenv("SQL_PASSWORD"))
sql_main_database = os.path.join(os.getenv("SQL_DATABASE"))
sql_port = 3306
ssh_host = os.path.join(os.getenv("SSH_HOSTNAME"))
ssh_user = os.path.join(os.getenv("SSH_USER"))
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
