---
name: whatsapp
description: Send WhatsApp Business messages via Cloud API v22 - text, templates, media, interactive buttons/lists, flows, location, contacts, reactions. Use when user needs to send messages, check templates, or manage WhatsApp Business.
allowed-tools: Bash, Read
---

# WhatsApp Business Cloud API v22

Send messages via WhatsApp Business Cloud API using Python CLI.

## Prerequisites
- `WHATSAPP_TOKEN` in `.env` (Meta access token)
- `WHATSAPP_PHONE_ID` in `.env` (Phone number ID)
- `WHATSAPP_WABA_ID` in `.env` (optional, for templates listing)
- Approved message templates for outbound messages outside 24h window

## Quick Commands

```bash
# Send text message (within 24h window)
python scripts/whatsapp_handler.py send 5491123456789 "Hello!"
python scripts/whatsapp_handler.py send 5491123456789 "Check https://example.com" --preview-url

# Send template message (any time)
python scripts/whatsapp_handler.py template 5491123456789 hello_world
python scripts/whatsapp_handler.py template 5491123456789 order_update --lang es --params='["ORD-123","shipped"]'
python scripts/whatsapp_handler.py template 5491123456789 promo --header-params='["Summer Sale"]' --params='["20%"]'

# Send media
python scripts/whatsapp_handler.py media 5491123456789 image https://example.com/img.jpg "Caption"
python scripts/whatsapp_handler.py media 5491123456789 video https://example.com/vid.mp4
python scripts/whatsapp_handler.py media 5491123456789 document https://example.com/doc.pdf

# Interactive buttons (max 3)
python scripts/whatsapp_handler.py buttons 5491123456789 "Want to proceed?" '[{"id":"yes","title":"Yes"},{"id":"no","title":"No"}]' --header "Confirm" --footer "Reply to continue"

# Interactive list
python scripts/whatsapp_handler.py list 5491123456789 "Choose an option" "View Options" '[{"title":"Products","rows":[{"id":"1","title":"Widget","description":"$10"},{"id":"2","title":"Gadget","description":"$20"}]}]'

# Location
python scripts/whatsapp_handler.py location 5491123456789 -40.1567 -71.3492 --name "Office" --address "San Martin de los Andes"

# Contact card
python scripts/whatsapp_handler.py contact 5491123456789 '{"name":{"formatted_name":"John Doe"},"phones":[{"phone":"5491123456789"}]}'

# React to message
python scripts/whatsapp_handler.py react 5491123456789 wamid.xxxxx "👍"

# Mark as read
python scripts/whatsapp_handler.py read wamid.xxxxx

# WhatsApp Flow (interactive form)
python scripts/whatsapp_handler.py flow 5491123456789 123456 "Start Survey" "Please complete this form" --screen "WELCOME"

# List templates
python scripts/whatsapp_handler.py templates
python scripts/whatsapp_handler.py templates --status APPROVED

# Phone number quality
python scripts/whatsapp_handler.py phone-info
```

## Message Types

| Type | 24h Window | Command |
|------|-----------|---------|
| Text | Required | `send` |
| Template | Not needed | `template` |
| Media | Required | `media` |
| Buttons | Required | `buttons` |
| List | Required | `list` |
| Location | Required | `location` |
| Contact | Required | `contact` |
| Reaction | Required | `react` |
| Flow | Required | `flow` |

## Phone Number Format
- Full international format without `+`: `5491123456789`
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
| `131026` | Message undeliverable | Check recipient number |
| `130429` | Rate limit hit | Slow down sending |

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
