#!/bin/bash

# entrypoint.sh

# Wait until the flag file exists
while [ ! -f /flags/tables_created ]; do
  echo "Waiting for tables to be created..."
  sleep 5
done

echo "Tables have been created. Starting gdelt_connect..."

# Run the main script
exec python fetch_gdelt_and_upload.py
