# weekly-learning

> Every Saturday, a deep-dive exploration of a random topic delivered by email.

## What It Does

Picks a random category (science, tech, history, geography, philosophy, math, economics, psychology), asks Gemini to choose a specific non-obvious topic within it, generates an ~800-word deep-dive article, and emails it as a Saturday morning read.

Each email includes:
- A hook paragraph to grab attention
- 3-4 sections exploring the topic in depth
- A surprising fact callout
- 3 suggestions for further reading

## How It Runs

- **Schedule:** Every Saturday at 9:00 AM IST (03:30 UTC) via GitHub Actions
- **Manual trigger:** `workflow_dispatch` in GitHub Actions UI
- **Local:** `python main.py` (sends email) or `python main.py --dry-run` (prints to stdout)

## Secrets Needed

| Secret | Description | Where to get it |
|--------|-------------|-----------------|
| `GEMINI_API_KEY` | Google Gemini API key | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `GMAIL_ADDRESS` | Gmail address to send from | Your Gmail (must have 2FA enabled) |
| `GMAIL_APP_PASSWORD` | Gmail App Password | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `EMAIL_RECIPIENT` | Email address to receive the article | Any email address |

Add these as **GitHub Secrets** (Settings > Secrets and variables > Actions) for scheduled runs, or copy `.env.example` to `.env` for local runs.

## How to Run Locally

```bash
cd weekly-learning
pip install -r requirements.txt
cp .env.example .env   # then fill in your values
python main.py --dry-run
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

## Topic Categories

The script randomly picks from these categories each week:

- Science & Nature
- Technology & Computing
- History & Civilization
- Geography & Cultures
- Philosophy & Ideas
- Mathematics & Logic
- Economics & Systems
- Psychology & Human Behavior

---

*Part of [Automation Lab](../README.md)*
