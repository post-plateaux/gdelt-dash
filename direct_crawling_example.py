#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Automatically load environment variables from sample.env
load_dotenv(".env")

BASE_URL = "http://localhost:11235"
# Load the Crawl4AI API token from the environment (as defined in sample.env)
API_TOKEN = os.environ.get("CRAWL4AI_API_TOKEN")
if not API_TOKEN:
    raise ValueError("CRAWL4AI_API_TOKEN environment variable not set")

HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def direct_crawl():
    url = f"{BASE_URL}/crawl_direct"
    payload = {
        "urls": "https://fifteen.postplateaux.com/",   # URL(s) to crawl
        "priority": 10                   # Optional: a higher priority speeds up processing
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("Direct crawl result:")
        print(response.json())
    else:
        print("Error during direct crawl:", response.text)

if __name__ == "__main__":
    direct_crawl()
