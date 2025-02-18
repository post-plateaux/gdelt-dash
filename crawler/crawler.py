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
        # Extract title directly from JSON returned by Postlight Parser CLI.
        try:
            result_data = json.loads(output["result"])
            title = result_data.get("title", "")
        except Exception as e:
            title = ""
        if output.get("result"):
            full_text = output["result"]
            print("=== DEBUG: Sending full content for language detection ===")
            print("Content snippet:", full_text[:500])
            try:
                detect_response = requests.post("http://libretranslate:5000/detect", data={"q": full_text}, timeout=30)
                detect_data = detect_response.json()
                print("=== DEBUG: Detection response:", json.dumps(detect_data, indent=2))
                if isinstance(detect_data, list) and len(detect_data) > 0:
                    detected_language = detect_data[0].get("language", "unknown")
                else:
                    detected_language = "unknown"
            except Exception as e:
                print("=== DEBUG: Detection failed with exception", e)
                detected_language = "unknown"
            output["detected_language"] = detected_language
            print("=== DEBUG: Detected language:", detected_language)
            # If the detected language is not English, translate the title
            if title and detected_language != "en":
                try:
                    translate_response = requests.post(
                        "http://libretranslate:5000/translate",
                        data={
                            "q": title,
                            "source": detected_language,
                            "target": "en",
                            "format": "text"
                        },
                        timeout=30
                    )
                    translate_data = translate_response.json()
                    print("=== DEBUG: Title translation response:", json.dumps(translate_data, indent=2))
                    translated_title = translate_data.get("translatedText", title)
                except Exception as e:
                    print("=== DEBUG: Title translation failed with exception", e)
                    translated_title = title
            else:
                translated_title = None
            output["translated_title"] = translated_title
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
