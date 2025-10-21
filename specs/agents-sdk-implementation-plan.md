# Agents SDK Implementation Plan

**Project**: Scout Plan Build MVP - Agents SDK
**Version**: 1.0
**Date**: 2025-10-20
**Owner**: Engineering Team

## Overview

This document outlines the phased implementation plan for transforming the current subprocess-based agent invocation system into a sophisticated multi-agent orchestration platform with persistent memory, parallel coordination, and robust error recovery.

**Total Estimated Timeline**: 8 weeks
**Team Size**: 2-3 engineers
**Risk Level**: Medium (backward compatibility maintained)

---

## Table of Contents

1. [Phase 1: Basic Orchestrator with State Management](#phase-1-basic-orchestrator-with-state-management)
2. [Phase 2: Parallel Execution Support](#phase-2-parallel-execution-support)
3. [Phase 3: Memory and Context Preservation](#phase-3-memory-and-context-preservation)
4. [Phase 4: Advanced Features](#phase-4-advanced-features)
5. [Testing Strategy](#testing-strategy)
6. [Risk Mitigation](#risk-mitigation)
7. [Success Metrics](#success-metrics)

---

## Phase 1: Basic Orchestrator with State Management

**Duration**: 2 weeks
**Goal**: Foundation layer with backward compatibility
**Risk**: Low

### 1.1 Project Setup (Days 1-2)

#### Tasks
- [ ] Create `agents_sdk/` package structure
- [ ] Set up development environment with dependencies
- [ ] Configure testing framework (pytest, pytest-asyncio)
- [ ] Create CI/CD pipeline for SDK

#### Deliverables
```
agents_sdk/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── session.py      # AgentSession
│   ├── response.py     # Response models
│   └── config.py       # Configuration
├── state/
│   ├── __init__.py
│   ├── backend.py      # StateBackend interface
│   ├── json_backend.py # JSONFileBackend
│   └── sqlite_backend.py # SQLiteBackend
├── memory/
│   ├── __init__.py
│   ├── backend.py      # MemoryBackend interface
│   └── inmemory.py     # InMemoryBackend
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── tests/
    └── __init__.py
```

#### Dependencies
```python
# requirements.txt additions
asyncio>=3.4.3
aiosqlite>=0.17.0  # Async SQLite
pydantic>=2.0.0    # Already exists
pytest>=7.4.0      # Already exists
pytest-asyncio>=0.21.0
tenacity>=8.2.0    # Retry logic
```

#### Acceptance Criteria
- [ ] Package structure created and importable
- [ ] All dependencies installed
- [ ] Basic tests passing
- [ ] CI/CD pipeline running

### 1.2 Core Agent Session (Days 3-5)

#### Tasks
- [ ] Implement `AgentSession` class
- [ ] Implement `AgentContext` dataclass
- [ ] Implement `Message` and `AgentResponse` models
- [ ] Create async wrapper for `prompt_claude_code()`
- [ ] Add session lifecycle management

#### Code Structure

**agents_sdk/core/session.py**:
```python
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
from adws.adw_modules.agent import prompt_claude_code
from adws.adw_modules.data_types import AgentPromptRequest

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentContext:
    working_directory: str
    environment: Dict[str, str]
    token_budget: Optional[int] = None
    tokens_used: int = 0

class AgentSession:
    def __init__(
        self,
        session_id: str,
        agent_name: str,
        context: Optional[AgentContext] = None
    ):
        self.session_id = session_id
        self.agent_name = agent_name
        self.context = context or AgentContext(
            working_directory=os.getcwd(),
            environment={}
        )
        self.status = AgentStatus.IDLE

    async def execute(
        self,
        prompt: str,
        model: str = "sonnet"
    ) -> AgentResponse:
        """Execute prompt via Claude Code CLI."""
        self.status = AgentStatus.RUNNING

        # Wrap synchronous prompt_claude_code in executor
        request = AgentPromptRequest(
            prompt=prompt,
            adw_id=self.session_id,
            agent_name=self.agent_name,
            model=model,
            dangerously_skip_permissions=True,
            output_file=self._get_output_file()
        )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            prompt_claude_code,
            request
        )

        self.status = AgentStatus.COMPLETED if response.success else AgentStatus.FAILED

        return AgentResponse(
            success=response.success,
            output=response.output,
            session_id=response.session_id,
            tokens_used=0,  # TODO: Extract from response
            execution_time_ms=0  # TODO: Measure
        )

    def _get_output_file(self) -> str:
        return f"agents/{self.session_id}/{self.agent_name}/raw_output.jsonl"
```

#### Tests
```python
# agents_sdk/tests/test_session.py
import pytest
from agents_sdk.core.session import AgentSession, AgentStatus

@pytest.mark.asyncio
async def test_agent_session_creation():
    session = AgentSession(
        session_id="test_001",
        agent_name="test_agent"
    )
    assert session.status == AgentStatus.IDLE
    assert session.session_id == "test_001"

@pytest.mark.asyncio
async def test_agent_session_execute(mock_claude_code):
    session = AgentSession("test_001", "test_agent")
    response = await session.execute("test prompt")
    assert session.status in [AgentStatus.COMPLETED, AgentStatus.FAILED]
```

#### Acceptance Criteria
- [ ] AgentSession can execute prompts via Claude Code CLI
- [ ] Session status tracked correctly
- [ ] Context maintained across executions
- [ ] All unit tests passing (>80% coverage)

### 1.3 State Backend Implementation (Days 6-8)

#### Tasks
- [ ] Implement `StateBackend` abstract interface
- [ ] Implement `JSONFileBackend` (backward compatible)
- [ ] Implement `SQLiteBackend`
- [ ] Add checkpoint save/load functionality
- [ ] Write migration script from current state format

#### Code Structure

**agents_sdk/state/backend.py**:
```python
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List

class StateBackend(ABC):
    @abstractmethod
    async def save(self, key: str, value: Any):
        """Save state."""
        pass

    @abstractmethod
    async def load(self, key: str) -> Optional[Any]:
        """Load state."""
        pass

    @abstractmethod
    async def save_checkpoint(self, workflow_id: str, checkpoint_data: Dict):
        """Save workflow checkpoint."""
        pass

    @abstractmethod
    async def load_checkpoint(self, workflow_id: str) -> Dict:
        """Load latest checkpoint."""
        pass
```

**agents_sdk/state/json_backend.py**:
```python
from pathlib import Path
import json
from .backend import StateBackend

class JSONFileBackend(StateBackend):
    """File-based state backend (backward compatible with current system)."""

    def __init__(self, base_dir: str = "agents"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, key: str, value: Any):
        file_path = self.base_dir / f"{key}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(value, f, indent=2)

    async def load(self, key: str) -> Optional[Any]:
        file_path = self.base_dir / f"{key}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            return json.load(f)

    async def save_checkpoint(self, workflow_id: str, checkpoint_data: Dict):
        checkpoint_key = f"{workflow_id}/checkpoint"
        await self.save(checkpoint_key, checkpoint_data)

    async def load_checkpoint(self, workflow_id: str) -> Dict:
        checkpoint_key = f"{workflow_id}/checkpoint"
        data = await self.load(checkpoint_key)
        return data or {}
```

**agents_sdk/state/sqlite_backend.py**:
```python
import aiosqlite
import json
from .backend import StateBackend

class SQLiteBackend(StateBackend):
    """SQLite-based state backend for better querying."""

    def __init__(self, db_path: str = "agents/state.db"):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    workflow_id TEXT,
                    checkpoint_name TEXT,
                    checkpoint_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (workflow_id, checkpoint_name)
                )
            """)
            await db.commit()

    async def save(self, key: str, value: Any):
        await self._init_db()  # Ensure tables exist
        async with aiosqlite.connect(self.db_path) as db:
            value_json = json.dumps(value)
            await db.execute("""
                INSERT OR REPLACE INTO state (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value_json))
            await db.commit()

    async def load(self, key: str) -> Optional[Any]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT value FROM state WHERE key = ?",
                (key,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
        return None
```

#### Tests
```python
@pytest.mark.asyncio
async def test_json_backend_save_load():
    backend = JSONFileBackend("test_agents")
    await backend.save("test_key", {"data": "value"})
    loaded = await backend.load("test_key")
    assert loaded == {"data": "value"}

@pytest.mark.asyncio
async def test_sqlite_backend_save_load():
    backend = SQLiteBackend(":memory:")
    await backend.save("test_key", {"data": "value"})
    loaded = await backend.load("test_key")
    assert loaded == {"data": "value"}

@pytest.mark.asyncio
async def test_checkpoint_save_load():
    backend = JSONFileBackend("test_agents")
    checkpoint = {
        "completed_tasks": ["task1", "task2"],
        "checkpoint_name": "checkpoint_2"
    }
    await backend.save_checkpoint("workflow_001", checkpoint)
    loaded = await backend.load_checkpoint("workflow_001")
    assert loaded == checkpoint
```

#### Acceptance Criteria
- [ ] StateBackend interface defined
- [ ] JSONFileBackend backward compatible with current system
- [ ] SQLiteBackend implemented and tested
- [ ] Checkpoint functionality working
- [ ] All tests passing (>85% coverage)

### 1.4 Backward Compatibility Layer (Days 9-10)

#### Tasks
- [ ] Create wrapper for existing `prompt_claude_code()`
- [ ] Add feature flag: `USE_AGENTS_SDK`
- [ ] Test with existing workflows
- [ ] Document migration path

#### Code Structure

**agents_sdk/compat.py**:
```python
"""
Backward compatibility layer for gradual migration.
"""
import os
import asyncio
from adws.adw_modules.data_types import AgentPromptRequest, AgentPromptResponse
from agents_sdk.core.session import AgentSession
from agents_sdk.state.json_backend import JSONFileBackend

# Global session cache
_session_cache = {}

def get_or_create_session(agent_name: str, adw_id: str) -> AgentSession:
    """Get or create agent session."""
    key = f"{agent_name}:{adw_id}"
    if key not in _session_cache:
        _session_cache[key] = AgentSession(
            session_id=adw_id,
            agent_name=agent_name
        )
    return _session_cache[key]

def prompt_claude_code_v2(request: AgentPromptRequest) -> AgentPromptResponse:
    """
    Enhanced version with session management.
    Drop-in replacement for original prompt_claude_code.
    """
    # Check feature flag
    if not os.getenv("USE_AGENTS_SDK", "false").lower() == "true":
        # Fall back to original implementation
        from adws.adw_modules.agent import prompt_claude_code
        return prompt_claude_code(request)

    # Use SDK version
    session = get_or_create_session(
        agent_name=request.agent_name,
        adw_id=request.adw_id
    )

    response = asyncio.run(session.execute(
        prompt=request.prompt,
        model=request.model
    ))

    # Return in original format
    return AgentPromptResponse(
        output=response.output,
        success=response.success,
        session_id=response.session_id
    )
```

**Usage**:
```python
# In .env file
USE_AGENTS_SDK=true

# In code (no changes needed!)
from adws.adw_modules.agent import prompt_claude_code
# OR
from agents_sdk.compat import prompt_claude_code_v2 as prompt_claude_code

response = prompt_claude_code(request)  # Works with both versions
```

#### Tests
```python
@pytest.mark.asyncio
async def test_backward_compatibility():
    """Test that SDK wrapper returns same format as original."""
    request = AgentPromptRequest(
        prompt="test",
        adw_id="test_001",
        agent_name="test_agent",
        model="sonnet",
        dangerously_skip_permissions=True,
        output_file="test.jsonl"
    )

    # SDK version
    os.environ["USE_AGENTS_SDK"] = "true"
    sdk_response = prompt_claude_code_v2(request)

    # Original version
    os.environ["USE_AGENTS_SDK"] = "false"
    original_response = prompt_claude_code_v2(request)

    # Both should return AgentPromptResponse with same fields
    assert type(sdk_response) == type(original_response)
    assert hasattr(sdk_response, "output")
    assert hasattr(sdk_response, "success")
    assert hasattr(sdk_response, "session_id")
```

#### Acceptance Criteria
- [ ] Wrapper maintains exact same interface
- [ ] Feature flag controls which version is used
- [ ] All existing tests still pass
- [ ] Documentation updated with migration guide

---

## Phase 2: Parallel Execution Support

**Duration**: 2 weeks
**Goal**: Enable concurrent agent execution
**Risk**: Medium

### 2.1 Workflow Orchestrator (Days 1-4)

#### Tasks
- [ ] Implement `Task` dataclass
- [ ] Implement `WorkflowSpec` dataclass
- [ ] Implement `WorkflowOrchestrator` class
- [ ] Add dependency graph execution
- [ ] Implement parallel batch execution

#### Code Structure

**agents_sdk/orchestration/orchestrator.py**:
```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import asyncio
from agents_sdk.core.session import AgentSession
from agents_sdk.state.backend import StateBackend

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    task_id: str
    agent_name: str
    prompt: str
    model: str = "sonnet"
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 3

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    response: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: int = 0

@dataclass
class WorkflowSpec:
    workflow_id: str
    tasks: List[Task]
    max_parallel: int = 5
    on_failure: str = "stop"  # or "continue"

@dataclass
class WorkflowResult:
    workflow_id: str
    success: bool
    task_results: List[TaskResult]
    total_time_ms: int

class WorkflowOrchestrator:
    def __init__(self, state_backend: StateBackend):
        self.state_backend = state_backend
        self.sessions: Dict[str, AgentSession] = {}

    async def run_workflow(
        self,
        workflow_spec: WorkflowSpec
    ) -> WorkflowResult:
        """Execute workflow with dependency-based execution."""

        start_time = datetime.now()
        task_graph = workflow_spec.tasks.copy()
        completed_tasks = set()
        task_results = []

        while task_graph:
            # Find tasks ready to run (no pending dependencies)
            ready_tasks = [
                task for task in task_graph
                if all(dep in completed_tasks for dep in task.depends_on)
            ]

            if not ready_tasks:
                break  # Circular dependency or all failed

            # Execute ready tasks in parallel
            batch_results = await self._execute_parallel_batch(
                ready_tasks,
                workflow_spec.max_parallel
            )

            task_results.extend(batch_results)

            # Update completed tasks
            for result in batch_results:
                if result.status == TaskStatus.COMPLETED:
                    completed_tasks.add(result.task_id)
                    task_graph = [t for t in task_graph if t.task_id != result.task_id]
                elif result.status == TaskStatus.FAILED:
                    if workflow_spec.on_failure == "stop":
                        break
                    else:
                        completed_tasks.add(result.task_id)
                        task_graph = [t for t in task_graph if t.task_id != result.task_id]

        end_time = datetime.now()
        total_time = int((end_time - start_time).total_seconds() * 1000)

        return WorkflowResult(
            workflow_id=workflow_spec.workflow_id,
            success=all(r.status == TaskStatus.COMPLETED for r in task_results),
            task_results=task_results,
            total_time_ms=total_time
        )

    async def _execute_parallel_batch(
        self,
        tasks: List[Task],
        max_parallel: int
    ) -> List[TaskResult]:
        """Execute tasks in parallel batches."""
        results = []

        for i in range(0, len(tasks), max_parallel):
            batch = tasks[i:i + max_parallel]
            batch_results = await asyncio.gather(
                *[self._execute_task(task) for task in batch],
                return_exceptions=True
            )

            for task, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results.append(TaskResult(
                        task_id=task.task_id,
                        status=TaskStatus.FAILED,
                        error=str(result)
                    ))
                else:
                    results.append(result)

        return results

    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute single task with retry."""
        session = await self._get_or_create_session(task.agent_name)

        try:
            response = await session.execute_with_retry(
                prompt=task.prompt,
                max_retries=task.retry_count
            )

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED if response.success else TaskStatus.FAILED,
                response=response
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
```

#### Tests
```python
@pytest.mark.asyncio
async def test_parallel_execution():
    """Test that independent tasks run in parallel."""
    orchestrator = WorkflowOrchestrator(JSONFileBackend())

    workflow = WorkflowSpec(
        workflow_id="test_parallel",
        tasks=[
            Task(task_id="task1", agent_name="agent1", prompt="test"),
            Task(task_id="task2", agent_name="agent2", prompt="test"),
        ],
        max_parallel=2
    )

    start = time.time()
    result = await orchestrator.run_workflow(workflow)
    duration = time.time() - start

    # Should run in parallel (< 2x sequential time)
    assert duration < 1.5  # Assuming each task takes ~1s
    assert len(result.task_results) == 2

@pytest.mark.asyncio
async def test_dependency_execution():
    """Test that dependent tasks run in correct order."""
    orchestrator = WorkflowOrchestrator(JSONFileBackend())

    execution_order = []

    async def track_execution(task_id):
        execution_order.append(task_id)

    workflow = WorkflowSpec(
        workflow_id="test_deps",
        tasks=[
            Task(task_id="task1", agent_name="agent1", prompt="test"),
            Task(task_id="task2", agent_name="agent2", prompt="test", depends_on=["task1"]),
        ]
    )

    result = await orchestrator.run_workflow(workflow)

    # task1 should complete before task2 starts
    task1_idx = next(i for i, r in enumerate(result.task_results) if r.task_id == "task1")
    task2_idx = next(i for i, r in enumerate(result.task_results) if r.task_id == "task2")
    assert task1_idx < task2_idx
```

#### Acceptance Criteria
- [ ] Tasks execute in parallel up to `max_parallel` limit
- [ ] Dependency graph respected
- [ ] Failures handled according to `on_failure` setting
- [ ] All tests passing (>80% coverage)

### 2.2 Retry Logic with Backoff (Days 5-6)

#### Tasks
- [ ] Add `execute_with_retry()` to AgentSession
- [ ] Implement exponential backoff
- [ ] Add configurable retry strategies
- [ ] Test retry behavior

#### Code Structure

**agents_sdk/core/session.py** (additions):
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class AgentSession:
    # ... existing code ...

    async def execute_with_retry(
        self,
        prompt: str,
        model: str = "sonnet",
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> AgentResponse:
        """Execute with exponential backoff retry."""

        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=backoff_factor),
            retry=retry_if_exception_type(TransientError)
        )
        async def _execute_with_retry():
            return await self.execute(prompt, model)

        return await _execute_with_retry()
```

#### Tests
```python
@pytest.mark.asyncio
async def test_retry_on_failure():
    """Test that failures are retried."""
    attempt_count = 0

    async def failing_execute(prompt, model):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise TransientError("Temporary failure")
        return AgentResponse(success=True, ...)

    session = AgentSession("test", "agent")
    session.execute = failing_execute

    response = await session.execute_with_retry("test", max_retries=3)

    assert attempt_count == 3
    assert response.success
```

#### Acceptance Criteria
- [ ] Transient failures are retried automatically
- [ ] Exponential backoff implemented correctly
- [ ] Max retries respected
- [ ] Permanent failures fail fast

### 2.3 Integration with Existing Workflows (Days 7-10)

#### Tasks
- [ ] Create `adws_v2/adw_plan_build.py` using orchestrator
- [ ] Migrate `adw_plan_build_test.py` to use parallel execution
- [ ] Add benchmarks comparing old vs new execution times
- [ ] Document migration examples

#### Example Migration

**Before** (adws/adw_plan_build.py):
```python
# Sequential subprocess calls
subprocess.run(["uv", "run", "adw_plan.py", issue_number, adw_id])
subprocess.run(["uv", "run", "adw_build.py", issue_number, adw_id])
```

**After** (adws_v2/adw_plan_build.py):
```python
from agents_sdk.orchestration import WorkflowOrchestrator, WorkflowSpec, Task
from agents_sdk.state.sqlite_backend import SQLiteBackend

async def main():
    orchestrator = WorkflowOrchestrator(SQLiteBackend())

    workflow = WorkflowSpec(
        workflow_id=f"plan_build_{adw_id}",
        tasks=[
            Task(
                task_id="plan",
                agent_name="sdlc_planner",
                prompt=f"/feature {issue_number} {adw_id} {issue_json}",
                model="opus"
            ),
            Task(
                task_id="build",
                agent_name="sdlc_implementor",
                prompt=f"/implement {plan_file}",
                model="opus",
                depends_on=["plan"]
            )
        ],
        max_parallel=2,
        on_failure="stop"
    )

    result = await orchestrator.run_workflow(workflow)

    if not result.success:
        print(f"Workflow failed: {result.task_results}")
        sys.exit(1)

    print(f"Workflow completed in {result.total_time_ms}ms")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Benchmarks
```python
# Test performance improvement
def benchmark_sequential_vs_parallel():
    # Sequential (current)
    start = time.time()
    run_sequential_workflow()
    sequential_time = time.time() - start

    # Parallel (SDK)
    start = time.time()
    asyncio.run(run_parallel_workflow())
    parallel_time = time.time() - start

    speedup = sequential_time / parallel_time
    print(f"Speedup: {speedup}x")
```

#### Acceptance Criteria
- [ ] At least one workflow migrated to SDK
- [ ] Parallel execution shows measurable performance gain (>1.5x)
- [ ] Existing functionality maintained
- [ ] Migration guide documented

---

## Phase 3: Memory and Context Preservation

**Duration**: 2 weeks
**Goal**: Add persistent memory and conversation context
**Risk**: Medium

### 3.1 Memory Backend Implementation (Days 1-4)

#### Tasks
- [ ] Implement `MemoryBackend` interface
- [ ] Implement `InMemoryBackend`
- [ ] Implement `AgentMemory` class
- [ ] Add conversation history tracking
- [ ] Implement TTL-based expiration

#### Code Structure

**agents_sdk/memory/backend.py**:
```python
from abc import ABC, abstractmethod
from typing import List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MemoryEntry:
    key: str
    value: Any
    timestamp: datetime
    ttl: Optional[int] = None

class MemoryBackend(ABC):
    @abstractmethod
    async def store(self, key: str, value: Any, ttl: Optional[int] = None):
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        pass

    @abstractmethod
    async def clear_expired(self):
        pass
```

**agents_sdk/memory/inmemory.py**:
```python
class InMemoryBackend(MemoryBackend):
    def __init__(self):
        self.storage: Dict[str, MemoryEntry] = {}

    async def store(self, key: str, value: Any, ttl: Optional[int] = None):
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=datetime.now(),
            ttl=ttl
        )
        self.storage[key] = entry

    async def retrieve(self, key: str) -> Optional[Any]:
        entry = self.storage.get(key)
        if entry:
            # Check expiration
            if entry.ttl:
                age = (datetime.now() - entry.timestamp).total_seconds()
                if age > entry.ttl:
                    del self.storage[key]
                    return None
            return entry.value
        return None

    async def clear_expired(self):
        now = datetime.now()
        expired = [
            k for k, v in self.storage.items()
            if v.ttl and (now - v.timestamp).total_seconds() > v.ttl
        ]
        for k in expired:
            del self.storage[k]
```

**agents_sdk/core/memory.py**:
```python
@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentMemory:
    def __init__(self, backend: MemoryBackend):
        self.backend = backend
        self.short_term: Dict[str, Any] = {}
        self.conversation_history: List[Message] = []

    async def store(self, key: str, value: Any, persist: bool = False):
        self.short_term[key] = value
        if persist:
            await self.backend.store(key, value)

    async def retrieve(self, key: str) -> Optional[Any]:
        # Try short-term first
        if key in self.short_term:
            return self.short_term[key]
        # Fall back to long-term
        return await self.backend.retrieve(key)

    def add_message(self, role: str, content: str, metadata: Dict = None):
        self.conversation_history.append(Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        ))

    def get_conversation_context(self, last_n: Optional[int] = None) -> str:
        messages = self.conversation_history[-last_n:] if last_n else self.conversation_history
        return "\n\n".join([
            f"[{msg.role.upper()}] {msg.content}"
            for msg in messages
        ])
```

#### Tests
```python
@pytest.mark.asyncio
async def test_memory_persistence():
    backend = InMemoryBackend()
    memory = AgentMemory(backend)

    # Store and retrieve
    await memory.store("key1", "value1", persist=True)
    value = await memory.retrieve("key1")
    assert value == "value1"

@pytest.mark.asyncio
async def test_conversation_history():
    backend = InMemoryBackend()
    memory = AgentMemory(backend)

    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there!")

    context = memory.get_conversation_context()
    assert "[USER] Hello" in context
    assert "[ASSISTANT] Hi there!" in context

@pytest.mark.asyncio
async def test_ttl_expiration():
    backend = InMemoryBackend()
    await backend.store("temp_key", "value", ttl=1)  # 1 second TTL

    value = await backend.retrieve("temp_key")
    assert value == "value"

    await asyncio.sleep(2)
    value = await backend.retrieve("temp_key")
    assert value is None  # Expired
```

#### Acceptance Criteria
- [ ] Memory stores and retrieves values correctly
- [ ] Conversation history tracked
- [ ] TTL expiration working
- [ ] All tests passing (>85% coverage)

### 3.2 Context-Aware Agent Execution (Days 5-7)

#### Tasks
- [ ] Integrate AgentMemory into AgentSession
- [ ] Add `include_history` parameter to execute()
- [ ] Implement conversation summarization for long histories
- [ ] Test context preservation across executions

#### Code Structure

**agents_sdk/core/session.py** (enhanced):
```python
class AgentSession:
    def __init__(
        self,
        session_id: str,
        agent_name: str,
        memory_backend: MemoryBackend,
        context: Optional[AgentContext] = None
    ):
        self.session_id = session_id
        self.agent_name = agent_name
        self.memory = AgentMemory(memory_backend)
        self.context = context or AgentContext(...)

    async def execute(
        self,
        prompt: str,
        model: str = "sonnet",
        include_history: bool = False,
        max_history_turns: int = 10
    ) -> AgentResponse:
        """Execute with optional conversation history."""

        # Build prompt with history if requested
        if include_history and self.memory.conversation_history:
            context = self.memory.get_conversation_context(
                last_n=max_history_turns
            )
            full_prompt = f"{context}\n\n[USER] {prompt}"
        else:
            full_prompt = prompt

        # Execute
        response = await self._execute_claude_code(full_prompt, model)

        # Store in conversation history
        self.memory.add_message("user", prompt)
        self.memory.add_message("assistant", response.output)

        return response
```

#### Tests
```python
@pytest.mark.asyncio
async def test_context_preservation():
    session = AgentSession("test", "agent", InMemoryBackend())

    # First execution
    response1 = await session.execute("What is 2+2?")
    assert response1.success

    # Second execution with history
    response2 = await session.execute(
        "What was my previous question?",
        include_history=True
    )

    # Agent should have context from previous turn
    assert "2+2" in response2.output or "previous question" in response2.output
```

#### Acceptance Criteria
- [ ] Conversation history included in prompts when requested
- [ ] History limited to `max_history_turns`
- [ ] Context preserved across multiple executions
- [ ] Tests validate context awareness

### 3.3 Long-Term Memory Patterns (Days 8-10)

#### Tasks
- [ ] Implement skill/learning storage
- [ ] Add memory search functionality
- [ ] Create memory cleanup utilities
- [ ] Document memory best practices

#### Code Structure

**agents_sdk/memory/patterns.py**:
```python
class MemoryPatterns:
    """Common memory patterns for agents."""

    @staticmethod
    async def store_skill(
        memory: AgentMemory,
        skill_name: str,
        skill_data: Dict[str, Any]
    ):
        """Store learned skill for reuse."""
        key = f"skill:{skill_name}"
        await memory.store(key, skill_data, persist=True)

    @staticmethod
    async def retrieve_skill(
        memory: AgentMemory,
        skill_name: str
    ) -> Optional[Dict]:
        """Retrieve learned skill."""
        key = f"skill:{skill_name}"
        return await memory.retrieve(key)

    @staticmethod
    async def cache_analysis(
        memory: AgentMemory,
        file_hash: str,
        analysis_result: Any,
        ttl: int = 3600
    ):
        """Cache expensive analysis with TTL."""
        key = f"cache:analysis:{file_hash}"
        await memory.store(key, analysis_result, persist=True)
        # Set TTL on backend
        await memory.backend.store(key, analysis_result, ttl=ttl)

    @staticmethod
    async def search_memories(
        memory: AgentMemory,
        query: str,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Search through stored memories."""
        return await memory.backend.search(query, limit)
```

#### Usage Examples
```python
# Store a learned checklist
await MemoryPatterns.store_skill(
    session.memory,
    "code_review_checklist",
    {
        "items": [
            "Check for SQL injection",
            "Verify input validation",
            "Ensure error handling"
        ],
        "confidence": 0.95
    }
)

# Cache expensive analysis
file_hash = hashlib.sha256(file_content.encode()).hexdigest()
await MemoryPatterns.cache_analysis(
    session.memory,
    file_hash,
    analysis_result,
    ttl=3600  # 1 hour
)

# Search memories
results = await MemoryPatterns.search_memories(
    session.memory,
    "security checklist",
    limit=5
)
```

#### Acceptance Criteria
- [ ] Common memory patterns implemented
- [ ] Skills can be stored and retrieved
- [ ] Caching working with TTL
- [ ] Search functionality implemented

---

## Phase 4: Advanced Features

**Duration**: 2 weeks
**Goal**: Production-ready features
**Risk**: Low

### 4.1 Event Bus for Agent Communication (Days 1-4)

#### Tasks
- [ ] Implement `EventBus` class
- [ ] Add pub/sub functionality
- [ ] Create common event types
- [ ] Add event history

#### Code Structure

**agents_sdk/events/event_bus.py**:
```python
from enum import Enum
from typing import Callable, Dict, List
from dataclasses import dataclass

class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Event:
    event_type: str
    payload: Any
    source_agent: str
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000

    async def publish(self, event: Event):
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        handlers = self.subscribers.get(event.event_type, [])
        tasks = [handler(event) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def get_history(self, event_type: Optional[str] = None) -> List[Event]:
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type]
        return self.event_history.copy()
```

#### Usage Examples
```python
# Create event bus
event_bus = EventBus()

# Subscribe to events
async def handle_task_completion(event: Event):
    print(f"Task {event.payload['task_id']} completed")

await event_bus.subscribe("task.completed", handle_task_completion)

# Publish events
await event_bus.publish(Event(
    event_type="task.completed",
    payload={"task_id": "build_001"},
    source_agent="builder"
))
```

#### Acceptance Criteria
- [ ] Pub/sub working correctly
- [ ] Multiple subscribers supported
- [ ] Event history maintained
- [ ] All tests passing

### 4.2 Streaming and Progress Callbacks (Days 5-7)

#### Tasks
- [ ] Add callback system to AgentSession
- [ ] Implement progress streaming
- [ ] Add real-time output parsing
- [ ] Test with long-running operations

#### Code Structure

**agents_sdk/core/callbacks.py**:
```python
from typing import Callable, Dict, Any

class CallbackManager:
    """Manages execution callbacks."""

    def __init__(self):
        self.callbacks: Dict[str, List[Callable]] = {}

    def register(self, event_name: str, callback: Callable):
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)

    async def trigger(self, event_name: str, *args, **kwargs):
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                await callback(*args, **kwargs)

# Usage in AgentSession
class AgentSession:
    def __init__(self, ..., callbacks: Optional[CallbackManager] = None):
        self.callbacks = callbacks or CallbackManager()

    async def execute(self, prompt: str, ...):
        await self.callbacks.trigger("on_start", prompt)

        # ... execution ...

        await self.callbacks.trigger("on_progress", {
            "percent": 50,
            "status": "Executing prompt..."
        })

        # ... more execution ...

        await self.callbacks.trigger("on_complete", response)
```

#### Usage Examples
```python
# Register callbacks
session = AgentSession("test", "agent")

async def show_progress(data):
    print(f"Progress: {data['percent']}% - {data['status']}")

session.callbacks.register("on_progress", show_progress)

# Execute with progress updates
response = await session.execute("long running task")
```

#### Acceptance Criteria
- [ ] Callbacks triggered at appropriate times
- [ ] Progress updates working
- [ ] Multiple callbacks supported per event
- [ ] Tests cover callback scenarios

### 4.3 Observability and Metrics (Days 8-10)

#### Tasks
- [ ] Add execution metrics collection
- [ ] Implement token usage tracking
- [ ] Create performance dashboards (basic)
- [ ] Add structured logging

#### Code Structure

**agents_sdk/observability/metrics.py**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class SessionMetrics:
    session_id: str
    agent_name: str
    total_executions: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_execution_time_ms: float = 0.0
    success_rate: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, SessionMetrics] = {}

    def record_execution(
        self,
        session_id: str,
        agent_name: str,
        tokens_used: int,
        execution_time_ms: int,
        success: bool
    ):
        if session_id not in self.metrics:
            self.metrics[session_id] = SessionMetrics(
                session_id=session_id,
                agent_name=agent_name
            )

        m = self.metrics[session_id]
        m.total_executions += 1
        m.total_tokens += tokens_used
        m.total_cost_usd += self._calculate_cost(tokens_used, agent_name)

        # Update running average
        m.avg_execution_time_ms = (
            (m.avg_execution_time_ms * (m.total_executions - 1) + execution_time_ms)
            / m.total_executions
        )

        # Update success rate
        successes = m.success_rate * (m.total_executions - 1) + (1 if success else 0)
        m.success_rate = successes / m.total_executions

    def get_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        return self.metrics.get(session_id)

    def _calculate_cost(self, tokens: int, model: str) -> float:
        # Simplified cost calculation
        rates = {
            "sonnet": 0.003 / 1000,  # per token
            "opus": 0.015 / 1000
        }
        return tokens * rates.get(model, 0.003)
```

#### Acceptance Criteria
- [ ] Metrics collected for all executions
- [ ] Token usage tracked accurately
- [ ] Cost calculations correct
- [ ] Metrics queryable

---

## Testing Strategy

### Unit Tests
- Target: >85% code coverage
- Tools: pytest, pytest-asyncio, pytest-cov
- Mock external dependencies (Claude Code CLI)

### Integration Tests
- Test with real Claude Code CLI (limited runs)
- Validate backward compatibility
- Test state persistence across restarts

### Performance Tests
- Benchmark parallel vs sequential execution
- Measure memory overhead
- Test with large conversation histories

### Migration Tests
- Ensure old workflows still work
- Validate data migration scripts
- Test feature flag switching

---

## Risk Mitigation

### Risk 1: Breaking Changes

**Mitigation**:
- Maintain backward compatibility layer
- Feature flags for gradual rollout
- Comprehensive test suite
- Documentation of migration path

### Risk 2: Performance Regression

**Mitigation**:
- Benchmarks for all phases
- Performance tests in CI/CD
- Profiling of critical paths
- Fallback to original implementation if needed

### Risk 3: State Migration Issues

**Mitigation**:
- Migration scripts with dry-run mode
- Backup procedures documented
- Rollback capability
- Schema versioning

### Risk 4: Adoption Resistance

**Mitigation**:
- Clear documentation
- Migration guides with examples
- Gradual rollout (opt-in first)
- Training sessions for team

---

## Success Metrics

### Phase 1
- [ ] All existing tests pass with SDK
- [ ] Feature flag working
- [ ] Zero production issues

### Phase 2
- [ ] 1.5x+ speedup for parallel workflows
- [ ] Retry logic reduces failures by 30%+
- [ ] At least 2 workflows migrated

### Phase 3
- [ ] Memory reduces repeated work by 40%+
- [ ] Context preservation improves agent accuracy
- [ ] No memory leaks

### Phase 4
- [ ] Event bus enables 3+ new workflow patterns
- [ ] Observability reduces debugging time by 50%+
- [ ] Production-ready for general use

---

## Rollout Plan

### Week 1-2 (Phase 1)
- Internal testing only
- Feature flag: `USE_AGENTS_SDK=false` by default

### Week 3-4 (Phase 2)
- Limited production testing on non-critical workflows
- Feature flag: `USE_AGENTS_SDK=true` for specific workflows

### Week 5-6 (Phase 3)
- Expanded production use
- Monitor metrics closely

### Week 7-8 (Phase 4)
- Full production rollout
- Deprecation plan for old implementation

---

## Deliverables Checklist

### Phase 1
- [ ] `agents_sdk/` package
- [ ] AgentSession implementation
- [ ] StateBackend implementations (JSON, SQLite)
- [ ] Backward compatibility layer
- [ ] Documentation

### Phase 2
- [ ] WorkflowOrchestrator
- [ ] Parallel execution
- [ ] Retry logic
- [ ] Performance benchmarks

### Phase 3
- [ ] MemoryBackend implementations
- [ ] AgentMemory integration
- [ ] Memory patterns library
- [ ] Memory best practices guide

### Phase 4
- [ ] EventBus
- [ ] Callback system
- [ ] Metrics collection
- [ ] Production monitoring

---

**Next Steps**:
1. Review and approve this plan
2. Set up project tracking (Jira/Linear)
3. Assign engineers to phases
4. Begin Phase 1 implementation

**Questions? Contact**: [Engineering Lead]
