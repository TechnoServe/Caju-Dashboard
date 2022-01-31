import geojson
import mariadb
import sys
from shapely.geometry import shape, Point


# conn = psycopg2.connect(
#     database="cnqa",
#     user="admin",
#     password="abc123def345",
#     host="ec2-3-22-99-140.us-east-2.compute.amazonaws.com",
#     port='5432'
# )

def get_qar_data_from_db():
    try:
        conn = mariadb.connect(
            database="cnqa_db",  # "cnqa",
            user="superuser",  # "dbuser",
            password="password",  # "12345678cnqa",
            host="localhost",  # "ec2-3-22-99-140.us-east-2.compute.amazonaws.com",
            port=5432,
            read_timeout=5,
            connect_timeout=5,
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return []

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
            {'document_id': item[0], 'country': item[6], 'department': item[8], 'commune': item[9], 'site': item[7],
             'latitude': item[4], 'longitude': item[5], 'altitude': item[3], 'kor': item[2]}
            for item in items
        ]

    class QarObject:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    items = get_items()
    qars = [
        QarObject(**item)
        for item in items
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

    for i in range(len(qars)):
        qars[i].department = get_department_from_coord(qars[i].longitude, qars[i].latitude)
    conn.close()

    return qars
