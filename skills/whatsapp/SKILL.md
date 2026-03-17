---
name: whatsapp
description: Send WhatsApp Business messages and check delivery status. Use when user needs to send messages, check templates, or verify delivery.
allowed-tools: Bash, Read
---

# WhatsApp Business API

Send messages via WhatsApp Business Cloud API using Python script.

## Prerequisites
- `WHATSAPP_TOKEN` in `.env` (Meta access token)
- `WHATSAPP_PHONE_ID` in `.env` (Phone number ID)
- Approved message templates for outbound messages outside 24h window

## Quick Commands

```bash
# Send text message (within 24h window)
python scripts/whatsapp_handler.py send 5491123456789 "Hello!"

# Send template message (any time)
python scripts/whatsapp_handler.py template 5491123456789 hello_world

# Check message status
python scripts/whatsapp_handler.py status wamid.xxxxx

# List templates
python scripts/whatsapp_handler.py templates
```

## Message Types

### Text (24h window only)
```bash
python scripts/whatsapp_handler.py send <number> "Message text"
```

### Template (any time)
```bash
python scripts/whatsapp_handler.py template <number> <template_name> --params='["value1","value2"]'
```

### Media
```bash
python scripts/whatsapp_handler.py media <number> image https://example.com/image.jpg "Caption"
```

## Phone Number Format
- Use full international format without `+`: `5491123456789`
- No spaces, dashes, or parentheses

## Rate Limits
- 80 messages/second per phone number
- 1000 messages/24h for unverified business
- Templates have separate quality-based limits

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `131047` | Outside 24h, no template | Use template message |
| `131051` | Invalid phone number | Check format |
| `132000` | Template not approved | Wait for approval |

## Output Format

```json
{
  "success": true,
  "data": {
    "messaging_product": "whatsapp",
    "contacts": [{"wa_id": "5491123456789"}],
    "messages": [{"id": "wamid.xxxxx"}]
  }
}
```
