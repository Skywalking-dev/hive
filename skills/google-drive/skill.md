---
name: google-drive
description: Manage files and folders in Google Drive - list, search, download, upload, share, and organize. Use when user needs Drive file operations.
allowed-tools: Bash, Read
---

# Google Drive API

Manage Google Drive files and folders via unified bash handler.

## Guardrails

- **NEVER share files outside @publica.la** without explicit user approval.
- `share` blocks external domains by default. Use `--allow-external` only when user explicitly requests.
- Always confirm with user before sharing, uploading, or moving files.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env` (or `GOOGLE_CLIENT_ID` / `GOOGLE_DRIVE_CLIENT_ID`)
- `GMAIL_CLIENT_SECRET` in `.env` (or `GOOGLE_CLIENT_SECRET` / `GOOGLE_DRIVE_CLIENT_SECRET`)
- `GOOGLE_DRIVE_REFRESH_TOKEN` in `.env` (or `GOOGLE_REFRESH_TOKEN`)

## Commands

```bash
# List recent files
scripts/google_handler.sh drive list [--limit=10] [--type=all]

# List files in folder
scripts/google_handler.sh drive list --folder-id=<id>

# Search files
scripts/google_handler.sh drive search "query" [--limit=10] [--type=all]

# Get file metadata
scripts/google_handler.sh drive get <id_or_url>

# Download a file
scripts/google_handler.sh drive download <id> [--output=path]

# Upload a file
scripts/google_handler.sh drive upload <path> [--folder-id=id] [--name=name]

# Create a folder
scripts/google_handler.sh drive mkdir <name> [--parent=id]

# Move a file
scripts/google_handler.sh drive move <file_id> <folder_id>

# Share a file (restricted to @publica.la)
scripts/google_handler.sh drive share <file_id> <email> [--role=reader] [--allow-external]

# List folders
scripts/google_handler.sh drive folders [--parent=id]
```

## Options

- `--limit=<n>` — Number of results (default: 10)
- `--type=<type>` — Filter: all, doc, sheet, pdf, folder
- `--folder-id=<id>` — Filter list to folder; target for upload
- `--output=<path>` — Output path for download
- `--name=<name>` — File name override for upload
- `--parent=<id>` — Parent folder for mkdir / folders
- `--role=<role>` — Share role: reader, writer (default: reader)
- `--allow-external` — Allow sharing outside @publica.la

Accepts full Google Drive/Docs/Sheets URLs or bare file IDs.

## Examples

```bash
# List 5 most recent files
scripts/google_handler.sh drive list --limit=5

# List only Google Docs
scripts/google_handler.sh drive list --type=doc

# Search for spreadsheets
scripts/google_handler.sh drive search "presupuesto" --type=sheet

# Get file info from URL
scripts/google_handler.sh drive get "https://drive.google.com/file/d/abc123/view"

# Download a file
scripts/google_handler.sh drive download abc123 --output=./local-copy.pdf

# Upload to specific folder
scripts/google_handler.sh drive upload ./report.pdf --folder-id=folder123

# Create folder
scripts/google_handler.sh drive mkdir "Q1 2026" --parent=folder123

# Move file
scripts/google_handler.sh drive move abc123 folder456

# Share internally
scripts/google_handler.sh drive share abc123 user@publica.la --role=writer

# Browse folders
scripts/google_handler.sh drive folders --parent=root
```

## Output

All commands return JSON `{"success": true, "data": {...}}`:
- `list`/`search`: `{count, type, files: [{id, name, mimeType, modifiedTime, size, url, owner, parents}]}`
- `get`: File metadata with permissions and sharing info
- `download`: `{fileId, fileName, mimeType, outputPath, size}`
- `upload`: `{fileId, name, mimeType, url, size}`
- `mkdir`: `{folderId, name, url}`
- `move`: `{fileId, name, newParents, url}`
- `share`: `{permissionId, fileId, email, role}`
- `folders`: `{count, parentId, folders: [{id, name, modifiedTime, url, parents}]}`
