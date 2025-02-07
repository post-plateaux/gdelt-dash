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

    # Drop the cameo_actor_type table if it exists
    cursor.execute("DROP TABLE IF EXISTS cameo_actor_type CASCADE;")
    print("Table cameo_actor_type dropped successfully.")

    # Create the cameo_actor_type table
    create_table_query = """
    CREATE TABLE cameo_actor_type (
        actor_type_code VARCHAR(10) PRIMARY KEY,
        actor_type_label VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_table_query)
    print("Table cameo_actor_type created successfully.")
    conn.commit()

    # Insert data directly into cameo_actor_type
    cameo_actor_type_data = [
    ("COP", "Police forces"),
    ("GOV", "Government"),
    ("INS", "Insurgents"),
    ("JUD", "Judiciary"),
    ("MIL", "Military"),
    ("OPP", "Political Opposition"),
    ("REB", "Rebels"),
    ("SEP", "Separatist Rebels"),
    ("SPY", "State Intelligence"),
    ("UAF", "Unaligned Armed Forces"),
    ("AGR", "Agriculture"),
    ("BUS", "Business"),
    ("CRM", "Criminal"),
    ("CVL", "Civilian"),
    ("DEV", "Development"),
    ("EDU", "Education"),
    ("ELI", "Elites"),
    ("ENV", "Environmental"),
    ("HLH", "Health"),
    ("HRI", "Human Rights"),
    ("LAB", "Labor"),
    ("LEG", "Legislature"),
    ("MED", "Media"),
    ("REF", "Refugees"),
    ("MOD", "Moderate"),
    ("RAD", "Radical"),
    ("AMN", "Amnesty International"),
    ("IRC", "Red Cross"),
    ("GRP", "Greenpeace"),
    ("UNO", "United Nations"),
    ("PKO", "Peacekeepers"),
    ("UIS", "Unidentified State Actor"),
    ("IGO", "Inter-Governmental Organization"),
    ("IMG", "International Militarized Group"),
    ("INT", "International/Transnational Generic"),
    ("MNC", "Multinational Corporation"),
    ("NGM", "Non-Governmental Movement"),
    ("NGO", "Non-Governmental Organization"),
    ("SET", "Settler")
]

    for actor_type_code, actor_type_label in cameo_actor_type_data:
        insert_query = "INSERT INTO cameo_actor_type (actor_type_code, actor_type_label) VALUES (%s, %s)"
        cursor.execute(insert_query, (actor_type_code, actor_type_label))
    print("Data loaded successfully into cameo_actor_type.")
    conn.commit()

except Exception as e:
    print(f"Failed to connect to the database: {e}")
    print(traceback.format_exc())
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
