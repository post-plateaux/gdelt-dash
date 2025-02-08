#!/bin/bash
echo "Starting internal Mercury Parser Server..."
# Change into the mercury-parser-server directory, install dependencies, and start the server in the background.
cd /mercury && npm install && npm start &

echo "Waiting 10 seconds for Mercury Parser Server to initialize..."
sleep 10

echo "Running Direct Crawling Example..."
python /app/direct_crawling_example.py
