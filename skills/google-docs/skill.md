---
name: google-docs
description: Read, create, and manage Google Docs with Markdown conversion. Use when user needs to read, write, search, or export Google Docs.
allowed-tools: Bash, Read
---

# Google Docs API

Read, create, update, and export Google Docs with Markdown conversion via unified bash handler.

## Guardrails

- Always confirm with user before creating or updating a Google Doc.
- When using `--replace`, warn that existing content will be overwritten.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env` (or `GOOGLE_CLIENT_ID` / `GOOGLE_DOCS_CLIENT_ID`)
- `GMAIL_CLIENT_SECRET` in `.env` (or `GOOGLE_CLIENT_SECRET` / `GOOGLE_DOCS_CLIENT_SECRET`)
- `GOOGLE_DOCS_REFRESH_TOKEN` in `.env` (or `GOOGLE_REFRESH_TOKEN`)

APIs required: Google Docs API + Google Drive API.

## Commands

```bash
# Get doc as Markdown
scripts/google_handler.sh docs read <id_or_url>

# Get doc with rich metadata (suggestions)
scripts/google_handler.sh docs read <id_or_url> --rich

# Create a new doc
scripts/google_handler.sh docs create "Title" [--body="# Markdown content"]

# Create doc from stdin
cat notes.md | scripts/google_handler.sh docs create "From file" --body-stdin

# Update doc content (append)
scripts/google_handler.sh docs update <id_or_url> --body="## New section"

# Update doc content (replace all)
scripts/google_handler.sh docs update <id_or_url> --body="# Replace all" --replace

# List recent docs
scripts/google_handler.sh docs list [--limit=10]

# Search docs
scripts/google_handler.sh docs search "query" [--limit=10]

# Export doc
scripts/google_handler.sh docs export <id_or_url> [--format=md]

# Export binary formats (redirect to file)
scripts/google_handler.sh docs export abc123 --format=pdf --output=doc.pdf
```

Supported export formats: `md`, `txt`, `html`, `pdf`, `docx`, `epub`.

## Options

- `--body=<markdown>` — Markdown content for create/update
- `--body-stdin` — Read content from stdin
- `--replace` — Replace existing content (with `update`)
- `--rich` — Get metadata and suggestions count (with `read`)
- `--format=<fmt>` — Export format: md, txt, html, pdf, docx, epub
- `--output=<path>` — Output file path for binary export
- `--limit=<n>` — Number of results (default: 10)

Accepts full Google Docs URLs or bare document IDs.

## Output

All commands return JSON `{"success": true, "data": {...}}`:
- `read`: `{documentId, title, url, modifiedTime, createdTime, content}`
- `read --rich`: `{documentId, title, url, revisionId, suggestionsCount, content}`
- `create`: `{documentId, title, url}`
- `update`: `{documentId, title, url, updatesApplied}`
- `list`: `{count, documents: [{documentId, title, modifiedTime, createdTime, url, owner}]}`
- `search`: `{query, count, documents: [...]}`
- `export (text)`: `{documentId, format, content}`
- `export (binary with --output)`: `{documentId, format, outputPath}`
