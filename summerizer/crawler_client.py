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
        debug_print(f"\n=== RAW CRAWLER REQUEST ===")
        debug_print(f"POST http://crawler:5000/crawl with URL: {url_arg}")
        
        response = requests.post("http://crawler:5000/crawl", json={"url": url_arg}, timeout=30)
        
        debug_print(f"\n=== RAW CRAWLER RESPONSE ({response.status_code}) ===")
        debug_print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        debug_print(f"Body: {response.text}")
        
        final_result = {"mentionidentifier": url_arg, "status": []}
        final_result["status"].append(f"Crawl request sent for URL {url_arg}.")
        try:
            data = response.json()
            
            debug_print(f"\n=== PARSED CRAWLER DATA ===")
            debug_print(json.dumps(data, indent=2))
            original_result = None
            raw_content = None
            if "result" in data:
                try:
                    original_result = json.loads(data["result"])
                except Exception:
                    original_result = None
                if original_result and isinstance(original_result, dict) and "content" in original_result:
                    raw_content = original_result["content"]
                    
                    debug_print(f"\n=== CONTENT METADATA ===")
                    debug_print(f"Detected language: {original_result.get('language', 'unknown')}")
                    debug_print(f"Content length: {len(raw_content)} chars")
                    debug_print(f"Title: {original_result.get('title', 'N/A')}")
                    
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
            debug_print(f"\n=== PRE-TRANSLATION CONTENT ===")
            debug_print(f"First 500 chars: {raw_content[:500]}...")
            
            summary_input = raw_content
            final_result["status"].append(f"Content received for URL {url_arg}.")
        if raw_content:
            final_result["article_source"] = summary_input  # save the translated or original content
            
            debug_print(f"\n=== CONTENT READY FOR PROCESSING ===")
            debug_print(f"Stored article source length: {len(summary_input)} chars")
        debug_print(f"[Crawler] URL: {url_arg} - Final result:")
        debug_print(json.dumps(final_result, indent=2))
        if raw_content:
            url_completed = {
                "source": url_arg,
                "title": raw_title if raw_title else "N/A",
                "content": summary_input,
                "detected_language": data.get("detected_language", "unknown")
            }
            return url_completed
        else:
            return {"error": f"No content available for URL {url_arg}"}
    except Exception as err:
        final_result = {"mentionidentifier": url_arg, "error": f"Error calling crawler for URL {url_arg}: {err}"}
        logging.debug("Final crawler result for URL %s: %s", url_arg, json.dumps(final_result, indent=2))
        return final_result
