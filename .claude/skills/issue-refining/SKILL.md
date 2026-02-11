---
name: issue-refining
description: Refine shaped issues into technical breakdown with agent sub-issues. Use when an issue has been shaped and needs technical planning - identifying agents, creating sub-issues with specific tasks, and adding technical specs (API, DB, components).
---

# Issue Refining

Technical breakdown of shaped issues → agent sub-issues.

## Linear Config

| Setting | Value |
|---------|-------|
| Team | Skywalking |
| Tools | `linear_getIssueById`, `linear_createIssue`, `linear_updateIssue` |
| Parent State | Shaping → Refining → To Do |
| Sub-issue State | To Do |

## Input

- Linear issue ID or URL
- Or: local backlog file reference

## Agents

| Agent | Focus | Trigger | Sub-agent Type |
|-------|-------|---------|----------------|
| Aurora | Design, brand, UI/UX | Visual/design work needed | `aurora-product-designer` |
| Kokoro | Backend, API, auth, DB | Server-side logic, migrations | `kokoro-backend-specialist` |
| Pixel | Frontend, React/Next.js | Components, pages, UI | `pixel-frontend-specialist` |
| Flux | Automation, n8n | Workflows, integrations | `flux-automation-specialist` |
| Hermes | Deploy, Vercel, monitoring | CI/CD, performance | `hermes-deployment-specialist` |
| Sentinela | QA, E2E, Playwright | Test coverage | `sentinela-test-automation-expert` |
| Lumen | SEO, schema | Search optimization | `lumen` |

## Flow

1. **Load issue** → Get from Linear or read local file
2. **Analyze scope** → Identify which agents needed
3. **Ask confirmation** → AskUserQuestion to confirm agents
4. **Create sub-issues** → One per agent with technical specs
5. **Update parent** → Move to "Refining" then "To Do" when ready

## Sub-issue Convention

**Title format:** `[{AGENT}] {specific task description}`

The agent name in brackets is the **delegation signal** for Mentat (orchestrator). When Mentat sees `[Kokoro]` in title, it knows to delegate that sub-issue to the Kokoro sub-agent.

**IMPORTANT:** Do NOT assign sub-issues to anyone. Leave `assigneeId` empty. The title prefix is sufficient for orchestration.

## Sub-issue Template

```yaml
linear_createIssue:
  teamId: "Skywalking"
  title: "[{AGENT}] {specific task}"
  parentId: "{parent_id}"
  stateId: "{to_do_state_id}"
  # NO assigneeId - agent name in title is the delegation signal
  description: |
    ## Scope
    {what this agent needs to do}

    ## Technical Specs
    {API endpoints, DB changes, components, etc.}

    ## Files to Touch
    - `path/to/file1.ts`
    - `path/to/file2.tsx`

    ## Acceptance Criteria
    - [ ] {criterion}
    - [ ] {criterion}

    ## Dependencies
    {other sub-issues this depends on}
```

## Technical Specs by Agent

### Kokoro (Backend)
- DB migrations (SQL)
- API endpoints (route, method, payload)
- Validation schemas
- Auth requirements

### Pixel (Frontend)
- Components to create/modify
- Pages affected
- Props/state requirements
- data-testid for Sentinela

### Aurora (Design)
- Design tokens needed
- Figma/spec references
- Responsive breakpoints
- Accessibility requirements

### Sentinela (QA)
- Test scenarios
- data-testid contract from Pixel
- Edge cases to cover
- Performance benchmarks

### Hermes (Deploy)
- Env vars needed
- Vercel config changes
- Monitoring setup

### Flux (Automation)
- n8n workflow scope
- Triggers and actions
- Error handling

## Dependency Detection

Common patterns:
- Kokoro before Pixel (API needed for frontend)
- Aurora before Pixel (design specs needed)
- Pixel before Sentinela (test IDs needed)
- All before Hermes (deploy last)

## Next Step

After refining:
- `/dev {issue-id}` → Mentat orchestrates agent work
  - Delegates sub-issues based on `[Agent]` prefix
  - Monitors progress, resolves doubts
  - Validates acceptance criteria
  - Comments on completion in Linear

## Example Output

For SKY-45 (WhatsApp button):

```
Parent: [Feature] WhatsApp button configurable
├── [Kokoro] Migration + API validation
│   - ALTER TABLE tenants ADD whatsapp_number
│   - Validation endpoint
├── [Pixel] WhatsAppButton component + dashboard UI
│   - components/storefront/WhatsAppButton.tsx
│   - Integration in 4 templates
│   - Dashboard settings UI
└── [Sentinela] E2E tests
    - Button visibility
    - Click behavior
    - Dashboard config flow

Next: /dev SKY-45
```
