#!/usr/bin/env python3
import os
import sys
import json
import requests
import subprocess
import psycopg2
import psycopg2.extras
from kafka import KafkaConsumer
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
from config import ACTOR_CODE
from openai import OpenAI
import concurrent.futures

def get_summary(text):
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
    
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": os.environ.get("SITE_URL", "http://example.com"),
            "X-Title": os.environ.get("SITE_NAME", "My Site")
        },
        model=model,
        messages=[
            {"role": "user", "content": f"Provide a single sentence summary for the following content: {text}"}
        ]
    )
    return {"summary": completion.choices[0].message.content}

def get_article(aggregated_text):
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

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": os.environ.get("SITE_URL", "http://example.com"),
            "X-Title": os.environ.get("SITE_NAME", "My Site")
        },
        model=model,
        messages=[
            {"role": "user", "content": (
                f"Using the following aggregated \n{aggregated_text}\n\n"
                "Please write a comprehensive article overviewing the events of the last 15 minutes. "
                "The article should integrate each entry's event content (or its translated version), "
                "the individual LLM summary, along with the source URL and the original title."
            )}
        ]
    )
    return {"article": completion.choices[0].message.content}

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
            print(f"Dispatching {len(results)} crawler requests...\n")

            # For each row, concurrently call the crawler's HTTP endpoint for the "mentionidentifier"
            def call_crawler(url_arg):
                try:
                    response = requests.post("http://crawler:5000/crawl", json={"url": url_arg}, timeout=30)
                    final_result = {"mentionidentifier": url_arg, "status": []}
                    final_result["status"].append(f"Crawl request sent for URL {url_arg}.")
                    try:
                        data = response.json()                        
                        # Process crawler response without printing raw details                        
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
                        raw_title = None
                        if original_result and isinstance(original_result, dict) and "title" in original_result:
                            raw_title = original_result["title"]
                        final_result["status"].append("Crawler returned successfully.")
                    except Exception as e:
                        final_result["error"] = f"Error parsing crawler response: {response.text}"
                        print(json.dumps(final_result, indent=2))
                        return
                    if raw_content:
                        try:
                            detect_response = requests.post("http://libretranslate:5000/detect", data={"q": raw_content}, timeout=30)
                            detect_data = detect_response.json()
                            if isinstance(detect_data, list) and len(detect_data) > 0:
                                detected_language = detect_data[0].get("language", "unknown")
                                final_result["status"].append(f"Detected language for URL {url_arg}: {detected_language}.")
                                if detected_language != "en":
                                    final_result["status"].append(f"Non-English content detected; initiating translation for URL {url_arg}.")
                                    try:
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
                                        final_result["error"] = f"Error calling /translate for URL {url_arg} (content): {e}"
                                        translated_content = "[TRANSLATION FAILED]"
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
                                            final_result.setdefault("errors", []).append(f"Error calling /translate for URL {url_arg} (title): {e}")
                                            translated_title = "[TRANSLATION FAILED]"
                                    final_result["translation_result"] = {
                                        "translatedTitle": translated_title if translated_title is not None else "[NO TITLE]",
                                        "translatedContent": translated_content,
                                        "translatedFrom": detected_language
                                    }
                                    summary_input = translated_content
                                else:
                                    final_result["status"].append(f"Content is in English; initiating summarization for URL {url_arg}.")
                                    summary_input = raw_content
                                try:
                                    summary_result = get_summary(summary_input)
                                    final_result["LLM_summary"] = summary_result.get("summary", "[NO SUMMARY]")
                                except Exception as e:
                                    final_result.setdefault("errors", []).append(f"Error calling LLM summerizer for URL {url_arg}: {e}")
                        except Exception as e:
                            final_result.setdefault("errors", []).append(f"Error processing raw content for URL {url_arg}: {e}")
                    print(json.dumps(final_result, indent=2))
                    if raw_content:
                        final_result["article_source"] = summary_input  # save the translated or original content
                    print(json.dumps(final_result, indent=2))
                    if raw_content:
                        url_completed = {
                            "source": url_arg,
                            "title": raw_title if raw_title else "N/A",
                            "content": summary_input,
                            "LLM_summary": final_result.get("LLM_summary", "[NO SUMMARY]")
                        }
                        return url_completed
                    else:
                        return {"error": f"No content available for URL {url_arg}"}
                except Exception as err:
                    final_result = {"mentionidentifier": url_arg, "error": f"Error calling crawler for URL {url_arg}: {err}"}
                    logging.debug("Final crawler result for URL %s: %s", url_arg, json.dumps(final_result, indent=2))
                    return final_result

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(call_crawler, row.get("mentionidentifier"))
                    for row in results if row.get("mentionidentifier")
                ]
            all_results = [f.result() for f in futures]
            # Filter only the successful URL_COMPLETED objects (those that include both "LLM_summary" and "source")
            url_completed_list = [res for res in all_results if res.get("LLM_summary") and res.get("source")]
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
                except Exception as e:
                    logging.error("Error calling aggregated article LLM: %s", e)
        # Continue waiting for additional messages

if __name__ == "__main__":
    main()
