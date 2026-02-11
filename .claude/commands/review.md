---
description: Review a PR and sync state with Linear
---

# /review Command

PR review + Linear sync. Uses `pr-review` skill.

## Usage

```bash
/review #123
/review https://github.com/org/repo/pull/123
/review SKY-123   # finds PR linked to this issue
```

## Flow

1. **Get PR** → `gh pr view`
2. **Find Linear issue** → From branch name or PR body
3. **Review changes** → Automated checks + analysis
4. **Sync state** → Update Linear based on PR state
5. **Provide feedback** → Comment on PR if issues found

## State Sync

| PR State | Linear State |
|----------|-------------|
| Open | In Review |
| Approved | Resolved |
| Merged | Testing |

## Output

- Review summary with checks
- Linear issue state updated
- PR comment if issues found

## Notes

- Auto-detects Linear ID from branch/PR body
- Uses `gh` CLI for GitHub operations
- Requires Linear MCP for state updates
