# Improvement Template

## Discovery Questions

**Batch 1:**
- Title/summary
- Current state description

**Batch 2:**
- Proposed improvement
- Why important now

**Batch 3:**
- Success metric (quantifiable)
- Priority: High / Medium / Low

**Batch 4 (Technical Context):**
- Relevant architectural patterns to consider
- Existing implementations to reuse or extend
- Security/performance constraints

**Optional:**
- Scope boundaries (what's NOT included)
- Dependencies

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

## Success Metric
{measurable outcome}

## Technical Context
- **Architecture:** {relevant patterns, existing structure}
- **Reuse:** {implementations to extend}
- **Security:** {constraints, performance requirements}

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
