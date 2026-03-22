# Changelog

All notable changes to this project will be documented in this file.

Format based on [Common Changelog](https://common-changelog.org/), versions follow [SemVer](https://semver.org/).

## [Unreleased]

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
