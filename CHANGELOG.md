# Changelog

All notable changes to this project will be documented in this file.

Format based on [Common Changelog](https://common-changelog.org/), versions follow [SemVer](https://semver.org/).

## [Unreleased]

### Added
- `investigate` skill: systematic debugging — evidence-first, rollback-first, max 2 attempts then escalate
- `postmortem` skill: blameless incident docs — 3 modes (dump/scratch/refine), Slack+Linear integration, P0-P3 severity
- `slack-api` skill: added mrkdwn formatting guide (bold, italic, links, no-tables) to prevent silent Slack formatting errors
- `scripts/groq_handler.sh`: Groq API handler (ask, models) — free tier, 3000+ tok/s inference
- `scripts/deepseek_handler.sh`: DeepSeek API handler (ask, models) — cheapest frontier ($0.30/$0.50 MTok), R1 reasoning support
- `scripts/openrouter_handler.sh`: OpenRouter API handler (ask, models, free) — universal fallback, 29+ free models, provider routing
- `scripts/review_pr.sh`: PR review via LLM handler — classifies PR complexity, routes to DeepSeek (normal) or auto-approves (simple)
- `hive setup`: now merges hive/CLAUDE.md handler docs into workspace CLAUDE.md (idempotent, marker-based)
- `hive setup`: post-setup API key verification with signup links for missing keys
- `ship_it` skill: simplify phase, Linear close, session inventory, token tracking in final report
- `blender` skill: 3D modeling via Blender MCP
- `technical-drawing` skill: ISO-standard SVG construction drawings
- `wrap` skill: end-of-session summary and conversation rename
- `scripts/gemini_handler.sh`: Gemini API handler (ask, search, embed)
- `scripts/openai_handler.sh`: OpenAI API handler (ask, responses, embeddings)
- `scripts/telegram_sketch_bot.py`: Telegram sketch-to-render bot via Gemini Pro
- `.gitignore`: cache/ directory excluded
- Agent frontmatter: `memory: project` on all 9 agents (persistent knowledge across sessions)
- Agent frontmatter: `isolation: worktree` on Pixel, Centinela, Kokoro (parallel work without conflicts)
- Agent frontmatter: `initialPrompt` on 6 agents (auto-load key docs on start)
- Skill frontmatter: `paths:` on 7 n8n skills + supabase (context-aware activation)
- Skill frontmatter: `context: fork` on process_video + perplexity (isolated subagent execution)
- Ecosystem monitor via GitHub Actions (`scripts/monitor.py` + `.github/workflows/monitor.yml`)
- Auto-maintain: Claude Code Action analyzes releases and opens PRs when Hive needs updates
- Slack #hive channel for ecosystem notifications (bot token + chat.postMessage)
- `generate_image` skill: Pro/Banana2 models, sketch-to-render workflow, decision tree, anti-patterns
- Linear state transitions in `dev`, `refine`, `shape` skills

### Changed
- `claude-review.yml`: PR review routing — classify (simple/normal/critical), DeepSeek for normal, Claude Sonnet for critical only
- `monitor.yml`: DeepSeek pre-filter before Claude maintain — skips Sonnet when releases don't affect Hive
- `CLAUDE.md`: architecture tree updated (Vercel cron → GitHub Actions)
- `agents/oraculo-research-specialist.md`: 3-tier search tools (Gemini → Perplexity → OpenAI)
- Root CLAUDE.md: added /batch and /simplify to commands, agent capabilities to delegation matrix
- Renamed miicel.io → micelio across skills and agents
- Monitor migrated from Vercel cron to GitHub Actions (Hobby plan limitation)
- Monitor Slack notifications use bot token instead of webhook

### Removed
- `scripts/invoke_forge.sh` — replaced by Codex native integration
- `scripts/invoke_mycelium.sh` — replaced by `gemini_handler.sh`
- `api/cron/monitor.py` — replaced by `scripts/monitor.py`
- `vercel.json` — no longer needed (cron moved to GitHub Actions)
- Vercel project for hive

### Fixed
- Anthropic pack: repo URL updated from `anthropics/claude-code-skills` to `anthropics/skills` (#5)
- Anthropic pack: skill name `pdf-anthropic` → `pdf` to match new repo structure

## [0.2.0] - 2026-03-19

### Added
- Skill pack system: core, google, marketing, devops, communication, media, tools, n8n, anthropic
- Unified `hive` CLI (`uv run hive install/remove/list/setup`)
- 8 marketing skills: copywriting, cold-email, content-strategy, social-content, page-cro, competitor-alternatives, pricing-strategy, email-sequence
- Workflow skills: ship_it, push_it, shape, capture, refine, reunion
- Security guardrails: `--confirm` flag on all write operations (trading, messaging, sharing)
- Gmail send permanently blocked (drafts only)
- Google Drive domain allowlist for sharing
- Pre-commit hook for secret detection
- `docs/ENV_VARIABLES.md` — full key-to-script-to-skill map
- `docs/SECURITY.md` — security model documentation
- LICENSE (MIT), CONTRIBUTING.md
- `.claude-plugin/plugin.json` — Claude Code plugin manifest

### Changed
- Moved skills/, agents/, scripts/ to repo root (plugin format)
- `install_skills.py` + `release.py` merged into `hive.py`
- Skills organized: core in `skills/`, packs in `available/`
- Third-party skills (n8n, Anthropic) install via `uv run hive install`
- Scripts use `load_dotenv()` from cwd (plugin-compatible)
- All docs use `uv run` instead of `python`

### Removed
- Old commands directory (replaced by skills)
- Hardcoded paths in invoke_forge.py, invoke_mycelium.py
- Crypto files from git history (personal, never public)
- Proprietary Anthropic skills from repo (install via pack)

## [0.1.0] - 2026-02-15

### Added
- Initial release: skills, agents, scripts
- 9 specialist agents: Aurora, Pixel, Kokoro, Sentinela, Hermes, Flux, Oraculo, Pregon, Lumen
- Google API handlers: Gmail, Docs, Drive, Calendar
- Communication handlers: Slack, WhatsApp
- Search: Perplexity, YouTube transcripts
- Automation: n8n skills (7)
- Multi-provider sync via release.py (Cursor, Gemini CLI, Codex)
- Pre-commit secret detection hook
