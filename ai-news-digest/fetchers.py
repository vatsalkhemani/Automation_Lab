import re
import logging
from datetime import datetime, timezone

import requests
import feedparser

from config import (
    NEWSAPI_KEY,
    NEWSAPI_BASE_URL,
    NEWSAPI_QUERY,
    NEWSAPI_LANGUAGE,
    NEWSAPI_SORT_BY,
    NEWSAPI_PAGE_SIZE,
    RSS_FEEDS,
    get_time_window,
)

logger = logging.getLogger(__name__)


def fetch_newsapi() -> list[dict]:
    """Fetch AI news articles from NewsAPI /v2/everything endpoint."""
    if not NEWSAPI_KEY:
        logger.warning("NEWSAPI_KEY not set, skipping NewsAPI fetch.")
        return []

    from_dt, to_dt = get_time_window()
    params = {
        "q": NEWSAPI_QUERY,
        "from": from_dt,
        "to": to_dt,
        "language": NEWSAPI_LANGUAGE,
        "sortBy": NEWSAPI_SORT_BY,
        "pageSize": NEWSAPI_PAGE_SIZE,
        "apiKey": NEWSAPI_KEY,
    }

    try:
        response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            logger.error(
                "NewsAPI returned status: %s -- %s",
                data.get("status"),
                data.get("message"),
            )
            return []

        articles = []
        for item in data.get("articles", []):
            if item.get("title") == "[Removed]":
                continue
            articles.append(
                {
                    "title": item.get("title", "").strip(),
                    "url": item.get("url", "").strip(),
                    "source": item.get("source", {}).get("name", "Unknown"),
                    "published": item.get("publishedAt", ""),
                    "description": (item.get("description") or "").strip(),
                }
            )

        logger.info("NewsAPI returned %d articles.", len(articles))
        return articles

    except requests.RequestException as e:
        logger.error("NewsAPI request failed: %s", e)
        return []


def fetch_rss() -> list[dict]:
    """Fetch AI news articles from curated RSS feeds."""
    from_dt_str, _ = get_time_window()
    from_dt = datetime.fromisoformat(from_dt_str)

    all_articles = []

    for feed_info in RSS_FEEDS:
        feed_name = feed_info["name"]
        feed_url = feed_info["url"]
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(
                    "RSS feed '%s' returned an error: %s",
                    feed_name,
                    feed.bozo_exception,
                )
                continue

            count = 0
            for entry in feed.entries:
                published_parsed = entry.get("published_parsed") or entry.get(
                    "updated_parsed"
                )
                if published_parsed:
                    entry_dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                    if entry_dt < from_dt:
                        continue
                    published_str = entry_dt.isoformat()
                else:
                    published_str = ""

                description = entry.get("summary", "") or ""
                description = re.sub(r"<[^>]+>", "", description).strip()
                if len(description) > 500:
                    description = description[:500] + "..."

                all_articles.append(
                    {
                        "title": entry.get("title", "").strip(),
                        "url": entry.get("link", "").strip(),
                        "source": feed_name,
                        "published": published_str,
                        "description": description,
                    }
                )
                count += 1

            logger.info("RSS feed '%s' returned %d recent articles.", feed_name, count)

        except Exception as e:
            logger.error("Failed to parse RSS feed '%s': %s", feed_name, e)
            continue

    logger.info("Total RSS articles: %d", len(all_articles))
    return all_articles
