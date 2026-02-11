---
skill: adversarial-review
trigger: Use when Mentat needs to decide whether to invoke Forge (GPT-5) or Mycelium (Gemini 2.5) for technical review and adversarial feedback
model: sonnet
---

# Adversarial Review (Debate Invocation)

**Purpose:** Guide Mentat's decisions on when and how to invoke Forge (GPT-5) or Mycelium (Gemini 2.5) for technical review, adversarial feedback, and system-wide consistency checks.

**Scope:** Technical review workflows, architectural validation, and collaborative decision-making with external AI agents.

**Reference:** `.claude/commands/debate.md` - Always follow the debate command protocol.

## Forge (GPT-5) Invocation Protocol

Mentat must invoke Forge (via `/debate` or direct) when:

### Mandatory Invocation (High-Stakes) ✅

**Always invoke Forge for:**
- ✅ Finalizing PRDs for projects >$5K
- ✅ Complex architectural decisions (microservices, distributed systems, etc.)
- ✅ Changes affecting critical performance or scalability
- ✅ Complex algorithm design or heavy mathematical calculations
- ✅ Security decisions (auth, encryption, data handling)
- ✅ Database schema changes affecting multiple systems
- ✅ Breaking changes to public APIs
- ✅ Production-critical bugs (P0)
- ✅ Data corruption or security vulnerabilities

**Rationale:** High-stakes decisions require adversarial review to catch risks Mentat might miss.

### Recommended Invocation (Complex Decisions) 🟡

**Strongly consider invoking Forge for:**
- 🟡 New architectures Mentat hasn't implemented before
- 🟡 Technical trade-offs with multiple viable options
- 🟡 Complex debugging requiring deep analysis
- 🟡 Critical code optimization (hot paths, N+1 queries, etc.)
- 🟡 Implementation plans >2 weeks
- 🟡 Refactoring large codebases (>1000 LOC)
- 🟡 Performance-critical features (real-time, high-throughput)
- 🟡 Payment flows and financial transactions
- 🟡 Real-time features (WebSockets, polling, SSE)

**Rationale:** Complex decisions benefit from Forge's execution-focused perspective.

### Optional Invocation (Nice to Have) 🔵

**Consider invoking Forge for:**
- 🔵 Code review before merge to production
- 🔵 Second opinion when Mentat is unsure
- 🔵 Exploration of technical alternatives
- 🔵 Validation of implementation approach
- 🔵 Review of test coverage strategy

**Rationale:** Optional but valuable for quality assurance.

### Do NOT Invoke (Waste of Time) ❌

**Never invoke Forge for:**
- ❌ Simple decisions already industry-consensus
- ❌ Typos, formatting, simple documentation
- ❌ Early drafts (invoke when document is >70% complete)
- ❌ Business strategy without substantial technical component
- ❌ Routine CRUD operations
- ❌ Simple bug fixes (<1 hour work)
- ❌ Copy-paste implementations from well-documented libraries
- ❌ Aesthetic preferences (color palette, font choices)
- ❌ Easily reversible decisions

**Rationale:** Forge's time is valuable; use it for decisions that matter.

## Mycelium (Gemini 2.5) Invocation Protocol

Mentat should invoke Mycelium (via `/debate` with `mycelium` agent) when:

### When to Invoke Mycelium 🍄

**Best for:**
- 🍄 System Architecture & Integration - cross-project consistency
- 🍄 Workflow Design - holistic system analysis
- 🍄 Cross-project dependencies and integration points
- 🍄 System-wide consistency checks

**Rationale:** Mycelium focuses on system architecture, integration and cross-project consistency.

### When NOT to Invoke Mycelium ❌

- ❌ Code review (use Forge)
- ❌ Implementation details (use Forge)
- ❌ Performance optimization (use Forge)
- ❌ Simple features without system impact

## Invocation Methods

### Via `/debate` Command (Preferred)

```bash
# Default (Forge) - for execution/technical review
/debate path/to/document.md

# Explicit Forge invocation
/debate path/to/document.md forge

# Mycelium - for PRD or System Architecture review
/debate path/to/document.md mycelium
```

**Process:**
1. Mentat prepares document for review (must be >70% complete)
2. Determines target agent (Forge or Mycelium) based on document type
3. Invokes agent via `/debate` command
4. Agent generates structured feedback following feedback template
5. Mentat incorporates feedback into document
6. Mentat deletes temporary feedback file
7. Mentat presents refined document to user

**Use for:**
- **Forge:** PRDs, architecture docs, implementation plans, technical proposals, code review
- **Mycelium:** PRDs, system architecture docs, workflow design, integration planning

### Via Direct Script Invocation

```bash
# Forge
python3 .claude/scripts/invoke_forge.py "path/to/document.md" "PRD"

# Mycelium
python3 .claude/scripts/invoke_mycelium.py "path/to/document.md" "PRD"
```

**Use for:** Custom scenarios or when `/debate` command is not available

## Expected Behavior

### Step 1: Mentat Prepares Document

**Document requirements:**
- Must be >70% complete
- Clear problem statement
- Proposed solution with rationale
- Trade-offs identified
- Options considered (minimum 2-3 for Forge)
- Tentative recommendation from Mentat

**Document types:**
- PRDs (Product Requirements Documents)
- Architecture documents
- Implementation plans
- Technical proposals
- Code files (for review)

### Step 2: Mentat Invokes Agent

**For Forge:**
- Provides clear context
- Specifies what needs review
- Highlights areas of concern
- Focuses on execution, code quality, performance, risks

**For Mycelium:**
- Provides system context
- Highlights integration points
- Focuses on consistency and completeness
- Emphasizes cross-project considerations

### Step 3: Agent Generates Feedback

**Forge feedback structure:**
- Executive summary
- Strengths
- Concerns (high/medium/low priority)
- Alternative approaches with pros/cons
- Specific recommendations
- Technical notes

**Mycelium feedback structure:**
- System-wide consistency check
- Integration points analysis
- PRD completeness assessment
- Cross-project dependencies
- Workflow design validation

### Step 4: Mentat Incorporates Feedback

- Updates original document
- Addresses high-priority concerns first
- Documents decisions made
- Maintains original document style
- Preserves valuable insights

### Step 5: Mentat Presents Refined Document

- Shows changes made
- Explains rationale for decisions
- Highlights remaining open questions
- Summarizes debate/review results

## Decision Framework

### When to Invoke Which Agent

**Decision tree:**

1. **What type of document?**
   - PRD or System Architecture → Consider **Mycelium**
   - Implementation Plan or Code → Consider **Forge**

2. **What's the primary concern?**
   - System consistency, integration → **Mycelium**
   - Execution, performance, risks → **Forge**

3. **Is this high-stakes AND system-wide?**
   - Yes → **Invoke both** (Forge first, then Mycelium)
   - No → Continue evaluation

4. **Is this high-stakes?**
   - Yes → **Mandatory invocation** (usually Forge)
   - No → Continue evaluation

5. **Is this complex?**
   - Yes → **Recommended invocation**
   - No → **Optional invocation** or skip

6. **Is document >70% complete?**
   - No → Wait, don't invoke yet
   - Yes → Proceed

### When to Invoke Both Agents

**Invoke both Forge and Mycelium when:**
- ✅ High-stakes system architecture (e.g., payment systems, distributed systems)
- ✅ Architecture decisions affecting multiple projects
- ✅ Complex integrations requiring both execution review and system consistency
- ✅ Critical workflows with cross-project dependencies

**Process:**
1. Invoke Forge first (execution and risk focus)
2. Incorporate Forge feedback
3. Invoke Mycelium second (system consistency and integration)
4. Incorporate Mycelium feedback
5. Present refined document with both perspectives addressed

### When to Invoke Forge vs Mycelium

| Scenario | Agent | Reason |
|----------|-------|--------|
| Architecture design | Forge | Execution and risk focus |
| Cross-project integration | Mycelium | Holistic system view |
| Implementation plan | Forge | Execution quality |
| Workflow design | Mycelium | System consistency |
| Code review | Forge | Code quality and performance |
| Performance optimization | Forge | Execution expertise |

## Examples

### Example 1: Dual Invocation (Forge + Mycelium)

```
User: "Necesito diseñar la arquitectura de un sistema distribuido para procesar pagos"
→ Mentat identifies: 
  - Complex architectural decision (high-stakes, payment system) → Forge needed
  - System architecture with cross-project impact → Mycelium needed
→ Prepares architecture document (>70% complete)
→ Invokes Forge first: /debate docs/projects/payment/ARCH.md forge
  → Forge reviews: Execution risks, performance, security, scalability
  → Provides feedback on: Payment flow risks, database design, API contracts
→ Mentat incorporates Forge feedback
→ Invokes Mycelium second: /debate docs/projects/payment/ARCH.md mycelium
  → Mycelium reviews: System integration, cross-project consistency, workflow design
  → Provides feedback on: Integration points with existing systems, consistency patterns
→ Mentat incorporates Mycelium feedback
→ Presents refined architecture to user with both perspectives addressed
```

**Rationale:** High-stakes payment system requires both execution review (Forge) and system-wide consistency (Mycelium).

### Example 2: Mycelium Invocation (System Integration)

```
User: "Necesito diseñar el workflow de integración entre el sistema de e-commerce y el ERP"
→ Mentat identifies: 
  - Workflow design with cross-system integration → Mycelium needed
  - System-wide consistency check required
  - Not high-stakes execution risk → Forge not needed
→ Prepares workflow design document (>70% complete)
→ Invokes Mycelium via /debate docs/projects/integration/WORKFLOW.md mycelium
→ Mycelium reviews workflow for:
  - Cross-project consistency (e-commerce ↔ ERP patterns)
  - Integration points and data flow
  - System-wide impact and dependencies
  - Workflow design alignment with existing patterns
→ Provides feedback on:
  - Integration patterns consistency
  - Data synchronization strategy
  - Error handling across systems
  - Workflow orchestration approach
→ Mentat incorporates feedback
→ Presents refined workflow design to user
```

**Rationale:** Workflow design focuses on system integration and consistency, which is Mycelium's strength.

### Example 3: Forge Invocation (Code Review)

```
User: "Revisa este código antes de merge a producción"
→ Mentat identifies: Code review, production merge
→ Invokes Forge via /debate src/api/endpoints.py forge
→ Forge reviews code quality, performance, security
→ Provides feedback on optimizations, edge cases, risks
→ Mentat incorporates feedback
→ Presents refined code to user
```

## Anti-patterns

❌ **Invoking for incomplete documents** - Document must be >70% complete
❌ **Invoking for simple decisions** - Use agents' time wisely
❌ **Skipping invocation for high-stakes decisions** - Always get adversarial review
❌ **Invoking wrong agent** - Forge for execution, Mycelium for system consistency
❌ **Not preparing document properly** - Must include context, options, trade-offs
❌ **Ignoring feedback** - Always incorporate high-priority concerns
❌ **Invoking too early** - Wait until document is substantial enough for meaningful review

## Key Principles

1. **Use Forge for execution** - Code quality, performance, risks, implementation
2. **Use Mycelium for systems** - PRD completeness, integration, consistency
3. **Prepare documents properly** - >70% complete, clear options, trade-offs
4. **Incorporate feedback** - Address high-priority concerns, document decisions
5. **Respect agent time** - Only invoke for decisions that matter
6. **Follow debate protocol** - Use `/debate` command, clean up temp files
7. **Document decisions** - Always explain why invocation was made and what changed

---

**Ready.** Use this skill when deciding whether to invoke Forge or Mycelium for technical review. Always follow the decision framework and respect the debate command protocol.

