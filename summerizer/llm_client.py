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
                            "description": "True if the content is about foreign sentiment; otherwise false."
                        },
                        "foreign_sentiment": {
                            "type": "integer",
                            "enum": [-3, -2, -1, 0, 1, 2, 3],
                            "description": "A numerical representation: -3 very negative, -2 negative, -1 slightly negative, 0 neutral, 1 slightly positive, 2 positive, 3 very positive."
                        },
                        "summary": {
                            "type": "string",
                            "description": "A concise one parapgraph summary of the content when relevant, or an empty string otherwise."
                        },
                        "quote": {
                            "type": "string",
                            "description": "An extract quote from the content that reflects the overall sentiment, or an empty string if not relevant."
                        }
                    },
                    "required": ["is_relevent", "foreign_sentiment", "summary", "quote"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    try:
        print("DEBUG: Raw LLM response:", completion)
        if not completion.choices or not completion.choices[0].message or not completion.choices[0].message.content:
            raise Exception("LLM response missing choices or message content")
        print("DEBUG: Full LLM response content:", completion.choices[0].message.content)
        response_json = json.loads(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"LLM did not return valid JSON, fallback triggered: {e}")
        response_json = {
            "is_relevent": False,
            "foreign_sentiment": 0,
            "summary": "",
            "quote": ""
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
    
    try:
        completion = client.chat.completions.create(**completion_args)
        if not completion.choices or len(completion.choices) == 0:
            logging.error("LLM returned no choices. Full response: %s", completion)
            raise Exception("LLM returned no choices.")
        article_text = completion.choices[0].message.content
    except Exception as e:
        logging.error("Error calling aggregated article LLM: %s", e)
        raise e
    
    return {"article": article_text}

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
