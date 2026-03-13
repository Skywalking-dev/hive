# Improvement Template

## Discovery Questions

**Batch 1:**
- Title/summary
- Current state description

**Batch 2:**
- Proposed improvement
- Why important now

**Batch 3:**
- Acceptance criteria (use EARS syntax — see below)
- Success metric (quantifiable)
- Priority: High / Medium / Low

**Batch 4 (Technical Context):**
- Relevant architectural patterns to consider
- Existing implementations to reuse or extend
- Security/performance constraints

**Optional:**
- Scope boundaries (what's NOT included)
- Dependencies

## EARS Syntax Guide

Write each acceptance criterion using one of these patterns:

| Pattern | Syntax |
|---------|--------|
| Always true | `THE SYSTEM SHALL [capability]` |
| Event-driven | `WHEN [event] THE SYSTEM SHALL [response]` |
| State-driven | `WHILE [state] THE SYSTEM SHALL [behavior]` |
| Conditional | `IF [condition] THE SYSTEM SHALL [action]` |

Mark ambiguous items with `[NEEDS CLARIFICATION: question]`.

## Description Template

```markdown
## Description
{2-4 sentences describing the improvement}

## Context
{why this matters now}

## Current State
{how it works today}

## Proposed State
{how it should work after improvement}

## Acceptance Criteria (EARS)
- [ ] WHEN {event} THE SYSTEM SHALL {response}
- [ ] THE SYSTEM SHALL {capability}
- [ ] IF {condition} THE SYSTEM SHALL {action}

## Success Metric
{measurable outcome}

## Technical Context
- **Architecture:** {relevant patterns, existing structure}
- **Reuse:** {implementations to extend}
- **Security:** {constraints, performance requirements}

## Open Questions
- [NEEDS CLARIFICATION: {ambiguous aspect}]

## Additional Context
{scope, dependencies, technical notes}

---
*Created via /shape*
```

## Linear Issue

```yaml
title: "[Improvement] {summary}"
labelIds: ["improvement"]
state: "Backlog"
priority: # based on impact
  High: 2
  Medium: 3
  Low: 4
```
