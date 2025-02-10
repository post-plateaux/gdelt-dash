#!/usr/bin/env python3
import os
import sys
import json
import requests

# def get_summary(text):
#     api_key = os.environ.get("OPENROUTER_API_KEY")
#     model = os.environ.get("OPENROUTER_MODEL")
#     if not model:
#         raise ValueError("OPENROUTER_MODEL not set")
#     if not api_key:
#         raise ValueError("OPENROUTER_API_KEY not set")
#
#     # Use the OpenRouter endpoint based on the model specified in the environment variable
#     url = f"https://openrouter.ai/api/v1/{model}"
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }
#
#     prompt_text = (f"Please analyze the following content and provide a structured response "
#                    f"indicating if the content is on topic, a short summary (if applicable), "
#                    f"whether it has been translated, and the source language. Content: {text}")
#
#     response_schema = {
#         "type": "object",
#         "properties": {
#             "on_topic": {"type": "boolean"},
#             "summary": {"type": ["string", "null"]},
#             "translated": {"type": "boolean"},
#             "source_language": {"type": "string"}
#         },
#         "required": ["on_topic", "translated", "source_language"]
#     }
#
#     payload = {
#         "model": model,
#         "prompt": prompt_text,
#         "temperature": 0.7,
#         "max_tokens": 200,
#         "response_mime_type": "application/json",
#         "response_schema": response_schema
#     }
#
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code != 200:
#         raise Exception(f"API request failed with status {response.status_code}: {response.text}")
#
#     return response.json()

def main():
    from kafka import KafkaConsumer
    print("Summerizer is waiting for 'database populated' messages from Kafka...")
    consumer = KafkaConsumer(
        'database_status',
        bootstrap_servers=["kafka:9092"],
        auto_offset_reset="latest",
        group_id="summerizer_group"
    )
    for message in consumer:
        msg = message.value.decode('utf-8')
        if msg == "database populated":
            print("Received 'database populated' message from Kafka!")
            # Summarization functionality is temporarily disabled.
            print("Operation: Kafka update processed. (Summarization functionality commented out.)")
        # Continue waiting for additional messages

if __name__ == "__main__":
    main()
