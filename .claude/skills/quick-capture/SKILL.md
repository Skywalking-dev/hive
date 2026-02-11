---
name: quick-capture
description: Capture ideas quickly into Linear backlog with minimal friction. Use when user has a quick idea, bug report, or thought that needs to be captured without full discovery process. Creates issue in Backlog state with title and brief context.
---

# Quick Capture

Fast idea capture → Linear Backlog.

## Linear Config

| Setting | Value |
|---------|-------|
| Team | Skywalking |
| State | Backlog |
| Tools | `linear_createIssue` |

## Input Format

Minimal required:
- **Title** (required): What is this about?
- **Context** (optional): 1-2 sentences of why/what

## Flow

1. Parse input for title + context
2. If missing title, ask with AskUserQuestion
3. Create in Linear with state "Backlog"
4. Return Linear URL

## Issue Creation

```yaml
linear_createIssue:
  teamId: "Skywalking"
  title: "{title}"
  description: |
    ## Quick Capture
    {context if provided}

    ---
    *Captured via /capture - needs shaping*
  stateId: "{backlog_state_id}"
  priority: 4  # Low - to be triaged
```

## Next Steps

After capture, issue follows workflow:

1. `/shape {issue-id}` → Full discovery, move to Shaping
2. `/refine {issue-id}` → Technical breakdown, agent sub-issues
3. `/dev {issue-id}` → Mentat orchestrates implementation

## Examples

```bash
/capture "Add dark mode toggle"
→ SKY-50 created in Backlog

/capture "API rate limiting broken on prod"
→ SKY-51 created in Backlog (high priority if "broken" detected)

/capture "Consider migrating to Bun"
→ SKY-52 created in Backlog
```

## Decision: Capture vs Shape

| Signal | Command |
|--------|---------|
| Quick thought, minimal context | `/capture` |
| Ready for discovery questions | `/shape` |
| Already defined, needs breakdown | `/refine` |
