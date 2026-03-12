---
description: Analyze video transcript to extract topics, insights, and connections
argument-hint: <text, file path, or YouTube URL>
---

# /analyze_video Command

Analyze video transcripts to extract structured knowledge using the `video-analysis` skill.

## Usage

```bash
/analyze_video <text, file path, or YouTube URL>
```

## Execution Instructions

### Step 1: Determine Input Type

1. **YouTube URL** → Extract video ID, run `cd hive && uv run python scripts/transcript_handler.py extract <video_id>`, parse JSON, use `data.total_text`
2. **File path** → Read file. If JSON from handler, extract `data.total_text`. If plain text, use directly.
3. **Pasted text / no argument** → Use text in conversation context. If no transcript available, ask user to provide one or use `/extract_transcript` first.

### Step 2: Analyze

Apply the `video-analysis` skill's 5-lens framework:
1. Topics (max 10, with depth level)
2. Actionable insights (with concrete steps)
3. Connections (internal + external)
4. Key quotes (verbatim, max 7)
5. Recommended deep dives

### Step 3: Output

Use the structured markdown template from the `video-analysis` skill. Match output language to transcript language.

### Step 4: Next Steps

Suggest:
- Further analysis on specific topics
- Cross-reference with other videos (`/analyze_video` with multiple URLs)
- Save analysis to file if requested

## Examples

```bash
# From YouTube URL (extracts + analyzes)
/analyze_video https://youtube.com/watch?v=U36BocbXJs8

# From file
/analyze_video /path/to/transcript.json

# After /extract_transcript (uses context)
/analyze_video

# Multiple videos comparison
/analyze_video
Compare these videos:
- https://youtube.com/watch?v=VIDEO1
- https://youtube.com/watch?v=VIDEO2
```
