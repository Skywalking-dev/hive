---
name: ship_it
description: Full shipping pipeline — lefthook + local review + fix + simplify + push + CI review + merge + deploy + verify + close Linear + report. Use when user says "ship it" and wants code to reach production verified. Handles everything from uncommitted changes to live deployment, with review happening PRE-push so PRs nacen verdes.
allowed-tools: Bash(git:*), Bash(gh:*), Bash(vercel:*), Bash(curl:*), Skill(review-diff), Skill(simplify), Skill(push_it), Skill(pr-review), Skill(vercel), Agent
---

# Ship It

Baseline → Lefthook → Local Review → Fix → Simplify → Push → CI Review → Merge → Deploy → Verify → Close → Report. Not done until it's live, verified, and documented.

## Design principle

Review + simplify happen **LOCAL and PRE-push**. Claude is already in session with full context — fixing in-session is cheaper than round-tripping through CI. PRs nacen verdes: clean history, single CI run, no `fix: resolve review findings` commit pollution.

Second pair of eyes still runs post-push via `reusable-pr-review.yml` (DeepSeek, cold, unbiased, cheap) — but on a diff that's already clean.

## Session Tracking

At the START of the pipeline, capture baseline state for the final report:

```bash
# Files modified in this session (uncommitted + recent commits on branch)
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
BASE=${BASE:-main}
git diff --name-only origin/${BASE}...HEAD 2>/dev/null
git diff --cached --name-only
git diff --name-only

# Token usage — read from session context if available
```

Store: `BASELINE_FILES`, `BASELINE_TOKENS`.

## Pipeline

### Phase 0 — Baseline
Capture state above. If nothing to ship (clean tree + HEAD == origin/BASE), exit with "nothing to ship".

### Phase 1 — Lefthook (pre-commit)
Linters/formatters run automatically via `lefthook.yml` on every commit. If the repo has no lefthook config:
1. Warn user: "No lefthook config found — linters not enforced pre-commit. Recommended: copy from skywalking-template."
2. Proceed anyway (not a blocker).

**Never run linters via LLM tool calls.** That's what lefthook is for.

### Phase 2 — Local Review (Claude, pre-push)
1. Run `/review-diff` on all changes (committed + uncommitted vs `origin/${BASE}`)
2. Read findings. Decision:
   - **CLEAN** → Phase 4
   - **PROCEED** (only MEDIUM/LOW) → Phase 4, note findings in report
   - **BLOCK** (any CRITICAL/HIGH) → Phase 3

### Phase 3 — Fix Loop (local, pre-push)
While `/review-diff` returns BLOCK:
1. Apply fixes in-session (no commit yet — keep working tree dirty)
2. Re-run `/review-diff`
3. Repeat

**Max iterations: 3.** If still BLOCK after 3 rounds, STOP and ask user. Report:
- What you tried
- What review-diff still flags
- What you don't understand

### Phase 4 — Simplify
1. Run `/simplify` on all changed files (now correctness-clean)
2. Apply any fixes in-session
3. No commit yet

### Phase 5 — Commit + Push
1. Stage all changes: `git add -A` (or specific files — avoid secrets)
2. Single clean commit with descriptive message (NOT `fix: resolve review findings` — the fixes never hit git history)
3. Run `/push_it` for push + PR creation, OR if branch is already pushed, just `git push` and update existing PR
4. Capture `PR_NUMBER` and `PR_URL`

### Phase 6 — CI Review (DeepSeek / second opinion)
1. Wait for CI workflows to complete: `gh pr checks {PR_NUMBER}` — poll every 30s, max 5min
2. Read the review comment posted by `reusable-pr-review.yml` (DeepSeek)
3. Decision:
   - **All checks pass + review clean** → Phase 7
   - **Review comment flags NEW findings** (things `/review-diff` missed):
     - CRITICAL/HIGH → re-enter Phase 3 fix loop (this time fix, commit, push, re-wait)
     - MEDIUM/LOW → note in report, proceed
   - **CI check fails** → STOP, alert user with failure details

**Max extra fix rounds triggered by CI: 2.** If CI still unhappy after 2 extra rounds, stop and escalate.

### Phase 7 — Merge
1. Final CI check: `gh pr checks {PR_NUMBER}` — all green
2. Merge: `gh pr merge {PR_NUMBER} --squash --delete-branch`

### Phase 8 — Verify Deploy
1. Detect platform (check `vercel.json`, `.vercel/`, deploy scripts)
2. **Vercel projects:**
   - `vercel ls --json` → find latest deployment on production
   - Poll `vercel inspect` until READY (max 3min)
   - `curl -sI {PRODUCTION_URL}` → verify HTTP 200
   - If known health endpoint exists, fetch it
3. **Non-Vercel:** check deploy script/CI-CD, report status
4. **Tooling-only repos** (hive, skywalking-core, etc.) → skip, note "n/a — tooling repo"
5. **If browser tools available:** navigate to production URL, screenshot, verify key elements render

### Phase 9 — Close Linear
1. Detect Linear issue from branch name or PR body (pattern: `(SKY|MIIC|[A-Z]+)-\d+`)
2. Update the issue with shipping comment:
   ```
   Shipped via PR #{NUMBER}

   Files changed: {FILE_COUNT}
   - {FILE_LIST (max 20, then "and N more")}

   Local review: {LOCAL_ROUNDS} rounds, {LOCAL_FIXES} fixes
   CI review: {CI_VERDICT}, {CI_EXTRA_ROUNDS} extra rounds
   Deploy: {PLATFORM} → {PRODUCTION_URL}
   Session tokens: ~{INPUT_TOKENS} input, ~{OUTPUT_TOKENS} output
   ```
3. Transition issue state → **Done**
4. If no Linear issue detected, skip and note in report

### Phase 10 — Report
Present to user:

```
🚀 Shipped: PR #{NUMBER} → {BRANCH} merged to {BASE}

📋 Session Inventory:
   Files modified: {FILE_COUNT}
   {FILE_LIST with status: M=modified, A=added, D=deleted}

🔍 Quality:
   Lefthook: {✓ ran | ⚠ no config}
   Local review (Claude): {LOCAL_ROUNDS} rounds, {LOCAL_FIXES} fixes → {CLEAN|PROCEED}
   Simplify: {result — fixes applied or "clean"}
   CI review (DeepSeek): {verdict}, {CI_EXTRA_ROUNDS} extra rounds
   CI checks: ✓ all passed

🚢 Deployment:
   Platform: {PLATFORM}
   Deploy: ✓ {DEPLOYMENT_ID} READY
   Verify: ✓ {PRODUCTION_URL} responding 200

📊 Session Cost:
   Tokens: ~{INPUT_TOKENS} input / ~{OUTPUT_TOKENS} output

🎫 Linear: {ISSUE_ID} → Done
```

## Rules

- NEVER merge with failing CI
- NEVER skip the local review phase (`/review-diff`) — that's the whole point of the pre-push refactor
- NEVER run linters via LLM tool calls — lefthook handles it for free
- NEVER commit the fix loop as separate commits — fixes happen in-session, then one clean commit
- If local review finds CRITICAL security issues, STOP and alert user before fixing
- If deploy fails, DO NOT retry blindly — report the error
- If production verification fails (non-200, key elements missing), alert user immediately
- Always squash merge to keep history clean
- Delete branch after merge
- Always attempt to close the Linear issue — if no issue found, note it explicitly
- Token counts: use best available estimate from session context; if unavailable, note "N/A"

## Relation to Other Skills

```
lefthook          → pre-commit, runs linters/formatters/tests (no LLM)
/review-diff      → Claude local pre-push review (no GitHub, no Linear)
/simplify         → code quality/reuse audit on clean code
/push_it          → commit + push + open PR
/pr-review        → review an existing open PR + Linear sync (manual / post-merge)
/ship_it          → full pipeline orchestrator

reusable-pr-review.yml → CI workflow, DeepSeek/Claude second opinion, runs automatically on every PR
```

## Why this order

Old order (before 2026-04):
```
simplify → push → pr-review → fix loop (N commits) → merge
```
Problems: noisy history, N CI runs, review operates on mid-quality code, fix commits clutter PR.

New order:
```
lefthook → review-diff → fix (in-session) → simplify → push → CI review (second opinion) → merge
```
Benefits: 1 commit, 1 CI run, PR nace verde, DeepSeek catches what Claude missed without session bias.
