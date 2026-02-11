#!/bin/bash
set -euo pipefail

# Load env
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
if [ -f "$PROJECT_ROOT/.env" ]; then
  set -a; source "$PROJECT_ROOT/.env"; set +a
fi

OUTPUT_DIR="${AUDIO_OUTPUT_DIR:-/tmp/audio_processed}"
mkdir -p "$OUTPUT_DIR"

CONVERT=false
TRANSCRIBE=false
FORMAT="mp3"
FILES=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --convert) CONVERT=true; shift ;;
    --transcribe) TRANSCRIBE=true; shift ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) FILES+=("$1"); shift ;;
  esac
done

if [ ${#FILES[@]} -eq 0 ]; then
  echo "Usage: process_audio.sh <file(s)> [--convert] [--transcribe] [--format mp3|wav|m4a]"
  exit 1
fi

# Default: transcribe if no flags
if ! $CONVERT && ! $TRANSCRIBE; then
  TRANSCRIBE=true
fi

for INPUT_FILE in "${FILES[@]}"; do
  if [ ! -f "$INPUT_FILE" ]; then
    echo "SKIP: $INPUT_FILE (not found)"
    continue
  fi

  BASENAME=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//')
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  UNIQUE="${BASENAME}_${TIMESTAMP}"

  echo "--- Processing: $(basename "$INPUT_FILE")"

  # Get duration
  DURATION=$(ffmpeg -i "$INPUT_FILE" 2>&1 | grep Duration | awk '{print $2}' | tr -d ',') || DURATION="unknown"
  echo "  Duration: $DURATION"

  PROCESS_FILE="$INPUT_FILE"

  if $CONVERT; then
    OUT_FILE="$OUTPUT_DIR/${UNIQUE}.${FORMAT}"
    echo "  Converting -> $FORMAT (128kbps)"
    ffmpeg -i "$INPUT_FILE" -ab 128k -y -loglevel error "$OUT_FILE"
    SIZE=$(du -h "$OUT_FILE" | awk '{print $1}')
    echo "  Converted: $OUT_FILE ($SIZE)"
    PROCESS_FILE="$OUT_FILE"
  fi

  if $TRANSCRIBE; then
    if [ -z "${OPENAI_API_KEY:-}" ]; then
      echo "  ERROR: OPENAI_API_KEY not set"
      continue
    fi

    # Compress to mp3 for API if not already converted
    if ! $CONVERT; then
      TEMP_FILE="$OUTPUT_DIR/${UNIQUE}_temp.mp3"
      ffmpeg -i "$INPUT_FILE" -ab 128k -y -loglevel error "$TEMP_FILE"
      PROCESS_FILE="$TEMP_FILE"
    fi

    # Check size (<25MB)
    FILE_SIZE=$(stat -f%z "$PROCESS_FILE" 2>/dev/null || stat -c%s "$PROCESS_FILE" 2>/dev/null)
    if [ "$FILE_SIZE" -gt 26214400 ]; then
      echo "  ERROR: File >25MB ($FILE_SIZE bytes). Split needed."
      continue
    fi

    TRANSCRIPT_FILE="$OUTPUT_DIR/${UNIQUE}.txt"
    echo "  Transcribing via Whisper..."

    RESPONSE=$(curl -s -X POST "https://api.openai.com/v1/audio/transcriptions" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -F "file=@$PROCESS_FILE" \
      -F "model=whisper-1" \
      -F "language=es" \
      -F "response_format=text")

    echo "$RESPONSE" > "$TRANSCRIPT_FILE"

    # Cleanup temp
    if ! $CONVERT && [ -f "${OUTPUT_DIR}/${UNIQUE}_temp.mp3" ]; then
      rm "${OUTPUT_DIR}/${UNIQUE}_temp.mp3"
    fi

    echo "  Transcript: $TRANSCRIPT_FILE"
    echo "  ---"
    echo "$RESPONSE" | head -5
    echo "  ---"
  fi

  echo ""
done

echo "Done. Output: $OUTPUT_DIR"
