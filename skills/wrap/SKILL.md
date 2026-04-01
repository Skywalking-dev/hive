---
name: wrap
description: End-of-session summary and conversation rename. Use when user says "/wrap", "wrap", "resumen de sesion", or signals they're done working. Generates a structured summary of what was accomplished and renames the conversation.
---

# Wrap

End-of-session closure. Summarize what happened, rename the conversation.

## Flow

1. **Scan conversation** for all actions taken:
   - Issues created/updated/closed in Linear
   - Code committed/pushed/merged
   - PRs opened/reviewed/shipped
   - Files created/edited/deleted
   - Agents delegated and their results
   - Decisions made
   - Research done

2. **Generate summary** in this format:

```markdown
## Sesion — {date}

### Shipped
- {list of PRs merged, deploys verified}

### Linear
- {issues closed, created, moved, organized}

### Decisions
- {key decisions or directions taken}

### Pending
- {anything left open, blockers, next steps}

### Stats
- PRs merged: N
- Issues closed: N
- Files changed: ~N
- Agents used: {list}
```

3. **Rename conversation** using the Bash tool:
```bash
claude conversation rename "{short-descriptive-name}"
```

The name should be 3-6 words capturing the main theme. Examples:
- "micelio improvements batch ship"
- "kronos bug fixes + linear cleanup"
- "nexestate discovery + backlog org"

Pick the dominant activity. If mixed, use the most impactful one.

## Rules

- Keep summary concise — bullets, no prose
- Only include what actually happened, not plans
- Stats should be approximate if exact count is unclear
- Rename should be lowercase, no special chars
- If session was short (1-2 actions), keep summary to 3-4 lines
