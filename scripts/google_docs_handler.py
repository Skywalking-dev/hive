#!/usr/bin/env python3
"""
Google Docs API handler for Hive.
Read, create, update, list, search, and export Google Docs with Markdown conversion.

Usage:
  python google_docs_handler.py get <id_or_url>                   # Get doc as Markdown
  python google_docs_handler.py get <id_or_url> --rich            # Get with metadata/suggestions
  python google_docs_handler.py create <title> [--body=md]        # Create doc
  python google_docs_handler.py update <id> --body=md [--replace] # Append or replace content
  python google_docs_handler.py list [--limit=10]                 # List recent docs
  python google_docs_handler.py search "query" [--limit=10]       # Search docs
  python google_docs_handler.py export <id> [--format=md]         # Export to md/txt/html/pdf/docx/epub
  python google_docs_handler.py setup                             # Print OAuth setup instructions

Env vars:
  GOOGLE_DOCS_CLIENT_ID      (fallback: GMAIL_CLIENT_ID)
  GOOGLE_DOCS_CLIENT_SECRET  (fallback: GMAIL_CLIENT_SECRET)
  GOOGLE_DOCS_REFRESH_TOKEN
"""

import os
import sys
import json
import re
import argparse
import secrets
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from dotenv import load_dotenv

load_dotenv()
from urllib.parse import urlencode, quote

TOKEN_URL = "https://oauth2.googleapis.com/token"
DOCS_API_BASE = "https://docs.googleapis.com/v1/documents"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD_BASE = "https://www.googleapis.com/upload/drive/v3/files"

BINARY_FORMATS = {"pdf", "docx", "epub"}
MIME_TYPES = {
    "md":   "text/markdown",
    "txt":  "text/plain",
    "html": "text/html",
    "pdf":  "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "epub": "application/epub+zip",
}


# ---------------------------------------------------------------------------
# Config / Auth
# ---------------------------------------------------------------------------

def get_config() -> tuple[str, str, str]:
    client_id = os.environ.get("GOOGLE_DOCS_CLIENT_ID") or os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_DOCS_CLIENT_SECRET") or os.environ.get("GMAIL_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_DOCS_REFRESH_TOKEN")

    if not client_id:
        raise ValueError("GOOGLE_DOCS_CLIENT_ID (or GMAIL_CLIENT_ID) not set in environment")
    if not client_secret:
        raise ValueError("GOOGLE_DOCS_CLIENT_SECRET (or GMAIL_CLIENT_SECRET) not set in environment")
    if not refresh_token:
        raise ValueError("GOOGLE_DOCS_REFRESH_TOKEN not set in environment")

    return client_id, client_secret, refresh_token


def get_access_token() -> str:
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
            if "access_token" not in result:
                raise ValueError(f"No access_token in response: {result}")
            return result["access_token"]
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise ValueError(f"Token refresh failed: {error_body}")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def http_get(url: str, token: str, binary: bool = False) -> bytes | str:
    req = Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")

    try:
        with urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return raw if binary else raw.decode("utf-8")
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {error_body}")


def http_post_json(url: str, payload: dict, token: str) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=UTF-8")

    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {error_body}")


def http_post_form(url: str, fields: dict) -> dict:
    body = urlencode(fields).encode("utf-8")
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {error_body}")


def http_post_multipart(url: str, metadata: dict, content: str, content_type: str, token: str) -> dict:
    boundary = f"boundary_{secrets.token_hex(8)}"
    meta_bytes = json.dumps(metadata).encode("utf-8")
    content_bytes = content.encode("utf-8")

    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
    ).encode("utf-8") + meta_bytes + (
        f"\r\n--{boundary}\r\n"
        f"Content-Type: {content_type}; charset=UTF-8\r\n\r\n"
    ).encode("utf-8") + content_bytes + (
        f"\r\n--{boundary}--"
    ).encode("utf-8")

    req = Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/related; boundary={boundary}")

    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {error_body}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_doc_id(id_or_url: str) -> str:
    m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", id_or_url)
    if m:
        return m.group(1)
    return id_or_url


def resolve_body(args: argparse.Namespace) -> str:
    if args.body_stdin:
        return sys.stdin.read()
    # If stdin is piped and no explicit body arg, read it
    if not sys.stdin.isatty() and not args.body:
        return sys.stdin.read()
    return args.body or ""


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------

def get_doc_as_markdown(token: str, doc_id: str) -> dict:
    # Try markdown export first, fallback to plain text
    export_url = f"{DRIVE_API_BASE}/{quote(doc_id, safe='')}/export?" + urlencode({"mimeType": "text/markdown"})
    try:
        content = http_get(export_url, token)
    except RuntimeError:
        export_url = f"{DRIVE_API_BASE}/{quote(doc_id, safe='')}/export?" + urlencode({"mimeType": "text/plain"})
        content = http_get(export_url, token)

    meta_url = f"{DRIVE_API_BASE}/{quote(doc_id, safe='')}?" + urlencode({
        "fields": "id,name,modifiedTime,createdTime,webViewLink"
    })
    meta = json.loads(http_get(meta_url, token))

    return {
        "success": True,
        "data": {
            "documentId": doc_id,
            "title": meta.get("name", ""),
            "url": meta.get("webViewLink", ""),
            "modifiedTime": meta.get("modifiedTime", ""),
            "createdTime": meta.get("createdTime", ""),
            "content": content,
        }
    }


def get_doc_rich(token: str, doc_id: str) -> dict:
    doc_url = f"{DOCS_API_BASE}/{quote(doc_id, safe='')}?suggestionsViewMode=PREVIEW_SUGGESTIONS_ACCEPTED"
    doc = json.loads(http_get(doc_url, token))

    suggestions_url = f"{DOCS_API_BASE}/{quote(doc_id, safe='')}?suggestionsViewMode=SUGGESTIONS_INLINE"
    suggestions_doc = json.loads(http_get(suggestions_url, token))

    markdown = docs_json_to_markdown(doc.get("body", {}).get("content", []))
    suggestions_count = count_suggestions(suggestions_doc)

    return {
        "success": True,
        "data": {
            "documentId": doc_id,
            "title": doc.get("title", ""),
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
            "revisionId": doc.get("revisionId", ""),
            "suggestionsCount": suggestions_count,
            "content": markdown,
        }
    }


def count_suggestions(doc: dict) -> int:
    serialized = json.dumps(doc)
    return serialized.count('"suggestedInsertionIds"') + serialized.count('"suggestedDeletionIds"')


# ---------------------------------------------------------------------------
# Docs JSON -> Markdown
# ---------------------------------------------------------------------------

def docs_json_to_markdown(content: list) -> str:
    md = ""
    for element in content:
        if "paragraph" in element:
            md += parse_paragraph(element["paragraph"])
        elif "table" in element:
            md += parse_table(element["table"])
        elif "sectionBreak" in element:
            md += "\n---\n\n"
    return md


def _apply_text_style(text_content: str, style: dict, original: str) -> str:
    """Apply bold/italic/strikethrough/link inline formatting, preserve trailing whitespace."""
    result = text_content

    def trail(s: str) -> str:
        if original.endswith("\n"):
            return s + "\n"
        if original.endswith(" "):
            return s + " "
        return s

    if style.get("bold"):
        result = trail("**" + result.strip() + "**")
    if style.get("italic"):
        result = trail("_" + result.strip() + "_")
    if style.get("strikethrough"):
        result = trail("~~" + result.strip() + "~~")
    if style.get("link", {}).get("url"):
        link_url = style["link"]["url"]
        result = trail("[" + result.strip() + "](" + link_url + ")")

    return result


def parse_paragraph(paragraph: dict) -> str:
    style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
    elements = paragraph.get("elements", [])

    text = ""
    for el in elements:
        if "textRun" in el:
            raw = el["textRun"].get("content", "")
            ts = el["textRun"].get("textStyle", {})
            if any([ts.get("bold"), ts.get("italic"), ts.get("strikethrough"), ts.get("link", {}).get("url")]):
                text += _apply_text_style(raw, ts, raw)
            else:
                text += raw
        elif "inlineObjectElement" in el:
            text += "![image]()"

    bullet = paragraph.get("bullet")
    if bullet:
        nesting = bullet.get("nestingLevel", 0)
        indent = "  " * nesting
        return indent + "- " + text.strip() + "\n"

    heading_map = {
        "HEADING_1": "# ",
        "HEADING_2": "## ",
        "HEADING_3": "### ",
        "HEADING_4": "#### ",
        "HEADING_5": "##### ",
        "HEADING_6": "###### ",
        "TITLE": "# ",
        "SUBTITLE": "## ",
    }
    if style in heading_map:
        return heading_map[style] + text.strip() + "\n\n"

    return text


def parse_table(table: dict) -> str:
    rows = table.get("tableRows", [])
    if not rows:
        return ""

    md = "\n"
    for row_index, row in enumerate(rows):
        cells = row.get("tableCells", [])
        row_text = "|"
        for cell in cells:
            cell_content = ""
            for element in cell.get("content", []):
                if "paragraph" in element:
                    cell_content += parse_paragraph(element["paragraph"]).strip()
            row_text += " " + cell_content.replace("|", "\\|").replace("\n", " ") + " |"
        md += row_text + "\n"
        if row_index == 0:
            md += "|" + " --- |" * len(cells) + "\n"

    md += "\n"
    return md


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_doc(token: str, title: str, body: str) -> dict:
    if body:
        html = markdown_to_html(body, title)
        return _create_doc_from_html(token, title, html)

    # Empty doc via Docs API
    response = http_post_json(DOCS_API_BASE, {"title": title}, token)
    doc_id = response.get("documentId")
    return {
        "success": bool(doc_id),
        "data": {
            "documentId": doc_id,
            "title": response.get("title", title),
            "url": f"https://docs.google.com/document/d/{doc_id}/edit" if doc_id else None,
        }
    }


def _create_doc_from_html(token: str, title: str, html: str) -> dict:
    url = DRIVE_UPLOAD_BASE + "?" + urlencode({
        "uploadType": "multipart",
        "fields": "id,name,webViewLink",
    })
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
    }
    data = http_post_multipart(url, metadata, html, "text/html", token)
    return {
        "success": bool(data.get("id")),
        "data": {
            "documentId": data.get("id"),
            "title": data.get("name", title),
            "url": data.get("webViewLink"),
        }
    }


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_doc(token: str, doc_id: str, markdown_body: str, replace: bool) -> dict:
    doc_url = f"{DOCS_API_BASE}/{quote(doc_id, safe='')}"
    doc = json.loads(http_get(doc_url, token))

    content = doc.get("body", {}).get("content", [])
    end_index = 1
    for element in content:
        if "endIndex" in element:
            end_index = element["endIndex"]

    requests: list[dict] = []

    if replace and end_index > 2:
        requests.append({
            "deleteContentRange": {
                "range": {
                    "startIndex": 1,
                    "endIndex": end_index - 1,
                }
            }
        })
        end_index = 1

    insert_start = 1 if replace else end_index - 1
    insert_requests = markdown_to_batch_update(markdown_body, insert_start)
    requests.extend(insert_requests)

    if not requests:
        return {
            "success": True,
            "data": {
                "documentId": doc_id,
                "message": "No content to update",
            }
        }

    batch_url = f"{DOCS_API_BASE}/{quote(doc_id, safe='')}:batchUpdate"
    result = http_post_json(batch_url, {"requests": requests}, token)

    return {
        "success": bool(result.get("documentId")),
        "data": {
            "documentId": result.get("documentId", doc_id),
            "title": doc.get("title", ""),
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
            "updatesApplied": len(requests),
        }
    }


def markdown_to_batch_update(markdown: str, start_index: int) -> list[dict]:
    requests: list[dict] = []
    lines = markdown.split("\n")
    current_index = start_index
    heading_ranges: list[dict] = []

    named_styles = {
        1: "HEADING_1",
        2: "HEADING_2",
        3: "HEADING_3",
        4: "HEADING_4",
        5: "HEADING_5",
        6: "HEADING_6",
    }

    for line in lines:
        heading_level = 0
        text = line

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            heading_level = len(m.group(1))
            text = m.group(2)

        insert_text = text + "\n"
        requests.append({
            "insertText": {
                "location": {"index": current_index},
                "text": insert_text,
            }
        })

        char_len = len(insert_text.encode("utf-8"))
        # Use character count not byte count for Docs API index
        text_len = len(insert_text)

        if heading_level > 0:
            heading_ranges.append({
                "start": current_index,
                "end": current_index + text_len,
                "level": heading_level,
            })

        current_index += text_len

    # Apply heading styles in reverse to avoid index shifts
    for rng in reversed(heading_ranges):
        requests.append({
            "updateParagraphStyle": {
                "range": {
                    "startIndex": rng["start"],
                    "endIndex": rng["end"],
                },
                "paragraphStyle": {
                    "namedStyleType": named_styles[rng["level"]],
                },
                "fields": "namedStyleType",
            }
        })

    return requests


# ---------------------------------------------------------------------------
# List & Search
# ---------------------------------------------------------------------------

def list_docs(token: str, limit: int) -> dict:
    params = urlencode({
        "q": "mimeType='application/vnd.google-apps.document' and trashed=false",
        "orderBy": "modifiedTime desc",
        "pageSize": limit,
        "fields": "files(id,name,modifiedTime,createdTime,webViewLink,owners)",
    })
    data = json.loads(http_get(f"{DRIVE_API_BASE}?{params}", token))
    docs = _map_files(data.get("files", []))
    return {
        "success": True,
        "data": {
            "count": len(docs),
            "documents": docs,
        }
    }


def search_docs(token: str, query: str, limit: int) -> dict:
    drive_query = (
        f"mimeType='application/vnd.google-apps.document' and trashed=false "
        f"and (name contains '{query}' or fullText contains '{query}')"
    )
    params = urlencode({
        "q": drive_query,
        "orderBy": "modifiedTime desc",
        "pageSize": limit,
        "fields": "files(id,name,modifiedTime,createdTime,webViewLink,owners)",
    })
    data = json.loads(http_get(f"{DRIVE_API_BASE}?{params}", token))
    docs = _map_files(data.get("files", []))
    return {
        "success": True,
        "data": {
            "query": query,
            "count": len(docs),
            "documents": docs,
        }
    }


def _map_files(files: list) -> list[dict]:
    return [
        {
            "documentId": f["id"],
            "title": f.get("name", ""),
            "modifiedTime": f.get("modifiedTime", ""),
            "createdTime": f.get("createdTime", ""),
            "url": f.get("webViewLink", ""),
            "owner": (f.get("owners") or [{}])[0].get("emailAddress", ""),
        }
        for f in files
    ]


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_doc(token: str, doc_id: str, fmt: str) -> bytes | str:
    if fmt not in MIME_TYPES:
        supported = ", ".join(MIME_TYPES.keys())
        raise ValueError(f"Unsupported format: {fmt}. Supported: {supported}")

    mime = MIME_TYPES[fmt]
    url = f"{DRIVE_API_BASE}/{quote(doc_id, safe='')}/export?" + urlencode({"mimeType": mime})
    is_binary = fmt in BINARY_FORMATS

    if fmt == "md":
        try:
            return http_get(url, token, binary=False)
        except RuntimeError:
            fallback = f"{DRIVE_API_BASE}/{quote(doc_id, safe='')}/export?" + urlencode({"mimeType": "text/plain"})
            return http_get(fallback, token, binary=False)

    return http_get(url, token, binary=is_binary)


# ---------------------------------------------------------------------------
# Markdown -> HTML (for create with body)
# ---------------------------------------------------------------------------

def apply_inline_formatting(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def markdown_to_html(markdown: str, title: str = "") -> str:
    escaped_title = html_escape(title)
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
    if title:
        html += f"<title>{escaped_title}</title>"
    html += "</head><body>"

    lines = markdown.split("\n")
    in_list = False
    in_code_block = False

    for line in lines:
        # Code block fence
        if re.match(r"^```", line):
            if in_code_block:
                html += "</pre>"
                in_code_block = False
            else:
                if in_list:
                    html += "</ul>"
                    in_list = False
                html += "<pre>"
                in_code_block = True
            continue

        if in_code_block:
            html += html_escape(line) + "\n"
            continue

        # Empty line
        if not line.strip():
            if in_list:
                html += "</ul>"
                in_list = False
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if in_list:
                html += "</ul>"
                in_list = False
            level = len(m.group(1))
            html += f"<h{level}>{apply_inline_formatting(m.group(2))}</h{level}>"
            continue

        # Horizontal rule
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", line.strip()):
            if in_list:
                html += "</ul>"
                in_list = False
            html += "<hr>"
            continue

        # Unordered list
        m = re.match(r"^[\s]*[-*+]\s+(.*)$", line)
        if m:
            if not in_list:
                html += "<ul>"
                in_list = True
            html += f"<li>{apply_inline_formatting(m.group(1))}</li>"
            continue

        # Ordered list
        m = re.match(r"^[\s]*\d+\.\s+(.*)$", line)
        if m:
            if not in_list:
                html += "<ul>"
                in_list = True
            html += f"<li>{apply_inline_formatting(m.group(1))}</li>"
            continue

        # Regular paragraph
        if in_list:
            html += "</ul>"
            in_list = False
        html += f"<p>{apply_inline_formatting(line)}</p>"

    if in_list:
        html += "</ul>"
    if in_code_block:
        html += "</pre>"

    html += "</body></html>"
    return html


# ---------------------------------------------------------------------------
# Setup instructions
# ---------------------------------------------------------------------------

def print_setup_instructions(client_id: Optional[str], client_secret: Optional[str]) -> dict:
    print("=== Google Docs OAuth Setup ===\n")

    if not client_id or not client_secret:
        print("First, configure Google Cloud credentials:\n")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Use existing project (same as Gmail)")
        print("3. Enable Google Docs API:")
        print("   - APIs & Services > Enable APIs and Services")
        print("   - Search 'Google Docs API' > Enable")
        print("4. Enable Google Drive API:")
        print("   - Search 'Google Drive API' > Enable")
        print("5. Reuse existing Gmail OAuth credentials or create new ones.")
        print("   Add redirect URI: http://localhost:8587")
        print("   - APIs & Services > Credentials > your OAuth Client > Authorized redirect URIs")
        print("6. Set GOOGLE_DOCS_CLIENT_ID and GOOGLE_DOCS_CLIENT_SECRET (or GMAIL_CLIENT_ID/SECRET)")
        print("7. Re-run: python google_docs_handler.py setup\n")
        return {"success": True, "data": {"message": "Credentials missing - instructions printed"}}

    redirect_uri = "http://localhost:8587"
    scopes = " ".join([
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.readonly",
    ])

    auth_params = urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scopes,
        "access_type": "offline",
        "prompt": "consent",
    })
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{auth_params}"

    print("Step 1: Open this URL in your browser:\n")
    print(auth_url)
    print()
    print("Step 2: After authorizing, you will be redirected to localhost:8587.")
    print("        Copy the full redirect URL and paste it here:")
    print()

    try:
        redirected = input("Redirect URL: ").strip()
        m = re.search(r"[?&]code=([^&\s]+)", redirected)
        code = m.group(1) if m else None
    except (EOFError, KeyboardInterrupt):
        code = None

    if not code:
        print("\nCould not extract authorization code from URL.")
        print("Alternative: use OAuth Playground at https://developers.google.com/oauthplayground/")
        print("  - Gear icon > Use your own OAuth credentials")
        print("  - Step 1: add scopes above, authorize")
        print("  - Step 2: exchange code for tokens, copy Refresh token")
        print("  - Set GOOGLE_DOCS_REFRESH_TOKEN=<value>")
        return {"success": False, "error": "No authorization code obtained"}

    print("\nExchanging code for tokens...")
    try:
        data = http_post_form("https://oauth2.googleapis.com/token", {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        })
    except RuntimeError as e:
        return {"success": False, "error": str(e)}

    if "refresh_token" in data:
        print("\n=== SUCCESS ===\n")
        print("Set this environment variable:\n")
        print(f"  export GOOGLE_DOCS_REFRESH_TOKEN=\"{data['refresh_token']}\"\n")
        print("Then you can use:")
        print("  python google_docs_handler.py list")
        print("  python google_docs_handler.py get <doc_id_or_url>")
        print("  python google_docs_handler.py create \"My Doc\" --body=\"# Hello\"")
        return {"success": True, "data": {"message": "Setup complete", "refresh_token": data["refresh_token"]}}
    else:
        err = data.get("error_description", str(data))
        return {"success": False, "error": f"Failed to get refresh token: {err}"}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Google Docs API handler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    subparsers.add_parser("setup", help="Print OAuth setup instructions")

    # get
    get_p = subparsers.add_parser("get", help="Get doc as Markdown (or rich)")
    get_p.add_argument("id_or_url", help="Document ID or full URL")
    get_p.add_argument("--rich", action="store_true", help="Include metadata and suggestions count")

    # create
    create_p = subparsers.add_parser("create", help="Create a new document")
    create_p.add_argument("title", help="Document title")
    create_p.add_argument("--body", default="", help="Markdown body content")
    create_p.add_argument("--body-stdin", action="store_true", dest="body_stdin", help="Read body from stdin")

    # update
    update_p = subparsers.add_parser("update", help="Update document content")
    update_p.add_argument("id_or_url", help="Document ID or full URL")
    update_p.add_argument("--body", default="", help="Markdown body content")
    update_p.add_argument("--body-stdin", action="store_true", dest="body_stdin", help="Read body from stdin")
    update_p.add_argument("--replace", action="store_true", help="Replace existing content instead of appending")

    # list
    list_p = subparsers.add_parser("list", help="List recent documents")
    list_p.add_argument("--limit", type=int, default=10, help="Max results")

    # search
    search_p = subparsers.add_parser("search", help="Search documents")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--limit", type=int, default=10, help="Max results")

    # export
    export_p = subparsers.add_parser("export", help="Export document")
    export_p.add_argument("id_or_url", help="Document ID or full URL")
    export_p.add_argument("--format", default="md", dest="fmt", help="Format: md, txt, html, pdf, docx, epub")

    args = parser.parse_args()

    try:
        if args.command == "setup":
            client_id = os.environ.get("GOOGLE_DOCS_CLIENT_ID") or os.environ.get("GMAIL_CLIENT_ID")
            client_secret = os.environ.get("GOOGLE_DOCS_CLIENT_SECRET") or os.environ.get("GMAIL_CLIENT_SECRET")
            result = print_setup_instructions(client_id, client_secret)
            # setup prints its own output; only print JSON result on failure
            if not result["success"]:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(0 if result["success"] else 1)

        token = get_access_token()

        if args.command == "get":
            doc_id = extract_doc_id(args.id_or_url)
            if args.rich:
                result = get_doc_rich(token, doc_id)
            else:
                result = get_doc_as_markdown(token, doc_id)

        elif args.command == "create":
            body = resolve_body(args)
            result = create_doc(token, args.title, body)

        elif args.command == "update":
            doc_id = extract_doc_id(args.id_or_url)
            body = resolve_body(args)
            if not body:
                result = {"success": False, "error": "--body or --body-stdin required with content"}
            else:
                result = update_doc(token, doc_id, body, args.replace)

        elif args.command == "list":
            result = list_docs(token, args.limit)

        elif args.command == "search":
            result = search_docs(token, args.query, args.limit)

        elif args.command == "export":
            doc_id = extract_doc_id(args.id_or_url)
            exported = export_doc(token, doc_id, args.fmt)
            if args.fmt in BINARY_FORMATS:
                # Write raw bytes to stdout
                sys.stdout.buffer.write(exported if isinstance(exported, bytes) else exported.encode("utf-8"))
                sys.exit(0)
            else:
                result = {
                    "success": True,
                    "data": {
                        "documentId": doc_id,
                        "format": args.fmt,
                        "content": exported,
                    }
                }

        else:
            result = {"success": False, "error": f"Unknown command: {args.command}"}

    except ValueError as e:
        result = {"success": False, "error": str(e)}
    except RuntimeError as e:
        result = {"success": False, "error": str(e)}
    except Exception as e:
        result = {"success": False, "error": f"Unexpected error: {e}"}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
