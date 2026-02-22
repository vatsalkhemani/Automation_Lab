# ai-news-digest

A fully automated pipeline that reads hundreds of AI articles every morning, picks the 10 that matter, and delivers a clean summary to your inbox — so you can stay current in 2 minutes instead of 2 hours.

<img width="418" height="1171" alt="Example digest email" src="https://github.com/user-attachments/assets/9ad7be3d-b9ab-4b93-8911-39ad04d9da17" />

## Status

**Shipped**

## How It Works

Every morning at 9:00 AM IST, this automation:

1. **Fetches** AI news from NewsAPI (80 articles) + 5 RSS feeds (TechCrunch, The Verge, MIT Tech Review, Ars Technica, VentureBeat)
2. **Deduplicates** by URL normalization and fuzzy title matching
3. **Curates** top 10 stories using Gemini 2.5 Flash — rewrites clickbait titles, categorizes each story, and extracts 3 key takeaways per story
4. **Emails** a clean HTML digest with bullet-point takeaways via Gmail SMTP

Resilient by design: if a source fails, the rest continue. If Gemini fails, raw descriptions are used as fallback.

## How It Runs

| | |
|---|---|
| **Schedule** | Daily at 03:30 UTC (9:00 AM IST) |
| **Manual trigger** | `workflow_dispatch` in GitHub Actions tab |
| **Entry point** | `python main.py` |
| **Dry run** | `python main.py --dry-run` |

## Architecture

```
main.py           — orchestrator, --dry-run support
├── config.py     — env vars, RSS URLs, NewsAPI query, constants
├── fetchers.py   — fetch_newsapi() + fetch_rss()
├── dedup.py      — URL normalization + fuzzy title matching
├── summarizer.py — Gemini 2.5 Flash with JSON auto-repair + fallback
└── emailer.py    — HTML email with bullet takeaways via Gmail SMTP
```

## Secrets Required

| Secret | Description | Where to get it |
|--------|-------------|-----------------|
| `NEWSAPI_KEY` | NewsAPI.org API key | [newsapi.org/register](https://newsapi.org/register) |
| `GEMINI_API_KEY` | Google Gemini API key | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `GMAIL_ADDRESS` | Gmail address to send from | Your Gmail (2FA required) |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your regular password) | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `EMAIL_RECIPIENT` | Email address to receive the digest | Any email address |

Add these in **Settings > Secrets and variables > Actions** for GitHub Actions, or in a local `.env` file.

## Local Development

```bash
cd ai-news-digest
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with your values

# Load env vars
export $(grep -v '^#' .env | xargs)

# Dry run (prints to stdout, no email)
python main.py --dry-run

# Full run (sends email)
python main.py
```

---

*Part of [Automation Lab](../README.md)*
