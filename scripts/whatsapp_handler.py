#!/usr/bin/env python3
"""
WhatsApp Business Cloud API handler for Hive.
Send messages, templates, interactive messages, media, contacts, location.
Uses Graph API v22.0.

Env vars:
  WHATSAPP_TOKEN    - Meta access token
  WHATSAPP_PHONE_ID - Phone number ID
  WHATSAPP_WABA_ID  - WhatsApp Business Account ID (optional, for templates)
"""

import os
import sys
import json
import argparse
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = "v22.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def get_config() -> tuple[str, str]:
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_id = os.environ.get("WHATSAPP_PHONE_ID")

    if not token:
        raise ValueError("WHATSAPP_TOKEN not set in environment")
    if not phone_id:
        raise ValueError("WHATSAPP_PHONE_ID not set in environment")

    return token, phone_id


def api_call(
    endpoint: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
    method: str = "POST",
) -> dict:
    """Make a Graph API call."""
    token, _ = get_config()

    url = f"{GRAPH_API_BASE}/{endpoint}"

    if params:
        params["access_token"] = token
        url = f"{url}?{urlencode(params)}"
    else:
        url = f"{url}?access_token={token}"

    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None

    if method == "GET":
        headers = {}
        body = None

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
        except Exception:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Text Messages ---


def send_text(to: str, message: str, preview_url: bool = False) -> dict:
    """Send a text message (24h window only)."""
    _, phone_id = get_config()
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message, "preview_url": preview_url},
    }
    return api_call(f"{phone_id}/messages", data)


# --- Template Messages ---


def send_template(
    to: str,
    template_name: str,
    language: str = "en",
    params: Optional[list] = None,
    header_params: Optional[list] = None,
) -> dict:
    """Send a template message (works outside 24h window)."""
    _, phone_id = get_config()

    template = {
        "name": template_name,
        "language": {"code": language},
    }

    components = []
    if header_params:
        components.append({
            "type": "header",
            "parameters": [{"type": "text", "text": p} for p in header_params],
        })
    if params:
        components.append({
            "type": "body",
            "parameters": [{"type": "text", "text": p} for p in params],
        })
    if components:
        template["components"] = components

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": template,
    }
    return api_call(f"{phone_id}/messages", data)


# --- Media Messages ---


def send_media(
    to: str, media_type: str, url: str, caption: Optional[str] = None
) -> dict:
    """Send media: image, video, audio, document, sticker."""
    _, phone_id = get_config()

    media_obj = {"link": url}
    if caption and media_type in ("image", "video", "document"):
        media_obj["caption"] = caption

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": media_type,
        media_type: media_obj,
    }
    return api_call(f"{phone_id}/messages", data)


# --- Interactive Messages ---


def send_buttons(to: str, body: str, buttons: list[dict], header: Optional[str] = None, footer: Optional[str] = None) -> dict:
    """
    Send interactive button message (max 3 buttons).
    buttons: [{"id": "btn_1", "title": "Yes"}, ...]
    """
    _, phone_id = get_config()

    interactive = {
        "type": "button",
        "body": {"text": body},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                for b in buttons[:3]
            ]
        },
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive,
    }
    return api_call(f"{phone_id}/messages", data)


def send_list(
    to: str,
    body: str,
    button_text: str,
    sections: list[dict],
    header: Optional[str] = None,
    footer: Optional[str] = None,
) -> dict:
    """
    Send interactive list message.
    sections: [{"title": "Section", "rows": [{"id": "1", "title": "Option", "description": "..."}]}]
    """
    _, phone_id = get_config()

    interactive = {
        "type": "list",
        "body": {"text": body},
        "action": {
            "button": button_text,
            "sections": sections,
        },
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive,
    }
    return api_call(f"{phone_id}/messages", data)


# --- Location ---


def send_location(to: str, latitude: float, longitude: float, name: Optional[str] = None, address: Optional[str] = None) -> dict:
    """Send a location pin."""
    _, phone_id = get_config()

    location = {"latitude": latitude, "longitude": longitude}
    if name:
        location["name"] = name
    if address:
        location["address"] = address

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "location",
        "location": location,
    }
    return api_call(f"{phone_id}/messages", data)


# --- Contacts ---


def send_contact(to: str, contact_json: str) -> dict:
    """
    Send a contact card.
    contact_json: JSON with name, phones, emails, etc.
    """
    _, phone_id = get_config()

    contacts = json.loads(contact_json) if isinstance(contact_json, str) else contact_json
    if not isinstance(contacts, list):
        contacts = [contacts]

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "contacts",
        "contacts": contacts,
    }
    return api_call(f"{phone_id}/messages", data)


# --- Reactions ---


def send_reaction(to: str, message_id: str, emoji: str) -> dict:
    """React to a message with an emoji."""
    _, phone_id = get_config()
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "reaction",
        "reaction": {"message_id": message_id, "emoji": emoji},
    }
    return api_call(f"{phone_id}/messages", data)


# --- Mark Read ---


def mark_read(message_id: str) -> dict:
    """Mark a message as read."""
    _, phone_id = get_config()
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    return api_call(f"{phone_id}/messages", data)


# --- Flows ---


def send_flow(
    to: str,
    flow_id: str,
    flow_cta: str,
    body: str,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    flow_action: str = "navigate",
    screen: Optional[str] = None,
    flow_data: Optional[str] = None,
) -> dict:
    """Send a WhatsApp Flow (interactive form)."""
    _, phone_id = get_config()

    action_payload = {
        "name": "flow",
        "parameters": {
            "flow_message_version": "3",
            "flow_id": flow_id,
            "flow_cta": flow_cta,
            "flow_action": flow_action,
        },
    }

    if screen:
        action_payload["parameters"]["flow_action_payload"] = {"screen": screen}
        if flow_data:
            action_payload["parameters"]["flow_action_payload"]["data"] = json.loads(flow_data)

    interactive = {
        "type": "flow",
        "body": {"text": body},
        "action": action_payload,
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive,
    }
    return api_call(f"{phone_id}/messages", data)


# --- Templates Management ---


def get_templates(limit: int = 25, status: Optional[str] = None) -> dict:
    """List message templates."""
    waba_id = os.environ.get("WHATSAPP_WABA_ID")
    if not waba_id:
        # Fallback: try to get from phone number info
        _, phone_id = get_config()
        phone_info = api_call(phone_id, method="GET")
        if not phone_info.get("success"):
            return {"success": False, "error": "WHATSAPP_WABA_ID not set and could not determine from phone"}
        waba_id = phone_info.get("data", {}).get("owner_business_info", {}).get("id")
        if not waba_id:
            return {"success": False, "error": "Could not determine WABA ID"}

    params = {"limit": str(limit), "fields": "name,status,language,category,components"}
    if status:
        params["status"] = status.upper()
    return api_call(f"{waba_id}/message_templates", params=params, method="GET")


# --- Phone Number Info ---


def phone_info() -> dict:
    """Get phone number info (quality rating, status, etc.)."""
    _, phone_id = get_config()
    return api_call(
        phone_id,
        params={"fields": "id,display_phone_number,verified_name,quality_rating,messaging_limit_tier,status"},
        method="GET",
    )


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(description="WhatsApp Business Cloud API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Text
    send_p = subparsers.add_parser("send", help="Send text message")
    send_p.add_argument("to", help="Phone number (international, no +)")
    send_p.add_argument("message", help="Message text")
    send_p.add_argument("--preview-url", action="store_true", help="Enable link preview")

    # Template
    tmpl_p = subparsers.add_parser("template", help="Send template message")
    tmpl_p.add_argument("to", help="Phone number")
    tmpl_p.add_argument("name", help="Template name")
    tmpl_p.add_argument("--lang", default="en", help="Template language code")
    tmpl_p.add_argument("--params", help="JSON array of body parameters")
    tmpl_p.add_argument("--header-params", help="JSON array of header parameters")

    # Media
    media_p = subparsers.add_parser("media", help="Send media message")
    media_p.add_argument("to", help="Phone number")
    media_p.add_argument("type", choices=["image", "video", "audio", "document", "sticker"])
    media_p.add_argument("url", help="Media URL")
    media_p.add_argument("caption", nargs="?", help="Caption")

    # Buttons
    btn_p = subparsers.add_parser("buttons", help="Send interactive buttons (max 3)")
    btn_p.add_argument("to", help="Phone number")
    btn_p.add_argument("body", help="Message body text")
    btn_p.add_argument("buttons", help='JSON: [{"id":"1","title":"Yes"},...]')
    btn_p.add_argument("--header")
    btn_p.add_argument("--footer")

    # List
    list_p = subparsers.add_parser("list", help="Send interactive list")
    list_p.add_argument("to", help="Phone number")
    list_p.add_argument("body", help="Message body text")
    list_p.add_argument("button_text", help="Button label to open list")
    list_p.add_argument("sections", help='JSON sections array')
    list_p.add_argument("--header")
    list_p.add_argument("--footer")

    # Location
    loc_p = subparsers.add_parser("location", help="Send location pin")
    loc_p.add_argument("to", help="Phone number")
    loc_p.add_argument("latitude", type=float)
    loc_p.add_argument("longitude", type=float)
    loc_p.add_argument("--name", help="Location name")
    loc_p.add_argument("--address", help="Address text")

    # Contact
    contact_p = subparsers.add_parser("contact", help="Send contact card")
    contact_p.add_argument("to", help="Phone number")
    contact_p.add_argument("contact_json", help="JSON contact object")

    # Reaction
    react_p = subparsers.add_parser("react", help="React to a message")
    react_p.add_argument("to", help="Phone number")
    react_p.add_argument("message_id", help="Message ID (wamid.xxx)")
    react_p.add_argument("emoji", help="Emoji character")

    # Mark read
    read_p = subparsers.add_parser("read", help="Mark message as read")
    read_p.add_argument("message_id", help="Message ID")

    # Flow
    flow_p = subparsers.add_parser("flow", help="Send WhatsApp Flow")
    flow_p.add_argument("to", help="Phone number")
    flow_p.add_argument("flow_id", help="Flow ID")
    flow_p.add_argument("flow_cta", help="CTA button text")
    flow_p.add_argument("body", help="Message body")
    flow_p.add_argument("--header")
    flow_p.add_argument("--footer")
    flow_p.add_argument("--screen", help="Initial screen name")
    flow_p.add_argument("--flow-data", help="JSON data for screen")

    # Templates list
    tmpl_list = subparsers.add_parser("templates", help="List message templates")
    tmpl_list.add_argument("--limit", type=int, default=25)
    tmpl_list.add_argument("--status", help="Filter: APPROVED, PENDING, REJECTED")

    # Phone info
    subparsers.add_parser("phone-info", help="Phone number quality and status")

    args = parser.parse_args()

    try:
        if args.command == "send":
            result = send_text(args.to, args.message, args.preview_url)
        elif args.command == "template":
            params = json.loads(args.params) if args.params else None
            header_params = json.loads(args.header_params) if args.header_params else None
            result = send_template(args.to, args.name, args.lang, params, header_params)
        elif args.command == "media":
            result = send_media(args.to, args.type, args.url, args.caption)
        elif args.command == "buttons":
            buttons = json.loads(args.buttons)
            result = send_buttons(args.to, args.body, buttons, args.header, args.footer)
        elif args.command == "list":
            sections = json.loads(args.sections)
            result = send_list(args.to, args.body, args.button_text, sections, args.header, args.footer)
        elif args.command == "location":
            result = send_location(args.to, args.latitude, args.longitude, args.name, args.address)
        elif args.command == "contact":
            result = send_contact(args.to, args.contact_json)
        elif args.command == "react":
            result = send_reaction(args.to, args.message_id, args.emoji)
        elif args.command == "read":
            result = mark_read(args.message_id)
        elif args.command == "flow":
            result = send_flow(
                args.to, args.flow_id, args.flow_cta, args.body,
                args.header, args.footer, screen=args.screen, flow_data=args.flow_data,
            )
        elif args.command == "templates":
            result = get_templates(args.limit, args.status)
        elif args.command == "phone-info":
            result = phone_info()
        else:
            result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
