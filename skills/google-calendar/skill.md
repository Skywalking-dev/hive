---
name: google-calendar
description: Read Google Calendar events, check availability, and search events. Use when user needs schedule info, today's events, or free/busy status.
allowed-tools: Bash, Read
---

# Google Calendar API

Read-only calendar access via unified bash handler.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env` (or `GOOGLE_CLIENT_ID` / `GOOGLE_CALENDAR_CLIENT_ID`)
- `GMAIL_CLIENT_SECRET` in `.env` (or `GOOGLE_CLIENT_SECRET` / `GOOGLE_CALENDAR_CLIENT_SECRET`)
- `GOOGLE_CALENDAR_REFRESH_TOKEN` in `.env` (or `GOOGLE_REFRESH_TOKEN`)

## Commands

```bash
# Today's events
scripts/google_handler.sh calendar today

# This week's events
scripts/google_handler.sh calendar week

# Events for N days
scripts/google_handler.sh calendar list --days=7

# Get event details
scripts/google_handler.sh calendar get <event_id>

# List calendars
scripts/google_handler.sh calendar calendars

# Check free/busy availability
scripts/google_handler.sh calendar freebusy 2026-02-10 2026-02-14

# Search events
scripts/google_handler.sh calendar search "standup" --days=30

# Create event
scripts/google_handler.sh calendar create --summary="Meeting" --start="2026-04-01T10:00:00-03:00" --end="2026-04-01T11:00:00-03:00" --desc="Agenda" --loc="Zoom"

# Delete event
scripts/google_handler.sh calendar delete <event_id>
```

## Options

- `--calendar=<id>` — Use specific calendar (default: `primary`)
- `--days=<n>` — Number of days to query
- `--summary=<title>` — Event title (create)
- `--start=<iso>` — ISO 8601 datetime (create)
- `--end=<iso>` — ISO 8601 datetime (create)
- `--desc=<text>` — Description (create)
- `--loc=<text>` — Location (create)

## Output

All commands return JSON `{"success": true, "data": {...}}`:
- `today`/`week`/`list`: `{period: {start, end}, count, events: [{id, summary, description, location, start, end, isAllDay, status, htmlLink, hangoutLink, attendees, organizer}]}`
- `get`: Single event object
- `calendars`: `[{id, summary, description, primary, accessRole, backgroundColor}]`
- `freebusy`: `{period, busySlots: [{start, end}], busyCount}`
- `search`: `{query, days, count, events: [...]}`
- `create`: `{id, summary, htmlLink, start, end}`
- `delete`: `{deleted: true, eventId}`
