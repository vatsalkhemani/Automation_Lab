# CLAUDE.md — Automation Lab

Read this file at the start of every session.

## Owner

Product manager who codes. Comfortable with Python, has built and shipped full-stack AI tools, understands APIs and LLMs. This repo is proof of work — it demonstrates systems thinking through real, working automations.

## Philosophy

- One automation at a time. Build it, test it, document it, ship it — then move on.
- Each folder is one self-contained automation. Someone can clone a single folder and get it running.
- No half-built things in main. If it's in main, it works.
- Well-structured and well-documented > clever.

## Stack Approach

- No hard preferences. Use the best free or near-free tool for each specific job.
- Python, Node, GitHub Actions, Make, n8n, any email provider, any LLM API with a free tier — all fair game.
- Pick what solves the problem simplest. Recommend and explain why.

## Secrets Approach

- ALL secrets go through GitHub Secrets, injected as environment variables at runtime.
- Every automation folder includes a `.env.example` with blank values showing what's needed.
- NEVER commit real secrets. The `.gitignore` blocks `.env` files (but allows `.env.example`).

## Repo Structure

- Root: `.gitignore`, `README.md`, `CLAUDE.md`, `ROADMAP.md`
- `.github/workflows/` at repo root holds ALL GitHub Actions workflows (one YAML per automation, e.g., `ai-news-digest.yml`). GitHub Actions only reads workflows from this location.
- Each automation lives in its own top-level folder with: `README.md`, `main.py` (or equivalent entry point), `.env.example`, and any supporting files.

## Automation List

| # | Automation        | Status |
|---|-------------------|--------|
| 1 | ai-news-digest    | idea   |
| 2 | weekly-learning   | idea   |
| 3 | hiring-tracker    | idea   |
| 4 | job-alerts        | idea   |
| 5 | gmail-declutter   | idea   |
| 6 | linkedin-outreach | idea   |

Status values: `idea` → `in-progress` → `shipped`

## Conventions

- Workflow YAML files: `.github/workflows/<automation-name>.yml` — NOT inside automation folders.
- Each automation README includes: what it does, how it runs, what secrets it needs, and example output.
- Commit messages: imperative mood, concise. Example: "Add ai-news-digest automation"
- When building an automation, create the `.env.example`, the workflow YAML, the script(s), and the README in a single effort before marking it shipped.
