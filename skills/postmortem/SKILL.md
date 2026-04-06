---
name: postmortem
description: "Blameless incident postmortem — gathers data from Slack, Linear, and user input to produce structured incident documentation. Three modes: extract from raw dumps, start from scratch, or refine existing drafts."
allowed-tools: Bash, Read, Write, Edit, mcp__linear__*, mcp__slack__*
---

# Postmortem

Produce blameless postmortem documents from incidents (technical, operational, administrative).

## Modes

| Mode | Trigger | Input |
|------|---------|-------|
| A — Dump | User pastes raw Slack/email/logs | Extract + structure |
| B — Scratch | No draft, provide sources step by step | Guided elicitation |
| C — Refine | User has a rough draft | Critique + complete |

Detect mode from first user message. If ambiguous, ask one question: "Do you have raw data to paste, or should I guide you through it?"

## Intake (Mode B — Guided)

Ask max 3-4 questions per batch via AskUserQuestion. Batches:

**Batch 1 — Scope**
1. What happened? (1-sentence description)
2. When did it start and end? (UTC preferred)
3. What was the user/customer impact?

**Batch 2 — Sources**
4. Linear ticket IDs involved? (e.g., SKY-241)
5. Slack thread URL(s)?
6. Any existing notes, logs, or docs?

**Batch 3 — Depth** (only if needed)
7. What was the root cause? (or "unknown" if still TBD)
8. What corrective actions are already in place?

Zero assumptions — if a data point is missing, mark it `[TBD]` not inferred.

## Data Gathering

### Linear

Fetch ticket via MCP:
```
linear_getIssueById(id: "SKY-XXX")
linear_searchIssues(query: "incident keyword")
```

Extract: title, description, comments, state history, linked issues.

### Slack

Fetch thread via skill:
```bash
uv run /Users/gpublica/workspace/skywalking/hive/scripts/slack_handler.py read "<thread_url>"
```

Extract: message timestamps (UTC), authors (roles not names), key decisions, alerts, fixes attempted.

Anonymise authors in timeline: use role (e.g., "on-call engineer") not username. Exception: named actions in corrective items.

### Mode A — Raw Dump

When user pastes raw text:
1. Extract all timestamps → normalize to UTC
2. Identify: detection, acknowledgement, first fix attempt, resolution
3. Flag gaps: "No detection-to-ack time found — adding [TBD]"
4. Ask only for fields that cannot be extracted

## Document Structure

```markdown
# Postmortem YYYY-MM-DD — <topic>

**Status:** Draft | Final
**Severity:** P0 | P1 | P2 | P3
**Duration:** Xh Ym
**Authors:** [initials or role]
**Last updated:** YYYY-MM-DD

---

## Incident Summary

<1 paragraph. Lead with impact, end with resolution. No jargon.>

## Impact

- **Users affected:** <count or segment>
- **Duration:** <start UTC> → <end UTC> (Xh Ym)
- **Services down:** <list>
- **Operational impact:** <revenue, SLA, support tickets, etc.>
- **Data loss:** None | [describe]

## Timeline

* **YYYY-MM-DD HH:MM UTC** — <event>
* **YYYY-MM-DD HH:MM UTC** — <event>

> Timestamps without confirmed source are marked [TBD].

## Root Cause

<1-2 sentences. "X caused Y because Z." If unknown: [TBD — investigation ongoing]>

### Contributing Factors

- <factor 1>
- <factor 2>

## Lessons Learned

- <actionable one-liner — "what do we do differently?">
- <actionable one-liner>

## Corrective Actions

### Immediate (done)
- **[Done]** <action> — <owner> — <date>

### Short-term (this sprint)
- <action> — <owner> — due <date>

### Long-term (backlog)
- <action> — <owner> — Linear: <ticket or TBD>

## References

- Linear: <url>
- Slack thread: <url>
- PR/commit: <url>
- Runbook: <url>
```

## Rules

**Blameless:**
- No personal blame. Systems fail, processes break.
- Name roles/decisions, not people, in narrative.
- Corrective actions target process/tooling, not individuals.

**Accuracy over completeness:**
- `[TBD]` beats guessing.
- Every data point: state its source inline if non-obvious.
- If two sources conflict, note both and flag: `[CONFLICT: Slack says X, Linear says Y]`.

**Actionable lessons:**
- Bad: "Communicate better"
- Good: "Add PagerDuty alert for DB connection pool >80%"
- Bad: "Be more careful with deployments"
- Good: "Add smoke test to Vercel preview before promoting to prod"

**Corrective actions:**
- Each must have an owner and a due date or Linear ticket.
- `[Done]` = verified closed, not just claimed.
- Pending items without a ticket → create one (ask user or create via `linear_createIssue`).

## Severity Guide

| Level | Criteria |
|-------|----------|
| P0 | Full outage, data loss risk, >100 users blocked |
| P1 | Partial outage or degraded perf, SLA at risk |
| P2 | Feature broken, workaround exists |
| P3 | Minor bug, cosmetic, single user |

## Stack Context (Skywalking)

- Infra: Vercel (edge/serverless), Supabase (Postgres + auth + edge functions)
- App: Next.js, Python services
- Queues/jobs: Vercel Cron, Supabase pg_cron
- Monitoring: Vercel logs, Supabase dashboard
- Auth: Supabase Auth (cookies — avoid `cookies()` in Lambda context, use `createClientFromRequest`)
- Agent debugging protocol: max 2 blind fix attempts, then escalate with evidence

## Output

1. Write draft to a file — ask user: "Where should I save this? (e.g., `docs/postmortems/YYYY-MM-DD-topic.md`)"
2. Default path if no answer: `docs/postmortems/<date>-<slug>.md` relative to current project root.
3. After saving, print the absolute path.
4. Offer: "Create Linear issue for pending corrective actions? (y/n)"

## Flow Summary

```
1. Detect mode (A/B/C)
2. Gather data (Slack + Linear + user input)
3. Summarize raw data → confirm with user
4. Write draft
5. Iterate (user edits inline or via chat)
6. Save file → print path
7. Offer Linear tickets for open corrective actions
```

## Example Invocations

```
/postmortem
→ Mode B: guided elicitation, 3-question batches

/postmortem SKY-241
→ Mode B: pre-load Linear ticket, ask for Slack thread + timeline

/postmortem [paste Slack dump]
→ Mode A: extract structure from dump, ask only for gaps

/postmortem refine docs/postmortems/2026-03-30-micelio.md
→ Mode C: load draft, identify missing fields, iterate
```

## Anti-patterns (never do)

- Do not infer timestamps from context — require source or mark [TBD].
- Do not write "the team should communicate better" as a lesson.
- Do not create a postmortem without at least: summary, impact duration, one confirmed root cause or explicit [TBD], and one corrective action.
- Do not skip the "Contributing Factors" section — single root cause framing misses systemic issues.
- Do not mark corrective actions [Done] without confirmation from user.
