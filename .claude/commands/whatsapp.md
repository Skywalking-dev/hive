---
description: Send WhatsApp messages or check message status
argument-hint: send <number> <message> | status <message_id> | templates
---

Send and manage WhatsApp Business messages using the whatsapp skill.

> [!IMPORTANT]
> Follow the rules in the [whatsapp] skill.

# Usage

## Send message
- `send <phone_number> <message>` - send text message
- `send <phone_number> --template=<name>` - send template message

## Status
- `status <message_id>` - check delivery status

## Templates
- `templates` - list available message templates

# Prerequisites
- `WHATSAPP_TOKEN` in `.env`
- `WHATSAPP_PHONE_ID` in `.env`
- Approved message templates for non-24h conversations
