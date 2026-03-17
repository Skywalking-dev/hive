#!/usr/bin/env python3
"""
WhatsApp Business API handler for Hive.
Send messages, templates, and check status.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = "v18.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def get_config() -> tuple[str, str]:
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_id = os.environ.get("WHATSAPP_PHONE_ID")

    if not token:
        raise ValueError("WHATSAPP_TOKEN not set in environment")
    if not phone_id:
        raise ValueError("WHATSAPP_PHONE_ID not set in environment")

    return token, phone_id


def api_call(endpoint: str, data: Optional[dict] = None, method: str = "POST") -> dict:
    """Make a Graph API call."""
    token, _ = get_config()
    url = f"{GRAPH_API_BASE}/{endpoint}"

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


def send_text(to: str, message: str) -> dict:
    """Send a text message."""
    _, phone_id = get_config()

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    return api_call(f"{phone_id}/messages", data)


def send_template(to: str, template_name: str, params: Optional[list] = None) -> dict:
    """Send a template message."""
    _, phone_id = get_config()

    template = {
        "name": template_name,
        "language": {"code": "en"},
    }

    if params:
        template["components"] = [{
            "type": "body",
            "parameters": [{"type": "text", "text": p} for p in params],
        }]

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": template,
    }

    return api_call(f"{phone_id}/messages", data)


def send_media(to: str, media_type: str, url: str, caption: Optional[str] = None) -> dict:
    """Send a media message (image, video, document)."""
    _, phone_id = get_config()

    media_obj = {"link": url}
    if caption and media_type in ("image", "video"):
        media_obj["caption"] = caption

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": media_type,
        media_type: media_obj,
    }

    return api_call(f"{phone_id}/messages", data)


def get_templates() -> dict:
    """List message templates."""
    token, phone_id = get_config()

    # Get business account ID first
    url = f"{GRAPH_API_BASE}/{phone_id}"
    headers = {"Authorization": f"Bearer {token}"}
    req = Request(url, headers=headers, method="GET")

    try:
        with urlopen(req, timeout=30) as resp:
            phone_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"success": False, "error": str(e)}

    waba_id = phone_data.get("owner_business_info", {}).get("id")
    if not waba_id:
        return {"success": False, "error": "Could not determine business account ID"}

    return api_call(f"{waba_id}/message_templates", method="GET")


def main():
    parser = argparse.ArgumentParser(description="WhatsApp Business API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Send text
    send_parser = subparsers.add_parser("send", help="Send text message")
    send_parser.add_argument("to", help="Phone number (international format)")
    send_parser.add_argument("message", help="Message text")

    # Send template
    template_parser = subparsers.add_parser("template", help="Send template message")
    template_parser.add_argument("to", help="Phone number")
    template_parser.add_argument("name", help="Template name")
    template_parser.add_argument("--params", help="JSON array of parameters")

    # Send media
    media_parser = subparsers.add_parser("media", help="Send media message")
    media_parser.add_argument("to", help="Phone number")
    media_parser.add_argument("type", choices=["image", "video", "document"])
    media_parser.add_argument("url", help="Media URL")
    media_parser.add_argument("caption", nargs="?", help="Caption")

    # List templates
    subparsers.add_parser("templates", help="List message templates")

    args = parser.parse_args()

    try:
        if args.command == "send":
            result = send_text(args.to, args.message)
        elif args.command == "template":
            params = json.loads(args.params) if args.params else None
            result = send_template(args.to, args.name, params)
        elif args.command == "media":
            result = send_media(args.to, args.type, args.url, args.caption)
        elif args.command == "templates":
            result = get_templates()
        else:
            result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
