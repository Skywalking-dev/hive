---
description: Read or interact with Slack threads and channels
argument-hint: <slack_message_url> | send <channel> <message>
---

Read Slack threads or post messages using the slack-api skill.

> [!IMPORTANT]
> Follow the rules in the [slack-api] skill.

# Usage

## Read a thread
Provide a Slack message URL to fetch the full conversation.

## Send a message
Use `send <channel_id> <message>` to post to a channel.

# Prerequisites
- `SLACK_BOT_TOKEN` in `.env`
- Bot must have access to the target channel
