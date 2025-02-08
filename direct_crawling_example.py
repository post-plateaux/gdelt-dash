#!/usr/bin/env python3
import os
import asyncio
import json
from dotenv import load_dotenv
import requests
from readability import Document
import subprocess
import html2text

# Automatically load environment variables from .env
load_dotenv(".env")




def main():
    url = "https://jacobin.com/2025/02/trump-musk-doge-protest-schumer"
    try:
        readability_response = requests.get(url)
        if readability_response.status_code == 200:
            doc = Document(readability_response.text)
            raw_html = doc.summary()
            print("\n\n----- Readability Extraction Output -----")
            print("Title:", doc.title())
            print("Extracted Content (HTML):")
            print(raw_html)
            
            # Convert raw HTML to Markdown using html2text
            md_converter = html2text.HTML2Text()
            md_converter.ignore_links = False  # Set to True to ignore links if desired
            md_text = md_converter.handle(raw_html)
            print("\n----- Markdown Output -----\n")
            print(md_text)
        else:
            print("Error fetching URL for Readability extraction:", readability_response.status_code)
    except Exception as e:
        print("Exception during Readability extraction:", e)
    
    # New block: Run Postlight Parser for side-by-side comparison
    try:
        print("\n----- Running Postlight Parser CLI -----\n")
        # Use npx to invoke Postlight Parser with markdown output
        cmd = ["npx", "@postlight/parser", url, "--format=markdown"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        postlight_output = result.stdout.strip()
        print("\n----- Postlight Parser Output -----\n")
        print(postlight_output)
    except Exception as e:
        print("Exception during Postlight Parser execution:", e)

if __name__ == "__main__":
    main()
