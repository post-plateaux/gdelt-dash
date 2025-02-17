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
    "Please write a comprehensive article overviewing the content you have been provided. "
    "The overarching theme of the article should be foreign sentiment concerning the United States. "
    "Compose at least one to two full and well thought out paragraph for each of the input sources you have recieved, and include a well thought out and carefully considered introsuction and conclusion paragraph which ties everything toegther, adding extra well thought out content where necessary to transition topics. "
    "The article should be coheasive, ahev good flow, and follow best writing practices. "
    "The article should link to the full origional source url. The name of the source, and the source langauage with a *translated from...* style statemnt. "
    "The article should flow naturally from one subject source to the next, without major interruptions to flow, and include both in text hyprlinks, in text numbered sources, and numbered citations at the end of the article. "
    "Format your output in Markdown using a clear main title (with '#' prefix), appropriate subheadings (with '##'), "
    "and bullet point lists where relevant. Ensure the markdown is well-structured with no extraneous text. "
    "Return only valid markdown."
)

CRAWLER_SELECTION_PROMPT = (
    "Given the following crawlers:\n{crawler_titles}\n"
    "Select exactly 15 crawlers which are most likely to express negative sentiment concerning the United States and Trump. "
    "The JSON object must contain one key 'selected_crawlers' whose value is an array of integers."
)
