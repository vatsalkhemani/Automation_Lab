# ai-news-digest

> Daily email with the top 10 AI stories, summarized as key takeaways.

## Status

**Shipped**

## What It Does

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

## Example Output

Each story has a factual title, category tag, and 3 bullet-point takeaways:

```
AI News Digest -- February 22, 2026 · 10 stories

🚀 Product Launch · The Hacker News
Anthropic Launches Claude Code Security for AI-Powered Vulnerability Scanning
  • Anthropic introduced Claude Code Security for its Claude Code offering.
  • The new feature scans software codebases for vulnerabilities.
  • It also suggests potential patches to address identified security flaws.

⚖️ Policy · TechCrunch
OpenAI Debated Calling Police About Suspected Canadian Shooter's Chats
  • OpenAI employees debated reporting a user's violent ChatGPT conversations.
  • The user later became a suspect in a Canadian school shooting.
  • OpenAI's internal tools flagged the chats for descriptions of gun violence.

💼 Business · CNBC
Tech Giants Commit Billions to Indian AI as New Delhi Pushes for Superpower Status
  • Major tech companies are investing billions in India's AI sector.
  • This comes as India aims to become an AI superpower.
  • Investments were highlighted at the India AI Impact Summit in New Delhi.
```

---

*Part of [Automation Lab](../README.md)*
