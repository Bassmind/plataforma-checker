<!--
Guidance for AI coding agents working on the "plataforma-checker" repository.
This file is intentionally concise and focused on discoverable facts and actionable next steps.
-->

# Copilot / AI agent instructions — plataforma-checker

Short, actionable facts to help an AI agent start contributing immediately.

## Big-picture (discoverable)
- This repository currently contains only `README.md`. The README describes the app as a small web app that polls the UNIO task platform every ~20 minutes, reads notifications, and sends email or WhatsApp messages while persisting the last-seen timestamp.
- From the README: "El proposito de esta pagina es revisar cada 20 minutos la plataforma UNIO... se mandara mail o Whatsapp, ademas de guardar la ultima fecha para comparar despues." Use this as the behavioral contract until code is present.

## What to look for first (priority checks)
1. Search the workspace for any Python or web files: `*.py`, `requirements.txt`, `pyproject.toml`, `package.json`, `Dockerfile`, `Procfile`, or a `src/` directory. The repository is minimal now — if none are present, coordinate about scaffolding or locate the missing source in another branch.
2. Find the scheduler/poller: look for a script that runs on an interval (cron syntax, APScheduler, Celery beat, or a simple loop using `time.sleep`). Typical search terms: `APScheduler`, `schedule`, `cron`, `time.sleep`, `while True`.
3. Find notification adapters: look for modules that mention `mail`, `smtp`, `twilio`, `whatsapp`, or `requests` to call an external API.
4. Find persistence: search for `sqlite`, `sqlite3`, `shelve`, `tinydb`, `json`, or calls that read/write a `last_*` timestamp.

## Development workflows & commands (how to discover them)
- No explicit build or test files are present. Before making changes, detect the project type:

PowerShell quick discovery (run locally):
```
Get-ChildItem -Recurse -File -Include *.py,requirements.txt,pyproject.toml,package.json,Dockerfile | Select-Object FullName
Select-String -Path * -Pattern "if __name__ == '__main__'|APScheduler|schedule|twilio|smtp|sqlite3" -SimpleMatch
```

- If Python files are found, prefer creating a `requirements.txt` (or `pyproject.toml`) and run tests with `pytest` when tests exist. If no test framework is present, create a tiny smoke test for the main poller and notifier before larger refactors.

## Project-specific conventions & patterns to follow
- Preserve simple, explicit I/O. The README indicates a small app; prefer minimal, readable scripts over heavy frameworks unless a web UI is discovered.
- Keep scheduler logic separate from notifier adapters. Expect three logical components: poller (fetch), processor (parse/decide if new), and notifier (email/WhatsApp) + storage for last-seen timestamp.
- When adding external integrations, prefer configuration through environment variables (12-factor style): SMTP credentials, WhatsApp API keys, POLL_INTERVAL (minutes), DATA_STORE_PATH.

## Integration points & external dependencies (what to expect)
- Email: SMTP libraries (`smtplib`, `email`) or third-party services (SendGrid). Search for `smtp`, `sendgrid`, `mail`.
- WhatsApp: likely via Twilio or a REST API; search for `twilio`, `whatsapp`, `requests`.
- Persistence: file-based (JSON/SQLite) is likely given the app scope; look for `sqlite3`, `open(..., 'w')`, or `json.dump`.

## Examples / quick templates (what to create if missing)
- Minimal poller contract: a function that returns a list of notification dicts, each containing at least `{ "id": str, "text": str, "date": ISO8601 }`.
- Minimal persistence contract: functions `load_last_seen() -> datetime | None` and `save_last_seen(dt: datetime)`.

## When to ask the human / missing facts
- If there is no source code in the repository, ask where the app code is (another branch, private repo, or omitted). Do not scaffold large features without confirming scope and intended runtime.
- Ask which WhatsApp/email provider to integrate if credentials or service choices are not present.

## Merge policy for this file
- If `.github/copilot-instructions.md` already exists, merge by preserving project-specific lines above and only replacing sections titled "Big-picture" and "What to look for first" when you can confirm updated facts from code.

---
If anything here is unclear or you want the agent to take the next step (scaffold a minimal app structure, add tests, or search a specific branch), tell me which action to perform next.
