# /extract_transcript Command

Extract video transcripts directly from YouTube API (free, fast, no downloads required).

## Usage

```bash
/extract_transcript <video_url_or_id> [--languages es,en] [--save]
```

**Arguments:**
- `video_url_or_id` (required): YouTube URL or video ID
- `--languages`: Language priority (default: es,en)
- `--save`: Save to cache (default: true)

**Examples:**

```bash
# From URL
/extract_transcript https://youtube.com/watch?v=U36BocbXJs8

# From video ID
/extract_transcript U36BocbXJs8

# Specific language priority
/extract_transcript U36BocbXJs8 --languages en,es

# Just extract without saving
/extract_transcript U36BocbXJs8 --save false
```

## Execution Instructions (for Mentat)

When user invokes `/extract_transcript`:

### Step 1: Parse Input

```
1. Extract video ID from URL or use provided ID
2. Parse language preferences
3. Parse save flag
```

### Step 2: Extract Transcript

```
4. cd projects/sw_permacultura_library
5. Run Python script to extract transcript
6. Use src/extractors/transcript.py::extract_transcript()
7. Handle errors gracefully
```

### Step 3: Display Results

```
8. Show transcript metadata (language, length, segments)
9. Show preview (first 500 characters)
10. If saved: show cache location
11. Suggest next steps (analyze, generate PDF)
```

## Output Format (for User)

```markdown
## Transcript Extracted

**Video ID:** [video_id]
**URL:** https://youtube.com/watch?v=[video_id]

### Details
- Language: [language_name] ([auto-generated/manual])
- Code: [language_code]
- Length: [X] characters
- Segments: [N] segments

### Preview
[First 500 characters of transcript...]

### Saved
✓ Cache: projects/sw_permacultura_library/data/cache/transcripts/[video_id].json

### Next Steps
1. Analyze topics: cd projects/sw_permacultura_library && uv run python scripts/2_analyze_topics.py --video-id [video_id]
2. Generate PDF: uv run python scripts/3_generate_pdfs.py --video-id [video_id]
```

## Error Handling

**No transcript available:**

```
✗ No transcript available for video: [video_id]

Possible reasons:
- Video has no captions/subtitles
- Video is private
- Transcripts disabled by uploader

Try:
- Check if video has captions in YouTube
- Try different video
```

**Invalid video ID:**

```
✗ Invalid video ID or URL: [input]

Valid formats:
- Full URL: https://youtube.com/watch?v=VIDEO_ID
- Short URL: https://youtu.be/VIDEO_ID
- Video ID: VIDEO_ID (11 characters)
```

**API error:**

```
✗ YouTube API error: [error_message]

This is usually temporary. Try:
- Wait a few seconds and retry
- Check internet connection
- Verify video is accessible
```

## Benefits vs Video Download

| Aspect | YouTube API | Video Download |
|--------|-------------|----------------|
| **Time** | 2-5 seconds | 10+ minutes |
| **Bandwidth** | <1 MB | 1-3 GB |
| **Cost** | FREE | $0.36+ (Whisper) |
| **Disk** | ~100 KB | 3+ GB |
| **Quality** | Native captions | Variable |

## Use Cases

### 1. Quick Transcript Extraction

```bash
/extract_transcript https://youtube.com/watch?v=VIDEO_ID
```

**Use for:**
- Getting transcript for analysis
- Creating content from video
- Research and note-taking

### 2. Batch Extraction

```bash
# Create list of video IDs
VIDEO_IDS="
U36BocbXJs8
abc123def45
xyz789uvw12
"

for id in $VIDEO_IDS; do
  /extract_transcript $id
done
```

### 3. Permacultura Library Integration

```bash
# Extract transcript
/extract_transcript VIDEO_ID

# Analyze with AI
cd projects/sw_permacultura_library
uv run python scripts/2_analyze_topics.py --video-id VIDEO_ID

# Generate PDF
uv run python scripts/3_generate_pdfs.py --video-id VIDEO_ID
```

## Technical Details

**Implementation:**
- Uses `youtube-transcript-api` library
- Accesses YouTube's native caption/subtitle data
- No authentication required
- No API quota limits for transcript access
- Supports auto-generated and manual captions

**Language Support:**
- Auto-detects available languages
- Tries languages in priority order
- Falls back if preferred language unavailable
- Supports 100+ languages

**Cache System:**
- Saves to `projects/sw_permacultura_library/data/cache/transcripts/`
- Format: `{video_id}.json`
- Prevents redundant API calls
- Includes metadata and timestamps

## Dependencies

- **youtube-transcript-api** (already installed in sw_permacultura_library)
- **Python 3.13+** (via uv in sw_permacultura_library)
- No API keys required
- No OAuth required

## Integration with Existing Tools

**sw_permacultura_library pipeline:**
```
/extract_transcript VIDEO_ID
    ↓
data/cache/transcripts/{video_id}.json
    ↓
scripts/2_analyze_topics.py (AI analysis)
    ↓
scripts/3_generate_pdfs.py (PDF generation)
```

**Standalone usage:**
```
/extract_transcript VIDEO_ID
    ↓
Read cached JSON directly
    ↓
Process with custom tools
```

## Limitations

- Only works for videos with available captions/subtitles
- Cannot extract from private videos
- Cannot extract if uploader disabled transcripts
- Quality depends on YouTube's caption quality (auto-generated may have errors)

## Future Enhancements

- Auto-translation to multiple languages
- Timestamp navigation
- Speaker diarization (if available)
- Export to SRT/VTT formats
- Integration with Claude for instant analysis

## Related

- Library: `projects/sw_permacultura_library/`
- Extractor: `projects/sw_permacultura_library/src/extractors/transcript.py`
- Cache: `projects/sw_permacultura_library/src/utils/cache.py`
- Skill: `.claude/skills/extract_transcript.md`

---
description: Extract video transcripts from YouTube API (free, fast, no downloads)
---

