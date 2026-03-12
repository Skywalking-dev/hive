---
name: video-analysis
description: Analyze video transcripts or text to extract topics, actionable insights, and connections. Use when user has transcript text and wants structured analysis.
---

# Skill: Video Analysis

## Overview

Analyze video transcripts to extract structured knowledge: topics, actionable insights, cross-references, and key quotes. Claude IS the analyzer — no external API calls, no scripts. Works with any content domain.

## When to Use

- User has transcript text (pasted, file, or just extracted via `/extract_transcript`)
- User wants structured analysis of video content
- Need to extract topics, insights, or actionable items from spoken content
- Cross-referencing multiple transcripts

## When NOT to Use

- Need transcript extraction (use `/extract_transcript` first)
- Need audio/visual analysis (not text-based)
- Content is not from video/audio (use general analysis instead)

## Input Handling

### Source Types

1. **Pasted text** — User pastes transcript directly
2. **File path** — Read transcript from file (JSON from handler or plain text)
3. **YouTube URL** — Chain: first run `/extract_transcript <url>`, then analyze the result
4. **Previous extraction** — Use transcript already in conversation context

### URL Detection

If input looks like a YouTube URL:
1. Extract video ID
2. Run: `cd hive && uv run python scripts/transcript_handler.py extract <video_id>`
3. Parse JSON result
4. Analyze the `total_text` field

### File Detection

If input is a file path:
1. Read the file
2. If JSON (from transcript handler): extract `data.total_text`
3. If plain text/markdown: use content directly

## Analysis Framework

Apply these 5 lenses to every transcript:

### 1. Topics (max 10)

Extract main topics discussed. For each topic:

- **Name**: Concise label (2-5 words)
- **Depth**: `introductory` | `intermediate` | `advanced`
- **Summary**: 1-2 sentences capturing the key point
- **Timestamp range**: If segments available, approximate time range

### 2. Actionable Insights

Concrete, implementable ideas. For each:

- **What**: The insight or technique
- **How**: 2-3 concrete steps to implement
- **Context**: When/where this applies
- **Difficulty**: `easy` | `medium` | `hard`

### 3. Connections

Links between topics within the transcript and to broader knowledge:

- **Internal**: How topics in this video relate to each other
- **External**: Related concepts, frameworks, or fields
- **Pattern**: Identify recurring themes or methodologies

### 4. Key Quotes

Verbatim quotes that capture essential ideas:

- Max 5-7 quotes
- Must be exact from transcript (not paraphrased)
- Include surrounding context
- Flag quotes that are particularly quotable/shareable

### 5. Recommended Deep Dives

Topics worth exploring further:

- What to search for
- Why it's worth going deeper
- Suggested sources or search terms

## Output Template

```markdown
# Video Analysis: [Title or Topic]

**Source:** [URL or file path]
**Language:** [detected language]
**Length:** [character/word count]

---

## Topics

### 1. [Topic Name] `[depth]`
[Summary]

### 2. [Topic Name] `[depth]`
[Summary]

[... up to 10]

---

## Actionable Insights

### [Insight title]
**What:** [description]
**How:**
1. [step]
2. [step]
3. [step]
**Difficulty:** [level]

[... repeat for each insight]

---

## Connections

**Internal links:**
- [Topic A] ↔ [Topic B]: [how they connect]

**External links:**
- [Topic] → [broader concept/field]

**Recurring patterns:**
- [pattern description]

---

## Key Quotes

> "[exact quote]"
— Context: [where/why this matters]

[... max 7]

---

## Recommended Deep Dives

1. **[Topic]** — [why + search terms]
2. **[Topic]** — [why + search terms]

---

## Next Steps

- [suggested action based on content]
```

## Quality Guidelines

1. **Max 10 topics** — prioritize by importance, not order of appearance
2. **Specific > generic** — "Use cover crops to fix nitrogen" beats "Soil improvement techniques"
3. **Actionable > descriptive** — insights must have concrete steps
4. **Exact quotes** — never paraphrase in the quotes section
5. **Honest depth** — don't inflate introductory content to "advanced"
6. **Domain-aware** — adapt terminology to the content's field
7. **Language match** — analyze in the same language as the transcript

## Multi-Transcript Mode

When analyzing multiple transcripts together:

1. Analyze each independently first
2. Then produce a cross-analysis:
   - **Common topics** across videos
   - **Contradictions** or different perspectives
   - **Progressive depth** — which video goes deeper on what
   - **Recommended viewing order** based on topic progression
   - **Combined insights** that emerge from the collection

## Chaining with Extract

Typical workflow:
```
User: /extract_transcript https://youtube.com/watch?v=VIDEO_ID
Claude: [extracts transcript, shows preview]

User: /analyze_video
Claude: [analyzes the transcript already in context]
```

Or all-in-one:
```
User: /analyze_video https://youtube.com/watch?v=VIDEO_ID
Claude: [extracts + analyzes in one flow]
```

## Examples

### Single video analysis
```
/analyze_video https://youtube.com/watch?v=U36BocbXJs8
```

### Analyze pasted text
```
/analyze_video
[user pastes transcript]
```

### Analyze from file
```
/analyze_video /path/to/transcript.json
```

### Multi-video comparison
```
/analyze_video
Videos:
- https://youtube.com/watch?v=VIDEO1
- https://youtube.com/watch?v=VIDEO2
Compare topics and insights across both.
```
