import os
from datetime import datetime, timedelta, timezone

# --- Secrets (from environment / GitHub Secrets) ---
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "")

# --- NewsAPI settings ---
NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
NEWSAPI_QUERY = (
    '"artificial intelligence" OR "machine learning" OR "large language model" '
    'OR "generative AI" OR OpenAI OR Anthropic OR Claude OR "Google Gemini" '
    'OR GPT OR LLM OR ChatGPT OR Perplexity OR Mistral OR "AI agent" '
    'OR "AI startup" OR Midjourney OR "Stable Diffusion" OR Copilot'
)
NEWSAPI_LANGUAGE = "en"
NEWSAPI_SORT_BY = "publishedAt"
NEWSAPI_PAGE_SIZE = 80

# --- RSS Feeds ---
RSS_FEEDS = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
]

# --- Time window ---
LOOKBACK_HOURS = 28  # slightly more than 24h to catch edge-case articles


def get_time_window():
    """Return (from_dt, to_dt) as ISO 8601 strings for the last LOOKBACK_HOURS."""
    now = datetime.now(timezone.utc)
    from_dt = now - timedelta(hours=LOOKBACK_HOURS)
    return from_dt.isoformat(), now.isoformat()


# --- Gemini settings ---
GEMINI_MODEL = "gemini-2.5-flash"

# --- Email settings ---
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465  # SSL

# --- Digest settings ---
MAX_ARTICLES_FOR_DIGEST = 30
