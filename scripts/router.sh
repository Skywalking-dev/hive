#!/usr/bin/env bash
# Smart router for Hive handlers.
# Maps task types to optimal provider/model by cost and quality.
# Usage: router.sh <task-type> [query] [--flag value...]
# Usage: router.sh route <task-type>  (just print the handler + model)
# Usage: router.sh list               (show all routes)
#
# Routes are based on docs/LLM_API_LANDSCAPE.md benchmarks.
# Update routes when landscape data changes.
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Route table ──
# Format: handler|model|cost_note
# Priority: free > cheapest paid > best quality
declare -A ROUTES=(
  # LLM — text generation
  [chat]='groq_handler.sh|llama-4-scout-17b-16e-instruct|free, 1200+ tok/s'
  [reason]='deepseek_handler.sh|deepseek-reasoner|$2.19/MTok out, best value reasoning'
  [code]='fireworks_handler.sh|accounts/fireworks/models/qwen3-8b|$0.20/MTok, fast code'
  [code-pro]='deepseek_handler.sh|deepseek-chat|$0.50/MTok, frontier code quality'
  [classify]='cerebras_handler.sh|llama3.1-8b|free, 1500+ tok/s, 1M TPD'
  [embed]='openai_handler.sh|text-embedding-3-small|$0.02/MTok'
  [search]='perplexity_handler.sh|sonar|$1/MTok, grounded + citations'
  [research]='perplexity_handler.sh|sonar-deep-research|$8/MTok, multi-step synthesis'
  [long]='openrouter_handler.sh|deepseek/deepseek-chat|$0.50/MTok, 1M context'
  [batch]='deepseek_handler.sh|deepseek-chat|$0.50/MTok, frontier at budget'
  [free]='groq_handler.sh|llama-4-scout-17b-16e-instruct|free, tools+vision'
  [fast]='cerebras_handler.sh|llama3.1-8b|free, fastest inference'

  # Image generation
  [image]='fal_handler.py|schnell|$0.003/img, FLUX Schnell'
  [image-pro]='fal_handler.py|flux-pro|$0.04/img, FLUX 1.1 Pro'
  [image-text]='fal_handler.py|ideogram|$0.03/img, 98% text accuracy'
  [image-svg]='fal_handler.py|recraft|$0.04 raster/$0.08 SVG'

  # Video generation
  [video]='fal_handler.py|wan|~$0.05/sec, Wan 2.7, open-source'
  [video-pro]='fal_handler.py|veo|Veo 3.1 Lite, $0.05/sec'
  [video-cinema]='fal_handler.py|veo-std|Veo 3.1 Standard, $0.40/sec, 4K+audio'

  # Audio
  [stt]='groq_handler.sh|whisper-large-v3|$0.00185/min, free tier'
  [tts]='openai_handler.sh|tts-1|$15/1M chars'
)

# ── Commands ──

cmd_route() {
  local task="${1:-}"
  [[ -n "$task" ]] || { echo "Usage: router.sh route <task-type>"; cmd_list; exit 1; }

  local route="${ROUTES[$task]:-}"
  if [[ -z "$route" ]]; then
    echo "{\"success\":false,\"error\":\"Unknown task type: $task\"}"
    echo "Available: ${!ROUTES[*]}" >&2
    exit 1
  fi

  IFS='|' read -r handler model cost <<< "$route"
  echo "{\"handler\":\"$handler\",\"model\":\"$model\",\"cost\":\"$cost\"}"
}

cmd_list() {
  echo "── Hive Router ──"
  printf "%-14s %-30s %-40s %s\n" "TASK" "HANDLER" "MODEL" "COST"
  printf "%-14s %-30s %-40s %s\n" "────" "───────" "─────" "────"

  # Sort keys
  for task in $(echo "${!ROUTES[@]}" | tr ' ' '\n' | sort); do
    IFS='|' read -r handler model cost <<< "${ROUTES[$task]}"
    printf "%-14s %-30s %-40s %s\n" "$task" "$handler" "$model" "$cost"
  done
}

cmd_run() {
  local task="${1:-}"
  shift || true

  local route="${ROUTES[$task]:-}"
  if [[ -z "$route" ]]; then
    echo "Unknown task: $task" >&2
    cmd_list >&2
    exit 1
  fi

  IFS='|' read -r handler model cost <<< "$route"

  # Determine command based on handler type
  local handler_path="${SCRIPT_DIR}/${handler}"

  if [[ "$handler" == *.py ]]; then
    # Python handler (fal_handler.py)
    local subcmd="image"
    [[ "$task" == video* ]] && subcmd="video"
    exec python3 "$handler_path" "$subcmd" "$@" --model "$model"
  else
    # Bash handler — route to ask command with model
    exec bash "$handler_path" ask "$@" --model "$model"
  fi
}

# ── Main ──
command="${1:-}"
shift 2>/dev/null || true

case "$command" in
  route) cmd_route "$@" ;;
  list)  cmd_list ;;
  help)  cmd_list ;;
  "")    cmd_list ;;
  *)     cmd_run "$command" "$@" ;;  # Direct task invocation: router.sh chat "query"
esac
