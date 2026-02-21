"""
AI News Digest -- Daily AI news summarized and delivered by email.

Usage:
    python main.py              # run the full pipeline
    python main.py --dry-run    # fetch and summarize, but print to stdout instead of emailing
"""

import sys
import logging
from datetime import datetime, timezone

from config import MAX_ARTICLES_FOR_DIGEST
from fetchers import fetch_newsapi, fetch_rss
from dedup import deduplicate
from summarizer import summarize
from emailer import send_digest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ai-news-digest")


def main():
    dry_run = "--dry-run" in sys.argv
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    logger.info("=== AI News Digest -- %s ===", today)

    # Step 1: Fetch from all sources
    logger.info("Fetching from NewsAPI...")
    newsapi_articles = fetch_newsapi()

    logger.info("Fetching from RSS feeds...")
    rss_articles = fetch_rss()

    # Step 2: Combine
    all_articles = newsapi_articles + rss_articles
    logger.info(
        "Total articles fetched: %d (NewsAPI: %d, RSS: %d)",
        len(all_articles),
        len(newsapi_articles),
        len(rss_articles),
    )

    if not all_articles:
        logger.warning("No articles fetched from any source. Exiting.")
        return

    # Step 3: Deduplicate
    logger.info("Deduplicating...")
    unique_articles = deduplicate(all_articles)
    logger.info("Articles after deduplication: %d", len(unique_articles))

    # Step 4: Sort by published date (newest first) and cap
    unique_articles.sort(key=lambda a: a.get("published", ""), reverse=True)
    capped_articles = unique_articles[:MAX_ARTICLES_FOR_DIGEST]

    # Step 5: Summarize with Gemini
    logger.info("Summarizing with Gemini...")
    digest = summarize(capped_articles)
    logger.info("Digest contains %d stories.", len(digest))

    if not digest:
        logger.warning("Summarization produced no results. Exiting.")
        return

    # Step 6: Send or print
    if dry_run:
        logger.info("DRY RUN -- printing digest to stdout.")
        for i, story in enumerate(digest, 1):
            print(f"\n--- Story {i} ---")
            print(f"Title:    {story.get('title')}")
            print(f"Source:   {story.get('source')}")
            print(f"Category: {story.get('category')}")
            print(f"URL:      {story.get('url')}")
            print(f"Summary:  {story.get('summary')}")
    else:
        logger.info("Sending email...")
        success = send_digest(digest, today)
        if success:
            logger.info("Done! Digest sent successfully.")
        else:
            logger.error("Failed to send digest email.")
            sys.exit(1)


if __name__ == "__main__":
    main()
