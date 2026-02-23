# Technical Deep Dive: weekly-learning

A plain-English explanation of how this automation works, why it's built this way, and the tradeoffs involved.

---

## The Problem

Learning new things outside your bubble takes effort. You *want* to read about philosophy, or how coral reefs communicate, or why some economies collapsed — but you never get around to it. This automation removes the friction: every Saturday, a well-written deep-dive on a random topic shows up in your inbox. No searching, no choosing, no decision fatigue.

## How It Works (End-to-End)

```
  [8 Topic Categories]
          |
    1. PICK random category
          |
    2. GENERATE article (Gemini)
          |
    3. EMAIL (Gmail SMTP)
          |
      📬 Inbox
```

### Step 1: Pick a Category

The script randomly selects one of 8 broad knowledge domains:

- Science & Nature
- Technology & Computing
- History & Civilization
- Geography & Cultures
- Philosophy & Ideas
- Mathematics & Logic
- Economics & Systems
- Psychology & Human Behavior

This is a simple `random.choice()` — no weighting, no history tracking. With 8 categories and the LLM picking a different specific topic each time, repeats are extremely unlikely.

### Step 2: Generate the Article

The selected category is sent to **Google Gemini 2.5 Flash** with a system prompt that instructs the LLM to:

- **Pick a specific, non-obvious topic** within the category — not the first thing you'd Google. For "History & Civilization", don't write about World War II; write about the Library of Ashurbanipal or the Great Emu War.
- **Write for a smart generalist** — clear explanations, no jargon assumed, but no dumbing down.
- **Be concrete** — names, dates, numbers, places. No vague filler.
- **Target ~800 words** — a satisfying 5-minute Saturday read.

The LLM returns structured JSON with:

```json
{
  "topic": "The specific topic name",
  "category": "The category",
  "hook": "An attention-grabbing opening paragraph",
  "sections": [
    {"heading": "Section title", "content": "2-3 paragraphs"}
  ],
  "surprising_fact": "One counterintuitive fact",
  "further_reading": ["Book or article 1", "Book or article 2", "Book or article 3"]
}
```

The JSON parser includes auto-repair for common LLM output issues:
1. **Strip markdown fences** — LLMs often wrap JSON in ` ```json ` blocks
2. **Fix trailing commas** — a frequent LLM mistake (`{"key": "value",}`)
3. If both attempts fail, the function returns `None` and the script exits with an error.

**Temperature is set to 0.9** (higher than ai-news-digest's 0.3) because we *want* creative, varied output here — not deterministic summarization.

### Step 3: Email

The article is rendered as a clean HTML email with:

- **Category badge** — colored pill label at the top (each category has its own color)
- **Large topic title** — the main headline
- **Italic hook paragraph** — sets the tone
- **Structured sections** — headings with multi-paragraph body text
- **"Surprising Fact" callout box** — amber left-border accent, stands out visually
- **"Go Deeper" section** — 3 reading suggestions with arrow indicators
- **Inline CSS + table layout** — required for Gmail/Outlook compatibility
- **Multipart format** — both HTML and plain-text versions

The subject line includes the topic name: `Weekly Learning: The Great Emu War — February 22, 2026`

---

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **Language** | Python 3.12 | Same as ai-news-digest. Consistent across the repo. |
| **LLM** | Google Gemini 2.5 Flash | Free tier (1M tokens/day). Each article uses ~2K tokens. Creative writing quality is good enough for this task. |
| **Email** | Gmail SMTP + App Password | Zero cost, stdlib only. Same infrastructure as ai-news-digest — no new accounts or services needed. |
| **Scheduling** | GitHub Actions cron | Free, no infra. Runs every Saturday. |
| **Secrets** | GitHub Secrets → env vars | Same pattern as every automation in this repo. |

### Dependencies (only 1)

```
google-genai  — Gemini SDK
```

Everything else is Python stdlib (`smtplib`, `email`, `json`, `re`, `random`).

---

## Why These Choices (Tradeoffs)

### Topic selection: random category + LLM pick vs. curated list vs. fully random

| Approach | Pros | Cons |
|----------|------|------|
| **Random category + LLM picks topic** | Balanced variety, surprising topics, no list to maintain | Can't guarantee specific topics; slight risk of overlap |
| **Curated topic list** | Full control over what you learn | Requires maintaining a list of 50+ topics; removes serendipity |
| **Fully random (LLM picks everything)** | Maximum surprise | Could cluster in one domain; no guaranteed breadth |

**Our choice: Random category + LLM picks topic.** The 8 categories guarantee breadth across domains. Within each category, the LLM is prompted to pick non-obvious topics, which keeps things surprising. No list to maintain.

### Single LLM call vs. two-step (pick topic, then write)

| Approach | Pros | Cons |
|----------|------|------|
| **Single call** | Faster, cheaper, simpler code | Topic choice is embedded in generation; harder to retry just the topic |
| **Two calls** | Can log/approve topic before generating; retry topic independently | 2x API calls, more latency, more code |

**Our choice: Single call.** This is a weekly automation sending 1 email. The extra complexity of two calls isn't worth it. If the topic is bad, just wait for next week — or trigger another run manually.

### Temperature 0.9 vs. lower

For ai-news-digest, temperature is 0.3 — we want deterministic, factual summarization. Here, we want creative, varied writing. **0.9** gives the LLM freedom to pick surprising topics and write with personality, without going off the rails.

### No topic history tracking

We deliberately don't track previously generated topics. Tracking would require persistent storage (database, file commit, external service), which adds complexity to what should be a zero-infrastructure automation. With 8 categories and the LLM's tendency to pick different topics, real repeats are rare.

---

## What Could Go Wrong

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Gemini API is down | No email sent | Script exits with code 1; GitHub Actions marks run as failed and notifies you |
| Gemini returns bad JSON | No email sent | 2-stage JSON auto-repair (parse → fix trailing commas). If both fail, exits with error. |
| Gemini writes a low-quality article | Mediocre email | The prompt is detailed and opinionated. Quality is consistently good in testing. Worst case, it's still interesting. |
| Gmail rejects auth | No email sent | Script exits with code 1; GitHub Actions notifies you |
| Topic repeats | Mild annoyance | Extremely unlikely with 8 categories × infinite topics. No mitigation needed. |

---

## Cost

**$0/month.** Every component is free tier:

- Gemini: 1M tokens/day (we use ~2K per run, once a week)
- Gmail SMTP: 500 emails/day (we send 1 per week)
- GitHub Actions: 2,000 minutes/month on free tier (each run takes ~15 seconds)

---

*Part of [Automation Lab](../README.md)*
