# Feature Template

## Discovery Questions

**Batch 1:**
- Title/summary of the feature
- User/beneficiary

**Batch 2:**
- Problem it solves
- Current situation/workaround

**Batch 3:**
- Acceptance criteria (use EARS syntax — see below)
- Priority: High / Medium / Low

**Batch 4 (Technical Context):**
- Relevant architectural patterns (e.g., existing API structure, DB schema)
- Existing implementations to reuse or reference
- Security/compliance constraints

**Optional:**
- Related issues

## EARS Syntax Guide

Write each acceptance criterion using one of these patterns:

| Pattern | Syntax |
|---------|--------|
| Always true | `THE SYSTEM SHALL [capability]` |
| Event-driven | `WHEN [event] THE SYSTEM SHALL [response]` |
| State-driven | `WHILE [state] THE SYSTEM SHALL [behavior]` |
| Conditional | `IF [condition] THE SYSTEM SHALL [action]` |
| Complex | `WHEN [event] WHILE [state] IF [condition] THE SYSTEM SHALL [response]` |

**Rules:**
- No "should", "could", "ideally" — only SHALL (mandatory) or WILL (intent)
- Each criterion must be independently testable
- Mark ambiguous items with `[NEEDS CLARIFICATION: question]`

## Description Template

```markdown
## Description
{2-4 sentences describing the feature}

## Context
{background, why this matters}

## User Story
As a {user type}, I want to {action} so that {benefit}.

## Technical Context
- **Architecture:** {relevant patterns, existing structure}
- **Reuse:** {existing implementations to reference}
- **Security:** {constraints, compliance requirements}

## Acceptance Criteria (EARS)
- [ ] WHEN {event} THE SYSTEM SHALL {response}
- [ ] THE SYSTEM SHALL {capability}
- [ ] IF {condition} THE SYSTEM SHALL {action}

## Open Questions
- [NEEDS CLARIFICATION: {ambiguous aspect}]

## Additional Context
{technical notes, related features}

---
*Created via /shape*
```

## Linear Issue

```yaml
title: "[Feature] {summary}"
labelIds: ["feature"]
state: "Backlog"
priority: # based on business value
  High: 2
  Medium: 3
  Low: 4
```
