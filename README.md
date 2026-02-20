# Automation Lab

**Automations that run so I don't have to.**

---

## What This Is

A collection of small, self-contained automations — each one solving a real problem, scheduled to run on its own via GitHub Actions. Every folder is a complete, working system: script, schedule, secrets config, and documentation.

## Philosophy

- **One at a time.** Each automation is built, tested, documented, and shipped before starting the next.
- **Best tool for the job.** Python, Node, any LLM API with a free tier, any email provider — whatever solves it cleanest.
- **Self-contained.** Each folder has everything you need: code, config, docs. Clone one folder and it works.
- **No secrets in code.** All credentials live in GitHub Secrets, injected as env vars at runtime. Each folder has a `.env.example` showing what's needed.

## Automations

| #  | Name | What It Does | Status |
|----|------|--------------|--------|
| 1  | [ai-news-digest](./ai-news-digest/) | Daily email with concise AI news from the last 24h | Planned |
| 2  | [weekly-learning](./weekly-learning/) | Saturday deep-dive email on a random topic | Planned |
| 3  | [hiring-tracker](./hiring-tracker/) | Weekly pulse on tech companies scaling or cutting | Planned |
| 4  | [job-alerts](./job-alerts/) | Daily filtered job openings delivered to inbox | Planned |
| 5  | [gmail-declutter](./gmail-declutter/) | Weekly automated inbox cleanup | Planned |
| 6  | [linkedin-outreach](./linkedin-outreach/) | Automated personalized LinkedIn outreach | Planned |

## How to Fork an Automation

1. **Pick a folder** — each automation is self-contained.
2. **Read its README** — it explains what it does, what secrets it needs, and how to run it.
3. **Set up secrets** — copy `.env.example` to `.env` locally, or add them to GitHub Secrets for scheduled runs.
4. **Run it** — locally with `python main.py` (or equivalent), or let GitHub Actions handle it on schedule.

## Secrets Approach

All secrets are managed through **GitHub Secrets** and injected as environment variables at runtime. No credentials are ever committed to the repo.

Each automation folder contains a `.env.example` file with blank values, documenting exactly which secrets are required:

1. Go to **Settings > Secrets and variables > Actions** in this repo.
2. Add each secret listed in the automation's `.env.example`.
3. The GitHub Actions workflow automatically picks them up.

---

Built by [Vatsal Khemani](https://github.com/vatsalkhemani)
