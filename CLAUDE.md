# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Read this file at the start of every session.

## Owner

Product manager who codes. Comfortable with Python, understands APIs and LLMs. This repo is proof of work — demonstrates systems thinking through real, working automations.

## Philosophy

- One automation at a time. Build it, test it, document it, ship it — then move on.
- Each folder is one self-contained automation. Someone can clone a single folder and get it running.
- No half-built things in main. If it's in main, it works.
- Well-structured and well-documented > clever.

## Stack Approach

- No hard preferences. Use the best free or near-free tool for each specific job.
- Python, Node, GitHub Actions, Make, n8n, any email provider, any LLM API with a free tier — all fair game.
- Pick what solves the problem simplest. Recommend and explain why.

## Running Automations

Each automation is run from inside its own folder:

```bash
cd <automation-name>
pip install -r requirements.txt
python main.py              # full run (sends email, posts, etc.)
python main.py --dry-run    # fetch + process, print to stdout, no side effects
```

There is no top-level build, lint, or test command. Each automation is independent.

## Secrets

- ALL secrets go through GitHub Secrets, injected as environment variables at runtime.
- Every automation folder includes a `.env.example` with blank values showing what's needed.
- For local runs, copy `.env.example` to `.env` and fill in values. The `.gitignore` blocks `.env` files.
- NEVER commit real secrets.

## Repo Structure

- `.github/workflows/` at repo root holds ALL GitHub Actions workflows (one YAML per automation). GitHub Actions only reads workflows from this path — never put workflow files inside automation folders.
- Each automation lives in its own top-level folder with: `README.md`, `main.py` (or equivalent), `.env.example`, and supporting modules.
- Root files: `.gitignore`, `README.md`, `CLAUDE.md`, `ROADMAP.md`

## Automation List

| # | Automation        | Status  |
|---|-------------------|---------|
| 1 | ai-news-digest    | shipped |
| 2 | weekly-learning   | shipped |
| 3 | hiring-tracker    | idea    |
| 4 | job-alerts        | idea    |
| 5 | gmail-declutter   | idea    |
| 6 | linkedin-outreach | idea    |

Status values: `idea` → `in-progress` → `shipped`

## Architecture Pattern (ai-news-digest as reference)

New automations should follow this pipeline pattern with isolated modules:

```
main.py          — orchestrator: runs the pipeline, handles --dry-run
config.py        — all settings, secrets (from env vars), and constants in one place
fetchers.py      — data ingestion (API calls, RSS, scraping)
dedup.py         — deduplication / cleaning
summarizer.py    — LLM processing (prompt, parse, fallback)
emailer.py       — delivery (SMTP, HTML rendering with inline CSS)
```

Key design decisions to follow:
- **Each data source is independent** — if one fails, others still run. Wrap each in its own try/except.
- **LLM calls always have a fallback** — if the API fails or returns bad output, the pipeline still delivers something.
- **JSON auto-repair for LLM output** — parse raw → fix trailing commas → salvage truncated arrays.
- **Email uses inline CSS + table layout** — required for Gmail/Outlook compatibility. No external stylesheets.
- Articles flow as `list[dict]` with keys: `title`, `url`, `source`, `published`, `description`. The summarizer transforms these into digest entries with: `title`, `source`, `url`, `takeaways` (list of strings), `category`.

## Workflow YAML Pattern

```yaml
name: Automation Name
on:
  schedule:
    - cron: "..."
  workflow_dispatch:
jobs:
  job-name:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <automation-folder>
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          SECRET_NAME: ${{ secrets.SECRET_NAME }}
```

`working-directory` is set at the job level so all `run` steps execute inside the automation folder.

## Conventions

- Commit messages: imperative mood, concise. Example: "Add ai-news-digest automation"
- When building an automation, create `.env.example`, workflow YAML, scripts, and README in a single effort before marking it shipped.
- Each automation README includes: what it does, how it runs, what secrets it needs, and example output.
- Update `ROADMAP.md` and the automation list in this file when status changes.
