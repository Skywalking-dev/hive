# Skill: Extract YouTube Transcript

## Overview

Extract video transcripts directly from YouTube API without downloading video files. Fast, free, and efficient way to get text content from YouTube videos for analysis, documentation, or content creation.

## When to Use

- User provides a YouTube URL
- Need transcript for analysis
- Creating content from video
- Research and note-taking
- Batch processing video content
- Integration with sw_permacultura_library

## When NOT to Use

- Video has no captions/subtitles available
- Need visual analysis (frames, screenshots)
- Need audio without transcript
- Video is private or restricted

## Prerequisites

- `sw_permacultura_library` project available
- `youtube-transcript-api` installed (already in project)
- Internet connection
- No API keys required ✅

## Usage Pattern

```bash
# Via command
/extract_transcript <video_url_or_id>

# Via direct Python invocation
cd projects/sw_permacultura_library
uv run python -c "from src.extractors.transcript import extract_transcript; print(extract_transcript('VIDEO_ID'))"
```

## Common Workflows

### 1. Single Video Extraction

**Use case:** Get transcript from one YouTube video

```bash
/extract_transcript https://youtube.com/watch?v=U36BocbXJs8
```

**Output:**
- Transcript text
- Metadata (language, length)
- Cached JSON file
- Next steps suggestions

**Time:** 2-5 seconds
**Cost:** FREE

### 2. Batch Video Processing

**Use case:** Extract transcripts from multiple videos

```bash
# List of video IDs
VIDEOS=(
    "U36BocbXJs8"
    "abc123def45"
    "xyz789uvw12"
)

for video in "${VIDEOS[@]}"; do
    /extract_transcript "$video"
    sleep 1  # Be nice to API
done
```

**Output:**
- All transcripts cached
- Ready for batch analysis

### 3. Permacultura Library Integration

**Use case:** Full pipeline from video to PDF

```bash
# Step 1: Extract transcript
/extract_transcript VIDEO_ID

# Step 2: Analyze topics with AI
cd projects/sw_permacultura_library
uv run python scripts/2_analyze_topics.py --video-id VIDEO_ID

# Step 3: Generate PDF
uv run python scripts/3_generate_pdfs.py --video-id VIDEO_ID
```

**Complete workflow** in 3 steps.

### 4. Channel Processing

**Use case:** Extract transcripts from entire channel

```bash
# First: Get channel video IDs (existing tool)
cd projects/sw_permacultura_library
uv run python scripts/1_extract_channel.py --channel-id CHANNEL_ID --max-videos 50

# Then: Extract transcripts (automatic via existing script)
# The extract_channel.py already uses YouTube API for transcripts
```

### 5. Quick Analysis with Claude

**Use case:** Immediate insights from video

```bash
# Extract transcript
/extract_transcript VIDEO_ID

# Read cached transcript
cat projects/sw_permacultura_library/data/cache/transcripts/VIDEO_ID.json

# Ask Claude to analyze
"Summarize this transcript in bullet points with key takeaways"
```

## Video ID Extraction

**Supported formats:**

```bash
# Full URL
https://youtube.com/watch?v=U36BocbXJs8

# Short URL
https://youtu.be/U36BocbXJs8

# Just ID
U36BocbXJs8

# Embed URL
https://youtube.com/embed/U36BocbXJs8
```

All extract to: `U36BocbXJs8`

## Language Handling

**Default priority:** `["es", "en"]`

YouTube API tries languages in order:
1. Spanish (if available)
2. English (if Spanish not available)
3. Auto-generated Spanish
4. Auto-generated English

**Custom priority:**

```bash
/extract_transcript VIDEO_ID --languages en,es,fr
```

**Auto-generated vs Manual:**
- Manual captions: More accurate, punctuated
- Auto-generated: May have errors, less punctuation
- Both work fine for most use cases

## Output Structure

**Cached JSON format:**

```json
{
  "video_id": "U36BocbXJs8",
  "transcript": [
    {
      "text": "Lo que vas a ver hoy...",
      "start": 0.0,
      "duration": 2.5
    }
  ],
  "total_text": "Full transcript concatenated...",
  "language": "Spanish (auto-generated)",
  "language_code": "es",
  "metadata": {
    "title": "Video Title",
    "description": "...",
    "published_at": "2024-01-01T00:00:00Z"
  }
}
```

**Cache location:**
```
projects/sw_permacultura_library/data/cache/transcripts/
└── {video_id}.json
```

## Performance Characteristics

**Speed:**
- 2-5 seconds typical
- No dependency on video length
- Only limited by network speed

**Bandwidth:**
- <1 MB per transcript
- Usually 50-200 KB

**Reliability:**
- Very high (YouTube native API)
- No rate limits for transcript access
- No authentication required

## Error Handling

**Common errors and solutions:**

```
No transcript available
→ Video has no captions
→ Check video on YouTube for caption availability
→ Try different video

CouldNotRetrieveTranscript (transient)
→ Temporary YouTube API issue
→ Retry after a few seconds
→ Usually resolves automatically

TranscriptsDisabled
→ Uploader disabled transcripts
→ No workaround available
→ Find different source

Invalid video ID
→ Check URL format
→ Verify video exists
→ Try copy-paste URL again
```

## Comparison with Alternatives

| Method | Time | Bandwidth | Cost | Accuracy |
|--------|------|-----------|------|----------|
| **YouTube API** | 2-5s | <1MB | FREE | High* |
| Whisper API | 10+ min | 1-3GB | $0.36+ | Very High |
| Manual transcription | Hours | 0 | Time | Perfect |

*Depends on caption quality (auto vs manual)

## Integration Patterns

### With sw_permacultura_library

```python
# Already integrated in existing scripts
# scripts/1_extract_channel.py uses this automatically
# scripts/1_extract_videos_basic.py uses this
```

### With Custom Processing

```python
# Direct import
from src.extractors.transcript import extract_transcript

transcript = extract_transcript('VIDEO_ID', languages=['es', 'en'])
if transcript:
    text = transcript['total_text']
    # Process as needed
```

### With n8n Workflow

```
Trigger: New video in playlist
    ↓
HTTP Request: Extract video ID
    ↓
Execute: /extract_transcript {video_id}
    ↓
Read: Cached JSON
    ↓
Process: AI analysis, store in DB, etc.
```

## Best Practices

### 1. Check Availability First

Not all videos have transcripts. Check before batch processing:

```bash
# Test with one video first
/extract_transcript VIDEO_ID

# If successful, proceed with batch
```

### 2. Use Caching Effectively

Transcript extraction creates cache automatically:

```bash
# First time: extracts from API
/extract_transcript VIDEO_ID

# Second time: reads from cache (instant)
/extract_transcript VIDEO_ID
```

### 3. Respect API (Though No Limits)

Even though there are no rate limits, be reasonable:

```bash
# Add small delays in batch processing
for video in "${VIDEOS[@]}"; do
    /extract_transcript "$video"
    sleep 1
done
```

### 4. Verify Language

Auto-generated transcripts may have errors:

```bash
# After extraction, check language
cat data/cache/transcripts/VIDEO_ID.json | jq '.language'

# If "auto-generated", expect some errors
# If manual, expect high accuracy
```

### 5. Handle Errors Gracefully

```bash
# In batch processing, continue on error
for video in "${VIDEOS[@]}"; do
    /extract_transcript "$video" || echo "Failed: $video"
done
```

## Advanced Usage

### Parallel Extraction

```bash
# Process multiple videos in parallel
VIDEO_IDS=("vid1" "vid2" "vid3")

for id in "${VIDEO_IDS[@]}"; do
    /extract_transcript "$id" &
done
wait

echo "All transcripts extracted"
```

### Custom Language Priority

```bash
# For multilingual channels
/extract_transcript VIDEO_ID --languages fr,en,es

# For English-only
/extract_transcript VIDEO_ID --languages en
```

### Extract and Analyze in One Go

```bash
# Chain commands
/extract_transcript VIDEO_ID && \
cd projects/sw_permacultura_library && \
uv run python scripts/2_analyze_topics.py --video-id VIDEO_ID
```

## Troubleshooting

**"No transcript available"**
- Check video on YouTube
- Look for CC button
- Try different video

**"Could not fetch metadata"**
- YOUTUBE_API_KEY not required for transcripts
- Metadata fetch may fail but transcript still works
- Non-critical warning

**Slow extraction**
- Check internet connection
- YouTube API may be slow
- Usually resolves in retry

**Wrong language extracted**
- Specify --languages flag
- Check available languages on YouTube
- Auto-generated may be only option

## Limitations

- Only text content (no visual analysis)
- Quality depends on YouTube captions
- Cannot access private videos
- Cannot extract if transcripts disabled
- Auto-generated may have errors

## Future Enhancements

- Auto-translation to multiple languages
- Summary generation (Claude integration)
- Timestamp-based navigation
- Export to SRT/VTT formats
- Speaker identification (when available)

## Related

- Command: `.claude/commands/extract_transcript.md`
- Library: `projects/sw_permacultura_library/`
- Extractor: `src/extractors/transcript.py`
- Cache: `src/utils/cache.py`
- Analyzer: `scripts/2_analyze_topics.py`
- PDF Generator: `scripts/3_generate_pdfs.py`

