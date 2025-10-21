"""
Parallel Performance Test Suite

Comprehensive benchmarks for measuring parallelization impact of:
- Skills system
- Mem0 integration
- Git Worktrees
- Archon workflow tracking

Run with: pytest benchmarks/parallel_test_suite.py -v --benchmark
"""

import asyncio
import time
import psutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import pytest

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    name: str
    duration_seconds: float
    speedup: float  # vs baseline
    cpu_percent: float
    memory_mb: float
    disk_io_mb: float
    api_calls: int
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "duration_seconds": self.duration_seconds,
            "speedup": self.speedup,
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
            "disk_io_mb": self.disk_io_mb,
            "api_calls": self.api_calls,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class ResourceSnapshot:
    """Snapshot of system resources."""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    disk_read_mb: float
    disk_write_mb: float


class ResourceMonitor:
    """Monitor system resources during benchmark execution."""

    def __init__(self):
        self.samples: List[ResourceSnapshot] = []
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.start_disk_io = psutil.disk_io_counters()

    async def start(self, interval_seconds: float = 0.5):
        """Start monitoring resources."""
        self.running = True
        self.start_disk_io = psutil.disk_io_counters()
        self.task = asyncio.create_task(self._monitor_loop(interval_seconds))

    async def _monitor_loop(self, interval: float):
        """Monitor loop - runs until stop() is called."""
        while self.running:
            try:
                disk_io = psutil.disk_io_counters()
                sample = ResourceSnapshot(
                    timestamp=time.time(),
                    cpu_percent=psutil.cpu_percent(interval=0.1),
                    memory_mb=psutil.virtual_memory().used / (1024 * 1024),
                    disk_read_mb=disk_io.read_bytes / (1024 * 1024),
                    disk_write_mb=disk_io.write_bytes / (1024 * 1024)
                )
                self.samples.append(sample)
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Error in resource monitor: {e}")
                break

    async def stop(self) -> Dict[str, float]:
        """Stop monitoring and return summary stats."""
        self.running = False
        if self.task:
            try:
                await asyncio.wait_for(self.task, timeout=1.0)
            except asyncio.TimeoutError:
                self.task.cancel()

        if not self.samples:
            return {
                "avg_cpu_percent": 0.0,
                "peak_memory_mb": 0.0,
                "disk_io_mb": 0.0
            }

        avg_cpu = sum(s.cpu_percent for s in self.samples) / len(self.samples)
        peak_memory = max(s.memory_mb for s in self.samples)

        # Calculate total disk I/O
        end_disk_io = psutil.disk_io_counters()
        disk_read_mb = (end_disk_io.read_bytes - self.start_disk_io.read_bytes) / (1024 * 1024)
        disk_write_mb = (end_disk_io.write_bytes - self.start_disk_io.write_bytes) / (1024 * 1024)
        total_disk_io = disk_read_mb + disk_write_mb

        return {
            "avg_cpu_percent": avg_cpu,
            "peak_memory_mb": peak_memory,
            "disk_io_mb": total_disk_io
        }


# ============================================================================
# Mock Task Implementations (Simulate Real Workflows)
# ============================================================================

class MockTask:
    """Base class for mock workflow tasks."""

    def __init__(self, name: str, duration_ms: int):
        self.name = name
        self.duration_ms = duration_ms
        self.api_calls = 0

    async def execute(self) -> Any:
        """Execute task (simulated with sleep)."""
        # Simulate CPU work
        start = time.time()
        while (time.time() - start) * 1000 < self.duration_ms:
            # Simulate some CPU work
            _ = sum(range(1000))

        self.api_calls += 1
        return {"status": "success", "task": self.name}


class MockPlanTask(MockTask):
    """Simulate planning phase."""
    def __init__(self):
        super().__init__("plan", duration_ms=180000)  # 3 min


class MockBuildTask(MockTask):
    """Simulate build phase."""
    def __init__(self):
        super().__init__("build", duration_ms=420000)  # 7 min


class MockTestTask(MockTask):
    """Simulate test phase."""
    def __init__(self):
        super().__init__("test", duration_ms=240000)  # 4 min


class MockReviewTask(MockTask):
    """Simulate review phase."""
    def __init__(self):
        super().__init__("review", duration_ms=180000)  # 3 min


class MockDocumentTask(MockTask):
    """Simulate documentation phase."""
    def __init__(self):
        super().__init__("document", duration_ms=120000)  # 2 min


# For faster testing, create short versions
class FastMockTask(MockTask):
    """Fast mock task for quick testing."""
    def __init__(self, name: str, duration_ms: int = 1000):
        super().__init__(name, duration_ms)


# ============================================================================
# Benchmark Scenarios
# ============================================================================

class BenchmarkRunner:
    """Run and collect benchmark results."""

    def __init__(self, output_dir: Path = Path("benchmark_results")):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[BenchmarkResult] = []
        self.baseline_duration: Optional[float] = None

    async def run_benchmark(
        self,
        name: str,
        task_fn,
        is_baseline: bool = False
    ) -> BenchmarkResult:
        """Run a single benchmark scenario."""
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")

        monitor = ResourceMonitor()
        await monitor.start()

        start_time = time.time()
        success = True
        error = None
        api_calls = 0

        try:
            result = await task_fn()
            # Count API calls if task returns them
            if isinstance(result, dict) and "api_calls" in result:
                api_calls = result["api_calls"]
        except Exception as e:
            success = False
            error = str(e)
            print(f"ERROR: {error}")

        duration = time.time() - start_time
        resources = await monitor.stop()

        # Set baseline if this is the first run
        if is_baseline or self.baseline_duration is None:
            self.baseline_duration = duration
            speedup = 1.0
        else:
            speedup = self.baseline_duration / duration if duration > 0 else 0.0

        result = BenchmarkResult(
            name=name,
            duration_seconds=duration,
            speedup=speedup,
            cpu_percent=resources["avg_cpu_percent"],
            memory_mb=resources["peak_memory_mb"],
            disk_io_mb=resources["disk_io_mb"],
            api_calls=api_calls,
            success=success,
            error=error
        )

        self.results.append(result)

        print(f"Duration: {duration:.2f}s")
        print(f"Speedup: {speedup:.2f}x")
        print(f"CPU: {resources['avg_cpu_percent']:.1f}%")
        print(f"Memory: {resources['peak_memory_mb']:.0f} MB")

        return result

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON."""
        output_file = self.output_dir / filename
        data = {
            "timestamp": datetime.now().isoformat(),
            "baseline_duration": self.baseline_duration,
            "results": [r.to_dict() for r in self.results]
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def print_summary(self):
        """Print summary table of results."""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        print(f"{'Benchmark':<40} {'Time (s)':<12} {'Speedup':<10} {'CPU %':<10}")
        print("-"*80)

        for result in self.results:
            print(
                f"{result.name:<40} "
                f"{result.duration_seconds:<12.2f} "
                f"{result.speedup:<10.2f}x "
                f"{result.cpu_percent:<10.1f}"
            )

        print("="*80)


# ============================================================================
# Test Scenarios
# ============================================================================

@pytest.fixture
def runner():
    """Create benchmark runner."""
    return BenchmarkRunner()


@pytest.mark.asyncio
async def test_baseline_sequential(runner):
    """Baseline: Sequential execution (current system)."""

    async def sequential_workflow():
        """Execute workflow sequentially."""
        tasks = [
            FastMockTask("plan", 300),
            FastMockTask("build", 700),
            FastMockTask("test", 400),
            FastMockTask("review", 300),
            FastMockTask("document", 200)
        ]

        api_calls = 0
        for task in tasks:
            await task.execute()
            api_calls += task.api_calls

        return {"api_calls": api_calls}

    await runner.run_benchmark(
        "01_Baseline_Sequential",
        sequential_workflow,
        is_baseline=True
    )


@pytest.mark.asyncio
async def test_parallel_agents_only(runner):
    """Parallel agents (test + review + document in parallel)."""

    async def parallel_workflow():
        """Execute with parallel agents (no skills yet)."""
        # Plan and build must be sequential
        plan = FastMockTask("plan", 300)
        await plan.execute()

        build = FastMockTask("build", 700)
        await build.execute()

        # Test, review, document can run in parallel
        parallel_tasks = [
            FastMockTask("test", 400).execute(),
            FastMockTask("review", 300).execute(),
            FastMockTask("document", 200).execute()
        ]

        await asyncio.gather(*parallel_tasks)

        return {"api_calls": 5}

    await runner.run_benchmark(
        "02_Parallel_Agents_Only",
        parallel_workflow
    )


@pytest.mark.asyncio
async def test_skills_parallelization(runner):
    """Skills-based sub-task parallelization."""

    async def skills_workflow():
        """Execute with skills parallelization."""
        plan = FastMockTask("plan", 300)
        await plan.execute()

        # Build phase with parallel skills
        build_skills = [
            FastMockTask("analyze_deps", 150).execute(),
            FastMockTask("analyze_patterns", 150).execute(),
            FastMockTask("generate_code", 200).execute(),
            FastMockTask("validate", 100).execute()
        ]
        await asyncio.gather(*build_skills)

        # Test phase with parallel skills
        test_skills = [
            FastMockTask("unit_tests", 120).execute(),
            FastMockTask("integration_tests", 150).execute(),
            FastMockTask("e2e_tests", 130).execute()
        ]
        await asyncio.gather(*test_skills)

        # Review and document
        await FastMockTask("review", 300).execute()
        await FastMockTask("document", 200).execute()

        return {"api_calls": 9}

    await runner.run_benchmark(
        "03_Skills_Parallelization",
        skills_workflow
    )


@pytest.mark.asyncio
async def test_parallel_agents_with_skills(runner):
    """Combined: Parallel agents + skills parallelization."""

    async def combined_workflow():
        """Execute with both parallel agents and skills."""
        # Plan
        plan = FastMockTask("plan", 300)
        await plan.execute()

        # Build with skills
        build_skills = [
            FastMockTask("analyze_deps", 150).execute(),
            FastMockTask("analyze_patterns", 150).execute(),
            FastMockTask("generate_code", 200).execute(),
            FastMockTask("validate", 100).execute()
        ]
        await asyncio.gather(*build_skills)

        # Parallel: test + review + document (each with skills)
        parallel_phases = [
            # Test with skills
            asyncio.gather(*[
                FastMockTask("unit_tests", 120).execute(),
                FastMockTask("integration_tests", 150).execute()
            ]),
            # Review
            FastMockTask("review", 300).execute(),
            # Document
            FastMockTask("document", 200).execute()
        ]

        await asyncio.gather(*parallel_phases)

        return {"api_calls": 8}

    await runner.run_benchmark(
        "04_Parallel_Agents_With_Skills",
        combined_workflow
    )


@pytest.mark.asyncio
async def test_mem0_caching_simulation(runner):
    """Simulate Mem0 caching impact."""

    cache = {}

    async def cached_task(name: str, duration_ms: int, cache_key: str):
        """Execute task with cache check."""
        if cache_key in cache:
            # Cache hit - instant return
            return cache[cache_key]

        # Cache miss - execute task
        task = FastMockTask(name, duration_ms)
        result = await task.execute()
        cache[cache_key] = result
        return result

    async def workflow_with_caching():
        """Execute with Mem0 caching."""
        # Plan
        await FastMockTask("plan", 300).execute()

        # Build with caching
        await cached_task("analyze_deps", 150, "deps")
        await cached_task("analyze_patterns", 150, "patterns")
        await FastMockTask("generate_code", 200).execute()

        # Test - reuse cached analysis
        await cached_task("analyze_deps", 150, "deps")  # Cache hit!
        await FastMockTask("run_tests", 400).execute()

        # Review - reuse cached analysis
        await cached_task("analyze_patterns", 150, "patterns")  # Cache hit!
        await FastMockTask("review_code", 300).execute()

        # Document
        await FastMockTask("document", 200).execute()

        return {"api_calls": 6, "cache_hits": 2}

    await runner.run_benchmark(
        "05_Mem0_Caching_Simulation",
        workflow_with_caching
    )


@pytest.mark.asyncio
async def test_full_stack_optimized(runner):
    """Full stack: Parallel agents + Skills + Mem0 caching."""

    cache = {}

    async def cached_skill(name: str, duration_ms: int, cache_key: str):
        """Cached skill execution."""
        if cache_key in cache:
            return cache[cache_key]

        task = FastMockTask(name, duration_ms)
        result = await task.execute()
        cache[cache_key] = result
        return result

    async def full_stack_workflow():
        """Fully optimized workflow."""
        # Plan
        await FastMockTask("plan", 300).execute()

        # Build with parallel skills + caching
        build_skills = [
            cached_skill("analyze_deps", 150, "deps"),
            cached_skill("analyze_patterns", 150, "patterns"),
            FastMockTask("generate_code", 200).execute(),
            FastMockTask("validate", 100).execute()
        ]
        await asyncio.gather(*build_skills)

        # Parallel phases with skills + caching
        parallel_phases = [
            # Test with skills + cache reuse
            asyncio.gather(
                cached_skill("analyze_deps", 150, "deps"),  # Cache hit
                FastMockTask("unit_tests", 120).execute(),
                FastMockTask("integration_tests", 150).execute()
            ),
            # Review with cache reuse
            asyncio.gather(
                cached_skill("analyze_patterns", 150, "patterns"),  # Cache hit
                FastMockTask("review_code", 200).execute()
            ),
            # Document
            FastMockTask("document", 200).execute()
        ]

        await asyncio.gather(*parallel_phases)

        return {"api_calls": 7, "cache_hits": 2}

    await runner.run_benchmark(
        "06_Full_Stack_Optimized",
        full_stack_workflow
    )


@pytest.mark.asyncio
async def test_multi_workflow_parallel(runner):
    """Multiple workflows in parallel (demonstrates worktree benefit)."""

    async def single_workflow(workflow_id: int):
        """Single workflow execution."""
        tasks = [
            FastMockTask(f"plan_{workflow_id}", 300),
            FastMockTask(f"build_{workflow_id}", 700),
            FastMockTask(f"test_{workflow_id}", 400)
        ]

        for task in tasks:
            await task.execute()

        return {"workflow_id": workflow_id}

    async def parallel_workflows():
        """Execute 5 workflows in parallel."""
        workflows = [
            single_workflow(i)
            for i in range(5)
        ]

        results = await asyncio.gather(*workflows)
        return {"api_calls": 15, "workflows": len(results)}

    await runner.run_benchmark(
        "07_Multi_Workflow_Parallel",
        parallel_workflows
    )


# ============================================================================
# Scaling Benchmarks
# ============================================================================

@pytest.mark.asyncio
async def test_scaling_2_agents(runner):
    """Scaling test: 2 parallel agents."""
    await runner.run_benchmark(
        "08_Scaling_2_Agents",
        lambda: run_n_parallel_agents(2)
    )


@pytest.mark.asyncio
async def test_scaling_4_agents(runner):
    """Scaling test: 4 parallel agents."""
    await runner.run_benchmark(
        "09_Scaling_4_Agents",
        lambda: run_n_parallel_agents(4)
    )


@pytest.mark.asyncio
async def test_scaling_6_agents(runner):
    """Scaling test: 6 parallel agents."""
    await runner.run_benchmark(
        "10_Scaling_6_Agents",
        lambda: run_n_parallel_agents(6)
    )


@pytest.mark.asyncio
async def test_scaling_8_agents(runner):
    """Scaling test: 8 parallel agents."""
    await runner.run_benchmark(
        "11_Scaling_8_Agents",
        lambda: run_n_parallel_agents(8)
    )


async def run_n_parallel_agents(n: int):
    """Run N agents in parallel."""
    agents = [
        FastMockTask(f"agent_{i}", 500).execute()
        for i in range(n)
    ]

    await asyncio.gather(*agents)
    return {"api_calls": n, "agents": n}


# ============================================================================
# Test Teardown
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
async def save_results_on_exit(request, runner):
    """Save results when all tests complete."""
    def finalizer():
        runner.save_results()
        runner.print_summary()

    request.addfinalizer(finalizer)


# ============================================================================
# Main Entry Point (for direct execution)
# ============================================================================

if __name__ == "__main__":
    async def main():
        """Run all benchmarks."""
        runner = BenchmarkRunner()

        # Run benchmarks in sequence
        await test_baseline_sequential(runner)
        await test_parallel_agents_only(runner)
        await test_skills_parallelization(runner)
        await test_parallel_agents_with_skills(runner)
        await test_mem0_caching_simulation(runner)
        await test_full_stack_optimized(runner)
        await test_multi_workflow_parallel(runner)

        # Scaling tests
        await test_scaling_2_agents(runner)
        await test_scaling_4_agents(runner)
        await test_scaling_6_agents(runner)
        await test_scaling_8_agents(runner)

        # Save and summarize
        runner.save_results()
        runner.print_summary()

    asyncio.run(main())
