#!/usr/bin/env bash
# Pre-commit hook: scan staged files for potential secrets
# Install: cp scripts/pre-commit-secrets.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# High-entropy patterns that indicate real secrets (macOS grep -Ei compatible)
SECRET_PATTERNS=(
    'BINANCE_API_KEY=[A-Za-z0-9]{20,}'
    'BINANCE_SECRET_KEY=[A-Za-z0-9]{20,}'
    'SECRET_KEY=[A-Za-z0-9+/=]{20,}'
    'API_KEY=[A-Za-z0-9+/=]{20,}'
    'xoxb-[0-9]{10,}'
    'xoxp-[0-9]{10,}'
    'sk-[A-Za-z0-9]{20,}'
    'SLACK_BOT_TOKEN=xoxb-'
    'WHATSAPP_TOKEN=[A-Za-z0-9]{20,}'
    'GMAIL_CLIENT_SECRET=[A-Za-z0-9_-]{20,}'
    'GMAIL_REFRESH_TOKEN=[A-Za-z0-9_/-]{20,}'
    'GEMINI_API_KEY=[A-Za-z0-9_-]{20,}'
    'GOOGLE_API_KEY=[A-Za-z0-9_-]{20,}'
    'SUPABASE_SERVICE_ROLE_KEY=eyJ'
    'VERCEL_TOKEN=[A-Za-z0-9]{20,}'
    'BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY'
    'ghp_[A-Za-z0-9]{36}'
    'gho_[A-Za-z0-9]{36}'
    'github_pat_[A-Za-z0-9_]{20,}'
)

# Allowlisted files where patterns are expected (docs, examples)
ALLOWLIST=(
    '.env.example'
    'scripts/pre-commit-secrets.sh'
)

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

FOUND=0

is_allowlisted() {
    local file="$1"
    for allowed in "${ALLOWLIST[@]}"; do
        if [[ "$file" == *"$allowed" ]]; then
            return 0
        fi
    done
    return 1
}

for file in $STAGED_FILES; do
    # Skip binary files, lock files, and allowlisted files
    if [[ "$file" == *.png ]] || [[ "$file" == *.jpg ]] || [[ "$file" == *.lock ]] || [[ "$file" == *.gif ]]; then
        continue
    fi
    if is_allowlisted "$file"; then
        continue
    fi

    for pattern in "${SECRET_PATTERNS[@]}"; do
        if git show ":$file" 2>/dev/null | grep -qEi "$pattern"; then
            if [ $FOUND -eq 0 ]; then
                echo -e "${RED}=== SECRETS DETECTED IN STAGED FILES ===${NC}"
                echo ""
            fi
            FOUND=1
            echo -e "${YELLOW}  $file${NC} matches: $pattern"
        fi
    done
done

# Block .env files from being committed
for file in $STAGED_FILES; do
    if [[ "$file" == .env ]] || [[ "$file" == .env.local ]] || [[ "$file" =~ \.env\..+\.local$ ]]; then
        if [ $FOUND -eq 0 ]; then
            echo -e "${RED}=== SECRETS DETECTED IN STAGED FILES ===${NC}"
            echo ""
        fi
        FOUND=1
        echo -e "${YELLOW}  $file${NC} - env files must not be committed"
    fi
done

if [ $FOUND -ne 0 ]; then
    echo ""
    echo -e "${RED}Commit blocked. Remove secrets before committing.${NC}"
    echo "  Use: git reset HEAD <file> to unstage"
    echo "  Or:  git commit --no-verify to bypass (NOT recommended)"
    exit 1
fi

exit 0
