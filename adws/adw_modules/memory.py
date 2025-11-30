"""Persistent Learnings Layer using mem0.

This module provides agent memory capabilities for the Scout-Plan-Build framework.
It stores and retrieves learnings, patterns, and decisions across sessions.

Key Insight: Gemini = code discovery ("where is auth?"),
             mem0 = agent memory ("what did we learn about auth in this project?")
Together they create self-improving agents.

Supports TWO modes:
1. **Cloud Mode** (recommended for getting started):
   - Just set MEM0_API_KEY
   - No local infrastructure needed
   - Get key from: https://app.mem0.ai/

2. **Self-Hosted Mode** (for privacy/control):
   - Requires: OPENAI_API_KEY (embeddings) + local Qdrant
   - pip install mem0ai openai qdrant-client

Environment:
    - MEM0_API_KEY: For cloud mode (preferred)
    - OPENAI_API_KEY: For self-hosted embeddings
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

# Lazy import to avoid hard dependency when not using memory features
_mem0_mode: Optional[str] = None  # "cloud", "self-hosted", or None


def _check_mem0_available() -> str:
    """Check mem0 availability and determine mode.

    Returns:
        "cloud" - MEM0_API_KEY set, use MemoryClient
        "self-hosted" - OPENAI_API_KEY set, use local Memory
        "" - Not configured
    """
    global _mem0_mode

    if _mem0_mode is not None:
        return _mem0_mode

    # Check for cloud mode first (simpler)
    if os.getenv("MEM0_API_KEY"):
        try:
            from mem0 import MemoryClient  # noqa: F401
            _mem0_mode = "cloud"
            logging.debug("mem0 cloud mode available")
            return _mem0_mode
        except ImportError:
            logging.debug("mem0 package not installed")

    # Check for self-hosted mode
    if os.getenv("OPENAI_API_KEY"):
        try:
            from mem0 import Memory  # noqa: F401
            _mem0_mode = "self-hosted"
            logging.debug("mem0 self-hosted mode available")
            return _mem0_mode
        except ImportError:
            logging.debug("mem0 package not installed")

    _mem0_mode = ""
    return _mem0_mode


# Confidence thresholds for different memory types
CONFIDENCE_LEVELS = {
    "decision": 0.85,      # Strong architectural choices
    "pattern": 0.80,       # Code patterns that work
    "discovery": 0.75,     # File discovery results
    "failure": 0.85,       # Error + solution pairs
    "hypothesis": 0.40,    # Unverified ideas
}


class PersistentLearningsLayer:
    """Wraps mem0 for persistent agent memory in Scout-Plan-Build framework.

    Memory Types (HIGH VALUE):
    - Decisions: "Use typer over argparse for CLI"
    - Patterns: "This project uses dataclasses, not Pydantic"
    - Discoveries: "Auth logic in middleware/auth.py"
    - Failures: "Error X → Solution Y"

    Memory Types (LOW VALUE - don't store):
    - Generic knowledge (LLM already knows)
    - Transient chat ("Hi", "Thanks")
    - Speculation as fact
    - Full code snippets (Gemini handles code)
    """

    def __init__(self, project_name: str, storage_path: Optional[str] = None):
        """Initialize the memory layer.

        Args:
            project_name: Unique identifier for this project's memories
            storage_path: Path for local vector store (default: .scout/qdrant)
        """
        self.project = project_name
        self.storage_path = storage_path or ".scout/qdrant"
        # Use MEM0_PROJ_ID if set, otherwise fall back to project_name
        self.mem0_project_id = os.getenv("MEM0_PROJ_ID", project_name)
        self._memory = None
        self._mode = _check_mem0_available()
        self._enabled = bool(self._mode)

        if self._enabled:
            self._init_memory()

    def _init_memory(self) -> None:
        """Initialize mem0 based on available mode (cloud or self-hosted)."""
        try:
            if self._mode == "cloud":
                # Cloud mode - simple, just needs MEM0_API_KEY
                from mem0 import MemoryClient
                api_key = os.getenv("MEM0_API_KEY")
                self._memory = MemoryClient(api_key=api_key)
                logging.info(f"mem0 cloud initialized (project_id: {self.mem0_project_id})")

            elif self._mode == "self-hosted":
                # Self-hosted mode - needs OpenAI + local Qdrant
                from mem0 import Memory

                # Ensure storage directory exists
                os.makedirs(self.storage_path, exist_ok=True)

                config = {
                    "llm": {
                        "provider": "anthropic",
                        "config": {
                            "model": "claude-3-haiku-20240307",
                            "temperature": 0.1,
                        }
                    },
                    "embedder": {
                        "provider": "openai",
                        "config": {
                            "model": "text-embedding-3-small"
                        }
                    },
                    "vector_store": {
                        "provider": "qdrant",
                        "config": {
                            "path": self.storage_path,
                            "collection_name": f"spb_{self.project}"
                        }
                    }
                }

                self._memory = Memory.from_config(config)
                logging.info(f"mem0 self-hosted initialized for project: {self.project}")

        except Exception as e:
            logging.warning(f"Failed to initialize mem0: {e}")
            self._enabled = False

    @property
    def enabled(self) -> bool:
        """Check if memory features are available."""
        return self._enabled and self._memory is not None

    # =========================================================================
    # SCOUT PHASE Methods
    # =========================================================================

    def get_scout_hints(self, task: str) -> str:
        """Get hints from past similar tasks for the Scout phase.

        Args:
            task: The current task description

        Returns:
            Formatted string of relevant hints, or empty string if none found
        """
        if not self.enabled:
            return ""

        try:
            results = self._memory.search(
                f"Scout patterns for: {task}",
                user_id=self.project,
                project_id=self.mem0_project_id,
                limit=5
            )
            return self._format_hints(results)
        except Exception as e:
            logging.debug(f"Memory search failed: {e}")
            return ""

    def record_discovery(
        self,
        task: str,
        files: list,
        source: str = "hybrid_search"
    ) -> None:
        """Record a file discovery for future reference.

        Args:
            task: The task that led to this discovery
            files: List of file paths discovered
            source: Where the discovery came from (e.g., "gemini", "ripgrep")
        """
        if not self.enabled:
            return

        try:
            content = f"For task '{task}', key files discovered: {', '.join(files[:10])}"

            self._memory.add(
                messages=[{"role": "system", "content": content}],
                user_id=self.project,
                project_id=self.mem0_project_id,
                metadata={
                    "type": "discovery_pattern",
                    "phase": "scout",
                    "source": source,
                    "confidence": CONFIDENCE_LEVELS["discovery"],
                    "file_count": len(files),
                    "created_at": datetime.now().isoformat(),
                }
            )
            logging.debug(f"Recorded discovery: {len(files)} files for '{task[:50]}...'")
        except Exception as e:
            logging.debug(f"Failed to record discovery: {e}")

    # =========================================================================
    # PLAN PHASE Methods
    # =========================================================================

    def get_planning_lessons(self, task_type: str) -> str:
        """Get lessons from past planning decisions.

        Args:
            task_type: Type of planning task (e.g., "feature", "bugfix", "refactor")

        Returns:
            Formatted string of relevant planning lessons
        """
        if not self.enabled:
            return ""

        try:
            results = self._memory.search(
                f"Planning lessons for {task_type} tasks",
                user_id=self.project,
                project_id=self.mem0_project_id,
                limit=5
            )
            return self._format_hints(results)
        except Exception as e:
            logging.debug(f"Memory search failed: {e}")
            return ""

    def record_decision(
        self,
        task: str,
        decision: str,
        rationale: str
    ) -> None:
        """Record an architectural or design decision.

        Args:
            task: The task context for this decision
            decision: What was decided
            rationale: Why this decision was made
        """
        if not self.enabled:
            return

        try:
            content = f"Decision for '{task}': {decision}. Rationale: {rationale}"

            self._memory.add(
                messages=[{"role": "system", "content": content}],
                user_id=self.project,
                project_id=self.mem0_project_id,
                metadata={
                    "type": "decision",
                    "phase": "plan",
                    "confidence": CONFIDENCE_LEVELS["decision"],
                    "created_at": datetime.now().isoformat(),
                    "immutable": True,  # Decisions don't expire
                }
            )
            logging.debug(f"Recorded decision: {decision[:50]}...")
        except Exception as e:
            logging.debug(f"Failed to record decision: {e}")

    # =========================================================================
    # BUILD PHASE Methods
    # =========================================================================

    def get_build_patterns(self, framework: Optional[str] = None) -> str:
        """Get implementation patterns for the Build phase.

        Args:
            framework: Optional framework filter (e.g., "react", "fastapi")

        Returns:
            Formatted string of relevant patterns
        """
        if not self.enabled:
            return ""

        try:
            query = "Implementation patterns"
            if framework:
                query += f" for {framework}"

            results = self._memory.search(
                query,
                user_id=self.project,
                project_id=self.mem0_project_id,
                limit=5
            )
            return self._format_hints(results)
        except Exception as e:
            logging.debug(f"Memory search failed: {e}")
            return ""

    def record_pattern(self, framework: str, pattern: str) -> None:
        """Record a successful implementation pattern.

        Args:
            framework: The framework/library this pattern applies to
            pattern: Description of the pattern
        """
        if not self.enabled:
            return

        try:
            content = f"Pattern for {framework}: {pattern}"

            self._memory.add(
                messages=[{"role": "system", "content": content}],
                user_id=self.project,
                project_id=self.mem0_project_id,
                metadata={
                    "type": "pattern",
                    "phase": "build",
                    "framework": framework,
                    "confidence": CONFIDENCE_LEVELS["pattern"],
                    "created_at": datetime.now().isoformat(),
                    "immutable": True,  # Patterns don't expire
                }
            )
            logging.debug(f"Recorded pattern for {framework}: {pattern[:50]}...")
        except Exception as e:
            logging.debug(f"Failed to record pattern: {e}")

    def record_failure(self, error: str, solution: str) -> None:
        """Record an error and its solution for future reference.

        High priority - these are very valuable learnings.

        Args:
            error: The error that occurred
            solution: How it was resolved
        """
        if not self.enabled:
            return

        try:
            content = f"Error: {error}\nSolution: {solution}"

            self._memory.add(
                messages=[{"role": "system", "content": content}],
                user_id=self.project,
                project_id=self.mem0_project_id,
                metadata={
                    "type": "failure_recovery",
                    "priority": "high",
                    "confidence": CONFIDENCE_LEVELS["failure"],
                    "created_at": datetime.now().isoformat(),
                    "immutable": True,  # Failure learnings don't expire
                }
            )
            logging.debug(f"Recorded failure: {error[:50]}... → {solution[:50]}...")
        except Exception as e:
            logging.debug(f"Failed to record failure: {e}")

    # =========================================================================
    # GENERAL Methods
    # =========================================================================

    def search(self, query: str, limit: int = 5) -> str:
        """General-purpose memory search.

        Args:
            query: What to search for
            limit: Maximum number of results

        Returns:
            Formatted string of relevant memories
        """
        if not self.enabled:
            return ""

        try:
            results = self._memory.search(
                query,
                user_id=self.project,
                project_id=self.mem0_project_id,
                limit=limit
            )
            return self._format_hints(results)
        except Exception as e:
            logging.debug(f"Memory search failed: {e}")
            return ""

    def record_hypothesis(self, hypothesis: str, context: str) -> None:
        """Record an unverified hypothesis for later validation.

        Lower confidence - will decay faster.

        Args:
            hypothesis: The unverified idea
            context: What led to this hypothesis
        """
        if not self.enabled:
            return

        try:
            content = f"Hypothesis: {hypothesis}. Context: {context}"

            # Session memories expire after 1 day
            expiration = datetime.now() + timedelta(days=1)

            self._memory.add(
                messages=[{"role": "system", "content": content}],
                user_id=self.project,
                project_id=self.mem0_project_id,
                metadata={
                    "type": "hypothesis",
                    "confidence": CONFIDENCE_LEVELS["hypothesis"],
                    "created_at": datetime.now().isoformat(),
                    "expiration_date": expiration.isoformat(),
                }
            )
            logging.debug(f"Recorded hypothesis: {hypothesis[:50]}...")
        except Exception as e:
            logging.debug(f"Failed to record hypothesis: {e}")

    def boost_confidence(self, memory_id: str, reason: str) -> None:
        """Boost confidence of a memory after validation.

        Call this when:
        - Tests pass: +0.10
        - User confirms: +0.05

        Args:
            memory_id: ID of the memory to boost
            reason: Why confidence is being boosted (e.g., "validated_by_tests")
        """
        if not self.enabled:
            return

        # Note: mem0 doesn't have direct confidence update API
        # This would need to be implemented via delete + re-add with new confidence
        # For now, we log the intent
        logging.debug(f"Would boost confidence for {memory_id}: {reason}")

    def _format_hints(self, results: list) -> str:
        """Format memory search results as hints for prompts.

        Args:
            results: List of memory search results from mem0

        Returns:
            Formatted string suitable for prompt injection
        """
        if not results:
            return ""

        hints = []
        for i, result in enumerate(results, 1):
            # mem0 returns results with 'memory' and 'metadata' keys
            if isinstance(result, dict):
                memory = result.get("memory", result.get("text", ""))
                metadata = result.get("metadata", {})
                confidence = metadata.get("confidence", 0.5)
                mem_type = metadata.get("type", "unknown")

                # Only include if confidence is above threshold
                if confidence >= 0.5:
                    hints.append(f"{i}. [{mem_type}] {memory}")
            else:
                # Handle string results
                hints.append(f"{i}. {result}")

        return "\n".join(hints) if hints else ""

    def get_stats(self) -> dict:
        """Get statistics about stored memories.

        Returns:
            Dictionary with memory statistics
        """
        if not self.enabled:
            return {"enabled": False}

        try:
            # Get all memories for this project
            all_memories = self._memory.get_all(
                user_id=self.project,
                project_id=self.mem0_project_id
            )

            stats = {
                "enabled": True,
                "project": self.project,
                "total_memories": len(all_memories) if all_memories else 0,
                "storage_path": self.storage_path,
            }

            # Count by type
            type_counts = {}
            if all_memories:
                for mem in all_memories:
                    if isinstance(mem, dict):
                        mem_type = mem.get("metadata", {}).get("type", "unknown")
                        type_counts[mem_type] = type_counts.get(mem_type, 0) + 1

            stats["by_type"] = type_counts
            return stats

        except Exception as e:
            logging.debug(f"Failed to get stats: {e}")
            return {"enabled": True, "error": str(e)}


# Singleton for easy access
_default_memory: Optional[PersistentLearningsLayer] = None


def get_memory(project_name: str = "default") -> PersistentLearningsLayer:
    """Get or create the default memory layer instance.

    Args:
        project_name: Project identifier (uses repo name by default)

    Returns:
        PersistentLearningsLayer instance
    """
    global _default_memory

    if _default_memory is None or _default_memory.project != project_name:
        _default_memory = PersistentLearningsLayer(project_name)

    return _default_memory
