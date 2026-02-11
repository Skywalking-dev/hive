---
description: Quick capture an idea to Linear backlog without full discovery
---

# /capture Command

Fast idea capture. Uses `quick-capture` skill.

## Usage

```bash
/capture "title of the idea"
/capture "title" "optional context"
```

## Flow

1. Parse title (required) and context (optional) from args
2. Get all the context you need to understand the idea, ask with AskUserQuestion
3. Create issue in Linear → Triage
4. Return URL

## Next Step

Run `/shape` on the captured issue for full discovery.
