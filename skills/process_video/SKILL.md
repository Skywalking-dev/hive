---
name: process_video
description: "Watch: extract transcripts from YouTube or local video files, then analyze content for topics, insights, and connections. Replaces extract_transcript + video-analysis as a single sense."
argument-hint: <youtube_url_or_file_path> [--analyze] [--languages es,en]
allowed-tools: Bash(uv run:*), Bash(ffmpeg:*), Read
---

# Process Video

Extract transcript + analyze content. One skill, one command.

## Modes

| Mode | Input | What Happens |
|------|-------|-------------|
| **YouTube** | URL or video ID | Extract transcript via API (free, fast) |
| **Local file** | Path to .mp4/.mkv/.webm | Extract audio → transcribe via Whisper |
| **Analyze** | Add `--analyze` or just ask | Extract + structured analysis |
| **Text only** | Pasted transcript | Skip extraction, go straight to analysis |

## Execution

### Step 1 — Detect Input Type

```
YouTube URL/ID → transcript_handler.py extract
Local video file → ffmpeg audio extract → process_audio → transcribe
Pasted text → skip to analysis
File path (.txt/.json) → read file → skip to analysis
```

### Step 2 — Extract Transcript

**YouTube:**
```bash
cd hive && uv run python scripts/transcript_handler.py extract <VIDEO_ID> --languages es,en
```

**Local video:**
```bash
# Extract audio
ffmpeg -i /path/to/video.mp4 -vn -acodec mp3 -ab 128k /tmp/video_audio.mp3
# Transcribe via process_audio skill
hive/skills/process_audio/scripts/process_audio.sh /tmp/video_audio.mp3 --transcribe
```

### Step 3 — Display Transcript

```markdown
## Transcript Extracted

**Source:** [URL or file]
**Language:** [detected]
**Length:** [chars] characters, [segments] segments

### Preview
[First 500 chars...]
```

### Step 4 — Analyze (if requested or default)

Apply 5 lenses:

#### 1. Topics (max 10)
- **Name**: 2-5 words
- **Depth**: introductory | intermediate | advanced
- **Summary**: 1-2 sentences

#### 2. Actionable Insights
- **What**: The insight
- **How**: 2-3 concrete steps
- **Difficulty**: easy | medium | hard

#### 3. Connections
- Internal links between topics
- External links to broader concepts
- Recurring patterns

#### 4. Key Quotes (max 7)
- Exact from transcript, never paraphrased
- With context

#### 5. Recommended Deep Dives
- What to search, why, suggested sources

### Output Template

```markdown
# Video Analysis: [Title]

**Source:** [URL/path]
**Language:** [lang]
**Length:** [count]

## Topics
### 1. [Name] `[depth]`
[Summary]

## Actionable Insights
### [Title]
**What:** [desc]
**How:** 1. [step] 2. [step] 3. [step]

## Connections
- [A] ↔ [B]: [how]

## Key Quotes
> "[exact]"
— [context]

## Deep Dives
1. **[Topic]** — [why + search terms]
```

## Multi-Video Mode

When multiple URLs/files:
1. Process each independently
2. Cross-analysis: common topics, contradictions, viewing order, combined insights

## Quality Rules

- Max 10 topics, prioritize by importance
- Specific > generic ("use cover crops to fix nitrogen" > "soil improvement")
- Actionable > descriptive
- Exact quotes only
- Analyze in same language as transcript
- **ALWAYS** show preview of transcript before analysis

## Prerequisites

- `hive` with deps (`cd hive && uv sync`)
- No API keys for YouTube transcripts
- `YOUTUBE_API_KEY` optional (metadata enrichment)
- `OPENAI_API_KEY` required for local video transcription (Whisper)
- `ffmpeg` required for local video files

## Deprecates

- `/extract_transcript` → use `/process_video <url>`
- `/video-analysis` → use `/process_video <url> --analyze` or just `/process_video <url>` (analyze is default)
