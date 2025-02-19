import os
import psycopg2
import pandas as pd
import traceback

# Retrieve database connection details
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT', '5432')  # Default to '5432' if not set

# Create a connection string
conn_string = f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}' port='{db_port}'"

# Read the TSV file to get column names and data types
file_path = os.path.join(os.path.dirname(__file__), 'eventMentions.tsv')
mentions_df = pd.read_csv(file_path, sep='\t', header=None)

# Define a mapping for the data types to PostgreSQL-compatible types
type_mapping = {
    'INTEGER': 'BIGINT',
    'FLOAT': 'REAL',
    'STRING': 'TEXT'
}

# Generate the SQL statement for table creation
columns = ", ".join([f"{row[0]} {type_mapping.get(row[1], 'TEXT')}" for _, row in mentions_df.iterrows()])
create_table_query = f"CREATE TABLE mentions_translated ({columns});"

# Connect to the PostgreSQL database and create the table
try:
    # Establish a connection to the database
    connection = psycopg2.connect(conn_string)
    cursor = connection.cursor()

    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS mentions_translated;")
    print("Dropped table mentions_translated if it existed.")

    # Execute the table creation query
    cursor.execute(create_table_query)
    connection.commit()

    print("Table 'mentions_translated' created successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the database connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()
