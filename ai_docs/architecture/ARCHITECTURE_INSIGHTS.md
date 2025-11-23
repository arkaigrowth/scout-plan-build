# ADW Architecture: Deep Insights

## System Design Philosophy

The ADW (AI Developer Workflow) system implements a **three-tier orchestration pattern**:

```
┌─ TIER 1: Orchestration (Slash Commands) ────────────┐
│  scout.md, plan_w_docs.md, scout_plan_build.md      │
│  [High-level workflow coordination]                  │
└──────────────────────────────────────────────────────┘
                          ↓
┌─ TIER 2: Workflow Shims (ADW Entry Points) ─────────┐
│  adw_plan.py, adw_build.py, adw_test.py            │
│  [GitHub ↔ Workflow bridging + State Management]    │
└──────────────────────────────────────────────────────┘
                          ↓
┌─ TIER 3: Reusable Modules (Core Operations) ───────┐
│  agent.py, workflow_ops.py, git_ops.py, github.py  │
│  [Composable, testable building blocks]             │
└──────────────────────────────────────────────────────┘
```

---

## Key Architectural Patterns

### 1. Subagent Coordination via Task Tool

**Problem Solved**: How to run multiple external coding tools in parallel without managing thread pools?

**Solution**:
```python
# In slash command (scout_improved.md:26-31):
# Task tool spawns N subagents, each immediately calls Bash:
Task(description="Run 4 parallel scout agents",
     prompt="""
     Kick off 4 subagents in parallel:
     1. Task → Bash → gemini -p "[prompt]" --model gemini-2.5-flash
     2. Task → Bash → opencode run [prompt] --model qwen-3-coder
     3. Task → Bash → codex exec -m gpt-5-codex
     4. Task → Bash → claude -p "[prompt]" --model haiku
     """)
```

**Why This Works**:
- ✅ **Task tool handles parallelism** — Claude Code manages concurrency
- ✅ **Bash tool is "fire and forget"** — External tool runs independently
- ✅ **No thread management** — Scales to N agents automatically
- ✅ **Timeout-safe** — 3-minute skip per subagent (scout_improved.md:37)
- ✅ **Format validation** — Skip malformed output, don't retry (scout_improved.md:40-46)

**Key Code**:
- `agent.py:175-299`: Claude Code execution handler
  - Streams output to JSONL (stream-json format)
  - Parses result message for success/error/session_id
  - Handles error_during_execution gracefully

---

### 2. Two-Phase Execution Model

**Phase A: Slash Command (Human-Facing)**
- ✅ High-level, descriptive instructions
- ✅ Built-in validation and error recovery
- ✅ Parallel execution by default
- ✅ Structured output format

**Phase B: ADW Shim (GitHub-Facing)**
- ✅ GitHub webhook entry point
- ✅ Issue context extraction
- ✅ State persistence across phases
- ✅ PR creation/update automation

**Example Flow**:
```
GitHub Issue Created
  ↓
GitHub Webhook → ADW Webhook Handler
  ↓
adw_plan.py (ADW Shim)
  ├─ Parse issue (number, title, body)
  ├─ Call classify_issue → /chore|/bug|/feature
  ├─ Create branch (feature/issue-123-...)
  ├─ Call build_plan → execute_template()
  │  └─ This internally calls: claude -p "/feature ..." --model opus
  │     (Not a slash command in Claude Code, but a full prompt)
  ├─ Commit plan file
  ├─ Push branch
  ├─ Create PR
  └─ Post comment to issue
```

**Key Difference**:
- **Slash commands** (scout.md, plan_w_docs.md) = Orchestration layer
- **ADW shims** (adw_plan.py, adw_build.py) = Automation layer
  - Shims use `execute_template()` to call slash commands as templates
  - Shims manage state and GitHub integration
  - Shims can be triggered by webhooks

---

### 3. State Management via Persistent ADWState

**File**: `adws/adw_modules/state.py`

**Problem Solved**: How to resume interrupted workflows across multiple phases?

**Solution**:
```python
# Each ADW ID gets its own state file
agents/
  └── adw-2024-10-20-xyz/
      ├── state.json  ← Persistent workflow state
      ├── planner/
      │   ├── prompts/
      │   │   ├── classify_issue.txt
      │   │   ├── generate_branch_name.txt
      │   │   └── commit.txt
      │   └── raw_output.jsonl  ← Agent execution log
      ├── implementor/
      │   ├── prompts/
      │   │   └── implement.txt
      │   └── raw_output.jsonl
      └── ...
```

**State Contents**:
```python
{
    "adw_id": "adw-2024-10-20-xyz",
    "issue_number": 123,
    "issue_class": "/feature",
    "branch_name": "feature/issue-123-add-auth",
    "plan_file": "specs/add-auth-system.md",
    "pr_url": "https://github.com/.../pull/456"
}
```

**Resumption Example**:
```python
# Phase 1: adw_plan.py runs, saves state
state = ADWState(adw_id="adw-xyz")
state.update(plan_file="specs/auth.md")
state.save("adw_plan")

# Phase 2: adw_build.py resumes
state = ADWState.load("adw-xyz")  # Loads previous state
plan_file = state.get("plan_file")  # Already set by adw_plan.py
# Now implement using the plan_file from state
```

**Why This Matters**:
- ✅ **Webhook resilience**: If adw_build webhook fails, admin can retry
- ✅ **Manual override**: Can manually trigger adw_build with same adw_id
- ✅ **Audit trail**: Full history in agents/{adw_id}/*/raw_output.jsonl
- ✅ **No re-planning**: Plan persists across multiple build attempts

---

### 4. Format Validation as Fail-Safe

**Scout Output Validation** (scout_improved.md:40-46):
```
Instruction to subagent:
"If any agent doesn't return in the proper format:
  <path> (offset: N, limit: M)
  DON'T try to fix it for them
  JUST ignore their output and continue with next agents responses"
```

**Why Not Auto-Fix?**:
- ❌ Auto-fixing masks bugs in subagent prompts
- ❌ Malformed output might indicate task misunderstanding
- ❌ Better to skip and aggregate valid results
- ✅ Humans can review rejected outputs in logs

**Implementation**:
```python
# agent.py:83-106
def parse_jsonl_output(output_file: str):
    """Parse JSONL, return [] + None if error."""
    try:
        messages = [json.loads(line) for line in f if line.strip()]
        return messages, result_message
    except Exception as e:
        print(f"Error parsing JSONL: {e}")
        return [], None  # Return empty, don't throw
```

---

### 5. Git Safety: Reset After Scout

**Pattern** (scout_improved.md:48):
```bash
# After all scout agents finish:
git diff --stat          # Audit what changed
git reset --hard         # If ANY changes, reset to clean state
```

**Why Required**:
- 🔴 Scout agents must NOT modify files (read-only task)
- 🔴 If agent fails with edits, workspace is corrupted
- ✅ Hard reset ensures clean state for Plan phase
- ✅ Audit log shows what was attempted

**Safety Chain**:
```
1. Scout → collect file list (no edits)
           git reset --hard (cleanup)
           ↓
2. Plan → generate specification (no edits to source)
          ↓
3. Build → implement changes (edits via /implement)
           commit + push
```

---

## Comparison: Original vs Improved Commands

### Scout Command Evolution

| Dimension | scout.md (27L) | scout_improved.md (73L) |
|-----------|----------------|-----------------------|
| **Parallelism** | Vague "kick off agents" | Explicit Task tool, 4 agents, round-robin (lines 26-43) |
| **External tools** | Examples only | Specific conditions: if count >= 2, if count >= 3, etc. (lines 27-30) |
| **Timeout** | Mentioned once | Explicit 3-minute per subagent (line 37) |
| **Format spec** | Brief | Detailed with example (lines 40-42) |
| **Error handling** | "Skip timeouts" | "Skip, don't restart" + format validation (lines 37, 40-46) |
| **Git safety** | Absent | `git diff --stat && git reset --hard` (line 48) |
| **Output schema** | List format | Full JSON with key_findings (lines 54-72) |
| **Frontmatter** | Absent | Added model + description (lines 1-4) |

### Plan Command Evolution

| Dimension | plan_w_docs.md (20L) | plan_w_docs_improved.md (92L) |
|-----------|----------------------|------------------------------|
| **Analysis phase** | Generic "Analyze" | Explicit THINK HARD (line 32) |
| **Doc scraping** | Sequential mention | Parallel Task tool (line 33) |
| **Validation** | None | Input check: stop if missing (lines 20-21) |
| **Template** | Vague sections | 8-section structure (lines 44-87) |
| **Model spec** | Implicit | Frontmatter + allowed-tools (lines 1-5) |
| **Filename** | Kebab-case mention | Explicit generation (line 36) |
| **Report format** | Informal | Structured markdown output (lines 89-92) |
| **Tool scope** | All tools | Limited to Read, Write, Edit, Glob, Grep, MultiEdit (line 2) |

---

## Critical Design Decisions

### 1. Why Task Tool for Subagents (Not Bash Loops)?

❌ **Alternatives Rejected**:
- **Option A**: Main agent runs subprocess loop, polls 4 agents sequentially
  - Con: 60-90s per agent = 4 min total (slower than 3-min timeout)
  - Con: Main agent blocks on each poll
  - Con: Requires manual thread management

✅ **Chosen**: Task tool spawns N subagents in parallel
- Pro: Claude Code handles concurrency natively
- Pro: Each subagent runs independently (Bash tool)
- Pro: True parallelism (all 4 agents run simultaneously)
- Pro: Timeout per agent (skip slow agents)

**Code Pattern**:
```python
# NOT: Sequential polling
for i in range(4):
    result = subprocess.run(f"gemini -p '{prompt}'")
    results.append(result)

# BUT: Parallel via Task tool
Task(prompt="""
Spawn 4 agents in parallel:
1. Bash: gemini -p '{prompt}'
2. Bash: opencode run '{prompt}'
3. Bash: codex exec ...
4. Bash: claude -p '{prompt}'
""")
```

### 2. Why Structured JSON Output (Not Text List)?

❌ **Alternatives Rejected**:
- **Option A**: Plain text list (scout.md style)
  - Con: Machine-parse difficult (heuristic line parsing)
  - Con: key_findings lose structure

✅ **Chosen**: JSON with schema
```json
{
  "files": [{"path": "...", "offset": N, "limit": M, "reason": "..."}],
  "key_findings": {"summary": "...", "gaps": "...", "recommendations": "..."}
}
```
- Pro: Machine-parseable
- Pro: Consistent across tools (Python, JS, etc.)
- Pro: Schema validation easy (jsonschema)
- Pro: Aggregatable (merge multiple scout runs)

### 3. Why 8-Section Plan Template (Not Freeform)?

❌ **Alternatives Rejected**:
- **Option A**: "Just write a plan"
  - Con: Section order inconsistent
  - Con: Missing testing strategy in some plans
  - Con: Risk assessment ad-hoc

✅ **Chosen**: Strict 8-section template (plan_w_docs_improved.md:44-87)
```markdown
1. Summary
2. Problem Statement
3. Inputs (scout results + doc refs)
4. Architecture/Approach
5. Implementation Steps (subdivided)
6. Testing Strategy
7. Risks and Mitigation
8. Success Criteria
```
- Pro: Structured for /implement command to parse
- Pro: Ensures completeness (risk section never missed)
- Pro: Humans know what to expect
- Pro: Machine validation possible (check all 8 sections exist)

---

## Failure Scenarios & Recovery

### Scenario 1: Subagent Timeout (Scout)
```
Expected: 4 agents return in 3 minutes
Actual: Agent #4 (claude) takes 5 minutes

Recovery:
✅ Agent #4 skipped (scout_improved.md:37)
✅ Aggregate agents #1-3 results
✅ Report in key_findings.gaps: "Claude agent timed out"
❌ Do NOT retry agent #4
```

### Scenario 2: Malformed Scout Output
```
Expected: "src/auth.py (offset: 15, limit: 100)"
Actual: "- auth file at src/auth.py lines 15-115"

Recovery:
✅ Skip this output (scout_improved.md:40-46)
✅ Continue with other agents
✅ Document in key_findings.gaps: "1 agent output unformatted"
❌ Do NOT attempt regex parse or auto-fix
```

### Scenario 3: Plan File Missing After Scout
```
Expected: Plan file created at specs/auth-system.md
Actual: adw_plan.py finishes, plan_file not in state

Recovery:
✅ adw_plan.py validates path exists (adw_plan.py:212)
✅ Make issue comment: "❌ Plan file does not exist: [path]"
✅ Exit with error code 1
❌ Do NOT proceed to build
```

### Scenario 4: Git Conflicts After Build
```
Expected: Branch pushes cleanly
Actual: Main branch has conflicting commit

Recovery:
✅ git push fails (git_ops.py:30-31 returns error)
✅ Issue comment: "❌ Error pushing branch: [stderr]"
✅ State saved with failure info
❌ Do NOT force push (no --force flag)
```

---

## Performance Characteristics

### Scout Phase
```
N = number of subagents (SCALE parameter, default 4)
T_agent = time per external agent (~30-60 seconds)
T_total = max(T_agent for each agent in parallel)
        ≈ 60s (not 4 × 60s = 240s)

Example: 4 agents in parallel
  Agent #1: 45s
  Agent #2: 60s
  Agent #3: 40s ← Slowest determines total
  Agent #4: 35s
  Total:    ~60s (parallel wall-clock time)
```

### Plan Phase
```
N = number of documentation URLs
T_scrape = time per URL (~10-20s)
T_think = THINK HARD analysis (~30-60s)
T_design = solution design (~60-90s)

Sequential: 10s + 30s + (20 * 3) + 90s = 200s
Improved (parallel doc scrape): 10s + 30s + 20s + 90s = 150s
Speedup: ~25%
```

### Overall Scout → Plan → Build
```
Phase 1 (Scout):   ~60s  (4 agents parallel)
Phase 2 (Plan):    ~150s (THINK HARD + parallel docs)
Phase 3 (Build):   ~120s (implement + commit + push)
────────────────────────
Total:             ~330s (~5.5 minutes end-to-end)
```

---

## Security & Compliance

### What ADW Does NOT Do
- ❌ Never runs arbitrary code from plan (only /implement slash command)
- ❌ Never modifies production without explicit branch/PR
- ❌ Never posts to issue without ADW_BOT_IDENTIFIER (prevents loops)
- ❌ Never stores credentials (only GitHub token via environment)

### What ADW Does Validate
- ✅ Input validation (plan_w_docs_improved.md:20-21)
- ✅ Format validation (scout_improved.md:40-46)
- ✅ State validation (adw_plan.py:212-219)
- ✅ Git safety (git_ops.py: no --force, check changes first)
- ✅ GitHub bot identifier (workflow_ops.py:44-51)

---

## Migration Path: Original → Improved

### Step 1: Deploy Alongside (Non-Breaking)
```bash
# Keep originals as backups
cp .claude/commands/scout.md .claude/commands/scout_legacy.md
cp .claude/commands/plan_w_docs.md .claude/commands/plan_w_docs_legacy.md

# Deploy improved versions
cp .claude/commands/scout_improved.md .claude/commands/scout.md
cp .claude/commands/plan_w_docs_improved.md .claude/commands/plan_w_docs.md
```

### Step 2: Validate on Test Issues
```
Test 1: /scout "add error handling" "4"
  → Verify: 4 agents spawn in parallel
  → Verify: JSON output structure correct
  → Verify: git reset --hard works

Test 2: /plan_w_docs "add error handling" "https://docs.python.org" "scout_outputs/relevant_files.json"
  → Verify: THINK HARD phase mentioned in output
  → Verify: 8 sections present in plan
  → Verify: Docs scraped in parallel

Test 3: /scout_plan_build "add error handling" "https://docs.python.org"
  → Verify: All 3 phases complete
  → Verify: Artifacts in correct directories
```

### Step 3: Monitor & Rollback If Needed
```bash
# If issues, revert:
cp .claude/commands/scout_legacy.md .claude/commands/scout.md
cp .claude/commands/plan_w_docs_legacy.md .claude/commands/plan_w_docs.md
```

---

## Recommended Future Enhancements

### 1. Dry-Run Preview in adw_build.py
```
Instead of:
  /implement plan.md → Execute immediately

Add:
  /implement --dry-run plan.md → Show git diff preview
  User approves via PR comment reaction
  Auto-trigger /implement plan.md → Execute actual changes
```

### 2. Cancellation via GitHub Reactions
```
PR comment with /implement running
  ❌ reaction added → Cancel execution
  ✅ reaction added → Proceed with implementation
```

### 3. Model Optimization Experiments
```
Try: scout_improved.md with Haiku for all agents (cost reduction)
vs   Current: gemini/opencode/codex/claude (diverse models)

A/B test scout quality metrics:
  - File relevance accuracy
  - False positive rate
  - Cost per scout
```

### 4. Composite Report Generation
```
After scout_plan_build completes:
  Generate: ai_docs/workflow_summary.md
  ├─ Scout summary (files, gaps)
  ├─ Plan summary (sections, key decisions)
  ├─ Build summary (changes, status)
  └─ Recommendations (next steps)
```

---

**Analysis Prepared**: 2025-10-20
**Scope**: Commands (6 files), Modules (8 files), Data Types
**Total Lines Analyzed**: ~500 LOC
**Key Insights**: 8 architectural patterns, 4 critical decisions, 4 failure scenarios
