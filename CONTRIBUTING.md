# Contributing to Hive

Thanks for your interest in contributing. Hive is maintained by [Skywalking](https://skywalking.dev), a dev studio in Patagonia, Argentina. We review issues and PRs within 1-2 weeks.

## Ways to Contribute

- **Report bugs** — open an issue with steps to reproduce
- **Suggest skills** — describe the integration you'd like to see
- **Improve docs** — fix typos, clarify instructions, add examples
- **Submit skills** — add new skills or improve existing ones
- **Fix issues** — check open issues for things you can help with

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md`
2. Follow the skill format:

```yaml
---
name: skill-name
description: What it does. When to trigger it.
allowed-tools: Bash, Read
---

# Instructions for the AI...
```

3. If your skill needs a Python handler, add it to `scripts/`
4. Update `.env.example` if new API keys are required
5. Open a PR

## Adding a Script

Scripts in `scripts/` are Python 3.11+ handlers for external APIs.

Rules:
- Load credentials via `load_dotenv()` from `.env` — never hardcode secrets
- Write operations must require `--confirm` flag (see [SECURITY.md](docs/SECURITY.md))
- Return JSON: `{"success": true/false, "data": ...}` or `{"success": false, "error": "..."}`
- Exit code 0 = success, 1 = error, 2 = dry run (needs confirmation)

## Pull Requests

- Keep PRs focused — one skill or one fix per PR
- Include a brief description of what changed and why
- Make sure `.env.example` is updated if you add new env vars
- Don't commit `.env`, credentials, or API keys

## Code Style

- Python: no strict linter enforced, just be consistent with existing code
- Skills: clear, concise Markdown — the AI reads this, not just humans
- Commit messages: `feat:`, `fix:`, `docs:`, `chore:` prefixes

## Security

If you find a security vulnerability, please email security@skywalking.dev instead of opening a public issue.

## Questions?

Open a GitHub Discussion or reach out at [skywalking.dev](https://skywalking.dev).
