# Feature Template

## Discovery Questions

**Batch 1:**
- Title/summary of the feature
- User/beneficiary

**Batch 2:**
- Problem it solves
- Current situation/workaround

**Batch 3:**
- Success criteria (acceptance criteria)
- Priority: High / Medium / Low

**Optional:**
- Technical constraints
- Related issues

## Description Template

```markdown
## Description
{2-4 sentences describing the feature}

## Context
{background, why this matters}

## User Story
As a {user type}, I want to {action} so that {benefit}.

## Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}
- [ ] {criterion 3}

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
