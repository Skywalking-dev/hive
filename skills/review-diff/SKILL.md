---
name: review-diff
description: Local pre-push code review by Claude. Analyzes git diff vs base branch and returns structured findings (CRITICAL/HIGH/MEDIUM/LOW) without touching GitHub or Linear. Use before pushing to catch issues in-session, fix them, and ship a clean PR. Different from /pr-review which is the post-push CI/Linear sync layer.
allowed-tools: Bash(git:*), Read, Grep, Glob
---

# Review Diff (Local)

Pre-push self-review. Runs in the active Claude session against uncommitted + committed-but-unpushed changes. No GitHub. No Linear. Pure analysis.

## When to use

- Inside `/ship_it` Phase 2, before push
- Standalone: `review the changes I have so far`
- After a fix loop, to confirm clean state before continuing

## NOT for

- Reviewing an already-open PR → use `/pr-review`
- Reviewing someone else's branch → use `/pr-review`
- Posting GitHub comments → use `/pr-review`

## Input

```
/review-diff                    # default: HEAD vs origin/main + working tree
/review-diff origin/develop     # explicit base branch
/review-diff --staged           # staged changes only
/review-diff --range A..B       # arbitrary range
```

## Execution Flow

### Step 1 — Resolve diff range

Default: everything not yet on remote base branch.

```bash
# Detect base branch
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
BASE=${BASE:-main}

# Range = base..HEAD + working tree
git diff origin/${BASE}...HEAD       # committed not yet pushed
git diff                             # unstaged
git diff --cached                    # staged
```

If working tree is clean and HEAD == origin/BASE: nothing to review, exit early.

### Step 2 — Inventory

```bash
# File list (all states)
git diff --name-status origin/${BASE}...HEAD
git diff --name-status
git diff --cached --name-status
```

Store: `FILES_CHANGED`, `ADDITIONS`, `DELETIONS`, `LANGUAGES_TOUCHED`.

### Step 3 — Read full diff

```bash
git diff origin/${BASE}...HEAD
git diff HEAD                         # working tree on top
```

For diffs >1500 lines, prioritize:
1. New files (full read)
2. Files in security-sensitive paths (`auth/`, `api/`, `middleware/`, `*_handler*`, `lib/db*`)
3. Files with most changes
Skip: lockfiles, generated files, snapshots.

### Step 4 — Analysis

Apply this checklist. Assign severity per finding.

#### Severity

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Security vuln, data loss, crash, exposed secret | Must fix before push |
| HIGH | Bug, missing validation, broken contract, logic error | Must fix before push |
| MEDIUM | Code smell, missing test, minor issue | Should fix |
| LOW | Style, suggestion, nit | Optional |

#### Security (CRITICAL/HIGH)
- Hardcoded secrets, API keys, tokens
- SQL injection (raw SQL with interpolation)
- XSS (`dangerouslySetInnerHTML`, unescaped user input)
- SSRF (user-controlled URLs in server fetches)
- Supabase RLS bypass (`service_role` in client code)
- Sensitive data in logs/error messages
- Missing auth on new API routes

#### Correctness (HIGH/MEDIUM)
- `console.log` / `print` / debug statements left in
- `any` types without justification
- Hardcoded values that should be env vars
- Missing error handling on async paths
- Unhandled promise rejections
- Edge cases ignored (null, empty, boundary)
- Off-by-one, race conditions

#### Architecture (MEDIUM)
- Duplicated logic — check existing utils/hooks first
- Components >200 lines without justification
- Pattern violations vs project conventions
- Circular dependencies
- Missing separation of concerns

#### Tests & Quality (MEDIUM/LOW)
- Missing `data-testid` per `docs/TEST_ID_CONTRACT.md`
- New logic without unit tests
- CHANGELOG not updated for significant changes
- Commented-out code
- TODOs without Linear ID

### Step 5 — Decision

| Findings | Decision |
|---|---|
| Any CRITICAL | BLOCK — must fix before push |
| Any HIGH | BLOCK — must fix before push |
| Only MEDIUM/LOW | PROCEED — fix recommended |
| Nothing | CLEAN — push when ready |

### Step 6 — Output

Structured report (terse, actionable):

```
review-diff: {N} files, +{ADD}/-{DEL}

CRITICAL ({n})
- file.ts:42 — {finding} → {fix suggestion}

HIGH ({n})
- file.ts:78 — {finding} → {fix suggestion}

MEDIUM ({n})
- file.ts:15 — {finding}

LOW ({n})
- file.ts:9 — {finding}

Decision: {BLOCK | PROCEED | CLEAN}
{1-line summary}
```

If BLOCK: list the exact fixes to apply. Do not push.
If PROCEED/CLEAN: ready for `/push_it` or next pipeline phase.

## Rules

- NEVER post to GitHub. NEVER touch Linear. This is local-only.
- NEVER auto-fix. Report findings, let the caller (or `/ship_it` fix loop) apply.
- NEVER skip files — if diff is too large, sample and warn, do not silently truncate.
- Always reference `file:line`.
- Be strict. If you would flag it in a real code review, flag it here.
- Bias to action: every finding gets a concrete suggested fix.

## Relation to other skills

```
review-diff   → local, Claude in session, pre-push, no side effects
pr-review     → post-push, GitHub PR + Linear sync, can run from CI
ship_it       → orchestrator: lefthook → review-diff → fix → simplify → push → CI runs DeepSeek → merge → deploy
```

## Why this exists

Pushing dirty code to trigger CI review wastes CI cycles, pollutes PR history with `fix: resolve review findings` commits, and slows feedback. Catching issues in-session (where Claude already has full context) is faster, cleaner, and produces PRs that nacen verdes.

Second pair of eyes still happens in CI via `claude-review.yml` reusable workflow — but with DeepSeek (cheap, cold, unbiased) on a clean diff.
