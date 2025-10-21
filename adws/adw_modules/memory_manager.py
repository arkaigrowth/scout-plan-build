"""Memory manager for ADW system using mem0.

Provides a singleton wrapper around mem0.Memory with ADW-specific
helpers and graceful degradation when mem0 is unavailable.

Architecture:
    - Singleton pattern (lazy initialization)
    - Graceful degradation (works without mem0)
    - Error handling (never crashes workflow)
    - Project scoping (isolated per repository)

Usage:
    from adw_modules.memory_manager import MemoryManager

    memory = MemoryManager.get_instance()

    if memory.is_available():
        memory.add(messages="...", user_id="project_x")
        results = memory.search(query="...", user_id="project_x")
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryManager:
    """Singleton wrapper for mem0.Memory with ADW-specific helpers.

    Provides lazy initialization and graceful degradation when mem0
    is unavailable or configuration fails.
    """

    _instance: Optional["MemoryManager"] = None
    _memory: Optional[Any] = None  # mem0.Memory instance
    _initialized: bool = False

    def __init__(self):
        """Private constructor - use get_instance() instead.

        Raises:
            RuntimeError: If called directly (use get_instance())
        """
        if MemoryManager._instance is not None:
            raise RuntimeError("Use MemoryManager.get_instance() instead")

        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self.metrics = MemoryMetrics()

    @classmethod
    def get_instance(cls) -> "MemoryManager":
        """Get or create singleton instance (lazy initialization).

        Returns:
            MemoryManager singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_initialized(self):
        """Initialize mem0 on first use (lazy pattern).

        Attempts to initialize mem0.Memory with optional custom config.
        If initialization fails, logs error and sets _memory to None
        (graceful degradation).
        """
        if self._initialized:
            return

        try:
            # Check if memory system is enabled
            enabled = os.getenv("ADW_MEMORY_ENABLED", "true").lower() == "true"
            if not enabled:
                self.logger.info("Memory system disabled via ADW_MEMORY_ENABLED")
                self._memory = None
                self._initialized = True
                return

            # Import mem0 (may fail if not installed)
            try:
                from mem0 import Memory
            except ImportError:
                self.logger.warning(
                    "mem0 not installed. Install with: pip install mem0ai"
                )
                self._memory = None
                self._initialized = True
                return

            # Get custom config if specified
            config = self._get_memory_config()

            # Initialize mem0
            if config:
                self._memory = Memory(config=config)
                self.logger.info("Mem0 initialized with custom config")
            else:
                self._memory = Memory()
                self.logger.info("Mem0 initialized with default config")

            self._initialized = True

        except Exception as e:
            self.logger.error(f"Failed to initialize mem0: {e}", exc_info=True)
            self._memory = None
            self._initialized = True  # Mark as initialized (but failed)

    def _get_memory_config(self) -> Optional[Any]:
        """Get custom mem0 config from environment or config file.

        Returns:
            MemoryConfig instance or None for defaults
        """
        try:
            from mem0.configs.base import MemoryConfig

            # Check for custom Qdrant path
            qdrant_path = os.getenv("ADW_MEMORY_QDRANT_PATH")
            if qdrant_path:
                self.logger.info(f"Using custom Qdrant path: {qdrant_path}")
                return MemoryConfig(
                    vector_store={
                        "provider": "qdrant",
                        "config": {
                            "path": qdrant_path,
                            "collection_name": "adw_memories"
                        }
                    }
                )

            # Could add more config sources here (yaml file, etc.)
            return None  # Use defaults

        except Exception as e:
            self.logger.error(f"Failed to load custom config: {e}")
            return None

    def is_available(self) -> bool:
        """Check if mem0 is available and working.

        Returns:
            True if mem0 is initialized and ready, False otherwise
        """
        self._ensure_initialized()
        return self._memory is not None

    def add(
        self,
        messages: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Add memory (wrapper with error handling and metrics).

        Args:
            messages: Content to store
            user_id: User/project scope
            agent_id: Agent/workflow scope
            run_id: Run/session scope
            metadata: Additional metadata
            **kwargs: Additional arguments passed to mem0.add()

        Returns:
            Memory add result or None on failure

        Note:
            Never raises exceptions - returns None on error
        """
        if not self.is_available():
            self.logger.debug("Mem0 not available, skipping add")
            self.metrics.log_add(0, False)
            return None

        try:
            start_time = datetime.utcnow()

            result = self._memory.add(
                messages=messages,
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                metadata=metadata,
                **kwargs
            )

            latency = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.log_add(latency, True)

            return result

        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}", exc_info=True)
            self.metrics.log_add(0, False)
            return None

    def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        threshold: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Search memories (wrapper with error handling and metrics).

        Args:
            query: Search query
            user_id: User/project scope
            agent_id: Agent/workflow scope
            run_id: Run/session scope
            limit: Max results
            filters: Additional filters
            threshold: Minimum relevance score
            **kwargs: Additional arguments passed to mem0.search()

        Returns:
            Search results (empty dict if unavailable or error)

        Note:
            Never raises exceptions - returns empty results on error
        """
        if not self.is_available():
            self.logger.debug("Mem0 not available, skipping search")
            return {"results": []}

        try:
            start_time = datetime.utcnow()

            results = self._memory.search(
                query=query,
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                limit=limit,
                filters=filters,
                threshold=threshold,
                **kwargs
            )

            latency = (datetime.utcnow() - start_time).total_seconds()
            result_count = len(results.get("results", []))
            self.metrics.log_search(latency, result_count)

            return results

        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}", exc_info=True)
            self.metrics.log_search(0, 0)
            return {"results": []}

    def get_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """Get all memories (wrapper with error handling).

        Args:
            user_id: User/project scope
            agent_id: Agent/workflow scope
            run_id: Run/session scope
            filters: Additional filters
            limit: Max results
            **kwargs: Additional arguments passed to mem0.get_all()

        Returns:
            All memories (empty dict if unavailable or error)
        """
        if not self.is_available():
            return {"results": []}

        try:
            results = self._memory.get_all(
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                filters=filters,
                limit=limit,
                **kwargs
            )
            return results

        except Exception as e:
            self.logger.error(f"Failed to get memories: {e}", exc_info=True)
            return {"results": []}

    def delete(self, memory_id: str) -> bool:
        """Delete specific memory.

        Args:
            memory_id: ID of memory to delete

        Returns:
            True on success, False on failure
        """
        if not self.is_available():
            return False

        try:
            self._memory.delete(memory_id=memory_id)
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}", exc_info=True)
            return False

    def delete_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> bool:
        """Delete all memories matching scope.

        Args:
            user_id: User/project scope
            agent_id: Agent/workflow scope
            run_id: Run/session scope

        Returns:
            True on success, False on failure
        """
        if not self.is_available():
            return False

        try:
            self._memory.delete_all(
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete memories: {e}", exc_info=True)
            return False

    def summarize_project(
        self,
        project_id: str,
        limit: int = 100
    ) -> str:
        """Generate summary of project learnings.

        Args:
            project_id: Project scope
            limit: Max memories to analyze

        Returns:
            Formatted summary string
        """
        if not self.is_available():
            return "Memory system unavailable"

        try:
            # Get all memories for project
            all_memories = self.get_all(user_id=project_id, limit=limit)

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
                cat_name = cat.replace("_", " ").title()
                summary += f"**{cat_name}**: {len(memories)} memories\n"
                if memories:
                    summary += f"  - {memories[0][:100]}...\n"
                summary += "\n"

            return summary

        except Exception as e:
            self.logger.error(f"Failed to summarize project: {e}", exc_info=True)
            return f"Error generating summary: {str(e)}"

    def get_metrics(self) -> Dict[str, Any]:
        """Get memory operation metrics.

        Returns:
            Dictionary of metrics
        """
        return self.metrics.report()


class MemoryMetrics:
    """Track memory operation metrics for monitoring."""

    def __init__(self):
        """Initialize metrics counters."""
        self.add_count = 0
        self.search_count = 0
        self.recall_hits = 0  # Searches with results
        self.recall_misses = 0  # Searches with no results
        self.errors = 0
        self.total_latency = 0.0

    def log_add(self, latency: float, success: bool):
        """Log an add operation.

        Args:
            latency: Operation latency in seconds
            success: Whether operation succeeded
        """
        self.add_count += 1
        self.total_latency += latency
        if not success:
            self.errors += 1

    def log_search(self, latency: float, result_count: int):
        """Log a search operation.

        Args:
            latency: Operation latency in seconds
            result_count: Number of results returned
        """
        self.search_count += 1
        self.total_latency += latency
        if result_count > 0:
            self.recall_hits += 1
        else:
            self.recall_misses += 1

    def report(self) -> Dict[str, Any]:
        """Generate metrics report.

        Returns:
            Dictionary of metrics
        """
        total_ops = self.add_count + self.search_count

        return {
            "total_operations": total_ops,
            "add_count": self.add_count,
            "search_count": self.search_count,
            "recall_hit_rate": self.recall_hits / max(self.search_count, 1),
            "error_rate": self.errors / max(self.add_count, 1),
            "avg_latency_ms": (self.total_latency / max(total_ops, 1)) * 1000
        }

    def reset(self):
        """Reset all metrics to zero."""
        self.__init__()


# ============================================================================
# Health Check Function
# ============================================================================

def memory_health_check() -> Dict[str, Any]:
    """Check memory system health.

    Returns:
        Health check result dictionary
    """
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
        "metrics": manager.get_metrics()
    }
