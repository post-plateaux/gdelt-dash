"""Prompt templates for the summerizer application.
All prompt texts are defined here for easy modification.
"""

SUMMARY_PROMPT = (
    "Evaluate the following content for its relevance to global refugee issues. "
    "If a mention source is provided, use it as additional context when determining relevance. "
    "If the content is closely related to refugees, return a JSON object with 'is_relevent' set to true "
    "and include separate entries for 'who', 'what', 'when', 'where', 'why', and 'how' "
    "(each containing two sentences that summarize that aspect). "
    "If the content is not directly about refugees, return 'is_relevent' as false without any additional fields. "
    "Strictly adhere to the provided JSON schema and do not include any additional text. Content: {text}"
)

ARTICLE_PROMPT = (
    "Please write a comprehensive article overviewing the events of the last 15 minutes. "
    "Format your output in Markdown using a clear main title (with '#' prefix), appropriate subheadings (with '##'), "
    "and bullet point lists where relevant. Ensure the markdown is well-structured with no extraneous text. "
    "Return only valid markdown."
)

CRAWLER_SELECTION_PROMPT = (
    "Given the following crawlers:\n{crawler_titles}\n"
    "Select exactly ten crawlers at random by their number and return a JSON object strictly following the provided JSON schema. "
    "The JSON object must contain one key 'selected_crawlers' whose value is an array of integers."
)
