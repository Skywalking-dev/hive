#!/usr/bin/env bash
# PR Review via LLM handler.
# Gets PR diff, classifies complexity, sends to appropriate model, posts as PR comment.
# Used by GitHub Actions as a cheaper alternative to claude-code-action for routine PRs.
#
# Usage:
#   review_pr.sh <pr_number> [--handler deepseek|openrouter] [--model M] [--critical-paths P1,P2]
#   review_pr.sh classify <pr_number>   # just classify, don't review
#
# Requires: gh CLI authenticated, handler API key in env
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env
if [[ -f "${HIVE_DIR}/.env" ]]; then
  set -a; source "${HIVE_DIR}/.env"; set +a
elif [[ -f ".env" ]]; then
  set -a; source ".env"; set +a
fi

die() { echo "::error::$1" >&2; exit 1; }

# --- Defaults ---
HANDLER="deepseek"
MODEL=""
CRITICAL_PATHS="auth,payment,mercadopago,security,middleware,encryption,webhook,supabase/migrations"
MAX_DIFF_LINES=8000

# --- Parse args ---
COMMAND="review"
PR_NUMBER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    classify)       COMMAND="classify"; shift ;;
    --handler)      HANDLER="$2"; shift 2 ;;
    --model)        MODEL="$2"; shift 2 ;;
    --critical-paths) CRITICAL_PATHS="$2"; shift 2 ;;
    --max-diff)     MAX_DIFF_LINES="$2"; shift 2 ;;
    *)
      if [[ -z "$PR_NUMBER" ]]; then
        PR_NUMBER="$1"; shift
      else
        die "Unknown arg: $1"
      fi
      ;;
  esac
done

[[ -n "$PR_NUMBER" ]] || die "Usage: review_pr.sh <pr_number> [--handler deepseek|openrouter] [--model M]"

# --- Resolve handler ---
HANDLER_SCRIPT="${SCRIPT_DIR}/${HANDLER}_handler.sh"
[[ -f "$HANDLER_SCRIPT" ]] || die "Handler not found: $HANDLER_SCRIPT"

if [[ -z "$MODEL" ]]; then
  case "$HANDLER" in
    deepseek)    MODEL="deepseek-chat" ;;
    openrouter)  MODEL="deepseek/deepseek-chat" ;;
    *)           MODEL="" ;;
  esac
fi

# --- Get PR info ---
echo "::group::Fetching PR #${PR_NUMBER}"

PR_TITLE=$(gh pr view "$PR_NUMBER" --json title -q '.title')
PR_BODY=$(gh pr view "$PR_NUMBER" --json body -q '.body' | head -100)
PR_FILES=$(gh pr view "$PR_NUMBER" --json files -q '.files[].path')
PR_DIFF=$(gh pr diff "$PR_NUMBER" | head -"$MAX_DIFF_LINES")

FILE_COUNT=$(echo "$PR_FILES" | grep -c . || echo 0)
DIFF_LINES=$(echo "$PR_DIFF" | grep -c . || echo 0)

echo "Title: $PR_TITLE"
echo "Files: $FILE_COUNT"
echo "Diff lines: $DIFF_LINES"
echo "::endgroup::"

# --- Classify PR ---
classify_pr() {
  local level="normal"
  local reasons=""

  IFS=',' read -ra PATHS <<< "$CRITICAL_PATHS"
  while IFS= read -r file; do
    for pattern in "${PATHS[@]}"; do
      if echo "$file" | grep -qi "$pattern"; then
        level="critical"
        reasons="${reasons}${file} matches '${pattern}'\n"
      fi
    done
  done <<< "$PR_FILES"

  # Large PRs are critical
  if [[ "$FILE_COUNT" -gt 20 ]] || [[ "$DIFF_LINES" -gt 5000 ]]; then
    level="critical"
    reasons="${reasons}Large PR: ${FILE_COUNT} files, ${DIFF_LINES} diff lines\n"
  fi

  # Simple heuristics
  local simple_patterns="README|CHANGELOG|docs/|\.md$|package-lock|pnpm-lock|\.gitignore"
  local all_simple=true
  while IFS= read -r file; do
    if ! echo "$file" | grep -qEi "$simple_patterns"; then
      all_simple=false
      break
    fi
  done <<< "$PR_FILES"

  if [[ "$all_simple" == "true" ]]; then
    level="simple"
    reasons="All files are docs/config/lockfiles"
  fi

  echo "$level"
  if [[ -n "$reasons" ]]; then
    echo -e "$reasons" >&2
  fi
}

LEVEL=$(classify_pr)
REASONS=$(classify_pr 2>&1 >/dev/null || true)

echo "Classification: $LEVEL"
if [[ -n "$REASONS" ]]; then
  echo "Reasons: $REASONS"
fi

if [[ "$COMMAND" == "classify" ]]; then
  echo "$LEVEL"
  exit 0
fi

# --- Review ---
if [[ "$LEVEL" == "simple" ]]; then
  echo "Simple PR — posting quick approval"
  gh pr comment "$PR_NUMBER" --body "$(cat <<'EOF'
## Review: Approved (auto)

Docs/config/lockfile changes only — no code review needed.

_Reviewed by Hive (auto-classify)_
EOF
  )"
  exit 0
fi

echo "::group::Sending to ${HANDLER} (${MODEL})"

SYSTEM_PROMPT="You are a strict senior engineer reviewing a pull request. Analyze the diff and report:

1. **Bugs & correctness**: null safety, off-by-one, race conditions, missing error handling
2. **Security**: injection, exposed secrets, auth bypass, unsafe input
3. **Performance**: N+1 queries, unnecessary re-renders, missing memoization
4. **Code quality**: duplicated logic, inconsistent patterns, missing types
5. **Tests**: missing test coverage for new logic

Rules:
- Be specific. Reference file:line.
- Suggest fixes with code blocks.
- If everything is clean, say so briefly.
- Do NOT be lenient. Flag anything you would flag in a real code review.
- Output GitHub-flavored Markdown.
- Keep it concise — no filler, no praise, just findings."

USER_PROMPT="# PR: ${PR_TITLE}

## Description
${PR_BODY}

## Files changed (${FILE_COUNT})
${PR_FILES}

## Diff
\`\`\`diff
${PR_DIFF}
\`\`\`"

REVIEW=$("$HANDLER_SCRIPT" ask "$USER_PROMPT" \
  --system "$SYSTEM_PROMPT" \
  --model "$MODEL" \
  --temperature 0.3 \
  --max-tokens 4000)

echo "::endgroup::"

# Extract content from handler response
CONTENT=$(echo "$REVIEW" | jq -r '.data.content // empty')
USAGE=$(echo "$REVIEW" | jq -r '.data.usage | "Tokens: \(.prompt_tokens // 0) in / \(.completion_tokens // 0) out"')

if [[ -z "$CONTENT" ]]; then
  echo "::warning::Empty response from handler"
  echo "$REVIEW" >&2
  exit 1
fi

# --- Post as PR comment ---
COMMENT_BODY="## Code Review

${CONTENT}

---
_Reviewed by **${HANDLER}** (${MODEL}) | ${USAGE} | Classification: ${LEVEL}_"

gh pr comment "$PR_NUMBER" --body "$COMMENT_BODY"

echo "Review posted to PR #${PR_NUMBER}"
