"""Prompt templates for the summerizer application.
All prompt texts are defined here for easy modification.
"""

SUMMARY_PROMPT = (
    "Evaluate the following content for its relevance to American conservatism and foreign policy. "
    "If a mention source is provided, use it as additional context when determining relevance. "
    "Return a JSON object with the following keys: 'is_relevent' (boolean), 'foreign_sentiment' (number), 'summary' (string), and 'quote' (string). "
    "For content closely related to Trump, the Trump administration, American foreign policy, or American conservatism, set 'is_relevent' to true; otherwise set it to false. "
    "When 'is_relevent' is true, 'foreign_sentiment' must be one of the following numbers: -3 (very negative), -2 (negative), -1 (slightly negative), 0 (neutral), 1 (slightly positive), 2 (positive), or 3 (very positive), 'summary' should be a brief 1 prarapgraph summary, and 'quote' should be a very short impactful extract quote (must be in English) from the content that reflects the overall sentiment. "
    "If 'is_relevent' is false, set 'foreign_sentiment' to 0 and both 'summary' and 'quote' to an empty string. "
    "Strictly adhere to the provided JSON schema and do not include any additional text. Content: {text}"
)

ARTICLE_PROMPT = (
    "Please write a comprehensive article focusing on the foreign sentiment expressed towards the United States as found in the aggregated text. "
    "Rather than reporting the events themselves, analyze and interpret the attitudes, opinions, and emotions in the content that reflect how foreign sources view U.S. policies, culture, and international relations. "
    "For each source, provide thoughtful discussion on how the content conveys sentiments toward the U.S. along with relevant context. "
    "Include a well-considered introduction and conclusion that ties the diverse perspectives into a coherent narrative, and use in-text hyperlinks, numbered citations, and attributions where appropriate. "
    "Format your output in Markdown using a clear main title (with '#' prefix) and bullet point lists where relevant. Ensure the markdown is well-structured with no extraneous text. "
    "Return only valid markdown."
)

CRAWLER_SELECTION_PROMPT = (
    "Given the following crawlers:\n{crawler_titles}\n"
    "Select exactly 15 crawlers which are most likely to express negative sentiment concerning the United States and Trump. "
    "Do not select the same article twice if it appears more than once. Try to select articles from distinct languages if possible. "
    "The JSON object must contain one key 'selected_crawlers' whose value is an array of integers."
)
