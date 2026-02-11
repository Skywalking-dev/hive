---
description: Refine a shaped issue into technical breakdown with agent sub-issues
---

# /refine Command

Technical breakdown flow. Uses `issue-refining` skill.

## Usage

```bash
/refine SKY-123
/refine https://linear.app/skywalking/issue/SKY-123
/refine @path/to/local/issue.md
```

## Flow

1. **Load issue** → From Linear ID/URL or local file
2. **Analyze** → Identify agents needed based on scope
3. **Confirm** → AskUserQuestion for agent selection
4. **Create sub-issues** → Per agent with technical specs
5. **Update state** → Parent moves Shaping → Refining → To Do

## Output

- Sub-issues created in Linear under parent
- Each sub-issue has:
  - Specific scope
  - Technical specs
  - Files to touch
  - Acceptance criteria
  - Dependencies on other sub-issues

## Notes

- Requires shaped issue (use `/shape` first if needed)
- Detects dependencies between agents automatically
- Moves parent to "To Do" when refinement complete
