---
name: google-calendar
description: Read Google Calendar events, check availability, and search events. Use when user needs schedule info, today's events, or free/busy status.
allowed-tools: Bash, Read
---

# Google Calendar API

Read-only calendar access via Python script.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env` (or `GOOGLE_CALENDAR_CLIENT_ID`)
- `GMAIL_CLIENT_SECRET` in `.env` (or `GOOGLE_CALENDAR_CLIENT_SECRET`)
- `GOOGLE_CALENDAR_REFRESH_TOKEN` in `.env`

## First-time Setup

```bash
python scripts/google_calendar_handler.py setup
```

## Commands

```bash
# Today's events
python scripts/google_calendar_handler.py today

# This week's events
python scripts/google_calendar_handler.py week

# Events for N days
python scripts/google_calendar_handler.py list [--days=7]

# Get event details
python scripts/google_calendar_handler.py get <event_id>

# List calendars
python scripts/google_calendar_handler.py calendars

# Check free/busy availability
python scripts/google_calendar_handler.py freebusy <start_date> <end_date>

# Search events
python scripts/google_calendar_handler.py search "query" [--days=30]
```

## Options

- `--calendar=<id>` - Use specific calendar (default: `primary`)
- `--days=<n>` - Number of days to query

## Examples

```bash
# Check today's schedule
python scripts/google_calendar_handler.py today

# See week ahead
python scripts/google_calendar_handler.py week

# Next 14 days
python scripts/google_calendar_handler.py list --days=14

# Search for standup meetings
python scripts/google_calendar_handler.py search "standup" --days=7

# Check availability for date range
python scripts/google_calendar_handler.py freebusy 2026-02-10 2026-02-14

# List all calendars
python scripts/google_calendar_handler.py calendars
```

## Output

All commands return JSON with `{success, data}` wrapper:
- `today`/`week`/`list`: `{period: {start, end}, count, events: [{id, summary, description, location, start, end, isAllDay, status, htmlLink, hangoutLink, attendees, organizer}]}`
- `get`: Single event object
- `calendars`: `[{id, summary, description, primary, accessRole, backgroundColor}]`
- `freebusy`: `{period, busySlots: [{start, end}], busyCount}`
- `search`: `{query, days, count, events: [...]}`
