# Agents SDK Architecture

**Version**: 1.0
**Date**: 2025-10-20
**Status**: Design Proposal
**Author**: System Architect AI

## Executive Summary

This document proposes a comprehensive Agents SDK architecture to transform the current "fire and forget" subprocess approach into a sophisticated multi-agent orchestration platform. The SDK will provide persistent agent memory, parallel coordination, state management, and robust error recovery while maintaining backward compatibility with existing ADW workflows.

**Current Pain Points**:
- No agent memory between invocations
- Sequential execution only (no parallelization)
- Basic error handling with no retry logic
- No agent-to-agent communication
- State management limited to file-based JSON
- No streaming or progress callbacks

**Proposed Solution**:
A layered SDK architecture with:
1. **Agent Core**: Enhanced agent invocation with memory and context
2. **Orchestrator Layer**: Parallel execution and workflow coordination
3. **State Management**: Multi-backend persistence (JSON, SQLite, Redis)
4. **Communication Protocol**: Agent-to-agent messaging and event bus
5. **Observability**: Metrics, tracing, and progress streaming

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Proposed Architecture](#2-proposed-architecture)
3. [Component Design](#3-component-design)
4. [State Management Strategy](#4-state-management-strategy)
5. [Memory Persistence Patterns](#5-memory-persistence-patterns)
6. [Inter-Agent Communication](#6-inter-agent-communication)
7. [Implementation Examples](#7-implementation-examples)
8. [Migration Path](#8-migration-path)
9. [Best Practices Guide](#9-best-practices-guide)

---

## 1. Current State Analysis

### 1.1 Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ADW Workflow Scripts                      │
│  (adw_plan.py, adw_build.py, adw_test.py, etc.)             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ calls execute_template()
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              workflow_ops.py                                 │
│  - build_plan()                                             │
│  - implement_plan()                                         │
│  - classify_issue()                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ uses
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              agent.py                                        │
│  - execute_template()                                       │
│  - prompt_claude_code()    ← CORE AGENT INVOCATION         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ subprocess.run()
                  ▼
┌─────────────────────────────────────────────────────────────┐
│           Claude Code CLI (claude)                           │
│  --model, --output-format stream-json, --verbose           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Current Agent Invocation Pattern

```python
# agent.py (current implementation)
def prompt_claude_code(request: AgentPromptRequest) -> AgentPromptResponse:
    """Execute Claude Code with the given prompt configuration."""

    # 1. Build command
    cmd = [CLAUDE_PATH, "-p", request.prompt]
    cmd.extend(["--model", request.model])
    cmd.extend(["--output-format", "stream-json"])
    cmd.append("--verbose")

    # 2. Execute subprocess (fire and forget)
    with open(request.output_file, "w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE,
                               text=True, env=get_claude_env())

    # 3. Parse JSONL output
    messages, result_message = parse_jsonl_output(request.output_file)

    # 4. Return response (no state preservation)
    return AgentPromptResponse(
        output=result_text,
        success=not is_error,
        session_id=session_id
    )
```

### 1.3 Current State Management

```python
# state.py (current implementation)
class ADWState:
    """Container for ADW workflow state with file persistence."""

    STATE_FILENAME = "adw_state.json"

    def __init__(self, adw_id: str):
        self.adw_id = adw_id
        self.data: Dict[str, Any] = {"adw_id": self.adw_id}

    def save(self, workflow_step: Optional[str] = None) -> None:
        """Save state to file in agents/{adw_id}/adw_state.json."""
        state_path = self.get_state_path()
        with open(state_path, "w") as f:
            json.dump(state_data.model_dump(), f, indent=2)

    @classmethod
    def load(cls, adw_id: str) -> Optional["ADWState"]:
        """Load state from file if it exists."""
        # Reads from agents/{adw_id}/adw_state.json
```

### 1.4 Identified Gaps

| Category | Current State | Gap | Impact |
|----------|--------------|-----|--------|
| **Agent Memory** | None - each invocation stateless | No context preservation | Agents repeat work, lose context |
| **Parallelization** | Sequential only | Can't run multiple agents concurrently | Slow execution |
| **Error Recovery** | Basic try/catch | No retry logic, circuit breakers | Fragile to transient failures |
| **Communication** | None | Agents can't coordinate | Limited workflow patterns |
| **State Backend** | JSON files only | No scalability options | Single-machine only |
| **Observability** | Logs to files | No metrics, traces, streaming | Hard to monitor |
| **Token Management** | Per-request limits | No budget management | Cost control issues |

### 1.5 Workflow Analysis

**Current Workflow Pattern** (adw_plan_build.py):
```python
# Sequential execution with no coordination
subprocess.run(["uv", "run", "adw_plan.py", issue_number, adw_id])
subprocess.run(["uv", "run", "adw_build.py", issue_number, adw_id])
```

**Issues**:
1. Scripts executed as separate processes
2. State passed via file system (agents/{adw_id}/adw_state.json)
3. No progress reporting during long operations
4. Failures require manual restart from beginning
5. No partial completion tracking

---

## 2. Proposed Architecture

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Application Layer                               │
│  Workflow Scripts: adw_plan.py, adw_build.py, etc.                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ uses
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Workflow   │  │   Parallel   │  │    Task      │            │
│  │ Orchestrator │  │   Executor   │  │   Manager    │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ coordinates
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Agent Core Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │    Agent     │  │    Memory    │  │   Context    │            │
│  │   Session    │  │   Manager    │  │   Manager    │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ uses
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │    State     │  │  Event Bus   │  │ Observability│            │
│  │   Backend    │  │              │  │              │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ executes
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                Claude Code CLI Execution                            │
│  subprocess management, output parsing, session tracking           │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Components

#### Agent Session
```python
class AgentSession:
    """Stateful agent session with memory and context preservation."""

    session_id: str
    agent_name: str
    memory: AgentMemory
    context: AgentContext
    metrics: SessionMetrics

    async def execute(self, prompt: str) -> AgentResponse
    async def execute_with_retry(self, prompt: str, max_retries: int = 3)
    def get_conversation_history(self) -> List[Message]
    def add_to_memory(self, key: str, value: Any)
    def get_from_memory(self, key: str) -> Optional[Any]
```

#### Workflow Orchestrator
```python
class WorkflowOrchestrator:
    """Coordinates multi-agent workflows with parallel execution."""

    workflow_id: str
    state_backend: StateBackend
    event_bus: EventBus

    async def run_workflow(self, workflow_spec: WorkflowSpec) -> WorkflowResult
    async def run_parallel(self, tasks: List[Task]) -> List[TaskResult]
    async def run_sequential(self, tasks: List[Task]) -> List[TaskResult]
    def checkpoint(self, checkpoint_name: str)
    def recover_from_checkpoint(self, checkpoint_name: str)
```

#### Memory Manager
```python
class MemoryManager:
    """Manages agent memory with persistence and retrieval."""

    backend: MemoryBackend  # JSON, SQLite, Redis, Vector DB

    async def store(self, key: str, value: Any, ttl: Optional[int] = None)
    async def retrieve(self, key: str) -> Optional[Any]
    async def search(self, query: str, limit: int = 10) -> List[MemoryEntry]
    async def clear_expired(self)
```

#### Event Bus
```python
class EventBus:
    """Pub/sub event system for agent communication."""

    async def publish(self, event: Event)
    async def subscribe(self, event_type: str, handler: Callable)
    async def unsubscribe(self, event_type: str, handler: Callable)
```

---

## 3. Component Design

### 3.1 Agent Core Components

#### AgentSession Class

```python
"""
Agent session with memory, context, and lifecycle management.
"""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from enum import Enum

class AgentStatus(Enum):
    """Agent session status."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentContext:
    """Context for agent execution."""
    working_directory: str
    environment: Dict[str, str]
    token_budget: Optional[int] = None
    tokens_used: int = 0
    max_execution_time: Optional[int] = None  # seconds

    def has_budget_remaining(self) -> bool:
        if self.token_budget is None:
            return True
        return self.tokens_used < self.token_budget

@dataclass
class Message:
    """A message in agent conversation history."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResponse:
    """Response from agent execution."""
    success: bool
    output: str
    session_id: str
    tokens_used: int
    execution_time_ms: int
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentMemory:
    """Agent memory with short-term and long-term storage."""

    def __init__(self, backend: "MemoryBackend"):
        self.backend = backend
        self.short_term: Dict[str, Any] = {}  # In-memory cache
        self.conversation_history: List[Message] = []

    async def store(self, key: str, value: Any, persist: bool = False):
        """Store value in memory."""
        self.short_term[key] = value
        if persist:
            await self.backend.store(key, value)

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from memory."""
        # Try short-term first
        if key in self.short_term:
            return self.short_term[key]
        # Fall back to long-term
        return await self.backend.retrieve(key)

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to conversation history."""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.conversation_history.append(message)

    def get_conversation_context(self, last_n: Optional[int] = None) -> str:
        """Get conversation history as formatted string."""
        messages = self.conversation_history[-last_n:] if last_n else self.conversation_history
        return "\n\n".join([
            f"[{msg.role.upper()}] {msg.content}"
            for msg in messages
        ])

class AgentSession:
    """Stateful agent session with memory and context preservation."""

    def __init__(
        self,
        session_id: str,
        agent_name: str,
        memory_backend: "MemoryBackend",
        context: Optional[AgentContext] = None,
        callbacks: Optional[Dict[str, Callable]] = None
    ):
        self.session_id = session_id
        self.agent_name = agent_name
        self.memory = AgentMemory(memory_backend)
        self.context = context or AgentContext(
            working_directory=os.getcwd(),
            environment={}
        )
        self.status = AgentStatus.IDLE
        self.callbacks = callbacks or {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    async def execute(
        self,
        prompt: str,
        model: str = "sonnet",
        include_history: bool = True
    ) -> AgentResponse:
        """Execute prompt with agent."""

        # Check token budget
        if not self.context.has_budget_remaining():
            return AgentResponse(
                success=False,
                output="",
                session_id=self.session_id,
                tokens_used=0,
                execution_time_ms=0,
                error="Token budget exceeded"
            )

        self.status = AgentStatus.RUNNING
        self._trigger_callback("on_start", prompt)

        try:
            # Build prompt with conversation history if requested
            if include_history and self.memory.conversation_history:
                context = self.memory.get_conversation_context(last_n=10)
                full_prompt = f"{context}\n\n[USER] {prompt}"
            else:
                full_prompt = prompt

            # Execute via Claude Code CLI
            request = AgentPromptRequest(
                prompt=full_prompt,
                adw_id=self.session_id,
                agent_name=self.agent_name,
                model=model,
                dangerously_skip_permissions=True,
                output_file=self._get_output_file()
            )

            response = await self._execute_claude_code(request)

            # Update memory
            self.memory.add_message("user", prompt)
            self.memory.add_message("assistant", response.output)

            # Update context
            self.context.tokens_used += response.tokens_used

            # Update status
            self.status = AgentStatus.COMPLETED if response.success else AgentStatus.FAILED
            self.last_activity = datetime.now()

            self._trigger_callback("on_complete", response)

            return response

        except Exception as e:
            self.status = AgentStatus.FAILED
            self._trigger_callback("on_error", e)
            raise

    async def execute_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> AgentResponse:
        """Execute with exponential backoff retry."""

        for attempt in range(max_retries):
            try:
                response = await self.execute(prompt)
                if response.success:
                    return response

                # If not last attempt, wait before retry
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    await asyncio.sleep(wait_time)

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)

        return AgentResponse(
            success=False,
            output="",
            session_id=self.session_id,
            tokens_used=0,
            execution_time_ms=0,
            error=f"Failed after {max_retries} retries"
        )

    def _trigger_callback(self, event_name: str, data: Any):
        """Trigger registered callback."""
        if event_name in self.callbacks:
            self.callbacks[event_name](self, data)

    def _get_output_file(self) -> str:
        """Get output file path for this session."""
        return f"agents/{self.session_id}/{self.agent_name}/raw_output.jsonl"

    async def _execute_claude_code(self, request: AgentPromptRequest) -> AgentResponse:
        """Execute Claude Code CLI (async wrapper)."""
        # Run prompt_claude_code in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, prompt_claude_code, request)
```

#### WorkflowOrchestrator Class

```python
"""
Workflow orchestration with parallel execution and checkpoint/recovery.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    """Individual task in workflow."""
    task_id: str
    agent_name: str
    prompt: str
    model: str = "sonnet"
    depends_on: List[str] = field(default_factory=list)  # Task IDs
    retry_count: int = 3
    timeout: Optional[int] = None  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    response: Optional[AgentResponse] = None
    error: Optional[str] = None
    execution_time_ms: int = 0

@dataclass
class WorkflowSpec:
    """Workflow specification."""
    workflow_id: str
    tasks: List[Task]
    max_parallel: int = 5
    checkpoint_interval: Optional[int] = None  # checkpoint every N tasks
    on_failure: str = "stop"  # "stop" or "continue"

@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    workflow_id: str
    success: bool
    task_results: List[TaskResult]
    total_time_ms: int
    checkpoints: List[str]

class WorkflowOrchestrator:
    """Coordinates multi-agent workflows with parallel execution."""

    def __init__(
        self,
        state_backend: "StateBackend",
        event_bus: Optional["EventBus"] = None
    ):
        self.state_backend = state_backend
        self.event_bus = event_bus
        self.sessions: Dict[str, AgentSession] = {}
        self.active_workflows: Dict[str, WorkflowResult] = {}

    async def run_workflow(
        self,
        workflow_spec: WorkflowSpec,
        memory_backend: "MemoryBackend"
    ) -> WorkflowResult:
        """Execute workflow with tasks."""

        workflow_id = workflow_spec.workflow_id
        start_time = datetime.now()

        # Load checkpoint if exists
        checkpoint_data = await self.state_backend.load_checkpoint(workflow_id)
        completed_tasks = set(checkpoint_data.get("completed_tasks", []))

        # Build dependency graph
        task_graph = self._build_dependency_graph(workflow_spec.tasks)

        # Execute tasks in dependency order
        task_results = []
        checkpoints = []

        while task_graph:
            # Find tasks with no dependencies (ready to run)
            ready_tasks = [
                task for task in task_graph
                if not task.depends_on or all(
                    dep_id in completed_tasks for dep_id in task.depends_on
                )
            ]

            if not ready_tasks:
                # Circular dependency detected
                break

            # Execute ready tasks in parallel (up to max_parallel)
            batch_results = await self._execute_parallel_batch(
                ready_tasks,
                workflow_spec.max_parallel,
                memory_backend
            )

            task_results.extend(batch_results)

            # Update completed tasks
            for result in batch_results:
                if result.status == TaskStatus.COMPLETED:
                    completed_tasks.add(result.task_id)
                    task_graph = [t for t in task_graph if t.task_id != result.task_id]
                elif result.status == TaskStatus.FAILED:
                    if workflow_spec.on_failure == "stop":
                        # Stop workflow on failure
                        break
                    else:
                        # Skip failed task and continue
                        completed_tasks.add(result.task_id)
                        task_graph = [t for t in task_graph if t.task_id != result.task_id]

            # Checkpoint if needed
            if workflow_spec.checkpoint_interval:
                if len(completed_tasks) % workflow_spec.checkpoint_interval == 0:
                    checkpoint_name = f"checkpoint_{len(completed_tasks)}"
                    await self._save_checkpoint(
                        workflow_id,
                        checkpoint_name,
                        completed_tasks,
                        task_results
                    )
                    checkpoints.append(checkpoint_name)

        end_time = datetime.now()
        total_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return WorkflowResult(
            workflow_id=workflow_id,
            success=all(r.status == TaskStatus.COMPLETED for r in task_results),
            task_results=task_results,
            total_time_ms=total_time_ms,
            checkpoints=checkpoints
        )

    async def _execute_parallel_batch(
        self,
        tasks: List[Task],
        max_parallel: int,
        memory_backend: "MemoryBackend"
    ) -> List[TaskResult]:
        """Execute batch of tasks in parallel."""

        results = []

        # Process in chunks of max_parallel
        for i in range(0, len(tasks), max_parallel):
            batch = tasks[i:i + max_parallel]

            # Create coroutines for each task
            coroutines = [
                self._execute_task(task, memory_backend)
                for task in batch
            ]

            # Execute in parallel
            batch_results = await asyncio.gather(*coroutines, return_exceptions=True)

            # Handle results and exceptions
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

    async def _execute_task(
        self,
        task: Task,
        memory_backend: "MemoryBackend"
    ) -> TaskResult:
        """Execute individual task."""

        start_time = datetime.now()

        # Get or create agent session
        session = await self._get_or_create_session(
            task.agent_name,
            memory_backend
        )

        try:
            # Execute with retry
            response = await session.execute_with_retry(
                prompt=task.prompt,
                max_retries=task.retry_count
            )

            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED if response.success else TaskStatus.FAILED,
                response=response,
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time_ms
            )

    async def _get_or_create_session(
        self,
        agent_name: str,
        memory_backend: "MemoryBackend"
    ) -> AgentSession:
        """Get existing session or create new one."""

        if agent_name not in self.sessions:
            session_id = f"{agent_name}_{uuid.uuid4().hex[:8]}"
            self.sessions[agent_name] = AgentSession(
                session_id=session_id,
                agent_name=agent_name,
                memory_backend=memory_backend
            )

        return self.sessions[agent_name]

    def _build_dependency_graph(self, tasks: List[Task]) -> List[Task]:
        """Build task dependency graph."""
        # Simple implementation - return tasks as-is
        # In production, would validate dependencies and detect cycles
        return tasks.copy()

    async def _save_checkpoint(
        self,
        workflow_id: str,
        checkpoint_name: str,
        completed_tasks: set,
        task_results: List[TaskResult]
    ):
        """Save workflow checkpoint."""
        checkpoint_data = {
            "checkpoint_name": checkpoint_name,
            "completed_tasks": list(completed_tasks),
            "task_results": [
                {
                    "task_id": r.task_id,
                    "status": r.status.value,
                    "execution_time_ms": r.execution_time_ms
                }
                for r in task_results
            ]
        }
        await self.state_backend.save_checkpoint(workflow_id, checkpoint_data)
```

---

## 4. State Management Strategy

### 4.1 Multi-Backend Architecture

```python
"""
Pluggable state backend system.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
import json
import sqlite3
import redis
from pathlib import Path

class StateBackend(ABC):
    """Abstract state backend interface."""

    @abstractmethod
    async def save(self, key: str, value: Any):
        """Save state."""
        pass

    @abstractmethod
    async def load(self, key: str) -> Optional[Any]:
        """Load state."""
        pass

    @abstractmethod
    async def delete(self, key: str):
        """Delete state."""
        pass

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix."""
        pass

    @abstractmethod
    async def save_checkpoint(self, workflow_id: str, checkpoint_data: Dict):
        """Save workflow checkpoint."""
        pass

    @abstractmethod
    async def load_checkpoint(self, workflow_id: str) -> Dict:
        """Load workflow checkpoint."""
        pass

class JSONFileBackend(StateBackend):
    """File-based state backend (current implementation)."""

    def __init__(self, base_dir: str = "agents"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, key: str, value: Any):
        """Save to JSON file."""
        file_path = self.base_dir / f"{key}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(value, f, indent=2)

    async def load(self, key: str) -> Optional[Any]:
        """Load from JSON file."""
        file_path = self.base_dir / f"{key}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            return json.load(f)

    async def delete(self, key: str):
        """Delete JSON file."""
        file_path = self.base_dir / f"{key}.json"
        if file_path.exists():
            file_path.unlink()

    async def list_keys(self, prefix: str = "") -> List[str]:
        """List all JSON files."""
        pattern = f"{prefix}*.json" if prefix else "*.json"
        return [
            p.stem for p in self.base_dir.glob(pattern)
        ]

    async def save_checkpoint(self, workflow_id: str, checkpoint_data: Dict):
        """Save workflow checkpoint."""
        checkpoint_key = f"{workflow_id}/checkpoint"
        await self.save(checkpoint_key, checkpoint_data)

    async def load_checkpoint(self, workflow_id: str) -> Dict:
        """Load workflow checkpoint."""
        checkpoint_key = f"{workflow_id}/checkpoint"
        data = await self.load(checkpoint_key)
        return data or {}

class SQLiteBackend(StateBackend):
    """SQLite-based state backend for better querying."""

    def __init__(self, db_path: str = "agents/state.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                workflow_id TEXT,
                checkpoint_name TEXT,
                checkpoint_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (workflow_id, checkpoint_name)
            )
        """)

        conn.commit()
        conn.close()

    async def save(self, key: str, value: Any):
        """Save to SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        value_json = json.dumps(value)
        cursor.execute("""
            INSERT OR REPLACE INTO state (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value_json))

        conn.commit()
        conn.close()

    async def load(self, key: str) -> Optional[Any]:
        """Load from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM state WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    async def delete(self, key: str):
        """Delete from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM state WHERE key = ?", (key,))
        conn.commit()
        conn.close()

    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if prefix:
            cursor.execute(
                "SELECT key FROM state WHERE key LIKE ?",
                (f"{prefix}%",)
            )
        else:
            cursor.execute("SELECT key FROM state")

        keys = [row[0] for row in cursor.fetchall()]
        conn.close()
        return keys

    async def save_checkpoint(self, workflow_id: str, checkpoint_data: Dict):
        """Save workflow checkpoint."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        checkpoint_name = checkpoint_data.get("checkpoint_name", "latest")
        data_json = json.dumps(checkpoint_data)

        cursor.execute("""
            INSERT OR REPLACE INTO checkpoints
            (workflow_id, checkpoint_name, checkpoint_data, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (workflow_id, checkpoint_name, data_json))

        conn.commit()
        conn.close()

    async def load_checkpoint(self, workflow_id: str) -> Dict:
        """Load latest workflow checkpoint."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT checkpoint_data FROM checkpoints
            WHERE workflow_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (workflow_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return {}

class RedisBackend(StateBackend):
    """Redis-based state backend for distributed systems."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)

    async def save(self, key: str, value: Any):
        """Save to Redis."""
        value_json = json.dumps(value)
        self.redis.set(key, value_json)

    async def load(self, key: str) -> Optional[Any]:
        """Load from Redis."""
        value_json = self.redis.get(key)
        if value_json:
            return json.loads(value_json)
        return None

    async def delete(self, key: str):
        """Delete from Redis."""
        self.redis.delete(key)

    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix."""
        pattern = f"{prefix}*" if prefix else "*"
        return [k.decode() for k in self.redis.keys(pattern)]

    async def save_checkpoint(self, workflow_id: str, checkpoint_data: Dict):
        """Save workflow checkpoint."""
        checkpoint_key = f"checkpoint:{workflow_id}"
        checkpoint_json = json.dumps(checkpoint_data)
        self.redis.set(checkpoint_key, checkpoint_json)

    async def load_checkpoint(self, workflow_id: str) -> Dict:
        """Load workflow checkpoint."""
        checkpoint_key = f"checkpoint:{workflow_id}"
        checkpoint_json = self.redis.get(checkpoint_key)
        if checkpoint_json:
            return json.loads(checkpoint_json)
        return {}
```

### 4.2 Backend Selection Strategy

| Use Case | Recommended Backend | Rationale |
|----------|-------------------|-----------|
| **Development** | JSONFileBackend | Simple, debuggable, no dependencies |
| **Single Machine Production** | SQLiteBackend | Better querying, atomicity, reasonable performance |
| **Distributed Systems** | RedisBackend | Distributed state, pub/sub, high performance |
| **Large-Scale** | Vector DB (future) | Semantic memory search, embeddings |

---

## 5. Memory Persistence Patterns

### 5.1 Memory Backend Interface

```python
"""
Memory persistence for agent context and history.
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MemoryEntry:
    """Single memory entry."""
    key: str
    value: Any
    timestamp: datetime
    ttl: Optional[int] = None  # Time to live in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

class MemoryBackend(ABC):
    """Abstract memory backend interface."""

    @abstractmethod
    async def store(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store value in memory."""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from memory."""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries."""
        pass

    @abstractmethod
    async def clear_expired(self):
        """Clear expired entries."""
        pass

    @abstractmethod
    async def list_keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern."""
        pass

class InMemoryBackend(MemoryBackend):
    """Simple in-memory backend (for development)."""

    def __init__(self):
        self.storage: Dict[str, MemoryEntry] = {}

    async def store(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store in dictionary."""
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=datetime.now(),
            ttl=ttl
        )
        self.storage[key] = entry

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from dictionary."""
        entry = self.storage.get(key)
        if entry:
            # Check if expired
            if entry.ttl:
                age_seconds = (datetime.now() - entry.timestamp).total_seconds()
                if age_seconds > entry.ttl:
                    del self.storage[key]
                    return None
            return entry.value
        return None

    async def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Simple substring search."""
        results = []
        for entry in self.storage.values():
            if query.lower() in str(entry.value).lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    async def clear_expired(self):
        """Remove expired entries."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.storage.items()
            if entry.ttl and (now - entry.timestamp).total_seconds() > entry.ttl
        ]
        for key in expired_keys:
            del self.storage[key]

    async def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys."""
        # Simple implementation - could add fnmatch for patterns
        return list(self.storage.keys())
```

### 5.2 Memory Patterns

#### Conversation History
```python
# Store conversation turns
await memory.store(
    f"conversation:{session_id}:{turn_number}",
    {"role": "user", "content": prompt}
)

# Retrieve last N turns
turns = []
for i in range(max(0, current_turn - 10), current_turn):
    turn_data = await memory.retrieve(f"conversation:{session_id}:{i}")
    if turn_data:
        turns.append(turn_data)
```

#### Task Results Cache
```python
# Cache expensive operations
cache_key = f"analysis:{file_hash}"
cached_result = await memory.retrieve(cache_key)

if cached_result:
    return cached_result

result = await expensive_analysis(file)
await memory.store(cache_key, result, ttl=3600)  # 1 hour TTL
```

#### Agent Skills/Learnings
```python
# Store learned patterns
await memory.store(
    f"skill:{agent_name}:code_review_checklist",
    {
        "items": [
            "Check for SQL injection",
            "Verify input validation",
            "Ensure proper error handling"
        ],
        "confidence": 0.95
    }
)
```

---

## 6. Inter-Agent Communication

### 6.1 Event Bus Design

```python
"""
Event-driven communication between agents.
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio

class EventPriority(Enum):
    """Event priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Event:
    """Event published to bus."""
    event_type: str
    payload: Any
    source_agent: str
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None

class EventBus:
    """Pub/sub event system for agent communication."""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000

    async def publish(self, event: Event):
        """Publish event to all subscribers."""
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Notify subscribers
        handlers = self.subscribers.get(event.event_type, [])
        handlers.extend(self.subscribers.get("*", []))  # Wildcard subscribers

        # Call handlers asynchronously
        tasks = [handler(event) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                h for h in self.subscribers[event_type] if h != handler
            ]

    def get_history(
        self,
        event_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history with filters."""
        events = self.event_history

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events[-limit:]
```

### 6.2 Communication Patterns

#### Task Delegation
```python
# Agent A delegates task to Agent B
await event_bus.publish(Event(
    event_type="task.delegated",
    payload={
        "task_id": "analyze_code",
        "target_agent": "code_analyzer",
        "prompt": "Analyze main.py for security issues"
    },
    source_agent="orchestrator"
))

# Agent B subscribes to delegated tasks
async def handle_task_delegation(event: Event):
    if event.payload["target_agent"] == "code_analyzer":
        result = await analyze_code(event.payload["prompt"])
        await event_bus.publish(Event(
            event_type="task.completed",
            payload={"task_id": event.payload["task_id"], "result": result},
            source_agent="code_analyzer",
            correlation_id=event.correlation_id
        ))

await event_bus.subscribe("task.delegated", handle_task_delegation)
```

#### Progress Streaming
```python
# Agent publishes progress updates
async def long_running_task():
    for i in range(100):
        # Do work
        await event_bus.publish(Event(
            event_type="progress.update",
            payload={"percent": i, "status": f"Processing item {i}"},
            source_agent="builder"
        ))

    await event_bus.publish(Event(
        event_type="task.completed",
        payload={"success": True},
        source_agent="builder"
    ))

# UI subscribes to progress
async def show_progress(event: Event):
    print(f"Progress: {event.payload['percent']}% - {event.payload['status']}")

await event_bus.subscribe("progress.update", show_progress)
```

#### Error Propagation
```python
# Agent publishes error
await event_bus.publish(Event(
    event_type="error.occurred",
    payload={
        "error_type": "APIError",
        "message": "Rate limit exceeded",
        "retry_after": 60
    },
    source_agent="github_client",
    priority=EventPriority.HIGH
))

# Orchestrator handles errors
async def handle_error(event: Event):
    if event.payload["error_type"] == "APIError":
        # Implement circuit breaker logic
        await pause_agent(event.source_agent, event.payload["retry_after"])

await event_bus.subscribe("error.occurred", handle_error)
```

---

## 7. Implementation Examples

### 7.1 Basic Usage

```python
"""
Example: Simple agent session usage.
"""

from agents_sdk import (
    AgentSession,
    InMemoryBackend,
    JSONFileBackend
)

# Initialize backends
memory_backend = InMemoryBackend()
state_backend = JSONFileBackend()

# Create agent session
session = AgentSession(
    session_id="plan_001",
    agent_name="sdlc_planner",
    memory_backend=memory_backend,
    callbacks={
        "on_start": lambda session, prompt: print(f"Starting: {prompt}"),
        "on_complete": lambda session, response: print(f"Done: {response.success}")
    }
)

# Execute with memory
response = await session.execute(
    prompt="/chore 123 adw_001 {\"title\": \"Fix typo\"}",
    model="sonnet",
    include_history=True
)

print(f"Success: {response.success}")
print(f"Output: {response.output}")
print(f"Tokens used: {response.tokens_used}")
```

### 7.2 Workflow Orchestration

```python
"""
Example: Parallel workflow execution.
"""

from agents_sdk import (
    WorkflowOrchestrator,
    WorkflowSpec,
    Task,
    SQLiteBackend
)

# Create orchestrator
orchestrator = WorkflowOrchestrator(
    state_backend=SQLiteBackend()
)

# Define workflow
workflow = WorkflowSpec(
    workflow_id="plan_build_test",
    tasks=[
        Task(
            task_id="plan",
            agent_name="sdlc_planner",
            prompt="/feature 42 adw_001 {\"title\": \"Add auth\"}",
            model="opus"
        ),
        Task(
            task_id="build",
            agent_name="sdlc_implementor",
            prompt="/implement specs/plan.md",
            model="opus",
            depends_on=["plan"]  # Wait for plan to complete
        ),
        Task(
            task_id="test",
            agent_name="test_runner",
            prompt="/test specs/plan.md",
            model="sonnet",
            depends_on=["build"]  # Wait for build to complete
        ),
        Task(
            task_id="document",
            agent_name="documenter",
            prompt="/document specs/plan.md",
            model="sonnet",
            depends_on=["build"]  # Parallel with test
        )
    ],
    max_parallel=2,
    checkpoint_interval=2,
    on_failure="stop"
)

# Execute workflow
result = await orchestrator.run_workflow(
    workflow_spec=workflow,
    memory_backend=InMemoryBackend()
)

print(f"Workflow success: {result.success}")
print(f"Total time: {result.total_time_ms}ms")
print(f"Checkpoints: {result.checkpoints}")

for task_result in result.task_results:
    print(f"Task {task_result.task_id}: {task_result.status.value}")
```

### 7.3 Event-Driven Coordination

```python
"""
Example: Event-driven agent coordination.
"""

from agents_sdk import EventBus, Event, EventPriority

event_bus = EventBus()

# Subscribe agents to events
async def planner_handler(event: Event):
    if event.event_type == "issue.created":
        # Plan the issue
        plan_result = await create_plan(event.payload["issue_number"])

        # Publish plan completed event
        await event_bus.publish(Event(
            event_type="plan.completed",
            payload={"plan_file": plan_result.plan_file},
            source_agent="planner"
        ))

async def builder_handler(event: Event):
    if event.event_type == "plan.completed":
        # Build from plan
        build_result = await build_from_plan(event.payload["plan_file"])

        # Publish build completed event
        await event_bus.publish(Event(
            event_type="build.completed",
            payload={"success": build_result.success},
            source_agent="builder"
        ))

# Register handlers
await event_bus.subscribe("issue.created", planner_handler)
await event_bus.subscribe("plan.completed", builder_handler)

# Trigger workflow by publishing initial event
await event_bus.publish(Event(
    event_type="issue.created",
    payload={"issue_number": "42"},
    source_agent="github_webhook",
    priority=EventPriority.HIGH
))
```

---

## 8. Migration Path

### 8.1 Phase 1: Backward Compatible Layer (Week 1-2)

**Goal**: Wrap existing `prompt_claude_code()` with SDK without breaking changes

```python
"""
Backward compatibility wrapper for existing code.
"""

# New SDK wrapper that maintains existing interface
def prompt_claude_code_v2(request: AgentPromptRequest) -> AgentPromptResponse:
    """Enhanced version with session management."""

    # Get or create session for this agent
    session = get_global_session(
        agent_name=request.agent_name,
        adw_id=request.adw_id
    )

    # Execute with session (adds memory automatically)
    response = asyncio.run(session.execute(
        prompt=request.prompt,
        model=request.model,
        include_history=False  # Disable for backward compat
    ))

    # Return in same format as original
    return AgentPromptResponse(
        output=response.output,
        success=response.success,
        session_id=response.session_id
    )

# Alias for gradual migration
# prompt_claude_code = prompt_claude_code_v2
```

**Changes**:
- Add `agents_sdk/` package alongside `adw_modules/`
- Implement core classes (AgentSession, MemoryBackend, StateBackend)
- Keep existing `agent.py` and `workflow_ops.py` unchanged
- Add opt-in flag: `USE_AGENTS_SDK=true` in environment

### 8.2 Phase 2: Orchestrator Integration (Week 3-4)

**Goal**: Replace sequential subprocess calls with WorkflowOrchestrator

**Before** (adw_plan_build.py):
```python
subprocess.run(["uv", "run", "adw_plan.py", issue_number, adw_id])
subprocess.run(["uv", "run", "adw_build.py", issue_number, adw_id])
```

**After**:
```python
from agents_sdk import WorkflowOrchestrator, WorkflowSpec, Task

orchestrator = WorkflowOrchestrator(state_backend=SQLiteBackend())

workflow = WorkflowSpec(
    workflow_id=f"plan_build_{adw_id}",
    tasks=[
        Task(
            task_id="plan",
            agent_name="sdlc_planner",
            prompt=f"/feature {issue_number} {adw_id} {issue_json}"
        ),
        Task(
            task_id="build",
            agent_name="sdlc_implementor",
            prompt=f"/implement {plan_file}",
            depends_on=["plan"]
        )
    ]
)

result = await orchestrator.run_workflow(workflow)
```

**Changes**:
- Create new entry points: `adws_v2/adw_plan_build.py`
- Maintain old scripts for gradual migration
- Add feature flag to switch between versions

### 8.3 Phase 3: Parallel Execution (Week 5-6)

**Goal**: Enable parallel agent execution for independent tasks

**Example**: Run tests and documentation in parallel
```python
workflow = WorkflowSpec(
    workflow_id=f"full_sdlc_{adw_id}",
    tasks=[
        Task(task_id="plan", agent_name="planner", ...),
        Task(task_id="build", agent_name="builder", depends_on=["plan"]),
        # These run in parallel after build completes
        Task(task_id="test", agent_name="tester", depends_on=["build"]),
        Task(task_id="document", agent_name="documenter", depends_on=["build"]),
        # Review waits for both test and document
        Task(task_id="review", agent_name="reviewer",
             depends_on=["test", "document"])
    ],
    max_parallel=3
)
```

**Changes**:
- Implement dependency graph execution
- Add `asyncio` support to existing workflows
- Optimize for parallel I/O operations

### 8.4 Phase 4: Advanced Features (Week 7-8)

**Goal**: Add streaming, callbacks, and advanced memory

**Features**:
- Streaming progress updates via event bus
- Callback hooks for UI integration
- Semantic memory search with embeddings
- Circuit breakers and rate limiting
- Comprehensive observability

---

## 9. Best Practices Guide

### 9.1 When to Use Sync vs Async

| Use Case | Pattern | Rationale |
|----------|---------|-----------|
| **Single agent call** | Sync | Simple, no concurrency needed |
| **Sequential workflow** | Sync or Async | Async enables timeouts/cancellation |
| **Parallel tasks** | Async | Required for concurrent execution |
| **Event-driven** | Async | Pub/sub requires async handlers |
| **Long-running** | Async | Prevents blocking, enables streaming |

**Example**:
```python
# Sync: Simple classification
response = prompt_claude_code(classification_request)

# Async: Parallel analysis
results = await asyncio.gather(
    analyze_security(file),
    analyze_performance(file),
    analyze_style(file)
)
```

### 9.2 Memory Management Strategies

#### Short-Term vs Long-Term Memory

```python
# Short-term: Current conversation
session.memory.store("current_plan", plan_data, persist=False)

# Long-term: Learnings across sessions
session.memory.store("security_checklist", checklist, persist=True)
```

#### Memory Cleanup

```python
# Set TTL for temporary data
await memory.store("cache:analysis", result, ttl=3600)  # 1 hour

# Periodic cleanup
async def cleanup_loop():
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        await memory.clear_expired()

asyncio.create_task(cleanup_loop())
```

### 9.3 Error Handling Patterns

#### Retry with Backoff

```python
# Built-in retry
response = await session.execute_with_retry(
    prompt=task_prompt,
    max_retries=3,
    backoff_factor=2.0
)
```

#### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            # Check if timeout elapsed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitOpenError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```

### 9.4 Testing Strategies

#### Unit Testing

```python
# Test agent session
@pytest.mark.asyncio
async def test_agent_session():
    memory_backend = InMemoryBackend()
    session = AgentSession(
        session_id="test_001",
        agent_name="test_agent",
        memory_backend=memory_backend
    )

    # Mock Claude Code execution
    with patch("agents_sdk.agent.prompt_claude_code") as mock:
        mock.return_value = AgentPromptResponse(
            output="Test output",
            success=True,
            session_id="test_001",
            tokens_used=100,
            execution_time_ms=500
        )

        response = await session.execute("test prompt")
        assert response.success
        assert len(session.memory.conversation_history) == 2
```

#### Integration Testing

```python
# Test workflow orchestration
@pytest.mark.asyncio
async def test_workflow_orchestration():
    orchestrator = WorkflowOrchestrator(
        state_backend=JSONFileBackend("test_agents")
    )

    workflow = WorkflowSpec(
        workflow_id="test_workflow",
        tasks=[
            Task(task_id="task1", agent_name="agent1", prompt="test"),
            Task(task_id="task2", agent_name="agent2", prompt="test",
                 depends_on=["task1"])
        ]
    )

    result = await orchestrator.run_workflow(workflow, InMemoryBackend())

    assert result.success
    assert len(result.task_results) == 2
    assert result.task_results[1].task_id == "task2"
```

### 9.5 Performance Optimization

#### Connection Pooling

```python
# Reuse agent sessions
class SessionPool:
    def __init__(self, max_sessions: int = 10):
        self.sessions = {}
        self.max_sessions = max_sessions

    async def get_session(self, agent_name: str) -> AgentSession:
        if agent_name not in self.sessions:
            if len(self.sessions) >= self.max_sessions:
                # Evict least recently used
                lru_agent = min(
                    self.sessions.keys(),
                    key=lambda k: self.sessions[k].last_activity
                )
                del self.sessions[lru_agent]

            self.sessions[agent_name] = AgentSession(...)

        return self.sessions[agent_name]
```

#### Caching Strategy

```python
# Cache expensive operations
@lru_cache(maxsize=100)
async def get_file_analysis(file_hash: str):
    return await analyze_file(file_hash)

# Warm cache on startup
async def warm_cache():
    for file in frequently_accessed_files:
        await get_file_analysis(file.hash)
```

---

## Appendices

### A. Architecture Decision Records

#### ADR-001: Multi-Backend State Management

**Status**: Proposed
**Date**: 2025-10-20

**Context**: Current system uses JSON files for state. Need to support distributed deployments and better querying.

**Decision**: Implement pluggable StateBackend interface with JSON, SQLite, and Redis implementations.

**Consequences**:
- ✅ Flexibility to choose backend based on deployment
- ✅ Easy to add new backends (e.g., PostgreSQL)
- ⚠️ Increased complexity in state management layer
- ⚠️ Need migration tools between backends

#### ADR-002: Async/Await for Orchestration

**Status**: Proposed
**Date**: 2025-10-20

**Context**: Need parallel agent execution without multi-processing overhead.

**Decision**: Use asyncio for concurrent task execution.

**Consequences**:
- ✅ Efficient I/O concurrency
- ✅ Single Python process (easier debugging)
- ⚠️ All code must be async-aware
- ⚠️ Learning curve for contributors

#### ADR-003: Event Bus for Agent Communication

**Status**: Proposed
**Date**: 2025-10-20

**Context**: Agents need to communicate without tight coupling.

**Decision**: Implement pub/sub event bus for agent coordination.

**Consequences**:
- ✅ Decoupled agent communication
- ✅ Easy to add new event handlers
- ✅ Observable system behavior
- ⚠️ Debugging can be harder (implicit connections)
- ⚠️ Need event schema versioning

### B. API Reference

See separate `agents_sdk/docs/API.md` for complete API documentation.

### C. Glossary

- **Agent Session**: Stateful agent instance with memory and context
- **Memory Backend**: Storage system for agent memory (conversation history, learnings)
- **State Backend**: Storage system for workflow state and checkpoints
- **Event Bus**: Pub/sub system for inter-agent communication
- **Workflow**: Directed acyclic graph (DAG) of tasks with dependencies
- **Task**: Single unit of work executed by an agent
- **Checkpoint**: Snapshot of workflow state for recovery

---

**End of Document**

*This architecture provides a solid foundation for transforming the current ADW system into a production-ready multi-agent orchestration platform while maintaining backward compatibility and enabling gradual migration.*
