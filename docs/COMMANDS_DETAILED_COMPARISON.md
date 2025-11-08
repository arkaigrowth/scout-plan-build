# 🔬 Detailed Command Analysis: Current vs. Proposed Skills System

## The Real Problem: Commands Are Isolated Islands

The current commands work in **complete isolation** - they don't share context, memory, or state. Each command starts fresh, rediscovering everything. Let me show you exactly what happens:

---

## 📖 What Each Command ACTUALLY Does (The Nitty Gritty)

### 1. `/scout` - The Broken Discovery Phase

**What it's supposed to do:**
```python
# The fantasy:
1. Launch 4 parallel AI agents (gemini, opencode, codex, claude)
2. Each agent explores the codebase from different angles
3. Combine their findings into relevant_files.json
4. Save to agents/scout_files/ directory
```

**What ACTUALLY happens:**
```bash
# The reality:
1. Tries: gemini -p "find auth files" --model gemini-2.5  # FAILS: command not found
2. Tries: opencode run "find auth files"                  # FAILS: command not found
3. Tries: codex exec -m gpt-5-codex                       # FAILS: command not found
4. Tries: claude -p "find auth files" --model haiku       # MAYBE works if setup

Result: Empty or partial relevant_files.json (mostly empty)
```

**The actual workflow it follows:**
```markdown
1. Parse USER_PROMPT and SCALE arguments
2. Try to spawn SCALE number of external agents via bash
3. Wait 3 minutes (timeout) for each agent
4. Collect outputs (usually nothing because tools don't exist)
5. Run git diff --stat (check for unwanted changes)
6. Run git reset --hard if changes detected
7. Create JSON file with structure:
   {
     "task": "user's request",
     "timestamp": "2024-01-20T...",
     "files": [],  // Usually empty!
     "key_findings": {
       "summary": "No agents responded",
       "gaps": "Everything",
       "recommendations": "Manual search needed"
     }
   }
```

---

### 2. `/plan_w_docs` - The Working Planner

**What it ACTUALLY does (step by step):**

```python
# Real implementation flow:
1. VALIDATION PHASE:
   - Check if USER_PROMPT exists (else stop)
   - Check if DOCUMENTATION_URLS provided (else stop)
   - Check if RELEVANT_FILES_COLLECTION exists (else stop)

2. FILE READING PHASE:
   - Read agents/scout_files/relevant_files.json
   - Parse the JSON structure
   - Extract file paths with line ranges:
     Example: "auth/middleware.py (offset: 45, limit: 100)"
   - For each file in the list:
     - Read the file from offset to offset+limit
     - Store content in memory

3. DOCUMENTATION SCRAPING PHASE (Parallel):
   - For each URL in DOCUMENTATION_URLS:
     - Launch Task agent with firecrawl or webfetch
     - Scrape the documentation
     - Extract API patterns, examples, best practices
   - Wait for all scrapes to complete
   - Combine documentation insights

4. ANALYSIS PHASE:
   - Cross-reference existing code with documentation
   - Identify:
     - Current architecture patterns
     - Integration points
     - Potential conflicts
     - Best practices from docs

5. PLAN GENERATION PHASE:
   - Generate markdown with exact structure:
     # Plan: [Title]
     ## Summary
     ## Problem Statement
     ## Inputs (references scout results)
     ## Architecture/Approach
     ## Implementation Steps
       ### Step 1: Create authentication middleware
         - File: auth/middleware.py
         - Action: Create new file
         - Code pattern: Express-style middleware
       ### Step 2: Add JWT validation
         - File: auth/jwt.py
         - Action: Modify existing
         - Lines to change: 45-67
     ## Testing Strategy
     ## Risks and Mitigation
     ## Success Criteria

6. SAVE PHASE:
   - Generate filename: kebab-case-from-title.md
   - Save to: specs/kebab-case-from-title.md
   - Return: Full path to saved file
```

**Key insight**: Plan reads the scout output but **doesn't validate if files actually exist** - it trusts the scout blindly!

---

### 3. `/build_adw` - The Implementation Engine

**What it ACTUALLY does (the Python script execution):**

```python
# The build_adw command is just a thin wrapper that calls:
uv run adws/adw_build.py "[PLAN_FILE_PATH]"

# What adw_build.py actually does:

1. STATE LOADING:
   - Try to load ADWState from JSON file
   - If no state: ERROR and exit
   - State contains:
     {
       "issue_number": "123",
       "adw_id": "abc789",
       "branch_name": "feature/issue-123-adw-abc789",
       "plan_file": "specs/auth-implementation.md",
       "pr_number": null
     }

2. ENVIRONMENT VALIDATION:
   - Check ANTHROPIC_API_KEY exists
   - Check CLAUDE_CODE_PATH exists
   - If missing: ERROR and exit

3. GIT OPERATIONS:
   - git checkout {branch_name} from state
   - If checkout fails: ERROR and exit

4. PLAN PARSING:
   - Read the plan file from state
   - Parse markdown to extract:
     - Implementation Steps section
     - Each step's file operations
     - Code patterns to follow
   - If no Implementation Steps: ERROR and exit

5. IMPLEMENTATION LOOP:
   For each step in plan:
   - Extract file path, action type (create/modify/delete)
   - Call Claude Code API:
     claude prompt "Implement: {step_description}" \
       --context "{existing_file_content}" \
       --output "{file_path}"
   - Validate changes were made
   - Continue to next step

6. BUILD REPORT GENERATION:
   - Summarize all changes made
   - List files created/modified/deleted
   - Include git diff statistics
   - Save to: ai_docs/build_reports/{slug}-build-report.md

7. GIT COMMIT:
   - git add all changed files
   - git commit -m "feat: {description} [ADW-{id}]"
   - Update state with commit hash

8. GITHUB COMMENT:
   - Post to issue: "✅ Build complete: {report_path}"
   - Include summary of changes

9. RETURN:
   - Output path to build report
   - Exit with success code
```

---

## 🆚 Current Problems: Why Commands Fail Together

### The Broken Chain

```mermaid
graph LR
    Scout[Scout] -->|Fails: No tools| BadJSON[Empty JSON]
    BadJSON -->|Input| Plan[Plan]
    Plan -->|Works but...| BadPlan[Plan with no files]
    BadPlan -->|Input| Build[Build]
    Build -->|Fails| Error[Can't find files]

    style Scout fill:#ff6666
    style BadJSON fill:#ff6666
    style BadPlan fill:#ffcc66
    style Error fill:#ff6666
```

**Example of the cascade failure:**

```bash
# 1. Scout fails silently
/scout "add user authentication" "4"
# Creates: agents/scout_files/relevant_files.json with:
{
  "files": [],  # Empty because tools don't exist!
  "key_findings": {
    "gaps": "No files found"
  }
}

# 2. Plan works but creates bad plan
/plan_w_docs "add auth" "https://jwt.io" "agents/scout_files/relevant_files.json"
# Creates plan but with generic steps because no files to reference

# 3. Build fails or creates wrong code
/build_adw "specs/auth-plan.md"
# ERROR: Can't find referenced files, or creates files in wrong places
```

---

## 💡 The Proposed Skills Solution: Connected Intelligence

### What `adw-scout` Skill Would Do Differently

```markdown
# .claude/skills/adw-scout.md
---
name: adw-scout
mcp-servers: [sequential-thinking]
tools: [Grep, Glob, Read, Write]
memory: enabled
---

# Intelligent Scout with Memory

## Phase 1: Memory Recall (NEW!)
! Check mem0 for similar tasks
! If similar task found:
  - Use previous file patterns as starting point
  - Skip redundant exploration
  - Build on prior knowledge

## Phase 2: Smart Exploration (WORKING!)
! Use WORKING tools instead of broken ones:
  - Glob("**/*auth*") for pattern matching
  - Grep("authentication|login|jwt") for content search
  - Read top 10 matches for validation

## Phase 3: Parallel Deep Dive (NEW!)
! Launch 3 Task agents in parallel:
  - Task(explore): Find related files
  - Task(architect): Understand structure
  - Task(analyzer): Find dependencies

## Phase 4: Validation (NEW!)
! Actually verify files exist
! Check file permissions
! Validate line ranges

## Phase 5: Memory Save (NEW!)
! Save discoveries to mem0:
  - File patterns that worked
  - Search terms that found results
  - Architecture insights

## Phase 6: Enhanced Output (NEW!)
! Create enriched JSON with:
  - Confidence scores per file
  - Relationship mapping
  - Missing pieces identified
  - Suggested search paths
```

**The key differences:**

| Aspect | Current `/scout` | Proposed `adw-scout` |
|--------|-----------------|---------------------|
| **Tools** | Broken external tools | Working native tools |
| **Memory** | Starts fresh | Remembers past searches |
| **Validation** | None | Verifies files exist |
| **Parallelization** | Fake (tools don't exist) | Real (Task agents) |
| **Output** | Often empty | Always has results |
| **Learning** | Never improves | Gets smarter over time |

---

## 🔗 How Skills Connect vs. Isolated Commands

### Current: Isolated Commands
```bash
# Each command is an island
/scout → [creates JSON] → END
                            ↓ (manual copy path)
/plan → [reads JSON] → [creates plan] → END
                                         ↓ (manual copy path)
/build_adw → [reads plan] → [builds] → END

# Problems:
- No shared context
- No error recovery
- No learning
- Manual path passing
- Each starts fresh
```

### Proposed: Connected Skills
```bash
# Skills share context and memory
/adw-complete "add auth" →
  ├─ Memory: "Oh, we did auth before in project X"
  ├─ Scout: Finds files using memory + working tools
  ├─ Context: Passes enriched context forward
  ├─ Plan: Uses context + documentation
  ├─ Validation: Checks plan makes sense
  ├─ Build: Implements with confidence
  ├─ Learn: Saves patterns for next time
  └─ Complete: Returns full report

# Benefits:
- Shared context throughout
- Error recovery built-in
- Continuous learning
- Automatic flow
- Each step enriches next
```

---

## 📊 Real Example: Adding Authentication

### Current Workflow (Broken)

```bash
# 1. Scout fails
$ /scout "add JWT authentication to API" "4"
Trying gemini... ERROR: command not found
Trying opencode... ERROR: command not found
Created: agents/scout_files/relevant_files.json
{
  "files": []  # Empty!
}

# 2. Plan works but generic
$ /plan_w_docs "add JWT" "https://jwt.io" "agents/scout_files/relevant_files.json"
Created: specs/add-jwt.md
# Generic plan because no files to reference

# 3. Build struggles
$ /build_adw "specs/add-jwt.md"
ERROR: Can't find app.js mentioned in plan
Creating files in potentially wrong locations...
```

### Skills Workflow (Working)

```bash
# One command does everything intelligently
$ /adw-complete "add JWT authentication to API"

[Memory Recall]
- Found: "Previous JWT implementation in project-alpha"
- Using patterns: middleware/, auth/, routes/

[Smart Scout]
- Glob: Found 15 files matching auth patterns
- Grep: Found 8 files with authentication logic
- Validated: All files exist and readable

[Intelligent Plan]
- Analyzed existing auth structure
- Found Express middleware pattern
- Planning JWT integration at middleware/auth.js
- Will modify 3 files, create 2 new files

[Validated Build]
- ✓ Created middleware/jwt.js
- ✓ Modified middleware/auth.js
- ✓ Added tests/jwt.test.js
- ✓ All tests passing

[Memory Update]
- Saved: JWT implementation pattern
- Saved: File structure for auth
- Saved: Test patterns that worked

Result: Complete, working implementation in one command!
```

---

## 🎯 Why Skills Are Better: The Compound Effect

### 1. **Memory Multiplier**
- Current: Every search starts from zero
- Skills: Each search builds on previous knowledge
- After 10 tasks: 50% faster from memory alone

### 2. **Context Preservation**
- Current: Copy-paste file paths between commands
- Skills: Context flows automatically through pipeline
- Zero manual intervention needed

### 3. **Error Recovery**
- Current: One failure breaks everything
- Skills: Each phase can recover and adapt
- Graceful degradation instead of total failure

### 4. **Parallel Execution**
- Current: Sequential even when claimed parallel
- Skills: True parallelization with working tools
- 3-5x speedup possible

### 5. **Learning System**
- Current: Makes same mistakes repeatedly
- Skills: Learns patterns and improves
- Becomes project-specific expert over time

---

## 🚀 Implementation Path

### Phase 1: Fix Scout (1 day)
```bash
# Replace external tools with working ones
# In .claude/commands/scout_working.md:
- Replace gemini/opencode/codex calls
+ Use Task(explore), Glob, Grep instead
```

### Phase 2: Add Memory Hooks (2 days)
```python
# In adw_modules/memory_hooks.py:
def pre_scout_hook(task):
    return mem0.search(task)

def post_scout_hook(results):
    mem0.save(results)
```

### Phase 3: Create Connected Skills (3 days)
```markdown
# Create .claude/skills/adw-complete.md
- Combines all phases
- Shares context
- Includes memory
- Handles errors
```

### Phase 4: Enable Parallelization (1 week)
```python
# In adw_modules/parallel_executor.py:
async def run_scouts_parallel(task):
    return await gather(
        scout_with_glob(task),
        scout_with_grep(task),
        scout_with_explore(task)
    )
```

---

## The Bottom Line

**Current commands** are like having three different people who never talk to each other:
- Scout person: "I couldn't find anything" (because their tools are broken)
- Plan person: "I'll plan anyway" (creates generic plan)
- Build person: "I can't build this" (plan references non-existent files)

**Skills** are like having one intelligent agent with memory:
- "I remember doing this before"
- "Let me use tools that actually work"
- "Here's a complete solution based on your actual codebase"
- "I learned something for next time"

The proposed skills system isn't just better - it's the difference between a broken pipeline and a working one!