---
description: Read Gmail inbox, search emails, or read full messages
argument-hint: inbox | search <query> | read <id>
---

Read emails using the gmail skill.

> [!IMPORTANT]
> Follow the rules in the [gmail] skill.

# Usage

## Check inbox
`/gmail inbox` - List recent inbox messages
`/gmail inbox --unread` - List unread only

## Search emails
`/gmail search "from:linear.app is:unread"` - Search with Gmail operators

## Read full email
`/gmail read <message_id>` - Get full email content

# Prerequisites
- `GMAIL_CLIENT_ID` in `.env`
- `GMAIL_CLIENT_SECRET` in `.env`
- `GMAIL_REFRESH_TOKEN` in `.env`

Run `python scripts/gmail_handler.py setup` for OAuth setup instructions.
