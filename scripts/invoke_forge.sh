#!/usr/bin/env bash
# Invoke Forge (GPT-5 via Codex CLI) for technical review and feedback.
# Usage: invoke_forge.sh <file_path> [doc_type]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIVE_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_ROOT="$(dirname "$HIVE_DIR")"

die() { echo -e "\033[0;31m$1\033[0m" >&2; exit 1; }
info() { echo -e "\033[1;33m$1\033[0m"; }
ok() { echo -e "\033[0;32m$1\033[0m"; }

# Args
FILE_PATH="${1:-}"
DOC_TYPE="${2:-document}"

[[ -n "$FILE_PATH" ]] || die "Usage: invoke_forge.sh <file_path> [doc_type]"
[[ -f "$FILE_PATH" ]] || die "File not found: $FILE_PATH"

# Check codex CLI
command -v codex &>/dev/null || die "Codex CLI not found. Install and configure it first."

# Context file
AGENTS_MD="${WORKSPACE_ROOT}/AGENTS.md"
[[ -f "$AGENTS_MD" ]] || die "AGENTS.md not found at ${AGENTS_MD}"

# Output file
FEEDBACK_FILE="$(dirname "$FILE_PATH")/$(basename "$FILE_PATH")-forge-feedback.md"

info "[Forge] Reading document: ${FILE_PATH}"

DOCUMENT_CONTENT=$(cat "$FILE_PATH")
AGENTS_CONTEXT=$(cat "$AGENTS_MD")

# Build prompt
PROMPT=$(cat <<EOPROMPT
Your name, role, personality, and operational guidelines are defined in AGENTS.md below:

--- AGENTS.md ---
${AGENTS_CONTEXT}
---

TASK: Review the following ${DOC_TYPE} and provide structured technical feedback.

DOCUMENT TO REVIEW:
---
${DOCUMENT_CONTENT}
---

INSTRUCTIONS:
1. Analyze this document from your perspective as Forge (execution-focused, pragmatic, technical)
2. Follow the "Feedback Template" defined in AGENTS.md
3. Focus on:
   - Technical feasibility
   - Implementation risks (performance, security, scalability)
   - Cost/complexity trade-offs
   - Alternative approaches with pros/cons
   - Specific, actionable recommendations

4. Be constructive but honest. If something does not work, say so with alternatives.
5. Prioritize issues: HIGH (must fix), MEDIUM (should consider), LOW (nice to have)
6. Provide benchmarks or references where relevant

OUTPUT: Generate a complete markdown document following your feedback template.
Do NOT include any preamble or meta-commentary. Start directly with the markdown document.
EOPROMPT
)

info "[Forge] Invoking GPT-5 via Codex CLI..."

# Invoke codex
CODEX_OUTPUT=$(codex exec --skip-git-repo-check "$PROMPT" 2>&1) || {
  die "[Forge] Codex CLI failed: ${CODEX_OUTPUT}"
}

if [[ -z "$CODEX_OUTPUT" ]]; then
  die "[Forge] Error: No output received from Codex"
fi

echo "$CODEX_OUTPUT" > "$FEEDBACK_FILE"

ok "[Forge] Feedback generated: ${FEEDBACK_FILE}"
ok "[Forge] Analysis complete"
echo "$FEEDBACK_FILE"
