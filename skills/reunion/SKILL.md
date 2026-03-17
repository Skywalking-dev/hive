---
skill: reunion
trigger: Use when multiple agents need to align on a decision, resolve conflicts between strategies, or produce a unified plan. Triggers on "reunion", "meeting", "alinear agentes", "que se reunan", "sync entre agentes".
model: opus
---

# Reunion de Agentes

**Purpose:** Structured alignment between 2-5 agents → concrete decisions, not transcripts.

**Output:** Decision doc at `docs/meetings/YYYY-MM-DD-{topic}.md`

**Core principle:** The output is for HUMANS. If a human can't read it in 2 minutes, it's too long.

## Protocol

### Step 0: Setup

Infer or ask:
1. **Tema** — What needs alignment?
2. **Participantes** — Which agents?
3. **Decisiones esperadas** — What concrete decisions must come out?

### Step 1: Create Meeting File

Create `docs/meetings/YYYY-MM-DD-{topic-slug}.md`:

```markdown
# {Tema}

> **Fecha:** YYYY-MM-DD | **Participantes:** Agent1, Agent2, ... | **Issue:** SKY-XXX

## Decisiones necesarias

1. {decision 1}
2. {decision 2}
...

---

## Propuestas

### {Agent1}

| Decisión | Propuesta | Justificación |
|---|---|---|
| {decisión 1} | {respuesta concreta} | {1 línea por qué} |
| {decisión 2} | {respuesta concreta} | {1 línea por qué} |

**Necesito de otros:** {1-2 bullets max}
**Conflicto que veo:** {1 bullet max, o "ninguno"}

### {Agent2}
...

---

## Conflictos

| # | Tema | {Agent1} dice | {Agent2} dice | Resolución |
|---|---|---|---|---|
| 1 | ... | ... | ... | _pendiente_ |

---

## Decisiones finales

| # | Decisión | Resolución | Owner |
|---|---|---|---|
| 1 | ... | ... | ... |

## Timeline

| Día | Entregable | Owner | Depende de |
|---|---|---|---|
| D+0 | ... | ... | — |

## Pendientes (usuario)

- ...
```

### Step 2: Propuestas (PARALLEL)

Launch ALL agents in parallel. Each agent:
- Reads its definition at `hive/agents/{agent}.md`
- Reads the meeting file
- Fills its table under "Propuestas"

**CRITICAL format rules for agents:**

```
You are {AgentName} for Skywalking.dev.
Read your definition at hive/agents/{agent-file}.md
Read the meeting file at {path}.

Fill your "Propuestas" table. Rules:
- ONE ROW per decision needed. Answer each decision directly.
- "Propuesta" column: concrete answer (hex code, lib name, file path, number). NO prose.
- "Justificación" column: ONE sentence max. Why this choice.
- "Necesito de otros": max 2 bullets. What blocks you.
- "Conflicto que veo": max 1 bullet. What will clash with another agent. Or "ninguno".
- TOTAL max 15 lines. If you write more, you failed.
- Spanish. No filler. No "estoy de acuerdo con la visión de...". Just answers.
```

### Step 3: Conflict Resolution (PARALLEL, only if needed)

After reading all proposals, Mentat:

1. Fills the "Conflictos" table — where agents disagree
2. If conflicts exist (>0 rows), launches ONLY the conflicting agents in parallel with:

```
You are {AgentName}. Read the meeting file at {path}.
You disagree with {OtherAgent} on: {conflict description}.
In the Conflictos table, write your final position in your column.
ONE sentence. Include what you'd accept as compromise.
```

3. If no conflicts, skip to Step 4.

**Max 1 conflict round.** If unresolved, Mentat decides.

### Step 4: Resoluciones (MENTAT)

Mentat reads all proposals + conflict resolutions and writes:

1. **Decisiones finales** — table with resolution + owner per decision
2. **Timeline** — table with day, deliverable, owner, dependency
3. **Pendientes (usuario)** — questions only the user can answer

That's it. No "acuerdos alcanzados", no "conflictos resueltos" recap, no redundant sections. The tables ARE the decisions.

### Step 5: Present to User

Show the Decisiones finales table + Pendientes. Link to meeting file. Done.

## Format Rules (NON-NEGOTIABLE)

- **Tables > prose.** Every decision is a table row, not a paragraph.
- **15 lines max per agent.** Agents that write more get their output truncated.
- **No repetition.** If Agent1 said X in Propuestas, Agent2 doesn't restate it in Conflictos.
- **No "estoy de acuerdo".** Agreement = same value in the table. No need to narrate it.
- **No preamble.** Agents don't explain their role, restate the context, or summarize what others said.
- **Concrete values only.** "warm earth tones" is not a proposal. `#C4A86A, #8B7355, #7A9B7F` is.
- **Spanish.** ES-LATAM, terse.
- **Total meeting file < 100 lines.** If it exceeds this, the format failed.

## Agent Reference

| Agent | subagent_type | Domain |
|---|---|---|
| Aurora | `aurora-product-designer` | Brand, visual design, UI specs |
| Kokoro | `kokoro-backend-specialist` | APIs, databases, auth, security |
| Pixel | `pixel-frontend-specialist` | Next.js, React, UI implementation |
| Flux | `flux-automation-specialist` | n8n workflows, integrations |
| Hermes | `hermes-deployment-specialist` | Vercel, CI/CD, performance |
| Sentinela | `sentinela-test-automation-expert` | Testing, QA, Playwright |
| Lumen | `lumen-seo-specialist` | SEO, visibility, schema markup |
| Pregon | `pregon-marketing-specialist` | Content, social, campaigns |
| Oraculo | `oraculo-research-specialist` | Web research, competitive intel |

**Note:** For agents without a dedicated subagent_type, use `general-purpose` with their definition from `hive/agents/{name}.md`.

## Anti-patterns

- **No transcripts.** This is a decision doc, not meeting minutes.
- **No "Ronda 1 / Ronda 2" format.** Proposals + conflicts + decisions. Three sections.
- **No agent monologues.** Tables enforce structure.
- **No Mentat opinion in Propuestas.** Mentat resolves conflicts, doesn't propose.
- **No meetings for 1 agent.** Direct delegation instead.
- **No meetings without decision targets.** If nothing needs deciding, don't meet.
