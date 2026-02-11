---
name: gmail
description: Read and search Gmail inbox, read full emails using Gmail API. Use when user needs to check email or search messages.
allowed-tools: Bash, Read
---

# Gmail API

Read inbox, search emails, and read full messages via Python script.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env`
- `GMAIL_CLIENT_SECRET` in `.env`
- `GMAIL_REFRESH_TOKEN` in `.env`

## First-time Setup

```bash
python scripts/gmail_handler.py setup
```

This prints instructions for:
1. Creating Google Cloud OAuth credentials
2. Enabling Gmail API
3. Getting refresh token via OAuth Playground

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
```

## Output Format

All commands return JSON:

```json
{
  "success": true,
  "data": {...}
}
```

### inbox/search
```json
{
  "count": 5,
  "query": "in:inbox is:unread",
  "messages": [
    {
      "id": "abc123",
      "from": "sender@example.com",
      "to": "me@example.com",
      "subject": "Hello",
      "date": "Mon, 20 Jan 2025 10:00:00 -0300",
      "snippet": "Preview text...",
      "labels": ["INBOX", "UNREAD"]
    }
  ]
}
```

### read
```json
{
  "id": "abc123",
  "threadId": "thread123",
  "from": "sender@example.com",
  "to": "me@example.com",
  "subject": "Hello",
  "date": "Mon, 20 Jan 2025 10:00:00 -0300",
  "labels": ["INBOX"],
  "body": "Full email content..."
}
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Token refresh failed` | Invalid credentials | Re-run setup, check .env |
| `401 Unauthorized` | Token expired/revoked | Get new refresh token |
| `403 Forbidden` | Scope not authorized | Re-authorize with correct scopes |
