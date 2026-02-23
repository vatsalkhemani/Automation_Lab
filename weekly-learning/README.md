# weekly-learning

Every Saturday, this automation picks a random topic — from philosophy to geography to psychology — generates an ~800-word deep-dive article using Gemini, and delivers it to your inbox as a morning read.

<!-- Replace the src below with your own screenshot uploaded to GitHub (drag into an issue or PR to get the URL) -->
<img width="418" alt="Example weekly learning email" src="https://github.com/user-attachments/assets/REPLACE_WITH_YOUR_SCREENSHOT" />

## Status

**Shipped**

## How It Works

Every Saturday at 9:00 AM IST, this automation:

1. **Picks** a random category from 8 knowledge domains (science, tech, history, geography, philosophy, math, economics, psychology)
2. **Generates** a deep-dive article using Gemini 2.5 Flash — the LLM picks a specific non-obvious topic within the category and writes an engaging exploration
3. **Emails** a clean HTML article with sections, a surprising fact callout, and further reading suggestions via Gmail SMTP

Each email includes:
- A hook paragraph that grabs attention
- 3-4 sections exploring the topic in depth
- A "Surprising Fact" callout box
- 3 suggestions for going deeper

## How It Runs

| | |
|---|---|
| **Schedule** | Every Saturday at 03:30 UTC (9:00 AM IST) |
| **Manual trigger** | `workflow_dispatch` in GitHub Actions tab |
| **Entry point** | `python main.py` |
| **Dry run** | `python main.py --dry-run` |

## Architecture

```
main.py           — orchestrator, --dry-run support
├── config.py     — env vars, topic categories, Gemini + email settings
├── generator.py  — Gemini 2.5 Flash content generation with JSON auto-repair
└── emailer.py    — HTML email with sections, callouts via Gmail SMTP
```

## Secrets Required

| Secret | Description | Where to get it |
|--------|-------------|-----------------|
| `GEMINI_API_KEY` | Google Gemini API key | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `GMAIL_ADDRESS` | Gmail address to send from | Your Gmail (2FA required) |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your regular password) | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `EMAIL_RECIPIENT` | Email address to receive the article | Any email address |

Add these in **Settings > Secrets and variables > Actions** for GitHub Actions, or in a local `.env` file.

## Local Development

```bash
cd weekly-learning
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

```
Category: History & Civilization
Topic:    The Great Emu War of 1932

In 1932, the Australian government declared war on emus — and lost. What started
as a pest control operation became one of history's most absurd military campaigns...

## The Problem: 20,000 Emus vs. Australian Wheat

After World War I, the Australian government encouraged veterans to take up farming
in Western Australia...

## The Military Response

Major G.P.W. Meredith of the Royal Australian Artillery was dispatched with two
soldiers, two Lewis guns, and 10,000 rounds of ammunition...

## The Aftermath

The military withdrew after less than a week. The emus had won...

Surprising Fact: The emus were so resilient that soldiers compared them to tanks,
noting they could absorb multiple bullets and keep running.

Go Deeper:
  -> "The Emu War" by Murray Johnson (Australian Historical Studies)
  -> "Bird vs. Gun: Australia's Strangest Conflict" — Atlas Obscura
  -> "Pest or Patriot? The Emu in Australian History" — ABC Australia
```

---

*Part of [Automation Lab](../README.md)*
