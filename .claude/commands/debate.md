---
description: Invoke Forge (GPT-5) or Mycelium (Gemini 2.5) for technical review and feedback
---

# /debate Command

Invokes **Forge** (AI Engineering Architect, GPT-5) or **Mycelium** (AI Systems Architect, Gemini 2.5) to provide technical feedback, alternative perspectives, and system-wide consistency checks.

## Purpose

Enable collaborative debate between Mentat (Claude 4.5 - planning) and other Core Agents to produce higher-quality decisions through adversarial review and holistic system analysis.

## Usage

```bash
/debate [file_path] [agent]
```

**Arguments:**
- `file_path`: Path to document to review (PRD, architecture doc, implementation plan, code file)
- `agent`: Optional. Target agent for the review.
  - `forge` (Default): Focus on execution, code quality, performance, risks.
  - `mycelium`: Focus on system architecture, integration, PRD completeness, consistency.

**Examples:**
```bash
# Default (Forge) - for execution/technical review
/debate docs/projects/client-x/IMPLEMENTATION_PLAN.md

# Explicit Forge invocation
/debate src/api/endpoints.py forge

# Mycelium - for PRD or System Architecture review
/debate docs/projects/client-x/PRD.md mycelium
/debate docs/projects/client-x/ARCH.md mycelium
```

## Flow

```
1. Mentat reads the document at [file_path]
   ↓
2. Mentat determines target agent (Forge or Mycelium)
   ↓
3. Mentat invokes appropriate script:
   Forge    → python3 .claude/scripts/invoke_forge.py [file] [type]
   Mycelium → python3 .claude/scripts/invoke_mycelium.py [file] [type]
   ↓
4. Script calls CLI (Codex or Gemini) with specialized prompt
   ↓
5. Agent analyzes document and generates feedback
   Output: [file_path]-[agent]-feedback.md (or -output.md)
   ↓
6. Mentat reads feedback document
   ↓
7. Mentat incorporates valuable feedback into original document
   ↓
8. Mentat deletes temporary feedback file
   ↓
9. Mentat presents refined document to user
```

## When to Use Which Agent

### 🏗️ Invoke Forge (Execution)
**Best for:**
- Implementation Plans
- Code Review & Refactoring
- Performance Optimization
- Security & Risk Assessment
- "How do we build this efficiently?"

### 🍄 Invoke Mycelium (Systems)
**Best for:**
- Product Requirements Documents (PRDs)
- System Architecture & Integration
- Cross-project Consistency
- Workflow Design
- "Does this make sense for the whole ecosystem?"

## Execution Instructions (for Mentat)

When user invokes `/debate [file] [agent]`:

### Step 1: Read and Validate
```
1. Read the file at [file_path]
2. Validate file exists and is readable
3. Determine document type and target agent
```

### Step 2: Invoke Agent
```
4. Execute appropriate script:
   If Forge (default):
   python3 .claude/scripts/invoke_forge.py "[file_path]" "[doc_type]"
   
   If Mycelium:
   python3 .claude/scripts/invoke_mycelium.py "[file_path]" "[doc_type]"

5. Wait for script to complete
6. Check for feedback file:
   - Forge: [file_path]-forge-feedback.md
   - Mycelium: [file_path]-mycelium-output.md
```

### Step 3: Process Feedback
```
7. Read feedback document
8. Analyze feedback quality and relevance
9. Identify HIGH priority issues
```

### Step 4: Incorporate Feedback
```
10. Update original document with:
    - Fixes for HIGH priority issues
    - Considerations for MEDIUM priority
    - Alternative approaches
11. Maintain original document style
```

### Step 5: Clean Up and Present
```
12. Delete temporary feedback file
13. Present refined document to user with summary of the debate/review.
```

## Output Format (for User)

```markdown
## Debate Results: [Document Name]
### [Agent Name]'s Assessment
[Summary of feedback]

### Key Changes Made
1. [Change 1]
2. [Change 2]

### Validated Decisions
- [Point 1]
- [Point 2]

### Updated Document
[Link or status]
```

## Configuration

**Scripts:**
- `.claude/scripts/invoke_forge.py` (requires `codex` CLI)
- `.claude/scripts/invoke_mycelium.py` (requires `gemini` CLI)

**Context Files:**
- `AGENTS.md` (for Forge)
- `GEMINI.md` (for Mycelium)
