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
