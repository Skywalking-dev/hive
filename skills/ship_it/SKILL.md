---
name: ship_it
description: Full shipping pipeline — commit, push, PR, review, fix, merge, deploy, verify. Use when user says "ship it" and wants code to reach production verified. Handles everything from uncommitted changes to live deployment.
allowed-tools: Bash(git:*), Bash(gh:*), Bash(vercel:*), Bash(curl:*), Skill(pr-review), Skill(push_it), Skill(vercel), Agent
---

# Ship It

Commit → Push → PR → Review → Fix → Merge → Deploy → Verify. Not done until it's live and working.

## Pipeline

### Phase 0 — Push (if needed)

If there are uncommitted changes or no open PR:

1. Run `/push_it` — stages, commits, pushes, opens PR
2. Continue to Phase 1 with the new PR

If a PR already exists and is up to date, skip to Phase 1.

### Phase 1 — Self-Review

1. Run `/pr-review` on the current PR
2. Read all findings and PR comments

### Phase 2 — Fix Loop

While there are CRITICAL or HIGH findings:

1. Fix each finding in the codebase
2. Commit fixes: `fix: resolve PR review findings`
3. Push
4. Re-run `/pr-review`
5. Repeat until APPROVE

**Max iterations:** 3. If still blocked after 3 rounds, stop and ask user.

### Phase 3 — Merge

1. Verify CI checks pass: `gh pr checks {PR_NUMBER}`
2. Wait for checks if pending (poll every 30s, max 5min)
3. Merge: `gh pr merge {PR_NUMBER} --squash --delete-branch`

### Phase 4 — Verify Deploy

1. Detect platform from project (check `vercel.json`, `.vercel/`, etc.)
2. **Vercel projects:**
   - `vercel ls --json` → find latest deployment
   - Wait for deployment to be READY (poll `vercel inspect`, max 3min)
   - `curl -sI {PRODUCTION_URL}` → verify HTTP 200
   - If the project has a known health endpoint or page, fetch it
3. **Non-Vercel:** Check if there's a deploy script or CI/CD, report status
4. **If browser tools available:** Navigate to production URL, take screenshot, verify key elements render

### Phase 5 — Report

```
🚀 Shipped: PR #{NUMBER} → {BRANCH} merged to {BASE}

Review: {N} rounds, {TOTAL_FIXES} fixes applied
CI: ✓ all checks passed
Deploy: ✓ {PLATFORM} deployment {ID} READY
Verify: ✓ {PRODUCTION_URL} responding 200

Linear: {ISSUE_ID} → Testing
```

## Rules

- NEVER merge with failing CI
- NEVER skip the review phase — always self-review first
- If review finds CRITICAL security issues, STOP and alert user before fixing
- If deploy fails, DO NOT retry blindly — report the error
- If production verification fails (non-200, key elements missing), alert user immediately
- Always squash merge to keep history clean
- Delete branch after merge

## Relation to Other Skills

```
/push_it  → commit + push + open PR (code done, ready for review)
/ship_it  → review + fix + merge + deploy + verify (ready for production)
/pr-review → just the review step (standalone)
```
