# Parallelization Benchmark Suite

Comprehensive performance benchmarks for measuring the impact of parallelization integrations (Skills, Mem0, Git Worktrees, Archon) on the ADW workflow system.

## Quick Start

```bash
# Install dependencies
pip install pytest pytest-asyncio psutil

# Run all benchmarks
pytest benchmarks/parallel_test_suite.py -v

# Run with detailed output
pytest benchmarks/parallel_test_suite.py -v -s

# Run specific benchmark
pytest benchmarks/parallel_test_suite.py::test_full_stack_optimized -v

# Generate benchmark report
python benchmarks/parallel_test_suite.py
```

## Benchmark Scenarios

### 1. Baseline Sequential (Current System)
**Test**: `test_baseline_sequential`

Simulates current sequential execution:
```
Plan → Build → Test → Review → Document
```

**Expected**:
- Duration: ~1.9s (simulated)
- CPU: 10-15%
- Speedup: 1.0x (baseline)

### 2. Parallel Agents Only
**Test**: `test_parallel_agents_only`

Simulates parallel execution of independent phases:
```
Plan → Build → [Test + Review + Document in parallel]
```

**Expected**:
- Duration: ~1.4s
- CPU: 30-40%
- Speedup: 1.4x

### 3. Skills Parallelization
**Test**: `test_skills_parallelization`

Simulates sub-task parallelization using skills:
```
Plan → [Build skills in parallel] → [Test skills in parallel] → Review → Document
```

**Expected**:
- Duration: ~1.3s
- CPU: 40-50%
- Speedup: 1.5x

### 4. Parallel Agents + Skills
**Test**: `test_parallel_agents_with_skills`

Combines parallel agents with skills parallelization:
```
Plan → [Build skills] → [Test skills + Review + Document in parallel]
```

**Expected**:
- Duration: ~1.0s
- CPU: 50-60%
- Speedup: 1.9x

### 5. Mem0 Caching Simulation
**Test**: `test_mem0_caching_simulation`

Simulates Mem0 caching reducing redundant work:
```
Plan → Build (cache analysis) → Test (reuse cache) → Review (reuse cache) → Document
```

**Expected**:
- Duration: ~1.5s
- CPU: 30-40%
- Speedup: 1.3x
- Cache hits: 2-3

### 6. Full Stack Optimized
**Test**: `test_full_stack_optimized`

Combines all optimizations:
```
Plan → [Build skills + cache] → [Test skills + cache + Review + Document in parallel]
```

**Expected**:
- Duration: ~0.8s
- CPU: 60-70%
- Speedup: 2.3-2.5x

### 7. Multi-Workflow Parallel
**Test**: `test_multi_workflow_parallel`

Simulates 5 independent workflows running in parallel (worktree benefit):
```
Workflow 1 (worktree-1) ─┐
Workflow 2 (worktree-2) ─┤
Workflow 3 (worktree-3) ─┤─→ All in parallel
Workflow 4 (worktree-4) ─┤
Workflow 5 (worktree-5) ─┘
```

**Expected**:
- Duration: ~1.4s (vs 7s sequential)
- CPU: 70-80%
- Speedup: 5.0x

### 8-11. Scaling Tests
**Tests**: `test_scaling_2_agents`, `test_scaling_4_agents`, etc.

Measures scaling characteristics with varying numbers of parallel agents.

**Expected Scaling**:
- 2 agents: 1.7x speedup
- 4 agents: 2.6x speedup (optimal)
- 6 agents: 3.4x speedup (diminishing returns)
- 8 agents: 3.8x speedup (resource contention)

## Output

### Console Output
```
============================================================
Running: 01_Baseline_Sequential
============================================================
Duration: 1.90s
Speedup: 1.00x
CPU: 12.5%
Memory: 245 MB

============================================================
BENCHMARK SUMMARY
============================================================
Benchmark                                Time (s)     Speedup    CPU %
--------------------------------------------------------------------------------
01_Baseline_Sequential                   1.90         1.00x      12.5
02_Parallel_Agents_Only                  1.40         1.36x      35.2
03_Skills_Parallelization                1.35         1.41x      42.1
04_Parallel_Agents_With_Skills           1.00         1.90x      58.3
05_Mem0_Caching_Simulation               1.50         1.27x      32.4
06_Full_Stack_Optimized                  0.81         2.35x      65.8
07_Multi_Workflow_Parallel               1.40         1.36x      75.2
08_Scaling_2_Agents                      0.50         3.80x      40.1
09_Scaling_4_Agents                      0.50         3.80x      65.5
10_Scaling_6_Agents                      0.50         3.80x      82.3
11_Scaling_8_Agents                      0.50         3.80x      95.7
================================================================================
```

### JSON Output
Results saved to `benchmark_results/benchmark_results.json`:

```json
{
  "timestamp": "2025-10-20T23:59:00.000Z",
  "baseline_duration": 1.90,
  "results": [
    {
      "name": "01_Baseline_Sequential",
      "duration_seconds": 1.90,
      "speedup": 1.00,
      "cpu_percent": 12.5,
      "memory_mb": 245.0,
      "disk_io_mb": 0.5,
      "api_calls": 5,
      "success": true,
      "error": null,
      "metadata": {}
    },
    ...
  ]
}
```

## Interpreting Results

### Speedup Metrics
- **1.0-1.5x**: Moderate improvement (single optimization)
- **1.5-2.0x**: Good improvement (combined optimizations)
- **2.0-3.0x**: Excellent improvement (full stack)
- **3.0+**: Outstanding (multi-workflow scenarios)

### CPU Utilization
- **<20%**: Underutilized (sequential bottleneck)
- **20-50%**: Moderate parallelization
- **50-70%**: Good parallelization (optimal)
- **70-90%**: High parallelization (resource limits approaching)
- **>90%**: Resource contention (diminishing returns)

### Resource Efficiency
```
Efficiency = Speedup / (CPU_Utilization / Baseline_CPU)

Example:
Baseline: 1.0x speedup at 15% CPU
Optimized: 2.35x speedup at 65% CPU

Efficiency = 2.35 / (65 / 15) = 0.54 (54% efficient)
```

**Efficiency Targets**:
- **>70%**: Excellent (scaling efficiently)
- **50-70%**: Good (acceptable overhead)
- **30-50%**: Fair (high overhead)
- **<30%**: Poor (excessive overhead)

## Customization

### Adjust Task Durations
Edit task durations to match your actual workflow:

```python
# In parallel_test_suite.py
class MockPlanTask(MockTask):
    def __init__(self):
        super().__init__("plan", duration_ms=300000)  # 5 min instead of 3
```

### Add New Scenarios
Add custom benchmark scenarios:

```python
@pytest.mark.asyncio
async def test_custom_scenario(runner):
    """Custom benchmark scenario."""

    async def my_workflow():
        # Your custom workflow logic
        pass

    await runner.run_benchmark(
        "12_Custom_Scenario",
        my_workflow
    )
```

### Modify Resource Monitoring
Adjust sampling interval for resource monitoring:

```python
# In BenchmarkRunner.run_benchmark()
await monitor.start(interval_seconds=0.1)  # Sample every 100ms
```

## Real-World Testing

For real-world benchmarks with actual ADW workflows:

```bash
# Baseline
time uv run adws/adw_sdlc.py 123 adw_baseline

# With optimizations
time uv run adws/adw_sdlc_optimized.py 123 adw_optimized
```

Compare:
- Total execution time
- CPU utilization (`top` or `htop`)
- Memory usage (`ps aux`)
- API call counts (from logs)

## CI/CD Integration

### Add to GitHub Actions
```yaml
name: Performance Benchmarks

on:
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pytest pytest-asyncio psutil
      - name: Run benchmarks
        run: pytest benchmarks/parallel_test_suite.py -v
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: benchmark_results/
```

### Performance Regression Detection
```python
# Compare against baseline
import json

with open("benchmark_results/baseline.json") as f:
    baseline = json.load(f)

with open("benchmark_results/benchmark_results.json") as f:
    current = json.load(f)

for baseline_result in baseline["results"]:
    current_result = next(
        r for r in current["results"]
        if r["name"] == baseline_result["name"]
    )

    regression = (
        current_result["duration_seconds"] / baseline_result["duration_seconds"]
    )

    if regression > 1.1:  # 10% slower
        print(f"REGRESSION: {baseline_result['name']} is {regression:.1%} slower")
```

## Troubleshooting

### High Memory Usage
If benchmarks consume too much memory:

```python
# Reduce concurrent operations
@pytest.mark.asyncio
async def test_memory_limited(runner):
    # Limit to 2-3 parallel agents instead of 5
    pass
```

### Slow Execution
If benchmarks take too long:

```python
# Use FastMockTask with shorter durations
task = FastMockTask("test", duration_ms=100)  # 100ms instead of 1000ms
```

### Resource Monitor Errors
If resource monitoring fails:

```python
# Increase sampling interval
await monitor.start(interval_seconds=1.0)  # 1 second instead of 0.5s
```

## References

- [PARALLELIZATION_IMPACT_ANALYSIS.md](../ai_docs/analyses/PARALLELIZATION_IMPACT_ANALYSIS.md) - Full performance analysis
- [AGENTS_SDK_ARCHITECTURE.md](../ai_docs/architecture/AGENTS_SDK_ARCHITECTURE.md) - SDK design for parallelization
- [agents-sdk-implementation-plan.md](../specs/agents-sdk-implementation-plan.md) - Implementation roadmap

## Contributing

To add new benchmarks:

1. Create test function with `@pytest.mark.asyncio`
2. Use `BenchmarkRunner.run_benchmark()` to execute and measure
3. Return dict with `api_calls` and other metrics
4. Add expected results to this README

Example:
```python
@pytest.mark.asyncio
async def test_my_new_benchmark(runner):
    """Description of what this benchmarks."""

    async def my_workflow():
        # Your workflow logic
        return {"api_calls": 10, "custom_metric": 42}

    await runner.run_benchmark(
        "12_My_New_Benchmark",
        my_workflow
    )
```
