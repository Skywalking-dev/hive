#!/usr/bin/env bash
# Groq API handler for Hive.
# Free tier, OAI-compatible. Fastest inference (3000+ tok/s).
# Models: llama-4-scout-17b-16e-instruct, llama-4-maverick-17b-128e-instruct,
#         llama-3.3-70b-versatile, llama-3.1-8b-instant
set -euo pipefail

BASE_URL="https://api.groq.com/openai"

# Load .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
elif [[ -f ".env" ]]; then
  set -a; source ".env"; set +a
fi

die() { echo "{\"success\":false,\"error\":\"$1\"}" >&2; exit 1; }

[[ -n "${GROQ_API_KEY:-}" ]] || die "GROQ_API_KEY not set"

# --- Core API call ---
api_call() {
  local endpoint="$1" payload="$2"
  curl -sS --max-time 120 \
    -X POST "${BASE_URL}${endpoint}" \
    -H "Authorization: Bearer ${GROQ_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# --- Commands ---

cmd_ask() {
  local query="" model="llama-4-scout-17b-16e-instruct" system="" temperature=0.7 max_tokens="" json_mode=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)       model="$2"; shift 2 ;;
      --system)      system="$2"; shift 2 ;;
      --temperature) temperature="$2"; shift 2 ;;
      --max-tokens)  max_tokens="$2"; shift 2 ;;
      --json)        json_mode=true; shift ;;
      *)             query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: ask <query> [--model M] [--system S] [--temperature T] [--max-tokens N] [--json]"

  local messages="[]"
  if [[ -n "$system" ]]; then
    messages=$(jq -n --arg s "$system" '[{"role":"system","content":$s}]')
  fi
  messages=$(echo "$messages" | jq --arg q "$query" '. + [{"role":"user","content":$q}]')

  local payload
  payload=$(jq -n --arg m "$model" --argjson msgs "$messages" --argjson t "$temperature" \
    '{model:$m, messages:$msgs, temperature:$t}')

  if [[ -n "$max_tokens" ]]; then
    payload=$(echo "$payload" | jq --argjson mt "$max_tokens" '.max_tokens = $mt')
  fi
  if [[ "$json_mode" == "true" ]]; then
    payload=$(echo "$payload" | jq '.response_format = {type:"json_object"}')
  fi

  local result
  result=$(api_call "/v1/chat/completions" "$payload") || { die "API call failed"; }

  if [[ -z "$result" ]] || ! echo "$result" | jq -e '.choices' &>/dev/null; then
    echo "$result" >&2
    die "Invalid response (no choices)"
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

cmd_models() {
  curl -sS --max-time 30 \
    -H "Authorization: Bearer ${GROQ_API_KEY}" \
    "${BASE_URL}/v1/models" | jq '{success: true, data: [.data[] | {id, owned_by, context_window}]}'
}

# --- Main ---
command="${1:-}"
shift || die "Usage: groq_handler.sh <ask|models> <query> [options]"

case "$command" in
  ask)    cmd_ask "$@" ;;
  models) cmd_models ;;
  *)      die "Unknown command: $command. Use: ask, models" ;;
esac
