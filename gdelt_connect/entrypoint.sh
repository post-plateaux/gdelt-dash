#!/bin/bash

echo "🔵 Waiting for tables to be created..."
while [ ! -f /flags/tables_created ]; do
  sleep 5
done

echo "🚀 Tables verified - starting GDELT connector..."
exec python -u fetch_gdelt_and_upload.py
