# Bug Template

## Discovery Questions

**Batch 1:**
- Title/summary of the bug
- Location (URL, screen, component)

**Batch 2:**
- Current (broken) behavior
- Expected behavior

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

## Description Template

```markdown
## Description
{2-4 sentences describing the bug}

## Context
{where it happens, who is affected}

## Current Behavior
{what's happening - broken state}

## Expected Behavior
{what should happen - correct state}

## Reproduction Steps
1. {step}
2. {step}
3. {step}

**Frequency:** {Always|Sometimes|Rarely}

## Technical Context
- **Affected code:** {paths, components, APIs}
- **Recent changes:** {commits, deploys that may relate}
- **Security:** {implications if any}

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
