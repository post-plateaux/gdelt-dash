#!/usr/bin/env python3
import os
import asyncio
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# Automatically load environment variables from sample.env
load_dotenv(".env")

# Define a data model for the extracted content
class ArticleSummary(BaseModel):
    title: str
    summary: str

async def main():
    # Retrieve the LLM API token from your environment (assumed to be for OpenRouter)
    api_token = os.getenv("OPENROUTER_API_KEY")
    if not api_token:
        print("Please set the OPENROUTER_API_KEY environment variable.")
        return

    # Configure the LLM extraction strategy.
    # This tells Crawl4AI to use an LLM (via OpenRouter) to convert raw HTML into structured JSON.
    llm_strategy = LLMExtractionStrategy(
        provider="openrouter/google/gemini-2.0-flash-001",  # Use the OpenRouter provider with your chosen model
        api_token=api_token,
        schema=json.dumps(ArticleSummary.model_json_schema()),  # Expect a JSON that fits the ArticleSummary model
        extraction_type="schema",            # Instruct the LLM to produce structured output matching the schema
        instruction="Extract the main article title and provide a short summary of the content.",
        chunk_token_threshold=1000,           # Optional: split long content into chunks for processing
        overlap_rate=0.1,
        apply_chunking=True,
        input_format="html",                  # Send the original HTML to the LLM
        extra_args={"temperature": 0.2, "max_tokens": 500},
        verbose=True
    )

    # Create the crawler configuration that integrates our LLM extraction strategy
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS  # For this demo, bypass any caching
    )

    # Set up the browser configuration (headless mode)
    browser_config = BrowserConfig(headless=True)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Specify the target URL to crawl. The LLM will process the fetched page.
        url = "https://www.newyorker.com/news/letter-from-trumps-washington/elon-musks-revolutionary-terror"
        result = await crawler.arun(url=url, config=crawl_config)

        if result.success:
            try:
                # The extracted_content is expected to be a JSON list of article summaries
                extracted_json = json.loads(result.extracted_content)
                # Use model_validate for Pydantic V2 and iterate over the list:
                articles = [ArticleSummary.model_validate(item)
                           for item in extracted_json if not item.get('error', False)]
                if articles:
                    for article in articles:
                        print("Extracted Article Summary:")
                        print(f"Title: {article.title}")
                        print(f"Summary: {article.summary}")
                else:
                    print("No valid article summaries extracted.")
            except Exception as e:
                print("Error parsing extraction result:", e)
                print("Raw extracted content:")
                print(result.extracted_content)

            # Optionally show token usage or other debug information
            llm_strategy.show_usage()
        else:
            print("Crawl error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
