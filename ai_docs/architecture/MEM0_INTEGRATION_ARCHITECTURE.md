# Mem0 Integration Architecture for ADW System

**Version**: 1.0
**Created**: 2025-10-20
**Status**: Design Complete - Implementation Ready

## Executive Summary

This document specifies the integration of mem0 (persistent memory for AI agents) into the ADW workflow system. The integration provides cross-session learning, pattern recognition, and context retention without disrupting the existing three-tier orchestration architecture.

**Core Value Proposition**:
- **Session Continuity**: Remember previous work patterns across days/weeks
- **Pattern Recognition**: Learn file associations, coding preferences, error resolutions
- **Context Efficiency**: Reduce redundant discovery by recalling relevant patterns
- **Decision Learning**: Build institutional knowledge from implementation decisions

**Integration Principle**: Memory as a **read-heavy advisory layer** - never blocks workflow, always enhances with learned context.

---

## 1. Mem0 Capabilities Analysis

### 1.1 Core API Operations

```python
from mem0 import Memory

# Initialize (uses Qdrant vector DB + OpenAI embeddings by default)
memory = Memory()

# Add memories (auto-extracts facts from messages)
memory.add(
    messages="Implemented JWT auth using passport.js library",
    user_id="project_scout_mvp",
    metadata={"workflow": "adw_build", "adw_id": "ext001", "issue_type": "feature"}
)

# Search memories (vector similarity)
results = memory.search(
    query="authentication patterns",
    user_id="project_scout_mvp",
    limit=5,
    threshold=0.7  # Relevance score
)

# Get all memories (filtered)
all_auth = memory.get_all(
    user_id="project_scout_mvp",
    filters={"issue_type": "feature"},
    limit=100
)

# Delete specific memory
memory.delete(memory_id="mem_123")

# Delete all memories for scope
memory.delete_all(user_id="project_scout_mvp")
```

### 1.2 Memory Scoping Strategy

Mem0 supports three ID scopes: `user_id`, `agent_id`, `run_id`. For ADW:

| Scope | ADW Mapping | Use Case |
|-------|-------------|----------|
| `user_id` | `"project_{repo_name}"` | Project-wide memories (files, patterns, decisions) |
| `agent_id` | `"adw_{workflow_type}"` | Workflow-specific patterns (e.g., "adw_scout", "adw_build") |
| `run_id` | `adw_id` (e.g., "ext001") | Session-specific context (current task execution) |

**Design Decision**: Use `user_id` for project scope, `agent_id` for workflow type, `run_id` for task session.

```python
# Example: Scout workflow remembers file patterns for this project
memory.add(
    messages="Files in adws/adw_modules/ contain core workflow operations",
    user_id="project_scout_mvp",
    agent_id="adw_scout",
    metadata={"category": "file_patterns", "directory": "adws/adw_modules"}
)

# Example: Build workflow remembers implementation decisions
memory.add(
    messages="Used Pydantic for validation in workflow_ops.py to prevent injection",
    user_id="project_scout_mvp",
    agent_id="adw_build",
    run_id="ext001",
    metadata={"category": "implementation_decision", "file": "workflow_ops.py"}
)
```

### 1.3 Storage & Performance

- **Vector Store**: Qdrant (local file: `/tmp/qdrant/` by default)
- **History DB**: SQLite (`~/.mem0/history.db`)
- **Embedding Model**: OpenAI `text-embedding-ada-002` (1536 dims)
- **Query Performance**: ~50-100ms for vector search (local Qdrant)
- **Storage Cost**: ~1KB per memory entry (vectorized)

**Performance Impact**: Negligible (<200ms added to workflow phases).

---

## 2. Integration Architecture

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  ADW Three-Tier Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TIER 1: Slash Commands (scout.md, plan_w_docs.md)         │
│           ↓                                                  │
│  TIER 2: Workflow Shims (adw_plan.py, adw_build.py)        │
│           ↓                                                  │
│  TIER 3: Core Modules (workflow_ops.py, agent.py)          │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ (new) Memory Hooks
                       ↓
┌─────────────────────────────────────────────────────────────┐
│               Mem0 Integration Layer (NEW)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  memory_hooks.py:                                           │
│    - pre_scout_recall()    → Recall file patterns          │
│    - post_scout_learn()    → Learn file discoveries        │
│    - pre_plan_recall()     → Recall design patterns        │
│    - post_plan_learn()     → Learn architecture decisions  │
│    - post_build_learn()    → Learn implementation patterns │
│    - on_error_learn()      → Learn failure resolutions     │
│                                                              │
│  memory_manager.py:                                         │
│    - MemoryManager class (singleton, lazy-init)            │
│    - remember(), recall(), forget(), summarize()           │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 Mem0 Storage (Local)                         │
├─────────────────────────────────────────────────────────────┤
│  Qdrant Vector DB: /tmp/qdrant/                            │
│  History DB: ~/.mem0/history.db                            │
│  Config: Optional project-specific override                │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Hook Injection Points

**Design Principle**: Hooks are **non-blocking advisory calls** - workflow proceeds even if memory operations fail.

| Phase | Hook | Location | Purpose |
|-------|------|----------|---------|
| **Pre-Scout** | `pre_scout_recall()` | Before `/scout` execution | Suggest files based on similar past tasks |
| **Post-Scout** | `post_scout_learn()` | After file list aggregated | Learn file-task associations |
| **Pre-Plan** | `pre_plan_recall()` | Before `/plan_w_docs` execution | Recall architecture patterns, doc preferences |
| **Post-Plan** | `post_plan_learn()` | After plan saved to `specs/` | Learn design decisions, risk patterns |
| **Post-Build** | `post_build_learn()` | After `/implement` completes | Learn implementation patterns, library choices |
| **On-Error** | `on_error_learn()` | When exceptions caught | Learn error patterns and resolutions |
| **Cross-Session** | `session_load()` / `session_save()` | ADWState lifecycle | Persist session-specific insights |

### 2.3 Integration Code Pattern

**Example: Scout Phase with Memory**

```python
# In adws/adw_plan.py (or slash command scout.md)

from adw_modules.memory_hooks import pre_scout_recall, post_scout_learn

def scout_workflow(task_description: str, scale: int = 4):
    """Scout workflow enhanced with memory recall."""

    # 1. RECALL: Get file suggestions from past similar tasks
    try:
        memory_hints = pre_scout_recall(
            task_description=task_description,
            project_id="project_scout_mvp"
        )
        # memory_hints = {
        #   "suggested_files": ["adws/adw_modules/workflow_ops.py", ...],
        #   "key_insights": "Auth tasks typically involve state.py and validators.py",
        #   "confidence": 0.85
        # }

        if memory_hints["confidence"] > 0.7:
            logger.info(f"Memory recall: {memory_hints['key_insights']}")
            logger.info(f"Suggested files: {memory_hints['suggested_files'][:5]}")
    except Exception as e:
        # Memory failure NEVER blocks workflow
        logger.warning(f"Memory recall failed (non-blocking): {e}")
        memory_hints = None

    # 2. EXECUTE: Run scout as normal (existing logic)
    scout_results = run_parallel_scout_agents(task_description, scale)

    # 3. LEARN: Save file discoveries for future recall
    try:
        post_scout_learn(
            task_description=task_description,
            scout_results=scout_results,
            project_id="project_scout_mvp",
            adw_id="ext001"
        )
        logger.info("Learned file patterns for future tasks")
    except Exception as e:
        logger.warning(f"Memory learning failed (non-blocking): {e}")

    return scout_results
```

**Key Properties**:
- ✅ Memory operations wrapped in try-except (never crash workflow)
- ✅ Confidence thresholds (only use high-confidence recalls)
- ✅ Logging for observability
- ✅ Graceful degradation (works without mem0)

---

## 3. Memory Schema Design

### 3.1 Memory Categories

We store five types of memories:

| Category | What We Learn | Example Memory |
|----------|---------------|----------------|
| **file_patterns** | File-task associations | "Auth tasks involve adws/adw_modules/validators.py and state.py" |
| **design_decisions** | Architecture choices & rationale | "Use Pydantic for validation to prevent injection attacks" |
| **implementation_patterns** | Code patterns, library choices | "JWT auth implemented with passport.js, not custom crypto" |
| **error_resolutions** | Failed scenarios & fixes | "Token limit errors fixed by setting CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768" |
| **session_context** | Task-specific insights | "Issue #123 required parallel agent execution for performance" |

### 3.2 Memory Metadata Schema

```python
from typing import TypedDict, Optional, Literal

class MemoryMetadata(TypedDict, total=False):
    """Standardized metadata for ADW memories."""

    # Categorization
    category: Literal[
        "file_patterns",
        "design_decisions",
        "implementation_patterns",
        "error_resolutions",
        "session_context"
    ]

    # Scoping
    workflow: Literal["adw_scout", "adw_plan", "adw_build", "adw_test", "adw_review"]
    adw_id: Optional[str]  # Session ID (e.g., "ext001")
    issue_number: Optional[int]  # GitHub issue reference
    issue_type: Optional[Literal["feature", "bug", "chore"]]

    # File references
    file: Optional[str]  # Single file (e.g., "workflow_ops.py")
    files: Optional[list[str]]  # Multiple files
    directory: Optional[str]  # Directory (e.g., "adws/adw_modules")

    # Context
    timestamp: str  # ISO 8601 timestamp
    confidence: float  # 0.0-1.0 (how confident is this memory?)
    tags: Optional[list[str]]  # Freeform tags (e.g., ["auth", "security"])

    # Source tracking
    agent_name: Optional[str]  # Which agent created this (e.g., "sdlc_planner")
    source: Optional[str]  # How was this learned? (e.g., "scout_results", "plan_analysis")
```

### 3.3 Memory Storage Examples

**Example 1: File Pattern Memory**

```python
memory.add(
    messages=(
        "Authentication tasks typically involve these files: "
        "adws/adw_modules/validators.py (input validation), "
        "adws/adw_modules/state.py (session management), "
        "adws/adw_modules/exceptions.py (error handling)"
    ),
    user_id="project_scout_mvp",
    agent_id="adw_scout",
    metadata={
        "category": "file_patterns",
        "workflow": "adw_scout",
        "tags": ["auth", "security"],
        "files": [
            "adws/adw_modules/validators.py",
            "adws/adw_modules/state.py",
            "adws/adw_modules/exceptions.py"
        ],
        "confidence": 0.9,
        "timestamp": "2025-10-20T15:30:00Z",
        "source": "scout_results"
    }
)
```

**Example 2: Design Decision Memory**

```python
memory.add(
    messages=(
        "Decision: Use Pydantic models for all input validation in workflow_ops.py. "
        "Rationale: Prevents injection attacks and provides runtime type checking. "
        "Alternative considered: Manual validation (rejected due to error-prone nature)."
    ),
    user_id="project_scout_mvp",
    agent_id="adw_plan",
    run_id="ext001",
    metadata={
        "category": "design_decisions",
        "workflow": "adw_plan",
        "file": "adws/adw_modules/workflow_ops.py",
        "tags": ["validation", "security", "pydantic"],
        "confidence": 1.0,
        "timestamp": "2025-10-20T15:45:00Z",
        "agent_name": "sdlc_planner",
        "source": "plan_analysis"
    }
)
```

**Example 3: Error Resolution Memory**

```python
memory.add(
    messages=(
        "Error: Token limit exceeded during Claude Code execution. "
        "Solution: Set environment variable CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768. "
        "Also added to utils.py line 181. Fixed permanently."
    ),
    user_id="project_scout_mvp",
    agent_id="adw_build",
    metadata={
        "category": "error_resolutions",
        "workflow": "adw_build",
        "file": "adws/adw_modules/utils.py",
        "tags": ["token_limit", "claude_code", "environment"],
        "confidence": 1.0,
        "timestamp": "2025-10-20T16:00:00Z",
        "source": "error_handler"
    }
)
```

**Example 4: Implementation Pattern Memory**

```python
memory.add(
    messages=(
        "Implemented parallel agent execution using Task tool spawning pattern. "
        "Each subagent immediately calls Bash tool for external tools (gemini, opencode, codex). "
        "This avoids thread management and leverages Claude Code's native concurrency."
    ),
    user_id="project_scout_mvp",
    agent_id="adw_scout",
    run_id="ext001",
    metadata={
        "category": "implementation_patterns",
        "workflow": "adw_scout",
        "tags": ["parallelization", "task_tool", "performance"],
        "confidence": 0.95,
        "timestamp": "2025-10-20T16:15:00Z",
        "agent_name": "sdlc_implementor",
        "source": "build_reflection"
    }
)
```

---

## 4. Hook Implementation Specifications

### 4.1 Pre-Scout Recall Hook

**Purpose**: Suggest relevant files based on task description similarity.

```python
def pre_scout_recall(
    task_description: str,
    project_id: str,
    limit: int = 10,
    threshold: float = 0.7
) -> dict:
    """Recall file patterns from past similar tasks.

    Args:
        task_description: Current task (e.g., "add JWT authentication")
        project_id: Project scope (e.g., "project_scout_mvp")
        limit: Max memories to retrieve
        threshold: Minimum relevance score (0.0-1.0)

    Returns:
        {
            "suggested_files": ["path/to/file.py", ...],
            "key_insights": "Summary of relevant patterns",
            "confidence": 0.85,
            "memories": [{"id": "mem_123", "memory": "...", "score": 0.9}, ...]
        }
    """
    memory = MemoryManager.get_instance()

    # Search for similar tasks
    results = memory.search(
        query=task_description,
        user_id=project_id,
        agent_id="adw_scout",
        filters={"category": "file_patterns"},
        limit=limit,
        threshold=threshold
    )

    if not results or not results.get("results"):
        return {
            "suggested_files": [],
            "key_insights": "No prior patterns found",
            "confidence": 0.0,
            "memories": []
        }

    # Extract files from metadata
    suggested_files = []
    for mem in results["results"]:
        metadata = mem.get("metadata", {})
        if "files" in metadata:
            suggested_files.extend(metadata["files"])
        elif "file" in metadata:
            suggested_files.append(metadata["file"])

    # Deduplicate and sort by frequency
    file_counts = {}
    for f in suggested_files:
        file_counts[f] = file_counts.get(f, 0) + 1

    sorted_files = sorted(file_counts.keys(), key=lambda x: file_counts[x], reverse=True)

    # Generate insights summary
    top_memory = results["results"][0]
    key_insights = top_memory.get("memory", "")[:200]  # Truncate
    avg_confidence = sum(m.get("score", 0) for m in results["results"]) / len(results["results"])

    return {
        "suggested_files": sorted_files[:limit],
        "key_insights": key_insights,
        "confidence": avg_confidence,
        "memories": results["results"]
    }
```

### 4.2 Post-Scout Learn Hook

**Purpose**: Save file discoveries for future recall.

```python
def post_scout_learn(
    task_description: str,
    scout_results: dict,
    project_id: str,
    adw_id: str
) -> None:
    """Learn file patterns from scout results.

    Args:
        task_description: Original task
        scout_results: Scout output (file list + key_findings)
        project_id: Project scope
        adw_id: Session ID
    """
    memory = MemoryManager.get_instance()

    # Extract files from scout results
    files = []
    if "files" in scout_results:
        files = [f["path"] for f in scout_results["files"]]

    if not files:
        return  # Nothing to learn

    # Create memory message
    message = (
        f"Task '{task_description}' involved these files: "
        f"{', '.join(files[:10])}"  # Limit to top 10 files
    )

    if "key_findings" in scout_results:
        findings = scout_results["key_findings"]
        if "summary" in findings:
            message += f". Key insight: {findings['summary']}"

    # Store memory
    memory.add(
        messages=message,
        user_id=project_id,
        agent_id="adw_scout",
        run_id=adw_id,
        metadata={
            "category": "file_patterns",
            "workflow": "adw_scout",
            "files": files[:20],  # Limit metadata size
            "confidence": 0.8,  # Moderate confidence (scout heuristic)
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "scout_results"
        }
    )
```

### 4.3 Pre-Plan Recall Hook

**Purpose**: Recall architecture patterns and design decisions.

```python
def pre_plan_recall(
    task_description: str,
    project_id: str,
    issue_type: str,  # "feature" | "bug" | "chore"
    limit: int = 5,
    threshold: float = 0.7
) -> dict:
    """Recall design patterns from past planning sessions.

    Returns:
        {
            "design_patterns": ["Use Pydantic for validation", ...],
            "architecture_recommendations": "...",
            "confidence": 0.75,
            "memories": [...]
        }
    """
    memory = MemoryManager.get_instance()

    # Search for similar plans
    results = memory.search(
        query=task_description,
        user_id=project_id,
        agent_id="adw_plan",
        filters={"category": "design_decisions", "issue_type": issue_type},
        limit=limit,
        threshold=threshold
    )

    if not results or not results.get("results"):
        return {
            "design_patterns": [],
            "architecture_recommendations": "No prior patterns found",
            "confidence": 0.0,
            "memories": []
        }

    # Extract patterns
    patterns = [mem.get("memory", "") for mem in results["results"]]

    # Aggregate into recommendations
    recommendations = "\n".join([
        f"- {pattern[:150]}" for pattern in patterns[:3]
    ])

    avg_confidence = sum(m.get("score", 0) for m in results["results"]) / len(results["results"])

    return {
        "design_patterns": patterns,
        "architecture_recommendations": recommendations,
        "confidence": avg_confidence,
        "memories": results["results"]
    }
```

### 4.4 Post-Plan Learn Hook

**Purpose**: Extract and save design decisions from plan files.

```python
def post_plan_learn(
    plan_file: str,
    project_id: str,
    adw_id: str,
    issue_type: str
) -> None:
    """Extract design decisions from plan markdown.

    Parses plan sections like:
    - Architecture/Approach
    - Risks and Mitigation
    - Implementation Steps

    And stores key decisions as memories.
    """
    memory = MemoryManager.get_instance()

    # Read plan file
    with open(plan_file, "r") as f:
        plan_content = f.read()

    # Extract sections (simplified - could use markdown parser)
    sections = {
        "architecture": extract_section(plan_content, "Architecture/Approach"),
        "risks": extract_section(plan_content, "Risks and Mitigation"),
        "implementation": extract_section(plan_content, "Implementation Steps")
    }

    # Store architecture decisions
    if sections["architecture"]:
        memory.add(
            messages=f"Architecture decision: {sections['architecture'][:500]}",
            user_id=project_id,
            agent_id="adw_plan",
            run_id=adw_id,
            metadata={
                "category": "design_decisions",
                "workflow": "adw_plan",
                "issue_type": issue_type,
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "plan_analysis"
            }
        )

    # Store risk patterns
    if sections["risks"]:
        memory.add(
            messages=f"Risk mitigation: {sections['risks'][:500]}",
            user_id=project_id,
            agent_id="adw_plan",
            run_id=adw_id,
            metadata={
                "category": "design_decisions",
                "workflow": "adw_plan",
                "tags": ["risk", "mitigation"],
                "confidence": 0.85,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "plan_analysis"
            }
        )
```

### 4.5 Post-Build Learn Hook

**Purpose**: Learn implementation patterns from successful builds.

```python
def post_build_learn(
    build_report_file: str,
    project_id: str,
    adw_id: str
) -> None:
    """Extract implementation patterns from build report.

    Build reports contain:
    - Files changed
    - Libraries used
    - Implementation decisions
    - Test results
    """
    memory = MemoryManager.get_instance()

    # Read build report
    with open(build_report_file, "r") as f:
        report_content = f.read()

    # Parse report (simplified - could use structured format)
    files_changed = extract_files_changed(report_content)
    libraries_used = extract_libraries(report_content)

    # Store implementation pattern
    if libraries_used:
        message = f"Implementation used libraries: {', '.join(libraries_used)}"
        memory.add(
            messages=message,
            user_id=project_id,
            agent_id="adw_build",
            run_id=adw_id,
            metadata={
                "category": "implementation_patterns",
                "workflow": "adw_build",
                "files": files_changed,
                "tags": libraries_used,
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "build_report"
            }
        )
```

### 4.6 On-Error Learn Hook

**Purpose**: Save error patterns and resolutions.

```python
def on_error_learn(
    error: Exception,
    context: dict,
    resolution: Optional[str] = None,
    project_id: str = "project_scout_mvp"
) -> None:
    """Learn from errors for future prevention.

    Args:
        error: Exception that occurred
        context: Error context (workflow, file, etc.)
        resolution: How it was fixed (if known)
        project_id: Project scope
    """
    memory = MemoryManager.get_instance()

    error_type = type(error).__name__
    error_message = str(error)

    # Build memory message
    message = f"Error: {error_type}: {error_message}"
    if resolution:
        message += f". Solution: {resolution}"

    # Extract workflow from context
    workflow = context.get("workflow", "unknown")

    memory.add(
        messages=message,
        user_id=project_id,
        agent_id=f"adw_{workflow}",
        metadata={
            "category": "error_resolutions",
            "workflow": f"adw_{workflow}",
            "tags": [error_type.lower(), "error"],
            "confidence": 1.0 if resolution else 0.5,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "error_handler",
            **context  # Include file, adw_id, etc.
        }
    )
```

---

## 5. MemoryManager Class Design

### 5.1 Singleton Pattern

```python
# adws/adw_modules/memory_manager.py

from mem0 import Memory
from typing import Optional, Dict, Any
import logging

class MemoryManager:
    """Singleton wrapper for mem0.Memory with ADW-specific helpers."""

    _instance: Optional["MemoryManager"] = None
    _memory: Optional[Memory] = None

    def __init__(self):
        """Private constructor - use get_instance() instead."""
        if MemoryManager._instance is not None:
            raise RuntimeError("Use MemoryManager.get_instance()")

        self.logger = logging.getLogger(__name__)
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "MemoryManager":
        """Get or create singleton instance (lazy initialization)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_initialized(self):
        """Initialize mem0 on first use (lazy pattern)."""
        if self._initialized:
            return

        try:
            # Initialize mem0 with default config
            # (uses Qdrant + OpenAI by default)
            self._memory = Memory()
            self._initialized = True
            self.logger.info("Mem0 initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize mem0: {e}")
            self._memory = None
            self._initialized = False

    def is_available(self) -> bool:
        """Check if mem0 is available and working."""
        self._ensure_initialized()
        return self._memory is not None

    def add(self, messages: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Add memory (wrapper with error handling)."""
        if not self.is_available():
            self.logger.warning("Mem0 not available, skipping add")
            return None

        try:
            result = self._memory.add(messages=messages, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            return None

    def search(self, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Search memories (wrapper with error handling)."""
        if not self.is_available():
            self.logger.warning("Mem0 not available, skipping search")
            return {"results": []}

        try:
            results = self._memory.search(query=query, **kwargs)
            return results
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return {"results": []}

    def get_all(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Get all memories (wrapper with error handling)."""
        if not self.is_available():
            return {"results": []}

        try:
            results = self._memory.get_all(**kwargs)
            return results
        except Exception as e:
            self.logger.error(f"Failed to get memories: {e}")
            return {"results": []}

    def delete(self, memory_id: str) -> bool:
        """Delete specific memory."""
        if not self.is_available():
            return False

        try:
            self._memory.delete(memory_id=memory_id)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}")
            return False

    def summarize_project(self, project_id: str) -> str:
        """Generate summary of project learnings."""
        if not self.is_available():
            return "Memory system unavailable"

        # Get all memories for project
        all_memories = self.get_all(user_id=project_id, limit=100)

        if not all_memories or not all_memories.get("results"):
            return "No learnings recorded yet"

        # Group by category
        by_category = {}
        for mem in all_memories["results"]:
            cat = mem.get("metadata", {}).get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(mem.get("memory", ""))

        # Format summary
        summary = f"Project Learnings ({len(all_memories['results'])} memories):\n\n"
        for cat, memories in by_category.items():
            summary += f"**{cat.replace('_', ' ').title()}**: {len(memories)} memories\n"
            summary += f"  - {memories[0][:100]}...\n"

        return summary
```

### 5.2 Configuration Override

Support project-specific config via environment or config file:

```python
# Optional: Load custom config
import os
from mem0.configs.base import MemoryConfig

def get_memory_config() -> Optional[MemoryConfig]:
    """Get custom mem0 config if specified."""

    # Check for custom Qdrant path
    qdrant_path = os.getenv("ADW_MEMORY_QDRANT_PATH")
    if qdrant_path:
        return MemoryConfig(
            vector_store={
                "provider": "qdrant",
                "config": {
                    "path": qdrant_path
                }
            }
        )

    return None  # Use defaults

# In MemoryManager._ensure_initialized():
config = get_memory_config()
self._memory = Memory(config=config) if config else Memory()
```

---

## 6. Workflow Integration Examples

### 6.1 Enhanced Scout Workflow

```python
# In .claude/commands/scout.md or adws/adw_plan.py

from adw_modules.memory_hooks import pre_scout_recall, post_scout_learn

def enhanced_scout(task_description: str, scale: int = 4):
    """Scout with memory recall."""

    logger.info(f"Scout: {task_description}")

    # RECALL: Get file hints
    try:
        hints = pre_scout_recall(
            task_description=task_description,
            project_id="project_scout_mvp"
        )

        if hints["confidence"] > 0.7:
            logger.info(f"💡 Memory recall (confidence: {hints['confidence']:.2f}):")
            logger.info(f"   Suggested files: {hints['suggested_files'][:5]}")
            logger.info(f"   Insight: {hints['key_insights']}")

            # Could pass hints to scout agents as context
            # (not implemented in initial version - just log)
    except Exception as e:
        logger.warning(f"Memory recall failed: {e}")

    # EXECUTE: Run scout (existing logic)
    scout_results = run_scout_agents(task_description, scale)

    # LEARN: Save discoveries
    try:
        post_scout_learn(
            task_description=task_description,
            scout_results=scout_results,
            project_id="project_scout_mvp",
            adw_id=state.get("adw_id")
        )
        logger.info("✅ Learned file patterns")
    except Exception as e:
        logger.warning(f"Memory learning failed: {e}")

    return scout_results
```

### 6.2 Enhanced Plan Workflow

```python
# In adws/adw_plan.py

from adw_modules.memory_hooks import pre_plan_recall, post_plan_learn

def enhanced_plan(issue: GitHubIssue, command: str, adw_id: str):
    """Plan with design pattern recall."""

    # RECALL: Get design patterns
    try:
        patterns = pre_plan_recall(
            task_description=issue.title,
            project_id="project_scout_mvp",
            issue_type=command.replace("/", "")
        )

        if patterns["confidence"] > 0.6:
            logger.info(f"💡 Recalled design patterns:")
            logger.info(patterns["architecture_recommendations"])

            # Could inject patterns into planner prompt
            # (not implemented initially - just log)
    except Exception as e:
        logger.warning(f"Memory recall failed: {e}")

    # EXECUTE: Run planning (existing logic)
    plan_response = build_plan(issue, command, adw_id, logger)
    plan_file = extract_plan_file(plan_response.output)

    # LEARN: Extract decisions
    try:
        post_plan_learn(
            plan_file=plan_file,
            project_id="project_scout_mvp",
            adw_id=adw_id,
            issue_type=command.replace("/", "")
        )
        logger.info("✅ Learned design decisions")
    except Exception as e:
        logger.warning(f"Memory learning failed: {e}")

    return plan_response
```

### 6.3 Enhanced Error Handling

```python
# In adw_modules/exceptions.py or workflow_ops.py

from adw_modules.memory_hooks import on_error_learn

def handle_workflow_error(error: Exception, context: dict):
    """Handle error with memory learning."""

    # Log error
    logger.error(f"Error in {context.get('workflow')}: {error}")

    # Learn from error (non-blocking)
    try:
        on_error_learn(
            error=error,
            context=context,
            resolution=None,  # Unknown yet
            project_id="project_scout_mvp"
        )
    except Exception as e:
        logger.warning(f"Failed to learn from error: {e}")

    # Re-raise or return error response
    raise error
```

---

## 7. Performance & Resource Analysis

### 7.1 Memory Operation Costs

| Operation | Latency | API Calls | Storage |
|-----------|---------|-----------|---------|
| `add()` | 100-300ms | 1 OpenAI embed + 1 Qdrant write | ~1KB/memory |
| `search()` | 50-150ms | 1 OpenAI embed + 1 Qdrant query | Read-only |
| `get_all()` | 20-50ms | 0 OpenAI (no embed) + 1 Qdrant scan | Read-only |
| `delete()` | 10-30ms | 0 OpenAI + 1 Qdrant delete | Frees storage |

**Total Added Latency Per Workflow Phase**:
- Scout: ~400ms (1 recall + 1 learn)
- Plan: ~400ms (1 recall + 1 learn)
- Build: ~200ms (1 learn only)
- **Total**: ~1 second added to full workflow (vs 5.5 min baseline = 0.3% overhead)

### 7.2 Storage Projections

Assuming **100 tasks/month** over **1 year**:

| Category | Memories/Task | Total/Year | Storage |
|----------|---------------|------------|---------|
| file_patterns | 1 | 1,200 | 1.2 MB |
| design_decisions | 2 | 2,400 | 2.4 MB |
| implementation_patterns | 1 | 1,200 | 1.2 MB |
| error_resolutions | 0.5 | 600 | 0.6 MB |
| **Total** | **4.5** | **5,400** | **5.4 MB** |

**Conclusion**: Negligible storage cost (~5 MB/year).

### 7.3 Cost Analysis (OpenAI Embeddings)

OpenAI `text-embedding-ada-002` pricing: **$0.0001 / 1K tokens**

| Phase | Tokens/Embed | Embeds/Task | Cost/Task |
|-------|-------------|-------------|-----------|
| Scout recall | 50 | 1 | $0.000005 |
| Scout learn | 100 | 1 | $0.00001 |
| Plan recall | 50 | 1 | $0.000005 |
| Plan learn | 200 | 2 | $0.00004 |
| Build learn | 150 | 1 | $0.000015 |
| **Total** | | **6** | **$0.000075** |

**Per 100 tasks**: ~$0.0075 (less than 1 cent)
**Per year (1,200 tasks)**: ~$0.09

**Conclusion**: Effectively free compared to Claude API costs ($0.05-0.50 per task).

### 7.4 Scaling Limits

**Qdrant Local Performance**:
- **10K memories**: Search ~50ms
- **100K memories**: Search ~100ms
- **1M memories**: Search ~200ms (still acceptable)

**Recommendation**: Local Qdrant sufficient for 1-10 year project lifespans. If scaling beyond 1M memories, consider Qdrant Cloud.

---

## 8. Privacy & Security Considerations

### 8.1 Sensitive Data Handling

**What We Store**:
- ✅ File paths (safe)
- ✅ Architecture decisions (safe)
- ✅ Library names (safe)
- ✅ Error types (safe)

**What We NEVER Store**:
- ❌ Credentials (API keys, passwords)
- ❌ User data (PII, emails, etc.)
- ❌ Secret configuration values
- ❌ Full file contents (only summaries)

**Sanitization Strategy**:

```python
import re

def sanitize_memory_content(content: str) -> str:
    """Remove sensitive patterns before storing."""

    # Redact API keys
    content = re.sub(r'api_key["\']?\s*[:=]\s*["\']?[\w-]+', 'api_key=REDACTED', content, flags=re.IGNORECASE)

    # Redact tokens
    content = re.sub(r'token["\']?\s*[:=]\s*["\']?[\w-]+', 'token=REDACTED', content, flags=re.IGNORECASE)

    # Redact passwords
    content = re.sub(r'password["\']?\s*[:=]\s*["\']?\S+', 'password=REDACTED', content, flags=re.IGNORECASE)

    # Redact email addresses
    content = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', 'EMAIL_REDACTED', content)

    return content

# In memory_hooks.py:
memory.add(
    messages=sanitize_memory_content(message),
    ...
)
```

### 8.2 Data Retention Policy

```python
def cleanup_old_memories(project_id: str, max_age_days: int = 365):
    """Delete memories older than retention period."""
    memory = MemoryManager.get_instance()

    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

    # Get all memories for project
    all_memories = memory.get_all(user_id=project_id, limit=1000)

    deleted_count = 0
    for mem in all_memories.get("results", []):
        timestamp_str = mem.get("metadata", {}).get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", ""))
            if timestamp < cutoff_date:
                memory.delete(mem["id"])
                deleted_count += 1

    logger.info(f"Cleaned up {deleted_count} old memories")

# Run periodically (e.g., weekly cron job)
```

### 8.3 Access Control

Mem0 scopes memories by `user_id`/`agent_id`/`run_id`. For multi-project deployments:

```python
def get_project_id() -> str:
    """Get project-specific memory scope from git repo."""
    from adw_modules.github import get_repo_url

    repo_url = get_repo_url()
    # Extract repo name: "github.com/owner/repo" -> "project_repo"
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    return f"project_{repo_name}"

# In memory hooks:
project_id = get_project_id()  # Auto-scoped per repo
```

**Result**: Memories are isolated per repository (no cross-contamination).

---

## 9. Migration & Rollout Strategy

### 9.1 Phase 1: Non-Blocking Integration (Week 1)

**Goal**: Deploy memory hooks without changing existing behavior.

**Steps**:
1. Add `memory_manager.py` and `memory_hooks.py` modules
2. Integrate hooks in workflows with try-except wrappers
3. Log all memory operations (don't use recall results yet)
4. Monitor for errors (memory failures should never crash workflows)

**Success Criteria**:
- ✅ 100% workflow success rate (with or without mem0)
- ✅ Memory operations logged but not acting on recalls
- ✅ No performance degradation (latency <200ms added)

### 9.2 Phase 2: Recall Activation (Week 2)

**Goal**: Start using memory recalls to inform workflows.

**Steps**:
1. Enable scout file suggestions (log in output, don't auto-include)
2. Enable plan pattern suggestions (log in output)
3. Human review of suggestions for accuracy
4. Tune confidence thresholds based on feedback

**Success Criteria**:
- ✅ Recall suggestions logged and visible to agents
- ✅ >70% recall relevance (human-evaluated)
- ✅ No false positives causing workflow failures

### 9.3 Phase 3: Auto-Enhancement (Week 3+)

**Goal**: Automatically inject high-confidence recalls into prompts.

**Steps**:
1. Inject file suggestions into scout agent prompts (if confidence >0.8)
2. Inject design patterns into planner prompts (if confidence >0.75)
3. Monitor for improvement in task quality
4. A/B test: workflows with vs without memory enhancement

**Success Criteria**:
- ✅ Measurable quality improvement (fewer iterations, better file selection)
- ✅ No negative side effects (no degraded plans)
- ✅ Positive user feedback

### 9.4 Rollback Plan

If memory integration causes issues:

```python
# Emergency disable flag
ADW_MEMORY_ENABLED = os.getenv("ADW_MEMORY_ENABLED", "true").lower() == "true"

# In MemoryManager.is_available():
if not ADW_MEMORY_ENABLED:
    return False

# Set environment variable to disable:
export ADW_MEMORY_ENABLED=false
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# tests/test_memory_manager.py

import pytest
from adw_modules.memory_manager import MemoryManager

def test_singleton_pattern():
    """MemoryManager should be singleton."""
    m1 = MemoryManager.get_instance()
    m2 = MemoryManager.get_instance()
    assert m1 is m2

def test_graceful_degradation():
    """Memory operations should never crash on failure."""
    manager = MemoryManager.get_instance()

    # Even if mem0 fails, should return None/empty
    result = manager.add(messages="test", user_id="test_project")
    assert result is None or isinstance(result, dict)

def test_sanitization():
    """Sensitive data should be redacted."""
    from adw_modules.memory_hooks import sanitize_memory_content

    content = "api_key='sk-1234567890' password=secret123"
    sanitized = sanitize_memory_content(content)

    assert "sk-1234567890" not in sanitized
    assert "secret123" not in sanitized
    assert "REDACTED" in sanitized
```

### 10.2 Integration Tests

```python
# tests/test_memory_integration.py

def test_scout_with_memory(tmp_path):
    """Scout workflow should work with memory hooks."""

    # First run: learn patterns
    results1 = enhanced_scout("add authentication", scale=2)
    assert "files" in results1

    # Second run: recall patterns
    results2 = enhanced_scout("add authentication", scale=2)
    # Should log recalled patterns (check logs)

    # Results should be valid regardless of memory
    assert "files" in results2

def test_memory_isolation():
    """Memories should be scoped per project."""

    # Add memory for project A
    memory = MemoryManager.get_instance()
    memory.add(
        messages="Project A pattern",
        user_id="project_a"
    )

    # Search in project B should not find it
    results = memory.search(
        query="Project A pattern",
        user_id="project_b"
    )
    assert len(results.get("results", [])) == 0
```

### 10.3 Performance Tests

```python
def test_memory_latency():
    """Memory operations should be fast (<500ms)."""
    import time

    memory = MemoryManager.get_instance()

    # Test add latency
    start = time.time()
    memory.add(
        messages="Test memory for latency",
        user_id="test_project"
    )
    add_latency = time.time() - start
    assert add_latency < 0.5  # 500ms threshold

    # Test search latency
    start = time.time()
    memory.search(
        query="Test memory",
        user_id="test_project"
    )
    search_latency = time.time() - start
    assert search_latency < 0.3  # 300ms threshold
```

---

## 11. Monitoring & Observability

### 11.1 Metrics to Track

```python
# In memory_manager.py

class MemoryMetrics:
    """Track memory operation metrics."""

    def __init__(self):
        self.add_count = 0
        self.search_count = 0
        self.recall_hits = 0  # Searches with results
        self.recall_misses = 0  # Searches with no results
        self.errors = 0
        self.total_latency = 0.0

    def log_add(self, latency: float, success: bool):
        self.add_count += 1
        self.total_latency += latency
        if not success:
            self.errors += 1

    def log_search(self, latency: float, result_count: int):
        self.search_count += 1
        self.total_latency += latency
        if result_count > 0:
            self.recall_hits += 1
        else:
            self.recall_misses += 1

    def report(self) -> dict:
        return {
            "total_operations": self.add_count + self.search_count,
            "add_count": self.add_count,
            "search_count": self.search_count,
            "recall_hit_rate": self.recall_hits / max(self.search_count, 1),
            "error_rate": self.errors / max(self.add_count, 1),
            "avg_latency_ms": (self.total_latency / max(self.add_count + self.search_count, 1)) * 1000
        }

# Add to MemoryManager
metrics = MemoryMetrics()
```

### 11.2 Logging Strategy

```python
# Enhanced logging in hooks

import logging

logger = logging.getLogger("adw.memory")
logger.setLevel(logging.INFO)

# In pre_scout_recall():
logger.info(f"Memory recall: query='{task_description[:50]}...', confidence={avg_confidence:.2f}, results={len(results)}")

# In post_scout_learn():
logger.info(f"Memory learn: category=file_patterns, files={len(files)}, adw_id={adw_id}")

# On errors:
logger.error(f"Memory operation failed: {e}", exc_info=True)
```

### 11.3 Health Check Endpoint

```python
# For webhook deployments (optional)

def memory_health_check() -> dict:
    """Check memory system health."""
    manager = MemoryManager.get_instance()

    is_available = manager.is_available()

    if is_available:
        # Test operations
        try:
            manager.add(
                messages="Health check test",
                user_id="health_check"
            )
            manager.delete_all(user_id="health_check")
            status = "healthy"
        except Exception as e:
            status = f"degraded: {e}"
    else:
        status = "unavailable"

    return {
        "status": status,
        "available": is_available,
        "metrics": manager.metrics.report()
    }
```

---

## 12. Future Enhancements

### 12.1 Multi-Agent Memory Sharing

**Concept**: Let parallel scout agents share discoveries in real-time.

```python
# During parallel scout execution
def scout_agent_with_shared_memory(agent_id: int, task: str, shared_memory_id: str):
    """Scout agent that contributes to shared memory."""

    # Search for discoveries from other agents
    other_findings = memory.search(
        query=task,
        run_id=shared_memory_id,
        limit=10
    )

    # Run scout with context from other agents
    results = run_scout(task, hints=other_findings)

    # Share findings immediately
    memory.add(
        messages=f"Agent {agent_id} found: {results}",
        run_id=shared_memory_id
    )

    return results
```

### 12.2 Memory Consolidation

**Concept**: Periodically merge similar memories to reduce noise.

```python
def consolidate_memories(project_id: str):
    """Merge duplicate/similar memories."""

    all_memories = memory.get_all(user_id=project_id, limit=1000)

    # Group by semantic similarity (using embeddings)
    clusters = cluster_by_similarity(all_memories["results"], threshold=0.9)

    # For each cluster, merge into single memory
    for cluster in clusters:
        if len(cluster) > 1:
            merged_message = merge_memory_messages(cluster)

            # Keep highest confidence memory, delete others
            keep_id = max(cluster, key=lambda m: m.get("score", 0))["id"]
            for mem in cluster:
                if mem["id"] != keep_id:
                    memory.delete(mem["id"])

            # Update kept memory
            # (mem0 doesn't have update API - would need delete + add)
```

### 12.3 Memory-Driven Analytics

**Concept**: Generate insights dashboard from memories.

```python
def generate_memory_insights(project_id: str) -> dict:
    """Analyze project learnings for insights."""

    all_memories = memory.get_all(user_id=project_id, limit=1000)

    insights = {
        "most_common_files": count_file_references(all_memories),
        "top_libraries": count_library_usage(all_memories),
        "error_patterns": analyze_error_frequency(all_memories),
        "design_patterns": extract_common_decisions(all_memories)
    }

    # Generate markdown report
    report = f"""
    # Project Memory Insights

    ## Most Frequently Modified Files
    {format_table(insights["most_common_files"])}

    ## Common Libraries
    {format_table(insights["top_libraries"])}

    ## Error Patterns
    {format_table(insights["error_patterns"])}

    ## Design Patterns
    {format_list(insights["design_patterns"])}
    """

    return insights, report
```

### 12.4 Memory-Guided Test Generation

**Concept**: Use learned error patterns to generate preventive tests.

```python
def generate_tests_from_errors(project_id: str):
    """Generate test cases from past errors."""

    # Get all error resolutions
    errors = memory.search(
        query="error",
        user_id=project_id,
        filters={"category": "error_resolutions"},
        limit=50
    )

    test_cases = []
    for error_mem in errors.get("results", []):
        # Extract error pattern
        error_type = extract_error_type(error_mem["memory"])
        resolution = extract_resolution(error_mem["memory"])

        # Generate test case
        test_code = f"""
def test_prevent_{error_type.lower()}():
    \"\"\"Regression test for: {error_mem['memory'][:100]}...\"\"\"

    # Test that resolution works
    {generate_test_code(error_type, resolution)}
        """

        test_cases.append(test_code)

    return test_cases
```

---

## 13. Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create `adws/adw_modules/memory_manager.py`
- [ ] Create `adws/adw_modules/memory_hooks.py`
- [ ] Add mem0 to `requirements.txt` (if not present)
- [ ] Test MemoryManager singleton and lazy initialization
- [ ] Test graceful degradation (works without mem0)

### Phase 2: Hook Integration
- [ ] Integrate `pre_scout_recall()` in scout workflow
- [ ] Integrate `post_scout_learn()` in scout workflow
- [ ] Integrate `pre_plan_recall()` in plan workflow
- [ ] Integrate `post_plan_learn()` in plan workflow
- [ ] Integrate `post_build_learn()` in build workflow
- [ ] Integrate `on_error_learn()` in exception handlers

### Phase 3: Testing
- [ ] Unit tests for memory_manager.py
- [ ] Unit tests for memory_hooks.py
- [ ] Integration tests for scout workflow
- [ ] Integration tests for plan workflow
- [ ] Performance tests (latency benchmarks)
- [ ] Security tests (sanitization)

### Phase 4: Documentation
- [ ] Update `CLAUDE.md` with memory usage instructions
- [ ] Add memory metrics to build reports
- [ ] Document memory cleanup procedures
- [ ] Add troubleshooting guide for mem0 issues

### Phase 5: Monitoring
- [ ] Add memory metrics logging
- [ ] Create memory health check function
- [ ] Set up cleanup cron job (optional)
- [ ] Monitor recall hit rates

---

## 14. Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Mem0 initialization failure** | Medium | Low | Graceful degradation, works without memory |
| **Slow memory operations** | Low | Medium | Async operations, timeout limits (<500ms) |
| **Memory storage bloat** | Low | Low | Retention policy (365 days), consolidation |
| **Sensitive data leakage** | Low | High | Content sanitization, no PII storage |
| **Cross-project contamination** | Very Low | Medium | Strict scoping by project_id |
| **OpenAI API failures** | Low | Low | Retry logic, fallback to no-memory mode |

**Overall Risk**: **Low** - Memory is advisory-only, never blocks critical path.

---

## 15. Success Metrics

### Short-Term (Month 1)
- ✅ Memory system deployed without errors
- ✅ >95% workflow success rate (with memory enabled)
- ✅ <200ms added latency per workflow
- ✅ Zero sensitive data leaks (audit logs clean)

### Medium-Term (Months 2-3)
- ✅ >70% recall relevance (human-evaluated)
- ✅ >50% recall hit rate (memories found for similar tasks)
- ✅ Measurable reduction in redundant file searches
- ✅ Positive developer feedback on suggestions

### Long-Term (6+ Months)
- ✅ >1000 memories accumulated (rich knowledge base)
- ✅ >80% recall relevance (high-quality suggestions)
- ✅ Demonstrable time savings (faster task completion)
- ✅ Memory-driven insights guide architecture decisions

---

## Appendix A: API Reference

### MemoryManager Methods

```python
class MemoryManager:
    @classmethod
    def get_instance() -> MemoryManager

    def is_available() -> bool
    def add(messages: str, **kwargs) -> Optional[Dict[str, Any]]
    def search(query: str, **kwargs) -> Optional[Dict[str, Any]]
    def get_all(**kwargs) -> Optional[Dict[str, Any]]
    def delete(memory_id: str) -> bool
    def summarize_project(project_id: str) -> str
```

### Hook Functions

```python
# Pre-execution recalls
def pre_scout_recall(task_description: str, project_id: str, ...) -> dict
def pre_plan_recall(task_description: str, project_id: str, issue_type: str, ...) -> dict

# Post-execution learning
def post_scout_learn(task_description: str, scout_results: dict, project_id: str, adw_id: str) -> None
def post_plan_learn(plan_file: str, project_id: str, adw_id: str, issue_type: str) -> None
def post_build_learn(build_report_file: str, project_id: str, adw_id: str) -> None

# Error learning
def on_error_learn(error: Exception, context: dict, resolution: Optional[str], ...) -> None

# Utilities
def sanitize_memory_content(content: str) -> str
def get_project_id() -> str
```

### Memory Metadata Schema

```python
{
    "category": "file_patterns" | "design_decisions" | "implementation_patterns" | "error_resolutions" | "session_context",
    "workflow": "adw_scout" | "adw_plan" | "adw_build" | "adw_test" | "adw_review",
    "adw_id": str,
    "issue_number": int,
    "issue_type": "feature" | "bug" | "chore",
    "file": str,
    "files": list[str],
    "directory": str,
    "timestamp": str,  # ISO 8601
    "confidence": float,  # 0.0-1.0
    "tags": list[str],
    "agent_name": str,
    "source": str
}
```

---

## Appendix B: Configuration Reference

### Environment Variables

```bash
# Enable/disable memory system
export ADW_MEMORY_ENABLED=true  # Default: true

# Custom Qdrant storage path
export ADW_MEMORY_QDRANT_PATH=/path/to/qdrant  # Default: /tmp/qdrant

# OpenAI API key (required for embeddings)
export OPENAI_API_KEY=sk-...

# Memory retention period (days)
export ADW_MEMORY_RETENTION_DAYS=365  # Default: 365

# Confidence threshold for recalls
export ADW_MEMORY_CONFIDENCE_THRESHOLD=0.7  # Default: 0.7
```

### Project-Specific Config (Optional)

```yaml
# .adw/memory_config.yaml
vector_store:
  provider: qdrant
  config:
    path: /custom/path/qdrant
    collection_name: project_custom

llm:
  provider: openai
  config:
    model: gpt-4  # For memory consolidation (optional)

embedder:
  provider: openai
  config:
    model: text-embedding-ada-002

retention_days: 365
confidence_threshold: 0.75
```

---

## Appendix C: Troubleshooting

### Problem: Memory operations failing silently

**Symptoms**: Logs show "Memory recall failed" warnings.

**Solution**:
1. Check `~/.mem0/history.db` exists and is writable
2. Check `/tmp/qdrant/` exists and is writable
3. Verify `OPENAI_API_KEY` is set
4. Test manually:
   ```python
   from mem0 import Memory
   m = Memory()
   m.add("test", user_id="test")
   ```

### Problem: Slow memory operations (>500ms)

**Symptoms**: Added latency >500ms per workflow.

**Solution**:
1. Check Qdrant collection size: `ls -lh /tmp/qdrant/`
2. Run memory consolidation to reduce duplicates
3. Consider Qdrant Cloud for large datasets (>100K memories)
4. Reduce `limit` parameter in searches

### Problem: Memory recalls not relevant

**Symptoms**: Recall confidence <0.5, suggestions don't match task.

**Solution**:
1. Increase training data (run more tasks to build memory)
2. Tune metadata categorization (ensure correct `category` tags)
3. Adjust confidence threshold (increase to 0.8 for stricter filtering)
4. Review and delete low-quality memories manually

### Problem: Sensitive data in memories

**Symptoms**: API keys/passwords found in memory storage.

**Solution**:
1. Run sanitization audit:
   ```python
   all_memories = memory.get_all(user_id="project_x")
   for m in all_memories["results"]:
       if "api_key" in m["memory"] or "password" in m["memory"]:
           print(f"Sensitive data in: {m['id']}")
   ```
2. Delete offending memories
3. Enhance `sanitize_memory_content()` with more patterns
4. Add pre-commit hook to scan for secrets

---

## Conclusion

This architecture provides a **non-invasive, high-value** integration of mem0 into the ADW system. Key properties:

1. **Zero Breaking Changes**: Existing workflows continue unchanged
2. **Graceful Degradation**: Works perfectly without mem0
3. **Performance**: <1 second added latency (0.3% overhead)
4. **Cost-Effective**: ~$0.09/year in embedding costs
5. **Privacy-Safe**: No sensitive data stored
6. **Scalable**: Handles 1M+ memories with local Qdrant

**Next Steps**: Implement Phase 1 (core infrastructure) and validate with integration tests.

---

**Document Prepared**: 2025-10-20
**Author**: System Architect Agent
**Review Status**: Ready for Implementation
**Estimated Implementation**: 2-3 days (20-30 hours)
