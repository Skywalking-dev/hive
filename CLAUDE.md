# Hive

> AI Tooling Omnimodal — Skywalking Claude Code plugin.
> Source of truth for skills, subagents, scripts, MCP config.

## Overview
Hive centralises AI tooling for Skywalking. Exposes skills + agents + scripts to any AI provider (Claude Code, Cursor, Gemini CLI, Codex) via sync script.

## Architecture
```
hive/
├── .claude-plugin/plugin.json   ← plugin manifest
├── skills/                      ← slash commands (SKILL.md each)
├── agents/                      ← specialist subagent definitions
├── scripts/                     ← Python/shell API handlers
├── docs/                        ← security, env reference
├── .mcp.json                    ← MCP servers (gws, n8n, etc.)
└── release.py                   ← sync → Cursor, Gemini, Codex
```

## Providers

| Provider    | Config Dir        | Method          |
| ----------- | ----------------- | --------------- |
| Claude Code | `.claude-plugin/` | plugin format   |
| Cursor      | `.cursor/`        | symlink + .mdc  |
| Gemini CLI  | `.agent/`         | symlink         |
| Codex       | `.codex/`         | symlink         |

## Skills + Scripts
Full listings → harness autoload (`<available-skills>`) + `@hive/docs/handlers.md`. Not re-listed here to save tokens.

Skill categories: Senses (perceive/express/interact), Shipping, Linear Ops, Development, Marketing, Communication, Finance, n8n, Incident Response.

Script handlers: `groq`, `deepseek`, `openrouter`, `openai`, `gemini`, `perplexity`, `xai`, `cerebras`, `fireworks`, `fal`, plus domain handlers (`binance`, `gate`, `transcript`, `accommodation_search`, `generate_image`, `generate_audio`).

## Skill Format
```yaml
---
name: skill-name
description: What it does. When to use it.
allowed-tools: Tool1, Tool2
---
```

## Commands
```bash
uv run hive install --all    # install third-party skills
uv run hive setup            # sync to all providers
uv sync                      # install deps (Python 3.11+)
```

## Env
Keys in `hive/.env`. Critical: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`, `PERPLEXITY_API_KEY`, `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`, `YOUTUBE_API_KEY`, `BINANCE_API_KEY`/`SECRET`, `GATE_API_KEY`/`SECRET`, `SERPAPI_KEY`, `RAPIDAPI_KEY`.

Full reference: `@hive/docs/env.md`.
