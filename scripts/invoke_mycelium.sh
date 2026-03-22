#!/usr/bin/env bash
# Invoke Mycelium (Gemini 2.5) for PRD and Implementation Plan creation.
# Usage: invoke_mycelium.sh <file_path> [doc_type]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_ROOT="$(dirname "$HIVE_DIR")"

# Load .env
if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
fi

die() { echo -e "\033[0;31m$1\033[0m" >&2; exit 1; }
info() { echo -e "\033[1;33m$1\033[0m"; }
ok() { echo -e "\033[0;32m$1\033[0m"; }

# Args
FILE_PATH="${1:-}"
DOC_TYPE="${2:-document}"

[[ -n "$FILE_PATH" ]] || die "Usage: invoke_mycelium.sh <file_path> [doc_type]"
[[ -f "$FILE_PATH" ]] || die "File not found: $FILE_PATH"

# API key
API_KEY="${GEMINI_API_KEY:-${GOOGLE_API_KEY:-}}"
[[ -n "$API_KEY" ]] || die "No API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in hive/.env"

# Context file
GEMINI_MD="${WORKSPACE_ROOT}/GEMINI.md"
[[ -f "$GEMINI_MD" ]] || die "GEMINI.md not found at ${GEMINI_MD}"

# Model
MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"

# Output file
OUTPUT_FILE="$(dirname "$FILE_PATH")/$(basename "$FILE_PATH")-mycelium-output.md"

info "[Mycelium] Reading document: ${FILE_PATH}"

DOCUMENT_CONTENT=$(cat "$FILE_PATH")
GEMINI_CONTEXT=$(cat "$GEMINI_MD")

# Build prompt
PROMPT=$(cat <<EOPROMPT
Your name, role, personality, and operational guidelines are defined in GEMINI.md below:

---
${GEMINI_CONTEXT}
---

TASK: Analyze the following ${DOC_TYPE} and generate a comprehensive PRD and Implementation Plan.

INPUT DOCUMENT:
---
${DOCUMENT_CONTENT}
---

INSTRUCTIONS:
1. Analyze this document from your perspective as Mycelium (Gemini 2.5).
2. Your goal is to produce a detailed PRD (Product Requirements Document) and Implementation Plan.
3. Follow the structure defined in GEMINI.md for Mycelium's outputs or the "Project Skeleton" section.
4. Focus on:
   - Detailed system architecture
   - Clear success metrics
   - Step-by-step implementation plan
   - Agent delegation (which parts go to Aurora, Kokoro, Pixel, Flux, etc.)
   - Risk assessment

5. Be thorough and structured.

OUTPUT: Generate a complete markdown document.
Do NOT include any preamble or meta-commentary. Start directly with the markdown document.
EOPROMPT
)

info "[Mycelium] Invoking Gemini API (model: ${MODEL})..."

# Gemini API call
PAYLOAD=$(jq -n \
  --arg model "$MODEL" \
  --arg prompt "$PROMPT" \
  '{
    contents: [{parts: [{text: $prompt}]}],
    generationConfig: {temperature: 0.7, maxOutputTokens: 8192}
  }')

RESPONSE=$(curl -sS --max-time 120 \
  "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Extract text from response
OUTPUT_TEXT=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].text // empty')

if [[ -z "$OUTPUT_TEXT" ]]; then
  ERROR=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
  die "[Mycelium] Error: ${ERROR}"
fi

echo "$OUTPUT_TEXT" > "$OUTPUT_FILE"

ok "[Mycelium] Output generated: ${OUTPUT_FILE}"
ok "[Mycelium] Analysis complete"
echo "$OUTPUT_FILE"
