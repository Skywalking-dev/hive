---
name: issue-shaping
description: Shape bugs, features, and improvements into well-defined Linear issues. Use when user wants to create a new ticket, report a bug, request a feature, or propose an improvement. Provides guided discovery via AskUserQuestion and creates issues directly in Linear with proper structure and sub-issues for agents.
---

# Issue Shaping

Guided discovery for Linear issues.

## Linear Config

| Setting | Value |
|---------|-------|
| MCP Server | `@tacticlaunch/mcp-linear` |
| Team | Skywalking |
| Tools | `linear_createIssue`, `linear_searchIssues` |

## Workflow States

**Parent issues:**
```
Backlog → Shaping → Refining → To Do → Prioritised → In Progress → In Review → Resolved → Testing → Ready to Deploy → Done → Done & Monitoring
```

**Sub-issues:** `To Do → In Progress → Done`

## Issue Types

| Type | Template | Label |
|------|----------|-------|
| Bug | [templates/bug.md](templates/bug.md) | `bug` |
| Feature | [templates/feature.md](templates/feature.md) | `feature` |
| Improvement | [templates/improvement.md](templates/improvement.md) | `improvement` |

Load the appropriate template based on issue type for discovery questions and description format.

## Priority Mapping

| Severity | Linear Priority |
|----------|----------------|
| Critical | 1 (Urgent) |
| High | 2 |
| Medium | 3 |
| Low | 4 |

## Agents for Sub-issues

| Agent | Focus | Title Prefix |
|-------|-------|--------------|
| Aurora | Design, brand, UI/UX | `[Aurora]` |
| Kokoro | Backend, API, auth, DB | `[Kokoro]` |
| Pixel | Frontend, React/Next.js | `[Pixel]` |
| Flux | Automation, n8n | `[Flux]` |
| Hermes | Deploy, Vercel, monitoring | `[Hermes]` |
| Sentinela | QA, E2E, Playwright | `[Sentinela]` |
| Lumen | SEO, schema | `[Lumen]` |

## Sub-issue Creation

**IMPORTANT:** Do NOT assign sub-issues. Title prefix is the delegation signal.

```yaml
linear_createIssue:
  teamId: "Skywalking"
  title: "[{AGENT}] {task description}"
  parentId: "{parent_issue_id}"
  stateId: "{to_do_state_id}"
  # NO assigneeId - [Agent] prefix is sufficient
```

## Flow

1. Ask type → load template
2. Follow template's discovery questions (batches of 2-3)
3. **Validate scope:** If >5 acceptance criteria, warn and suggest split (see below)
4. Check duplicates: `linear_searchIssues`
5. Create parent issue using template
6. Optionally add agent sub-issues (or defer to `/refine`)
7. Confirm with Linear URL

## Scope Validation (Anti-Waterfall Check)

After collecting acceptance criteria, count them. If >5 AC:

**Warning to user:**
> "This spec has {N} acceptance criteria. Specs with >5 AC tend to produce imprecise agent output and higher costs. Consider splitting into 2+ focused issues."

**Then:**
1. Suggest logical grouping for split (e.g., by user flow, by component, by agent)
2. Ask user: "Split into smaller issues or continue as-is?"
3. If split → create multiple issues with subset of AC each
4. If continue → proceed but add label or note: `large-scope`

**Rationale:** Large specs = waterfall disguised as agile. Smaller specs produce better agent output, lower cost, faster feedback loops.

## Next Steps

After shaping:
- `/refine {issue-id}` → Create technical breakdown with agent sub-issues
- `/dev {issue-id}` → Mentat orchestrates agent work

## Example

```
User: I want to add a WhatsApp button to the storefront

/shape
→ Type: Feature
→ Discovery: title, user, problem, success criteria
→ Creates SKY-45 in Linear
→ Asks: "Create agent sub-issues now?"
  → Yes: Creates [Kokoro], [Pixel], [Sentinela] sub-issues
  → No: User can run /refine SKY-45 later
```
