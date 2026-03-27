#!/bin/bash
# Auto-QA Stop hook — runs project tests if available.
# Returns exit 2 (block) if tests fail, exit 0 (pass) otherwise.
# Skips silently if no test runner is found.

# Detect test runner
if [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
  RUNNER="pnpm test --run 2>&1"
elif [ -f "pyproject.toml" ] && grep -q 'pytest' pyproject.toml 2>/dev/null; then
  RUNNER="uv run pytest --tb=short -q 2>&1"
else
  # No test runner found — pass through
  exit 0
fi

# Run tests
OUTPUT=$(eval "$RUNNER")
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "Tests failed. Fix before finishing." >&2
  echo "$OUTPUT" | tail -20 >&2
  exit 2
fi

exit 0
