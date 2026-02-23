"""
Weekly Learning -- A deep-dive exploration of a random topic, delivered by email every Saturday.

Usage:
    python main.py              # generate and send the email
    python main.py --dry-run    # generate and print to stdout instead of emailing
"""

import random
import sys
import logging
from datetime import datetime, timezone

from config import TOPIC_CATEGORIES
from generator import generate_topic
from emailer import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("weekly-learning")


def main():
    dry_run = "--dry-run" in sys.argv
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    logger.info("=== Weekly Learning -- %s ===", today)

    # Step 1: Pick a random category
    category = random.choice(TOPIC_CATEGORIES)
    logger.info("Selected category: %s", category)

    # Step 2: Generate deep-dive article
    logger.info("Generating article with Gemini...")
    article = generate_topic(category)

    if not article:
        logger.error("Failed to generate article. Exiting.")
        sys.exit(1)

    logger.info("Topic: %s", article.get("topic", "Unknown"))

    # Step 3: Send or print
    if dry_run:
        logger.info("DRY RUN -- printing article to stdout.\n")
        print(f"Category: {article.get('category', '')}")
        print(f"Topic:    {article.get('topic', '')}\n")
        print(article.get("hook", ""))
        for section in article.get("sections", []):
            print(f"\n## {section.get('heading', '')}\n")
            print(section.get("content", ""))
        print(f"\nSurprising Fact: {article.get('surprising_fact', '')}\n")
        print("Go Deeper:")
        for item in article.get("further_reading", []):
            print(f"  -> {item}")
    else:
        logger.info("Sending email...")
        success = send_email(article, today)
        if success:
            logger.info("Done! Weekly learning email sent successfully.")
        else:
            logger.error("Failed to send email.")
            sys.exit(1)


if __name__ == "__main__":
    main()
