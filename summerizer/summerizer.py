#!/usr/bin/env python3
import os
import sys
import json
import requests
import subprocess
from kafka import KafkaConsumer, KafkaProducer
from kafka_client import create_consumer, create_producer, send_message
from db_utils import run_sql_query
import time
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
from config import ACTOR_CODE, SQL_QUERY
from crawler_client import call_crawler
from openai import OpenAI
import concurrent.futures
from datetime import datetime

def post_with_retries(url, data, timeout, retries=2):
    attempts = 0
    while attempts <= retries:
        try:
            response = requests.post(url, data=data, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            attempts += 1
            if attempts > retries:
                raise e



def is_allowed(url):
    blocked = os.environ.get("BLOCKED_DOMAINS", "")
    if blocked:
        domains = [d.strip() for d in blocked.split(",") if d.strip()]
        for domain in domains:
            if domain in url:
                return False
        return True
    return True

latest_article_text = ""





def get_summary(text, mentionsourcename=None):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL")
    if not model:
        raise ValueError("OPENROUTER_MODEL not set")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    

    summary_prompt = os.environ.get("SUMMARY_PROMPT")
    if not summary_prompt:
        raise ValueError("SUMMARY_PROMPT environment variable is not set")
    final_summary_prompt = summary_prompt.format(text=text)
    if mentionsourcename:
        final_summary_prompt += f"\nMention Source: {mentionsourcename}"

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": os.environ.get("SITE_URL", "http://example.com"),
            "X-Title": os.environ.get("SITE_NAME", "My Site")
        },
        model=model,
        messages=[
            {"role": "user", "content": final_summary_prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "refugee_summarization_extended",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "is_relevent": {
                            "type": "boolean",
                            "description": "True if the content is about refugees globally; otherwise false."
                        },
                        "who": {
                            "type": "string",
                            "description": "If is_relevent is true, provide two sentences describing who is involved."
                        },
                        "what": {
                            "type": "string",
                            "description": "If is_relevent is true, provide two sentences describing what is happening."
                        },
                        "when": {
                            "type": "string",
                            "description": "If is_relevent is true, provide two sentences describing when the events occurred."
                        },
                        "where": {
                            "type": "string",
                            "description": "If is_relevent is true, provide two sentences describing where the events occurred."
                        },
                        "why": {
                            "type": "string",
                            "description": "If is_relevent is true, provide two sentences describing why the events occurred."
                        },
                        "how": {
                            "type": "string",
                            "description": "If is_relevent is true, provide two sentences describing how the events occurred."
                        }
                    },
                    "required": ["is_relevent"],
                    "additionalProperties": False
                }
            }
        }
    )
    try:
        response_json = json.loads(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"LLM did not return valid JSON, fallback triggered: {e}")
        response_json = {
            "is_relevent": False,
            "who": "",
            "what": "",
            "when": "",
            "where": "",
            "why": "",
            "how": ""
        }
    return response_json

def get_article(aggregated_text):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_ARTICLE_MODEL") or os.environ.get("OPENROUTER_MODEL")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    if not model:
        raise ValueError("Neither OPENROUTER_ARTICLE_MODEL nor OPENROUTER_MODEL is set")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    article_prompt = os.environ.get("ARTICLE_PROMPT")
    if not article_prompt:
        raise ValueError("ARTICLE_PROMPT environment variable not set")
    final_prompt = f"Using the following aggregated text:\n{aggregated_text}\n\n{article_prompt}"

    tokens_str = os.environ.get("ARTICLE_MAX_TOKENS")
    temperature_str = os.environ.get("ARTICLE_TEMPERATURE")
    max_tokens = int(tokens_str) if tokens_str else None
    temperature = float(temperature_str) if temperature_str else None

    completion_args = dict(
        extra_headers={
            "HTTP-Referer": os.environ.get("SITE_URL", "http://example.com"),
            "X-Title": os.environ.get("SITE_NAME", "My Site")
        },
        model=model,
        messages=[
            {"role": "user", "content": final_prompt}
        ]
    )
    if max_tokens is not None:
        completion_args["max_tokens"] = max_tokens
    if temperature is not None:
        completion_args["temperature"] = temperature

    completion = client.chat.completions.create(**completion_args)
    return {"article": completion.choices[0].message.content}

def get_selected_crawlers(crawler_titles):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )
    prompt = f"Placeholder Prompt: Given the following crawlers:\n{json.dumps(crawler_titles, indent=2)}\nPlease select ten of the crawlers at random by their number. Return a JSON object with a single key \"selected_crawlers\" that is a list of the crawler numbers selected."
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": os.environ.get("SITE_URL", "http://example.com"),
            "X-Title": os.environ.get("SITE_NAME", "My Site")
        },
        model=os.environ.get("OPENROUTER_MODEL"),
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    try:
        response_json = json.loads(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"LLM did not return valid JSON for crawler selection, fallback triggered: {e}")
        response_json = {"selected_crawlers": []}
    return response_json

def main():
    print("Summerizer is waiting for 'database populated' messages from Kafka...")
    consumer = create_consumer(
        topic='database_status',
        servers=["kafka:9092"],
        group_id="summerizer_group",
        auto_offset_reset="latest",
        max_poll_interval_ms=600000
    )
    for message in consumer:
        msg = message.value.decode('utf-8')
        if msg == "database populated":
            print("Received 'database populated' message from Kafka!")
            # Retrieve SQL query from config
            query = SQL_QUERY.format(actor_code=ACTOR_CODE)


            results = run_sql_query(query)
            print("[SQL] Query Results:")
            print(json.dumps(results, indent=2))
            print(f"[Dispatch] Dispatching {len(results)} crawler requests...\n")


            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(call_crawler, row, get_summary)
                    for row in results if row.get("mentionidentifier") and is_allowed(row.get("mentionidentifier"))
                ]
            all_results = [f.result() for f in futures]
            # New LLM call to select crawlers from their titles
            crawler_titles = {}
            for idx, res in enumerate(all_results, start=1):
                if "title" in res and res["title"] != "N/A":
                    crawler_titles[idx] = res["title"]
            if crawler_titles:
                try:
                    selection_result = get_selected_crawlers(crawler_titles)
                    logging.info("Crawler selection LLM returned: %s", json.dumps(selection_result, indent=2))
                except Exception as e:
                    logging.error("Error calling crawler selection LLM: %s", e)
            else:
                logging.warning("No valid crawler titles found for selection LLM.")
            url_completed_list = [
                res for res in all_results 
                if res.get("LLM_summary") 
                and res.get("source") 
                and res["LLM_summary"].get("is_relevent", False)
            ]
            if not url_completed_list:
                logging.warning("No successful crawler results returned; skipping article generation.")
            else:
                # Convert the list of URL_COMPLETED objects to a JSON-formatted string
                aggregated_payload = json.dumps(url_completed_list, indent=2)
                logging.debug("Aggregated URL_COMPLETED payload for article generation:\n%s", aggregated_payload)
                try:
                    article_result = get_article(aggregated_payload)
                    logging.info("Aggregated Article Overview generated successfully:")
                    print("Aggregated Article Overview:")
                    print(json.dumps(article_result, indent=2))
                    global latest_article_text
                    latest_article_text = article_result.get("article", "")
                except Exception as e:
                    logging.error("Error calling aggregated article LLM: %s", e)
                    
                try:
                    # Archive the current article from article.md to ancients.md if it exists
                    try:
                        with open("content/article.md", "r", encoding="utf-8") as ad_file:
                            old_article = ad_file.read()
                    except FileNotFoundError:
                        old_article = ""
                    if old_article.strip():
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        archive_block = f"<details>\n<summary>{timestamp}</summary>\n\n{old_article}\n\n</details>\n\n"
                        try:
                            with open("content/ancients.md", "r", encoding="utf-8") as an_file:
                                used_ancients = an_file.read()
                        except FileNotFoundError:
                            used_ancients = ""
                        new_ancients = archive_block + used_ancients
                        with open("content/ancients.md", "w", encoding="utf-8") as an_file:
                            an_file.write(new_ancients)
                        logging.info("Previous article archived to content/ancients.md")
                except Exception as e:
                    logging.error("Failed to archive previous article: %s", e)
                    
                try:
                    with open("content/article.md", "w", encoding="utf-8") as md_file:
                        md_file.write(latest_article_text)
                    logging.info("Article successfully written to content/article.md")
                    producer = create_producer(servers=["kafka:9092"])
                    send_message(producer, "article_update", b"article updated")

                    logging.info("Article update complete. Pausing for 10 minutes before processing new requests.")
                    time.sleep(600)  # delay for 10 minutes
                except Exception as e:
                    logging.error("Failed to write article to content/article.md: %s", e)
        # Continue waiting for additional messages

if __name__ == "__main__":
    main()
