# Hive

Give your AI coding assistant superpowers. 60+ skills, 10 agents, LLM handlers for 6 providers — works with Claude Code, Cursor, Gemini CLI, and Codex.

## What is Hive?

Hive turns your AI assistant into a full dev team. Instead of copy-pasting API docs or writing boilerplate, use slash commands:

```bash
/shape                                       # create a well-defined issue
/dev                                         # orchestrate work across agents
/ship_it                                     # review, fix, merge, deploy, verify
/perplexity "best auth library for Next.js"  # search the web
/gmail inbox --unread                        # check email
/generate_image "a mountain landscape"       # create an image
```

Need something bigger? Delegate to specialist agents that handle design, frontend, backend, QA, SEO, and more.

## Quick Start

```bash
# 1. Clone into your workspace
cd ~/workspace
git clone https://github.com/Skywalking-dev/hive.git

# 2. Install dependencies
cd hive
uv sync

# 3. Configure API keys (add only the ones you need)
cp .env.example .env
# Edit .env with your keys

# 4. Install skill packs
uv run hive install --all

# 5. Setup workspace
uv run hive setup
```

That's it. Open Claude Code from `~/workspace/` and all skills, agents, and handlers are available.

### What `hive setup` does

```
[hive] Actions:
  Symlink ~/workspace/.claude/skills  -> hive/skills     # skills available
  Symlink ~/workspace/.claude/agents  -> hive/agents     # agents available
  Generate .cursor/rules/ from skills                     # Cursor compatible
  Merge .mcp.json configs                                 # MCP servers
  Merge hive/CLAUDE.md into workspace CLAUDE.md           # handler docs
  Verify API keys in hive/.env                            # missing key checklist
```

Setup is **idempotent** — run it again after pulling updates to sync everything.

### Workspace structure after setup

```
~/workspace/                          <- open your AI tool here
├── .claude/
│   ├── skills/ -> hive/skills/       <- symlink
│   └── agents/ -> hive/agents/       <- symlink
├── .cursor/rules/                    <- generated .mdc files
├── .mcp.json                         <- merged MCP servers
├── CLAUDE.md                         <- workspace config + hive handler docs
├── hive/                             <- this repo (source of truth)
│   ├── skills/
│   ├── agents/
│   ├── scripts/
│   └── .env                          <- API keys (gitignored)
└── your-projects/
```

## LLM Handlers

Hive includes shell handlers for 6 LLM providers. All are OAI-compatible and load keys from `hive/.env`.

| Handler | Default Model | Cost out/MTok | Commands |
|---------|---------------|---------------|----------|
| `groq_handler.sh` | Llama 4 Scout | Free | `ask`, `models` |
| `deepseek_handler.sh` | DeepSeek V4 | $0.50 | `ask`, `models` |
| `openrouter_handler.sh` | deepseek-chat | Free with `--free` | `ask`, `models`, `free` |
| `gemini_handler.sh` | Gemini 2.5 Flash | $2.50 (free tier) | `ask`, `search`, `embed` |
| `openai_handler.sh` | GPT-4.1 | $8.00 | `ask`, `responses`, `embeddings` |
| `perplexity_handler.sh` | Sonar Pro | $15.00 | `ask`, `search`, `agent` |

### Usage

```bash
# Free and fast
hive/scripts/groq_handler.sh ask "Explain this error" --json

# Cheapest frontier model
hive/scripts/deepseek_handler.sh ask "Review this code" --system "You are a code reviewer"

# Deep reasoning
hive/scripts/deepseek_handler.sh ask "Analyze this architecture" --reasoner

# Free via OpenRouter
hive/scripts/openrouter_handler.sh ask "Summarize this" --free

# With fallback chain
hive/scripts/openrouter_handler.sh ask "Translate this" --fallbacks "google/gemini-2.5-flash,meta-llama/llama-4-scout"

# Web search with citations
hive/scripts/perplexity_handler.sh search "latest Next.js release"
```

### Model routing by task

| Task | Best pick | Why |
|------|-----------|-----|
| Classification / routing | Groq | Free, 3000+ tok/s |
| Reviews / batch / bulk | DeepSeek V4 | Cheapest frontier ($0.50/MTok) |
| Complex reasoning | DeepSeek R1 | 91% cheaper than Opus |
| Code generation | OpenAI or DeepSeek | Dedicated code models |
| Web search / grounded | Perplexity Sonar | Built-in search + citations |
| Vision / multimodal | Gemini Flash | Free tier, 1M context |
| Fallback / free models | OpenRouter `--free` | 29+ free models |

## Skills

### Core (always installed)

| Command | What it does |
|---------|-------------|
| `/shape` | Guided issue creation with discovery |
| `/capture` | Quick idea to backlog |
| `/refine` | Technical breakdown into agent sub-issues |
| `/dev` | Orchestrate work across agents |
| `/push_it` | Commit + push + open PR |
| `/ship_it` | Full pipeline: review, fix, merge, deploy, verify |
| `/pr-review` | PR review with Linear sync |
| `/reunion` | Multi-agent meeting |

### Senses (sensory extensions)

| Command | Sense | What it does |
|---------|-------|-------------|
| `/process_video` | Watch | Video/YouTube -> transcript -> analysis |
| `/process_audio` | Hear | Audio -> text (Whisper) |
| `/perplexity` | Research | Real-time web knowledge |
| `/generate_image` | Express | Idea -> image (Gemini Imagen 4.0) |
| Chrome automation | Touch | Operate browser as human |

### Google

| Command | What it does |
|---------|-------------|
| `/gmail` | Read inbox, search, drafts, labels, filters |
| `/google-docs` | Read, create, update, export docs as Markdown |
| `/google-drive` | List, search, upload, download, share files |
| `/google-calendar` | View events, check availability |
| `/google-workspace` | Sheets, Tasks, Chat, Slides via gws CLI |

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
| `/github-cli` | Git workflows, PR management, branch cleanup |
| `/test-debug` | E2E test execution with real-time monitoring |

### Marketing & Content

| Command | What it does |
|---------|-------------|
| `/copywriting` | Landing pages, hero sections, CTAs |
| `/social-content` | LinkedIn posts, X threads |
| `/content-strategy` | Content calendars, blog topics |
| `/cold-email` | B2B outreach sequences |
| `/email-sequence` | Nurture drips, onboarding flows |
| `/competitor-alternatives` | Battle cards, positioning |
| `/page-cro` | Conversion rate optimization |
| `/pricing-strategy` | Pricing tiers, LATAM adaptation |

### n8n Automation

| Command | What it does |
|---------|-------------|
| `/n8n-code-javascript` | JS Code nodes, $input/$json syntax |
| `/n8n-code-python` | Python Code nodes |
| `/n8n-expression-syntax` | Expression validation |
| `/n8n-node-configuration` | Node config guidance |
| `/n8n-workflow-patterns` | Architecture patterns |
| `/n8n-validation-expert` | Error interpretation |
| `/n8n-mcp-tools-expert` | MCP tool usage |

## Agents

### Mentat — Orchestrator

Coordinates the entire agent ecosystem: breaks down work, delegates to specialists, synthesizes results, ensures delivery. System architect + project manager + technical lead.

### Specialists

| Agent | Domain |
|-------|--------|
| **Aurora** | Brand identity, design systems, UI specs, test ID contracts |
| **Pixel** | Next.js/React implementation, performance, accessibility |
| **Kokoro** | FastAPI, databases, auth, backend architecture |
| **Centinela** | QA strategy, Playwright E2E, regression testing |
| **Hermes** | Vercel deployments, CI/CD, edge functions, monitoring |
| **Flux** | n8n workflows, integrations, automation |
| **Oraculo** | Web research, competitive intel, tech evaluation |
| **Pregon** | Content strategy, social media, email campaigns |
| **Lumen** | Technical SEO, Core Web Vitals, schema markup |

## Skill Packs

Core skills are always available. Everything else installs via packs:

```bash
uv run hive list                        # see all packs and status
uv run hive install google devops       # install specific packs
uv run hive install --all               # install everything
uv run hive remove marketing            # uninstall a pack
```

| Pack | Skills | What's in it |
|------|--------|-------------|
| **core** | 10 | shape, capture, refine, dev, push_it, ship_it, reunion (always installed) |
| **google** | 5 | Gmail, Docs, Drive, Calendar, Workspace |
| **marketing** | 8 | Copywriting, cold email, CRO, pricing, content, social |
| **devops** | 4 | Vercel, Supabase, GitHub CLI, test debugging |
| **communication** | 2 | Slack, WhatsApp |
| **media** | 2 | Audio processing, video analysis |
| **tools** | 5 | Perplexity, adversarial review, budgets, reports, travel |
| **n8n** | 7 | n8n automation ([czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills), MIT) |
| **anthropic** | 3 | PDF tools, skill creator, frontend design ([Anthropic](https://github.com/anthropics/skills), Proprietary) |

## Multi-Provider Sync

Write skills once, use them everywhere:

| Provider | How it syncs |
|----------|-------------|
| Claude Code | `.claude-plugin/` — native plugin |
| Cursor | `.cursor/rules/` — auto-generated `.mdc` files |
| Gemini CLI | `.agent/` — symlink |
| Codex | `.codex/` — symlink |

## API Keys

All integrations are optional. Add keys as you need them. After setup, Hive tells you what's missing:

```
[hive] API keys configured: Gemini, OpenAI, Perplexity, Slack
    * Groq         https://console.groq.com          <- missing required
  Optional keys (not configured):
      DeepSeek     https://platform.deepseek.com
      OpenRouter   https://openrouter.ai/settings/keys
```

See [docs/ENV_VARIABLES.md](docs/ENV_VARIABLES.md) for every key mapped to its script, skill, and purpose.

## Security

Hive is designed to be operated by AI agents, so security guardrails are built in:

- **Write operations require `--confirm`** — without it, scripts show a dry-run preview and exit
- **Gmail sending is permanently blocked** — the handler only creates drafts
- **Google Drive sharing is domain-restricted** — external sharing requires explicit `--allow-external`
- **Pre-commit hook** scans for API keys, tokens, and private keys
- **Zero hardcoded credentials** — everything comes from `.env`

See [docs/SECURITY.md](docs/SECURITY.md) for the full model.

## Creating Skills

```yaml
---
name: my-skill
description: What it does. When to trigger it.
allowed-tools: Bash, Read
---

# Instructions for the AI...
```

Save as `skills/<name>/SKILL.md`. Use `/skill-creator` for guided creation.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- API keys for the integrations you want (all optional)

## Contributing

Issues and PRs welcome. Hive is maintained by [Skywalking](https://skywalking.dev).

## License

MIT
