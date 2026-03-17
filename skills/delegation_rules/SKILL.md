---
name: delegation-rules
description: Guide Mentat's delegation decisions to specialist agents. Use when routing tasks to sub-agents (Kokoro, Pixel, Aurora, Flux, Hermes, Sentinela, Lumen) based on Linear sub-issues with [Agent] title prefix.
---

# Delegation Rules

Route tasks to specialist agents via Linear sub-issues.

## Delegation Signal

**Title format:** `[{AGENT}] {task description}`

The agent name in brackets is the **delegation signal**. When Mentat sees a sub-issue with `[Kokoro]` prefix, delegate to Kokoro sub-agent.

**Do NOT assign** sub-issues to anyone in Linear. The title prefix is sufficient for orchestration.

## Agent Routing

| Trigger Keywords | Agent | Title Prefix | Sub-agent Type |
|------------------|-------|--------------|----------------|
| API, endpoint, database, backend, auth, migration | Kokoro | `[Kokoro]` | `kokoro-backend-specialist` |
| UI, component, frontend, React, Next.js, page | Pixel | `[Pixel]` | `pixel-frontend-specialist` |
| workflow, n8n, automation, webhook, integration | Flux | `[Flux]` | `flux-automation-specialist` |
| deploy, vercel, CI/CD, performance, monitoring | Hermes | `[Hermes]` | `hermes-deployment-specialist` |
| brand, visual, design system, moodboard, wireframe | Aurora | `[Aurora]` | `aurora-product-designer` |
| test, E2E, QA, Playwright, regression | Sentinela | `[Sentinela]` | `sentinela-test-automation-expert` |
| SEO, schema markup, Core Web Vitals | Lumen | `[Lumen]` | `lumen` |

## Delegation Flow

```
1. User request → Mentat analyzes
2. /shape → Create parent issue in Linear
3. /refine → Create sub-issues with [Agent] prefix
4. /dev → Mentat orchestrates:
   a. Load issue + sub-issues from Linear
   b. Check dependencies
   c. Delegate each [Agent] sub-issue via Task tool
   d. Monitor progress, resolve doubts
   e. Validate acceptance criteria
   f. Comment on completion
   g. Move sub-issue to Done
5. All sub-issues Done → Parent moves forward
```

## When to Delegate

**Delegate when:**
- Task requires specialist expertise
- Sub-issue exists with `[Agent]` prefix
- `/dev` is invoked

**Do yourself when:**
- Coordination/planning
- Quick fix without sub-issues
- No specialist knowledge needed

## Multi-agent Order

For full-stack features:

```
1. Mentat     → Architecture, /shape, /refine
2. Aurora     → Design specs (if UI work)
3. Kokoro     → Backend/API first
4. Pixel      → Frontend after API ready
5. Flux       → Automation/integrations
6. Sentinela  → E2E tests after frontend
7. Hermes     → Deploy last
8. Mentat     → Final validation
```

## Dependency Detection

| Agent | Waits For |
|-------|-----------|
| Pixel | Kokoro (API), Aurora (design) |
| Sentinela | Pixel (test IDs) |
| Hermes | All implementation done |

## Delegation Protocol

When delegating via Task tool:

```yaml
Task:
  subagent_type: "{agent-specialist}"
  prompt: |
    ## Linear Issue: {issue-id}
    ## Task: {title without [Agent] prefix}

    {description from sub-issue}

    ## Acceptance Criteria
    {criteria}

    ## Instructions
    1. Implement the task
    2. Follow team conventions
    3. When done, I'll add completion comment to Linear

    ## Dependencies
    {status of blocking issues}
```

## Completion Protocol

When agent returns:

1. **Validate** acceptance criteria met
2. **Comment** on Linear sub-issue:
   ```markdown
   ## Implementation Complete

   **Agent:** {agent-name}
   **Status:** Done

   ### Summary
   {what was done}

   ### Files Changed
   - `path/to/file.ts`

   ### Acceptance Criteria
   - [x] {criterion}
   ```
3. **Update state** → Move sub-issue to Done

## Example

```
Parent: SKY-45 [Feature] WhatsApp button
├── [Kokoro] Add whatsapp_number migration
│   → Delegate to kokoro-backend-specialist
│   → Agent implements
│   → Mentat comments, marks Done
├── [Pixel] WhatsAppButton component + dashboard UI
│   → Blocked until Kokoro done
│   → Delegate to pixel-frontend-specialist
│   → Agent asks: "Which templates?"
│   → Mentat answers: "All 4"
│   → Agent completes
│   → Mentat comments, marks Done
└── [Sentinela] E2E tests for WhatsApp flow
    → Blocked until Pixel done
    → Delegate to sentinela-test-automation-expert
    → Mentat comments, marks Done
```

## Anti-patterns

- Delegating without `[Agent]` prefix in title
- Assigning sub-issues to users (use title prefix only)
- Ignoring dependencies between agents
- Creating local `*_TASKS.md` files (deprecated)
- Not validating acceptance criteria before marking Done
- Skipping completion comments on Linear

## Commands

| Action | Command |
|--------|---------|
| Create parent issue | `/shape` |
| Create agent sub-issues | `/refine` |
| Start orchestrated work | `/dev` |
| Review PR | `/review` |
