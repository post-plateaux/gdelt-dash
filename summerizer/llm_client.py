import os
import json
import logging
from openai import OpenAI
from prompts import SUMMARY_PROMPT, ARTICLE_PROMPT, CRAWLER_SELECTION_PROMPT

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
    
    final_summary_prompt = SUMMARY_PROMPT.format(text=text)
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
    
    final_prompt = f"Using the following aggregated text:\n{aggregated_text}\n\n{ARTICLE_PROMPT}"
    
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
    prompt = CRAWLER_SELECTION_PROMPT.format(crawler_titles=json.dumps(crawler_titles, indent=2))
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": os.environ.get("SITE_URL", "http://example.com"),
            "X-Title": os.environ.get("SITE_NAME", "My Site")
        },
        model=os.environ.get("OPENROUTER_MODEL"),
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "crawler_selection",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "selected_crawlers": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of selected crawler numbers"
                        }
                    },
                    "required": ["selected_crawlers"],
                    "additionalProperties": False
                }
            }
        }
    )
    try:
        response_json = json.loads(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"LLM did not return valid JSON for crawler selection, fallback triggered: {e}")
        response_json = {"selected_crawlers": []}
    return response_json
