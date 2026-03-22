---
name: gmail
description: Read and search Gmail inbox, manage drafts, organize with labels, and create filters. Use when user needs to check email, compose drafts, or organize messages.
allowed-tools: Bash, Read
---

# Gmail API

Read inbox, search emails, manage drafts, labels, and filters via unified bash handler.

## Guardrails

- **NEVER send emails directly without user confirmation.** Use `draft` to compose; user reviews and sends manually from Gmail — or explicitly confirms `send`.
- Always confirm with user before creating a draft on their behalf.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env` (or `GOOGLE_CLIENT_ID`)
- `GMAIL_CLIENT_SECRET` in `.env` (or `GOOGLE_CLIENT_SECRET`)
- `GMAIL_REFRESH_TOKEN` in `.env` (or `GOOGLE_REFRESH_TOKEN`)

## Quick Commands

```bash
# List inbox
scripts/google_handler.sh gmail list [--max=10] [--unread]

# List with custom query
scripts/google_handler.sh gmail list --query="from:linear.app" --max=20

# Search emails
scripts/google_handler.sh gmail search "query" [--max=10]

# Read full email
scripts/google_handler.sh gmail read <message_id>

# List labels
scripts/google_handler.sh gmail labels
```

## Drafts (safe - does NOT auto-send)

```bash
# List drafts
scripts/google_handler.sh gmail drafts [--max=10]

# Create draft
scripts/google_handler.sh gmail draft <to> <subject> <body>

# Update draft
scripts/google_handler.sh gmail draft-update <draft_id> [--to=x] [--subject=y] [--body=z]

# Update with stdin body
echo "body" | scripts/google_handler.sh gmail draft-update <draft_id> --subject=x --body-stdin

# Delete draft
scripts/google_handler.sh gmail draft-delete <draft_id>
```

## Send (requires explicit user confirmation)

```bash
# Send email directly
scripts/google_handler.sh gmail send <to> <subject> <body>
```

## Labels & Organization

```bash
# Create label
scripts/google_handler.sh gmail create-label <name>

# Apply label to messages
scripts/google_handler.sh gmail apply-label <labelId> <msgId1> [msgId2...]

# Organize: find/create label + search + apply to all matching
scripts/google_handler.sh gmail organize "Label Name" "search query"
```

## Filters

```bash
# Create auto-filter (find/create label + set filter)
scripts/google_handler.sh gmail create-filter "Label Name" "from:example.com"

# List existing filters
scripts/google_handler.sh gmail list-filters
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
scripts/google_handler.sh gmail list --unread --max=5

# Search Linear notifications
scripts/google_handler.sh gmail search "from:linear.app is:unread"

# Read specific email
scripts/google_handler.sh gmail read 18d5a2b3c4d5e6f7

# Create a draft (user reviews and sends)
scripts/google_handler.sh gmail draft "team@publica.la" "Update" "Status report"

# Organize all Vercel emails under a label
scripts/google_handler.sh gmail organize "Vercel" "from:vercel.com"

# Auto-filter future Linear emails
scripts/google_handler.sh gmail create-filter "Linear" "from:linear.app"
```

## Output Format

All commands return JSON `{"success": true, "data": {...}}`.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Token refresh request failed` | Invalid credentials | Check .env vars |
| `401 Unauthorized` | Token expired/revoked | Get new refresh token |
| `403 Forbidden` | Scope not authorized | Re-authorize with correct scopes |
