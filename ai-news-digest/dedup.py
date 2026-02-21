import logging
from difflib import SequenceMatcher
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)


def _normalize_url(url: str) -> str:
    """Normalize a URL for comparison: strip query params, fragments, trailing slashes."""
    try:
        parsed = urlparse(url.lower().strip())
        normalized = urlunparse(
            (
                parsed.scheme,
                parsed.netloc.replace("www.", ""),
                parsed.path.rstrip("/"),
                "",
                "",
                "",
            )
        )
        return normalized
    except Exception:
        return url.lower().strip()


def _titles_similar(title1: str, title2: str, threshold: float = 0.75) -> bool:
    """Check if two titles are similar using SequenceMatcher ratio."""
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() >= threshold


def deduplicate(articles: list[dict]) -> list[dict]:
    """
    Remove duplicate articles by URL normalization and fuzzy title matching.
    When duplicates are found, keep the version with the longer description.
    """
    seen_urls: dict[str, int] = {}
    result: list[dict] = []

    for article in articles:
        norm_url = _normalize_url(article["url"])

        # Check 1: exact URL match
        if norm_url in seen_urls:
            existing_idx = seen_urls[norm_url]
            if len(article.get("description", "")) > len(
                result[existing_idx].get("description", "")
            ):
                result[existing_idx] = article
            continue

        # Check 2: title similarity
        is_dup = False
        for i, existing in enumerate(result):
            if _titles_similar(article["title"], existing["title"]):
                if len(article.get("description", "")) > len(
                    result[i].get("description", "")
                ):
                    result[i] = article
                is_dup = True
                break

        if not is_dup:
            seen_urls[norm_url] = len(result)
            result.append(article)

    dedup_count = len(articles) - len(result)
    if dedup_count > 0:
        logger.info(
            "Deduplication removed %d articles (%d -> %d).",
            dedup_count,
            len(articles),
            len(result),
        )

    return result
