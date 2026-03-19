---
name: pr-review
description: Review pull requests and sync with Linear issues. Use when there's a PR to review, need to sync PR state with Linear, or want automated review feedback. Handles GitHub PR operations and Linear state transitions.
---

# PR Review

Review PRs, provide structured feedback, sync Linear state.

## Config

| Setting | Value |
|---------|-------|
| GitHub | `gh` CLI (authenticated) |
| Linear | MCP `list_issues`, `save_issue`, `create_comment`, `get_issue` |
| Team | Skywalking |

## Input

```bash
/review #123                                    # PR number (current repo)
/review https://github.com/org/repo/pull/123    # PR URL
/review SKY-123                                 # finds PR linked to Linear issue
```

## Execution Flow

### Step 1 — Resolve PR

Determine PR number and repo from input.

**If PR number or URL:**
```bash
gh pr view {number} --json number,title,body,state,headRefName,baseRefName,reviews,statusCheckRollup,files,additions,deletions,url
```

**If Linear issue ID:**
```bash
# Extract from Linear issue, find PR by branch pattern
gh pr list --json number,title,headRefName --jq '.[] | select(.headRefName | test("{ISSUE_ID}"))'
```

**If no input:**
```bash
# Use current branch
gh pr view --json number,title,body,state,headRefName,baseRefName,reviews,statusCheckRollup,files,additions,deletions,url
```

**Store:** `PR_NUMBER`, `PR_TITLE`, `PR_BODY`, `PR_STATE`, `BRANCH_NAME`, `BASE_BRANCH`, `PR_URL`, `FILES_CHANGED`, `CI_STATUS`

### Step 2 — Extract Linear Issue ID

From branch name (preferred) or PR body.

**Branch regex:** `(SKY|MIIC|[A-Z]+)-\d+`

```bash
# From branch name
echo "{BRANCH_NAME}" | grep -oE '(SKY|MIIC|[A-Z]+)-[0-9]+'
```

**PR body patterns:**
```
Closes SKY-123
Fixes SKY-123
Fixes https://linear.app/skywalking/issue/SKY-123
Related: SKY-456
```

**If no Linear ID found:** Warn and continue review without Linear sync.

**Store:** `LINEAR_ID` (e.g., `SKY-123`)

### Step 3 — Load Linear Issue Context

**If LINEAR_ID exists:**

Use Linear MCP to get issue details:
```
get_issue(id: "{LINEAR_ID}", includeRelations: true)
```

**Extract:**
- `ISSUE_TITLE` — what the issue is about
- `ACCEPTANCE_CRITERIA` — parse bullet list from description (look for "## Acceptance Criteria", "## AC", "## Criterios", or checkbox patterns `- [ ]`)
- `ISSUE_STATE` — current state
- `PARENT_ID` — if it's a sub-issue
- `LABELS` — bug/feature/improvement

### Step 4 — Read PR Diff

```bash
gh pr diff {PR_NUMBER}
```

For large diffs (>500 lines), focus on:
```bash
gh pr diff {PR_NUMBER} --name-only    # file list first
gh pr view {PR_NUMBER} --json files   # see additions/deletions per file
```

Then read high-impact files individually (new files, large changes, security-sensitive paths).

### Step 5 — Run Review Analysis

Analyze the diff against this checklist. Assign severity to each finding.

#### Severity Levels

| Level | Meaning | Merge Impact |
|-------|---------|-------------|
| CRITICAL | Security vuln, data loss, crash | Block merge |
| HIGH | Bug, missing validation, broken contract | Block merge |
| MEDIUM | Code smell, missing test, minor issue | Warn, don't block |
| LOW | Style, suggestion, nit | Informational |

#### Security Checks (CRITICAL/HIGH)

- [ ] No hardcoded secrets, API keys, passwords, tokens
- [ ] No SQL injection vectors (raw SQL with string interpolation)
- [ ] No XSS vectors (dangerouslySetInnerHTML, unescaped user input)
- [ ] No SSRF vectors (user-controlled URLs in server-side fetch)
- [ ] Supabase RLS not bypassed (no service_role key in client code)
- [ ] No sensitive data in logs or error messages
- [ ] Auth checks present on new API routes

#### Correctness Checks (HIGH/MEDIUM)

- [ ] No `console.log` or debug statements in production code
- [ ] Types are correct (no `any` without justification)
- [ ] No hardcoded values that should be env vars or constants
- [ ] Error handling present (try/catch on async, error boundaries)
- [ ] No unhandled promise rejections
- [ ] Edge cases considered (null, empty, boundary values)

#### Architecture Checks (MEDIUM)

- [ ] Follows project patterns (App Router, server components, etc.)
- [ ] Components <200 lines (or justified)
- [ ] No duplicate logic (check for existing utils/hooks)
- [ ] Proper separation of concerns
- [ ] No circular dependencies introduced

#### Test & Quality Checks (MEDIUM/LOW)

- [ ] `data-testid` on new interactive elements (per TEST_ID_CONTRACT)
- [ ] Unit tests for new logic
- [ ] CHANGELOG updated for significant changes
- [ ] No commented-out code
- [ ] No TODO without Linear issue reference

#### Acceptance Criteria Validation (HIGH)

**If ACCEPTANCE_CRITERIA exists from Step 3:**

For each AC bullet:
1. Check if the diff addresses it
2. Mark as: implemented / partial / missing / can't verify

```
AC Validation:
- [x] "User can click WhatsApp button" → WhatsAppButton.tsx added, onClick handler present
- [~] "Button appears on all templates" → Only added to ProductPage, missing CartPage
- [ ] "Analytics event on click" → No analytics code found in diff
```

**Any "missing" AC = HIGH severity finding.**

### Step 6 — Determine Review Decision

Based on findings:

| Condition | Decision | Action |
|-----------|----------|--------|
| Any CRITICAL finding | REQUEST_CHANGES | Block merge |
| Any HIGH finding | REQUEST_CHANGES | Block merge |
| Only MEDIUM/LOW | COMMENT | Approve with notes |
| No findings | APPROVE | Clean approval |
| AC partially met | REQUEST_CHANGES | List missing AC |
| AC fully met + no HIGH+ | APPROVE | Approve with AC confirmation |

### Step 7 — Post Review on GitHub

**Format the review body:**

```markdown
## PR Review: {PR_TITLE}

**Decision:** {APPROVE | REQUEST_CHANGES | COMMENT}
**Linear:** {LINEAR_ID} | **AC:** {X/Y met}

### Findings

#### CRITICAL
- {finding with file:line reference}

#### HIGH
- {finding with file:line reference}

#### MEDIUM
- {finding}

#### LOW
- {finding}

### Acceptance Criteria
- [x] {AC 1} — implemented
- [~] {AC 2} — partial: {detail}
- [ ] {AC 3} — missing

### Summary
{1-2 sentence summary of overall assessment}
```

**Post to GitHub:**

```bash
# If APPROVE
gh pr review {PR_NUMBER} --approve --body "{REVIEW_BODY}"

# If REQUEST_CHANGES
gh pr review {PR_NUMBER} --request-changes --body "{REVIEW_BODY}"

# If COMMENT (no findings warrant blocking)
gh pr review {PR_NUMBER} --comment --body "{REVIEW_BODY}"
```

### Step 8 — Sync Linear State

**If LINEAR_ID exists:**

| PR Review Decision | Current Linear State | New Linear State |
|-------------------|---------------------|-----------------|
| PR just opened | In Progress | In Review |
| APPROVE | In Review | Resolved |
| REQUEST_CHANGES | In Review | In Progress |
| PR merged | any | Testing |
| PR closed (not merged) | any | To Do |

**Update Linear issue state:**
```
save_issue(id: "{LINEAR_ID}", state: "{NEW_STATE}")
```

**Add Linear comment:**
```
create_comment(
  issueId: "{LINEAR_ID}",
  body: "## PR Review: #{PR_NUMBER}\n\n**Decision:** {DECISION}\n**AC:** {X/Y met}\n\n{SUMMARY}\n\n[View PR]({PR_URL})"
)
```

**If sub-issue with parent:**
Check if all sibling sub-issues are Done/Resolved → if yes, update parent state.

### Step 9 — Report to User

Output structured result:

```
PR #{PR_NUMBER}: {PR_TITLE}
Branch: {BRANCH_NAME} → {BASE_BRANCH}
Linear: {LINEAR_ID} ({ISSUE_STATE} → {NEW_STATE})
CI: {CI_STATUS}

Review: {DECISION}
├── CRITICAL: {count}
├── HIGH: {count}
├── MEDIUM: {count}
└── LOW: {count}

AC: {X}/{Y} met
{list of unmet AC if any}

{top 3 most important findings}

Actions taken:
✓ GitHub review posted
✓ Linear state → {NEW_STATE}
✓ Linear comment added
```

## Error Handling

### No PR Found
```
No open PR found for {input}.
Tip: Make sure the PR exists and you have access. Try `gh pr list` to see open PRs.
```

### No Linear ID
```
⚠️ No Linear issue ID found in branch name or PR body.
Review will proceed without Linear sync.
Tip: Use branch format `feature/SKY-123/description` or add "Closes SKY-123" to PR body.
```

### CI Failing
```
⚠️ CI checks failing:
- {check name}: {status}
Include CI failures as HIGH severity findings in review.
```

### Large Diff (>1000 lines)
```
Large PR detected ({N} files, {additions}+/{deletions}-).
Focusing review on:
1. New files
2. Security-sensitive paths (auth, API, middleware)
3. Files with most changes
Recommendation: Consider splitting this PR.
```

## Integration with Pipeline

```
/shape → /refine → /dev → /push_it → /ship_it (calls /pr-review → fix → merge → verify)
                                                            ↑
                                                  /pr-review runs here (also standalone)
```

After `/review`:
- If APPROVE → human can merge, or use `gh pr merge`
- If REQUEST_CHANGES → agent/dev fixes, pushes, re-run `/review`
- On merge → Linear moves to Testing automatically

## Example Session

```
User: /review #47

Mentat:
├── Fetches PR #47: "SKY-45: Add WhatsApp button"
├── Branch: feature/SKY-45/pixel-20250118
├── Linear ID: SKY-45
├── Loads SKY-45: 3 acceptance criteria
├── Reads diff: 4 files, +180/-12
│
├── Review:
│   ├── CRITICAL: 0
│   ├── HIGH: 1 — Missing auth check on /api/whatsapp endpoint
│   ├── MEDIUM: 2 — console.log L45, missing data-testid on icon
│   └── LOW: 1 — Consider extracting phone formatter util
│
├── AC: 2/3 met
│   ├── [x] Button component renders
│   ├── [x] Opens WhatsApp with pre-filled message
│   └── [ ] Analytics event on click — not implemented
│
├── Decision: REQUEST_CHANGES
├── Posted review on GitHub
├── Linear SKY-45: In Review → In Progress
└── Linear comment added

Next: Fix HIGH finding + missing AC, push, then `/review #47` again.
```
