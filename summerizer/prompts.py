"""Prompt templates for the summerizer application.
All prompt texts are defined here for easy modification.
"""

SUMMARY_PROMPT = (
    "Evaluate the following content for its relevance to American conservatism and foreign policy. "
    "If a mention source is provided, use it as additional context when determining relevance. "
    "Return a JSON object with the following keys: 'is_relevent' (boolean), 'foreign_sentiment' (string), 'summary' (string), and 'quote' (string). "
    "For content closely related to Trump, the Trump administration, American foreign policy, or American conservatism, set 'is_relevent' to true; otherwise set it to false. "
    "When 'is_relevent' is true, 'foreign_sentiment' should be one of the following labels: 'very negative', 'negative', 'slightly negative', 'neutral', 'slightly positive', 'positive', or 'very positive', 'summary' should be a brief one-paragraph summary, and 'quote' should be a very short impactful extract quote (must be in English) from the content that reflects poorly on the United States. "
    "If 'is_relevent' is false, set 'foreign_sentiment' to an empty string and both 'summary' and 'quote' to an empty string. "
    "Strictly adhere to the provided JSON schema and do not include any additional text. Content: {text}"
)

ARTICLE_PROMPT = (
    "Please write an extensive, well-written, article focusing on the foreign sentiment expressed towards the United States as found in the aggregated text. "
    "Rather than reporting the events themselves, analyze and interpret the attitudes, opinions, and emotions in the content that reflect how foreign sources view U.S. policies, culture, and international relations. "
    "For each input source, provide at least one thoughtful paragraph on how the content conveys sentiments toward the U.S. along with relevant context. "
    "Use the provided quotations and attributions where appropriate. "
    "Do not include citations, a seperate process will attach a bibliography for your article. "
    "Format your output in Markdown. Ensure the markdown is well-structured with no extraneous text. "
    "Return only valid markdown. Do not include the article title in the main article_in_markdown field."
)

CRAWLER_SELECTION_PROMPT = (
    "Given the following crawlers:\n{crawler_titles}\n"
    "Select exactly 3 crawlers which are most likely to express negative sentiment concerning the United States and Trump. "
    "Do not select the same article twice if it appears more than once. Try to select articles from distinct languages if possible. "
    "The JSON object must contain one key 'selected_crawlers' whose value is an array of integers."
)
