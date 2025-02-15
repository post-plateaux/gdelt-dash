import logging
from datetime import datetime

def archive_article(article_path="content/article.md", ancients_path="content/ancients.md"):
    """
    Reads the current article from 'article_path' and archives it by prepending
    an archive block (with timestamp) to 'ancients_path'.
    """
    try:
        with open(article_path, "r", encoding="utf-8") as ad_file:
            old_article = ad_file.read()
    except FileNotFoundError:
        old_article = ""
    except Exception as e:
        logging.error("Error reading %s: %s", article_path, e)
        old_article = ""
    
    if old_article.strip():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        archive_block = f"<details>\n<summary>{timestamp}</summary>\n\n{old_article}\n\n</details>\n\n"
        try:
            try:
                with open(ancients_path, "r", encoding="utf-8") as an_file:
                    used_ancients = an_file.read()
            except FileNotFoundError:
                used_ancients = ""
            new_ancients = archive_block + used_ancients
            with open(ancients_path, "w", encoding="utf-8") as an_file:
                an_file.write(new_ancients)
            logging.info("Previous article archived to %s", ancients_path)
        except Exception as e:
            logging.error("Failed to archive previous article: %s", e)

def write_article(new_article_text, article_path="content/article.md"):
    """
    Writes the provided new_article_text into 'article_path'.
    """
    try:
        with open(article_path, "w", encoding="utf-8") as md_file:
            md_file.write(new_article_text)
        logging.info("Article successfully written to %s", article_path)
    except Exception as e:
        logging.error("Failed to write article to %s: %s", article_path, e)
        raise e
