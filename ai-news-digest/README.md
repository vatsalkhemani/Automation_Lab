# ai-news-digest

> Daily email with a concise summary of AI news from the last 24 hours.

## Status

**Shipped**

## What It Does

Every morning, this automation:

1. **Fetches** AI news from two sources:
   - **NewsAPI** — searches recent articles by AI-related keywords
   - **RSS feeds** — pulls from TechCrunch AI, The Verge AI, MIT Tech Review, Ars Technica, and VentureBeat AI
2. **Deduplicates** overlapping articles (by URL and title similarity)
3. **Summarizes** using Google Gemini — selects the top 8-12 stories, categorizes them, and writes concise summaries
4. **Emails** a clean HTML digest via Gmail SMTP

If any source fails, the pipeline continues with whatever is available. If Gemini fails, raw article descriptions are used as a fallback.

## How It Runs

- **Trigger:** GitHub Actions daily cron at 11:00 UTC (6:00 AM ET)
- **Manual trigger:** Available via `workflow_dispatch` in the Actions tab
- **Entry point:** `python main.py`
- **Dry run:** `python main.py --dry-run` (prints digest to stdout, no email sent)

## Architecture

```
main.py           — orchestrator
├── config.py     — env vars, constants, RSS feed URLs
├── fetchers.py   — fetch_newsapi() + fetch_rss()
├── dedup.py      — URL normalization + fuzzy title matching
├── summarizer.py — Gemini summarization with fallback
└── emailer.py    — HTML email via Gmail SMTP
```

## Secrets Required

| Secret | Description | Where to get it |
|--------|-------------|-----------------|
| `NEWSAPI_KEY` | NewsAPI.org API key | [newsapi.org/register](https://newsapi.org/register) |
| `GEMINI_API_KEY` | Google Gemini API key | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `GMAIL_ADDRESS` | Gmail address to send from | Your Gmail (must have 2FA enabled) |
| `GMAIL_APP_PASSWORD` | Gmail App Password | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `EMAIL_RECIPIENT` | Email address to receive the digest | Any email address |

For GitHub Actions: add these in **Settings > Secrets and variables > Actions**.

For local development: copy `.env.example` to `.env` and fill in values.

## Local Development

```bash
cd ai-news-digest
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with your API keys

# Load env vars (Linux/Mac)
export $(grep -v '^#' .env | xargs)

# Load env vars (Windows PowerShell)
# Get-Content .env | Where-Object { $_ -notmatch '^#' -and $_ -match '=' } | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v) }

# Dry run (fetch + summarize, print to stdout)
python main.py --dry-run

# Full run (sends email)
python main.py
```

## Configuration

Key settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `LOOKBACK_HOURS` | 28 | How far back to look for articles (slightly >24h for safety) |
| `NEWSAPI_PAGE_SIZE` | 50 | Max articles to fetch from NewsAPI per request |
| `MAX_ARTICLES_FOR_DIGEST` | 20 | Cap on articles sent to Gemini for summarization |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model for summarization |
| `RSS_FEEDS` | 5 feeds | List of RSS feed URLs to scrape |

## Example Output

The email includes a dark header, categorized stories with icons, and a clean layout:

```
AI News Digest — February 21, 2026 · 10 stories

🚀 Product Launch · TechCrunch
OpenAI Launches GPT-5 with Real-Time Reasoning
OpenAI released GPT-5 today, featuring real-time chain-of-thought
reasoning and multimodal capabilities. The model is available via
API starting at $15/1M tokens.

🔬 Research · MIT Tech Review
DeepMind Achieves New Milestone in Protein Folding
Google DeepMind published results showing AlphaFold 3 can now
predict protein-drug interactions with 95% accuracy...
```

---

*Part of [Automation Lab](../README.md)*
