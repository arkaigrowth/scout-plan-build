# Spec: Git Worktree Parallel Agents

**ADW ID:** ADW-WORKTREE-001
**Issue:** feature/bitbucket-integration (extends existing branch)
**Created:** 2024-11-22
**Schema Version:** 1.1.0

---

## Overview

Implement IndyDevDan-style parallel agent workflow using git worktrees. Run N Claude agents simultaneously on the same feature, each in an isolated worktree, then compare results and merge the best implementation.

**Research Source:** [IndyDevDan Video Analysis](../ai_docs/research/videos/idd-video-git-worktrees-f8RnRuaxee8-analysis.md)

---

## Existing Infrastructure (From Scout)

| Component | File | Status |
|-----------|------|--------|
| Worktree management | `scripts/worktree_manager.sh` | ✅ 562 lines, full featured |
| Parallel subprocess | `adws/adw_sdlc.py` | ✅ Popen pattern proven |
| Parallel scouts | `adws/adw_scout_parallel.py` | ✅ 6-agent pattern |
| Git operations | `adws/adw_modules/git_ops.py` | ✅ 397 lines |
| VCS detection | `adws/adw_modules/vcs_detection.py` | ✅ GitHub + Bitbucket |

**Key Insight:** We don't need to build from scratch. We need to COMPOSE existing capabilities into the IndyDevDan workflow.

---

## Requirements

### R1: Parallel Worktree Initialization
Create N worktrees for parallel agent execution.

**Input:**
- Feature name (e.g., "ui-revamp")
- Number of parallel agents (default: 3)
- Base branch (default: current branch)

**Output:**
```
trees/
├── ui-revamp-1/   # Agent 1's workspace
├── ui-revamp-2/   # Agent 2's workspace
└── ui-revamp-3/   # Agent 3's workspace
```

### R2: Parallel Agent Execution
Run N Claude agents simultaneously, each implementing the same spec in their worktree.

**Pattern (from IndyDevDan):**
```
1. Read spec file
2. Spawn N subprocess agents
3. Each agent works in isolated worktree
4. Wait for all to complete
5. Report results
```

### R3: Comparison & Merge Workflow
Help user compare implementations and merge the best.

**Commands:**
- List all worktree results with status
- Show diff stats for each
- Merge selected worktree to main
- Clean up worktrees after merge

### R4: Integration with Existing VCS
Support both GitHub and Bitbucket via existing vcs_detection.py.

---

## Implementation Plan

### Phase 1: Slash Commands (Primary Deliverable)

#### 1.1 `/init-parallel-worktrees`
**File:** `.claude/commands/init-parallel-worktrees.md`

```markdown
# Initialize Parallel Worktrees

Create N parallel worktrees for concurrent agent development.

## Arguments
- FEATURE_NAME: $ARGUMENTS[0] (required)
- NUM_AGENTS: $ARGUMENTS[1] (default: 3)

## Execution

1. Validate feature name (alphanumeric, dash, underscore only)
2. Create trees/ directory if not exists
3. For each agent 1..N in parallel:
   - git worktree add -b {FEATURE_NAME}-{N} ./trees/{FEATURE_NAME}-{N}
   - Copy .env if exists
   - Run npm install OR pip install (detect project type)
4. Report created worktrees with paths
```

#### 1.2 `/run-parallel-agents`
**File:** `.claude/commands/run-parallel-agents.md`

```markdown
# Run Parallel Agents

Execute N agents in parallel, each implementing the spec in their worktree.

## Arguments
- SPEC_FILE: $ARGUMENTS[0] (required, path to spec)
- FEATURE_NAME: $ARGUMENTS[1] (required, matches worktree prefix)

## Execution

1. Read spec file content
2. Detect existing worktrees matching {FEATURE_NAME}-*
3. For each worktree in parallel (subprocess.Popen pattern):
   - cd to worktree
   - Launch claude with spec as prompt
   - Capture output to trees/{worktree}/agent_output.log
4. Wait for all agents to complete
5. Report: success/failure status for each agent
```

#### 1.3 `/compare-worktrees`
**File:** `.claude/commands/compare-worktrees.md`

```markdown
# Compare Parallel Worktree Results

Show comparison of all parallel agent implementations.

## Arguments
- FEATURE_NAME: $ARGUMENTS[0] (required)

## Output

| Worktree | Branch | Files Changed | Lines +/- | Status |
|----------|--------|---------------|-----------|--------|
| trees/ui-1 | ui-revamp-1 | 5 | +120/-30 | ✅ Complete |
| trees/ui-2 | ui-revamp-2 | 7 | +200/-50 | ✅ Complete |
| trees/ui-3 | ui-revamp-3 | 4 | +80/-20 | ❌ Failed |

## Commands to explore:
- cd trees/ui-revamp-1 && git diff main --stat
- cd trees/ui-revamp-2 && npm run dev (port 5174)
```

#### 1.4 `/merge-worktree`
**File:** `.claude/commands/merge-worktree.md`

```markdown
# Merge Selected Worktree

Merge the chosen parallel implementation back to main branch.

## Arguments
- WORKTREE_PATH: $ARGUMENTS[0] (e.g., trees/ui-revamp-2)

## Execution

1. cd to worktree
2. git add . && git commit -m "feat: {feature} - parallel agent implementation"
3. git push origin {branch}
4. cd back to main repo
5. git merge {branch}
6. Prompt: clean up all worktrees? (y/n)
```

### Phase 2: Python Module (Optional Enhancement)

#### 2.1 `adws/adw_parallel_worktrees.py`

```python
"""
Parallel Worktree Agent Orchestration

Implements IndyDevDan's parallel agent pattern using existing infrastructure.
"""

import subprocess
from pathlib import Path
from adw_modules.git_ops import create_branch, get_current_branch
from adw_modules.vcs_detection import detect_vcs_provider

def init_worktrees(feature_name: str, num_agents: int = 3) -> list[Path]:
    """Create N parallel worktrees."""
    trees_dir = Path("trees")
    trees_dir.mkdir(exist_ok=True)

    worktrees = []
    for i in range(1, num_agents + 1):
        branch = f"{feature_name}-{i}"
        path = trees_dir / f"{feature_name}-{i}"
        subprocess.run(["git", "worktree", "add", "-b", branch, str(path)])
        worktrees.append(path)

    return worktrees

def run_parallel_agents(spec_path: str, worktrees: list[Path]) -> dict:
    """Run claude in each worktree in parallel (Popen pattern)."""
    processes = []
    for wt in worktrees:
        proc = subprocess.Popen(
            ["claude", "-p", f"Implement this spec:\n{Path(spec_path).read_text()}"],
            cwd=wt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append((wt, proc))

    results = {}
    for wt, proc in processes:
        stdout, stderr = proc.communicate()
        results[str(wt)] = {
            "returncode": proc.returncode,
            "output": stdout.decode()
        }

    return results
```

---

## File Changes Summary

| File | Action | Lines Est. |
|------|--------|-----------|
| `.claude/commands/init-parallel-worktrees.md` | Create | ~40 |
| `.claude/commands/run-parallel-agents.md` | Create | ~50 |
| `.claude/commands/compare-worktrees.md` | Create | ~30 |
| `.claude/commands/merge-worktree.md` | Create | ~35 |
| `scripts/worktree_manager.sh` | Update (add parallel init) | ~30 |
| `adws/adw_parallel_worktrees.py` | Create (optional) | ~100 |

**Total:** ~285 lines (mostly slash commands)

---

## Success Criteria

1. ✅ Can run `/init-parallel-worktrees feature-name 3` and get 3 isolated worktrees
2. ✅ Can run `/run-parallel-agents specs/feature.md feature-name` and have 3 agents work in parallel
3. ✅ Can run `/compare-worktrees feature-name` and see diff stats for all implementations
4. ✅ Can run `/merge-worktree trees/feature-2` to merge the best implementation
5. ✅ Works with both GitHub and Bitbucket repos (via vcs_detection)

---

## Test Plan

1. **Unit Test:** Create worktrees, verify isolation
2. **Integration Test:** Run parallel agents on simple spec
3. **E2E Test:** Full workflow - init → parallel run → compare → merge

---

## Notes

- **Leverage existing code:** worktree_manager.sh already handles most worktree operations
- **Proven pattern:** subprocess.Popen is already working in adw_sdlc.py
- **Keep it simple:** Slash commands first, Python module as enhancement
- **VCS agnostic:** Use vcs_detection.py for GitHub/Bitbucket compatibility
