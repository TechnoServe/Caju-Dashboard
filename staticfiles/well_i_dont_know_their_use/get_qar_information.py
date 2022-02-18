import mariadb
import sys

conn = mariadb.connect(
    user="sean",
    host="localhost",
    database="cnqa_db")
cur = conn.cursor()


# Automatically commit transactions
conn.set_session(autocommit=False)

cur = conn.cursor()


def get_items():
    # Run a query
    cur.execute('SELECT'
                ' document_id, qar, kor,'
                ' location_altitude, location_lat,'
                ' location_lon, location_country, location_city,'
                ' location_region, location_sub_region'
                ' FROM cnqa_db.free_qar_result;')

    # Get all the rows for that query
    items = cur.fetchall()

    # Convert the result into a list of dictionaries (useful later)
    return [
        {'document_id': item[0], 'country': item[6], 'department': item[7], 'commune': item[8], 'site': item[9],
         'latitude': item[4], 'longitude': item[5], 'altitude': item[3], 'kor': item[2]}
        for item in items
    ]


print(get_items())
