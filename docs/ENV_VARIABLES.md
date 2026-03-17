# API Keys Reference

Every integration in Hive is powered by a Python script in `scripts/` and exposed through a skill in `skills/`. This document maps each API key to its script, skill, and purpose.

## Quick Setup

```bash
cp .env.example .env
# Fill in only the keys you need — all integrations are optional
```

## Key Map

### Google APIs

All Google services share a single OAuth2 client. `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` are the defaults — service-specific overrides (`GOOGLE_DOCS_CLIENT_ID`, etc.) are optional.

Each service requires its own refresh token. Run the setup command to generate it:

```bash
python scripts/<handler>.py setup
```

#### Gmail

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `GMAIL_CLIENT_ID` | `gmail_handler.py` | `/gmail` | OAuth2 client ID (shared default for all Google services) |
| `GMAIL_CLIENT_SECRET` | `gmail_handler.py` | `/gmail` | OAuth2 client secret (shared default for all Google services) |
| `GMAIL_REFRESH_TOKEN` | `gmail_handler.py` | `/gmail` | Long-lived token for Gmail API access |

**Use case:** Read inbox, search emails, compose drafts, manage labels, create filters.

#### Google Docs

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `GOOGLE_DOCS_REFRESH_TOKEN` | `google_docs_handler.py` | `/google-docs` | Token for Docs API (read, create, update, export) |
| `GOOGLE_DOCS_CLIENT_ID` | `google_docs_handler.py` | `/google-docs` | Optional override. Falls back to `GMAIL_CLIENT_ID` |
| `GOOGLE_DOCS_CLIENT_SECRET` | `google_docs_handler.py` | `/google-docs` | Optional override. Falls back to `GMAIL_CLIENT_SECRET` |

**Use case:** Read docs as Markdown, create/update docs, export to PDF/DOCX/HTML, search docs.

#### Google Drive

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `GOOGLE_DRIVE_REFRESH_TOKEN` | `google_drive_handler.py` | `/google-drive` | Token for Drive API (list, search, upload, share) |
| `GOOGLE_DRIVE_CLIENT_ID` | `google_drive_handler.py` | `/google-drive` | Optional override. Falls back to `GMAIL_CLIENT_ID` |
| `GOOGLE_DRIVE_CLIENT_SECRET` | `google_drive_handler.py` | `/google-drive` | Optional override. Falls back to `GMAIL_CLIENT_SECRET` |

**Use case:** List files, search, download, upload, share, organize folders.

#### Google Calendar

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `GOOGLE_CALENDAR_REFRESH_TOKEN` | `google_calendar_handler.py` | `/google-calendar` | Token for Calendar API (read-only) |
| `GOOGLE_CALENDAR_CLIENT_ID` | `google_calendar_handler.py` | `/google-calendar` | Optional override. Falls back to `GMAIL_CLIENT_ID` |
| `GOOGLE_CALENDAR_CLIENT_SECRET` | `google_calendar_handler.py` | `/google-calendar` | Optional override. Falls back to `GMAIL_CLIENT_SECRET` |

**Use case:** View today/week events, check free/busy, search events, list calendars.

#### YouTube

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `YOUTUBE_API_KEY` | `transcript_handler.py` | `/extract_transcript` | YouTube Data API for video metadata and listing |

**Use case:** Extract transcripts, get video metadata, list channel videos.

#### Gemini

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `GEMINI_API_KEY` | `invoke_mycelium.py` | `/reunion` | Google Gemini API for AI agent invocation |

**Use case:** Powers the Mycelium sub-agent for generating PRDs and implementation plans.

### Search

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `PERPLEXITY_API_KEY` | `perplexity_handler.py` | `/perplexity` | Perplexity Sonar, Search, and Agent APIs |

**Use case:** Web search with AI summaries, raw search results, multi-provider agent queries.

### Communication

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `SLACK_BOT_TOKEN` | `slack_handler.py` | `/slack` | Slack Bot OAuth token (xoxb-*) |
| `WHATSAPP_TOKEN` | `whatsapp_handler.py` | `/whatsapp` | Meta WhatsApp Business API bearer token |
| `WHATSAPP_PHONE_ID` | `whatsapp_handler.py` | `/whatsapp` | WhatsApp Business phone number ID |

**Slack:** Read threads, post messages, upload files.
**WhatsApp:** Send messages via WhatsApp Business API, check delivery status.

### Infrastructure

| Key | Script | Skill | What it does |
|-----|--------|-------|--------------|
| `SUPABASE_URL` | (MCP) | `/supabase` | Supabase project URL |
| `SUPABASE_ANON_KEY` | (MCP) | `/supabase` | Public/anonymous key for client-side access |
| `SUPABASE_SERVICE_ROLE_KEY` | (MCP) | `/supabase` | Admin key for server-side operations |
| `VERCEL_TOKEN` | (CLI) | `/vercel` | Vercel API token for deployments and management |

**Supabase:** Database queries, migrations, auth operations. Accessed via MCP server, not a Python script.
**Vercel:** Deploy, manage environment variables, view logs, configure cron. Uses Vercel CLI directly.

## How Credentials Flow

```
.env  →  load_dotenv()  →  scripts/*.py  →  skill invokes script via Bash
                                          →  MCP server reads env directly
```

1. You set keys in `.env`
2. Python scripts load them via `load_dotenv()` at startup
3. Skills call scripts through Bash commands
4. MCP-based integrations (Supabase, Google Workspace CLI) read env vars directly

## Security Notes

- `.env` is in `.gitignore` — never committed
- A pre-commit hook (`scripts/pre-commit-secrets.sh`) scans for secret patterns and blocks commits
- All scripts use `os.environ.get()` — no hardcoded credentials
- Google OAuth tokens are scoped per-service via separate refresh tokens

## Which Keys Do I Need?

You only need the keys for integrations you plan to use. Here's a quick guide:

| I want to... | Keys needed |
|--------------|-------------|
| Read/send emails | `GMAIL_*` |
| Work with Google Docs | `GMAIL_CLIENT_ID/SECRET` + `GOOGLE_DOCS_REFRESH_TOKEN` |
| Manage Google Drive files | `GMAIL_CLIENT_ID/SECRET` + `GOOGLE_DRIVE_REFRESH_TOKEN` |
| Check my calendar | `GMAIL_CLIENT_ID/SECRET` + `GOOGLE_CALENDAR_REFRESH_TOKEN` |
| Extract YouTube transcripts | `YOUTUBE_API_KEY` |
| Use Gemini AI agents | `GEMINI_API_KEY` |
| Search the web with AI | `PERPLEXITY_API_KEY` |
| Send Slack messages | `SLACK_BOT_TOKEN` |
| Send WhatsApp messages | `WHATSAPP_*` |
| Query databases | `SUPABASE_*` |
| Deploy to Vercel | `VERCEL_TOKEN` |
