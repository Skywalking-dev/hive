# Bug Template

## Discovery Questions

**Batch 1:**
- Title/summary of the bug
- Location (URL, screen, component)

**Batch 2:**
- Current (broken) behavior
- Expected behavior (use EARS — see below)

**Batch 3:**
- Reproduction steps (numbered)
- Frequency: Always / Sometimes / Rarely

**Batch 4:**
- Priority/Severity
- Additional context (screenshots, logs)

**Batch 5 (Technical Context):**
- Relevant code paths / components affected
- Recent changes that may have caused the issue
- Security implications (if any)

## EARS for Bug Fix Criteria

Write expected behavior using EARS patterns:

| Pattern | Syntax |
|---------|--------|
| Always true | `THE SYSTEM SHALL [capability]` |
| Event-driven | `WHEN [event] THE SYSTEM SHALL [response]` |
| Conditional | `IF [condition] THE SYSTEM SHALL [action]` |

Mark unknowns with `[NEEDS CLARIFICATION: question]`.

## Description Template

```markdown
## Description
{2-4 sentences describing the bug}

## Context
{where it happens, who is affected}

## Current Behavior
{what's happening - broken state}

## Expected Behavior (EARS)
- WHEN {event} THE SYSTEM SHALL {correct response}
- THE SYSTEM SHALL {expected capability}

## Reproduction Steps
1. {step}
2. {step}
3. {step}

**Frequency:** {Always|Sometimes|Rarely}

## Technical Context
- **Affected code:** {paths, components, APIs}
- **Recent changes:** {commits, deploys that may relate}
- **Security:** {implications if any}

## Open Questions
- [NEEDS CLARIFICATION: {unclear aspect}]

## Additional Context
{screenshots, logs, related issues}

---
*Created via /shape*
```

## Linear Issue

```yaml
title: "[Bug] {summary}"
labelIds: ["bug"]
state: "Backlog"
priority: # based on severity
  Critical: 1
  High: 2
  Medium: 3
  Low: 4
```
