---
name: dev
description: Orchestrate work on Linear issues by delegating sub-issues to specialist agents. Use when starting work on an issue with [Agent] sub-issues. Mentat monitors progress, resolves doubts, and validates acceptance criteria.
---

# Dev

Mentat orchestrates agent work on Linear issues.

## Linear Config

| Setting | Value |
|---------|-------|
| Team | Skywalking |
| Tools | `linear_getIssueById`, `linear_searchIssues`, `linear_updateIssue`, `linear_createComment` |

## Input

```bash
/dev SKY-123
/dev https://linear.app/skywalking/issue/SKY-123
```

## Orchestration Flow

```
1. Load parent issue from Linear
2. Get all sub-issues
3. Check dependencies (order matters)
4. For each sub-issue with [Agent] prefix:
   a. Delegate to agent via Task tool
   b. Agent implements
   c. Agent comments on completion
   d. Mentat validates acceptance criteria
5. When all sub-issues Done → parent moves forward
```

## Agent Detection

Parse `[Agent]` from sub-issue title:

| Title Pattern | Agent Type | Sub-agent |
|---------------|------------|-----------|
| `[Kokoro] ...` | backend | `kokoro-backend-specialist` |
| `[Pixel] ...` | frontend | `pixel-frontend-specialist` |
| `[Aurora] ...` | design | `aurora-product-designer` |
| `[Flux] ...` | automation | `flux-automation-specialist` |
| `[Hermes] ...` | deploy | `hermes-deployment-specialist` |
| `[Centinela] ...` | testing | `centinela-test-automation-expert` |
| `[Lumen] ...` | seo | `lumen` |

## Dependency Order

Execute in dependency order:

```
1. Aurora     → Design specs first (if UI work)
2. Kokoro     → Backend/API before frontend
3. Pixel      → Frontend after API ready
4. Flux       → Automation/integrations
5. Centinela  → E2E tests after frontend
6. Hermes     → Deploy last
```

Detect blockers:
- Pixel waits for Kokoro (API) and Aurora (design)
- Centinela waits for Pixel (test IDs)
- Hermes waits for all implementation

## Delegation Protocol

### 1. Prepare Context

For each sub-issue, extract:
- Title (without `[Agent]` prefix)
- Description (scope, specs, files)
- Acceptance criteria
- Dependencies (other sub-issues)

### 2. Delegate via Task Tool

```
Task tool call:
- subagent_type: {agent-specialist}
- prompt: |
    ## Linear Issue: {issue-id}
    ## Task: {title}

    {description}

    ## Acceptance Criteria
    {criteria}

    ## Instructions
    1. Implement the task
    2. Follow team conventions
    3. When done, I'll add a completion comment to Linear

    ## Dependencies
    {dependency status}
```

### 3. Monitor Progress

Mentat responsibilities during session:
- Answer agent questions (agents ask via returned message)
- Provide missing context
- Resolve blockers
- Validate implementation matches criteria

### 4. Completion Comment

When agent finishes, Mentat adds Linear comment:

```markdown
linear_createComment:
  issueId: "{sub-issue-id}"
  body: |
    ## Implementation Complete

    **Agent:** {agent-name}
    **Status:** Done

    ### Summary
    {brief summary of what was done}

    ### Files Changed
    - `path/to/file1.ts`
    - `path/to/file2.tsx`

    ### Acceptance Criteria
    - [x] {criterion 1}
    - [x] {criterion 2}
```

### 5. Update Sub-issue State

```yaml
linear_updateIssue:
  id: "{sub-issue-id}"
  stateId: "{done-state-id}"
```

## Git Integration

For each agent delegation:

1. **Branch naming:** `feature/{parent-id}/{agent}-{YYYYMMDD}`
   - Example: `feature/SKY-45/kokoro-20250118`

2. **Worktree (parallel work):**
   ```bash
   git worktree add ../{parent-id}-{agent} feature/{parent-id}/{agent}-{YYYYMMDD}
   ```

3. **Commits:** Agent commits during implementation

4. **PR:** Created per agent or consolidated

## Session Flow Example

```
User: /dev SKY-45

Mentat:
├── Loads SKY-45 from Linear
├── Finds 3 sub-issues:
│   ├── SKY-46: [Kokoro] Add migration
│   ├── SKY-47: [Pixel] WhatsAppButton component
│   └── SKY-48: [Centinela] E2E tests
│
├── Checks dependencies:
│   ├── Kokoro: no deps → ready
│   ├── Pixel: needs Kokoro → blocked
│   └── Centinela: needs Pixel → blocked
│
├── Delegates SKY-46 to Kokoro agent
│   ├── Agent implements migration + API
│   ├── Agent returns: "Done. Added migration, validation endpoint."
│   └── Mentat: Comments on SKY-46, marks Done
│
├── Pixel unblocked → Delegates SKY-47
│   ├── Agent implements component
│   ├── Agent asks: "What template should button appear in?"
│   ├── Mentat: "All 4 templates. See DESIGN_SPECS."
│   ├── Agent completes
│   └── Mentat: Comments on SKY-47, marks Done
│
├── Centinela unblocked → Delegates SKY-48
│   └── ... (similar flow)
│
└── All Done → Updates SKY-45 state
```

## Error Handling

### Agent Blocked

```
Agent: "Can't proceed - API spec missing."
Mentat:
  1. Check if Kokoro sub-issue exists
  2. If not, create one via /refine
  3. If yes, delegate Kokoro first
```

### Acceptance Criteria Not Met — Rewind > Fix Rule

```
Mentat validates criteria after agent completion.
If not met:
  1. STOP — do NOT patch the bad output
  2. Identify what's wrong with the spec/prompt
  3. Improve the spec (sub-issue description, context, criteria)
  4. Re-delegate from scratch with improved spec
  5. Only mark Done when all criteria pass

NEVER patch agent output. Always rewind to better spec.
Rationale: patching compounds tech debt. Better specs = better output.
```

### Agent Question

```
Agent returns question in response.
Mentat:
  1. Answer directly if known
  2. Check specs/context files
  3. Ask user if unclear
  4. Re-delegate with answer
```

## State Transitions

| Event | Parent State | Sub-issue State |
|-------|--------------|-----------------|
| Start work | In Progress | In Progress (current) |
| Agent done | In Progress | Done |
| All agents done | In Review | All Done |
| PR merged | Testing | - |

## Output Format

**On start:**
```
Starting work on SKY-45: [Feature] WhatsApp button

Sub-issues found:
├── SKY-46: [Kokoro] Add migration → Ready
├── SKY-47: [Pixel] WhatsAppButton → Blocked (Kokoro)
└── SKY-48: [Centinela] E2E tests → Blocked (Pixel)

Delegating SKY-46 to Kokoro...
```

**On completion:**
```
SKY-46 [Kokoro] Complete ✓
├── Migration applied
├── Validation endpoint added
└── Acceptance criteria: 3/3 met

Unblocked: SKY-47 [Pixel]
Delegating...
```

**On finish:**
```
SKY-45 Complete ✓
├── All 3 sub-issues Done
├── PRs: #47, #48, #49
└── Ready for review

Moving SKY-45 to "In Review"
```
