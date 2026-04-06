---
name: slack-api
description: Interact with Slack via Python script. Read threads, post messages, upload files. Use when user asks for Slack content, mentions thread URLs, or needs to send messages.
allowed-tools: Bash, Read
---

# Slack API

Read and write to Slack channels and threads using the Python script at `scripts/slack_handler.py`.

## Prerequisites
- `SLACK_BOT_TOKEN` in `.env`
- Bot must be invited to target channels

## Quick Commands

```bash
# Read a thread
python scripts/slack_handler.py read "https://workspace.slack.com/archives/C123/p456"

# Post a message
python scripts/slack_handler.py send C123456 "Hello from Hive"

# Reply to thread
python scripts/slack_handler.py reply C123456 1234567890.123456 "Thread reply"

# Upload file
python scripts/slack_handler.py upload C123456 /path/to/file.pdf
```

## Output Format

All commands return JSON:
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `not_in_channel` | Bot not in channel | Invite bot or use public channel |
| `channel_not_found` | Invalid channel ID | Use channel ID (C...) not name |
| `ratelimited` | Too many requests | Wait and retry |

## Block Kit

For rich messages, use Block Kit JSON structure:
- `header` → title
- `section` → content with optional `accessory`
- `actions` → buttons
- `context` → footer/metadata

Each interactive element needs unique `action_id`.

## mrkdwn Formatting

Slack uses **mrkdwn**, not standard Markdown. Many patterns silently break.

### Critical differences

| What you want | Markdown (WRONG) | Slack mrkdwn (RIGHT) |
|---|---|---|
| Bold | `**text**` | `*text*` |
| Italic | `*text*` | `_text_` |
| Strikethrough | `~~text~~` | `~text~` |
| Link | `[text](url)` | `<url\|text>` |

### What does NOT work in Slack

- Tables (pipe syntax) — use bold label pairs or code blocks
- Headers (`#`, `##`) — use `*bold text*` with blank lines
- `---` horizontal rules
- Syntax-highlighted code fences (`` ```python ``)
- Images `![alt](url)`
- HTML tags

### Patterns

**Sections** (replace headers): `*Section title*` + blank line
**Structured data** (replace tables): `*Label:* value` on each line
**Status lists**: `:white_check_mark: *Item* — done` / `:x: *Item* — pending`
**Code blocks**: triple backticks on their own lines, no language tag
**Lists**: `• Item` (bullet character, not `-`)
