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
from file_manager import archive_article, write_article
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
from config import config
from crawler_client import call_crawler
from llm_client import get_summary, get_article, get_selected_crawlers
from get_translation import get_translation
import concurrent.futures
from datetime import datetime
TESTING_MODE = True
# Helper: pause for user confirmation if in testing mode.
def pause_for_testing(step):
    if TESTING_MODE:
        input(f"\n[TEST MODE] About to {step}. Press Enter to continue...")

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
            pause_for_testing("run SQL query")
            # Retrieve SQL query from config
            query = config.SQL_QUERY.format(actor_code=config.ACTOR_CODE)


            results = run_sql_query(query)
            print("[SQL] Query Results:")
            print(json.dumps(results, indent=2))
            pause_for_testing("dispatch crawler requests")
            print(f"[Dispatch] Dispatching {len(results)} crawler requests...\n")


            filtered_results = [row for row in results if row.get("mentionidentifier") and is_allowed(row.get("mentionidentifier"))]
            if TESTING_MODE:
                filtered_results = filtered_results[:2]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(call_crawler, row)
                    for row in filtered_results
                ]
            all_results = [f.result() for f in futures]
            pause_for_testing("prepare LLM crawler selection")
            # New LLM call to select crawlers from their titles
            crawler_titles = {}
            for idx, res in enumerate(all_results, start=1):
                if "title" in res and res["title"] != "N/A":
                    crawler_titles[idx] = res["title"]
            if crawler_titles:
                print("Passing to selection LLM, full JSON:", json.dumps(crawler_titles, indent=2))
                try:
                    selection_result = get_selected_crawlers(crawler_titles)
                    logging.info("Crawler selection LLM returned: %s", json.dumps(selection_result, indent=2))
                except Exception as e:
                    logging.error("Error calling crawler selection LLM: %s", e)
                    selection_result = {}
            else:
                logging.warning("No valid crawler titles found for selection LLM.")
                selection_result = {}

            selected_results = []
            if selection_result.get("selected_crawlers"):
                for idx in selection_result["selected_crawlers"]:
                    # idx is 1-based index
                    res = all_results[idx - 1]
                    try:
                        translated_content = get_translation(res["content"])
                        summary = get_summary(translated_content)
                    except Exception as e:
                        logging.error("Error calling translation/summarization LLM for selected result %s: %s", idx, e)
                        summary = {"is_relevent": False}
                        translated_content = res["content"]
                    res["translated_content"] = translated_content
                    res["LLM_summary"] = summary
                    selected_results.append(res)
            else:
                logging.warning("No crawlers selected by the crawler selection LLM.")

            pause_for_testing("aggregate selected results for article generation")
            url_completed_list = selected_results
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
                    archive_article()
                except Exception as e:
                    logging.error("Archiving article failed: %s", e)

                try:
                    write_article(latest_article_text)
                except Exception as e:
                    logging.error("Writing article failed: %s", e)
    
                pause_for_testing("finalize article update and send Kafka message")
                producer = create_producer(servers=["kafka:9092"])
                send_message(producer, "article_update", b"article updated")
                logging.info("Article update complete. Pausing for 10 minutes before processing new requests.")
                time.sleep(600)  # delay for 10 minutes
        # Continue waiting for additional messages

if __name__ == "__main__":
    main()
