# Agent Box Integration Decision Document

**Date**: 2025-11-22
**Decision**: Progressive Enhancement Strategy
**Priority**: State Management > Organization > Sandboxing

## Executive Summary

Adopt Agent Box patterns progressively without breaking current framework. Start with state management and run isolation, evolve toward full sandboxing over time.

## The Problems (Prioritized)

### 1. 🔴 No State Management (CRITICAL)
- Can't tell if agents are running
- Can't resume crashed sessions
- No run tracking or history
- No resource monitoring

### 2. 🟡 Organizational Chaos (HIGH)
- Duplicate directories (ai_docs/scout vs scout_outputs)
- Outputs scattered across 5+ locations
- No unified run artifacts
- Hard to clean up old runs

### 3. 🟡 Limited Sandboxing (HIGH)
- Git worktrees provide minimal isolation
- No resource limits
- No network restrictions
- Agents can read their own output (self-poisoning)

## Recommended Solution: 3-Phase Progressive Enhancement

### Phase 1: State Management Layer (Week 1)
**Goal**: Track and manage agent runs without breaking changes

```python
# Create agents/supervisor.py (150 lines)
class RunManager:
    def track_run(self, command, args):
        run_id = f"{timestamp}_{slugify(command)}_{short_hash()}"
        run_dir = f"agent_runs/{run_id}/"

        # Create meta.yaml
        meta = {
            "run_id": run_id,
            "command": command,
            "started_at": now(),
            "status": "ACTIVE"
        }

        # Track in state.json
        state = {
            "pid": os.getpid(),
            "session_id": None,  # Capture from Claude
            "last_heartbeat": now()
        }

        # Keep existing commands working
        if command == "scout":
            # Call existing scout, track outputs
            pass
```

**Changes Required**:
- Add `agent_runs/` directory
- Create lightweight Python wrapper
- No breaking changes to existing commands

### Phase 2: Unified Run Directories (Week 2)
**Goal**: Consolidate outputs without breaking canonical paths

```
agent_runs/
├── 2025-11-22_1430_scout_auth_abc/
│   ├── meta.yaml           # Request info
│   ├── state.json          # Mutable status
│   ├── spec.md            # Symlink to specs/
│   ├── report.md          # Symlink to ai_docs/reports/
│   └── artifacts/
│       ├── scout.json     # Actual scout output
│       └── raw/           # Stream logs
└── latest -> 2025-11-22_1430_scout_auth_abc/
```

**Strategy**: Use symlinks to maintain backward compatibility while organizing by run

### Phase 3: Sandboxing Enhancement (Month 2)
**Goal**: Add true isolation without disrupting workflow

```python
# Progressive sandboxing levels
class SandboxLevel(Enum):
    NONE = 0          # Current state
    WORKTREE = 1      # Git isolation (current)
    PROCESS = 2       # Agent Box model
    CONTAINER = 3     # Docker isolation
    CLOUD = 4         # E2B or similar

# Start with PROCESS level
def run_sandboxed(command, level=SandboxLevel.PROCESS):
    if level >= SandboxLevel.PROCESS:
        # Implement Agent Box airlock
        worktree = create_worktree(run_id)
        ignore_patterns = [".agents/", "agent_runs/"]
```

## Implementation Priority

### Immediate (This Session)
1. **Fix duplicate directories**:
   ```bash
   # Consolidate to canonical location
   mv ai_docs/scout/* scout_outputs/archive/
   rmdir ai_docs/scout
   # Update any hardcoded references
   ```

2. **Create state tracking structure**:
   ```bash
   mkdir -p agent_runs/.template
   # Create template meta.yaml and state.json
   ```

3. **Add run ID generation**:
   ```python
   # In adw_common.py
   def generate_run_id(task_type: str) -> str:
       timestamp = datetime.now().strftime("%m%d-%H%M")
       slug = slugify(task_type)[:20]
       hash = secrets.token_hex(2)
       return f"{timestamp}-{slug}-{hash}"
   ```

### Next Week
1. Implement RunManager class
2. Add watchdog for zombie processes
3. Create unified run directories
4. Add session resumability

### Month 2
1. Docker container integration
2. Resource limits (memory, CPU, timeout)
3. Network isolation options
4. Full Agent Box supervisor

## Migration Path

### From Current to Agent Box Structure

**Current** (Distributed):
```
specs/issue-001-adw-XXX.md
ai_docs/reports/auth-report.md
scout_outputs/relevant_files.json
```

**Transitional** (Symlinks):
```
agent_runs/1122-1430-auth-abc/
├── spec.md -> ../../specs/issue-001-adw-XXX.md
├── report.md -> ../../ai_docs/reports/auth-report.md
└── artifacts/scout.json
```

**Future** (Unified):
```
agent_runs/1122-1430-auth-abc/
├── meta.yaml
├── state.json
├── spec.md         # Direct file
├── report.md       # Direct file
└── artifacts/      # All outputs
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Low | High | Use symlinks, maintain compatibility |
| Complexity overhead | Medium | Medium | Start simple, enhance progressively |
| User confusion | Medium | Low | Clear documentation, gradual rollout |
| Performance impact | Low | Low | Minimal overhead, optional features |

## Success Metrics

### Phase 1 (State Management)
- ✓ Can track running agents
- ✓ Can detect crashed agents
- ✓ Can see run history

### Phase 2 (Organization)
- ✓ Single directory per run
- ✓ Easy cleanup of old runs
- ✓ No duplicate directories

### Phase 3 (Sandboxing)
- ✓ Process isolation implemented
- ✓ Resource limits enforced
- ✓ Self-poisoning prevented

## Decision

**Proceed with Phase 1 immediately**. The state management layer adds immediate value without disruption. Phase 2 and 3 can follow based on actual needs.

## Alternative Considered

**Full Agent Box Implementation**: Rejected due to:
- Major breaking changes
- Requires complete rewrite
- Loses Claude Code integration
- 2-3 day implementation

**Do Nothing**: Rejected due to:
- Growing organizational chaos
- No ability to track/resume agents
- Security debt accumulating

---

**Recommendation**: Start Phase 1 today. Low risk, high value, builds toward long-term sandboxing goal.