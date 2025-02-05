import os
import psycopg2
import traceback

# Retrieve database connection details
db_user = os.getenv('POSTGIS_USER')
db_password = os.getenv('POSTGIS_PASSWORD')
db_name = os.getenv('POSTGIS_DB')
db_host = os.getenv('POSTGIS_HOST')
db_port = os.getenv('POSTGIS_PORT', '5432')  # Default to '5432' if not set

# Create a connection string
conn_string = f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}' port='{db_port}'"

try:
    # Attempt to connect to the database
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print("Connection to the database was successful!")

    # Drop the cameo_religion table if it exists
    cursor.execute("DROP TABLE IF EXISTS cameo_religion CASCADE;")
    print("Table cameo_religion dropped successfully.")

    # Create the cameo_religion table
    create_table_query = """
    CREATE TABLE cameo_religion (
        religion_code VARCHAR(10) PRIMARY KEY,
        religion_label VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_table_query)
    print("Table cameo_religion created successfully.")
    conn.commit()

    # Insert data directly into cameo_religion
    cameo_religion_data = [
    ("ADR", "African Diasporic Religion"),
    ("ALE", "Alewi"),
    ("ATH", "Agnostic"),
    ("BAH", "Bahai Faith"),
    ("BUD", "Buddhism"),
    ("CHR", "Christianity"),
    ("CON", "Confucianism"),
    ("CPT", "Coptic"),
    ("CTH", "Catholic"),
    ("DOX", "Orthodox"),
    ("DRZ", "Druze"),
    ("HIN", "Hinduism"),
    ("HSD", "Hasidic"),
    ("ITR", "Indigenous Tribal Religion"),
    ("JAN", "Jainism"),
    ("JEW", "Judaism"),
    ("JHW", "Jehovah's Witness"),
    ("LDS", "Latter Day Saints"),
    ("MOS", "Muslim"),
    ("MRN", "Maronite"),
    ("NRM", "New Religious Movement"),
    ("PAG", "Pagan"),
    ("PRO", "Protestant"),
    ("SFI", "Sufi"),
    ("SHI", "Shia"),
    ("SHN", "Old Shinto School"),
    ("SIK", "Sikh"),
    ("SUN", "Sunni"),
    ("TAO", "Taoist"),
    ("UDX", "Ultra-Orthodox"),
    ("ZRO", "Zoroastrianism")
]

    for religion_code, religion_label in cameo_religion_data:
        insert_query = "INSERT INTO cameo_religion (religion_code, religion_label) VALUES (%s, %s)"
        cursor.execute(insert_query, (religion_code, religion_label))
    print("Data loaded successfully into cameo_religion.")
    conn.commit()

except Exception as e:
    print(f"Failed to connect to the database: {e}")
    print(traceback.format_exc())
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
