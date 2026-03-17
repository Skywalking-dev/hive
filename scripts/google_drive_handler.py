#!/usr/bin/env python3
"""
Google Drive API handler for Hive.
List, search, get, download, upload, mkdir, move, share, folders.
"""

import os
import sys
import json
import re
import mimetypes
import argparse
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode, quote

from dotenv import load_dotenv

load_dotenv()

DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
DRIVE_UPLOAD_BASE = "https://www.googleapis.com/upload/drive/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ALLOWED_DOMAINS = ["publica.la"]


# ---------------------------------------------------------------------------
# Config & Auth
# ---------------------------------------------------------------------------

def get_config() -> tuple[str, str, str]:
    client_id = os.environ.get("GOOGLE_DRIVE_CLIENT_ID") or os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET") or os.environ.get("GMAIL_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN")

    if not client_id:
        raise ValueError("GOOGLE_DRIVE_CLIENT_ID (or GMAIL_CLIENT_ID) not set")
    if not client_secret:
        raise ValueError("GOOGLE_DRIVE_CLIENT_SECRET (or GMAIL_CLIENT_SECRET) not set")
    if not refresh_token:
        raise ValueError("GOOGLE_DRIVE_REFRESH_TOKEN not set. Run: python google_drive_handler.py setup")

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

def _http_get(url: str, token: str) -> bytes:
    req = Request(url, headers={"Authorization": f"Bearer {token}"}, method="GET")
    try:
        with urlopen(req, timeout=60) as resp:
            return resp.read()
    except HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}")


def _http_post_json(url: str, token: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}")


def _http_patch_json(url: str, token: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, method="PATCH")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}")


def _http_post_multipart(url: str, token: str, body: bytes, boundary: str) -> dict:
    req = Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/related; boundary={boundary}")
    try:
        with urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}")


# ---------------------------------------------------------------------------
# ID extraction
# ---------------------------------------------------------------------------

def extract_file_id(id_or_url: str) -> str:
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"/document/d/([a-zA-Z0-9_-]+)",
        r"/spreadsheets/d/([a-zA-Z0-9_-]+)",
        r"/presentation/d/([a-zA-Z0-9_-]+)",
        r"/folders/([a-zA-Z0-9_-]+)",
        r"[?&]id=([a-zA-Z0-9_-]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, id_or_url)
        if m:
            return m.group(1)
    return id_or_url  # assume already an ID


# ---------------------------------------------------------------------------
# File type filter
# ---------------------------------------------------------------------------

MIME_FILTERS = {
    "doc": "mimeType='application/vnd.google-apps.document'",
    "sheet": "mimeType='application/vnd.google-apps.spreadsheet'",
    "pdf": "mimeType='application/pdf'",
    "folder": "mimeType='application/vnd.google-apps.folder'",
}

WORKSPACE_EXPORT = {
    "application/vnd.google-apps.document": {
        "mime": "application/pdf",
        "ext": "pdf",
    },
    "application/vnd.google-apps.spreadsheet": {
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ext": "xlsx",
    },
    "application/vnd.google-apps.presentation": {
        "mime": "application/pdf",
        "ext": "pdf",
    },
    "application/vnd.google-apps.drawing": {
        "mime": "application/pdf",
        "ext": "pdf",
    },
}

FILE_FIELDS = "id,name,mimeType,modifiedTime,createdTime,size,webViewLink,owners,parents"


def _build_type_clause(file_type: str) -> str:
    return MIME_FILTERS.get(file_type, "")


def _format_file(f: dict) -> dict:
    owners = f.get("owners") or []
    return {
        "id": f.get("id", ""),
        "name": f.get("name", ""),
        "mimeType": f.get("mimeType", ""),
        "modifiedTime": f.get("modifiedTime", ""),
        "createdTime": f.get("createdTime", ""),
        "size": f.get("size"),
        "url": f.get("webViewLink", ""),
        "owner": owners[0].get("emailAddress", "") if owners else "",
        "parents": f.get("parents", []),
    }


# ---------------------------------------------------------------------------
# Actions: List & Search
# ---------------------------------------------------------------------------

def list_files(token: str, limit: int, file_type: str) -> dict:
    q = "trashed=false"
    clause = _build_type_clause(file_type)
    if clause:
        q += f" and {clause}"

    params = urlencode({
        "q": q,
        "orderBy": "modifiedTime desc",
        "pageSize": limit,
        "fields": f"files({FILE_FIELDS})",
    })
    raw = _http_get(f"{DRIVE_API_BASE}/files?{params}", token)
    data = json.loads(raw)
    files = [_format_file(f) for f in data.get("files", [])]
    return {"success": True, "data": {"count": len(files), "type": file_type, "files": files}}


def search_files(token: str, query: str, limit: int, file_type: str) -> dict:
    # Escape single quotes in query
    safe_q = query.replace("'", "\\'")
    q = f"trashed=false and (name contains '{safe_q}' or fullText contains '{safe_q}')"
    clause = _build_type_clause(file_type)
    if clause:
        q += f" and {clause}"

    params = urlencode({
        "q": q,
        "orderBy": "modifiedTime desc",
        "pageSize": limit,
        "fields": f"files({FILE_FIELDS})",
    })
    raw = _http_get(f"{DRIVE_API_BASE}/files?{params}", token)
    data = json.loads(raw)
    files = [_format_file(f) for f in data.get("files", [])]
    return {"success": True, "data": {"query": query, "type": file_type, "count": len(files), "files": files}}


def get_file(token: str, file_id: str) -> dict:
    fields = "id,name,mimeType,modifiedTime,createdTime,size,webViewLink,owners,parents,shared,sharingUser,permissions,description"
    params = urlencode({"fields": fields})
    raw = _http_get(f"{DRIVE_API_BASE}/files/{file_id}?{params}", token)
    data = json.loads(raw)

    result = _format_file(data)
    result["description"] = data.get("description", "")
    result["shared"] = data.get("shared", False)
    result["permissions"] = [
        {
            "id": p.get("id", ""),
            "type": p.get("type", ""),
            "role": p.get("role", ""),
            "emailAddress": p.get("emailAddress", ""),
            "displayName": p.get("displayName", ""),
        }
        for p in data.get("permissions", [])
    ]
    return {"success": True, "data": result}


# ---------------------------------------------------------------------------
# Actions: Download
# ---------------------------------------------------------------------------

def download_file(token: str, file_id: str, output_path: Optional[str]) -> dict:
    # Get metadata
    meta_params = urlencode({"fields": "id,name,mimeType,size"})
    meta_raw = _http_get(f"{DRIVE_API_BASE}/files/{file_id}?{meta_params}", token)
    meta = json.loads(meta_raw)

    mime_type = meta.get("mimeType", "")
    file_name = meta.get("name", "download")

    if mime_type in WORKSPACE_EXPORT:
        export = WORKSPACE_EXPORT[mime_type]
        export_params = urlencode({"mimeType": export["mime"]})
        url = f"{DRIVE_API_BASE}/files/{file_id}/export?{export_params}"
        if not output_path:
            output_path = f"{file_name}.{export['ext']}"
    else:
        url = f"{DRIVE_API_BASE}/files/{file_id}?alt=media"
        if not output_path:
            output_path = file_name

    content = _http_get(url, token)
    with open(output_path, "wb") as fh:
        fh.write(content)

    return {
        "success": True,
        "data": {
            "fileId": file_id,
            "fileName": file_name,
            "mimeType": mime_type,
            "outputPath": output_path,
            "size": len(content),
        },
    }


# ---------------------------------------------------------------------------
# Actions: Upload
# ---------------------------------------------------------------------------

def upload_file(token: str, file_path: str, folder_id: Optional[str], name: Optional[str]) -> dict:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name = name or os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as fh:
        file_content = fh.read()

    metadata: dict = {"name": file_name}
    if folder_id:
        metadata["parents"] = [folder_id]

    boundary = "boundary_gdrive_hive_upload"
    meta_json = json.dumps(metadata).encode("utf-8")

    parts = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
    ).encode("utf-8")
    parts += meta_json
    parts += (
        f"\r\n--{boundary}\r\n"
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8")
    parts += file_content
    parts += f"\r\n--{boundary}--".encode("utf-8")

    url = f"{DRIVE_UPLOAD_BASE}/files?uploadType=multipart&fields=id,name,mimeType,webViewLink,size"
    data = _http_post_multipart(url, token, parts, boundary)

    return {
        "success": "id" in data,
        "data": {
            "fileId": data.get("id"),
            "name": data.get("name", file_name),
            "mimeType": data.get("mimeType", mime_type),
            "url": data.get("webViewLink"),
            "size": data.get("size"),
        },
    }


# ---------------------------------------------------------------------------
# Actions: Folders
# ---------------------------------------------------------------------------

def create_folder(token: str, name: str, parent_id: Optional[str]) -> dict:
    metadata: dict = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    url = f"{DRIVE_API_BASE}/files?fields=id,name,webViewLink"
    data = _http_post_json(url, token, metadata)

    return {
        "success": "id" in data,
        "data": {
            "folderId": data.get("id"),
            "name": data.get("name", name),
            "url": data.get("webViewLink"),
        },
    }


def move_file(token: str, file_id: str, new_folder_id: str) -> dict:
    # Get current parents
    meta_params = urlencode({"fields": "id,name,parents"})
    meta_raw = _http_get(f"{DRIVE_API_BASE}/files/{file_id}?{meta_params}", token)
    meta = json.loads(meta_raw)
    current_parents = ",".join(meta.get("parents", []))

    params = urlencode({
        "addParents": new_folder_id,
        "removeParents": current_parents,
        "fields": "id,name,parents,webViewLink",
    })
    url = f"{DRIVE_API_BASE}/files/{file_id}?{params}"
    data = _http_patch_json(url, token, {})

    return {
        "success": "id" in data,
        "data": {
            "fileId": data.get("id", file_id),
            "name": data.get("name", ""),
            "newParents": data.get("parents", []),
            "url": data.get("webViewLink"),
        },
    }


def list_folders(token: str, parent_id: Optional[str]) -> dict:
    q = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        q += f" and '{parent_id}' in parents"

    params = urlencode({
        "q": q,
        "orderBy": "name",
        "pageSize": 100,
        "fields": "files(id,name,modifiedTime,webViewLink,parents)",
    })
    raw = _http_get(f"{DRIVE_API_BASE}/files?{params}", token)
    data = json.loads(raw)

    folders = [
        {
            "id": f["id"],
            "name": f.get("name", ""),
            "modifiedTime": f.get("modifiedTime", ""),
            "url": f.get("webViewLink", ""),
            "parents": f.get("parents", []),
        }
        for f in data.get("files", [])
    ]
    return {"success": True, "data": {"count": len(folders), "parentId": parent_id, "folders": folders}}


# ---------------------------------------------------------------------------
# Actions: Share
# ---------------------------------------------------------------------------

def share_file(token: str, file_id: str, email: str, role: str) -> dict:
    url = f"{DRIVE_API_BASE}/files/{file_id}/permissions"
    body = {"type": "user", "role": role, "emailAddress": email}
    data = _http_post_json(url, token, body)

    return {
        "success": "id" in data,
        "data": {
            "permissionId": data.get("id"),
            "fileId": file_id,
            "email": email,
            "role": role,
        },
    }


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def print_setup_instructions() -> dict:
    client_id = os.environ.get("GOOGLE_DRIVE_CLIENT_ID") or os.environ.get("GMAIL_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET") or os.environ.get("GMAIL_CLIENT_SECRET", "")

    instructions = """
Google Drive OAuth Setup Instructions
======================================

1. Go to Google Cloud Console: https://console.cloud.google.com/

2. Use existing project (same as Gmail) or create new.

3. Enable Google Drive API:
   - APIs & Services > Enable APIs and Services
   - Search "Google Drive API" > Enable

4. OAuth credentials (reuse Gmail creds if available):
   - APIs & Services > Credentials > your OAuth Client
   - Note GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET
   - (Can reuse GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET)

5. Get refresh token via OAuth Playground:
   - Go to: https://developers.google.com/oauthplayground/
   - Click gear icon > "Use your own OAuth credentials"
   - Enter Client ID and Client Secret
   - In Step 1, add these scopes:
       https://www.googleapis.com/auth/drive.file
       https://www.googleapis.com/auth/drive.readonly
       https://www.googleapis.com/auth/drive.metadata.readonly
   - Click "Authorize APIs" and complete the flow
   - In Step 2, click "Exchange authorization code for tokens"
   - Copy the "Refresh token" value

6. Set environment variables:
   export GOOGLE_DRIVE_CLIENT_ID="your-client-id"
   export GOOGLE_DRIVE_CLIENT_SECRET="your-client-secret"
   export GOOGLE_DRIVE_REFRESH_TOKEN="your-refresh-token"

   (Falls back to GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET if Drive-specific not set)

7. Verify:
   python google_drive_handler.py list
"""
    print(instructions)
    return {"success": True, "data": {"message": "Setup instructions printed"}}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Google Drive API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    subparsers.add_parser("setup", help="Print OAuth setup instructions")

    # list
    p = subparsers.add_parser("list", help="List recent files")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--type", dest="file_type", default="all",
                   choices=["all", "doc", "sheet", "pdf", "folder"])

    # search
    p = subparsers.add_parser("search", help="Search files")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--type", dest="file_type", default="all",
                   choices=["all", "doc", "sheet", "pdf", "folder"])

    # get
    p = subparsers.add_parser("get", help="Get file metadata")
    p.add_argument("id_or_url", help="File ID or Google URL")

    # download
    p = subparsers.add_parser("download", help="Download a file")
    p.add_argument("id_or_url", help="File ID or Google URL")
    p.add_argument("--output", default=None, help="Output path")

    # upload
    p = subparsers.add_parser("upload", help="Upload a file")
    p.add_argument("path", help="Local file path")
    p.add_argument("--folder", default=None, help="Destination folder ID")
    p.add_argument("--name", default=None, help="Override filename")

    # mkdir
    p = subparsers.add_parser("mkdir", help="Create a folder")
    p.add_argument("name", help="Folder name")
    p.add_argument("--parent", default=None, help="Parent folder ID")

    # move
    p = subparsers.add_parser("move", help="Move file to folder")
    p.add_argument("file_id", help="File ID or URL")
    p.add_argument("folder_id", help="Destination folder ID")

    # share
    p = subparsers.add_parser("share", help="Share file with a user")
    p.add_argument("file_id", help="File ID or URL")
    p.add_argument("email", help="Recipient email")
    p.add_argument("--role", default="reader", choices=["reader", "writer", "commenter"])
    p.add_argument("--allow-external", action="store_true",
                   help="Allow sharing outside publica.la")

    # folders
    p = subparsers.add_parser("folders", help="List folders")
    p.add_argument("--parent", default=None, help="Parent folder ID")

    args = parser.parse_args()

    try:
        if args.command == "setup":
            result = print_setup_instructions()

        elif args.command == "list":
            token = get_access_token()
            result = list_files(token, args.limit, args.file_type)

        elif args.command == "search":
            token = get_access_token()
            result = search_files(token, args.query, args.limit, args.file_type)

        elif args.command == "get":
            token = get_access_token()
            file_id = extract_file_id(args.id_or_url)
            result = get_file(token, file_id)

        elif args.command == "download":
            token = get_access_token()
            file_id = extract_file_id(args.id_or_url)
            result = download_file(token, file_id, args.output)

        elif args.command == "upload":
            token = get_access_token()
            result = upload_file(token, args.path, args.folder, args.name)

        elif args.command == "mkdir":
            token = get_access_token()
            result = create_folder(token, args.name, args.parent)

        elif args.command == "move":
            token = get_access_token()
            file_id = extract_file_id(args.file_id)
            result = move_file(token, file_id, args.folder_id)

        elif args.command == "share":
            email_domain = args.email.rsplit("@", 1)[-1].lower()
            if not args.allow_external and email_domain not in ALLOWED_DOMAINS:
                result = {
                    "success": False,
                    "error": (
                        f"Domain '{email_domain}' not allowed. "
                        f"Allowed: {', '.join(ALLOWED_DOMAINS)}. "
                        "Use --allow-external to override."
                    ),
                }
            else:
                token = get_access_token()
                file_id = extract_file_id(args.file_id)
                result = share_file(token, file_id, args.email, args.role)

        elif args.command == "folders":
            token = get_access_token()
            result = list_folders(token, args.parent)

        else:
            result = {"success": False, "error": f"Unknown command: {args.command}"}

    except (ValueError, FileNotFoundError, RuntimeError) as e:
        result = {"success": False, "error": str(e)}
    except Exception as e:
        result = {"success": False, "error": f"Unexpected: {e}"}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
