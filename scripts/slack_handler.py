#!/usr/bin/env python3
"""
Slack API handler for Hive.
Read threads, post messages, upload files.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

SLACK_API_BASE = "https://slack.com/api"


def get_token() -> str:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN not set in environment")
    return token


def api_call(method: str, data: Optional[dict] = None, token: Optional[str] = None) -> dict:
    """Make a Slack API call."""
    token = token or get_token()
    url = f"{SLACK_API_BASE}/{method}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = Request(url, data=body, headers=headers, method="POST" if data else "GET")

    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if not result.get("ok"):
                return {"success": False, "error": result.get("error", "unknown")}
            return {"success": True, "data": result}
    except HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_thread_url(url: str) -> tuple[str, str]:
    """Extract channel and thread_ts from Slack URL."""
    # Format: https://workspace.slack.com/archives/C123/p1234567890123456
    match = re.search(r"/archives/([A-Z0-9]+)/p(\d+)", url)
    if not match:
        raise ValueError(f"Invalid Slack URL: {url}")

    channel = match.group(1)
    ts = match.group(2)
    # Convert p1234567890123456 to 1234567890.123456
    thread_ts = f"{ts[:10]}.{ts[10:]}"
    return channel, thread_ts


def read_thread(url: str) -> dict:
    """Read a full thread from Slack."""
    try:
        channel, thread_ts = parse_thread_url(url)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    # Try to join channel first
    api_call("conversations.join", {"channel": channel})

    messages = []
    cursor = None

    while True:
        params = {"channel": channel, "ts": thread_ts, "limit": 100}
        if cursor:
            params["cursor"] = cursor

        result = api_call("conversations.replies", params)
        if not result["success"]:
            return result

        messages.extend(result["data"].get("messages", []))

        cursor = result["data"].get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return {
        "success": True,
        "data": {
            "channel": channel,
            "thread_ts": thread_ts,
            "message_count": len(messages),
            "messages": [
                {
                    "user": m.get("user"),
                    "text": m.get("text"),
                    "ts": m.get("ts"),
                }
                for m in messages
            ],
        },
    }


def send_message(channel: str, text: str, thread_ts: Optional[str] = None) -> dict:
    """Post a message to a channel or thread."""
    data = {"channel": channel, "text": text}
    if thread_ts:
        data["thread_ts"] = thread_ts
    return api_call("chat.postMessage", data)


def upload_file(channel: str, filepath: str, comment: Optional[str] = None) -> dict:
    """Upload a file to a channel."""
    if not os.path.exists(filepath):
        return {"success": False, "error": f"File not found: {filepath}"}

    # Use files.upload v2 flow
    with open(filepath, "rb") as f:
        content = f.read()

    filename = os.path.basename(filepath)

    # Get upload URL
    result = api_call("files.getUploadURLExternal", {
        "filename": filename,
        "length": len(content),
    })

    if not result["success"]:
        return result

    # Upload to URL
    upload_url = result["data"]["upload_url"]
    file_id = result["data"]["file_id"]

    req = Request(upload_url, data=content, method="POST")
    try:
        urlopen(req, timeout=60)
    except Exception as e:
        return {"success": False, "error": f"Upload failed: {e}"}

    # Complete upload
    data = {
        "files": [{"id": file_id}],
        "channel_id": channel,
    }
    if comment:
        data["initial_comment"] = comment

    return api_call("files.completeUploadExternal", data)


def main():
    parser = argparse.ArgumentParser(description="Slack API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Read thread
    read_parser = subparsers.add_parser("read", help="Read a thread")
    read_parser.add_argument("url", help="Slack thread URL")

    # Send message
    send_parser = subparsers.add_parser("send", help="Send a message")
    send_parser.add_argument("channel", help="Channel ID")
    send_parser.add_argument("text", help="Message text")

    # Reply to thread
    reply_parser = subparsers.add_parser("reply", help="Reply to a thread")
    reply_parser.add_argument("channel", help="Channel ID")
    reply_parser.add_argument("thread_ts", help="Thread timestamp")
    reply_parser.add_argument("text", help="Message text")

    # Upload file
    upload_parser = subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("channel", help="Channel ID")
    upload_parser.add_argument("filepath", help="Path to file")
    upload_parser.add_argument("--comment", help="Initial comment")

    args = parser.parse_args()

    if args.command == "read":
        result = read_thread(args.url)
    elif args.command == "send":
        result = send_message(args.channel, args.text)
    elif args.command == "reply":
        result = send_message(args.channel, args.text, args.thread_ts)
    elif args.command == "upload":
        result = upload_file(args.channel, args.filepath, args.comment)
    else:
        result = {"success": False, "error": "Unknown command"}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
