# Parallelization Decision Matrix

**Version**: 1.0
**Date**: 2025-10-20
**Purpose**: Guide when and how to parallelize ADW workflows

## Executive Summary

This matrix provides decision rules for determining:
1. **When** to parallelize vs. execute sequentially
2. **Which** parallelization strategy to use
3. **How many** parallel agents to allocate
4. **What** resource allocation is needed

Use this as a practical guide when implementing or optimizing workflows.

---

## Table of Contents

1. [Quick Decision Tree](#1-quick-decision-tree)
2. [Task-Level Parallelization Matrix](#2-task-level-parallelization-matrix)
3. [Agent Allocation Guidelines](#3-agent-allocation-guidelines)
4. [Resource Allocation Strategies](#4-resource-allocation-strategies)
5. [Integration Selection Guide](#5-integration-selection-guide)
6. [Anti-Patterns to Avoid](#6-anti-patterns-to-avoid)

---

## 1. Quick Decision Tree

```
START: New workflow to implement

│
├─ Are tasks independent?
│   │
│   ├─ YES → Can tasks run in parallel?
│   │   │
│   │   ├─ YES → Use PARALLEL AGENTS
│   │   │         (Worktrees + orchestrator)
│   │   │
│   │   └─ NO → Dependencies exist
│   │             │
│   │             ├─ Partial dependencies?
│   │             │   └─ Use DEPENDENCY GRAPH
│   │             │       (Execute ready tasks in parallel)
│   │             │
│   │             └─ Full sequential chain?
│   │                 └─ Check for SUB-TASK parallelization
│   │
│   └─ NO → Tasks share state/files
│       │
│       └─ Can skills decompose task?
│           │
│           ├─ YES → Use SKILLS PARALLELIZATION
│           │         (Parallel sub-tasks)
│           │
│           └─ NO → SEQUENTIAL execution
│                   (No parallelization possible)
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

---

## 2. Task-Level Parallelization Matrix

### ADW Workflow Phases

| Phase | Parallelizable? | Strategy | Dependencies | Expected Speedup |
|-------|----------------|----------|--------------|------------------|
| **Plan** | ❌ No | Sequential | None (must be first) | 1.0x |
| **Build** | ⚠️ Partial | Skills | Depends on plan | 1.3-1.5x |
| **Test** | ✅ Yes | Agents + Skills | Depends on build | 1.5-2.0x |
| **Review** | ✅ Yes | Agents + Skills | Depends on build | 1.3-1.5x |
| **Document** | ✅ Yes | Agents + Skills | Depends on build | 1.5-2.0x |
| **Integration** | ❌ No | Sequential | Depends on all | 1.0x |

### Detailed Phase Analysis

#### Plan Phase
```yaml
parallelizable: false
reason: "Must complete before other phases can start"
strategy: Sequential
optimization: "Use fastest model (sonnet), minimal analysis"
typical_duration: 2-3 minutes
```

**Sequential Only**:
- Defines requirements for all other phases
- Must complete before build can start
- No parallelization possible

**Optimization**:
- Cache previous plans for similar issues
- Use Mem0 to recall past patterns
- Minimize unnecessary analysis

#### Build Phase
```yaml
parallelizable: partial
reason: "Can parallelize sub-tasks, but overall sequential"
strategy: Skills parallelization
optimization: "Decompose into parallel skills"
typical_duration: 5-7 minutes (sequential) → 3-4 minutes (parallel)
```

**Skills Parallelization**:
```python
# Parallel build skills
build_skills = [
    analyze_dependencies(),      # 1 min
    analyze_patterns(),          # 1 min
    analyze_security(),          # 30s
    analyze_performance()        # 30s
]

# Run in parallel
results = await asyncio.gather(*build_skills)
# Total: max(1, 1, 0.5, 0.5) = 1 min vs 3 min sequential

# Sequential code generation (uses results)
code = await generate_code(results)  # 2 min

# Parallel validation
validation = [
    validate_syntax(code),       # 20s
    validate_types(code),        # 30s
    validate_tests(code),        # 30s
    validate_docs(code)          # 20s
]

await asyncio.gather(*validation)
# Total: max(0.33, 0.5, 0.5, 0.33) = 0.5 min vs 1.8 min sequential

# Total: 1 + 2 + 0.5 = 3.5 min vs 6.8 min sequential
# Speedup: 1.94x
```

#### Test Phase
```yaml
parallelizable: true
reason: "Tests can run independently in isolated worktrees"
strategy: Agents + Skills
optimization: "Parallel test suites + parallel test execution"
typical_duration: 3-4 minutes (sequential) → 1.5-2 minutes (parallel)
```

**Full Parallelization**:
```python
# Strategy 1: Parallel test suites (worktrees)
test_suites = [
    run_unit_tests(worktree_1),       # 2 min
    run_integration_tests(worktree_2), # 3 min
    run_e2e_tests(worktree_3)         # 4 min
]

await asyncio.gather(*test_suites)
# Total: max(2, 3, 4) = 4 min vs 9 min sequential
# Speedup: 2.25x

# Strategy 2: Skills within test suite
unit_tests = [
    test_module_a(),  # 30s
    test_module_b(),  # 30s
    test_module_c(),  # 30s
    test_module_d()   # 30s
]

await asyncio.gather(*unit_tests)
# Total: max(0.5, 0.5, 0.5, 0.5) = 0.5 min vs 2 min sequential
# Speedup: 4x

# Combined: 1.5-2 min total
```

#### Review Phase
```yaml
parallelizable: true
reason: "Review aspects can run independently"
strategy: Agents + Skills
optimization: "Parallel review aspects (security, style, performance)"
typical_duration: 2-3 minutes (sequential) → 1-1.5 minutes (parallel)
```

**Parallel Review Skills**:
```python
review_aspects = [
    review_security(code),      # 1.5 min
    review_style(code),         # 1 min
    review_performance(code),   # 1.5 min
    review_best_practices(code) # 1 min
]

results = await asyncio.gather(*review_aspects)
# Total: max(1.5, 1, 1.5, 1) = 1.5 min vs 5 min sequential
# Speedup: 3.33x

# Aggregate results
final_review = aggregate_review_results(results)  # 30s

# Total: 2 min vs 5.5 min sequential
# Speedup: 2.75x
```

#### Document Phase
```yaml
parallelizable: true
reason: "Different doc sections can be generated independently"
strategy: Agents + Skills
optimization: "Parallel doc generation for different sections"
typical_duration: 2-3 minutes (sequential) → 1-1.5 minutes (parallel)
```

**Parallel Documentation**:
```python
doc_sections = [
    generate_api_docs(code),      # 1 min
    generate_readme(code),        # 1.5 min
    generate_architecture_doc(code), # 1 min
    generate_examples(code)       # 1 min
]

docs = await asyncio.gather(*doc_sections)
# Total: max(1, 1.5, 1, 1) = 1.5 min vs 4.5 min sequential
# Speedup: 3x

# Combine docs
final_docs = combine_documentation(docs)  # 30s

# Total: 2 min vs 5 min sequential
# Speedup: 2.5x
```

### Multi-Workflow Parallelization

| Scenario | Sequential | Parallel | Speedup | Strategy |
|----------|-----------|----------|---------|----------|
| 1 workflow | 20 min | 8.5 min | 2.35x | Agents + Skills |
| 2 workflows | 40 min | 17 min | 2.35x | 2 worktrees |
| 5 workflows | 100 min | 10 min | 10x | 5 worktrees |
| 10 workflows | 200 min | 20 min | 10x | 5 worktrees (2 batches) |

**Key Insight**: Multi-workflow scenarios show **near-linear scaling** with worktrees.

---

## 3. Agent Allocation Guidelines

### Optimal Agent Count Formula

```python
def calculate_optimal_agents(
    available_cpu_cores: int,
    available_memory_gb: float,
    task_count: int,
    task_independence: float  # 0.0 = fully dependent, 1.0 = fully independent
) -> int:
    """Calculate optimal number of parallel agents."""

    # CPU-based limit
    cpu_limit = max(1, available_cpu_cores - 1)  # Reserve 1 core for OS

    # Memory-based limit (3 GB per agent)
    memory_limit = int(available_memory_gb / 3.0 * 0.8)  # 80% safety margin

    # Task-based limit
    task_limit = max(1, int(task_count * task_independence))

    # Optimal is minimum of all limits
    optimal = min(cpu_limit, memory_limit, task_limit, 6)  # Cap at 6 for API limits

    return max(1, optimal)
```

### Agent Allocation Table

| Available Resources | Recommended Agents | Max Parallel Tasks | Typical Speedup |
|---------------------|-------------------|-------------------|-----------------|
| 4 cores, 8 GB RAM | 2 agents | 2-3 | 1.5-1.8x |
| 8 cores, 16 GB RAM | 4 agents | 4-6 | 2.0-2.5x |
| 16 cores, 32 GB RAM | 6 agents | 6-8 | 2.5-3.5x |
| 32 cores, 64 GB RAM | 8 agents | 8-10 | 3.0-4.0x |

**API Rate Limit Constraint**: Cap at 6-8 agents regardless of resources (Anthropic limits).

### Dynamic Agent Allocation

```python
class AdaptiveAgentPool:
    """Dynamically adjust agent count based on resource availability."""

    def __init__(self):
        self.max_agents = self._calculate_max_agents()
        self.current_agents = 0

    def _calculate_max_agents(self) -> int:
        """Calculate max agents based on current resources."""
        import psutil

        cpu_cores = psutil.cpu_count()
        available_memory_gb = psutil.virtual_memory().available / (1024**3)

        return calculate_optimal_agents(
            cpu_cores,
            available_memory_gb,
            task_count=10,  # Assume 10 tasks
            task_independence=0.7  # Assume 70% independent
        )

    async def acquire_agent(self) -> Optional[AgentWorker]:
        """Acquire agent from pool (may wait if at capacity)."""
        if self.current_agents >= self.max_agents:
            # Wait for agent to become available
            await self._wait_for_availability()

        self.current_agents += 1
        return AgentWorker()

    async def release_agent(self, agent: AgentWorker):
        """Release agent back to pool."""
        self.current_agents -= 1

    async def scale_down_if_needed(self):
        """Reduce agent count if resource pressure detected."""
        memory = psutil.virtual_memory()

        if memory.percent > 85:  # >85% memory usage
            self.max_agents = max(1, self.max_agents - 1)
            print(f"Scaled down to {self.max_agents} agents due to memory pressure")
```

### Agent Allocation Decision Matrix

| Condition | Agent Count | Reasoning |
|-----------|------------|-----------|
| Task duration < 1 min | 1 | Overhead not worth it |
| Task duration 1-3 min | 2-3 | Moderate benefit |
| Task duration 3-10 min | 4-6 | High benefit |
| Task duration >10 min | 4-6 | Optimal (API limits) |
| CPU cores < 4 | 1-2 | CPU bottleneck |
| Memory < 8 GB | 1-2 | Memory bottleneck |
| Independent tasks < 3 | Sequential | Not enough parallelism |
| Independent tasks 3-5 | 3-4 | Good parallelization |
| Independent tasks >5 | 4-6 | Optimal parallelization |

---

## 4. Resource Allocation Strategies

### Memory Management

**Per-Agent Memory Budget**:
```python
class MemoryBudgetManager:
    """Manage memory allocation for agents."""

    MEMORY_PER_AGENT_MB = 3000  # 3 GB per agent

    def __init__(self, total_memory_gb: float):
        self.total_memory_mb = total_memory_gb * 1024
        self.safety_margin = 0.8  # Use only 80% of available
        self.available_mb = self.total_memory_mb * self.safety_margin

    def max_agents(self) -> int:
        """Calculate max agents based on memory."""
        return int(self.available_mb / self.MEMORY_PER_AGENT_MB)

    def can_allocate(self, agent_count: int) -> bool:
        """Check if we can allocate N agents."""
        required_mb = agent_count * self.MEMORY_PER_AGENT_MB
        current_used_mb = psutil.virtual_memory().used / (1024 * 1024)

        return (current_used_mb + required_mb) < self.available_mb

# Usage
manager = MemoryBudgetManager(total_memory_gb=16)
max_agents = manager.max_agents()  # 4 agents on 16 GB system
```

### CPU Allocation

**CPU Affinity Strategy**:
```python
import os

def set_agent_cpu_affinity(agent_id: int, total_agents: int):
    """Pin agent to specific CPU cores."""
    import psutil

    cpu_count = psutil.cpu_count()
    cores_per_agent = cpu_count // total_agents

    # Assign cores
    start_core = agent_id * cores_per_agent
    end_core = start_core + cores_per_agent
    cores = list(range(start_core, end_core))

    # Set affinity (Linux/Mac)
    try:
        p = psutil.Process(os.getpid())
        p.cpu_affinity(cores)
        print(f"Agent {agent_id} pinned to cores {cores}")
    except AttributeError:
        # Not supported on this OS
        pass
```

### Disk I/O Management

**Worktree Placement Strategy**:
```python
class WorktreeStorageManager:
    """Manage worktree placement on disk."""

    def __init__(self):
        self.fast_disks = self._detect_fast_disks()

    def _detect_fast_disks(self) -> List[Path]:
        """Detect NVMe/SSD drives."""
        # On Mac: /Volumes/*
        # On Linux: Check /proc/partitions for nvme devices
        fast_disks = []

        for disk in psutil.disk_partitions():
            if "nvme" in disk.device.lower() or disk.fstype == "apfs":
                fast_disks.append(Path(disk.mountpoint))

        return fast_disks or [Path("/tmp")]  # Fallback

    def allocate_worktree_path(self, worktree_id: int) -> Path:
        """Allocate worktree on fastest available disk."""
        # Round-robin across fast disks
        disk = self.fast_disks[worktree_id % len(self.fast_disks)]
        return disk / "worktrees" / f"agent-{worktree_id}"
```

### Network Bandwidth Management

**API Rate Limiting**:
```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    """Rate limit API calls across parallel agents."""

    def __init__(self, max_calls_per_minute: int = 50):
        self.max_calls = max_calls_per_minute
        self.calls = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make API call."""
        async with self.lock:
            now = datetime.now()

            # Remove calls older than 1 minute
            cutoff = now - timedelta(minutes=1)
            self.calls = [c for c in self.calls if c > cutoff]

            # Check if we're at limit
            if len(self.calls) >= self.max_calls:
                # Calculate wait time
                oldest_call = min(self.calls)
                wait_seconds = 60 - (now - oldest_call).total_seconds()

                if wait_seconds > 0:
                    print(f"Rate limit: waiting {wait_seconds:.1f}s")
                    await asyncio.sleep(wait_seconds)

            # Record this call
            self.calls.append(datetime.now())

# Global rate limiter
api_limiter = RateLimiter(max_calls_per_minute=50)

async def call_api(prompt: str):
    """Make API call with rate limiting."""
    await api_limiter.acquire()
    return await execute_claude_code(prompt)
```

---

## 5. Integration Selection Guide

### When to Use Each Integration

| Integration | Use When | Don't Use When | Expected Benefit |
|-------------|----------|---------------|------------------|
| **Skills** | Task has decomposable sub-tasks | Task is atomic | 1.3-1.5x speedup |
| **Mem0** | Repeated analysis across agents | One-time operations | 15-30% efficiency |
| **Worktrees** | Parallel agents need isolation | Single agent execution | 1.4-10x speedup |
| **Archon** | Long-running workflows | Quick operations | Reliability, not speed |

### Integration Combinations

**Recommended Combinations**:

1. **Worktrees + Skills**: Best for parallel execution with sub-task decomposition
   - Use case: Multiple features, each with complex build
   - Speedup: 3-5x

2. **Skills + Mem0**: Best for reducing redundant work
   - Use case: Repeated analysis patterns
   - Speedup: 1.5-2x (via efficiency gains)

3. **Worktrees + Mem0**: Best for parallel agents with shared knowledge
   - Use case: Multiple similar features
   - Speedup: 2-4x

4. **Full Stack** (All integrations): Best for complex multi-workflow scenarios
   - Use case: Large-scale development
   - Speedup: 5-10x

**Anti-Combinations** (Don't use together):

- Archon + Short tasks: Overhead exceeds benefit
- Mem0 + Unique operations: No cache hits possible
- Worktrees + Single agent: Unnecessary complexity

### Integration Decision Tree

```
Need parallelization?
│
├─ Multiple independent workflows?
│   └─ YES → Use WORKTREES (primary)
│       │
│       ├─ Sub-tasks parallelizable?
│       │   └─ YES → Add SKILLS
│       │
│       └─ Repeated analysis?
│           └─ YES → Add MEM0
│
└─ Single workflow with sub-tasks?
    └─ Use SKILLS (primary)
        │
        └─ Need persistence?
            └─ YES → Add ARCHON
```

---

## 6. Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Premature Parallelization

**Problem**: Parallelizing tasks that run in <1 minute

```python
# BAD: Overhead exceeds benefit
async def bad_example():
    # Each task takes 10s, overhead is 5s per agent
    tasks = [
        quick_task_1(),  # 10s
        quick_task_2()   # 10s
    ]

    # Parallel: 10s + 5s overhead = 15s
    # Sequential: 20s
    # Result: Slower with parallelization!
    await asyncio.gather(*tasks)

# GOOD: Sequential for quick tasks
async def good_example():
    await quick_task_1()
    await quick_task_2()
    # Total: 20s (faster than parallel)
```

**Rule**: Only parallelize tasks >2 minutes duration.

### ❌ Anti-Pattern 2: Over-Parallelization

**Problem**: Too many agents exhaust resources

```python
# BAD: 20 agents on 8-core machine
async def bad_example():
    agents = [create_agent(i) for i in range(20)]
    # Result: Context switching overhead, memory exhaustion

# GOOD: Limit to optimal count
async def good_example():
    optimal_agents = calculate_optimal_agents(
        cpu_cores=8,
        memory_gb=16,
        task_count=20,
        independence=1.0
    )
    # Returns: 4-6 agents (optimal)
```

**Rule**: Use adaptive agent pool, cap at 6-8 agents.

### ❌ Anti-Pattern 3: Ignoring Dependencies

**Problem**: Parallelizing dependent tasks causes failures

```python
# BAD: Test depends on build completing
async def bad_example():
    # Both run in parallel - test fails!
    await asyncio.gather(
        build_code(),
        run_tests()  # Needs build to complete first
    )

# GOOD: Respect dependencies
async def good_example():
    await build_code()  # Complete first
    await run_tests()   # Then test
```

**Rule**: Build dependency graph before parallelizing.

### ❌ Anti-Pattern 4: No Resource Monitoring

**Problem**: Silent resource exhaustion

```python
# BAD: No monitoring
async def bad_example():
    while True:
        agent = create_agent()
        # Keeps creating until OOM

# GOOD: Monitor and adapt
async def good_example():
    pool = AdaptiveAgentPool()

    while True:
        if pool.can_allocate():
            agent = await pool.acquire_agent()
        else:
            await pool.wait_for_availability()
```

**Rule**: Always monitor CPU, memory, and API rate limits.

### ❌ Anti-Pattern 5: Caching Non-Deterministic Results

**Problem**: Mem0 caches results that shouldn't be cached

```python
# BAD: Caching timestamp-dependent results
async def bad_example():
    # Different every time!
    result = await mem0.get_or_compute("current_time", get_current_time)

# GOOD: Cache only deterministic results
async def good_example():
    # Same input → same output
    result = await mem0.get_or_compute(
        f"analysis:{file_hash}",
        lambda: analyze_file(file_path)
    )
```

**Rule**: Only cache pure functions (deterministic outputs).

### ❌ Anti-Pattern 6: Worktree Leaks

**Problem**: Creating worktrees without cleanup

```python
# BAD: Worktrees accumulate
async def bad_example():
    for i in range(100):
        wt = create_worktree(f"agent-{i}")
        await work_in_worktree(wt)
        # Never cleaned up - 100 worktrees remain!

# GOOD: Pool pattern with cleanup
async def good_example():
    pool = WorktreePool(size=5)
    await pool.initialize()

    try:
        for i in range(100):
            wt = await pool.acquire()
            try:
                await work_in_worktree(wt)
            finally:
                await pool.release(wt)  # Reused
    finally:
        await pool.cleanup()  # All removed
```

**Rule**: Use pool pattern, always cleanup worktrees.

---

## Appendices

### A. Quick Reference Table

| Scenario | Strategy | Agents | Expected Speedup | Integrations |
|----------|----------|--------|------------------|--------------|
| Single workflow, no sub-tasks | Sequential | 1 | 1.0x | None |
| Single workflow, sub-tasks | Skills | 1 | 1.3-1.5x | Skills |
| Single workflow, parallel phases | Parallel agents | 3-4 | 1.4-1.9x | Worktrees |
| Single workflow, full optimization | Combined | 4-6 | 2.0-2.5x | All |
| Multi-workflow (2-5) | Parallel workflows | 2-5 | 2-5x | Worktrees |
| Multi-workflow (5-10) | Batched | 5 | 5-10x | Worktrees + Mem0 |
| Complex analysis | Skills + cache | 1 | 1.5-2.0x | Skills + Mem0 |
| Long-running (>1hr) | Checkpointed | 4-6 | 2-3x | All + Archon |

### B. Resource Estimation Calculator

```python
def estimate_resources(
    workflow_count: int,
    avg_workflow_duration_min: float,
    parallelization_strategy: str
) -> Dict[str, Any]:
    """Estimate resource requirements."""

    strategies = {
        "sequential": {"speedup": 1.0, "agents": 1, "memory_gb": 3},
        "skills": {"speedup": 1.3, "agents": 1, "memory_gb": 3.5},
        "parallel_agents": {"speedup": 1.9, "agents": 4, "memory_gb": 10},
        "full_stack": {"speedup": 2.35, "agents": 5, "memory_gb": 12}
    }

    config = strategies[parallelization_strategy]

    # Calculate totals
    total_duration_min = (
        workflow_count * avg_workflow_duration_min / config["speedup"]
    )

    cpu_cores_needed = config["agents"] + 1  # +1 for orchestrator
    memory_gb_needed = config["memory_gb"]
    disk_gb_needed = 5 + (config["agents"] * 2)  # Base + worktrees

    return {
        "total_duration_min": total_duration_min,
        "cpu_cores_needed": cpu_cores_needed,
        "memory_gb_needed": memory_gb_needed,
        "disk_gb_needed": disk_gb_needed,
        "estimated_cost_usd": total_duration_min * 0.1  # $0.10/min estimate
    }

# Example
resources = estimate_resources(
    workflow_count=5,
    avg_workflow_duration_min=20,
    parallelization_strategy="full_stack"
)

print(f"Duration: {resources['total_duration_min']:.0f} minutes")
print(f"CPU cores: {resources['cpu_cores_needed']}")
print(f"Memory: {resources['memory_gb_needed']} GB")
print(f"Disk: {resources['disk_gb_needed']} GB")
print(f"Cost: ${resources['estimated_cost_usd']:.2f}")
```

### C. Checklist for Parallelization Implementation

**Before Implementing**:
- [ ] Measure baseline performance (sequential)
- [ ] Identify independent tasks
- [ ] Build dependency graph
- [ ] Calculate optimal agent count
- [ ] Verify resource availability
- [ ] Plan error handling strategy

**During Implementation**:
- [ ] Implement resource monitoring
- [ ] Add rate limiting
- [ ] Create worktree pool
- [ ] Implement dependency scheduler
- [ ] Add progress tracking
- [ ] Test failure scenarios

**After Implementation**:
- [ ] Benchmark performance improvement
- [ ] Verify resource utilization
- [ ] Check for resource leaks
- [ ] Validate error handling
- [ ] Document parallelization strategy
- [ ] Create runbook for operations

---

**End of Matrix**

Use this matrix as a practical guide when making parallelization decisions. When in doubt, start with the simplest approach (sequential) and add parallelization incrementally based on measured performance bottlenecks.
