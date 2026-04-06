---
name: investigate
description: "Systematic debugging — prevents jumping to fixes without root cause analysis. Use when debugging errors, analyzing failures, or investigating unexpected behavior. Forces evidence-based investigation before any code changes."
---

# Investigate

Evidence-first debugging. No code changes until root cause is confirmed.

**Core principle:** Investigate first, code later. A wrong fix costs more than the original bug.

---

## Protocol

### Step 0 — STOP

Before touching any code:

- [ ] Is this a **production outage**? → Apply Rollback-First Policy (see below), then return here.
- [ ] What exactly is broken? Define the failure in one sentence.
- [ ] What is the expected behavior vs. actual behavior?

---

### Step 1 — Check Recent Changes

What changed last?

```bash
git log --oneline -20
git log --oneline --since="48 hours ago"
git diff HEAD~1 HEAD --stat
```

Check deployments, env var changes, dependency upgrades, config changes. Most bugs live here.

---

### Step 2 — Reproduce

**Cannot reproduce = cannot fix.**

- Reproduce locally or in staging before writing any fix.
- Confirm it fails consistently (not flaky).
- Note the exact steps, input, and environment.

If you cannot reproduce: collect more data (logs, error traces, request IDs) before proceeding.

---

### Step 3 — Isolate with Git

Narrow down when the bug was introduced.

```bash
# Find the commit that broke it
git bisect start
git bisect bad HEAD
git bisect good <last-known-good-sha>
# git will checkout commits — test each, mark good/bad
git bisect good   # or: git bisect bad
git bisect reset  # when done
```

If bisect is too slow, check the diff of the most suspect commit:

```bash
git show <commit-sha>
git diff <before>..<after> -- path/to/file
```

---

### Step 4 — Investigate

Gather evidence. Do not form conclusions before this is complete.

**Key questions:**
- What do the logs say at the exact moment of failure?
- What changed in the environment (env vars, external APIs, DB state, schema)?
- Does it fail for all users or a subset? All environments or one?
- Is there a pattern (timing, specific input, load, auth state)?

**Techniques by layer:**

| Layer | Tools |
|-------|-------|
| Application logs | Structured logs, correlation IDs, error traces |
| Network | Request/response inspection, status codes, latency |
| Database | Query logs, slow query analysis, migration history |
| Auth | Token state, session validity, RLS policies (Supabase) |
| External services | Status pages, API response payloads, rate limits |
| Frontend | Browser console, network tab, component state |

---

### Step 5 — State Your Hypothesis

Before writing any fix:

> "I believe the bug is caused by **[X]** because **[evidence Y]**. The fix is **[Z]**."

If you cannot complete this sentence with concrete evidence, go back to Step 4.

One hypothesis at a time. Never test two variables simultaneously.

---

### Step 6 — Fix (One Variable)

- Change **one thing** per attempt.
- Never push multiple speculative fixes at once.
- Each fix attempt must be traceable to the hypothesis.

**Max 2 blind attempts.** If the second fix does not work → Step 8 (Escalate).

---

### Step 7 — Verify Root Cause

Before merging:

- [ ] Can you explain **why** the fix works, not just that it works?
- [ ] Does the original reproduction case pass?
- [ ] No regressions in adjacent behavior?
- [ ] Is the fix minimal (no unrelated changes)?

Proof = test output, log showing correct behavior, or clear explanation of runtime behavior.

---

### Step 8 — Escalate (if stuck)

After 2 failed attempts, stop and escalate to Gonza with:

```
What I tried:
1. [attempt 1] — outcome
2. [attempt 2] — outcome

What I observed:
- [logs, errors, behavior]

What I still don't understand:
- [the gap in knowledge]
```

Do not push a third speculative fix. The 71h micelio outage (2026-03-30) was caused by 13 speculative fixes without root cause analysis.

---

## Rollback-First Policy (Production)

When production breaks after a deploy:

1. **Revert immediately** — Vercel instant rollback or `git revert`. Restore service first.
2. **Confirm restored** — check `/api/health` returns 200 (or equivalent health signal).
3. **Then run this protocol** — reproduce locally, identify root cause, fix, test, redeploy.

Timeline target: service restored <15 min, root cause fix within 24h.

Never diagnose in production while the service is down.

---

## Decision Tree

After root cause is confirmed, classify the fix:

```
Is it a regression (worked before)?
├── Yes → Bug fix. Minimal change. Tests first.
└── No → Was it ever specified?
    ├── No → Potential feature. Shape a Linear issue.
    └── Yes → Implementation gap. Improvement.
```

---

## Red Flags — Stop and Discuss

Escalate immediately if:

- Fix requires changing 5+ unrelated files
- You're not sure what the code is supposed to do
- The bug disappears when you add logging (Heisenbug)
- Fix works locally but not in staging/production
- You've made 2 attempts and still can't reproduce consistently
- The fix touches auth, payments, or data migrations

---

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Fixing without reproducing | You might be fixing the wrong thing |
| Multiple changes per attempt | Can't tell which change worked |
| Deleting and re-creating to "reset state" | Masks the root cause |
| Blaming infra before ruling out code | Wrong escalation path |
| Copy-pasting fixes from similar bugs | Context differs, cause differs |
| Pushing to production to test | Turns a bug into an outage |

---

## Questions Checklist

**At start:**
- What changed in the last 24-48h?
- Does it fail in all environments or just one?
- Is there a correlation ID or request trace?

**During investigation:**
- What do the logs say at the exact failure point?
- Is the input/data valid at each layer?
- Is the failure deterministic or intermittent?

**Before fixing:**
- Can I state the root cause in one sentence?
- Is my fix the minimal change that addresses the cause?
- What's the rollback plan if this fix makes things worse?

---

## Integration with Hive Pipeline

```
Bug reported
  → /investigate       ← you are here
  → root cause found
  → /shape (if new issue needed)
  → fix branch
  → /push_it
  → /pr-review
  → /ship_it
```
