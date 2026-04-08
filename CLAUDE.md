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
| Gemini API | Image generation (Imagen 4.0, Nano Banana), TTS |
| Google Stitch | Design-to-code, UI generation, React components (MCP) |

## Architecture

```
hive/
├── .claude-plugin/
│   └── plugin.json   ← plugin manifest
├── .github/workflows/ ← GitHub Actions (monitor, issue handler, review)
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
/push_it                    # commit + push + PR
/ship_it                    # review → fix → merge → deploy → verify
/generate_image "prompt"    # create image via Gemini
/process_video <url>        # extract + analyze video
```

## Skills (Senses Framework)

Skills are sensory extensions — each one gives Mentat a new capability.

### Perceive
| Skill | Sense | What |
|-------|-------|------|
| `process_audio` | Hear | Audio → text (Whisper) |
| `process_video` | Watch | Video → transcript → analysis |
| `perplexity` | Research | Real-time web knowledge |

### Express
| Skill | Sense | What |
|-------|-------|------|
| `generate_image` | Visual expression | Idea → image (Gemini Imagen 4.0 + Nano Banana) |
| `generate_audio` | Speak | Text → voice (TODO: Gemini TTS) |

### Interact
| Skill | Sense | What |
|-------|-------|------|
| `claude-in-chrome` | Touch | Operate browser as human |

### Shipping Pipeline
| Skill | Purpose |
|-------|---------|
| `push_it` | Commit + push + open PR |
| `ship_it` | Calls /pr-review → fix loop → merge → deploy → verify |
| `pr-review` | PR review + Linear sync (standalone or via ship_it) |
| `github-cli` | Git workflows, branch housekeeping |

### Linear Operations
| Skill | Purpose |
|-------|---------|
| `shape` | Guided discovery → Linear issue |
| `capture` | Quick idea → Linear backlog |
| `refine` | Technical breakdown → agent sub-issues |
| `dev` | Orchestrate agent work on issue |
| `backlog_manager` | Issue CRUD, queries, state changes |
| `delegation_rules` | Route to specialist agents |

### Development
| Skill | Purpose |
|-------|---------|
| `frontend-design` | Distinctive UI, no generic AI look |
| `pdf` | PDF extract, merge, fill forms |
| `vercel` | Deploy, env, logs, cron |
| `supabase` | DB queries, migrations, auth, logs |
| `report-viewer` | HTML dashboards, auto-open in browser |
| `test-debug` | E2E test execution + collaborative debugging |

### Marketing & Content
| Skill | Purpose |
|-------|---------|
| `copywriting` | Landing pages, hero sections, CTAs |
| `social-content` | LinkedIn posts, X threads |
| `content-strategy` | Content calendars, blog topics |
| `cold-email` | B2B outreach sequences |
| `email-sequence` | Nurture drips, onboarding flows |
| `competitor-alternatives` | Battle cards, positioning |
| `page-cro` | Conversion rate optimization |
| `pricing-strategy` | Pricing tiers, LATAM adaptation |

### Communication
| Skill | Purpose |
|-------|---------|
| `gmail` | Read, draft, organize email |
| `slack-api` | Read/post Slack threads |
| `whatsapp` | Send WhatsApp Business messages |
| `google-docs` | Read/create Google Docs |
| `google-drive` | File management in Drive |
| `google-calendar` | Events, availability |
| `google-workspace` | All Google APIs fallback |

### Finance
| Skill | Purpose |
|-------|---------|
| `financial-advisor` | Portfolio analysis, asset allocation |
| `binance` | Spot/futures, balances, orders |
| `gate` | Gate.io markets, earn, positions |

### n8n Automation
| Skill | Purpose |
|-------|---------|
| `n8n-code-javascript` | JS Code nodes |
| `n8n-code-python` | Python Code nodes |
| `n8n-expression-syntax` | Expression validation |
| `n8n-node-configuration` | Node config guidance |
| `n8n-workflow-patterns` | Architecture patterns |
| `n8n-validation-expert` | Error interpretation |
| `n8n-mcp-tools-expert` | MCP tool usage |

### Incident Response
| Skill | Purpose |
|-------|---------|
| `investigate` | Systematic debugging — evidence-first, rollback-first |
| `postmortem` | Blameless incident documentation |

### Other
| Skill | Purpose |
|-------|---------|
| `adversarial_review` | Debate invocation (Forge) |
| `reunion` | Multi-agent meeting |
| `travel-assistant` | Trip planning, flights, budget |
| `accommodation-search` | Hotels/hostels/apartments via Google Hotels + Booking.com |
| `crear_presupuesto` | Generate presupuestos |
| `skill-creator` | Guided skill creation |

## Scripts (Handlers)

| Script | Used By | API |
|--------|---------|-----|
| `scripts/gemini_handler.sh` | Oraculo, generate_image | Gemini (ask, search, embed) |
| `scripts/openai_handler.sh` | Oraculo | OpenAI (ask, responses, embeddings) |
| `scripts/perplexity_handler.sh` | Oraculo, perplexity skill | Perplexity (ask, search, agent) |
| `scripts/groq_handler.sh` | Reviews, classification | Groq (ask, models) — free tier, 3000+ tok/s |
| `scripts/deepseek_handler.sh` | Reviews, batch tasks | DeepSeek (ask, models) — cheapest frontier |
| `scripts/openrouter_handler.sh` | Fallback, free models | OpenRouter (ask, models, free) — universal gateway |
| `scripts/xai_handler.sh` | Long context | xAI Grok (ask, models) — 2M context, $25 free credit |
| `scripts/cerebras_handler.sh` | Free inference | Cerebras (ask, models) — 1M free TPD, 1500+ tok/s |
| `scripts/fireworks_handler.sh` | Open-source hosting | Fireworks (ask, models) — fastest OSS, fine-tuning |
| `scripts/fal_handler.py` | Image + video gen | fal.ai (image, video, status, models) — FLUX, Kling, Veo, Hailuo |
| `scripts/generate_image.py` | `generate_image` | Gemini Imagen 4.0 + Nano Banana |
| `scripts/transcript_handler.py` | `process_video` | YouTube Transcript API |
| `scripts/binance_handler.py` | `binance` | Binance API |
| `scripts/gate_handler.py` | `gate` | Gate.io API |
| `scripts/accommodation_search.py` | `accommodation-search` | SerpAPI Google Hotels + Booking.com RapidAPI |

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

## Env Vars

Required keys in `.env`:
- `GEMINI_API_KEY` — Image generation (Imagen, Nano Banana)
- `OPENAI_API_KEY` — Audio transcription (Whisper)
- `YOUTUBE_API_KEY` — Video metadata (optional, transcripts are free)
- `BINANCE_API_KEY` / `BINANCE_SECRET_KEY` — Binance trading
- `GATE_API_KEY` / `GATE_SECRET_KEY` — Gate.io trading
- `SERPAPI_KEY` — Google Hotels search (accommodation-search, 100 free/mo)
- `RAPIDAPI_KEY` — Booking.com search (accommodation-search, ~500 free/mo)
