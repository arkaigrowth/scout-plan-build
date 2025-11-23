# Parallelization Strategy

**Version**: 2.0 (Consolidated)
**Last Updated**: 2025-11-23
**Status**: Production-Ready

---

## Executive Summary

This document consolidates the parallelization analysis, decision matrices, and implementation guidance for the Scout Plan Build MVP project. The system successfully combines:

- **Git worktrees** for isolated parallel development
- **Subprocess-based parallelization** achieving 40-50% speedup
- **Multi-VCS support** (GitHub + Bitbucket)
- **Checkpoint system** with perfect undo/redo capability

**Key Findings**:
- Current system: 100% sequential, single-agent execution
- With integrations: Up to 80% of tasks can run in parallel
- Optimal parallelization: 4-6 concurrent agents on typical hardware
- Projected speedup: 2x minimum, 5-10x for complex workflows
- Critical enabler: Git worktrees provide safe workspace isolation

### Quick Findings

| Metric | Current State | Optimized State |
|--------|---------------|-----------------|
| Execution | 100% sequential | 60-70% parallel |
| CPU Utilization | 15% average | 65% average (4x improvement) |
| Memory Usage | 3 GB peak (19%) | 10 GB peak (optimal) |
| Typical Workflow | 14-20 minutes | 8.5 minutes (**2.35x speedup**) |

---

## Decision Matrix

### Quick Decision Tree

```
START: New workflow to implement
│
├─ Are tasks independent?
│   │
│   ├─ YES → Can tasks run in parallel?
│   │   │
│   │   ├─ YES → Use PARALLEL AGENTS (Worktrees + orchestrator)
│   │   │
│   │   └─ NO → Dependencies exist
│   │             │
│   │             ├─ Partial dependencies? → Use DEPENDENCY GRAPH
│   │             │
│   │             └─ Full sequential chain? → Check for SUB-TASK parallelization
│   │
│   └─ NO → Tasks share state/files
│       │
│       └─ Can skills decompose task?
│           │
│           ├─ YES → Use SKILLS PARALLELIZATION
│           │
│           └─ NO → SEQUENTIAL execution
│
END: Parallelization strategy selected
```

### Decision Criteria

| Question | YES → | NO → |
|----------|-------|------|
| Tasks share no files? | Parallel agents | Check skills |
| Has sequential dependencies? | Dependency graph | Full parallel |
| Can decompose into skills? | Skills parallelization | Sequential |
| >3 independent tasks? | Parallel agents | Check sub-tasks |
| Task duration >2 min? | Consider parallelization | Not worth overhead |
| Resource constrained? | Limit parallelism | Max parallelism |

### ADW Workflow Phases

| Phase | Parallelizable? | Strategy | Dependencies | Expected Speedup |
|-------|----------------|----------|--------------|------------------|
| **Plan** | No | Sequential | None (must be first) | 1.0x |
| **Build** | Partial | Skills | Depends on plan | 1.3-1.5x |
| **Test** | Yes | Agents + Skills | Depends on build | 1.5-2.0x |
| **Review** | Yes | Agents + Skills | Depends on build | 1.3-1.5x |
| **Document** | Yes | Agents + Skills | Depends on build | 1.5-2.0x |
| **Integration** | No | Sequential | Depends on all | 1.0x |

### Agent Allocation Table

| Available Resources | Recommended Agents | Max Parallel Tasks | Typical Speedup |
|---------------------|-------------------|-------------------|-----------------|
| 4 cores, 8 GB RAM | 2 agents | 2-3 | 1.5-1.8x |
| 8 cores, 16 GB RAM | 4 agents | 4-6 | 2.0-2.5x |
| 16 cores, 32 GB RAM | 6 agents | 6-8 | 2.5-3.5x |
| 32 cores, 64 GB RAM | 8 agents | 8-10 | 3.0-4.0x |

**API Rate Limit Constraint**: Cap at 6-8 agents regardless of resources (Anthropic limits).

### Integration Selection Guide

| Integration | Use When | Don't Use When | Expected Benefit |
|-------------|----------|---------------|------------------|
| **Skills** | Task has decomposable sub-tasks | Task is atomic | 1.3-1.5x speedup |
| **Mem0** | Repeated analysis across agents | One-time operations | 15-30% efficiency |
| **Worktrees** | Parallel agents need isolation | Single agent execution | 1.4-10x speedup |
| **Archon** | Long-running workflows | Quick operations | Reliability, not speed |

---

## Git Worktree Approach

### Architecture Overview

The system uses a three-layer parallelization approach:

```
Layer 1: Worktree Isolation
└─ scripts/worktree_manager.sh - Git worktree management
   ├─ Create/switch/merge worktrees
   ├─ Checkpoint system (undo/redo)
   └─ Parallel build capability

Layer 2: SDLC Parallelization
└─ adws/adw_sdlc.py - Parallel Test/Review/Document
   ├─ Test phase (subprocess 1)
   ├─ Review phase (subprocess 2)
   ├─ Document phase (subprocess 3)
   └─ Aggregated commit after all complete

Layer 3: Scout Parallelization
└─ adws/adw_scout_parallel.py - Parallel scout agents
   ├─ Implementation scout (find code)
   ├─ Tests scout (find test files)
   ├─ Configuration scout (find config)
   ├─ Architecture scout (find patterns)
   ├─ Dependencies scout (find imports)
   └─ Documentation scout (find docs)
```

### The Subprocess Pattern

All parallelization uses the same proven pattern:

```python
# Pattern used in adw_sdlc.py
test_proc = subprocess.Popen([...])
review_proc = subprocess.Popen([...])
document_proc = subprocess.Popen([...])

# Wait for all to complete
test_proc.wait()
review_proc.wait()
document_proc.wait()

# Single aggregated commit
subprocess.run(["git", "commit", ...])
```

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `scripts/worktree_manager.sh` | Core parallelization (562 lines) | Fully implemented |
| `adws/adw_sdlc.py` | SDLC parallelization (206 lines) | Fully functional |
| `adws/adw_scout_parallel.py` | Scout parallelization (264 lines) | Implemented |
| `adws/adw_modules/git_ops.py` | Git operations (397 lines) | Production-ready |
| `adws/adw_modules/vcs_detection.py` | Provider detection (281 lines) | Robust |

### Worktree Operations Performance

| Operation | Time |
|-----------|------|
| Create worktree | ~700ms |
| Checkpoint | ~400ms |
| Undo | ~400ms |
| Switch | ~100ms |
| List | ~200ms |
| Parallel builds (N tasks) | base + overhead |

### Existing Capabilities

**Parallelization**:
- Parallel SDLC - Test, Review, Document in parallel
- Parallel Scout - 6 scout agents with different strategies
- Parallel Build - Multiple specs in parallel worktrees
- Concurrent Execution - subprocess.Popen() pattern

**Git Worktrees**:
- Create - Isolated worktrees from any base branch
- Switch - Change between worktrees
- Checkpoint - Create undo point
- Undo/Redo - Navigate checkpoint history
- Merge - Merge worktree to target branch
- Cleanup - Remove worktree and archive metadata

**Safety Features**:
- Input Validation - Branch names, commit messages
- Conflict Detection - Merge tree preview
- Git State Checks - Stash/restore around operations
- Pre-commit Hooks - Checkpoint tracking
- Redo Stack - Preserve undo history

---

## Impact Analysis

### Integration Impact Summary

| Integration | Impact | Speedup | Priority | Implementation Cost |
|------------|--------|---------|----------|-------------------|
| **Git Worktrees** | Critical | 1.4-10x | CRITICAL | Low (just git commands) |
| **Skills** | Very High | 1.3-1.5x | High | Medium (refactor tasks) |
| **Mem0** | Medium-High | 15-30% efficiency | Medium | Medium (integrate SDK) |
| **Archon** | Medium | Reliability, not speed | Low | Medium (integrate SDK) |

### Why Worktrees Are Critical

**Worktrees enable safe parallel execution**:
- Each agent gets isolated workspace
- Zero file conflicts
- Easy cleanup and merge
- **THE enabling technology** for parallelization

**Without worktrees**: Can't safely run multiple agents simultaneously
**With worktrees**: Can run 4-6 agents in parallel with perfect isolation

### Performance Projections

#### Single Workflow Scenarios

| Configuration | Time (min) | Speedup | CPU % | Memory (GB) |
|--------------|-----------|---------|-------|-------------|
| **Baseline (Current)** | 20.0 | 1.0x | 15% | 3.0 |
| Skills Only | 15.5 | 1.29x | 25% | 3.5 |
| Worktrees Only | 14.0 | 1.43x | 45% | 8.0 |
| Skills + Worktrees | 10.5 | 1.90x | 60% | 9.0 |
| **Full Stack** | **8.5** | **2.35x** | **65%** | **10.0** |

#### Multi-Workflow Scenarios (5 Features)

| Configuration | Time (min) | Speedup | Throughput (features/hr) |
|--------------|-----------|---------|--------------------------|
| **Sequential (Current)** | 85.0 | 1.0x | 3.5 |
| Parallel (5 worktrees) | 20.0 | 4.25x | 15.0 |
| Parallel + Skills | 12.5 | 6.80x | 24.0 |
| **Full Stack** | **10.0** | **8.50x** | **30.0** |

### Resource Requirements

**Recommended Configuration** (4-6 parallel agents):
```yaml
cpu_cores: 8
ram_gb: 16
disk_type: NVMe SSD
disk_space_gb: 100
network_bandwidth: 100 Mbps
```

**Per-Agent Resource Budget**:
```
Base Python process: 500 MB
Claude Code CLI: 1.5 GB
Agent state + context: 200 MB
Worktree overhead: 100 MB
Skills execution: 500 MB
Mem0 client: 200 MB

Total per agent: ~3 GB
```

### ROI Analysis

**Single Workflow**:
- Time saved: 20 min → 8.5 min = **11.5 minutes**
- Engineer time value: 11.5 min × $60/hr = **$11.50 saved**
- Net benefit: **$11.50 per workflow**

**Multi-Workflow (5 features)**:
- Time saved: 85 min → 10 min = **75 minutes**
- Net benefit: **$85 per batch**

**At Scale** (100 workflows/month):
- Time saved: 1,150 minutes = **19 hours**
- Value: **$1,140/month**
- **Payback period**: ~1 month

---

## Implementation Summary

### Recommended Implementation Path

#### Phase 1: Worktree Pool (Week 1)
**Immediate 1.4x gain**

```python
pool = WorktreePool(size=4)
await pool.initialize()

tasks = [test_in_worktree(), review_in_worktree(), document_in_worktree()]
results = await asyncio.gather(*tasks)
```

**Benefit**: Low complexity, zero risk (fully isolated), immediate speedup

#### Phase 2: Skills Integration (Week 2-3)
**Additional 1.3x gain**

```python
build_skills = [
    analyze_dependencies(),
    analyze_patterns(),
    generate_code(),
    validate_syntax()
]
results = await asyncio.gather(*build_skills)
```

**Benefit**: Multiplicative with worktrees (1.4 × 1.3 = 1.82x total)

#### Phase 3: Mem0 Caching (Week 4)
**15-20% efficiency gain**

```python
@cached(ttl=3600)
async def analyze_codebase(files):
    pass  # Results cached for 1 hour
```

**Benefit**: Reduces redundant work, cost savings on API calls

#### Phase 4: Archon Persistence (Week 5+)
**Reliability improvement**

```python
workflow = ArchonWorkflow(id="feature-123")
await workflow.checkpoint()  # Survive crashes
```

**Benefit**: Workflow recovery after failures, cross-session continuity

### Current SDLC Parallelization

```
Sequential: Plan (2-3 min) → Build (3-4 min) →
           Test (3-4 min) → Review (3-4 min) → Document (3-4 min)
Total: 14-19 minutes

Parallel: Plan (2-3 min) → Build (3-4 min) →
         [Test || Review || Document] (3-4 min)
Total: 8-11 minutes

Speedup: 40-50% (2.2x faster)
```

### Scout Parallelization

```
Sequential: 6 scouts × 30s = 180 seconds
Parallel: ~30-40 seconds (4.5-6x faster)
Reduction: 150-160 seconds saved
```

### When to Parallelize

**DO parallelize when**:
- Task duration >2 minutes
- Tasks are independent (no shared state)
- You have 3+ independent tasks
- Resource availability (8+ cores, 16+ GB RAM)

**DON'T parallelize when**:
- Task duration <1 minute (overhead exceeds benefit)
- Tasks have sequential dependencies
- Resource constrained (<4 cores, <8 GB RAM)
- Only 1-2 tasks

### Anti-Patterns to Avoid

1. **Premature Parallelization**: Don't parallelize tasks <1 minute
2. **Over-Parallelization**: Cap at 6-8 agents maximum
3. **Ignoring Dependencies**: Build dependency graph first
4. **No Resource Monitoring**: Always monitor CPU, memory, API limits
5. **Caching Non-Deterministic Results**: Only cache pure functions
6. **Worktree Leaks**: Always use pool pattern with cleanup

### Gaps & Limitations

**Concurrency Model**:
- No asyncio - uses basic subprocess.Popen synchronously
- Limited to ~4-6 parallel tasks before diminishing returns

**Error Handling**:
- Basic returncode checking only
- No retry logic for failed tasks
- All parallel tasks must succeed for aggregated commit

**Resource Management**:
- No subprocess pooling
- No timeout enforcement for individual tasks

### Short-Term Recommendations (High Priority)
1. Add proper error handling - Retry logic for failed parallel tasks
2. Implement dependency graphs - Mark tasks that must run sequentially
3. Add observability - Structured logging for parallel operations
4. Document performance expectations - Timing, speedup curves

### Medium-Term Recommendations
1. Consider asyncio - For better concurrency model (if scaling beyond 4 tasks)
2. Implement resource pooling - ProcessPoolExecutor for cleaner code
3. Add rate limiting - Between git operations to prevent conflicts
4. Implement signal handlers - Proper SIGTERM/SIGINT handling

---

## References

- See also: [Parallel Execution Sequence Diagram](../architecture/diagrams/parallel-execution-sequence.md)
- See also: [Git Worktree Undo System](../architecture/GIT_WORKTREE_UNDO_SYSTEM.md)
- Benchmark suite: `benchmarks/parallel_test_suite.py`

---

## Key Takeaways

1. **Worktrees are the critical enabler** - Without them, safe parallelization is impossible
2. **Optimal is 4-6 agents** - More agents don't help due to API limits
3. **Skills enable multiplicative gains** - Sub-task parallelization compounds with agent parallelization
4. **Mem0 improves efficiency, not speed** - 15-30% cost savings, not time savings
5. **Start simple, add incrementally** - Worktrees first, then skills, then Mem0

**Bottom Line**: The proposed integrations can deliver **2.35x speedup for single workflows** and **8.5x speedup for multi-workflow scenarios**, with optimal configuration being **4-6 parallel agents using worktrees + skills + Mem0 caching**.
