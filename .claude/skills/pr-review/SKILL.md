---
name: pr-review
description: Review pull requests and sync with Linear issues. Use when there's a PR to review, need to sync PR state with Linear, or want automated review feedback. Handles GitHub PR operations and Linear state transitions.
---

# PR Review

GitHub PR review + Linear state sync.

## Config

| Setting | Value |
|---------|-------|
| GitHub | `gh` CLI |
| Linear | MCP `linear_updateIssue`, `linear_createComment` |
| PR State → Linear State | Draft → In Progress, Open → In Review, Merged → Testing |

## Input

- PR URL: `https://github.com/org/repo/pull/123`
- PR number: `#123` (uses current repo)
- Linear issue ID: `SKY-123` (finds linked PR)

## Flow

1. **Get PR info** → `gh pr view`
2. **Extract Linear ID** → From branch name or PR body
3. **Sync state** → Update Linear issue state
4. **Review PR** → Analyze changes, provide feedback
5. **Update status** → Comment on PR, update Linear

## State Mapping

| PR State | Linear State |
|----------|-------------|
| Draft | In Progress |
| Open (ready for review) | In Review |
| Changes requested | In Progress |
| Approved | Resolved |
| Merged | Testing |
| Closed (not merged) | To Do |

## Branch Name Convention

Extract Linear ID from branch:
```
feature/SKY-123/kokoro-20250118  → SKY-123
feature/MIIC-45/pixel-20250118   → MIIC-45
fix/SKY-67-cart-bug              → SKY-67
```

Regex: `(SKY|MIIC|[A-Z]+)-\d+`

## PR Body Detection

Look for Linear links:
```markdown
Closes SKY-123
Fixes https://linear.app/skywalking/issue/SKY-123
Related: SKY-456
```

## Review Checklist

Auto-check in PR:
- [ ] Tests pass
- [ ] No console.log/debug statements
- [ ] Types are correct
- [ ] No hardcoded values
- [ ] data-testid where needed
- [ ] Changelog updated (if significant)

## Commands

### Get PR Info
```bash
gh pr view {number} --json title,body,state,reviews,checks
```

### Add Review Comment
```bash
gh pr review {number} --comment --body "{feedback}"
```

### Approve
```bash
gh pr review {number} --approve
```

### Request Changes
```bash
gh pr review {number} --request-changes --body "{issues}"
```

## Linear Update

```yaml
linear_updateIssue:
  id: "{issue_id}"
  stateId: "{new_state_id}"
```

Add comment on state change:
```yaml
linear_createComment:
  issueId: "{issue_id}"
  body: |
    PR #47 review complete.
    Status: Approved
    Moving to Resolved.
```

## Automation Triggers

When PR is:
- **Opened** → Move Linear to "In Review"
- **Approved** → Move Linear to "Resolved"
- **Merged** → Move Linear to "Testing"
- **Changes requested** → Keep in "In Review", add comment

## Integration with Work Orchestration

When agent completes work via `/dev`:
1. Agent creates PR
2. Mentat runs `/review` to sync with Linear
3. PR approval → sub-issue moves to Done
4. All sub-issues Done → parent moves forward

## Example

```bash
/review https://github.com/skywalking/miicel.io/pull/47

# Output:
PR #47: Add WhatsApp button component
State: Open (ready for review)
Linked: SKY-45

Review:
✅ Tests passing
✅ Types correct
⚠️ Missing data-testid on WhatsAppButton
❌ Console.log on line 45

Linear: SKY-45 → In Review
```
