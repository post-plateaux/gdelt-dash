import os
import psycopg2
import traceback

# Retrieve database connection details
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT', '5432')  # Default to '5432' if not set

# Create a connection string
conn_string = f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}' port='{db_port}'"

try:
    # Attempt to connect to the database
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print("Connection to the database was successful!")

    # Drop the cameo_goldstein_scale table if it exists
    cursor.execute("DROP TABLE IF EXISTS cameo_goldstein_scale CASCADE;")
    print("Table cameo_goldstein_scale dropped successfully.")

    # Create the cameo_goldstein_scale table
    create_table_query = """
    CREATE TABLE cameo_goldstein_scale (
        event_code VARCHAR(10) PRIMARY KEY,
        goldstein_scale FLOAT NOT NULL
    );
    """
    cursor.execute(create_table_query)
    print("Table cameo_goldstein_scale created successfully.")
    conn.commit()

    # Insert data directly into cameo_goldstein_scale
    cameo_goldstein_scale_data = [
    ("01", 0.0),
    ("010", 0.0),
    ("011", -0.1),
    ("012", -0.4),
    ("013", 0.4),
    ("014", 0.0),
    ("015", 0.0),
    ("016", -2.0),
    ("017", 0.0),
    ("018", 3.4),
    ("019", 3.4),
    ("02", 3.0),
    ("020", 3.0),
    ("021", 3.4),
    ("0211", 3.4),
    ("0212", 3.4),
    ("0213", 3.4),
    ("0214", 3.4),
    ("022", 3.2),
    ("023", 3.4),
    ("0231", 3.4),
    ("0232", 3.4),
    ("0233", 3.4),
    ("0234", 3.4),
    ("024", -0.3),
    ("0241", -0.3),
    ("0242", -0.3),
    ("0243", -0.3),
    ("0244", -0.3),
    ("025", -0.3),
    ("0251", -0.3),
    ("0252", -0.3),
    ("0253", -0.3),
    ("0254", -0.3),
    ("0255", -0.3),
    ("0256", -0.3),
    ("026", 4.0),
    ("027", 4.0),
    ("028", 4.0),
    ("03", 4.0),
    ("030", 4.0),
    ("031", 5.2),
    ("0311", 5.2),
    ("0312", 5.2),
    ("0313", 5.2),
    ("0314", 5.2),
    ("032", 4.5),
    ("033", 5.2),
    ("0331", 5.2),
    ("0332", 5.2),
    ("0333", 5.2),
    ("0334", 6.0),
    ("034", 7.0),
    ("0341", 7.0),
    ("0342", 7.0),
    ("0343", 7.0),
    ("0344", 7.0),
    ("035", 7.0),
    ("0351", 7.0),
    ("0352", 7.0),
    ("0353", 7.0),
    ("0354", 7.0),
    ("0355", 7.0),
    ("0356", 7.0),
    ("036", 4.0),
    ("037", 5.0),
    ("038", 7.0),
    ("039", 5.0),
    ("04", 1.0),
    ("040", 1.0),
    ("041", 1.0),
    ("042", 1.9),
    ("043", 2.8),
    ("044", 2.5),
    ("045", 5.0),
    ("046", 7.0),
    ("05", 3.5),
    ("050", 3.5),
    ("051", 3.4),
    ("052", 3.5),
    ("053", 3.8),
    ("054", 6.0),
    ("055", 7.0),
    ("056", 7.0),
    ("057", 8.0),
    ("06", 6.0),
    ("060", 6.0),
    ("061", 6.4),
    ("062", 7.4),
    ("063", 7.4),
    ("064", 7.0),
    ("07", 7.0),
    ("070", 7.0),
    ("071", 7.4),
    ("072", 8.3),
    ("073", 7.4),
    ("074", 8.5),
    ("075", 7.0),
    ("08", 5.0),
    ("080", 5.0),
    ("081", 5.0),
    ("0811", 5.0),
    ("0812", 5.0),
    ("0813", 5.0),
    ("0814", 5.0),
    ("082", 5.0),
    ("083", 5.0),
    ("0831", 5.0),
    ("0832", 5.0),
    ("0833", 5.0),
    ("0834", 5.0),
    ("084", 7.0),
    ("0841", 7.0),
    ("0842", 7.0),
    ("085", 7.0),
    ("086", 9.0),
    ("0861", 9.0),
    ("0862", 9.0),
    ("0863", 9.0),
    ("087", 9.0),
    ("0871", 9.0),
    ("0872", 9.0),
    ("0873", 9.0),
    ("0874", 10.0),
    ("09", -2.0),
    ("090", -2.0),
    ("091", -2.0),
    ("092", -2.0),
    ("093", -2.0),
    ("094", -2.0),
    ("10", -5.0),
    ("100", -5.0),
    ("101", -5.0),
    ("1011", -5.0),
    ("1012", -5.0),
    ("1013", -5.0),
    ("1014", -5.0),
    ("102", -5.0),
    ("103", -5.0),
    ("1031", -5.0),
    ("1032", -5.0),
    ("1033", -5.0),
    ("1034", -5.0),
    ("104", -5.0),
    ("1041", -5.0),
    ("1042", -5.0),
    ("1043", -5.0),
    ("1044", -5.0),
    ("105", -5.0),
    ("1051", -5.0),
    ("1052", -5.0),
    ("1053", -5.0),
    ("1054", -5.0),
    ("1055", -5.0),
    ("1056", -5.0),
    ("107", -5.0),
    ("108", -5.0),
    ("11", -2.0),
    ("110", -2.0),
    ("111", -2.0),
    ("112", -2.0),
    ("1121", -2.0),
    ("1122", -2.0),
    ("1123", -2.0),
    ("1124", -2.0),
    ("1125", -2.0),
    ("113", -2.0),
    ("114", -2.0),
    ("115", -2.0),
    ("116", -2.0),
    ("12", -4.0),
    ("120", -4.0),
    ("121", -4.0),
    ("1211", -4.0),
    ("1212", -4.0),
    ("122", -4.0),
    ("1221", -4.0),
    ("1222", -4.0),
    ("1223", -4.0),
    ("1224", -4.0),
    ("123", -4.0),
    ("1231", -4.0),
    ("1232", -4.0),
    ("1233", -4.0),
    ("1234", -4.0),
    ("124", -4.0),
    ("1241", -4.0),
    ("1242", -4.0),
    ("1243", -4.0),
    ("1244", -4.0),
    ("1245", -4.0),
    ("1246", -4.0),
    ("125", -5.0),
    ("126", -5.0),
    ("127", -5.0),
    ("128", -5.0),
    ("129", -5.0),
    ("13", -6.0),
    ("130", -4.4),
    ("131", -5.8),
    ("1311", -5.8),
    ("1312", -5.8),
    ("1313", -5.8),
    ("132", -5.8),
    ("1321", -5.8),
    ("1322", -5.8),
    ("1323", -5.8),
    ("1324", -5.8),
    ("133", -5.8),
    ("134", -5.8),
    ("135", -5.8),
    ("136", -7.0),
    ("137", -7.0),
    ("138", -7.0),
    ("1381", -7.0),
    ("1382", -7.0),
    ("1383", -7.0),
    ("1384", -7.0),
    ("1385", -7.0),
    ("139", -7.0),
    ("14", -6.5),
    ("140", -6.5),
    ("141", -6.5),
    ("1411", -6.5),
    ("1412", -6.5),
    ("1413", -6.5),
    ("1414", -6.5),
    ("142", -6.5),
    ("1421", -6.5),
    ("1422", -6.5),
    ("1423", -6.5),
    ("1424", -6.5),
    ("143", -6.5),
    ("1431", -6.5),
    ("1432", -6.5),
    ("1433", -6.5),
    ("1434", -6.5),
    ("144", -7.5),
    ("1441", -7.5),
    ("1442", -7.5),
    ("1443", -7.5),
    ("1444", -7.5),
    ("145", -7.5),
    ("1451", -7.5),
    ("1452", -7.5),
    ("1453", -7.5),
    ("1454", -7.5),
    ("15", -7.2),
    ("150", -7.2),
    ("151", -7.2),
    ("152", -7.2),
    ("153", -7.2),
    ("154", -7.2),
    ("16", -4.0),
    ("160", -4.0),
    ("161", -4.0),
    ("162", -5.6),
    ("1621", -5.6),
    ("1622", -5.6),
    ("1623", -5.6),
    ("163", -8.0),
    ("164", -7.0),
    ("165", -6.5),
    ("166", -7.0),
    ("1661", -7.0),
    ("1662", -7.0),
    ("1663", -7.0),
    ("17", -7.0),
    ("170", -7.0),
    ("171", -9.2),
    ("1711", -9.2),
    ("1712", -9.2),
    ("172", -5.0),
    ("1721", -5.0),
    ("1722", -5.0),
    ("1723", -5.0),
    ("1724", -5.0),
    ("173", -5.0),
    ("174", -5.0),
    ("175", -9.0),
    ("18", -9.0),
    ("180", -9.0),
    ("181", -9.0),
    ("182", -9.5),
    ("1821", -9.0),
    ("1822", -9.0),
    ("1823", -10.0),
    ("183", -10.0),
    ("1831", -10.0),
    ("1832", -10.0),
    ("1833", -10.0),
    ("184", -8.0),
    ("185", -8.0),
    ("186", -10.0),
    ("19", -10.0),
    ("190", -10.0),
    ("191", -9.5),
    ("192", -9.5),
    ("193", -10.0),
    ("194", -10.0),
    ("195", -10.0),
    ("196", -9.5),
    ("20", -10.0),
    ("200", -10.0),
    ("201", -9.5),
    ("202", -10.0),
    ("203", -10.0),
    ("204", -10.0),
    ("2041", -10.0),
    ("2042", -10.0)
]

    for event_code, goldstein_scale in cameo_goldstein_scale_data:
        insert_query = "INSERT INTO cameo_goldstein_scale (event_code, goldstein_scale) VALUES (%s, %s)"
        cursor.execute(insert_query, (event_code, goldstein_scale))
    print("Data loaded successfully into cameo_goldstein_scale.")
    conn.commit()

except Exception as e:
    print(f"Failed to connect to the database: {e}")
    print(traceback.format_exc())
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()