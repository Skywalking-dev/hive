---
description: /dev Command
---

# /dev Command

Mentat orchestrates agent work on Linear issues.

## Usage

```bash
/dev SKY-123
/dev https://linear.app/skywalking/issue/SKY-123
```

## Flow

1. **Load skill** → Read `.claude/skills/dev/SKILL.md`
2. **Get issue** → `linear_getIssueById`
3. **Find sub-issues** → Filter children with `[Agent]` prefix
4. **Check dependencies** → Order by agent dependency chain
5. **Delegate** → Task tool to each agent sequentially
6. **Monitor** → Answer agent questions, validate criteria
7. **Comment** → `linear_createComment` on completion
8. **Update state** → `linear_updateIssue` to Done

## Delegation Order

```
Aurora → Kokoro → Pixel → Flux → Sentinela → Hermes
```

Skip agents without sub-issues.

## Agent Mapping

| Prefix | Sub-agent Type |
|--------|----------------|
| `[Kokoro]` | `kokoro-backend-specialist` |
| `[Pixel]` | `pixel-frontend-specialist` |
| `[Aurora]` | `aurora-product-designer` |
| `[Flux]` | `flux-automation-specialist` |
| `[Hermes]` | `hermes-deployment-specialist` |
| `[Sentinela]` | `sentinela-test-automation-expert` |
| `[Lumen]` | `lumen` |

## Mentat Responsibilities

During orchestration:
- Answer agent questions
- Provide missing context
- Validate acceptance criteria met
- Add completion comments to Linear
- Move sub-issues to Done

## Output

Show progress as each agent completes:

```
Starting SKY-45...

[1/3] Delegating [Kokoro] Add migration...
      Done ✓

[2/3] Delegating [Pixel] WhatsAppButton...
      Question: "Which templates?"
      Answer: "All 4 templates"
      Done ✓

[3/3] Delegating [Sentinela] E2E tests...
      Done ✓

All sub-issues complete. SKY-45 → In Review
```

## Notes

- Linear is source of truth
- Sub-issues use title prefix for routing
- No manual assignment needed
- Mentat owns orchestration session
