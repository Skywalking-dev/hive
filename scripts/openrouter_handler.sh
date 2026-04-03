#!/usr/bin/env bash
# OpenRouter API handler for Hive.
# Universal fallback — single API for all providers. 29+ free models.
# OAI-compatible with extra routing headers.
# Free models: deepseek/deepseek-r1:free, qwen/qwen3-coder:free, google/gemma-3-27b-it:free
set -euo pipefail

BASE_URL="https://openrouter.ai/api"

# Load .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
elif [[ -f ".env" ]]; then
  set -a; source ".env"; set +a
fi

die() { echo "{\"success\":false,\"error\":\"$1\"}" >&2; exit 1; }

[[ -n "${OPENROUTER_API_KEY:-}" ]] || die "OPENROUTER_API_KEY not set"

SITE_NAME="${OPENROUTER_SITE_NAME:-Skywalking Hive}"
SITE_URL="${OPENROUTER_SITE_URL:-https://skywalking.dev}"

# --- Core API call ---
api_call() {
  local endpoint="$1" payload="$2"
  curl -sS --max-time 120 \
    -X POST "${BASE_URL}${endpoint}" \
    -H "Authorization: Bearer ${OPENROUTER_API_KEY}" \
    -H "HTTP-Referer: ${SITE_URL}" \
    -H "X-Title: ${SITE_NAME}" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# --- Commands ---

cmd_ask() {
  local query="" model="deepseek/deepseek-chat" system="" temperature=0.7 max_tokens="" json_mode=false provider="" fallbacks="" use_free=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)       model="$2"; shift 2 ;;
      --system)      system="$2"; shift 2 ;;
      --temperature) temperature="$2"; shift 2 ;;
      --max-tokens)  max_tokens="$2"; shift 2 ;;
      --json)        json_mode=true; shift ;;
      --provider)    provider="$2"; shift 2 ;;
      --fallbacks)   fallbacks="$2"; shift 2 ;;
      --free)        use_free=true; shift ;;
      *)             query="$1"; shift ;;
    esac
  done

  # Apply :free suffix after all args parsed (order-independent)
  if [[ "$use_free" == "true" ]]; then
    model="${model}:free"
  fi

  [[ -n "$query" ]] || die "Usage: ask <query> [--model M] [--system S] [--temperature T] [--max-tokens N] [--json] [--free] [--provider P] [--fallbacks M1,M2]"

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

  # OpenRouter routing: provider preferences
  if [[ -n "$provider" ]]; then
    payload=$(echo "$payload" | jq --arg p "$provider" '.provider = {order: [$p]}')
  fi

  # OpenRouter routing: fallback models
  if [[ -n "$fallbacks" ]]; then
    local fallback_json
    fallback_json=$(echo "$fallbacks" | jq -R 'split(",")')
    payload=$(echo "$payload" | jq --argjson fb "$fallback_json" --arg m "$model" \
      '.route = "fallback" | .models = ([$m] + $fb)')
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
        usage: ($r.usage // {}),
        provider: ($r.provider // null)
      }
    }'
}

cmd_models() {
  local filter="${1:-}"
  local url="${BASE_URL}/v1/models"

  local result
  result=$(curl -sS --max-time 30 "$url")

  if [[ -n "$filter" ]]; then
    echo "$result" | jq --arg f "$filter" '{success: true, data: [.data[] | select(.id | contains($f)) | {id, name: .name, context_length, pricing}]}'
  else
    echo "$result" | jq '{success: true, count: (.data | length), data: [.data[:20][] | {id, name: .name, context_length, pricing}]}'
  fi
}

cmd_free() {
  local url="${BASE_URL}/v1/models"
  curl -sS --max-time 30 "$url" | jq '{
    success: true,
    data: [.data[] | select((.pricing.prompt == "0" or .pricing.prompt == null) and (.id | endswith(":free"))) | {id, name: .name, context_length}] | sort_by(.context_length) | reverse
  }'
}

# --- Main ---
command="${1:-}"
shift || die "Usage: openrouter_handler.sh <ask|models|free> <query> [options]"

case "$command" in
  ask)    cmd_ask "$@" ;;
  models) cmd_models "${1:-}" ;;
  free)   cmd_free ;;
  *)      die "Unknown command: $command. Use: ask, models, free" ;;
esac
