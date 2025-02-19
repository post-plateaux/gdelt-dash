import os
import psycopg2
import pandas as pd
import traceback
import requests  # Added
import io        # Added
import zipfile   # Added
import time      # Added
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaProducer

def wait_for_table(cursor, table_name, timeout=60):
    """Wait for a table to exist in the database."""
    start = time.time()
    while time.time() - start < timeout:
        cursor.execute("SELECT to_regclass(%s);", (table_name,))
        result = cursor.fetchone()
        if result and result[0]:
            print(f"Table '{table_name}' exists.")
            return
        time.sleep(2)
    raise Exception(f"Timeout waiting for table '{table_name}' to exist.")

# Global counter for rows padded
PADDING_COUNT = 0

# Retrieve database connection details
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT', '5432')  # Default to '5432' if not set

# Create a connection string
conn_string = f"dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}' port='{db_port}'"

# Data directory
data_dir = "./data"
batch_size = 2000  # Number of rows to insert in a single batch

def fetch_and_download_gdelt_data():
    """Fetch and download GDELT data from both English and Translation sources"""
    print("\n" + "="*50)
    print(f"🛜 DOWNLOADING DATA FROM GDELT SOURCES [{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}]")
    sources = [
        ("MAIN", "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"),
        ("TRANSLATION", "http://data.gdeltproject.org/gdeltv2/lastupdate-translation.txt")
    ]
    zip_files = []
    for source_type, url in sources:
        try:
            print(f"\n🔎 CHECKING {source_type} SOURCE")
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            urls = [line.split()[-1] for line in data.splitlines() 
                   if any(x in line for x in ['export', 'mentions'])]
            
            print(f"📥 FOUND {len(urls)} FILES IN {source_type} SOURCE")
            for file_url in urls:
                with requests.get(file_url, stream=True) as r:
                    r.raise_for_status()
                    zip_files.append(io.BytesIO(r.content))
                filename = file_url.split('/')[-1]
                print(f"✅ DOWNLOAD SUCCESS: {filename.upper()}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading from {url}: {e}")
    return zip_files

def extract_files(zip_files):
    """Extract files from in-memory ZIP files and return their contents."""
    print("\n" + "📦"*20)
    print(f"🧹 EXTRACTING FILES FROM {len(zip_files)} ARCHIVES")
    extracted_files = {}
    for i, zip_file in enumerate(zip_files, 1):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                extracted_files[file_name] = zip_ref.read(file_name)
                print(f"📄 EXTRACTED: {file_name.upper()}")
    print(f"🚀 TOTAL EXTRACTED FILES: {len(extracted_files)}")
    return extracted_files

def validate_and_parse_row(row, expected_columns, delimiter):
    global PADDING_COUNT
    fields = row.strip().split(delimiter)
    fields = [None if field == "" else field for field in fields]
    if len(fields) < expected_columns:
        missing = expected_columns - len(fields)
        PADDING_COUNT += 1
        fields.extend(['' for _ in range(missing)])
    if len(fields) == expected_columns:
        return fields
    else:
        raise ValueError(f"Expected {expected_columns} fields but got {len(fields)}. Fields: {fields}. Raw row: {row}")

def load_data_to_db(table_name, file_content, columns, delimiter=','):
    """Load data from in-memory file content into the database."""
    global PADDING_COUNT
    PADDING_COUNT = 0
    try:
        # Connect to the database
        connection = psycopg2.connect(conn_string)
        cursor = connection.cursor()

        print(f"Loading data for table '{table_name}'")
        # Decode content and count total rows in file
        decoded_content = file_content.decode('utf-8')
        all_rows = decoded_content.strip().splitlines()
        print(f"Total rows in file: {len(all_rows)}")

        # Validate rows and build a list of valid rows
        valid_rows = []
        failed_validation_count = 0
        max_printed_validation_errors = 5
        printed_validation_errors = 0
        for line_number, row in enumerate(all_rows, start=1):
            try:
                parsed = validate_and_parse_row(row, len(columns), delimiter)
                valid_rows.append(parsed)
            except Exception as e:
                failed_validation_count += 1
                if printed_validation_errors < max_printed_validation_errors:
                    print(f"Validation error on line {line_number}: {e}")
                    printed_validation_errors += 1
                elif printed_validation_errors == max_printed_validation_errors:
                    print("Further validation errors suppressed.")
                    printed_validation_errors += 1
        total_valid = len(valid_rows)
        print(f"Total valid rows: {total_valid} (skipped {failed_validation_count} invalid rows)")
        if PADDING_COUNT:
            print(f"DEBUG: Padding was necessary on {PADDING_COUNT} row(s).")
            PADDING_COUNT = 0  # reset for next file

        successful_inserts_total = 0
        for i in range(0, total_valid, batch_size):
            batch = valid_rows[i:i+batch_size]
            successful_inserts_total += insert_batch(cursor, table_name, columns, batch)

        failed_inserts = total_valid - successful_inserts_total
        print(f"{successful_inserts_total} of {total_valid} valid rows successfully inserted; {failed_inserts} rows failed to insert")

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
    columns_str = ', '.join(columns)
    values_placeholders = ', '.join(['%s'] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_placeholders})"
    try:
        cursor.executemany(insert_query, batch)
        cursor.connection.commit()  # commit on successful batch insertion
        print(f"Inserted a batch of {len(batch)} rows into {table_name}")
        return len(batch)
    except Exception as e:
        print(f"Error inserting batch: {e}. Attempting row-by-row insertion.")
        cursor.connection.rollback()  # roll back to clear error state
        successful_inserts = 0
        for r in batch:
            try:
                cursor.execute(insert_query, r)
                cursor.connection.commit()
                successful_inserts += 1
            except Exception as single_e:
                print(f"Failed to insert row {r}: {single_e}")
                cursor.connection.rollback()  # clear error state before next row
        print(f"Inserted {successful_inserts} out of {len(batch)} rows individually into {table_name}")
        return successful_inserts

def delete_all_rows(conn):
    """Delete all rows from the events and mentions tables."""
    cursor = conn.cursor()
    try:
        tables_to_delete = ['events', 'mentions', 'events_translated', 'mentions_translated']
        
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
    print("\n🔵 GDELT CONNECT SERVICE INITIALIZED 🔵\n")

    # Wait for the 'database_prepared' message from Kafka before proceeding
    consumer = KafkaConsumer(
        'database_status',
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='earliest',
        group_id='gdelt_connect_group'
    )
    print("Waiting for 'database_prepared' message from Kafka...")
    for message in consumer:
        if message.value.decode('utf-8') == 'database_prepared':
            print("Received 'database_prepared' message from Kafka!")
            break
    consumer.close()

    # Verify database connection first
    try:
        test_conn = psycopg2.connect(conn_string)
        test_conn.close()
        print("✅ DATABASE CONNECTION VERIFIED")
    except Exception as e:
        print(f"❌ DATABASE CONNECTION FAILED: {str(e).upper()}")
        exit(1)
    
    while True:
        cycle_start = datetime.utcnow()
        try:
            print("\n" + "="*50)
            print(f"🚀 STARTING PROCESSING CYCLE AT {cycle_start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # Step 1: Fetch and download the GDELT data.
            print("\nInitiating GDELT data download...")
            zip_files = fetch_and_download_gdelt_data()
            
            # Step 2: Extract downloaded ZIP files
            extracted_files = extract_files(zip_files)
            
            # Step 3: Connect to the database and delete all rows
            connection = psycopg2.connect(conn_string)
            print("Connection to the database was successful!")
            
            # Check that all required tables exist
            cursor = connection.cursor()
            required_tables = ["events", "mentions", "events_translated", "mentions_translated"]
            for tbl in required_tables:
                wait_for_table(cursor, tbl)
            cursor.close()
            
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
                    table_name = "events_translated" if "translation" in file_name else "events"
                    load_data_to_db(table_name, file_content, events_columns, delimiter='\t')
                    print(f"{'TRANSLATED' if 'translation' in file_name else 'ENGLISH'} EXPORT DATASET INSERTED SUCCESSFULLY")
                elif "mentions" in file_name:
                    table_name = "mentions_translated" if "translation" in file_name else "mentions"
                    load_data_to_db(table_name, file_content, mentions_columns, delimiter='\t')
                    print(f"{'TRANSLATED' if 'translation' in file_name else 'ENGLISH'} MENTIONS DATASET INSERTED SUCCESSFULLY")

            connection.close()
            print("Connection closed.")

            # Send Kafka message "database populated" after data insertion cycle
            try:
                producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
                producer.send('database_status', b'database populated').get(timeout=10)
                print("Kafka message sent: 'database populated'")
            except Exception as e:
                print(f"Error sending Kafka message: {e}")
            finally:
                if 'producer' in locals():
                    producer.close()
            
            print("\n" + "✅"*20)
            print(f"💾 SUCCESSFULLY LOADED {len(extracted_files)} DATASETS:")
            print(f"  - Events (EN):       {'✅' if any('export' in f and 'translation' not in f for f in extracted_files) else '❌'}")
            print(f"  - Events (Translated): {'✅' if any('translation' in f and 'export' in f for f in extracted_files) else '❌'}")
            print(f"  - Mentions (EN):    {'✅' if any('mentions' in f and 'translation' not in f for f in extracted_files) else '❌'}")
            print(f"  - Mentions (Translated): {'✅' if any('translation' in f and 'mentions' in f for f in extracted_files) else '❌'}")
            
            duration = (datetime.utcnow() - cycle_start).total_seconds()
            print(f"\n⏱️  CYCLE COMPLETED IN {duration:.2f} SECONDS")

        except Exception as e:
            print(f"\n❌ CRITICAL FAILURE: {str(e).upper()}")
            traceback.print_exc()
            
        finally:
            elapsed = (datetime.utcnow() - cycle_start).total_seconds()
            cycle_duration = interval_minutes * 60
            sleep_time = max(0, cycle_duration - elapsed)
            next_run = datetime.utcnow() + timedelta(seconds=sleep_time)
            print(f"\n⏳ NEXT UPDATE AT {next_run.strftime('%H:%M:%S UTC')} (in {sleep_time:.2f} seconds)")
            print("="*50 + "\n")
            time.sleep(sleep_time)


