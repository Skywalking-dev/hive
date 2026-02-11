---
description: Shape a new ticket through guided discovery. Creates issues in Linear.
---

# /shape Command

Guided issue creation flow. Uses `issue-shaping` skill for logic and templates.

## Usage

```bash
/shape
/shape "optional title hint"
```

## Flow

1. **Load skill** → Read `.claude/skills/issue-shaping/SKILL.md` for templates and specs

2. **Ask type** (AskUserQuestion):
   - Bug - Something broken
   - Feature - New functionality
   - Improvement - Enhancement

3. **Gather context** → Follow skill's discovery questions by type (batches of 2-3)

4. **Check duplicates** → `linear_search_issues` before creating

5. **Create in Linear** → `linear_create_issue` using skill's templates

6. **Sub-issues?** → Ask if agent sub-issues needed, create per skill specs

7. **Confirm** → Show Linear URL, offer refinements

## Notes

- All logic, templates, priorities in skill
- Command just orchestrates the flow
- Never skip required questions
- Infer from context when possible
