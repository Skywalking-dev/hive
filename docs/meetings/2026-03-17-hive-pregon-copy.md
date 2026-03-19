# Hive — Landing Page Copy
> Author: Pregon | Date: 2026-03-17 | Page: skywalking.dev/hive

---

## SEO

**Meta title:**
`Hive — 40+ skills and 9 agents for Claude Code`

**Meta description:**
`Open source plugin for Claude Code, Cursor, and Gemini CLI. Slash commands for Gmail, Slack, GitHub, Vercel, Supabase, and more. MIT licensed.`

**OG description (social sharing):**
`Stop copy-pasting docs. Hive gives your AI assistant slash commands for the tools you already use — Gmail, Slack, Supabase, Vercel, GitHub. 40+ skills, 9 specialist agents, one repo.`

---

## Hero

**Headline:**
```
Give your AI assistant superpowers.
```

**Subheadline:**
```
40+ skills. 9 agents. One plugin.
Works with Claude Code, Cursor, Gemini CLI, and Codex.
```

---

## Animated Terminal — 6 Commands

Each line appears sequentially in the hero terminal. Pause 1.2s between lines. Show the comment inline.

```bash
/gmail inbox --unread                        # check email without leaving your editor
/slack read <thread_url>                     # catch up on a thread in seconds
/perplexity "best auth library for Next.js"  # search the web with AI summaries
/shape                                       # turn a fuzzy idea into a Linear issue
/ship_it                                     # commit, push, open PR in one command
/google-docs get <url>                       # read any doc as Markdown, instantly
```

**Terminal label (top bar of the terminal UI):**
```
~/projects/myapp  claude
```

---

## CTAs

**Primary button:**
```
View on GitHub
```
_(with live star count badge next to it)_

**Secondary button:**
```
Book a call
```
_(links to Calendly with `?utm_source=github&utm_medium=hive&utm_campaign=oss-launch`)_

**Secondary button subtext (below the button, small):**
```
Want this configured for your team?
```

---

## Social proof line

```
Used in production at Skywalking — the dev studio that built it, in Patagonia, Argentina.
```

---

## Section: Skills

**Section title:**
```
Everything your stack needs.
```

**Section intro:**
```
Skills are Markdown files that teach your AI how to use a tool. Add a key, get a command. No wiring required.
```

**Category labels** (for the grid groupings):

| Category label | Skills it covers |
|---|---|
| Google | Gmail, Docs, Drive, Calendar, Workspace, YouTube |
| Search & AI | Perplexity, video analysis |
| Communication | Slack, WhatsApp |
| Infrastructure | Supabase, Vercel |
| Dev Workflow | shape, refine, dev, ship_it, pr-review, capture |
| Dev Tools | test-debug, GitHub CLI, adversarial review |
| Media | Audio transcription |

**Bottom of section (link):**
```
Don't see your tool? Write a skill in 10 minutes. →
```
_(links to the skill creation docs / `#creating-skills` anchor)_

---

## Section: Agents

**Section title:**
```
A full team, on demand.
```

**Section intro:**
```
Agents are specialist personas with deep domain knowledge. Delegate a task, get back a result. Each agent knows its domain — you don't have to.
```

**Agent card copy** (name + one-line focus):

| Agent | Card line |
|---|---|
| Aurora | Brand identity, design systems, UI specs |
| Pixel | Next.js/React — build fast, ship accessible |
| Kokoro | FastAPI, databases, auth, backend architecture |
| Sentinela | QA strategy, Playwright E2E, regression |
| Hermes | Vercel, CI/CD, edge functions, monitoring |
| Flux | n8n workflows, automation, integrations |
| Oraculo | Web research, competitive intel, tech evaluation |
| Pregon | Content strategy, social media, email campaigns |
| Lumen | Technical SEO, Core Web Vitals, schema |

---

## Section: Quick Start

**Section title:**
```
Running in under 2 minutes.
```

**Section intro:**
```
Clone, sync, add the keys you need. Everything else is optional.
```

**Code block 1 — Install:**
```bash
git clone https://github.com/Skywalking-dev/hive.git
cd hive
uv sync
cp .env.example .env
python install_skills.py --all
```

**Code block 2 — Use as Claude Code plugin:**
```bash
claude --plugin-dir /path/to/hive
```

**Code block 3 — Sync to other providers:**
```bash
python release.py   # Cursor, Gemini CLI, Codex
```

**Note below code:**
```
Zero required API keys. Add credentials only for the integrations you use.
```

---

## Section: Final CTA

**Section title:**
```
Open source. MIT licensed. No vendor lock-in.
```

**Body:**
```
Hive is maintained by Skywalking. Star the repo to follow updates. If you want it configured and running for your team, book a call.
```

**Primary button (repeat):**
```
View on GitHub
```

**Secondary button (repeat):**
```
Book a call
```

---

## Notes for Pixel (implementation)

- Terminal animation: type each command at ~40 chars/sec, pause on the comment, then fade in next line.
- Star badge: use GitHub's shields.io badge (`?style=social`) inline with the primary CTA.
- "Used in production" line: place directly under the hero CTA buttons, small text, muted color (`#8B949E`).
- Section intros: Inter, 18px, `#8B949E`, max-width 600px centered.
- Quick Start code blocks: JetBrains Mono, syntax highlighted, copy-to-clipboard button on hover.
- All external links open in new tab. UTM on Calendly links only.
