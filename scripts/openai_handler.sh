#!/usr/bin/env bash
# OpenAI API handler for Hive.
# Chat completions, responses API, embeddings.
set -euo pipefail

BASE_URL="https://api.openai.com"

# Load .env — resolve from script location (hive/scripts/ → hive/.env)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
elif [[ -f ".env" ]]; then
  set -a; source ".env"; set +a
fi

die() { echo "{\"success\":false,\"error\":\"$1\"}" >&2; exit 1; }

[[ -n "${OPENAI_API_KEY:-}" ]] || die "OPENAI_API_KEY not set"

# --- Core API call ---
api_call() {
  local endpoint="$1" payload="$2"
  curl -sS --max-time 120 \
    -X POST "${BASE_URL}${endpoint}" \
    -H "Authorization: Bearer ${OPENAI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# --- Commands ---

cmd_ask() {
  local query="" model="gpt-4.1" system="" temperature=0.7 max_tokens="" stream=false json_mode=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)       model="$2"; shift 2 ;;
      --system)      system="$2"; shift 2 ;;
      --temperature) temperature="$2"; shift 2 ;;
      --max-tokens)  max_tokens="$2"; shift 2 ;;
      --json)        json_mode=true; shift ;;
      --stream)      stream=true; shift ;;
      *)             query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: ask <query> [--model M] [--system S] [--temperature T] [--max-tokens N] [--json] [--stream]"

  # Build messages array
  local messages="[]"
  if [[ -n "$system" ]]; then
    messages=$(jq -n --arg s "$system" '[{"role":"system","content":$s}]')
  fi
  messages=$(echo "$messages" | jq --arg q "$query" '. + [{"role":"user","content":$q}]')

  # Build payload
  local payload
  payload=$(jq -n --arg m "$model" --argjson msgs "$messages" --argjson t "$temperature" \
    '{model:$m, messages:$msgs, temperature:$t}')

  if [[ -n "$max_tokens" ]]; then
    payload=$(echo "$payload" | jq --argjson mt "$max_tokens" '.max_tokens = $mt')
  fi
  if [[ "$json_mode" == "true" ]]; then
    payload=$(echo "$payload" | jq '.response_format = {type:"json_object"}')
  fi
  if [[ "$stream" == "true" ]]; then
    payload=$(echo "$payload" | jq '.stream = true')
    curl -sS --max-time 120 -N \
      -X POST "${BASE_URL}/v1/chat/completions" \
      -H "Authorization: Bearer ${OPENAI_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "$payload" | while IFS= read -r line; do
        line="${line#data: }"
        [[ "$line" == "[DONE]" ]] && break
        [[ -z "$line" ]] && continue
        echo "$line" | jq -r '.choices[0].delta.content // empty' 2>/dev/null | tr -d '\n'
      done
    echo
    return
  fi

  local result
  result=$(api_call "/v1/chat/completions" "$payload")

  if echo "$result" | jq -e '.error' &>/dev/null 2>&1; then
    echo "$result"
    return 1
  fi

  jq -n \
    --argjson r "$result" \
    '{
      success: true,
      data: {
        content: ($r.choices[0].message.content // ""),
        model: ($r.model // ""),
        usage: ($r.usage // {})
      }
    }'
}

cmd_responses() {
  local query="" model="gpt-4.1" instructions="" tools="" max_tokens="" reasoning="" stream=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)        model="$2"; shift 2 ;;
      --instructions) instructions="$2"; shift 2 ;;
      --tools)        tools="$2"; shift 2 ;;
      --max-tokens)   max_tokens="$2"; shift 2 ;;
      --reasoning)    reasoning="$2"; shift 2 ;;
      --stream)       stream=true; shift ;;
      *)              query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: responses <query> [--model M] [--instructions S] [--tools T] [--max-tokens N] [--reasoning R] [--stream]"

  # Build payload
  local payload
  payload=$(jq -n --arg m "$model" --arg q "$query" '{model:$m, input:$q}')

  if [[ -n "$instructions" ]]; then
    payload=$(echo "$payload" | jq --arg i "$instructions" '.instructions = $i')
  fi
  if [[ -n "$tools" ]]; then
    local tools_json
    tools_json=$(echo "$tools" | jq -R 'split(",") | map({type:.})')
    payload=$(echo "$payload" | jq --argjson t "$tools_json" '.tools = $t')
  fi
  if [[ -n "$max_tokens" ]]; then
    payload=$(echo "$payload" | jq --argjson mt "$max_tokens" '.max_output_tokens = $mt')
  fi
  if [[ -n "$reasoning" ]]; then
    payload=$(echo "$payload" | jq --arg r "$reasoning" '.reasoning = {effort:$r}')
  fi
  if [[ "$stream" == "true" ]]; then
    payload=$(echo "$payload" | jq '.stream = true')
    curl -sS --max-time 120 -N \
      -X POST "${BASE_URL}/v1/responses" \
      -H "Authorization: Bearer ${OPENAI_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "$payload" | while IFS= read -r line; do
        line="${line#data: }"
        [[ "$line" == "[DONE]" ]] && break
        [[ -z "$line" ]] && continue
        echo "$line" | jq -r '.delta.text // empty' 2>/dev/null | tr -d '\n'
      done
    echo
    return
  fi

  local result
  result=$(api_call "/v1/responses" "$payload")

  if echo "$result" | jq -e '.error' &>/dev/null 2>&1; then
    echo "$result"
    return 1
  fi

  local content
  content=$(echo "$result" | jq -r '
    .output_text // (
      [.output[]? | select(.type=="message") | .content[]? | select(.type=="output_text") | .text] | join("")
    ) // ""
  ')

  jq -n \
    --arg c "$content" \
    --argjson r "$result" \
    '{
      success: true,
      data: {
        content: $c,
        model: ($r.model // ""),
        usage: ($r.usage // {})
      }
    }'
}

cmd_embeddings() {
  local input="" model="text-embedding-3-small" dimensions=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)      model="$2"; shift 2 ;;
      --dimensions) dimensions="$2"; shift 2 ;;
      *)            input="$1"; shift ;;
    esac
  done

  [[ -n "$input" ]] || die "Usage: embeddings <text> [--model M] [--dimensions N]"

  local payload
  payload=$(jq -n --arg m "$model" --arg i "$input" '{model:$m, input:$i}')

  if [[ -n "$dimensions" ]]; then
    payload=$(echo "$payload" | jq --argjson d "$dimensions" '.dimensions = $d')
  fi

  local result
  result=$(api_call "/v1/embeddings" "$payload")

  if echo "$result" | jq -e '.error' &>/dev/null 2>&1; then
    echo "$result"
    return 1
  fi

  jq -n \
    --argjson r "$result" \
    '{
      success: true,
      data: {
        embedding: ($r.data[0].embedding // []),
        model: ($r.model // ""),
        usage: ($r.usage // {})
      }
    }'
}

# --- Main ---
command="${1:-}"
shift || die "Usage: openai_handler.sh <ask|responses|embeddings> <query> [options]"

case "$command" in
  ask)        cmd_ask "$@" ;;
  responses)  cmd_responses "$@" ;;
  embeddings) cmd_embeddings "$@" ;;
  *)          die "Unknown command: $command. Use: ask, responses, embeddings" ;;
esac
