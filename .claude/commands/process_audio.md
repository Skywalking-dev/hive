---
description: Process audio files with conversion and OpenAI Whisper transcription
---

# /process_audio Command

Process audio files: convert formats and/or transcribe using OpenAI Whisper API.

## Usage

```bash
/process_audio <file_path> [--convert] [--transcribe] [--format mp3|wav|m4a]
```

**Arguments:**
- `file_path` (required): Path to audio file
- `--convert`: Convert to specified format (default: mp3)
- `--transcribe`: Transcribe audio to text using Whisper API
- `--format`: Output format for conversion (mp3, wav, m4a)

**Examples:**

```bash
# Convert + transcribe
/process_audio /Downloads/meeting.wav --convert --transcribe

# Only transcribe
/process_audio /Downloads/audio.mp3 --transcribe

# Convert to specific format
/process_audio /Downloads/recording.m4a --convert --format wav
```

## Execution Instructions (for Mentat)

When user invokes `/process_audio`:

### Step 1: Validate Input

```
1. Check file exists at specified path
2. Verify file is readable
3. Check file extension is audio format
```

### Step 2: Validate Dependencies

```
4. If --convert: verify ffmpeg installed
5. If --transcribe: verify OPENAI_API_KEY in .env
6. Alert user if missing dependencies
```

### Step 3: Execute Script

```
7. Run: ./scripts/process_audio.sh [file_path] [flags]
8. Monitor output for errors
9. Capture output paths
```

### Step 4: Report Results

```
10. Show converted file path (if --convert)
11. Show transcript file path + preview (if --transcribe)
12. Display metadata (duration, size)
13. Provide next steps or suggestions
```

## Output Format (for User)

```markdown
## Audio Processing Results

**Input:** [original file path]

### Conversion
✓ Format: [format]
✓ Output: [output_path]
  Duration: [seconds]s | Size: [size]

### Transcription
✓ Transcript: [transcript_path]
  Preview:
  [first 3 lines of transcript]

**Output Directory:** /tmp/audio_processed
```

## Error Handling

**Missing ffmpeg:**

```
Error: ffmpeg no instalado
Instalar: brew install ffmpeg
```

**Missing API key:**

```
Error: OPENAI_API_KEY no configurada
Agregar a .env:
OPENAI_API_KEY=sk-...
```

**File too large (>25MB):**

```
Warning: Archivo >25MB
Whisper API limit: 25MB
Sugerencia: split archivo o usar --convert para comprimir primero
```

## Dependencies

- **ffmpeg** (conversion): `brew install ffmpeg`
- **OpenAI API key** (transcription): Add `OPENAI_API_KEY` to `.env`
- **Script**: `scripts/process_audio.sh`

## Related

- Skill: `.claude/skills/process_audio.md`
- Script: `scripts/process_audio.sh`

---
description: Process audio files (convert + transcribe)
---

# /process_audio Command

Process audio files: convert formats and/or transcribe using OpenAI Whisper API.

## Usage

```bash
/process_audio <file_path> [--convert] [--transcribe] [--format mp3|wav|m4a]
```

**Arguments:**
- `file_path` (required): Path to audio file
- `--convert`: Convert to specified format (default: mp3)
- `--transcribe`: Transcribe audio to text using Whisper API
- `--format`: Output format for conversion (mp3, wav, m4a)

**Examples:**
```bash
# Convert + transcribe
/process_audio /Downloads/meeting.wav --convert --transcribe

# Only transcribe
/process_audio /Downloads/audio.mp3 --transcribe

# Convert to specific format
/process_audio /Downloads/recording.m4a --convert --format wav
```

## Execution Instructions (for Mentat)

When user invokes `/process_audio`:

### Step 1: Validate Input
```
1. Check file exists at specified path
2. Verify file is readable
3. Check file extension is audio format
```

### Step 2: Validate Dependencies
```
4. If --convert: verify ffmpeg installed
5. If --transcribe: verify OPENAI_API_KEY in .env
6. Alert user if missing dependencies
```

### Step 3: Execute Script
```
7. Run: ./scripts/process_audio.sh [file_path] [flags]
8. Monitor output for errors
9. Capture output paths
```

### Step 4: Report Results
```
10. Show converted file path (if --convert)
11. Show transcript file path + preview (if --transcribe)
12. Display metadata (duration, size)
13. Provide next steps or suggestions
```

## Output Format (for User)

```markdown
## Audio Processing Results

**Input:** [original file path]

### Conversion
✓ Format: [format]
✓ Output: [output_path]
  Duration: [seconds]s | Size: [size]

### Transcription
✓ Transcript: [transcript_path]
  Preview:
  [first 3 lines of transcript]

**Output Directory:** /tmp/audio_processed
```

## Error Handling

**Missing ffmpeg:**
```
Error: ffmpeg no instalado
Instalar: brew install ffmpeg
```

**Missing API key:**
```
Error: OPENAI_API_KEY no configurada
Agregar a .env:
OPENAI_API_KEY=sk-...
```

**File too large (>25MB):**
```
Warning: Archivo >25MB
Whisper API limit: 25MB
Sugerencia: split archivo o usar --convert para comprimir primero
```

## Dependencies

- **ffmpeg** (conversion): `brew install ffmpeg`
- **OpenAI API key** (transcription): Add `OPENAI_API_KEY` to `.env`
- **Script**: `scripts/process_audio.sh`

## Related

- Skill: `.claude/skills/process_audio.md`
- Script: `scripts/process_audio.sh`
