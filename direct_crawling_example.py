#!/usr/bin/env python3
import os
import asyncio
import json
from dotenv import load_dotenv
import requests
from readability import Document

# Automatically load environment variables from .env
load_dotenv(".env")

def main():
    url = "https://www.newyorker.com/news/letter-from-trumps-washington/elon-musks-revolutionary-terror"
    try:
        readability_response = requests.get(url)
        if readability_response.status_code == 200:
            doc = Document(readability_response.text)
            print("\n\n----- Readability Extraction Output -----")
            print("Title:", doc.title())
            print("Extracted Content (HTML):")
            print(doc.summary())
        else:
            print("Error fetching URL for Readability extraction:", readability_response.status_code)
    except Exception as e:
        print("Exception during Readability extraction:", e)

if __name__ == "__main__":
    main()
