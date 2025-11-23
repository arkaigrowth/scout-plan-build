# Scout-Plan-Build Framework - Canonical Directory Structure

**Updated:** 2024-11-22
**Version:** v2024.11.22 (Added research/ folder)

---

## 🎯 Core Principle: One Location Per Output Type

Every output type has **ONE canonical location**. No ambiguity, no duplicates.

---

## 📂 Complete Directory Tree (With Real Examples)

```
scout_plan_build_mvp/                    ← Project root
│
├── adws/                                 ← Framework Python modules (DON'T MODIFY)
│   ├── adw_scout_parallel.py            ← Parallel scout implementation
│   ├── scout_simple.py                  ← Simple scout implementation
│   ├── adw_plan.py                      ← Plan phase orchestrator
│   ├── adw_build.py                     ← Build phase orchestrator
│   ├── adw_sdlc.py                      ← Full SDLC workflow
│   └── adw_modules/
│       ├── constants.py                 ← ✨ CANONICAL PATHS (single source of truth)
│       ├── validators.py                ← Path enforcement
│       ├── state.py                     ← Workflow state management
│       ├── git_ops.py                   ← Git operations
│       ├── workflow_ops.py              ← Workflow orchestration
│       ├── github.py                    ← GitHub integration
│       ├── bitbucket_ops.py             ← Bitbucket integration (NEW)
│       ├── vcs_detection.py             ← VCS provider detection (NEW)
│       └── ...
│
├── specs/                                ← ✅ Implementation plans (CANONICAL)
│   ├── issue-001-adw-AUTH-001-jwt-authentication.md
│   ├── issue-002-adw-FILTER-001-text-filters.md
│   └── issue-NNN-adw-XXX-YYY-feature-name.md
│
├── scout_outputs/                        ← ✅ Scout results (CANONICAL)
│   │
│   ├── README.md                         ← Structure documentation
│   ├── relevant_files.json               ← 📌 PRIMARY OUTPUT (plan phase reads this)
│   │                                     Example content:
│   │                                     {
│   │                                       "task": "authentication bug",
│   │                                       "files": ["src/auth.py", "tests/test_auth.py"],
│   │                                       "count": 2,
│   │                                       "method": "parallel_squadron"
│   │                                     }
│   │
│   ├── reports/                          ← ✅ Analysis & execution reports (NEW)
│   │   ├── architecture_report.json
│   │   ├── configuration_report.json
│   │   ├── implementation_report.json
│   │   └── tests_report.json
│   │
│   ├── temp/                             ← Temporary scout working files
│   │   └── (empty - reserved for future use)
│   │
│   └── workflows/                        ← ✅ Workflow state (replaces agents/)
│       ├── ADW-AUTH-001/
│       │   ├── adw_state.json            ← Workflow state
│       │   ├── execution.log             ← Execution logs
│       │   └── agent_prompts/            ← Agent prompt history
│       │
│       ├── ADW-FILTER-001/
│       │   ├── adw_state.json
│       │   └── execution.log
│       │
│       └── ADW-XXX-YYY/                  ← Each workflow gets its own directory
│
├── ai_docs/                              ← ✅ AI-generated documentation
│   │
│   ├── build_reports/                    ← ✅ Build phase outputs (CANONICAL)
│   │   ├── jwt-authentication-ADW-AUTH-001-build-report.md
│   │   ├── text-filters-ADW-FILTER-001-build-report.md
│   │   └── feature-name-ADW-XXX-YYY-build-report.md
│   │
│   ├── reviews/                          ← ✅ Code review reports (CANONICAL)
│   │   ├── jwt-authentication-ADW-AUTH-001-review.md
│   │   └── feature-name-ADW-XXX-YYY-review.md
│   │
│   ├── research/                         ← ✅ External learning resources (NEW)
│   │   ├── videos/                       ← Video transcript analyses
│   │   ├── articles/                     ← Article summaries
│   │   ├── implementations/              ← Reference codebase notes
│   │   └── papers/                       ← Academic papers
│   │
│   └── outputs/                          ← ✅ Timestamped outputs (FileOrganizer)
│       ├── 20241120-143052-ADW-AUTH-001-jwt-auth/
│       │   ├── metadata.json             ← Task context
│       │   ├── scout_results.json        ← Scout findings
│       │   └── build_report.md           ← Build report
│       │
│       ├── 20241120-155230-ADW-FILTER-001-text-filters/
│       │   └── ...
│       │
│       └── latest/                       ← Symlink to most recent output
│
├── docs/                                 ← Project documentation (your docs)
│   ├── WORKFLOW_ARCHITECTURE.md
│   ├── SPEC_SCHEMA.md
│   └── ...
│
├── scripts/                              ← Utility scripts
│   ├── validate_pipeline.sh
│   ├── worktree_manager.sh
│   └── install_to_new_repo.sh
│
├── logs/                                 ← ✅ Hook logs (session-based)
│   └── f67ada19-d93f-49c5-97fc-b71de9cb32e7/  ← Session ID
│       ├── chat.json                     ← Chat transcript
│       ├── pre_tool_use.json             ← Pre-tool hook events
│       ├── post_tool_use.json            ← Post-tool hook events
│       ├── user_prompt_submit.json       ← User prompts
│       └── stop.json                     ← Session end events
│
├── .claude/                              ← Claude Code configuration
│   ├── commands/                         ← Slash commands
│   │   ├── scout.md
│   │   ├── plan_w_docs.md
│   │   └── build_adw.md
│   │
│   ├── hooks/                            ← Event hooks (observability)
│   │   ├── pre_tool_use.py
│   │   ├── post_tool_use.py
│   │   ├── user_prompt_submit.py
│   │   └── utils/
│   │       └── constants.py              ← Hook logging constants
│   │
│   └── skills/                           ← Workflow skills
│       ├── adw-scout.md
│       └── adw-complete.md
│
├── .scout_framework.yaml                 ← Framework manifest
├── .adw_config.json                      ← Project configuration
├── .env                                  ← Environment variables
└── .gitignore
```

---

## 🚫 DEPRECATED Locations (Do NOT Use)

```
❌ ai_docs/scout/                         ← REMOVED in v2024.11.20
   └── relevant_files.json                (use scout_outputs/relevant_files.json instead)

❌ agents/                                ← REMOVED (renamed to scout_outputs/workflows/)
   └── ADW-XXX/
       └── adw_state.json                 (use scout_outputs/workflows/ADW-XXX/ instead)
```

**Migration Note:** If you have old files in these locations, they will still be readable for backward compatibility, but all NEW writes go to the canonical locations.

---

## 📋 Real-World Example: Full Workflow

### **Scenario:** Implement JWT authentication feature

#### **1. Scout Phase**

**Command:**
```bash
python adws/scout_simple.py "JWT authentication implementation"
```

**Output:**
```
scout_outputs/
└── relevant_files.json                   ← Scout results saved here
```

**Content:**
```json
{
  "task": "JWT authentication implementation",
  "files": [
    "./src/auth/jwt_handler.py",
    "./src/auth/middleware.py",
    "./tests/test_auth.py",
    "./config/auth_config.py"
  ],
  "count": 4,
  "method": "native_tools",
  "timestamp": "2024-11-20T14:30:52Z"
}
```

#### **2. Plan Phase**

**Command:**
```bash
/plan_w_docs "Implement JWT auth" "" "scout_outputs/relevant_files.json"
```

**Output:**
```
specs/
└── issue-001-adw-AUTH-001-jwt-authentication.md
```

**Content:** Full implementation specification with:
- Requirements from docs
- File-by-line implementation plan
- Test cases
- Success criteria

#### **3. Build Phase**

**Command:**
```bash
/build_adw "specs/issue-001-adw-AUTH-001-jwt-authentication.md"
```

**Outputs:**
```
scout_outputs/workflows/ADW-AUTH-001/      ← Workflow state
├── adw_state.json                         ← {adw_id, issue_number, branch_name, ...}
└── execution.log                          ← Timestamped execution logs

ai_docs/build_reports/                     ← Build report
└── jwt-authentication-ADW-AUTH-001-build-report.md
```

**Build Report Content:**
```markdown
# Build Report: JWT Authentication

**ADW ID:** ADW-AUTH-001
**Timestamp:** 2024-11-20T15:45:12Z

## Files Modified
- src/auth/jwt_handler.py (created)
- src/auth/middleware.py (modified)
- tests/test_auth.py (created)

## Tests Added
- test_jwt_token_generation()
- test_jwt_token_validation()
- test_expired_token_handling()

## Build Status: ✅ Success
```

#### **4. Review Phase**

**Command:**
```bash
python adws/adw_review.py --adw-id ADW-AUTH-001
```

**Output:**
```
ai_docs/reviews/
└── jwt-authentication-ADW-AUTH-001-review.md
```

#### **5. Optional: Timestamped Archive**

**Using FileOrganizer:**
```python
from adw_modules.file_organization import FileOrganizer

organizer = FileOrganizer()
task_dir = organizer.create_task_directory("jwt-auth", "ADW-AUTH-001")
# Creates: ai_docs/outputs/20241120-154512-ADW-AUTH-001-jwt-auth/
```

---

## 🔍 How to Find Files

### **Where did my scout results go?**
```bash
cat scout_outputs/relevant_files.json
```

### **Where is my implementation plan?**
```bash
ls specs/issue-*-adw-*.md
# Or specific:
cat specs/issue-001-adw-AUTH-001-jwt-authentication.md
```

### **Where is my build report?**
```bash
ls ai_docs/build_reports/*-ADW-AUTH-001-*.md
```

### **Where is my workflow state?**
```bash
cat scout_outputs/workflows/ADW-AUTH-001/adw_state.json
```

### **Where are my logs?**
```bash
# Framework execution logs
cat scout_outputs/workflows/ADW-AUTH-001/execution.log

# Hook event logs (session-based)
ls logs/  # Lists all sessions
cat logs/<session-id>/post_tool_use.json
```

---

## ✅ Enforcement

### **Validators Check These Paths:**

From `adws/adw_modules/validators.py`:

```python
ALLOWED_PATH_PREFIXES = [
    "specs/",                    # ✅ Plans go here
    "scout_outputs/",            # ✅ Scout results go here
    "scout_outputs/temp/",       # ✅ Temporary scout files
    "scout_outputs/workflows/",  # ✅ Workflow state goes here
    "ai_docs/build_reports/",    # ✅ Build reports go here
    "ai_docs/reviews/",          # ✅ Reviews go here
    "ai_docs/outputs/",          # ✅ Timestamped outputs go here
    "docs/",                     # ✅ Documentation
    "scripts/",                  # ✅ Utility scripts
    "adws/",                     # ✅ Framework modules
]

# ❌ These are intentionally EXCLUDED:
# - "ai_docs/scout/" (deprecated - use scout_outputs/)
# - "agents/" (deprecated - use scout_outputs/workflows/)
```

Any attempt to write to non-allowed paths will be **rejected** by the validators.

---

## 🎓 Best Practices

### **DO:**
- ✅ Import paths from `adw_modules.constants`
- ✅ Use helper functions like `get_scout_output_path()`
- ✅ Check validators before writing to filesystem
- ✅ Use session-based logging in hooks (`logs/{session_id}/`)

### **DON'T:**
- ❌ Hardcode paths like `Path("ai_docs/scout/relevant_files.json")`
- ❌ Write to deprecated locations (`ai_docs/scout/`, `agents/`)
- ❌ Duplicate writes to multiple locations
- ❌ Use string concatenation for paths

---

## 📊 Summary Table

| Output Type | Canonical Location | Used By | Example File |
|-------------|-------------------|---------|--------------|
| **Scout results** | `scout_outputs/relevant_files.json` | Plan phase | `{"task": "...", "files": [...]}` |
| **Implementation plans** | `specs/issue-NNN-adw-XXX-*.md` | Build phase | `specs/issue-001-adw-AUTH-001-jwt-auth.md` |
| **Build reports** | `ai_docs/build_reports/` | Review/user | `jwt-auth-ADW-AUTH-001-build-report.md` |
| **Code reviews** | `ai_docs/reviews/` | User | `jwt-auth-ADW-AUTH-001-review.md` |
| **Research** | `ai_docs/research/` | AI context | `videos/git-worktree-parallelization.md` |
| **Workflow state** | `scout_outputs/workflows/{adw_id}/` | All phases | `ADW-AUTH-001/adw_state.json` |
| **Execution logs** | `scout_outputs/workflows/{adw_id}/` | Debugging | `ADW-AUTH-001/execution.log` |
| **Hook logs** | `logs/{session_id}/` | Observability | `<session-id>/post_tool_use.json` |
| **Timestamped archives** | `ai_docs/outputs/{timestamp}-{adw_id}-{task}/` | FileOrganizer | `20241120-154512-ADW-AUTH-001-jwt-auth/` |

---

## 🔄 Migration from Old Structure

If you have files in deprecated locations:

```bash
# Migrate scout outputs
mv ai_docs/scout/relevant_files.json scout_outputs/relevant_files.json

# Migrate workflow state
mv agents/ADW-*/  scout_outputs/workflows/
```

**Note:** The framework will continue to READ from old locations for backward compatibility, but will WRITE to new locations only.

---

**Questions?** Check `adws/adw_modules/constants.py` for the definitive source of truth.

**Last Updated:** 2024-11-22 (Added research/ for external learning resources)
