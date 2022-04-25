import sqlite3


def import_dummy_data():
    # create the database in RAM
    connection = sqlite3.connect(":memory:")

    cursor = connection.cursor()

    sql_file = open("training_dummy_data.sql")
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)


if __name__ == '__main__':
    import_dummy_data()
