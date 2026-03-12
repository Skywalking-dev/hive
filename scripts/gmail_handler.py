#!/usr/bin/env python3
"""
Gmail API handler for Hive.
Read inbox, search emails, read full messages, manage drafts, labels, filters.

Security: send and draft-send commands are intentionally BLOCKED.
Use draft-create to compose, then review and send manually from Gmail.

Required scopes:
  https://www.googleapis.com/auth/gmail.readonly
  https://www.googleapis.com/auth/gmail.compose
  https://www.googleapis.com/auth/gmail.labels
  https://www.googleapis.com/auth/gmail.modify
"""

import os
import re
import sys
import json
import base64
import argparse
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

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
            raw = resp.read()
            if not raw:
                return {"success": True, "data": {}}
            result = json.loads(raw.decode("utf-8"))
            return {"success": True, "data": result}
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", error_body)
        except Exception:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def api_call_delete(endpoint: str) -> dict:
    """DELETE call; Gmail returns 204 No Content on success."""
    token = get_access_token()
    url = f"{GMAIL_API_BASE}/{endpoint}"

    req = Request(url, method="DELETE")
    req.add_header("Authorization", f"Bearer {token}")

    try:
        with urlopen(req, timeout=30) as resp:
            # 204 = success, body empty
            return {"success": True, "data": {}}
    except HTTPError as e:
        if e.code == 204:
            return {"success": True, "data": {}}
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", error_body)
        except Exception:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Inbox / Search / Read
# ---------------------------------------------------------------------------

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
        detail = api_call(
            f"messages/{msg['id']}?format=metadata"
            "&metadataHeaders=From&metadataHeaders=To"
            "&metadataHeaders=Subject&metadataHeaders=Date"
        )
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
        detail = api_call(
            f"messages/{msg['id']}?format=metadata"
            "&metadataHeaders=From&metadataHeaders=To"
            "&metadataHeaders=Subject&metadataHeaders=Date"
        )
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


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

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


def create_label(name: str) -> dict:
    """Create a new Gmail label."""
    result = api_call("labels", method="POST", data={
        "name": name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    })

    if not result["success"]:
        return result

    data = result["data"]
    return {
        "success": bool(data.get("id")),
        "data": {
            "id": data.get("id"),
            "name": data.get("name"),
        },
    }


def _find_or_create_label(name: str) -> tuple[bool, str, str]:
    """Return (created, label_id, label_name). Raises on failure."""
    labels_result = list_labels()
    if not labels_result["success"]:
        raise ValueError(f"Failed to list labels: {labels_result.get('error')}")

    for label in labels_result["data"]["labels"]:
        if label["name"].lower() == name.lower():
            return False, label["id"], label["name"]

    create_result = create_label(name)
    if not create_result["success"]:
        raise ValueError(f"Failed to create label '{name}': {create_result.get('error')}")

    return True, create_result["data"]["id"], create_result["data"]["name"]


def apply_label(label_id: str, message_ids: list[str]) -> dict:
    """Apply a label to one or more messages."""
    results = []
    for msg_id in message_ids:
        r = api_call(f"messages/{msg_id}/modify", method="POST", data={
            "addLabelIds": [label_id],
        })
        results.append({
            "messageId": msg_id,
            "success": r["success"],
            **({"error": r["error"]} if not r["success"] else {}),
        })

    successful = sum(1 for r in results if r["success"])
    return {
        "success": True,
        "data": {
            "labelId": label_id,
            "processed": len(results),
            "successful": successful,
            "results": results,
        },
    }


def organize(label_name: str, query: str) -> dict:
    """Find-or-create label, search messages, apply label to all matches."""
    try:
        created, label_id, label_name_final = _find_or_create_label(label_name)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    params = urlencode({"q": query, "maxResults": 100})
    search_result = api_call(f"messages?{params}")
    if not search_result["success"]:
        return search_result

    message_ids = [m["id"] for m in search_result["data"].get("messages", [])]

    if not message_ids:
        return {
            "success": True,
            "data": {
                "labelName": label_name_final,
                "labelId": label_id,
                "labelCreated": created,
                "query": query,
                "messagesFound": 0,
                "messagesLabeled": 0,
            },
        }

    apply_result = apply_label(label_id, message_ids)
    if not apply_result["success"]:
        return apply_result

    return {
        "success": True,
        "data": {
            "labelName": label_name_final,
            "labelId": label_id,
            "labelCreated": created,
            "query": query,
            "messagesFound": len(message_ids),
            "messagesLabeled": apply_result["data"]["successful"],
        },
    }


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

def _parse_query_to_criteria(query: str) -> dict:
    """Parse a Gmail search query string into Gmail filter criteria fields."""
    criteria: dict = {}

    m = re.search(r"from:(\S+)", query, re.IGNORECASE)
    if m:
        criteria["from"] = m.group(1)

    m = re.search(r"\bto:(\S+)", query, re.IGNORECASE)
    if m:
        criteria["to"] = m.group(1)

    m = re.search(r"subject:(.+?)(?:\s+(?:from|to|OR|AND)|$)", query, re.IGNORECASE)
    if m:
        criteria["subject"] = m.group(1).strip()

    # "from:X OR to:X" with same value — collapse to from only (Gmail API limitation)
    or_match = re.search(r"from:(\S+)\s+OR\s+to:(\S+)", query, re.IGNORECASE)
    if or_match and or_match.group(1) == or_match.group(2):
        criteria = {"from": or_match.group(1)}

    if not criteria:
        criteria["query"] = query

    return criteria


def create_filter(label_name: str, query: str) -> dict:
    """Create a Gmail filter that labels matching emails."""
    try:
        _, label_id, label_name_final = _find_or_create_label(label_name)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    criteria = _parse_query_to_criteria(query)

    result = api_call("settings/filters", method="POST", data={
        "criteria": criteria,
        "action": {"addLabelIds": [label_id]},
    })

    if not result["success"]:
        return result

    data = result["data"]
    return {
        "success": bool(data.get("id")),
        "data": {
            "filterId": data.get("id"),
            "labelName": label_name_final,
            "labelId": label_id,
            "criteria": criteria,
        },
    }


def list_filters() -> dict:
    """List all Gmail filters."""
    result = api_call("settings/filters")

    if not result["success"]:
        return result

    filters = [
        {
            "id": f["id"],
            "criteria": f.get("criteria", {}),
            "action": f.get("action", {}),
        }
        for f in result["data"].get("filter", [])
    ]

    return {
        "success": True,
        "data": {"filters": filters},
    }


# ---------------------------------------------------------------------------
# Drafts
# ---------------------------------------------------------------------------

def _build_raw_message(to: str, subject: str, body: str) -> str:
    """Build base64url-encoded RFC 2822 message."""
    lines = []
    if to:
        lines.append(f"To: {to}")
    lines.append(f"Subject: {subject}")
    lines.append("Content-Type: text/plain; charset=utf-8")
    lines.append("")
    lines.append(body)
    raw = "\r\n".join(lines)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).rstrip(b"=").decode("ascii")


def _get_draft(draft_id: str) -> dict:
    """Fetch a single draft and return normalized dict."""
    result = api_call(f"drafts/{draft_id}")
    if not result["success"]:
        return result

    data = result["data"]
    message = data.get("message", {})
    headers = {
        h["name"].lower(): h["value"]
        for h in message.get("payload", {}).get("headers", [])
    }

    def _extract(part: dict) -> str:
        if part.get("mimeType") == "text/plain":
            body_data = part.get("body", {}).get("data", "")
            if body_data:
                return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
        for subpart in part.get("parts", []):
            r = _extract(subpart)
            if r:
                return r
        return ""

    body = _extract(message.get("payload", {}))
    if not body:
        raw_data = message.get("payload", {}).get("body", {}).get("data", "")
        if raw_data:
            body = base64.urlsafe_b64decode(raw_data).decode("utf-8", errors="replace")

    return {
        "success": True,
        "data": {
            "id": data.get("id"),
            "messageId": message.get("id"),
            "threadId": message.get("threadId"),
            "to": headers.get("to", ""),
            "subject": headers.get("subject", ""),
            "snippet": message.get("snippet", ""),
            "body": body,
        },
    }


def list_drafts(limit: int = 10) -> dict:
    """List drafts with summary details."""
    params = urlencode({"maxResults": limit})
    result = api_call(f"drafts?{params}")

    if not result["success"]:
        return result

    drafts = []
    for draft in result["data"].get("drafts", []):
        detail = _get_draft(draft["id"])
        if detail["success"]:
            drafts.append(detail["data"])

    return {
        "success": True,
        "data": {
            "count": len(drafts),
            "drafts": drafts,
        },
    }


def draft_create(to: str, subject: str, body: str) -> dict:
    """Create a new draft."""
    if not subject:
        return {"success": False, "error": "subject is required"}

    encoded = _build_raw_message(to, subject, body)
    result = api_call("drafts", method="POST", data={"message": {"raw": encoded}})

    if not result["success"]:
        return result

    data = result["data"]
    return {
        "success": bool(data.get("id")),
        "data": {
            "draftId": data.get("id"),
            "messageId": data.get("message", {}).get("id"),
        },
    }


def draft_update(draft_id: str, to: str = "", subject: str = "", body: str = "") -> dict:
    """Update an existing draft, preserving fields not provided."""
    existing = _get_draft(draft_id)
    if not existing["success"]:
        return existing

    ex = existing["data"]
    final_to = to or ex["to"]
    final_subject = subject or ex["subject"]
    final_body = body or ex["body"]

    encoded = _build_raw_message(final_to, final_subject, final_body)
    result = api_call(f"drafts/{draft_id}", method="PUT", data={"message": {"raw": encoded}})

    if not result["success"]:
        return result

    data = result["data"]
    return {
        "success": bool(data.get("id")),
        "data": {
            "draftId": data.get("id"),
            "messageId": data.get("message", {}).get("id"),
        },
    }


def draft_delete(draft_id: str) -> dict:
    """Delete a draft."""
    result = api_call_delete(f"drafts/{draft_id}")
    if not result["success"]:
        return result
    return {
        "success": True,
        "data": {"draftId": draft_id, "deleted": True},
    }


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

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
     - https://www.googleapis.com/auth/gmail.compose   (drafts)
     - https://www.googleapis.com/auth/gmail.labels    (label management)
     - https://www.googleapis.com/auth/gmail.modify    (apply labels, organize)
   - Click "Authorize APIs" and complete the flow
   - In Step 2, click "Exchange authorization code for tokens"
   - Copy the "Refresh token" value

7. Set environment variables:
   export GMAIL_CLIENT_ID="your-client-id"
   export GMAIL_CLIENT_SECRET="your-client-secret"
   export GMAIL_REFRESH_TOKEN="your-refresh-token"

Or add to your .env file.

Note: send and draft-send commands are intentionally blocked.
Use draft-create to compose, then review and send manually from Gmail.
"""
    print(instructions)
    return {"success": True, "data": {"message": "Setup instructions printed"}}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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

    # Labels (list)
    subparsers.add_parser("labels", help="List Gmail labels")

    # Create label
    cl_parser = subparsers.add_parser("create-label", help="Create a new label")
    cl_parser.add_argument("name", help="Label name")

    # Apply label
    al_parser = subparsers.add_parser("apply-label", help="Apply label to messages")
    al_parser.add_argument("label_id", help="Label ID")
    al_parser.add_argument("message_ids", nargs="+", help="Message ID(s)")

    # Organize
    org_parser = subparsers.add_parser("organize", help="Find-or-create label, search, apply to all")
    org_parser.add_argument("label_name", help="Label name")
    org_parser.add_argument("query", help="Gmail search query")

    # Create filter
    cf_parser = subparsers.add_parser("create-filter", help="Create Gmail filter with label")
    cf_parser.add_argument("label_name", help="Label name")
    cf_parser.add_argument("query", help="Gmail search query (e.g. 'from:example.com')")

    # List filters
    subparsers.add_parser("list-filters", help="List Gmail filters")

    # Drafts
    drafts_parser = subparsers.add_parser("drafts", help="List drafts")
    drafts_parser.add_argument("--limit", type=int, default=10, help="Max drafts")

    # Draft create
    dc_parser = subparsers.add_parser("draft-create", help="Create a new draft")
    dc_parser.add_argument("--to", default="", help="Recipient email")
    dc_parser.add_argument("--subject", required=True, help="Email subject")
    dc_parser.add_argument("--body", default="", help="Email body")

    # Draft update
    du_parser = subparsers.add_parser("draft-update", help="Update an existing draft")
    du_parser.add_argument("draft_id", help="Draft ID")
    du_parser.add_argument("--to", default="", help="Override recipient")
    du_parser.add_argument("--subject", default="", help="Override subject")
    du_parser.add_argument("--body", default="", help="Override body")
    du_parser.add_argument("--body-stdin", action="store_true", help="Read body from stdin")

    # Draft delete
    dd_parser = subparsers.add_parser("draft-delete", help="Delete a draft")
    dd_parser.add_argument("draft_id", help="Draft ID")

    # BLOCKED: send
    subparsers.add_parser("send", help="[BLOCKED] Use draft-create instead")

    # BLOCKED: draft-send
    subparsers.add_parser("draft-send", help="[BLOCKED] Review and send manually from Gmail")

    args = parser.parse_args()

    try:
        if args.command == "setup":
            result = print_setup_instructions()

        elif args.command in ("send", "draft-send"):
            sys.stderr.write(
                f"Error: '{args.command}' is disabled for security.\n"
                "Use 'draft-create' to compose, then review and send manually from Gmail.\n"
            )
            sys.exit(1)

        elif args.command == "inbox":
            result = list_inbox(args.limit, args.unread)

        elif args.command == "search":
            result = search_emails(args.query, args.limit)

        elif args.command == "read":
            result = read_email(args.message_id)

        elif args.command == "labels":
            result = list_labels()

        elif args.command == "create-label":
            result = create_label(args.name)

        elif args.command == "apply-label":
            result = apply_label(args.label_id, args.message_ids)

        elif args.command == "organize":
            result = organize(args.label_name, args.query)

        elif args.command == "create-filter":
            result = create_filter(args.label_name, args.query)

        elif args.command == "list-filters":
            result = list_filters()

        elif args.command == "drafts":
            result = list_drafts(args.limit)

        elif args.command == "draft-create":
            result = draft_create(args.to, args.subject, args.body)

        elif args.command == "draft-update":
            body = args.body
            if args.body_stdin or (not body and not sys.stdin.isatty()):
                stdin_body = sys.stdin.read()
                if stdin_body:
                    body = stdin_body
            result = draft_update(args.draft_id, args.to, args.subject, body)

        elif args.command == "draft-delete":
            result = draft_delete(args.draft_id)

        else:
            result = {"success": False, "error": "Unknown command"}

    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
