#!/usr/bin/env python3
"""
Gmail API handler for Hive.
Read inbox, search emails, read full messages, send emails.
"""

import os
import sys
import json
import base64
import argparse
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def get_config() -> tuple[str, str, str]:
    client_id = os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
    refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")

    if not client_id:
        raise ValueError("GMAIL_CLIENT_ID not set in environment")
    if not client_secret:
        raise ValueError("GMAIL_CLIENT_SECRET not set in environment")
    if not refresh_token:
        raise ValueError("GMAIL_REFRESH_TOKEN not set in environment")

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


def api_call(endpoint: str, method: str = "GET", data: Optional[dict] = None) -> dict:
    """Make a Gmail API call."""
    token = get_access_token()
    url = f"{GMAIL_API_BASE}/{endpoint}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "data": result}
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", error_body)
        except:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_inbox(limit: int = 10, unread_only: bool = False) -> dict:
    """List inbox messages."""
    query = "in:inbox"
    if unread_only:
        query += " is:unread"

    params = urlencode({"q": query, "maxResults": limit})
    result = api_call(f"messages?{params}")

    if not result["success"]:
        return result

    messages = result["data"].get("messages", [])
    detailed = []

    for msg in messages:
        detail = api_call(f"messages/{msg['id']}?format=metadata&metadataHeaders=From&metadataHeaders=To&metadataHeaders=Subject&metadataHeaders=Date")
        if detail["success"]:
            headers = {h["name"]: h["value"] for h in detail["data"].get("payload", {}).get("headers", [])}
            detailed.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": detail["data"].get("snippet", ""),
                "labels": detail["data"].get("labelIds", []),
            })

    return {
        "success": True,
        "data": {
            "count": len(detailed),
            "query": query,
            "messages": detailed,
        },
    }


def search_emails(query: str, limit: int = 10) -> dict:
    """Search emails with Gmail query syntax."""
    params = urlencode({"q": query, "maxResults": limit})
    result = api_call(f"messages?{params}")

    if not result["success"]:
        return result

    messages = result["data"].get("messages", [])
    detailed = []

    for msg in messages:
        detail = api_call(f"messages/{msg['id']}?format=metadata&metadataHeaders=From&metadataHeaders=To&metadataHeaders=Subject&metadataHeaders=Date")
        if detail["success"]:
            headers = {h["name"]: h["value"] for h in detail["data"].get("payload", {}).get("headers", [])}
            detailed.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": detail["data"].get("snippet", ""),
                "labels": detail["data"].get("labelIds", []),
            })

    return {
        "success": True,
        "data": {
            "count": len(detailed),
            "query": query,
            "messages": detailed,
        },
    }


def read_email(message_id: str) -> dict:
    """Read full email content."""
    result = api_call(f"messages/{message_id}?format=full")

    if not result["success"]:
        return result

    data = result["data"]
    headers = {h["name"]: h["value"] for h in data.get("payload", {}).get("headers", [])}

    # Extract body
    body = ""
    payload = data.get("payload", {})

    def extract_body(part: dict) -> str:
        """Recursively extract text body from message parts."""
        if part.get("mimeType") == "text/plain":
            body_data = part.get("body", {}).get("data", "")
            if body_data:
                return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
        elif part.get("mimeType") == "text/html" and not body:
            body_data = part.get("body", {}).get("data", "")
            if body_data:
                return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")

        for subpart in part.get("parts", []):
            result = extract_body(subpart)
            if result:
                return result
        return ""

    body = extract_body(payload)
    if not body and payload.get("body", {}).get("data"):
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    return {
        "success": True,
        "data": {
            "id": message_id,
            "threadId": data.get("threadId"),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "labels": data.get("labelIds", []),
            "body": body,
        },
    }


def list_labels() -> dict:
    """List Gmail labels."""
    result = api_call("labels")

    if not result["success"]:
        return result

    labels = [
        {"id": l["id"], "name": l["name"], "type": l.get("type", "user")}
        for l in result["data"].get("labels", [])
    ]

    return {
        "success": True,
        "data": {"labels": labels},
    }


def print_setup_instructions():
    """Print OAuth setup instructions."""
    instructions = """
Gmail OAuth Setup Instructions
==============================

1. Go to Google Cloud Console: https://console.cloud.google.com/

2. Create a new project (or select existing)

3. Enable Gmail API:
   - Go to "APIs & Services" > "Enable APIs and Services"
   - Search for "Gmail API" and enable it

4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON

5. Get your credentials:
   - GMAIL_CLIENT_ID: from the downloaded JSON
   - GMAIL_CLIENT_SECRET: from the downloaded JSON

6. Get refresh token using OAuth Playground:
   - Go to: https://developers.google.com/oauthplayground/
   - Click gear icon, check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret
   - In Step 1, select Gmail API v1 scopes:
     - https://www.googleapis.com/auth/gmail.readonly
     - https://www.googleapis.com/auth/gmail.send
   - Click "Authorize APIs" and complete the flow
   - In Step 2, click "Exchange authorization code for tokens"
   - Copy the "Refresh token" value

7. Set environment variables:
   export GMAIL_CLIENT_ID="your-client-id"
   export GMAIL_CLIENT_SECRET="your-client-secret"
   export GMAIL_REFRESH_TOKEN="your-refresh-token"

Or add to your .env file.
"""
    print(instructions)
    return {"success": True, "data": {"message": "Setup instructions printed"}}


def main():
    parser = argparse.ArgumentParser(description="Gmail API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Setup
    subparsers.add_parser("setup", help="Print OAuth setup instructions")

    # Inbox
    inbox_parser = subparsers.add_parser("inbox", help="List inbox messages")
    inbox_parser.add_argument("--limit", type=int, default=10, help="Max messages")
    inbox_parser.add_argument("--unread", action="store_true", help="Unread only")

    # Search
    search_parser = subparsers.add_parser("search", help="Search emails")
    search_parser.add_argument("query", help="Gmail search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # Read
    read_parser = subparsers.add_parser("read", help="Read full email")
    read_parser.add_argument("message_id", help="Message ID")

    # Labels
    subparsers.add_parser("labels", help="List Gmail labels")

    args = parser.parse_args()

    try:
        if args.command == "setup":
            result = print_setup_instructions()
        elif args.command == "inbox":
            result = list_inbox(args.limit, args.unread)
        elif args.command == "search":
            result = search_emails(args.query, args.limit)
        elif args.command == "read":
            result = read_email(args.message_id)
        elif args.command == "labels":
            result = list_labels()
        else:
            result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
