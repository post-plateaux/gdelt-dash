#!/usr/bin/env python3
import os
import sys
import json
import requests
import subprocess
import psycopg2
import psycopg2.extras
from kafka import KafkaConsumer
from config import ACTOR_CODE

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
            # Define the SQL query
            SQL_QUERY = f"""WITH ref_actor_events AS (
              SELECT globaleventid
              FROM events
              WHERE actor1type1code = '{ACTOR_CODE}'
                    OR actor1type2code = '{ACTOR_CODE}'
                    OR actor1type3code = '{ACTOR_CODE}'
                    OR actor2type1code = '{ACTOR_CODE}'
                    OR actor2type2code = '{ACTOR_CODE}'
                    OR actor2type3code = '{ACTOR_CODE}'
              UNION
              SELECT globaleventid
              FROM events_translated
              WHERE actor1type1code = '{ACTOR_CODE}'
                    OR actor1type2code = '{ACTOR_CODE}'
                    OR actor1type3code = '{ACTOR_CODE}'
                    OR actor2type1code = '{ACTOR_CODE}'
                    OR actor2type2code = '{ACTOR_CODE}'
                    OR actor2type3code = '{ACTOR_CODE}'
            ),
            combined_mentions AS (
              SELECT *
              FROM mentions
              WHERE globaleventid IN (SELECT globaleventid FROM ref_actor_events)
                AND confidence >= 70
              UNION ALL
              SELECT *
              FROM mentions_translated
              WHERE globaleventid IN (SELECT globaleventid FROM ref_actor_events)
                AND confidence >= 70
            ),
            unique_mentions AS (
              SELECT DISTINCT ON (mentionidentifier) *
              FROM combined_mentions
              ORDER BY mentionidentifier, globaleventid
            )
            SELECT DISTINCT ON (globaleventid) *
            FROM unique_mentions
            ORDER BY globaleventid, mentionidentifier;
            """

            def run_sql_query(query):
                host = os.environ.get("POSTGRES_HOST", "postgres")
                dbname = os.environ.get("POSTGRES_DB")
                user = os.environ.get("POSTGRES_USER")
                password = os.environ.get("POSTGRES_PASSWORD")
                port = int(os.environ.get("POSTGRES_PORT", 5432))
                conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(query)
                result = cur.fetchall()
                cur.close()
                conn.close()
                return result

            results = run_sql_query(SQL_QUERY)
            print("SQL Query Results:")
            print(json.dumps(results, indent=2))

            # For each row, concurrently call the crawler's HTTP endpoint for the "mentionidentifier"
            import concurrent.futures
            def call_crawler(url_arg):
                print(f"Calling crawler for URL: {url_arg}")
                try:
                    # Call the crawler endpoint; internal Docker networking lets us reference it via hostname "crawler"
                    response = requests.post("http://crawler:5000/crawl", json={"url": url_arg}, timeout=30)
                    print(f"Crawler response for {url_arg}:")
                    try:
                        data = response.json()
                        # Save original result content before hiding only the main content chunk
                        original_result = None
                        raw_content = None
                        if "result" in data:
                            try:
                                original_result = json.loads(data["result"])
                            except Exception:
                                original_result = None
                            if original_result and isinstance(original_result, dict) and "content" in original_result:
                                raw_content = original_result["content"]
                                original_result["content"] = "[CONTENT HIDDEN]"
                                data["result"] = json.dumps(original_result)
                            else:
                                data["result"] = "[CONTENT HIDDEN]"
                        print(json.dumps(data, indent=2))
                        # If raw content is available, call the /detect endpoint of libretranslate
                        if raw_content:
                            try:
                                detect_response = requests.post("http://libretranslate:5000/detect", data={"q": raw_content}, timeout=30)
                                detect_data = detect_response.json()
                                if isinstance(detect_data, list) and len(detect_data) > 0:
                                    detected_language = detect_data[0].get("language", "unknown")
                                    print(f"Detected language for {url_arg}: {detected_language}")
                                    if detected_language != "en":
                                        try:
                                            # Translate content
                                            translate_content_response = requests.post(
                                                "http://libretranslate:5000/translate",
                                                data={
                                                    "q": raw_content,
                                                    "source": detected_language,
                                                    "target": "en"
                                                },
                                                timeout=30
                                            )
                                            translate_content_data = translate_content_response.json()
                                            translated_content = translate_content_data.get("translatedText", "[TRANSLATION FAILED]")
                                        except Exception as e:
                                            print(f"Error calling /translate for URL {url_arg} (content): {e}")
                                            translated_content = "[TRANSLATION FAILED]"
                                        # Translate title if available
                                        translated_title = None
                                        if raw_title:
                                            try:
                                                translate_title_response = requests.post(
                                                    "http://libretranslate:5000/translate",
                                                    data={
                                                        "q": raw_title,
                                                        "source": detected_language,
                                                        "target": "en"
                                                    },
                                                    timeout=30
                                                )
                                                translate_title_data = translate_title_response.json()
                                                translated_title = translate_title_data.get("translatedText", "[TRANSLATION FAILED]")
                                            except Exception as e:
                                                print(f"Error calling /translate for URL {url_arg} (title): {e}")
                                                translated_title = "[TRANSLATION FAILED]"
                                        translation_result = {
                                            "translatedTitle": translated_title if translated_title is not None else "[NO TITLE]",
                                            "translatedContent": translated_content,
                                            "translatedFrom": detected_language
                                        }
                                        print("Translation result:")
                                        print(json.dumps(translation_result, indent=2))
                                else:
                                    print(f"Could not detect language for {url_arg}: {detect_data}")
                            except Exception as e:
                                print(f"Error calling libretranslate /detect for URL {url_arg}: {e}")
                    except Exception as e:
                        print("Error parsing crawler response:", response.text)
                except Exception as err:
                    print(f"Error calling crawler for URL {url_arg}: {err}")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(call_crawler, row.get("mentionidentifier"))
                    for row in results if row.get("mentionidentifier")
                ]
                concurrent.futures.wait(futures)
        # Continue waiting for additional messages

if __name__ == "__main__":
    main()
