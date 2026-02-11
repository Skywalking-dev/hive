---
name: backlog-manager
description: Manage issues across Linear workspace. Use when user wants to create, update, move, or query issues. Routes to appropriate command based on workflow state.
---

# Backlog Manager

Issue lifecycle management via Linear.

## Source of Truth

**Linear** is the single source of truth for all issues.
- Workspace: Skywalking
- MCP Server: `@tacticlaunch/mcp-linear`

**Local `docs/backlog/`**: DEPRECATED (historical reference only)

## Linear Structure

### Workspace & Projects

| Local Folder | Linear Project | Code |
|--------------|----------------|------|
| `docs/backlog/` | Skywalking (default) | SKY |
| `projects/miicel.io/` | miicel.io | MIIC |
| `projects/natu/` | Natu | NATU |
| `projects/{slug}/` | {Project Name} | {CODE} |

### Workflow States

**Parent issues:**
```
Backlog → Shaping → Refining → To Do → Prioritised → In Progress → In Review → Resolved → Testing → Ready to Deploy → Done → Done & Monitoring
```

**Sub-issues (agent tasks):**
```
To Do → In Progress → Done
```

## Command Routing

| State | Command | Skill | Action |
|-------|---------|-------|--------|
| Backlog | `/capture` | quick-capture | Quick idea → Linear |
| Shaping | `/shape` | issue-shaping | Full discovery → shaped issue |
| Refining | `/refine` | issue-refining | Agent sub-issues + specs |
| In Progress | `/dev` | dev | Delegate to agents |
| In Review | `/review` | pr-review | PR review + Linear sync |
| Ready to Deploy | `/ship_it` | - | CHANGELOG + merge |

## Issue Types

| Type | Label | Use Case |
|------|-------|----------|
| Bug | `bug` | Something broken |
| Feature | `feature` | New functionality |
| Improvement | `improvement` | Enhancement |

## Agent Sub-issues

Agents get Linear sub-issues with `[Agent]` prefix.

**Title format:** `[{AGENT}] {task description}`

The agent name in brackets is the **delegation signal** for Mentat (orchestrator). When Mentat sees `[Kokoro]` in title, it delegates that sub-issue to the Kokoro sub-agent.

**IMPORTANT:** Do NOT assign sub-issues to anyone. The title prefix is sufficient for orchestration.

| Agent | Focus | Example Title |
|-------|-------|---------------|
| Aurora | Design, brand, UI/UX | `[Aurora] Design WhatsApp button styles` |
| Kokoro | Backend, API, DB | `[Kokoro] Add whatsapp_number migration` |
| Pixel | Frontend, React | `[Pixel] WhatsAppButton component` |
| Flux | Automation, n8n | `[Flux] Notification workflow` |
| Hermes | Deploy, Vercel | `[Hermes] Configure env vars` |
| Sentinela | QA, E2E | `[Sentinela] E2E tests for WhatsApp` |
| Lumen | SEO | `[Lumen] Schema markup` |

## Decision Tree

### Which Command?

```
User has idea/bug/feature?
├── Quick thought, minimal context → /capture
├── Needs discovery/definition → /shape
└── Already shaped, needs breakdown → /refine

Issue refined with sub-issues?
└── → /dev (Mentat orchestrates)

User has PR ready?
└── → /review

User ready to deploy?
└── → /ship_it
```

### Which Project?

```
User mentions project?
├── miicel.io, miic → Project: miicel.io
├── natu → Project: Natu
├── SKY, skywalking, internal → Project: Skywalking (default)
└── Ask if unclear
```

## Work Orchestration

When `/dev` is called:

1. Mentat loads parent issue from Linear
2. Finds sub-issues with `[Agent]` prefix
3. Checks dependencies (order matters)
4. Delegates to each agent via Task tool
5. Monitors progress, resolves doubts
6. Validates acceptance criteria
7. Adds completion comment to Linear
8. Moves sub-issue to Done

See `dev` skill for full protocol.

## Linear MCP Tools

| Tool | Use |
|------|-----|
| `linear_createIssue` | Create parent or sub-issue |
| `linear_updateIssue` | Update state, priority, etc. |
| `linear_searchIssues` | Find duplicates, query |
| `linear_getIssueById` | Get issue details |
| `linear_createComment` | Add completion comments |

## Integration with Local Files

**Specs can still live locally** when needed:
```
projects/{project}/specs/
├── {ISSUE_ID}_DESIGN_SPECS.md
├── {ISSUE_ID}_API_SPECS.md
└── {ISSUE_ID}_NOTES.md
```

Link these from Linear issue description.

## Migration Notes

### Deprecated (do not use)
- `docs/backlog/.state.json` - counter frozen
- `*_TASKS.md` files - use Linear sub-issues
- `/bg_entry` command - use `/capture` or `/shape`
- `/delegate @*_TASKS.md` - use `/dev` for orchestration
- `/start_work` - replaced by `/dev`

### Active Commands
- `/capture` - quick idea → Linear backlog
- `/shape` - guided discovery → shaped issue
- `/refine` - technical breakdown → agent sub-issues
- `/dev` - Mentat orchestrates agent work
- `/review` - PR review + Linear sync
- `/ship_it` - deploy flow
- `/debate` - Forge review (reference Linear issue ID)

## Examples

### Quick Capture
```bash
/capture "Add dark mode toggle"
→ Creates in Linear: Skywalking project, Backlog state
```

### Shape Feature
```bash
/shape
→ Discovery questions
→ Creates shaped issue in Linear
```

### Refine Issue
```bash
/refine SKY-123
→ Identifies agents (Kokoro, Pixel)
→ Creates sub-issues with technical specs
```

### Start Work
```bash
/dev SKY-123
→ Mentat delegates to agents
→ Monitors progress
→ Validates acceptance criteria
```

### Review PR
```bash
/review #47
→ Syncs PR state with Linear
→ SKY-123 moves to "In Review"
```

## Anti-patterns

- Creating local `*_TASKS.md` files - use Linear sub-issues
- Using `/bg_entry` - use `/capture` or `/shape`
- Managing state in local folders - Linear is source of truth
- Duplicating info between Linear and local files
- Assigning sub-issues manually - use `[Agent]` prefix only

## Output Format

**On routing:**
```
Detected: {action_type}
Project: {Linear project}
Command: /{command}

Executing...
```

**On query:**
```
Linear Issues ({project}):

Backlog: {count}
- SKY-1: {title}

In Progress: {count}
- SKY-2: {title} [Kokoro, Pixel]

In Review: {count}
- SKY-3: {title} → PR #47
```
