# ADW Command Architecture Analysis

## Executive Summary

The Scout → Plan → Build workflow uses a **modular command system** with three tiers:
1. **Slash commands** (.claude/commands/*.md) — high-level orchestration
2. **ADW shims** (adws/adw_*.py) — workflow entry points with state management
3. **Module layer** (adw_modules/*) — reusable operations (agent exec, git, GitHub API)

---

## 1. SCOUT COMMAND: Evolution & Key Patterns

### Original (`scout.md` — 27 lines)
- **Focus**: Basic search task for subagents
- **Subagent model**: Fixed to external tools (gemini, opencode, codex, claude)
- **Output**: Simple file list with `<path> (offset: N, limit: M)` format
- **No structured JSON output**

**Location**: `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/scout.md:1-27`

### Improved (`scout_improved.md` — 73 lines)
**Key Changes**:
- ✅ **Frontmatter added** (lines 1-4): Model specification + allowed tools
- ✅ **Explicit parallel execution** (lines 26-31): Task tool spawns N agents in parallel
- ✅ **Structured output format** (lines 54-72): JSON schema with reason, key_findings
- ✅ **Clear subagent instructions** (lines 32-46):
  - 3-minute timeout enforcement (line 37)
  - Format validation (line 40-42)
  - Skip failures without retry (line 37)
- ✅ **Git safety check** (line 48): `git diff --stat` + `git reset --hard` on changes

**Location**: `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/scout_improved.md:1-73`

### Data Flow Pattern
```
SCOUT COMMAND
  ├─ Parse USER_PROMPT + SCALE (default 4)
  ├─ Task tool (parallel) → spawn N subagents
  │  └─ Each: Bash tool → external coder (gemini/opencode/codex/claude)
  │     └─ Return: <path> (offset: N, limit: M) lines
  ├─ Aggregate + validate format
  ├─ Git safety: git diff --stat && git reset --hard
  └─ Write agents/scout_files/relevant_files.json
     ├─ files[].path, reason, offset, limit
     └─ key_findings { summary, gaps, recommendations }
```

---

## 2. PLAN COMMANDS: Improvements & Approach

### Original (`plan_w_docs.md` — 20 lines)
- **Simple template**: Analyze → Scrape → Design → Document
- **No structured plan template**
- **No parallel doc scraping**
- **Minimal validation**

**Location**: `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/plan_w_docs.md:1-20`

### Improved (`plan_w_docs_improved.md` — 92 lines)
**Key Changes**:
- ✅ **Allowed tools specified** (line 2): Limits scope to Read, Write, Edit, Glob, Grep, MultiEdit
- ✅ **THINK HARD phase** (line 32): Explicit deep analysis of requirements
- ✅ **Parallel doc scraping** (line 33): Task tool for concurrent firecrawl/webfetch
- ✅ **8-section plan template** (lines 44-87):
  - Summary, Problem Statement, Inputs, Architecture/Approach
  - Implementation Steps (multi-step format)
  - Testing Strategy, Risks & Mitigation, Success Criteria
- ✅ **Input validation** (lines 20-21): Stop if USER_PROMPT/DOCS/FILES missing
- ✅ **Kebab-case filename generation** (line 36)
- ✅ **Clear report section** (lines 89-92)

**Location**: `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/plan_w_docs_improved.md:1-92`

### Data Flow Pattern
```
PLAN COMMAND
  ├─ Parse USER_PROMPT, DOCUMENTATION_URLS, RELEVANT_FILES_COLLECTION
  ├─ VALIDATE inputs (stop if missing)
  ├─ READ relevant_files.json (structure: <path> (offset: N, limit: M))
  ├─ THINK HARD: Analyze USER_PROMPT deeply
  ├─ Task tool (parallel) → Scrape each DOC_URL
  │  ├─ Via firecrawl OR webfetch
  │  └─ Save excerpts to ai_docs/
  ├─ Design solution (integrate with existing files)
  └─ Write specs/<kebab-case-title>.md
     ├─ 8-section structure (summary through success criteria)
     └─ Return: full path to plan file
```

---

## 3. AGENT SPAWNING: Task Tool Patterns

### Key Files
- **Agent executor**: `adws/adw_modules/agent.py:175-299`
- **Template requests**: `adws/adw_modules/data_types.py:27-46` (SlashCommand types)
- **Workflow ops**: `adws/adw_modules/workflow_ops.py:1-50` (agent names & model mapping)

### Pattern: Task → Bash → External Tool
**Example from scout_improved.md:26-31**:
```
Task tool with prompt:
  ├─ Spawn subagent_1 (gemini)
  ├─ Spawn subagent_2 (opencode)
  ├─ Spawn subagent_3+ (codex, claude)
  └─ Each immediately calls Bash with:
      bash: gemini -p "[prompt]" --model gemini-2.5-flash-preview-09-2025
      bash: opencode run [prompt] --model cerebras/qwen-3-coder-480b
      bash: codex exec -m gpt-5-codex -s read-only ...
      bash: claude -p "[prompt]" --model haiku
```

### Internal Agent Execution (ADW Shims)
**File**: `adws/adw_modules/agent.py:175-299`

1. **`prompt_claude_code(request: AgentPromptRequest)`** (lines 175-259)
   - Builds: `[CLAUDE_PATH, "-p", request.prompt, "--model", model, "--output-format", "stream-json", "--verbose"]`
   - Redirects stdout to JSONL file
   - Parses result message (type=="result", is_error flag, session_id)
   - Handles error_during_execution subtype (line 229-233)

2. **`execute_template(request: AgentTemplateRequest)`** (lines 262-299)
   - Maps slash command → model (line 265-270): `/bug` → "opus", `/chore` → "sonnet"
   - Constructs prompt: `f"{slash_command} {' '.join(args)}"`
   - Creates output_dir at `agents/{adw_id}/{agent_name}/`
   - Calls `prompt_claude_code()` with dangerously_skip_permissions=True

**Location**: `adws/adw_modules/agent.py:175-299`

### Model Selection Mapping
**File**: `adws/adw_modules/agent.py:27-52`
```python
SLASH_COMMAND_MODEL_MAP = {
    "/feature", "/bug", "/implement", "/review", "/patch": "opus"      # Complex
    "/chore", "/test", "/classify_issue", "/commit", "/document": "sonnet"  # Standard
}
```

---

## 4. DATA FLOW: Scout → Plan → Build

### Phase 1: Scout
```
INPUT:  USER_PROMPT ("Add feature X"), SCALE (4)
OUTPUT: agents/scout_files/relevant_files.json
  {
    "task": "...",
    "timestamp": "ISO-8601",
    "files": [
      { "path": "src/auth.py", "reason": "...", "offset": 15, "limit": 100 }
    ],
    "key_findings": { "summary": "...", "gaps": "...", "recommendations": "..." }
  }
```

### Phase 2: Plan
```
INPUT:
  USER_PROMPT ("Add feature X")
  DOCUMENTATION_URLS (space/comma-separated)
  RELEVANT_FILES_COLLECTION (path to scout JSON)

OUTPUT: specs/<kebab-case-title>.md
  # Plan: Feature X
  ## Summary
  ## Problem Statement
  ## Inputs (scout results + doc references)
  ## Architecture/Approach
  ## Implementation Steps (Step 1, 2, 3, ...)
  ## Testing Strategy
  ## Risks and Mitigation
  ## Success Criteria
```

### Phase 3: Build
```
INPUT:  Plan file (specs/<kebab-case-title>.md)
        ADW ID (for state management)

INTERNAL FLOW:
  1. Load state (adw_id) → find plan_file
  2. Parse plan file + extract Implementation Steps
  3. Call /implement slash command → execute via Claude
  4. Commit changes + push branch
  5. Create/update PR

OUTPUT: ai_docs/build_reports/<slug>-build-report.md
  - Git diff --stat
  - Files created/modified
  - Implementation notes
  - Status (✅/❌)
```

**Location**:
- `adws/adw_plan.py:149-196` (build_plan → execute_template)
- `adws/adw_build.py:61-100+` (implement_plan → execute_template)
- `adws/adw_modules/workflow_ops.py:149-202` (build_plan, implement_plan)

---

## 5. KEY SAFETY PATTERNS

### Git Operations (`adws/adw_modules/git_ops.py`)

| Operation | Pattern | Safety Check |
|-----------|---------|--------------|
| **Create branch** | `git checkout -b <name>` | Check if exists, fallback to checkout (lines 55-74) |
| **Commit** | `git add -A && git commit -m "..."` | Verify changes exist first (lines 77-100) |
| **Push** | `git push -u origin <branch>` | Return error message, no force (lines 24-32) |
| **Scout cleanup** | `git diff --stat && git reset --hard` | Audit changes, reset if any (scout_improved.md:48) |

**Location**: `adws/adw_modules/git_ops.py:15-80+`

### Timeout & Error Handling

| Context | Timeout | Strategy |
|---------|---------|----------|
| **Subagent (Task)** | 3 minutes | Skip on timeout, don't retry (scout_improved.md:37) |
| **Claude Code CLI** | 5 minutes | Return error response (agent.py:252-255) |
| **JSON parse** | N/A | Return [] + None if error (agent.py:104-106) |
| **Subprocess** | N/A | Catch FileNotFoundError, return error response (agent.py:68-80) |

### Validation Layers

1. **Input validation** (plan_w_docs_improved.md:20-21)
   - Stop if USER_PROMPT/DOCS/FILES missing

2. **Format validation** (scout_improved.md:40-46)
   - Skip malformed subagent output
   - Don't attempt correction

3. **State validation** (adw_plan.py:88-93, 203-220)
   - Check plan_file exists before proceeding
   - Validate state.get("adw_id") present

4. **Git safety** (adw_modules/git_ops.py:78-100)
   - Check for changes before commit
   - Error on push failures (no force)

**Location**: `adws/adw_modules/git_ops.py`, `adws/adw_plan.py:200-220`, `scout_improved.md:40-48`

---

## 6. DIRECTORY STRUCTURE & Artifact Organization

```
scout_plan_build_mvp/
├── .claude/commands/
│  ├── scout.md (original 27L) → scout_improved.md (improved 73L)
│  ├── plan_w_docs.md (original 20L) → plan_w_docs_improved.md (improved 92L)
│  ├── scout_plan_build.md (composite)
│  └── scout_plan_build_improved.md (enhanced reporting)
├── adws/
│  ├── adw_plan.py (entry: issue → plan file)
│  ├── adw_build.py (entry: plan file → implementation)
│  ├── adw_test.py, adw_review.py, adw_document.py (phase commands)
│  ├── adw_plan_build.py, adw_plan_build_test.py (composite flows)
│  ├── adw_modules/
│  │  ├── agent.py (execute_template, prompt_claude_code)
│  │  ├── workflow_ops.py (build_plan, implement_plan, classify_issue)
│  │  ├── git_ops.py (create_branch, commit_changes, push_branch)
│  │  ├── github.py (fetch_issue, make_issue_comment, GitHub API)
│  │  ├── state.py (ADWState: persistent workflow state)
│  │  ├── data_types.py (GitHubIssue, SlashCommand types, ADWWorkflow)
│  │  └── utils.py (setup_logger, get_safe_subprocess_env)
│  └── adw_tests/, adw_triggers/
├── agents/
│  └── scout_files/relevant_files.json ← SCOUT output
├── specs/
│  └── <kebab-case-title>.md ← PLAN output
└── ai_docs/
   ├── build_reports/<slug>-build-report.md ← BUILD output
   └── reviews/<slug>-review.md ← REVIEW output (optional)
```

---

## 7. Comparison Matrix: Original vs Improved

| Aspect | Original | Improved | Impact |
|--------|----------|----------|--------|
| **Scout parallelism** | Implicit | Explicit Task tool (lines 26-31) | Clearer execution model |
| **Scout output** | Plain list | Structured JSON (lines 54-72) | Machine-parseable results |
| **Plan template** | Vague | 8-section structure (lines 44-87) | Consistent deliverables |
| **Doc scraping** | Sequential | Parallel Task tool (line 33) | Faster doc integration |
| **Error handling** | Silent skip | Explicit format validation (line 40-46) | Better debugging |
| **Plan validation** | None | Input check (lines 20-21) | Fail-fast on missing data |
| **Build reporting** | Minimal | Comprehensive sections (scout_plan_build_improved.md:38-79) | Clear status tracking |
| **Git safety** | Absent | `git diff --stat` + reset (scout_improved.md:48) | Workspace hygiene |

---

## 8. Key Integration Points

### Webhook Loop Prevention (`adw_modules/github.py`)
- **ADW_BOT_IDENTIFIER**: String prefix to prevent recursive issue comments
- Used in `format_issue_message()` (workflow_ops.py:44-51)

### State Persistence (`adw_modules/state.py`)
- Stores per-ADW-ID workflow state (JSON file at `agents/{adw_id}/state.json`)
- Tracks: issue_number, branch_name, plan_file, issue_class, etc.
- Used for resuming interrupted workflows

### Model Selection
- `/feature`, `/bug` → opus (complex tasks)
- `/chore`, `/test` → sonnet (standard tasks)
- See `agent.py:27-52`

---

## Recommended Next Steps

1. **Deploy improved commands**: Replace original scout/plan with improved versions
2. **Add test scenarios**: Validate parallel execution, JSON output, error recovery
3. **Document subagent contract**: Formalize external tool interface
4. **Implement patch applier**: Safe file-range-bounded edits in adw_build.py
5. **Add GH integration**: Post build reports as PR comments (--post-to-gh flag)

---

**Analysis Date**: 2025-10-20
**Analyzed By**: Claude Code Architecture Review
**Files Scanned**: 18 (commands, shims, modules, types)
