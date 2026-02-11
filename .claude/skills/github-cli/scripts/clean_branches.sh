#!/bin/bash
# Clean up local branches that are gone on remote (marked as [gone])
# Usage: ./clean_branches.sh

echo "🧹 Finding branches marked as [gone]..."
gone_branches=$(git branch -vv | grep '\[gone\]' | awk '{print $1}')

if [ -z "$gone_branches" ]; then
    echo "✅ No [gone] branches found"
    exit 0
fi

echo "Found branches to clean:"
echo "$gone_branches"
echo ""

# Also remove associated worktrees if any
echo "🔧 Cleaning worktrees..."
for branch in $gone_branches; do
    if git worktree list | grep -q "$branch"; then
        git worktree remove "$branch" 2>/dev/null || true
    fi
done

# Delete branches
echo "❌ Deleting branches..."
for branch in $gone_branches; do
    git branch -D "$branch"
    echo "  Deleted: $branch"
done

echo "✅ Cleanup complete"
