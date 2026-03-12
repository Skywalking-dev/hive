---
name: google-docs
description: Read, create, and manage Google Docs with Markdown conversion. Use when user needs to read, write, search, or export Google Docs.
allowed-tools: Bash, Read
---

# Google Docs API

Read, create, update, and export Google Docs with Markdown conversion via Python script.

## Guardrails

- Always confirm with user before creating or updating a Google Doc.
- When using `--replace`, warn that existing content will be overwritten.

## Prerequisites

- `GMAIL_CLIENT_ID` in `.env` (or `GOOGLE_DOCS_CLIENT_ID`)
- `GMAIL_CLIENT_SECRET` in `.env` (or `GOOGLE_DOCS_CLIENT_SECRET`)
- `GOOGLE_DOCS_REFRESH_TOKEN` in `.env`

APIs required: Google Docs API + Google Drive API.

## First-time Setup

```bash
python scripts/google_docs_handler.py setup
```

## Commands

```bash
# Get doc as Markdown
python scripts/google_docs_handler.py get <id_or_url>

# Get doc with rich metadata (suggestions)
python scripts/google_docs_handler.py get <id_or_url> --rich

# Create a new doc
python scripts/google_docs_handler.py create <title> [--body="# Markdown content"]

# Update doc content
python scripts/google_docs_handler.py update <id_or_url> --body="## New section"
python scripts/google_docs_handler.py update <id_or_url> --body="# Replace all" --replace

# List recent docs
python scripts/google_docs_handler.py list [--limit=10]

# Search docs
python scripts/google_docs_handler.py search "query" [--limit=10]

# Export doc
python scripts/google_docs_handler.py export <id_or_url> [--format=md]
```

Supported export formats: `md`, `txt`, `html`, `pdf`, `docx`, `epub`.
Binary formats (pdf/docx/epub) output raw bytes - redirect to file:
```bash
python scripts/google_docs_handler.py export abc123 --format=pdf > doc.pdf
```

## Options

- `--body=<markdown>` - Markdown content for create/update
- `--body-stdin` - Read content from stdin
- `--replace` - Replace existing content (with `update`)
- `--rich` - Get metadata and suggestions count (with `get`)
- `--format=<fmt>` - Export format: md, txt, html, pdf, docx, epub
- `--limit=<n>` - Number of results (default: 10)

Accepts full Google Docs URLs or bare document IDs.

## Examples

```bash
# List recent docs
python scripts/google_docs_handler.py list --limit=5

# Read a doc by URL
python scripts/google_docs_handler.py get "https://docs.google.com/document/d/abc123/edit"

# Create doc with inline Markdown
python scripts/google_docs_handler.py create "Sprint Notes" --body="# Sprint 42\n\n- Item 1"

# Create doc piping from file
cat notes.md | python scripts/google_docs_handler.py create "From file" --body-stdin

# Append to existing doc
python scripts/google_docs_handler.py update abc123 --body="## Added section"

# Replace entire content
python scripts/google_docs_handler.py update abc123 --body="# Fresh start" --replace

# Search docs
python scripts/google_docs_handler.py search "presupuesto" --limit=5

# Export to PDF
python scripts/google_docs_handler.py export abc123 --format=pdf > doc.pdf
```

## Output

All commands return JSON with `{success, data}` wrapper:
- `get`: `{documentId, title, url, modifiedTime, createdTime, content}`
- `get --rich`: `{documentId, title, url, revisionId, suggestionsCount, content}`
- `create`: `{success, documentId, title, url}`
- `update`: `{success, documentId, title, url, updatesApplied}`
- `list`: `{count, documents: [{documentId, title, modifiedTime, createdTime, url, owner}]}`
- `search`: `{query, count, documents: [...]}`
- `export`: `{documentId, format, content}` (text) or raw binary (pdf/docx/epub)
