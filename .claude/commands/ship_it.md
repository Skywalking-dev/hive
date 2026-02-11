---
description: "Ship changes to production: update CHANGELOG.md, commit, push, and create MR"
---

# Ship it

Ship changes to production: update changelog, commit, push, and create a Merge Request.

## Objective

Ensure changes reach production following the complete flow:
1. Log changes in CHANGELOG.md
2. Commit all modified files
3. Push to remote branch
4. Create Merge Request (MR) to merge into main
5. Close backlog items if applicable

## Instructions

1. **Get context**: Review `git status` and `git diff` to identify all modified files.

2. **Update CHANGELOG.md**:
   - Locate CHANGELOG.md in the project
   - Read existing format and structure
   - Add new entry at the **top** of the [Unreleased] section
   - Follow Common Changelog + SemVer format (see CLAUDE.md)

3. **Commit**:
   - Include CHANGELOG.md and all modified files
   - Descriptive message following project conventions

4. **Push**: Push changes to current remote branch.

5. **Create MR**: Create Merge Request to merge into `main` (or project's main branch).


## Notes

**CHANGELOG:**
- Keep entries concise but descriptive
- Use bullet points for sub-details
- Follow existing format conventions in the CHANGELOG
- Don't modify released versions (only [Unreleased])
- Use Common Changelog + SemVer conventions per CLAUDE.md

**Complete process:**
- The changelog is only part of the deploy process
- Ensure all modified files are included in the commit
- The MR must have a clear description of the changes

## Usage Examples

```bash
# Ship changes to production
/ship-it

# With additional context (optional)
/ship-it feature: improved authentication
```
