#!/bin/bash
echo "Starting Crawler server..."
python /app/crawler.py --server &
pid=$!
sleep 5
echo "Crawler server has started and is ready."
wait $pid
