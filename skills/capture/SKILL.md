---
name: capture
description: Capture ideas quickly into Linear backlog with minimal friction. Use when user has a quick idea, bug report, or thought that needs to be captured without full discovery process. Creates issue in Backlog state with title and brief context.
---

# Quick Capture

Fast idea capture → Linear Backlog. Extracts painpoint, propuesta y objetivo en una sola pregunta.

## Linear Config

| Setting | Value |
|---------|-------|
| Team | Skywalking |
| State | Backlog |
| Tools | `linear_createIssue` |

## Flow

1. Parse input for whatever context the user provided
2. Identify what's missing from the **3 pillars** (see below)
3. Ask **ONE single AskUserQuestion** with only the missing pillars — never ask what the user already said
4. Create in Linear with state "Backlog"
5. Return Linear URL

## The 3 Pillars

Every capture needs these 3 elements. Extract them from the user's input — only ask for what's missing:

| Pillar | Question | Purpose |
|--------|----------|---------|
| **Painpoint** | Qué problema/fricción existe hoy? | El "por qué" — qué duele, qué falla, qué falta |
| **Propuesta** | Qué se propone hacer? | El "qué" — la idea, feature, fix, cambio |
| **Objetivo** | Qué resultado se espera lograr? | El "para qué" — métrica, outcome, mejora concreta |

### Parsing Rules

- If user says `"Add dark mode toggle"` → propuesta is clear, ask painpoint + objetivo
- If user says `"Los usuarios no pueden ver la app de noche, necesitamos dark mode"` → painpoint + propuesta clear, ask objetivo
- If user provides all 3 → don't ask anything, create directly
- Always infer what you can. Don't re-ask what's obvious from context

### Single Question Format

When asking, combine missing pillars into ONE question:

```
Para capturar bien esto necesito:
- **Dolor:** {pregunta sobre painpoint}
- **Objetivo:** {pregunta sobre resultado esperado}

(responde breve, 1 línea cada uno)
```

## Issue Creation

```yaml
linear_createIssue:
  teamId: "Skywalking"
  title: "{propuesta — concise}"
  description: |
    ## Painpoint
    {painpoint}

    ## Propuesta
    {propuesta}

    ## Objetivo
    {objetivo}

    ---
    *Captured via /capture — needs /shape for full discovery*
  stateId: "{backlog_state_id}"
  priority: 4  # Low - to be triaged
```

### Priority Auto-detection

| Signal in input | Priority |
|-----------------|----------|
| "broken", "roto", "down", "caído", "prod" | 2 (High) |
| "urgent", "urgente", "asap", "blocker" | 1 (Urgent) |
| Default | 4 (Low) |

## Next Steps

After capture, issue follows workflow:

1. `/shape {issue-id}` → Full discovery, move to Shaping
2. `/refine {issue-id}` → Technical breakdown, agent sub-issues
3. `/dev {issue-id}` → Mentat orchestrates implementation

## Examples

```bash
/capture "Add dark mode toggle"
→ Asks: painpoint + objetivo (propuesta already clear)
→ SKY-50 created in Backlog

/capture "Los usuarios se quejan de que no pueden usar la app de noche, agregar dark mode para mejorar retención"
→ All 3 pillars present → creates directly, no questions
→ SKY-51 created in Backlog

/capture "API rate limiting broken on prod"
→ Asks: objetivo (painpoint = broken, propuesta = fix rate limiting)
→ SKY-52 created in Backlog (priority: High — "broken" + "prod")
```

## Decision: Capture vs Shape

| Signal | Command |
|--------|---------|
| Quick thought, 1-3 bullets max | `/capture` |
| Ready for full discovery (AC, scope, agents) | `/shape` |
| Already defined, needs breakdown | `/refine` |
