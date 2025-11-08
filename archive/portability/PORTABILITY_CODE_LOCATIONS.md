# Portability Issues - Code Location Reference

Quick reference to find and fix portability blockers.

## Blocker 1: Path Whitelist

### Location
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/validators.py`  
**Lines**: 29-38

### Current Code
```python
# Allowed path prefixes for file operations
ALLOWED_PATH_PREFIXES = [
    "specs/",
    "agents/",
    "ai_docs/",
    "docs/",
    "scripts/",
    "adws/",
    "app/",
]
```

### Problem
- Hardcoded list prevents custom directory structures
- Used by SafeFilePath class (line 140-144)
- No environment variable override

### Validation Location
**Lines**: 138-144
```python
# Verify path is within allowed prefixes (if not absolute)
if not Path(v).is_absolute():
    has_allowed_prefix = any(v.startswith(prefix) for prefix in ALLOWED_PATH_PREFIXES)
    if not has_allowed_prefix:
        raise ValueError(f"File path must start with one of: {', '.join(ALLOWED_PATH_PREFIXES)}")
```

### Fix Strategy
1. Create environment variable: `ADW_ALLOWED_PATH_PREFIXES`
2. Load at module initialization
3. Provide sensible defaults
4. Update validation error message

### Estimated Effort
- 45 minutes (including testing)

---

## Blocker 2: State Directory

### Location
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/state.py`  
**Lines**: 59-64

### Current Code
```python
def get_state_path(self) -> str:
    """Get path to state file."""
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return os.path.join(project_root, "agents", self.adw_id, self.STATE_FILENAME)
```

### Problem
- State MUST go to `agents/{adw_id}/adw_state.json`
- No way to customize
- Causes conflicts in monorepos
- Called by:
  - `save()` method (line 66)
  - `load()` class method (line 115)

### Related Code Locations
- State file saving: **lines 66-112** (save method)
- State file loading: **lines 115-145** (load method)

### Fix Strategy
1. Add `ADW_AGENTS_DIR` environment variable
2. Load in constructor or module init
3. Default to "agents" for backward compatibility
4. Update path calculation

### Estimated Effort
- 1 hour (affects state loading/saving)

---

## Blocker 3: Logging Directory

### Location
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/utils.py`  
**Lines**: 30-37

### Current Code
```python
# Create log directory: agents/{adw_id}/adw_plan_build/
# __file__ is in adws/adw_modules/, so we need to go up 3 levels to get to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_dir = os.path.join(project_root, "agents", adw_id, trigger_type)
os.makedirs(log_dir, exist_ok=True)

# Log file path: agents/{adw_id}/adw_plan_build/execution.log
log_file = os.path.join(log_dir, "execution.log")
```

### Problem
- Logs hardcoded to agents directory
- Called by every script's logger setup
- Appears in multiple functions:
  - `setup_logger()` (line 20-73)
  - `get_logger()` (line 76-85)

### Related Calls
- `adw_plan.py` line 95: `logger = setup_logger(adw_id, "adw_plan")`
- `adw_build.py` line 81: `temp_logger = setup_logger(adw_id, "adw_build")`
- `adw_test.py` uses similar pattern
- All workflow scripts use this

### Fix Strategy
1. Create ADWConfig class in new config.py
2. Load `ADW_LOG_DIR` from environment
3. Update setup_logger() to use config
4. Default to "agents"

### Estimated Effort
- 1.5 hours (touches many files)

---

## Blocker 4: Plan File Discovery

### Location (Evidence from grep)
**File**: `adws/adw_modules/workflow_ops.py`  
**Pattern**: `glob.glob(f"specs/*{issue_number}*.md")`

### Problem
- Hardcoded search path "specs/"
- Will fail if plans stored elsewhere
- Silent failure if specs directory doesn't exist

### Usage Context
- Called when looking up existing plans
- Used in build phase to find plan to implement

### Fix Strategy
1. Add `ADW_SPECS_DIR` environment variable
2. Use in glob pattern
3. Handle missing directory gracefully

### Estimated Effort
- 30 minutes (simple search/replace)

---

## Blocker 5: Build Report Output

### Location (Evidence from grep)
**File**: `adws/adw_review.py`  
**Pattern**: `default="ai_docs/reviews"`

### Problem
- Output directory hardcoded as argument default
- Can be overridden with CLI flag but not flexible

### Similar Occurrences
- `adws/adw_build.py`: `default="ai_docs/build_reports"`
- `adws/scout_simple.py`: `Path("ai_docs/scout")`

### Fix Strategy
1. Use environment variables in argparse defaults
2. Or load from ADWConfig class
3. Keep CLI override capability

### Estimated Effort
- 1 hour (multiple files, consistent pattern)

---

## Blocker 6: Installation Script Validation

### Location
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/scripts/install_to_new_repo.sh`  
**Lines**: 1-100+

### Current State
```bash
# Script creates directories and copies files
# But does NOT verify:
# - Target directory is writable
# - Python version is 3.9+
# - uv is installed
# - gh CLI is available (if needed)
# - Claude Code CLI is available
# - Copy operations succeeded
```

### Missing Validation Functions
```bash
# These should exist but don't:
check_python_version()      # Verify Python 3.9+
check_uv_installed()        # Verify uv command available
check_gh_cli_installed()    # Verify gh command available
check_directory_writable()  # Verify target is writable
check_copy_success()        # Verify all files copied
```

### What Gets Called
```bash
# Current execution flow:
mkdir -p "$TARGET_REPO/specs"          # No check if mkdir succeeded
cp -r "$SOURCE_DIR/adws" "$TARGET_REPO/"  # No check if copy succeeded
```

### Fix Strategy
1. Add validation functions
2. Call before main operations
3. Exit with clear error messages
4. Document in comments what's being checked

### Estimated Effort
- 1.5-2 hours (adding 10-15 validation checks)

---

## Blocker 7: Environment Variables (Undocumented)

### Location
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/.env.sample`

### Current Variables
```
ANTHROPIC_API_KEY=sk-ant-...          # Required
GITHUB_REPO_URL=...                   # Required
CLAUDE_CODE_PATH=/path/to/claude      # Optional (default: "claude")
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768   # Optional (default: 8192)
GITHUB_PAT=ghp_...                    # Optional
E2B_API_KEY=...                       # Optional
AGENT_CLOUD_SANDBOX_KEY=...          # Optional
AGENT_CLOUD_SANDBOX_URL=...          # Optional
R2_ACCESS_KEY_ID=...                 # Optional
R2_SECRET_ACCESS_KEY=...             # Optional
R2_ENDPOINT_URL=...                  # Optional
R2_BUCKET_NAME=...                   # Optional
R2_PUBLIC_URL=...                    # Optional
```

### Missing Documentation
- No explanation of each variable
- No indication of which are truly required
- No consequences of missing values
- No examples of valid values

### Related Code
- `adws/adw_plan.py` line 49-56: Checks for ANTHROPIC_API_KEY and CLAUDE_CODE_PATH
- `adws/adw_modules/utils.py` line 161-215: Lists all safe env vars

### Fix Strategy
1. Create ENVIRONMENT_VARIABLES.md
2. Document each variable:
   - Purpose
   - Required/Optional
   - Example value
   - How to obtain
   - Failure mode if missing
3. Add comments to .env.sample

### Estimated Effort
- 1-2 hours (documentation only)

---

## Code Locations Summary Table

| Issue | File | Lines | Problem | Fix Time |
|-------|------|-------|---------|----------|
| Path Whitelist | validators.py | 29-38, 140-144 | Hardcoded list | 45 min |
| State Directory | state.py | 59-64, 66-112, 115-145 | agents/ locked | 1 hour |
| Log Directory | utils.py | 30-37 | agents/ locked | 1.5 hours |
| Plan Search | workflow_ops.py | (not shown) | specs/ locked | 30 min |
| Report Output | review.py, build.py, scout_simple.py | (not shown) | ai_docs/ locked | 1 hour |
| Install Validation | install_to_new_repo.sh | 1-100+ | No checks | 2 hours |
| Environment Docs | .env.sample | All | Undocumented | 1 hour |

**TOTAL FIX TIME: 8-10 hours for full portability**

---

## Quick Navigation Guide

### If you need to fix path issues:
1. Start with: `adws/adw_modules/validators.py` line 29-38
2. Then: `adws/adw_modules/state.py` line 59-64
3. Then: `adws/adw_modules/utils.py` line 30-37

### If you need to add configuration:
1. Create: `adws/adw_modules/config.py` (new file)
2. Update: Any file that has hardcoded paths
3. Load: Configuration at module initialization

### If you need to improve installation:
1. Edit: `scripts/install_to_new_repo.sh`
2. Add: Validation functions
3. Update: Error messages to be helpful

### If you need to document:
1. Update: `.env.sample` with explanations
2. Create: `docs/ENVIRONMENT_VARIABLES.md`
3. Update: `README.md` with prerequisites

---

**Key Files to Understand First**:
1. `adws/adw_modules/validators.py` - Path validation logic
2. `adws/adw_modules/state.py` - State persistence
3. `adws/adw_modules/utils.py` - Logging and utilities
4. `scripts/install_to_new_repo.sh` - Installation process
5. `.env.sample` - Configuration template

