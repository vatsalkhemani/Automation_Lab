# weekly-learning

Every Saturday, this automation picks a random topic — from history to health to psychology — generates a ~1000-word explainer using Gemini, and delivers it to your inbox. Topics are mainstream and foundational: things a well-rounded person should know. The writing is conversational, not academic — you finish reading and feel like you actually understand something new.

<!-- Replace the src below with your own screenshot uploaded to GitHub (drag into an issue or PR to get the URL) -->
<img width="250" height="400" alt="image" src="https://github.com/user-attachments/assets/0f7dc5fd-2377-4698-8b70-7c814874d277" />
<img width="250" height="400" alt="image" src="https://github.com/user-attachments/assets/26e21db0-a2d3-41d9-ac4f-1bfac75f8144" />



## Status

**Shipped**

## How It Works

Every Saturday at 9:00 AM IST, this automation:

1. **Picks** a random category from 11 knowledge domains (science, tech, history, geography, philosophy, math, economics, psychology, health, arts, politics)
2. **Generates** a clear, conversational explainer using Gemini 2.5 Flash — the LLM picks a big, widely-relevant topic within the category and writes it like it's explaining to a smart friend over coffee
3. **Emails** a clean HTML article with sections, a surprising fact callout, and further reading suggestions via Gmail SMTP

Each email includes:
- A hook that tells you why this topic matters
- 3-4 sections with short paragraphs and plain language
- A "Surprising Fact" callout box
- 3 suggestions for going deeper (books, videos, podcasts)

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
Category: Arts & Culture
Topic:    The Renaissance: A Rebirth of Ideas

Ever wonder why some periods in history just seem to explode with creativity? The
Renaissance is a perfect example. It was a pivotal time when Europe rediscovered
ancient knowledge, creating a cascade of innovation in art, science, and thought
that still shapes our world today.

## What Was the Renaissance, Anyway?

Imagine Europe emerging from what historians used to call the 'Dark Ages'. Suddenly,
around the 14th century, there was a massive intellectual and artistic awakening,
primarily starting in Italy.

This wasn't just a gradual shift; it was a deliberate 'rebirth' of classical Greek
and Roman ideas. Scholars started digging up ancient texts, admiring their
philosophies and scientific approaches that had been largely forgotten.

## Where Did All This Brilliance Come From?

Italy, especially city-states like Florence, Venice, and Rome, became the epicenter.
Powerful merchant families, like the Medicis, became patrons, commissioning artists,
architects, and scholars.

Artists like Leonardo da Vinci, Michelangelo, and Raphael weren't just painting
pretty pictures; they were innovators. Da Vinci was an engineer, anatomist, and
inventor, embodying the 'Renaissance Man' ideal.

## Why Does the Renaissance Still Matter Today?

Think about our appreciation for art, our scientific method, or even our democratic
ideals — many threads trace back to this period. It taught us the power of
observation, critical thinking, and the pursuit of knowledge for its own sake.

Surprising Fact: Leonardo da Vinci, perhaps the ultimate 'Renaissance Man,' was an
illegitimate child and didn't receive a formal humanist education. His genius was
largely self-taught through observation and relentless experimentation.

Go Deeper:
  -> The Swerve: How the World Became Modern by Stephen Greenblatt (Book)
  -> Medici: Godfathers of the Renaissance (PBS Documentary)
  -> A Little History of the World by E.H. Gombrich (Book)
```

---

*Part of [Automation Lab](../README.md)*
