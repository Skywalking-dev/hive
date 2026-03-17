---
description: Extract video transcripts from YouTube API (free, fast, no downloads)
argument-hint: <video_url_or_id> [--languages es,en]
---

# Extract YouTube Transcript

Extract transcripts from YouTube videos via `youtube-transcript-api`. Free, fast (~3s), no video download.

## When to Use

- User provides a YouTube URL or video ID
- Need transcript for analysis, content creation, research
- Batch processing video content

## When NOT to Use

- Video has no captions/subtitles
- Need visual analysis or audio processing
- Video is private or transcripts disabled

## Execution

### Step 1: Parse Input

Extract video ID from input. Supported formats:
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`
- Raw `VIDEO_ID` (11 chars)

### Step 2: Run Handler

```bash
cd hive && uv run python scripts/transcript_handler.py extract <VIDEO_ID> --languages <LANGS>
```

Default languages: `es,en`. Parse JSON output, check `success` field.

### Step 3: Display Results

```markdown
## Transcript Extracted

**Video:** [title] ([video_id])
**URL:** https://youtube.com/watch?v=[video_id]

### Details
- Language: [language] ([language_code])
- Length: [char_count] characters
- Segments: [segment_count]

### Preview
[First 500 characters of total_text...]

### Next Steps
1. Analyze: `/analyze_video` (uses transcript already in context)
2. Full text available in the extraction output above
```

## Other Commands

```bash
# Video metadata only (requires YOUTUBE_API_KEY)
cd hive && uv run python scripts/transcript_handler.py metadata <VIDEO_ID>

# List channel videos (requires YOUTUBE_API_KEY)
cd hive && uv run python scripts/transcript_handler.py channel <CHANNEL_ID> --max 20
```

## Output Structure

```json
{
  "success": true,
  "data": {
    "video_id": "U36BocbXJs8",
    "title": "Video Title",
    "language": "Spanish",
    "language_code": "es",
    "total_text": "Full transcript concatenated...",
    "char_count": 12345,
    "segment_count": 150,
    "segments": [{"text": "...", "start": 0.0, "duration": 2.5}]
  }
}
```

## Error Handling

- **No transcript available** → video has no captions, try different video
- **TranscriptsDisabled** → uploader disabled, no workaround
- **CouldNotRetrieveTranscript** → transient, automatic retry with backoff (3 attempts)
- **Invalid video ID** → check URL format, verify video exists

## Prerequisites

- `hive` project with deps installed (`cd hive && uv sync`)
- No API keys required for transcripts
- `YOUTUBE_API_KEY` optional (metadata enrichment)

## Related

- Handler: `hive/scripts/transcript_handler.py`
- Analysis: `/analyze_video`
