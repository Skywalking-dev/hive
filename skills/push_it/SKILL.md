---
name: push_it
description: Commit, push, and open a PR in one step. Use when user says "push it", wants to commit + push + PR, or is done coding and ready for review.
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Push It

Commit all changes, push, and open a PR — one command.

## Steps

0. **Context**: Run `git status`, `git diff HEAD`, `git branch --show-current`, and `git log --oneline -5` to understand what changed

1. **Stage changes**: Add relevant files (avoid secrets, `.env`, large binaries)
2. **Branch**: If on `main`, create a feature branch first
3. **CHANGELOG**: If `CHANGELOG.md` exists, add entry under `[Unreleased]` (Common Changelog + SemVer)
4. **Commit**: Write a concise commit message based on the diff
5. **Push**: Push to origin with `-u` flag
6. **PR**: Create PR via `gh pr create`

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
