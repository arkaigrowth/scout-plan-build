# Plan: Phase 1 Agent Box State Management & Framework Portability

## Summary
Implement Agent Box Phase 1: Add run ID generation, state tracking, directory consolidation, and interactive framework initialization. Make the framework portable to any repo.

## Problem Statement
1. **No state management**: Can't track running agents, detect crashes, or resume sessions
2. **Duplicate directories**: `ai_docs/scout/` vs `scout_outputs/` causes confusion
3. **No portability**: Framework requires manual setup in new repos
4. **No interactivity**: Can't gather user preferences during setup

## Inputs
- **Scout Results**: `scout_outputs/phase1-state-management.json`
- **Reference Doc**: `ai_docs/research/implementations/agent-box-supervisor-chad.md`
- **Existing Infrastructure**:
  - `adws/adw_common.py` - Has `slugify()` function
  - `adws/adw_modules/constants.py` - Has canonical path definitions
  - `LEGACY_SCOUT_DIR` already marked deprecated

## Architecture/Approach

### Run ID Format (User-Friendly)
```
{MMDD}-{slug}-{hash}

Examples:
- 1122-auth-fix-a1b2
- 1122-scout-api-c3d4
- 1123-init-db-e5f6
```

**Rationale**:
- MMDD gives date context without year clutter
- Slug is human-readable
- 4-char hash prevents collisions
- Sorts chronologically by date

### Directory Structure
```
agent_runs/                    # NEW: Centralized run tracking
├── .template/
│   ├── meta.yaml             # Template for run metadata
│   └── state.json            # Template for run state
├── 1122-scout-auth-a1b2/     # Example run
│   ├── meta.yaml             # Immutable request info
│   ├── state.json            # Mutable status tracking
│   ├── output.md             # Primary output
│   └── artifacts/            # Supporting files
└── latest -> 1122-scout-auth-a1b2/  # Symlink to most recent

scout_outputs/                 # EXISTING: Keep for compatibility
├── relevant_files.json       # Canonical scout output
├── workflows/{adw_id}/       # Workflow state
└── archive/                  # NEW: Archived old outputs
```

### State Machine
```
ACTIVE → DONE     (normal completion)
ACTIVE → CRASHED  (process died)
ACTIVE → STALLED  (heartbeat timeout)
STALLED → ACTIVE  (resume)
CRASHED → ACTIVE  (resume)
```

## Implementation Steps

### Step 1: Add Run ID Generation (adws/adw_common.py)
**Files**: `adws/adw_common.py`
**Lines to add**: ~15

```python
import secrets
from datetime import datetime

def generate_run_id(task_type: str, task_name: str = "") -> str:
    """Generate unique run ID in format MMDD-slug-hash."""
    date_part = datetime.now().strftime("%m%d")
    slug_part = slugify(task_type)[:20]
    if task_name:
        slug_part = f"{slug_part}-{slugify(task_name)[:10]}"
    hash_part = secrets.token_hex(2)  # 4 chars
    return f"{date_part}-{slug_part}-{hash_part}"
```

### Step 2: Add Constants (adws/adw_modules/constants.py)
**Files**: `adws/adw_modules/constants.py`
**Lines to add**: ~20

```python
# Agent Runs (NEW - Phase 1)
AGENT_RUNS_DIR = Path("agent_runs")
"""Centralized directory for all agent run tracking."""

AGENT_RUNS_TEMPLATE_DIR = AGENT_RUNS_DIR / ".template"
"""Templates for run metadata and state."""

def get_run_dir(run_id: str) -> Path:
    """Get the directory for a specific run."""
    run_dir = AGENT_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def get_latest_run() -> Optional[Path]:
    """Get the most recent run directory."""
    latest = AGENT_RUNS_DIR / "latest"
    if latest.is_symlink():
        return latest.resolve()
    return None
```

### Step 3: Create RunManager (agents/supervisor.py)
**Files**: `agents/supervisor.py` (NEW)
**Lines**: ~100

```python
#!/usr/bin/env python3
"""
Agent Run Supervisor - State Management Layer

Tracks agent runs, monitors health, enables resumability.
Based on Agent Box v6.2 spec (Chad/Gemini).
"""
import json
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Literal
from enum import Enum

class RunStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DONE = "DONE"
    CRASHED = "CRASHED"
    STALLED = "STALLED"

@dataclass
class RunMeta:
    """Immutable run metadata (meta.yaml)"""
    run_id: str
    task_type: str  # scout, plan, build, review
    task_description: str
    started_at: str
    model: str = "claude-sonnet-4"

@dataclass
class RunState:
    """Mutable run state (state.json)"""
    status: RunStatus
    pid: Optional[int] = None
    session_id: Optional[str] = None
    last_heartbeat: Optional[str] = None
    error: Optional[str] = None

class RunManager:
    def __init__(self, runs_dir: Path = Path("agent_runs")):
        self.runs_dir = runs_dir
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def create_run(self, task_type: str, task_desc: str) -> str:
        """Create a new run and return its ID."""
        from adws.adw_common import generate_run_id

        run_id = generate_run_id(task_type, task_desc)
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Write meta.yaml
        meta = RunMeta(
            run_id=run_id,
            task_type=task_type,
            task_description=task_desc,
            started_at=datetime.now().isoformat()
        )
        (run_dir / "meta.yaml").write_text(
            yaml.dump(asdict(meta), default_flow_style=False)
        )

        # Write initial state.json
        state = RunState(status=RunStatus.ACTIVE, pid=os.getpid())
        (run_dir / "state.json").write_text(
            json.dumps(asdict(state), indent=2)
        )

        # Update latest symlink
        latest = self.runs_dir / "latest"
        if latest.is_symlink():
            latest.unlink()
        latest.symlink_to(run_id)

        return run_id

    def complete_run(self, run_id: str) -> None:
        """Mark run as completed."""
        self._update_status(run_id, RunStatus.DONE)

    def crash_run(self, run_id: str, error: str) -> None:
        """Mark run as crashed."""
        self._update_status(run_id, RunStatus.CRASHED, error=error)

    def heartbeat(self, run_id: str) -> None:
        """Update heartbeat timestamp."""
        run_dir = self.runs_dir / run_id
        state_file = run_dir / "state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            state["last_heartbeat"] = datetime.now().isoformat()
            state_file.write_text(json.dumps(state, indent=2))

    def _update_status(self, run_id: str, status: RunStatus, error: str = None):
        run_dir = self.runs_dir / run_id
        state_file = run_dir / "state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            state["status"] = status.value
            if error:
                state["error"] = error
            state_file.write_text(json.dumps(state, indent=2))
```

### Step 4: Create Init-Framework Command (.claude/commands/init-framework.md)
**Files**: `.claude/commands/init-framework.md` (NEW)
**Purpose**: Interactive framework setup using AskUserQuestion

```markdown
# Initialize Scout-Plan-Build Framework

Set up the framework in a new repository with interactive configuration.

## Workflow

1. **Gather Preferences** using AskUserQuestion tool:
   - Directory structure preference
   - Run ID format preference
   - Sandboxing level
   - Git workflow preference

2. **Create Directory Structure**:
   - agent_runs/ with templates
   - scout_outputs/ (if not exists)
   - specs/ (if not exists)
   - ai_docs/ subdirectories

3. **Copy Configuration Files**:
   - CLAUDE.md (framework instructions)
   - .gitignore additions
   - adws/ modules (if needed)

4. **Report Success**

## Questions to Ask

Use AskUserQuestion with these:

1. "What sandboxing level do you want?"
   - Git worktrees only
   - Process isolation (recommended)
   - Docker containers

2. "How should run IDs be formatted?"
   - MMDD-slug-hash (default)
   - timestamp-slug
   - Custom pattern

3. "Include parallel worktree support?"
   - Yes (recommended for complex features)
   - No (simpler setup)
```

### Step 5: Consolidate Duplicate Directories
**Files**: `ai_docs/scout/` → `scout_outputs/archive/`
**Actions**:
1. Move all files from `ai_docs/scout/` to `scout_outputs/archive/`
2. Remove empty `ai_docs/scout/` directory
3. Update any hardcoded references

```bash
mkdir -p scout_outputs/archive
mv ai_docs/scout/* scout_outputs/archive/
rmdir ai_docs/scout
```

### Step 6: Create Templates (agent_runs/.template/)
**Files**:
- `agent_runs/.template/meta.yaml`
- `agent_runs/.template/state.json`

**meta.yaml**:
```yaml
# Run Metadata Template
# Copy this for new runs, fill in values

run_id: "{MMDD}-{slug}-{hash}"
task_type: scout|plan|build|review
task_description: "Description of what this run does"
started_at: "ISO8601 timestamp"
model: "claude-sonnet-4"
config_hash: null  # Optional: for safety verification
```

**state.json**:
```json
{
  "status": "ACTIVE",
  "pid": null,
  "session_id": null,
  "last_heartbeat": null,
  "error": null
}
```

## Testing Strategy

### Unit Tests
- Test `generate_run_id()` returns valid format
- Test `RunManager.create_run()` creates correct files
- Test state transitions work correctly

### Integration Tests
- Create a run, verify files exist
- Update heartbeat, verify timestamp changes
- Complete run, verify status changes
- Test latest symlink updates correctly

### Validation Criteria
- [ ] `agent_runs/` directory created with templates
- [ ] `ai_docs/scout/` removed, contents in archive
- [ ] New runs create proper directory structure
- [ ] State tracking works across run lifecycle
- [ ] `/init-framework` command works interactively

## Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing workflows | Use symlinks for backward compat |
| YAML parsing issues | Use standard library PyYAML |
| Symlink issues on Windows | Fall back to regular file |
| Import cycles | Keep RunManager standalone |

## Success Criteria

1. **State Tracking Works**: Can create, track, and complete runs
2. **No Duplicates**: Single source of truth for each output type
3. **Portable**: `/init-framework` sets up any repo
4. **Interactive**: Uses AskUserQuestion for preferences
5. **Non-Breaking**: Existing commands continue working

## Estimated Effort

| Step | Time | Risk |
|------|------|------|
| Run ID generation | 10 min | Low |
| Constants update | 10 min | Low |
| RunManager class | 30 min | Medium |
| Init-framework command | 20 min | Low |
| Directory consolidation | 5 min | Low |
| Templates | 5 min | Low |
| Testing | 20 min | Low |
| **Total** | **~100 min** | **Low-Medium** |

---

**Next Step**: Run `/build_adw "specs/phase1-agent-box-state-management.md"` to implement