#!/usr/bin/env bash
# Perplexity API handler for Hive.
# Sonar (chat+search), Search (raw results), Agent (multi-provider).
set -euo pipefail

BASE_URL="https://api.perplexity.ai"

# Load .env — resolve from script location (hive/scripts/ → hive/.env)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
elif [[ -f ".env" ]]; then
  set -a; source ".env"; set +a
fi

die() { echo "{\"success\":false,\"error\":\"$1\"}" >&2; exit 1; }

[[ -n "${PERPLEXITY_API_KEY:-}" ]] || die "PERPLEXITY_API_KEY not set"

# --- Core API call ---
api_call() {
  local endpoint="$1" payload="$2"
  curl -sS --max-time 120 \
    -X POST "${BASE_URL}${endpoint}" \
    -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# --- Commands ---

cmd_ask() {
  local query="" model="sonar-pro" system="" domains="" recency="" json_schema="" stream=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)    model="$2"; shift 2 ;;
      --system)   system="$2"; shift 2 ;;
      --domains)  domains="$2"; shift 2 ;;
      --recency)  recency="$2"; shift 2 ;;
      --json-schema) json_schema="$2"; shift 2 ;;
      --stream)   stream=true; shift ;;
      *)          query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: ask <query> [--model M] [--system S] [--domains D] [--recency R] [--json-schema J] [--stream]"

  # Build messages array
  local messages="[]"
  if [[ -n "$system" ]]; then
    messages=$(jq -n --arg s "$system" '[{"role":"system","content":$s}]')
  fi
  messages=$(echo "$messages" | jq --arg q "$query" '. + [{"role":"user","content":$q}]')

  # Build payload
  local payload
  payload=$(jq -n --arg m "$model" --argjson msgs "$messages" '{model:$m, messages:$msgs}')

  if [[ "$stream" == "true" ]]; then
    payload=$(echo "$payload" | jq '.stream = true')
  fi

  # Web search options
  local web_opts="{}"
  if [[ -n "$domains" ]]; then
    web_opts=$(echo "$web_opts" | jq --arg d "$domains" '.search_domain_filter = ($d | split(","))')
  fi
  if [[ -n "$recency" ]]; then
    web_opts=$(echo "$web_opts" | jq --arg r "$recency" '.search_recency_filter = $r')
  fi
  if [[ "$web_opts" != "{}" ]]; then
    payload=$(echo "$payload" | jq --argjson wo "$web_opts" '.web_search_options = $wo')
  fi

  # Structured output
  if [[ -n "$json_schema" ]]; then
    payload=$(echo "$payload" | jq --argjson js "$json_schema" '.response_format = {type:"json_schema", json_schema:{schema:$js}}')
  fi

  if [[ "$stream" == "true" ]]; then
    # Stream: parse SSE lines
    curl -sS --max-time 120 -N \
      -X POST "${BASE_URL}/chat/completions" \
      -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
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
  result=$(api_call "/chat/completions" "$payload")

  # Check for error
  if echo "$result" | jq -e '.error' &>/dev/null 2>&1; then
    echo "$result"
    return 1
  fi

  # Extract and format output
  jq -n \
    --argjson r "$result" \
    '{
      success: true,
      data: {
        content: ($r.choices[0].message.content // ""),
        model: ($r.model // ""),
        usage: ($r.usage // {}),
        citations: ($r.citations // null)
      }
    } | if .data.citations == null then del(.data.citations) else . end'
}

cmd_search() {
  local query="" max_results=10 domains="" exclude_domains="" country="" language=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --max-results)      max_results="$2"; shift 2 ;;
      --domains)          domains="$2"; shift 2 ;;
      --exclude-domains)  exclude_domains="$2"; shift 2 ;;
      --country)          country="$2"; shift 2 ;;
      --language)         language="$2"; shift 2 ;;
      *)                  query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: search <query> [--max-results N] [--domains D] [--exclude-domains D] [--country C] [--language L]"

  local payload
  payload=$(jq -n --arg q "$query" --argjson mr "$max_results" '{query:$q, max_results:$mr}')

  if [[ -n "$domains" ]]; then
    payload=$(echo "$payload" | jq --arg d "$domains" '.search_domain_filter = ($d | split(","))')
  fi
  if [[ -n "$exclude_domains" ]]; then
    payload=$(echo "$payload" | jq --arg d "$exclude_domains" '.search_domain_filter = ($d | split(",") | map("-" + .))')
  fi
  if [[ -n "$country" ]]; then
    payload=$(echo "$payload" | jq --arg c "$country" '.country = $c')
  fi
  if [[ -n "$language" ]]; then
    payload=$(echo "$payload" | jq --arg l "$language" '.search_language_filter = ($l | split(","))')
  fi

  local result
  result=$(api_call "/search" "$payload")

  jq -n --argjson r "$result" '{success: true, data: $r}'
}

cmd_agent() {
  local query="" model="openai/gpt-5.2" tools="web_search" max_tokens="" reasoning="" stream=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)     model="$2"; shift 2 ;;
      --tools)     tools="$2"; shift 2 ;;
      --max-tokens) max_tokens="$2"; shift 2 ;;
      --reasoning) reasoning="$2"; shift 2 ;;
      --stream)    stream=true; shift ;;
      *)           query="$1"; shift ;;
    esac
  done

  [[ -n "$query" ]] || die "Usage: agent <query> [--model M] [--tools T] [--max-tokens N] [--reasoning R] [--stream]"

  # Build tools array
  local tools_json
  tools_json=$(echo "$tools" | jq -R 'split(",") | map({type:.})')

  local payload
  payload=$(jq -n --arg m "$model" --arg q "$query" --argjson t "$tools_json" '{model:$m, input:$q, tools:$t}')

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
      -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
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
  result=$(api_call "/v1/responses" "$payload")

  if echo "$result" | jq -e '.error' &>/dev/null 2>&1; then
    echo "$result"
    return 1
  fi

  # Extract text from agent response
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

# --- Main ---
command="${1:-}"
shift || die "Usage: perplexity_handler.sh <ask|search|agent> <query> [options]"

case "$command" in
  ask)    cmd_ask "$@" ;;
  search) cmd_search "$@" ;;
  agent)  cmd_agent "$@" ;;
  *)      die "Unknown command: $command. Use: ask, search, agent" ;;
esac
