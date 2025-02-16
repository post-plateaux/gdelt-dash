import requests
import json
import logging

DEBUG_MODE = True

def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print(*args, **kwargs)

def call_crawler(row, summary_func=None):
    url_arg = row.get("mentionidentifier")
    mention_source = row.get("mentionsourcename")
    try:
        response = requests.post("http://crawler:5000/crawl", json={"url": url_arg}, timeout=30)
        final_result = {"mentionidentifier": url_arg, "status": []}
        final_result["status"].append(f"Crawl request sent for URL {url_arg}.")
        try:
            data = response.json()
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
            raw_title = data.get("translated_title")
            if not raw_title and original_result and isinstance(original_result, dict):
                raw_title = original_result.get("title")
            final_result["status"].append("Crawler returned successfully.")
        except Exception as e:
            final_result["error"] = f"Error parsing crawler response: {response.text}"
            debug_print(json.dumps(final_result, indent=2))
            return

        if raw_content:
            summary_input = raw_content
            final_result["status"].append(f"Content received for URL {url_arg}.")
        if raw_content:
            final_result["article_source"] = summary_input  # save the translated or original content
        debug_print(f"[Crawler] URL: {url_arg} - Final result:")
        debug_print(json.dumps(final_result, indent=2))
        if raw_content:
            url_completed = {
                "source": url_arg,
                "title": raw_title if raw_title else "N/A",
                "content": summary_input,
                "language": "unknown"
            }
            return url_completed
        else:
            return {"error": f"No content available for URL {url_arg}"}
    except Exception as err:
        final_result = {"mentionidentifier": url_arg, "error": f"Error calling crawler for URL {url_arg}: {err}"}
        logging.debug("Final crawler result for URL %s: %s", url_arg, json.dumps(final_result, indent=2))
        return final_result
