# Hive

Give your AI coding assistant superpowers. 40+ skills, 10 agents (1 orchestrator + 9 specialists), one repo — works with Claude Code, Cursor, Gemini CLI, and Codex.

## What is Hive?

Hive turns your AI assistant into a full dev team. Instead of copy-pasting API docs or writing boilerplate, just use slash commands:

```bash
/gmail inbox --unread                        # check email
/perplexity "best auth library for Next.js"  # search the web
/google-docs get <url>                       # read a doc as Markdown
/slack read <thread_url>                     # catch up on a thread
/shape                                       # create a well-defined issue
/ship_it                                     # commit, push, open PR
```

Need something bigger? Delegate to specialist agents that handle design, frontend, backend, QA, SEO, and more — each with deep domain knowledge.

## Quick Start

```bash
# Clone into your workspace
cd ~/workspace
git clone https://github.com/Skywalking-dev/hive.git
cd hive
uv sync                          # install Python deps
cp .env.example .env             # add only the keys you need
uv run hive install --all   # install third-party skills (n8n, Anthropic)

# Install into workspace (creates symlinks one level up)
uv run hive setup
```

This creates symlinks in your workspace root so Claude Code, Cursor, and other providers can find hive's skills and agents:

```
~/workspace/                     ← open Claude Code here
├── .claude/
│   ├── skills/ → hive/skills/   ← symlink
│   └── agents/ → hive/agents/   ← symlink
├── .cursor/rules/               ← generated .mdc files
├── hive/                        ← this repo (source of truth)
│   ├── skills/
│   ├── agents/
│   └── scripts/
└── your-projects/
```

> All integrations are optional. Hive works with zero API keys — just add them as you need each integration.

## How It Works

```
hive/
├── .claude-plugin/
│   └── plugin.json    ← plugin manifest
├── skills/             ← active skills (core + installed packs)
├── available/          ← pack skills (not active until installed)
│   ├── google/
│   ├── marketing/
│   ├── devops/
│   └── ...
├── packs/              ← pack definitions (JSON)
├── agents/             ← 10 agent definitions (1 orchestrator + 9 specialists)
├── scripts/            ← Python handlers for external APIs
├── docs/               ← security model, env variable reference
└── hive.py             ← CLI: install packs, setup workspace
```

**Skills** are Markdown files that teach your AI assistant how to use a tool. Each skill maps to a `/slash-command` and declares which tools the AI can use. The AI reads the skill, understands the API, and executes it.

**Agents** are specialist personas with deep domain knowledge. You delegate tasks to them and they work autonomously.

**Scripts** are lightweight Python handlers that connect skills to external APIs (Gmail, Slack, Google Drive, etc.). All credentials come from `.env` — nothing is hardcoded.

## Skills

### Google

| Command | What it does |
|---------|-------------|
| `/gmail` | Read inbox, search, drafts, labels, filters |
| `/google-docs` | Read, create, update, export docs as Markdown |
| `/google-drive` | List, search, upload, download, share files |
| `/google-calendar` | View events, check availability |
| `/google-workspace` | Sheets, Tasks, Chat, Slides via gws CLI |
| `/extract_transcript` | YouTube transcript extraction |

### Search & AI

| Command | What it does |
|---------|-------------|
| `/perplexity` | Web search with AI summaries (Sonar API) |
| `/video-analysis` | Transcript analysis into structured insights |

### Communication

| Command | What it does |
|---------|-------------|
| `/slack` | Read threads, send messages, upload files |
| `/whatsapp` | Send messages via WhatsApp Business API |

### Infrastructure

| Command | What it does |
|---------|-------------|
| `/supabase` | Database queries, migrations, auth |
| `/vercel` | Deploy, env vars, logs, cron |

### Development Workflow

| Command | What it does |
|---------|-------------|
| `/shape` | Guided issue creation with templates |
| `/refine` | Technical breakdown into agent sub-issues |
| `/dev` | Orchestrate work across agents |
| `/ship_it` | Commit + push + open PR in one step |
| `/pr-review` | PR review with issue sync |
| `/capture` | Quick idea capture to backlog |

### Development Tools

| Command | What it does |
|---------|-------------|
| `/test-debug` | E2E test execution with real-time monitoring |
| `/github-cli` | Git workflows, PR management, branch cleanup |
| `/adversarial_review` | Technical review via external AI agents |

### Media

| Command | What it does |
|---------|-------------|
| `/process_audio` | Audio conversion and transcription |

## Agents

### Mentat — AI General Advisor

The orchestrator. Mentat coordinates the entire agent ecosystem: breaks down complex work, delegates to specialists, synthesizes results, and ensures delivery. Think system architect + project manager + technical lead in one.

- Strategic planning and architecture design
- Multi-agent coordination and task routing
- Business-technical bridge (ROI-driven decisions)
- n8n workflow design and optimization

### Specialists

Domain experts that Mentat delegates to. Each one has deep knowledge and works autonomously.

| Agent | What they do |
|-------|-------------|
| **Aurora** | Brand identity, design systems, UI mockups, test ID contracts |
| **Pixel** | Next.js/React implementation, performance, accessibility |
| **Kokoro** | FastAPI, databases, auth, backend architecture |
| **Centinela** | QA strategy, Playwright E2E, regression testing |
| **Hermes** | Vercel deployments, CI/CD, edge functions, monitoring |
| **Flux** | n8n workflows, integrations, automation |
| **Oraculo** | Web research, competitive intel, tech evaluation |
| **Pregon** | Content strategy, social media, email campaigns |
| **Lumen** | Technical SEO, Core Web Vitals, schema markup |

## Multi-Provider Sync

Write skills once, use them everywhere:

| Provider | How it syncs |
|----------|-------------|
| Claude Code | `.claude-plugin/` — plugin format (native) |
| Cursor | `.cursor/rules/` — auto-generated `.mdc` files |
| Gemini CLI | `.agent/` — symlink |
| Codex | `.codex/` — symlink |

```bash
uv run hive setup       # sync to Cursor, Gemini CLI, Codex
```

## Security

Hive is designed to be operated by AI agents, so security guardrails are built in:

- **Write operations require `--confirm`** — without it, scripts show a dry-run preview and exit. The AI must show you what it will do before executing.
- **Gmail sending is permanently blocked** — the handler only creates drafts. You review and send manually.
- **Google Drive sharing is domain-restricted** — external sharing requires explicit `--allow-external` flag.
- **Pre-commit hook** scans for API keys, tokens, and private keys before every commit.
- **Zero hardcoded credentials** — everything comes from `.env`.

See [docs/SECURITY.md](docs/SECURITY.md) for the full model.

## Configuration

See [docs/ENV_VARIABLES.md](docs/ENV_VARIABLES.md) for every API key mapped to its script, skill, and purpose.

## Creating Skills

A skill is a Markdown file in `skills/<name>/SKILL.md`:

```yaml
---
name: my-skill
description: What it does. When to trigger it.
allowed-tools: Bash, Read
---

# Instructions for the AI...
```

Use `/skill-creator` for guided creation, or add the file manually.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- API keys for the integrations you want (all optional)

## Skill Packs

Hive ships with core workflow skills. Everything else installs via packs:

```bash
uv run hive install --list              # see all packs
uv run hive install google devops       # install specific packs
uv run hive install --all               # install everything
uv run hive install remove marketing  # uninstall a pack
```

| Pack | Skills | What's in it |
|------|--------|-------------|
| **core** | 10 | shape, capture, refine, dev, push_it, ship_it, reunion (always installed) |
| **google** | 6 | Gmail, Docs, Drive, Calendar, Workspace, YouTube |
| **marketing** | 8 | Copywriting, cold email, CRO, pricing, content, social |
| **devops** | 4 | Vercel, Supabase, GitHub CLI, test debugging |
| **communication** | 2 | Slack, WhatsApp |
| **media** | 2 | Audio processing, video analysis |
| **tools** | 5 | Perplexity, adversarial review, budgets, reports, travel |
| **n8n** | 7 | n8n automation ([czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills), MIT) |
| **anthropic** | 3 | PDF tools, skill creator, frontend design ([Anthropic](https://github.com/anthropics/skills), Proprietary) |

## Contributing

Issues and PRs welcome. Hive is maintained by [Skywalking](https://skywalking.dev), a dev studio in Patagonia, Argentina.

## License

MIT
