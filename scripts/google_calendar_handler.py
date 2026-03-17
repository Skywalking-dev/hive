#!/usr/bin/env python3
"""
Google Calendar API handler for Hive.
Read calendar events, check availability, list calendars.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode, quote

from dotenv import load_dotenv

load_dotenv()

CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
TZ_NAME = "America/Argentina/Buenos_Aires"
TZ_OFFSET = timezone(timedelta(hours=-3))


def get_config() -> tuple[str, str, str]:
    client_id = os.environ.get("GOOGLE_CALENDAR_CLIENT_ID") or os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CALENDAR_CLIENT_SECRET") or os.environ.get("GMAIL_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_CALENDAR_REFRESH_TOKEN")

    if not client_id:
        raise ValueError("GOOGLE_CALENDAR_CLIENT_ID (or GMAIL_CLIENT_ID) not set in environment")
    if not client_secret:
        raise ValueError("GOOGLE_CALENDAR_CLIENT_SECRET (or GMAIL_CLIENT_SECRET) not set in environment")
    if not refresh_token:
        raise ValueError("GOOGLE_CALENDAR_REFRESH_TOKEN not set in environment")

    return client_id, client_secret, refresh_token


def get_access_token() -> str:
    """Get access token using refresh token."""
    client_id, client_secret, refresh_token = get_config()

    data = urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode("utf-8")

    req = Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["access_token"]
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise ValueError(f"Token refresh failed: {error_body}")


def api_get(path: str) -> dict:
    """GET request to Calendar API."""
    token = get_access_token()
    url = f"{CALENDAR_API_BASE}/{path}"
    req = Request(url, headers={"Authorization": f"Bearer {token}"}, method="GET")
    try:
        with urlopen(req, timeout=30) as resp:
            return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_msg = json.loads(error_body).get("error", {}).get("message", error_body)
        except Exception:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def api_post(path: str, body: dict) -> dict:
    """POST request to Calendar API."""
    token = get_access_token()
    url = f"{CALENDAR_API_BASE}/{path}"
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=30) as resp:
            return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_msg = json.loads(error_body).get("error", {}).get("message", error_body)
        except Exception:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def now_local() -> datetime:
    return datetime.now(TZ_OFFSET)


def format_dt(dt: datetime) -> str:
    """ISO 8601 with offset, e.g. 2025-01-27T00:00:00-03:00"""
    return dt.isoformat()


def format_event(item: dict) -> dict:
    start = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date")
    end = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date")
    is_all_day = "date" in item.get("start", {}) and "dateTime" not in item.get("start", {})
    return {
        "id": item.get("id", ""),
        "summary": item.get("summary", "(Sin titulo)"),
        "description": item.get("description", ""),
        "location": item.get("location", ""),
        "start": start,
        "end": end,
        "isAllDay": is_all_day,
        "status": item.get("status", "confirmed"),
        "htmlLink": item.get("htmlLink", ""),
        "hangoutLink": item.get("hangoutLink", ""),
        "attendees": [
            {
                "email": a.get("email", ""),
                "name": a.get("displayName", ""),
                "responseStatus": a.get("responseStatus", "needsAction"),
            }
            for a in item.get("attendees", [])
        ],
        "organizer": {
            "email": item.get("organizer", {}).get("email", ""),
            "name": item.get("organizer", {}).get("displayName", ""),
        },
    }


def get_events_between(calendar_id: str, start: datetime, end: datetime) -> dict:
    params = urlencode({
        "timeMin": format_dt(start),
        "timeMax": format_dt(end),
        "singleEvents": "true",
        "orderBy": "startTime",
        "maxResults": 100,
    })
    path = f"calendars/{quote(calendar_id, safe='')}/events?{params}"
    result = api_get(path)
    if not result["success"]:
        return result
    events = [format_event(item) for item in result["data"].get("items", [])]
    return {
        "success": True,
        "data": {
            "period": {
                "start": start.strftime("%Y-%m-%d %H:%M"),
                "end": end.strftime("%Y-%m-%d %H:%M"),
            },
            "count": len(events),
            "events": events,
        },
    }


def cmd_today(calendar_id: str) -> dict:
    now = now_local()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return get_events_between(calendar_id, start, end)


def cmd_week(calendar_id: str) -> dict:
    now = now_local()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = (start + timedelta(days=7)).replace(hour=23, minute=59, second=59)
    return get_events_between(calendar_id, start, end)


def cmd_list(calendar_id: str, days: int) -> dict:
    now = now_local()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = (start + timedelta(days=days)).replace(hour=23, minute=59, second=59)
    return get_events_between(calendar_id, start, end)


def cmd_get(calendar_id: str, event_id: str) -> dict:
    path = f"calendars/{quote(calendar_id, safe='')}/events/{quote(event_id, safe='')}"
    result = api_get(path)
    if not result["success"]:
        return result
    return {"success": True, "data": format_event(result["data"])}


def cmd_calendars() -> dict:
    result = api_get("users/me/calendarList")
    if not result["success"]:
        return result
    calendars = [
        {
            "id": c.get("id", ""),
            "summary": c.get("summary", ""),
            "description": c.get("description", ""),
            "primary": c.get("primary", False),
            "accessRole": c.get("accessRole", ""),
            "backgroundColor": c.get("backgroundColor", ""),
        }
        for c in result["data"].get("items", [])
    ]
    return {"success": True, "data": {"calendars": calendars}}


def cmd_freebusy(start_date: str, end_date: str) -> dict:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").replace(
            hour=0, minute=0, second=0, tzinfo=TZ_OFFSET
        )
        end = datetime.strptime(end_date, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, tzinfo=TZ_OFFSET
        )
    except ValueError as e:
        return {"success": False, "error": f"Invalid date format (use YYYY-MM-DD): {e}"}

    body = {
        "timeMin": format_dt(start),
        "timeMax": format_dt(end),
        "items": [{"id": "primary"}],
    }
    result = api_post("freeBusy", body)
    if not result["success"]:
        return result

    busy = result["data"].get("calendars", {}).get("primary", {}).get("busy", [])
    return {
        "success": True,
        "data": {
            "period": {
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
            },
            "busySlots": [{"start": s["start"], "end": s["end"]} for s in busy],
            "busyCount": len(busy),
        },
    }


def cmd_search(calendar_id: str, query: str, days: int) -> dict:
    now = now_local()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = (start + timedelta(days=days)).replace(hour=23, minute=59, second=59)

    params = urlencode({
        "timeMin": format_dt(start),
        "timeMax": format_dt(end),
        "q": query,
        "singleEvents": "true",
        "orderBy": "startTime",
        "maxResults": 50,
    })
    path = f"calendars/{quote(calendar_id, safe='')}/events?{params}"
    result = api_get(path)
    if not result["success"]:
        return result
    events = [format_event(item) for item in result["data"].get("items", [])]
    return {
        "success": True,
        "data": {
            "query": query,
            "days": days,
            "count": len(events),
            "events": events,
        },
    }


def print_setup_instructions(client_id: Optional[str]) -> dict:
    """Print OAuth setup instructions (no local server, instructions only)."""
    if not client_id:
        print("""
Google Calendar OAuth Setup - Step 1: Get Credentials
======================================================

1. Go to: https://console.cloud.google.com/
2. Use existing project (same as Gmail) or create new.
3. Enable Google Calendar API:
   - APIs & Services > Enable APIs and Services
   - Search "Google Calendar API" > Enable
4. If reusing Gmail credentials, skip to Step 2.
   Otherwise create OAuth credentials:
   - APIs & Services > Credentials > Create Credentials
   - OAuth client ID > Desktop app
   - Download JSON and extract client_id + client_secret
5. Set env vars:
   export GOOGLE_CALENDAR_CLIENT_ID="your-client-id"   # or reuse GMAIL_CLIENT_ID
   export GOOGLE_CALENDAR_CLIENT_SECRET="your-secret"  # or reuse GMAIL_CLIENT_SECRET
6. Re-run: python google_calendar_handler.py setup
""")
        return {"success": True, "data": {"message": "Step 1 instructions printed"}}

    scopes = " ".join([
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events.readonly",
    ])
    params = urlencode({
        "client_id": client_id,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "response_type": "code",
        "scope": scopes,
        "access_type": "offline",
        "prompt": "consent",
    })
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"

    print(f"""
Google Calendar OAuth Setup - Step 2: Get Refresh Token
========================================================

Option A - OAuth Playground (recommended, no local server needed):
  1. Go to: https://developers.google.com/oauthplayground/
  2. Click gear icon > check "Use your own OAuth credentials"
  3. Enter your Client ID and Client Secret
  4. In Step 1, select these scopes:
       https://www.googleapis.com/auth/calendar.readonly
       https://www.googleapis.com/auth/calendar.events.readonly
  5. Click "Authorize APIs" and complete the flow
  6. In Step 2, click "Exchange authorization code for tokens"
  7. Copy the "Refresh token" value

Option B - Manual auth URL:
  1. Open this URL in your browser:

     {auth_url}

  2. Authorize access
  3. Copy the authorization code shown
  4. Exchange code for tokens (replace CODE below):

     curl -X POST https://oauth2.googleapis.com/token \\
       -d "client_id={client_id}" \\
       -d "client_secret=YOUR_CLIENT_SECRET" \\
       -d "code=CODE" \\
       -d "grant_type=authorization_code" \\
       -d "redirect_uri=urn:ietf:wg:oauth:2.0:oob"

  5. Copy the "refresh_token" from the response

Set env var:
  export GOOGLE_CALENDAR_REFRESH_TOKEN="your-refresh-token"

Then test:
  python google_calendar_handler.py today
  python google_calendar_handler.py week
  python google_calendar_handler.py list --days=14
""")
    return {"success": True, "data": {"message": "Setup instructions printed"}}


def main():
    parser = argparse.ArgumentParser(description="Google Calendar API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    subparsers.add_parser("setup", help="Print OAuth setup instructions")

    # today
    today_p = subparsers.add_parser("today", help="Events for today")
    today_p.add_argument("--calendar", default="primary", help="Calendar ID")

    # week
    week_p = subparsers.add_parser("week", help="Events for this week (7 days)")
    week_p.add_argument("--calendar", default="primary", help="Calendar ID")

    # list
    list_p = subparsers.add_parser("list", help="Events for N days")
    list_p.add_argument("--days", type=int, default=7, help="Number of days")
    list_p.add_argument("--calendar", default="primary", help="Calendar ID")

    # get
    get_p = subparsers.add_parser("get", help="Get event details")
    get_p.add_argument("event_id", help="Event ID")
    get_p.add_argument("--calendar", default="primary", help="Calendar ID")

    # calendars
    subparsers.add_parser("calendars", help="List all calendars")

    # freebusy
    fb_p = subparsers.add_parser("freebusy", help="Check free/busy slots")
    fb_p.add_argument("start", help="Start date (YYYY-MM-DD)")
    fb_p.add_argument("end", help="End date (YYYY-MM-DD)")

    # search
    search_p = subparsers.add_parser("search", help="Search events")
    search_p.add_argument("query", help="Search term")
    search_p.add_argument("--days", type=int, default=30, help="Days to search")
    search_p.add_argument("--calendar", default="primary", help="Calendar ID")

    args = parser.parse_args()

    try:
        if args.command == "setup":
            client_id = os.environ.get("GOOGLE_CALENDAR_CLIENT_ID") or os.environ.get("GMAIL_CLIENT_ID")
            result = print_setup_instructions(client_id)
        elif args.command == "today":
            result = cmd_today(args.calendar)
        elif args.command == "week":
            result = cmd_week(args.calendar)
        elif args.command == "list":
            result = cmd_list(args.calendar, args.days)
        elif args.command == "get":
            result = cmd_get(args.calendar, args.event_id)
        elif args.command == "calendars":
            result = cmd_calendars()
        elif args.command == "freebusy":
            result = cmd_freebusy(args.start, args.end)
        elif args.command == "search":
            result = cmd_search(args.calendar, args.query, args.days)
        else:
            result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
