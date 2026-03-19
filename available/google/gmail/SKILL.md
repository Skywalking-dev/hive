---
name: gmail
description: Read and search Gmail inbox, manage drafts, organize with labels, and create filters. Use when user needs to check email, compose drafts, or organize messages.
allowed-tools: Bash, Read
---

# Gmail API

Read inbox, search emails, manage drafts, labels, and filters via Python script.

## Guardrails

- **NEVER send emails directly.** `send` and `draft-send` are disabled.
- To compose an email, use `draft-create`. User reviews and sends manually from Gmail.
- Always confirm with user before creating a draft on their behalf.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env`
- `GMAIL_CLIENT_SECRET` in `.env`
- `GMAIL_REFRESH_TOKEN` in `.env`

## First-time Setup

```bash
python scripts/gmail_handler.py setup
```

## Quick Commands

```bash
# List inbox
python scripts/gmail_handler.py inbox [--limit=10] [--unread]

# Search emails
python scripts/gmail_handler.py search "query" [--limit=10]

# Read full email
python scripts/gmail_handler.py read <message_id>

# List labels
python scripts/gmail_handler.py labels
```

## Drafts (safe - does NOT send)

```bash
# List drafts
python scripts/gmail_handler.py drafts [--limit=10]

# Create draft
python scripts/gmail_handler.py draft-create <to> <subject> <body>

# Update draft
python scripts/gmail_handler.py draft-update <draft_id> [--to=x] [--subject=y] [--body=z]

# Update with stdin body
echo "body" | python scripts/gmail_handler.py draft-update <draft_id> --subject=x --body-stdin

# Delete draft
python scripts/gmail_handler.py draft-delete <draft_id>
```

## Labels & Organization

```bash
# Create label
python scripts/gmail_handler.py create-label <name>

# Apply label to messages
python scripts/gmail_handler.py apply-label <labelId> <msgId1> [msgId2...]

# Organize: find/create label + search + apply to all matching
python scripts/gmail_handler.py organize "Label Name" "search query"
```

## Filters

```bash
# Create auto-filter (find/create label + set filter)
python scripts/gmail_handler.py create-filter "Label Name" "from:example.com"

# List existing filters
python scripts/gmail_handler.py list-filters
```

## Gmail Search Operators

- `from:sender@example.com`
- `to:recipient@example.com`
- `subject:keyword`
- `is:unread` / `is:read`
- `after:2025/01/01` / `before:2025/12/31`
- `has:attachment`
- `label:INBOX` / `label:SENT`
- `in:inbox` / `in:sent` / `in:trash`

## Examples

```bash
# Check unread emails
python scripts/gmail_handler.py inbox --unread --limit=5

# Search Linear notifications
python scripts/gmail_handler.py search "from:linear.app is:unread"

# Search by subject and date
python scripts/gmail_handler.py search "subject:Invoice after:2025/01/01"

# Read specific email
python scripts/gmail_handler.py read 18d5a2b3c4d5e6f7

# Create a draft (user reviews and sends)
python scripts/gmail_handler.py draft-create "team@publica.la" "Update" "Status report"

# Organize all Vercel emails under a label
python scripts/gmail_handler.py organize "Vercel" "from:vercel.com"

# Auto-filter future Linear emails
python scripts/gmail_handler.py create-filter "Linear" "from:linear.app"
```

## Output Format

All commands return JSON with `{success, data}` wrapper.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Token refresh failed` | Invalid credentials | Re-run setup, check .env |
| `401 Unauthorized` | Token expired/revoked | Get new refresh token |
| `403 Forbidden` | Scope not authorized | Re-authorize with correct scopes |
