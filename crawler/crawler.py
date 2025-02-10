#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import requests
import html2text
from readability import Document
import uvicorn
import sys
import json
from dotenv import load_dotenv
import os

# Automatically load environment variables from .env
load_dotenv(".env")

app = FastAPI(title="Crawler Service", description="Endpoint to crawl a given URL.")

class CrawlRequest(BaseModel):
    url: str

def crawl_url(url: str) -> dict:
    output = {}
    parser_success = False

    # Attempt to use Postlight Parser CLI
    try:
        print("----- Running Postlight Parser CLI -----")
        cmd = ["postlight-parser", url, "--format=markdown"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        postlight_output = result.stdout.strip()
        if postlight_output:
            parser_success = True
            output["source"] = "Postlight"
            output["result"] = postlight_output
        else:
            output["postlight_warning"] = "Postlight returned empty output."
    except Exception as e:
        output["postlight_exception"] = str(e)

    # Fallback to Readability extraction if needed
    if not parser_success:
        try:
            print("----- Falling Back to Readability Extraction -----")
            response = requests.get(url)
            if response.status_code == 200:
                doc = Document(response.text)
                raw_html = doc.summary()
                md_converter = html2text.HTML2Text()
                md_converter.ignore_links = False
                md_text = md_converter.handle(raw_html)
                output["source"] = "Readability"
                output["result"] = md_text
            else:
                output["readability_error"] = f"HTTP status code: {response.status_code}"
        except Exception as e:
            output["readability_exception"] = str(e)
    return output

@app.post("/crawl")
def crawl_endpoint(request: CrawlRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="No URL provided.")
    result = crawl_url(request.url)
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        uvicorn.run(app, host="0.0.0.0", port=5000)
    elif len(sys.argv) > 1:
        url = sys.argv[1]
        result = crawl_url(url)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python crawler.py --server OR python crawler.py <URL>")
        sys.exit(1)
