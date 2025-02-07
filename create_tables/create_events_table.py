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

# Read the CSV file to get column names and data types
file_path = 'Events.csv'  # Update this path as needed
events_df = pd.read_csv(file_path, header=None)

# Define a mapping for the data types to PostgreSQL-compatible types
type_mapping = {
    'INTEGER': 'BIGINT',
    'FLOAT': 'REAL',
    'STRING': 'TEXT'
}

# Generate the SQL statement for table creation
columns = ", ".join([f"{row[0]} {type_mapping.get(row[1], 'TEXT')}" for _, row in events_df.iterrows()])
create_table_query = f"CREATE TABLE events ({columns});"

# Connect to the PostgreSQL database and create the table
try:
    # Establish a connection to the database
    connection = psycopg2.connect(conn_string)
    cursor = connection.cursor()

    # Execute the table creation query
    cursor.execute(create_table_query)
    connection.commit()

    print("Table 'events' created successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the database connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()
