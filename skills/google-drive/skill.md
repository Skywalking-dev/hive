---
name: google-drive
description: Manage files and folders in Google Drive - list, search, download, upload, share, and organize. Use when user needs Drive file operations.
allowed-tools: Bash, Read
---

# Google Drive API

Manage Google Drive files and folders via Python script.

## Guardrails

- **NEVER share files outside @publica.la** without explicit user approval.
- `share` blocks external domains by default. Use `--allow-external` only when user explicitly requests.
- Always confirm with user before sharing, uploading, or moving files.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env` (or `GOOGLE_DRIVE_CLIENT_ID`)
- `GMAIL_CLIENT_SECRET` in `.env` (or `GOOGLE_DRIVE_CLIENT_SECRET`)
- `GOOGLE_DRIVE_REFRESH_TOKEN` in `.env`

## First-time Setup

```bash
python scripts/google_drive_handler.py setup
```

## Commands

```bash
# List recent files
python scripts/google_drive_handler.py list [--limit=10] [--type=all]

# Search files
python scripts/google_drive_handler.py search "query" [--limit=10] [--type=all]

# Get file metadata
python scripts/google_drive_handler.py get <id_or_url>

# Download a file
python scripts/google_drive_handler.py download <id> [--output=path]

# Upload a file
python scripts/google_drive_handler.py upload <path> [--folder=id] [--name=name]

# Create a folder
python scripts/google_drive_handler.py mkdir <name> [--parent=id]

# Move a file
python scripts/google_drive_handler.py move <file_id> <folder_id>

# Share a file (restricted to @publica.la)
python scripts/google_drive_handler.py share <file_id> <email> [--role=reader] [--allow-external]

# List folders
python scripts/google_drive_handler.py folders [--parent=id]
```

## Options

- `--limit=<n>` - Number of results (default: 10)
- `--type=<type>` - Filter by type: all, doc, sheet, pdf, folder
- `--output=<path>` - Output path for download
- `--folder=<id>` - Target folder for upload
- `--name=<name>` - File name for upload
- `--parent=<id>` - Parent folder for mkdir/folders
- `--role=<role>` - Share role: reader, writer (default: reader)
- `--allow-external` - Allow sharing outside @publica.la

Accepts full Google Drive/Docs/Sheets URLs or bare file IDs.

## Examples

```bash
# List 5 most recent files
python scripts/google_drive_handler.py list --limit=5

# List only Google Docs
python scripts/google_drive_handler.py list --type=doc

# Search for spreadsheets
python scripts/google_drive_handler.py search "presupuesto" --type=sheet

# Get file info from URL
python scripts/google_drive_handler.py get "https://drive.google.com/file/d/abc123/view"

# Download a file
python scripts/google_drive_handler.py download abc123 --output=./local-copy.pdf

# Upload to specific folder
python scripts/google_drive_handler.py upload ./report.pdf --folder=folder123

# Create folder
python scripts/google_drive_handler.py mkdir "Q1 2026" --parent=folder123

# Move file
python scripts/google_drive_handler.py move abc123 folder456

# Share internally
python scripts/google_drive_handler.py share abc123 user@publica.la --role=writer

# Browse folders
python scripts/google_drive_handler.py folders --parent=root
```

## Output

All commands return JSON with `{success, data}` wrapper:
- `list`/`search`: `{count, type, files: [{id, name, mimeType, modifiedTime, size, url, owner, parents}]}`
- `get`: File metadata with permissions and sharing info
- `download`: `{success, fileId, fileName, mimeType, outputPath, size}`
- `upload`: `{success, fileId, name, mimeType, url, size}`
- `mkdir`: `{success, folderId, name, url}`
- `move`: `{success, fileId, name, newParents, url}`
- `share`: `{success, permissionId, fileId, email, role}`
- `folders`: `{count, parentId, folders: [{id, name, modifiedTime, url, parents}]}`
