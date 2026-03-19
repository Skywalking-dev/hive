---
name: github-cli
description: GitHub CLI operations for commit, push, PR creation, reviews, and branch housekeeping. Use for git workflows, PR management, branch cleanup, review comments, and GitHub API interactions via `gh` CLI.
---

# GitHub CLI

## Overview

Streamline GitHub workflows via `gh` CLI: commits, pushes, PR creation, reviews, and branch cleanup. All scripts assume authenticated `gh` setup.

## Branch Naming Convention

For Linear-based workflow:

**Format:** `feature/{issue-id}/{agent}-{YYYYMMDD}`

**Examples:**
```
feature/SKY-45/kokoro-20250118   → Kokoro working on SKY-45
feature/SKY-45/pixel-20250118   → Pixel working on SKY-45
feature/MIIC-12/aurora-20250118 → Aurora working on MIIC-12
```

**Legacy format (still supported):**
```
feature/SKY-123-whatsapp-button
fix/MIIC-45-cart-bug
```

## Workflows

### Housekeeping: Clean Obsolete Branches

Remove local branches marked as `[gone]` (deleted on remote) + associated worktrees:

```bash
./scripts/clean_branches.sh
```

**What it does:**
- Finds all `[gone]` branches via `git branch -vv`
- Removes associated worktrees
- Force-deletes branches locally

### Git: Commit + Push

```bash
git add <files>
git commit -m "{issue-id}: {message}"
git push
```

Commit message convention:
```
SKY-45: Add whatsapp_number migration
SKY-45: Implement WhatsAppButton component
```

### PR: Create for Linear Issue

```bash
gh pr create \
  --title "SKY-45: Add WhatsApp button" \
  --body "Closes SKY-45

## Summary
- Added migration for whatsapp_number
- Created WhatsAppButton component
- Added E2E tests

## Testing
- [ ] Unit tests pass
- [ ] E2E tests pass
- [ ] Manual QA done"
```

### PR: Additional Operations

Common `gh` commands for PR interactions:

```bash
gh pr list                              # List all PRs
gh pr view <NUMBER>                     # View PR details
gh pr edit <NUMBER> --title "New"       # Edit PR title/body
gh pr close <NUMBER>                    # Close PR
gh pr merge <NUMBER>                    # Merge PR
gh pr review <NUMBER> -c -b "feedback"  # Add comment review
gh pr merge <NUMBER> --squash           # Squash merge
gh pr checks <NUMBER>                   # View CI status
```

## Worktree for Parallel Work

When multiple agents work on same issue:

```bash
# Create worktree for agent
git worktree add ../SKY-45-kokoro feature/SKY-45/kokoro-20250118

# Work in isolated directory
cd ../SKY-45-kokoro

# When done, remove worktree
git worktree remove ../SKY-45-kokoro
```

## Integration with Linear

### Extract Linear ID from Branch

```bash
# Current branch: feature/SKY-45/kokoro-20250118
git branch --show-current | grep -oE '(SKY|MIIC|[A-Z]+)-[0-9]+'
# Output: SKY-45
```

### PR → Linear State Sync

Use `/review` command to:
1. Get PR state
2. Update Linear issue state
3. Add comment to Linear

## Scripts

All scripts in `scripts/` are executable:

- `clean_branches.sh` - Remove [gone] branches + worktrees

## Best Practices

1. **Always include Linear ID** in branch name and commit messages
2. **Use worktrees** for parallel agent work
3. **Run `/review`** after creating PR to sync with Linear
4. **Clean branches** regularly with `clean_branches.sh`
