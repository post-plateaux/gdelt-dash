import subprocess

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

    # Write flag file after all scripts are successfully executed
    try:
        with open('/flags/tables_created', 'w') as f:
            f.write('Tables created successfully.\n')
        print("Flag file created to indicate successful table creation.")
    except Exception as e:
        print(f"Error creating flag file: {e}")
        exit(1)
