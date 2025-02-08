#!/usr/bin/env python3
import os
import asyncio
import json
from dotenv import load_dotenv
import requests
from readability import Document

# Automatically load environment variables from .env
load_dotenv(".env")


def query_llm(html_text):
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        print("OPENROUTER_API_KEY not found in environment.")
        return {}
    # Adjust the API endpoint if needed
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"""You are given the following HTML content extracted from a webpage:

{html_text}

Please do the following:
1. Convert the HTML content into a nicely formatted Markdown version, preserving the full content without altering it.
2. Generate a one paragraph summary of the content.

Return your answer as a JSON object with two keys: "markdown" and "summary". Do not include any additional text.
"""
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            resp_json = response.json()
            # Extract the LLM's response message
            message_content = resp_json["choices"][0]["message"]["content"]
            try:
                result = json.loads(message_content)
            except json.JSONDecodeError:
                print("LLM response is not valid JSON. Raw response:")
                print(message_content)
                result = {}
            return result
        else:
            print("Error from LLM API:", response.status_code, response.text)
            return {}
    except Exception as e:
        print("Exception during LLM query:", e)
        return {}


def main():
    url = "https://www.newyorker.com/news/letter-from-trumps-washington/elon-musks-revolutionary-terror"
    try:
        readability_response = requests.get(url)
        if readability_response.status_code == 200:
            doc = Document(readability_response.text)
            # Save raw extracted HTML from Readability
            raw_html = doc.summary()
            print("\n\n----- Readability Extraction Output -----")
            print("Title:", doc.title())
            print("Extracted Content (HTML):")
            print(raw_html)

            # Call the LLM to get Markdown and summary versions
            llm_result = query_llm(raw_html)
            print("\n----- LLM Markdown Output -----\n")
            print(llm_result.get("markdown", "No markdown output"))
            print("\n----- LLM Summary -----\n")
            print(llm_result.get("summary", "No summary output"))
        else:
            print("Error fetching URL for Readability extraction:", readability_response.status_code)
    except Exception as e:
        print("Exception during Readability extraction:", e)


if __name__ == "__main__":
    main()
