---
name: ship_it
description: Full shipping pipeline — simplify, commit, push, PR, review, fix, merge, deploy, verify, close Linear, report. Use when user says "ship it" and wants code to reach production verified. Handles everything from uncommitted changes to live deployment.
allowed-tools: Bash(git:*), Bash(gh:*), Bash(vercel:*), Bash(curl:*), Skill(pr-review), Skill(push_it), Skill(simplify), Skill(vercel), Agent
---

# Ship It

Simplify → Push → Review → Fix → Merge → Deploy → Verify → Close → Report. Not done until it's live, verified, and documented.

## Session Tracking

At the START of the pipeline, capture baseline state for the final report:

```bash
# Files modified in this session (uncommitted + recent commits on branch)
git diff --name-only HEAD~$(git rev-list --count origin/main..HEAD) 2>/dev/null || git diff --name-only
git diff --cached --name-only
git diff --name-only

# Token usage — read from session context if available
```

Store these for Phase 7.

## Pipeline

### Phase 0 — Simplify

1. Run `/simplify` on all changed files
2. If simplify produces fixes, commit them: `refactor: simplify per review`
3. Push if needed

### Phase 1 — Push (if needed)

If there are uncommitted changes or no open PR:

1. Run `/push_it` — stages, commits, pushes, opens PR
2. Continue to Phase 2 with the new PR

If a PR already exists and is up to date, skip to Phase 2.

### Phase 2 — Self-Review

1. Run `/pr-review` on the current PR
2. Read all findings and PR comments

### Phase 3 — Fix Loop

While there are CRITICAL or HIGH findings:

1. Fix each finding in the codebase
2. Commit fixes: `fix: resolve PR review findings`
3. Push
4. Re-run `/pr-review`
5. Repeat until APPROVE

**Max iterations:** 3. If still blocked after 3 rounds, stop and ask user.

### Phase 4 — Merge

1. Verify CI checks pass: `gh pr checks {PR_NUMBER}`
2. Wait for checks if pending (poll every 30s, max 5min)
3. Merge: `gh pr merge {PR_NUMBER} --squash --delete-branch`

### Phase 5 — Verify Deploy

1. Detect platform from project (check `vercel.json`, `.vercel/`, etc.)
2. **Vercel projects:**
   - `vercel ls --json` → find latest deployment
   - Wait for deployment to be READY (poll `vercel inspect`, max 3min)
   - `curl -sI {PRODUCTION_URL}` → verify HTTP 200
   - If the project has a known health endpoint or page, fetch it
3. **Non-Vercel:** Check if there's a deploy script or CI/CD, report status
4. **If browser tools available:** Navigate to production URL, take screenshot, verify key elements render

### Phase 6 — Close Linear

1. Detect Linear issue from branch name or PR body (pattern: `SKY-\d+`, `[A-Z]+-\d+`)
2. Update the issue with a shipping comment:
   ```
   Shipped via PR #{NUMBER}

   Files changed: {FILE_COUNT}
   - {FILE_LIST (max 20, then "and N more")}

   Review: {N} rounds, {FIXES} fixes
   Deploy: {PLATFORM} → {PRODUCTION_URL}
   Session tokens: ~{INPUT_TOKENS} input, ~{OUTPUT_TOKENS} output
   ```
3. Transition issue state → **Done**
4. If no Linear issue detected, skip and note in report

### Phase 7 — Report

Present to user:

```
🚀 Shipped: PR #{NUMBER} → {BRANCH} merged to {BASE}

📋 Session Inventory:
   Files modified: {FILE_COUNT}
   {FILE_LIST with status indicators: M=modified, A=added, D=deleted}

🔍 Quality:
   Simplify: {SIMPLIFY_RESULT — fixes applied or "clean"}
   Review: {N} rounds, {TOTAL_FIXES} fixes applied
   CI: ✓ all checks passed

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
- NEVER skip the simplify phase — always clean code before shipping
- NEVER skip the review phase — always self-review after simplify
- If review finds CRITICAL security issues, STOP and alert user before fixing
- If deploy fails, DO NOT retry blindly — report the error
- If production verification fails (non-200, key elements missing), alert user immediately
- Always squash merge to keep history clean
- Delete branch after merge
- Always attempt to close the Linear issue — if no issue found, note it explicitly
- Token counts: use best available estimate from session context; if unavailable, note "N/A"

## Relation to Other Skills

```
/simplify → code quality review (3 agents audit changed code)
/push_it  → commit + push + open PR (code done, ready for review)
/ship_it  → simplify + review + fix + merge + deploy + verify + close + report
/pr-review → just the review step (standalone)
```
