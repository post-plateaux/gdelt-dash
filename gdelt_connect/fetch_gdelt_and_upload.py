import os
import psycopg2
import pandas as pd
import traceback
import requests  # Added
import io        # Added
import zipfile   # Added
import time      # Added

# Retrieve database connection details
db_user = os.getenv('POSTGIS_USER')
db_password = os.getenv('POSTGIS_PASSWORD')
db_name = os.getenv('POSTGIS_DB')
db_host = os.getenv('POSTGIS_HOST')
db_port = os.getenv('POSTGIS_PORT', '5432')  # Default to '5432' if not set

# Create a connection string
conn_string = f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}' port='{db_port}'"

# Data directory
data_dir = "./data"
batch_size = 2000  # Number of rows to insert in a single batch

def fetch_and_download_gdelt_data():
    """Fetch and download GDELT data from both English and Translation sources"""
    sources = [
        "http://data.gdeltproject.org/gdeltv2/lastupdate.txt",
        "http://data.gdeltproject.org/gdeltv2/lastupdate-translation.txt"
    ]
    zip_files = []
    for url in sources:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            # Get URLs for both export and mentions, ignore gkg
            urls = [line.split()[-1] for line in data.splitlines() 
                   if any(x in line for x in ['export', 'mentions'])]
            for file_url in urls:
                with requests.get(file_url, stream=True) as r:
                    r.raise_for_status()
                    zip_files.append(io.BytesIO(r.content))
                print(f"Downloaded {file_url.split('/')[-1]}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading from {url}: {e}")
    return zip_files

def extract_files(zip_files):
    """Extract files from in-memory ZIP files and return their contents."""
    extracted_files = {}
    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                extracted_files[file_name] = zip_ref.read(file_name)
            print(f"Extracted files from ZIP")
    return extracted_files

def validate_and_parse_row(row, expected_columns):
    # Split the row into fields based on a delimiter
    if isinstance(row, str):
        fields = row.split('\t' if '\t' in row else ',')
    else:
        fields = list(row)

    # Convert empty strings to None
    fields = [None if field == "" else field for field in fields]

    # Ensure the number of fields matches the expected number of columns
    if len(fields) == expected_columns:
        return fields
    else:
        raise ValueError(f"Row has {len(fields)} fields but expected {expected_columns}")

def load_data_to_db(table_name, file_content, columns, delimiter=','):
    """Load data from in-memory file content into the database."""
    try:
        # Connect to the database
        connection = psycopg2.connect(conn_string)
        cursor = connection.cursor()

        print(f"Loading data for table '{table_name}'")
        file = io.StringIO(file_content.decode('utf-8'))
        batch = []
        for line_number, row in enumerate(file, start=1):
                try:
                    # Validate and parse the row
                    parsed_row = validate_and_parse_row(row, len(columns))
                    batch.append(parsed_row)

                    # Insert batch if the batch size is reached
                    if len(batch) >= batch_size:
                        insert_batch(cursor, table_name, columns, batch)
                        batch.clear()  # Clear the batch after insertion

                except ValueError as ve:
                    print(f"Validation error on line {line_number}: {ve}")
                    # Optionally, write problematic lines to a separate file for manual review
                    with open(f"{table_name}_error_rows.txt", 'a') as error_file:
                        error_file.write(f"Line {line_number}: {row}")

                except psycopg2.DataError as de:
                    print(f"Data error on line {line_number}: {de}")
                    connection.rollback()
                    # Optionally, write problematic lines to a separate file for manual review
                    with open(f"{table_name}_error_rows.txt", 'a') as error_file:
                        error_file.write(f"Line {line_number}: {row}")

                except Exception as e:
                    print(f"Error inserting row at line {line_number}: {e}")
                    connection.rollback()
                    # Optionally, write problematic lines to a separate file for manual review
                    with open(f"{table_name}_error_rows.txt", 'a') as error_file:
                        error_file.write(f"Line {line_number}: {row}")

        # Insert any remaining rows in the last batch
        if batch:
            insert_batch(cursor, table_name, columns, batch)

        connection.commit()
        print(f"Data loaded into {table_name}")
    except Exception as e:
        print(f"An error occurred while loading data into {table_name}: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_batch(cursor, table_name, columns, batch):
    # Create insert query with the given column names
    columns_str = ', '.join(columns)
    values_placeholders = ', '.join(['%s'] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_placeholders})"

    try:
        # Execute batch insert
        cursor.executemany(insert_query, batch)
        print(f"Inserted a batch of {len(batch)} rows into {table_name}")
    except Exception as e:
        print(f"Error inserting batch: {e}")

def delete_all_rows(conn):
    """Delete all rows from the events and mentions tables."""
    cursor = conn.cursor()
    try:
        tables_to_delete = ['events', 'mentions']
        
        for table_name in tables_to_delete:
            print(f"Deleting all rows from table: {table_name}")
            cursor.execute(f"DELETE FROM {table_name};")
        
        conn.commit()
        print("All rows deleted successfully.")
    except Exception as e:
        print(f"Failed to delete rows: {e}")
        conn.rollback()
    finally:
        cursor.close()

import time

# Define the interval in minutes
interval_minutes = 15  # Change this to your desired interval

if __name__ == "__main__":
    while True:
        # Step 1: Fetch and download the GDELT data
        zip_files = fetch_and_download_gdelt_data()
        
        # Step 2: Extract downloaded ZIP files
        extracted_files = extract_files(zip_files)
        
        # Step 3: Connect to the database and delete all rows
        try:
            connection = psycopg2.connect(conn_string)
            print("Connection to the database was successful!")
            
            # Delete all rows from the events and mentions tables
            delete_all_rows(connection)
            events_columns = [
                "globaleventid", "sqldate", "monthyear", "year", "fractiondate", 
                "actor1code", "actor1name", "actor1countrycode", "actor1knowngroupcode", 
                "actor1ethniccode", "actor1religion1code", "actor1religion2code", 
                "actor1type1code", "actor1type2code", "actor1type3code", "actor2code", 
                "actor2name", "actor2countrycode", "actor2knowngroupcode", 
                "actor2ethniccode", "actor2religion1code", "actor2religion2code", 
                "actor2type1code", "actor2type2code", "actor2type3code", "isrootevent", 
                "eventcode", "eventbasecode", "eventrootcode", "quadclass", 
                "goldsteinscale", "nummentions", "numsources", "numarticles", 
                "avgtone", "actor1geo_type", "actor1geo_fullname", 
                "actor1geo_countrycode", "actor1geo_adm1code", "actor1geo_adm2code", 
                "actor1geo_lat", "actor1geo_long", "actor1geo_featureid", 
                "actor2geo_type", "actor2geo_fullname", "actor2geo_countrycode", 
                "actor2geo_adm1code", "actor2geo_adm2code", "actor2geo_lat", 
                "actor2geo_long", "actor2geo_featureid", "actiongeo_type", 
                "actiongeo_fullname", "actiongeo_countrycode", "actiongeo_adm1code", 
                "actiongeo_adm2code", "actiongeo_lat", "actiongeo_long", 
                "actiongeo_featureid", "dateadded", "sourceurl"
            ]
            mentions_columns = [
                "globaleventid", "eventtimedate", "mentiontimedate", "mentiontype", 
                "mentionsourcename", "mentionidentifier", "sentenceid", 
                "actor1charoffset", "actor2charoffset", "actioncharoffset", 
                "inrawtext", "confidence", "mentiondoclen", "mentiondoctone", 
                "mentiondoctranslationinfo", "extras"
            ]
            # Step 4: Load the extracted data into the database
            for file_name, file_content in extracted_files.items():
                # Determine delimiter and table based on file type
                if "export" in file_name:
                    # All export files (both English and translated) use tab delimiter
                    load_data_to_db("events", file_content, events_columns, delimiter='\t')
                elif "mentions" in file_name:
                    # All mentions files are tab-delimited regardless of language
                    load_data_to_db("mentions", file_content, mentions_columns, delimiter='\t')

            connection.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Failed to connect to the database: {e}")

        # Sleep for the specified interval
        print(f"Sleeping for {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)


