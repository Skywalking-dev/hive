---
name: google-workspace
description: Access any Google Workspace API via gws CLI or MCP tools. Use for Sheets, Tasks, Chat, Slides, People, Forms, Meet, and as fallback for Drive/Gmail/Calendar/Docs when existing handlers lack a feature. Use existing Python handlers first for Gmail (send-blocking), Drive (domain allowlist), Calendar, Docs.
allowed-tools: Bash, Read, mcp__google-workspace__*
---

# Google Workspace CLI (gws)

Unified CLI for all Google Workspace APIs. Dynamically discovers API methods from Google Discovery Documents.

## When to Use

| Need | Use |
|------|-----|
| Gmail read/draft/labels/filters | `scripts/gmail_handler.py` (has send-blocking guardrail) |
| Drive list/search/upload/share | `scripts/google_drive_handler.py` (has domain allowlist) |
| Calendar events/freebusy | `scripts/google_calendar_handler.py` |
| Docs get/create/update/export | `scripts/google_docs_handler.py` (has Markdown conversion) |
| **Sheets, Tasks, Chat, Slides, People, Forms, Meet, Admin** | **gws** |
| Any API not covered by existing handlers | **gws** |
| Bulk operations with auto-pagination | **gws --page-all** |

## MCP Tools

When MCP server is running, tools are available as `mcp__google-workspace__*`. Use compact mode — one tool per service + discover.

## CLI Syntax

```bash
gws <service> <resource> <method> [--params '{}'] [--json '{}']
```

## Schema Discovery

Always check schema before executing unfamiliar methods:

```bash
gws schema <service.resource.method>
# e.g.
gws schema sheets.spreadsheets.values.get
gws schema tasks.tasklists.list
```

## Common Commands

### Sheets

```bash
# Read spreadsheet values
gws sheets spreadsheets.values get --params '{"spreadsheetId": "ID", "range": "Sheet1!A1:D10"}'

# Write values
gws sheets spreadsheets.values update --params '{"spreadsheetId": "ID", "range": "Sheet1!A1", "valueInputOption": "USER_ENTERED"}' --json '{"values": [["a","b"],["c","d"]]}'

# Get spreadsheet metadata
gws sheets spreadsheets get --params '{"spreadsheetId": "ID"}'
```

### Tasks

```bash
# List task lists
gws tasks tasklists list

# List tasks in a list
gws tasks tasks list --params '{"tasklist": "LIST_ID"}'

# Create task
gws tasks tasks insert --params '{"tasklist": "LIST_ID"}' --json '{"title": "Do something", "notes": "Details"}'

# Complete task
gws tasks tasks patch --params '{"tasklist": "LIST_ID", "task": "TASK_ID"}' --json '{"status": "completed"}'
```

### Chat

```bash
# List spaces
gws chat spaces list

# Send message
gws chat spaces.messages create --params '{"parent": "spaces/SPACE_ID"}' --json '{"text": "Hello"}'
```

### People / Contacts

```bash
# List contacts
gws people people.connections list --params '{"resourceName": "people/me", "personFields": "names,emailAddresses"}'

# Search
gws people people searchContacts --params '{"query": "John", "readMask": "names,emailAddresses"}'
```

### Slides

```bash
# Get presentation
gws slides presentations get --params '{"presentationId": "ID"}'
```

## Flags

| Flag | Purpose |
|------|---------|
| `--params '{}'` | URL/query parameters |
| `--json '{}'` | Request body (POST/PATCH/PUT) |
| `--upload <path>` | File upload (multipart) |
| `--output <path>` | Save binary response to file |
| `--format table` | Table output instead of JSON |
| `--page-all` | Auto-paginate (NDJSON) |
| `--page-limit N` | Max pages (default 10) |
| `--api-version v2` | Override API version |

## Auth

```bash
# First-time setup (needs gcloud)
gws auth setup

# Login (opens browser)
gws auth login -s drive,gmail,calendar,docs,sheets,tasks,chat

# Check status
gws auth status

# Multi-account
gws auth login --account work@publica.la
gws auth login --account personal@gmail.com
gws auth default --account work@publica.la
```

## Output

All commands return JSON by default. Use `--format table` for human-readable output.

## Guardrails

- For Gmail send operations, prefer `scripts/gmail_handler.py` which blocks `send`/`draft-send`
- For Drive sharing, prefer `scripts/google_drive_handler.py` which enforces domain allowlist
- Always confirm destructive operations (delete, permanent remove) with user
- Use `gws schema` before executing unfamiliar methods to verify required params
