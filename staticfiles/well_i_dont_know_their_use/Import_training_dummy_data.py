# import sqlite3 module
import sqlite3


def import_dummy_data():
    # create con object to connect 
    # the database
    connection = sqlite3.connect("./my_db.db")
    # create the cursor object
    cursor = connection.cursor()
    # execute the script
    sql_file = open("../../test.sql")
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)


if __name__ == '__main__':
    import_dummy_data()