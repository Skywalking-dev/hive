# Hive

> AI Tooling Omnimodal - Skywalking
> Source of truth: `.claude/`

## Overview

Hive es el repositorio central de AI tooling para Skywalking. Provee commands, skills y scripts para interactuar con nuestro stack de forma unificada desde cualquier AI provider.

## Stack

| Service | Purpose |
|---------|---------|
| Supabase | Database, Auth, Edge Functions |
| Vercel | Deployments, Serverless |
| WhatsApp | Business messaging |
| Slack | Team communication |
| gws (Google Workspace CLI) | All Google APIs via CLI + MCP (Sheets, Tasks, Chat, etc.) |

## Architecture

```
hive/
├── .claude/
│   ├── skills/       ← skills = knowledge + slash commands (single source)
│   └── agents/       ← specialist agent definitions
├── scripts/          ← conectores Python (API/CLI)
├── .mcp.json         ← MCP servers config (gws, n8n, etc.)
└── release.py        ← propagación multi-provider
```

> **No commands directory.** Skills replaced commands entirely — one concept, one place.

## Providers

| Provider | Config Dir | Synced From |
|----------|------------|-------------|
| Claude Code | `.claude/` | source |
| Cursor | `.cursor/` | symlink |
| Gemini CLI | `.agent/` | symlink |
| Codex | `.codex/` | symlink |

## Usage

```bash
# Sync to all providers
python release.py

# Run a command
/slack <thread_url>
/supabase <query>
/vercel logs <deployment>
/whatsapp send <number> <message>
/gws sheets spreadsheets.values get --params '{"spreadsheetId": "ID", "range": "A1:D10"}'
```

## Development

Scripts are Python 3.11+. Use `uv` for dependency management.

```bash
cd hive
uv sync
```

## Skill Format (Claude Code Standard)

```yaml
---
name: skill-name
description: What it does. When to use it.
allowed-tools: Tool1, Tool2
---

# Content...
```
