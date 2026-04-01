#!/usr/bin/env bash
# Gemini API handler for Hive.
# Generate content, grounded search, structured output.
set -euo pipefail

BASE_URL="https://generativelanguage.googleapis.com/v1beta"

# Load .env — resolve from script location (hive/scripts/ → hive/.env)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
elif [[ -f ".env" ]]; then
  set -a; source ".env"; set +a
fi

die() { echo "{\"success\":false,\"error\":\"$1\"}" >&2; exit 1; }

API_KEY="${GEMINI_API_KEY:-${GOOGLE_API_KEY:-}}"
[[ -n "$API_KEY" ]] || die "GEMINI_API_KEY or GOOGLE_API_KEY not set"

# --- Core API call ---
api_call() {
  local endpoint="$1" payload="$2"
  curl -sS --max-time 120 \
    -X POST "${BASE_URL}${endpoint}?key=${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# --- Commands ---

cmd_ask() {
  local query="" model="gemini-2.5-flash" system="" temperature=0.7 max_tokens=8192 json_mode=false grounding=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)       model="$2"; shift 2 ;;
      --system)      system="$2"; shift 2 ;;
      --temperature) temperature="$2"; shift 2 ;;
      --max-tokens)  max_tokens="$2"; shift 2 ;;
      --json)        json_mode=true; shift ;;
      --grounding)   grounding=true; shift ;;
      *)             query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: ask <query> [--model M] [--system S] [--temperature T] [--max-tokens N] [--json] [--grounding]"

  # Build contents
  local contents
  contents=$(jq -n --arg q "$query" '[{parts:[{text:$q}]}]')

  # Build payload
  local payload
  payload=$(jq -n \
    --argjson c "$contents" \
    --argjson t "$temperature" \
    --argjson mt "$max_tokens" \
    '{contents:$c, generationConfig:{temperature:$t, maxOutputTokens:$mt}}')

  # System instruction
  if [[ -n "$system" ]]; then
    payload=$(echo "$payload" | jq --arg s "$system" '.systemInstruction = {parts:[{text:$s}]}')
  fi

  # JSON mode
  if [[ "$json_mode" == "true" ]]; then
    payload=$(echo "$payload" | jq '.generationConfig.responseMimeType = "application/json"')
  fi

  # Google Search grounding
  if [[ "$grounding" == "true" ]]; then
    payload=$(echo "$payload" | jq '.tools = [{"google_search":{}}]')
  fi

  local result
  result=$(api_call "/models/${model}:generateContent" "$payload")

  # Check for error
  local error
  error=$(echo "$result" | jq -r '.error.message // empty')
  if [[ -n "$error" ]]; then
    echo "{\"success\":false,\"error\":\"$error\"}"
    return 1
  fi

  # Extract content
  local content
  content=$(echo "$result" | jq -r '.candidates[0].content.parts[0].text // ""')

  # Extract grounding metadata if present
  local grounding_meta
  grounding_meta=$(echo "$result" | jq '.candidates[0].groundingMetadata // null')

  jq -n \
    --arg c "$content" \
    --argjson r "$result" \
    --argjson g "$grounding_meta" \
    '{
      success: true,
      data: {
        content: $c,
        model: ($r.modelVersion // ""),
        usage: {
          input_tokens: ($r.usageMetadata.promptTokenCount // 0),
          output_tokens: ($r.usageMetadata.candidatesTokenCount // 0),
          total_tokens: ($r.usageMetadata.totalTokenCount // 0)
        }
      }
    } | if $g != null then .data.grounding = $g else . end'
}

cmd_search() {
  local query="" model="gemini-2.5-flash" max_tokens=4096

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)      model="$2"; shift 2 ;;
      --max-tokens) max_tokens="$2"; shift 2 ;;
      *)            query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: search <query> [--model M] [--max-tokens N]"

  # Grounded search — always enables google_search tool
  local payload
  payload=$(jq -n \
    --arg q "$query" \
    --argjson mt "$max_tokens" \
    '{
      contents: [{parts:[{text:$q}]}],
      tools: [{"google_search":{}}],
      generationConfig: {temperature:0.3, maxOutputTokens:$mt}
    }')

  local result
  result=$(api_call "/models/${model}:generateContent" "$payload")

  local error
  error=$(echo "$result" | jq -r '.error.message // empty')
  if [[ -n "$error" ]]; then
    echo "{\"success\":false,\"error\":\"$error\"}"
    return 1
  fi

  local content
  content=$(echo "$result" | jq -r '.candidates[0].content.parts[0].text // ""')

  local sources
  sources=$(echo "$result" | jq '[.candidates[0].groundingMetadata.groundingChunks[]?.web // empty]')

  jq -n \
    --arg c "$content" \
    --argjson s "$sources" \
    --argjson r "$result" \
    '{
      success: true,
      data: {
        content: $c,
        sources: $s,
        model: ($r.modelVersion // ""),
        usage: {
          input_tokens: ($r.usageMetadata.promptTokenCount // 0),
          output_tokens: ($r.usageMetadata.candidatesTokenCount // 0)
        }
      }
    }'
}

cmd_embed() {
  local input="" model="text-embedding-004"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model) model="$2"; shift 2 ;;
      *)       input="$1"; shift ;;
    esac
  done

  [[ -n "$input" ]] || die "Usage: embed <text> [--model M]"

  local payload
  payload=$(jq -n --arg t "$input" '{content:{parts:[{text:$t}]}}')

  local result
  result=$(api_call "/models/${model}:embedContent" "$payload")

  local error
  error=$(echo "$result" | jq -r '.error.message // empty')
  if [[ -n "$error" ]]; then
    echo "{\"success\":false,\"error\":\"$error\"}"
    return 1
  fi

  jq -n \
    --argjson r "$result" \
    '{
      success: true,
      data: {
        embedding: ($r.embedding.values // [])
      }
    }'
}

# --- Main ---
command="${1:-}"
shift || die "Usage: gemini_handler.sh <ask|search|embed> <query> [options]"

case "$command" in
  ask)    cmd_ask "$@" ;;
  search) cmd_search "$@" ;;
  embed)  cmd_embed "$@" ;;
  *)      die "Unknown command: $command. Use: ask, search, embed" ;;
esac
