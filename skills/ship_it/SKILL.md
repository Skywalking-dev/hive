---
name: ship_it
description: Commit, push, and open a PR in one step. Use when user says "ship it", wants to commit + push + PR, or is done with a feature and ready to merge.
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Ship It

Commit all changes, push, and open a PR — one command.

## Context

- Current git status: !`git status`
- Current git diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`

## Steps

1. **Stage changes**: Add relevant files (avoid secrets, `.env`, large binaries)
2. **Branch**: If on `main`, create a feature branch first
3. **Commit**: Write a concise commit message based on the diff
4. **Push**: Push to origin with `-u` flag
5. **PR**: Create PR via `gh pr create`

## Commit Message Format

```
<type>: <what changed>

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`

## PR Format

```bash
gh pr create --title "<short title>" --body "$(cat <<'EOF'
## Summary
- <bullet points>

## Test plan
- [ ] <how to verify>
EOF
)"
```

## Rules

- NEVER commit `.env`, credentials, or secrets
- NEVER force push to `main`
- ALWAYS create a new branch if on `main`
- Keep commit messages short and focused on "why"
- One commit per ship (squash if multiple changes)
- Execute ALL steps in a single response — do not pause between them
