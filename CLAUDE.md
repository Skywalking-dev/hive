# Hive

> AI Tooling Omnimodal - Skywalking
> Claude Code Plugin

## Overview

Hive es el repositorio central de AI tooling para Skywalking. Provee skills, agents y scripts para interactuar con nuestro stack de forma unificada desde cualquier AI provider.

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
├── .claude-plugin/
│   └── plugin.json   ← plugin manifest
├── skills/            ← slash commands + knowledge (source of truth)
├── agents/            ← specialist agent definitions
├── scripts/           ← Python API handlers
├── docs/              ← security model, env reference
├── .mcp.json          ← MCP servers config (gws, n8n, etc.)
└── release.py         ← sync to Cursor, Gemini CLI, Codex
```

## Providers

| Provider | Config Dir | Method |
|----------|------------|--------|
| Claude Code | `.claude-plugin/` | plugin format |
| Cursor | `.cursor/` | symlink + .mdc |
| Gemini CLI | `.agent/` | symlink |
| Codex | `.codex/` | symlink |

## Usage

```bash
# Install third-party skills
uv run hive install --all

# Sync to all providers
uv run hive setup

# Use slash commands
/gmail inbox --unread
/slack read <thread_url>
/perplexity "query"
/shape
/ship_it
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
