#!/usr/bin/env bash
# Fireworks AI API handler for Hive.
# OAI-compatible. Fastest open-source inference, fine-tuning, 40% batch discount.
# Models: accounts/fireworks/models/qwen3-8b, accounts/fireworks/models/llama-v3p3-70b-instruct
set -euo pipefail

BASE_URL="https://api.fireworks.ai/inference"

# Load .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
elif [[ -f ".env" ]]; then
  set -a; source ".env"; set +a
fi

die() { echo "{\"success\":false,\"error\":\"$1\"}" >&2; exit 1; }

[[ -n "${FIREWORKS_API_KEY:-}" ]] || die "FIREWORKS_API_KEY not set"

# --- Core API call ---
api_call() {
  local endpoint="$1" payload="$2"
  curl -sS --max-time 120 \
    -X POST "${BASE_URL}${endpoint}" \
    -H "Authorization: Bearer ${FIREWORKS_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# --- Commands ---

cmd_ask() {
  local query="" model="accounts/fireworks/models/qwen3-8b" system="" temperature=0.7 max_tokens="" json_mode=false stream=false

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
  if [[ "$stream" == "true" ]]; then
    payload=$(echo "$payload" | jq '.stream = true')
    curl -sS --max-time 120 -N \
      -X POST "${BASE_URL}/v1/chat/completions" \
      -H "Authorization: Bearer ${FIREWORKS_API_KEY}" \
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
    -H "Authorization: Bearer ${FIREWORKS_API_KEY}" \
    "${BASE_URL}/v1/models" | jq '{success: true, data: [.data[:20][] | {id, owned_by}]}'
}

# --- Main ---
command="${1:-}"
shift || die "Usage: fireworks_handler.sh <ask|models> <query> [options]"

case "$command" in
  ask)    cmd_ask "$@" ;;
  models) cmd_models ;;
  *)      die "Unknown command: $command. Use: ask, models" ;;
esac
