#!/usr/bin/env python3
import os
import sys
import json
import requests

def get_summary(text):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL", "gpt-3.5-turbo")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    url = "https://api.openrouter.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"Provide a one sentence summary of the following text:\n\n{text}"

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 60,
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")

    response_json = response.json()
    # Extract the summary from the first choice's message content
    summary = response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    return summary

def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            raise ValueError("No input provided. Expecting JSON with a 'text' key.")
        input_data = json.loads(raw_input)
        text = input_data.get("text")
        if not text:
            raise ValueError("JSON must contain a 'text' key.")

        summary = get_summary(text)
        output = {"summary": summary}
        print(json.dumps(output))
    except Exception as e:
        error = {"error": str(e)}
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
