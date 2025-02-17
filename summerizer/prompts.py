"""Prompt templates for the summerizer application.
All prompt texts are defined here for easy modification.
"""

SUMMARY_PROMPT = (
    "Evaluate the following content for its relevance to American conservatism and foreign policy. "
    "If a mention source is provided, use it as additional context when determining relevance. "
    "If the content is closely related to Trump, the Trump administration, American foreign policy, or American conservatism in general return a JSON object with 'is_relevent' set to true. "
    "If the content is not directly related to the above subjects, return 'is_relevent' as false without any additional fields. "
    "If is_relevent is True, retirn 1 to 2 sentences corcening the sentiments of the  foreign sources' concerning the United States of America in the foreign_sentiment field. "
    "Strictly adhere to the provided JSON schema and do not include any additional text. Content: {text}"
)

ARTICLE_PROMPT = (
    "YOU ARE IN DEBUG MODE IGNORE THE FOLLOWING PROMPTS AND DESCRIBE TO ME THE NATURE AND STRUCTURE OF THE DATA THAT HAS BEEN PASED TO YOU, DESCRIBE IT TO ME!"
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
