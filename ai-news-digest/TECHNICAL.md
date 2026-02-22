# Technical Deep Dive: ai-news-digest

A plain-English explanation of how this automation works, why it's built this way, and the tradeoffs involved.

---

## The Problem

Keeping up with AI news is exhausting. Dozens of sources publish hundreds of articles daily — most are noise. This automation reads everything, picks what matters, and delivers a 2-minute summary to your inbox every morning.

## How It Works (End-to-End)

```
  [NewsAPI]     [RSS Feeds]
      \             /
       \           /
     1. FETCH articles
            |
     2. DEDUPLICATE
            |
     3. SUMMARIZE (Gemini)
            |
     4. EMAIL (Gmail SMTP)
            |
        📬 Inbox
```

### Step 1: Fetch

Two independent sources run in parallel:

- **NewsAPI** — A REST API that searches 150,000+ news sources by keyword. We query for terms like "artificial intelligence", "OpenAI", "Claude", "ChatGPT", etc. Returns ~80 articles from the last 28 hours.
- **RSS Feeds** — Direct feeds from 5 curated publications (TechCrunch, The Verge, MIT Tech Review, Ars Technica, VentureBeat). These catch stories that NewsAPI might miss or delay.

Each source is wrapped in error handling. If NewsAPI is down, RSS still runs (and vice versa). The pipeline never stops because one source fails.

### Step 2: Deduplicate

The same story often appears in both NewsAPI and RSS. We remove duplicates using two checks:

1. **URL normalization** — Strip query parameters, fragments, and `www.` prefixes, then compare. Fast O(n) check.
2. **Title similarity** — Use Python's `SequenceMatcher` to catch cases where the same story has slightly different titles across sources (e.g., "OpenAI Launches New Model" vs "OpenAI launches new model today"). Threshold: 75% similarity.

When a duplicate is found, we keep the version with the richer description.

### Step 3: Summarize

The deduplicated articles are sent to **Google Gemini 2.5 Flash** with a carefully crafted prompt that instructs the LLM to:

- Select the **top 10** most important stories
- **Rewrite clickbait titles** into factual headlines
- Extract **3 key takeaways** per story (max 15 words each)
- **Categorize** each story (Product Launch, Research, Business, Policy, etc.)
- **Skip junk** — PyPI packages, listicles, spam, event promos

The LLM returns structured JSON. A parser with auto-repair handles common issues (trailing commas, truncated responses, markdown fences).

If Gemini fails entirely, a fallback returns the raw article descriptions — the email still goes out, just less polished.

### Step 4: Email

The digest is rendered as a clean HTML email using:

- **Inline CSS** (email clients don't support stylesheets)
- **Table-based layout** (for Outlook/Gmail compatibility)
- **Multipart format** — both HTML and plain-text versions, so it works everywhere
- **Gmail SMTP over SSL** (port 465) with an App Password

---

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Language** | Python 3.12 | Best ecosystem for APIs, RSS parsing, and scripting. Everyone can read it. |
| **News source** | NewsAPI (free tier) | 100 requests/day, covers 150K+ sources, simple REST API. One call gets 80 articles. |
| **RSS parsing** | feedparser | The standard Python RSS library. Handles RSS 2.0, Atom, edge cases. Zero config. |
| **LLM** | Google Gemini 2.5 Flash | Generous free tier (1M tokens/day). Fast. Good enough for summarization — we don't need frontier reasoning here. |
| **Email** | Gmail SMTP + App Password | Zero cost, zero signup. Uses Python's built-in `smtplib` — no external dependency. |
| **Scheduling** | GitHub Actions cron | Free for public repos. No server to maintain. Runs reliably. |
| **Secrets** | GitHub Secrets → env vars | Industry standard. Secrets never touch the codebase. |

### Dependencies (only 3)

```
feedparser    — RSS parsing
requests      — HTTP calls to NewsAPI
google-genai  — Gemini SDK
```

Everything else is Python stdlib (`smtplib`, `email`, `json`, `re`, `difflib`, `urllib.parse`).

---

## Why These Choices (Tradeoffs)

### NewsAPI vs. scraping vs. RSS-only

| Approach | Pros | Cons |
|----------|------|------|
| **NewsAPI** | Broadest coverage, simple API, keyword search | Free tier limited to 100 req/day; articles can be 24h delayed |
| **RSS-only** | Free, no API key, real-time | Limited to publications you manually curate; no keyword search |
| **Web scraping** | Most flexible | Brittle, breaks when sites change, legal gray area |

**Our choice: NewsAPI + RSS combined.** NewsAPI gives breadth (150K sources), RSS gives depth (curated quality sources with no delay). If either fails, the other still works.

### Gemini vs. GPT vs. Claude vs. no LLM

| Approach | Pros | Cons |
|----------|------|------|
| **Gemini 2.5 Flash** | Free tier (1M tokens/day), fast, good quality | Google can change free tier limits |
| **GPT-4o-mini** | Very cheap ($0.15/1M tokens), reliable | Requires paid API key |
| **Claude Haiku** | Great summarization quality | Requires paid API key |
| **No LLM (rule-based)** | No API dependency | Can't rewrite titles, can't curate, can't extract takeaways |

**Our choice: Gemini 2.5 Flash.** For a daily digest, the free tier is more than enough (we use ~5K tokens per run). The task — summarization and curation — doesn't need frontier intelligence. If Gemini's free tier changes, swapping to GPT-4o-mini is a one-line config change.

### Gmail SMTP vs. Resend vs. SendGrid

| Approach | Pros | Cons |
|----------|------|------|
| **Gmail SMTP** | Free, no signup, stdlib only | Tied to personal Gmail, 500 emails/day limit |
| **Resend** | Great API, 100 free/day | Requires account + domain verification for production |
| **SendGrid** | Established, 100 free/day | More complex setup, heavier SDK |

**Our choice: Gmail SMTP.** This is a personal automation sending 1 email/day. Gmail's 500/day limit is irrelevant. No extra dependency, no extra account. If this ever needs to scale to multiple recipients, switching to Resend is straightforward.

### GitHub Actions vs. cron server vs. cloud functions

| Approach | Pros | Cons |
|----------|------|------|
| **GitHub Actions** | Free, no infra, version-controlled schedule | Max 6-hour runtime, can be delayed by ~15 min |
| **AWS Lambda + EventBridge** | Precise timing, scalable | Requires AWS account, more complex deploy |
| **Local cron** | Full control | Machine must be on, no redundancy |

**Our choice: GitHub Actions.** Zero infrastructure. The workflow YAML lives in the repo alongside the code. The ~15 min cron delay doesn't matter for a morning digest. If the job fails, GitHub sends a notification.

---

## What Could Go Wrong

| Failure | Impact | Mitigation |
|---------|--------|------------|
| NewsAPI is down | Fewer articles (RSS still works) | Independent error handling per source |
| All RSS feeds break | Fewer articles (NewsAPI still works) | Feeds are checked individually; broken ones are logged and skipped |
| Gemini quota exceeded | Lower quality digest | Fallback returns raw descriptions — email still goes out |
| Gemini returns bad JSON | Lower quality digest | 3-stage JSON auto-repair (parse → fix commas → salvage truncated) |
| Gmail rejects auth | No email sent | Script exits with code 1; GitHub Actions marks run as failed and notifies you |
| No articles found | No email sent | Script exits cleanly (code 0) — nothing to report is not an error |

---

## Cost

**$0/month.** Every component is free tier:

- NewsAPI: 100 requests/day (we use 1)
- Gemini: 1M tokens/day (we use ~5K)
- Gmail SMTP: 500 emails/day (we send 1)
- GitHub Actions: 2,000 minutes/month on free tier (each run takes ~30 seconds)

---

*Part of [Automation Lab](../README.md)*
