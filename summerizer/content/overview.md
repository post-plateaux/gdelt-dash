# GDELT Data Dashboard: Automated Content Curation and Analysis

**Overview**  
This self-hosted project has evolved into a fully automated data ingestion and content curation platform built around the massive GDELT dataset. The pipeline continuously fetches live updates from GDELT every 15 minutes and not only processes structured event data but now also extracts, translates, and summarizes related web content using advanced automation techniques. The end result is a dynamic dashboard combining real-time visualizations with curated, human-readable articles that distill global events into clear insights.

**GDELT: Purpose and Evolution**  
Originally designed to map global events and sentiment, GDELT classifies events by country, actor type, and tone. Despite its ambition, the raw output can sometimes lack nuance. Recognizing this, the updated system enhances GDELT’s data through automated web scraping, translation, and summarization—bridging the gap between raw data and actionable context. By aggregating live event mentions with AI-powered content curation, the platform transforms data into engaging articles that highlight key details (the “who, what, when, where, why, and how”) of critical events worldwide.

**Technical Approach**

1. **Data Ingestion and Processing:**  
   - Every 15 minutes, a dedicated process fetches the latest GDELT data. It downloads, validates, and parses the new records into events and mentions, then loads them in batches into PostgreSQL—ensuring that only fresh, up-to-date records are present.
   - Upon successful database population, a Kafka-based signal triggers downstream services for content extraction and analysis.

2. **Automated Content Extraction:**  
   - A new crawler service automatically scrapes web pages associated with each event. It leverages a dual-approach: first attempting extraction with a specialized parser (Postlight Parser) and falling back to Readability when needed.
   - This ensures that rich, markdown-formatted content is retrieved from article URLs embedded in the dataset.

3. **Translation Service:**  
   - To handle the global nature of the data, the system integrates with LibreTranslate. Non-English web content is automatically detected and translated into English, standardizing all text for further analysis.
   - Automated language detection ensures that every piece of content is processed in the appropriate language context before summarization.

4. **Summarization and Article Creation:**  
   - A sophisticated summarization service listens for database updates and, using state-of-the-art large language models, generates concise summaries of the scraped content. It extracts key details about the events—such as who, what, when, where, why, and how—in a structured format.
   - The aggregated summaries are then compiled into a comprehensive article, creating a narrative overview of global events as they unfold. Previous articles are archived automatically, allowing a historical log of past content alongside the current overview.

5. **Visualization and Web Interface:**  
   - Grafana remains the primary visualization layer, offering real-time dashboards that query PostgreSQL for structured event data.
   - A modern web interface—built with TailwindCSS and served through Nginx—not only embeds these visualizations but now also displays the dynamically generated articles, creating a seamless blend between data and narrative.

6. **Infrastructure and Orchestration:**  
   - The entire stack is containerized with Docker Compose, orchestrating services like PostgreSQL, Grafana, Kafka, the crawler, summerizer, and LibreTranslate across isolated networks. This robust, modular design supports secure operation, rapid deployment, and ease of maintenance.
   - Advanced networking and container orchestration, including dedicated PCIe passthrough and hypervisor management, ensure high performance and secure data handling throughout the system.

**Future Directions: Evaluating GDELT’s Accuracy**  
With the new content curation layer in place, the next phase will focus on quantitatively assessing the accuracy of GDELT’s classifications. By comparing the automated narratives with the raw event data, the project aims to develop an automated accuracy grading system—providing deeper insights into both data reliability and the inherent challenges of sentiment analysis.
