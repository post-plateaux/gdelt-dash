import subprocess
from kafka import KafkaProducer

def run_script(script_path):
    """Run a Python script located at script_path."""
    try:
        print(f"Running {script_path}...")
        subprocess.run(['python3', script_path], check=True)
        print(f"Successfully ran {script_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        raise  # Re-raise the exception to stop execution if an error occurs

if __name__ == "__main__":
    # List of scripts to run in order
    scripts = [
        'create_actor_type_code_table.py',
        'create_country_code_table.py',
        'create_ethnic_code_table.py',
        'create_event_code_table.py',
        'create_events_table.py',
        'create_events_translated_table.py',
        'create_fips_country_code_table.py',
        'create_goldstein_code_table.py',
        'create_known_group_code_table.py',
        'create_mentions_table.py',
        'create_mentions_translated_table.py',
        'create_religion_code_table.py'
    ]

    # Run each script
    for script in scripts:
        try:
            run_script(script)
        except subprocess.CalledProcessError:
            print("Failed to create tables, stopping execution.")
            exit(1)

    # Publish 'database_prepared' message to Kafka instead of creating a flag file
    try:
        producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
        # Send the message 'database_prepared' as a byte string to the 'database_status' topic
        future = producer.send('database_status', b'database_prepared')
        future.get(timeout=10)
        producer.flush()
        print("Kafka message sent: 'database_prepared'")
    except Exception as e:
        print(f"Error sending Kafka message: {e}")
        exit(1)
    finally:
        if 'producer' in locals():
            producer.close()
