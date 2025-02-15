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

    if parser_success:
        # Extract title from markdown result; use the first line starting with "# "
        title = ""
        for line in output["result"].splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if title:
            try:
                detect_response = requests.post("http://libretranslate:5000/detect", data={"q": title}, timeout=30)
                detect_data = detect_response.json()
                if isinstance(detect_data, list) and len(detect_data) > 0:
                    detected_language = detect_data[0].get("language", "unknown")
                else:
                    detected_language = "unknown"
            except Exception as e:
                detected_language = "unknown"
            output["detected_language"] = detected_language
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
