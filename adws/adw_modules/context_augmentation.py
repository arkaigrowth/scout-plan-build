"""Context Augmentation Layer - Orchestrates Memory + Search.

This module provides the main entry point for context-aware code discovery.
It combines:
- Memory (mem0): Past learnings, patterns, decisions
- Search (Gemini + ripgrep): Current codebase exploration

The flow:
1. Query memory for hints from past similar tasks
2. Augment the search query with memory context
3. Execute hybrid search (semantic + literal)
4. Store new learnings from successful discoveries
5. Format and inject context into agent prompts

Dependencies:
    - memory.py: PersistentLearningsLayer
    - gemini_search.py: HybridSearchClient
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Optional

from .memory import PersistentLearningsLayer, get_memory
from .gemini_search import (
    HybridSearchClient,
    SearchResult,
    Snippet,
    QueryType,
    classify_query,
)


@dataclass
class AugmentedContext:
    """Result of context augmentation for an agent prompt."""
    original_prompt: str
    augmented_prompt: str
    memory_hints: str
    search_results: SearchResult
    context_block: str
    total_snippets: int
    sources_used: list[str] = field(default_factory=list)


class ContextAugmenter:
    """Orchestrates memory + search for context injection into agent prompts.

    This is the main entry point for the context augmentation layer.
    Use this before any Scout/Plan/Build agent invocation to provide
    relevant context automatically.

    Example:
        augmenter = ContextAugmenter("my-project")
        result = augmenter.augment_prompt_with_context(
            task="Add caching to UserService",
            base_prompt="You are a senior developer..."
        )
        # result.augmented_prompt now includes relevant context
    """

    def __init__(
        self,
        project_name: Optional[str] = None,
        memory: Optional[PersistentLearningsLayer] = None,
        search_client: Optional[HybridSearchClient] = None
    ):
        """Initialize the context augmenter.

        Args:
            project_name: Unique project identifier (default: cwd name)
            memory: Optional pre-configured memory layer
            search_client: Optional pre-configured search client
        """
        self.project_name = project_name or os.path.basename(os.getcwd())
        self.memory = memory or get_memory(self.project_name)
        self.search = search_client or HybridSearchClient()

        logging.debug(f"ContextAugmenter initialized for project: {self.project_name}")
        logging.debug(f"Memory enabled: {self.memory.enabled}")
        logging.debug(f"Gemini enabled: {self.search.gemini_enabled}")

    def augment_prompt_with_context(
        self,
        task: str,
        base_prompt: str,
        phase: str = "scout",
        max_snippets: int = 10,
        path_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
    ) -> AugmentedContext:
        """Full context augmentation pipeline.

        Pipeline:
        1. Get hints from past similar tasks (memory)
        2. Augment query with memory context
        3. Execute hybrid search
        4. Store new learnings
        5. Format and inject context

        Args:
            task: The current task description
            base_prompt: The base prompt to augment
            phase: Current phase (scout, plan, build)
            max_snippets: Maximum code snippets to include
            path_filter: Optional path prefix filter
            language_filter: Optional language filter

        Returns:
            AugmentedContext with all augmentation details
        """
        sources_used = []

        # =====================================================================
        # Step 1: Get hints from memory
        # =====================================================================
        memory_hints = ""

        if phase == "scout":
            memory_hints = self.memory.get_scout_hints(task)
        elif phase == "plan":
            memory_hints = self.memory.get_planning_lessons(task)
        elif phase == "build":
            memory_hints = self.memory.get_build_patterns()

        if memory_hints:
            sources_used.append("memory")
            logging.debug(f"Got memory hints: {len(memory_hints)} chars")

        # =====================================================================
        # Step 2: Augment query with memory context
        # =====================================================================
        augmented_query = task
        if memory_hints:
            # Add memory context as hints for the search
            augmented_query = f"{task}\n\nPast patterns that may help: {memory_hints}"

        # =====================================================================
        # Step 3: Execute hybrid search
        # =====================================================================
        search_results = self.search.hybrid_search(
            augmented_query,
            path_filter=path_filter,
            language_filter=language_filter,
            limit=max_snippets
        )

        sources_used.extend(search_results.sources_used)

        # =====================================================================
        # Step 4: Store new learnings
        # =====================================================================
        if search_results.success and search_results.snippets:
            # Record the discovery for future reference
            file_paths = [s.file_path for s in search_results.snippets[:5]]
            self.memory.record_discovery(
                task=task,
                files=file_paths,
                source="hybrid_search"
            )
            logging.debug(f"Recorded discovery: {len(file_paths)} files")

        # =====================================================================
        # Step 5: Format context block
        # =====================================================================
        context_block = self._format_context_block(
            search_results.snippets,
            max_snippets
        )

        # =====================================================================
        # Step 6: Build augmented prompt
        # =====================================================================
        augmented_prompt = self._build_augmented_prompt(
            base_prompt=base_prompt,
            memory_hints=memory_hints,
            context_block=context_block,
            phase=phase
        )

        return AugmentedContext(
            original_prompt=base_prompt,
            augmented_prompt=augmented_prompt,
            memory_hints=memory_hints,
            search_results=search_results,
            context_block=context_block,
            total_snippets=len(search_results.snippets),
            sources_used=sources_used,
        )

    def quick_context(
        self,
        task: str,
        max_snippets: int = 5
    ) -> str:
        """Get quick context for a task without full prompt augmentation.

        Useful for adding context to an existing prompt or for exploration.

        Args:
            task: The task description
            max_snippets: Maximum snippets to return

        Returns:
            Formatted context string
        """
        # Get memory hints
        hints = self.memory.get_scout_hints(task)

        # Execute search
        results = self.search.hybrid_search(task, limit=max_snippets)

        # Format
        parts = []

        if hints:
            parts.append("## Past Patterns\n" + hints)

        if results.snippets:
            parts.append("## Relevant Files\n" + self._format_file_list(results.snippets))

        return "\n\n".join(parts) if parts else "No relevant context found."

    def record_success(
        self,
        task: str,
        pattern: Optional[str] = None,
        decision: Optional[str] = None,
        rationale: Optional[str] = None
    ) -> None:
        """Record a successful pattern or decision for future reference.

        Call this after a successful task completion.

        Args:
            task: The task that was completed
            pattern: Optional pattern that worked
            decision: Optional decision that was made
            rationale: Optional rationale for the decision
        """
        if pattern:
            # Infer framework from task
            framework = self._infer_framework(task)
            self.memory.record_pattern(framework, pattern)

        if decision and rationale:
            self.memory.record_decision(task, decision, rationale)

    def record_failure(self, error: str, solution: str) -> None:
        """Record a failure and its solution for future reference.

        Call this after recovering from an error.

        Args:
            error: The error that occurred
            solution: How it was fixed
        """
        self.memory.record_failure(error, solution)

    def _format_context_block(
        self,
        snippets: list[Snippet],
        max_snippets: int
    ) -> str:
        """Format snippets into a context block for prompts.

        Args:
            snippets: List of code snippets
            max_snippets: Maximum to include

        Returns:
            Formatted markdown context block
        """
        if not snippets:
            return "No relevant code snippets found."

        parts = []
        for i, snippet in enumerate(snippets[:max_snippets], 1):
            # Format each snippet
            source_tag = f"[{snippet.source}]" if snippet.source != "unknown" else ""
            line_info = f":{snippet.line_start}" if snippet.line_start else ""

            header = f"### {i}. `{snippet.file_path}{line_info}` {source_tag}"

            # Truncate content if too long
            content = snippet.content
            if len(content) > 500:
                content = content[:500] + "\n... (truncated)"

            parts.append(f"{header}\n\n```\n{content}\n```")

        return "\n\n".join(parts)

    def _format_file_list(self, snippets: list[Snippet]) -> str:
        """Format snippets as a simple file list.

        Args:
            snippets: List of snippets

        Returns:
            Markdown bullet list of files
        """
        if not snippets:
            return "No files found."

        lines = []
        for snippet in snippets:
            source = f" ({snippet.source})" if snippet.source != "unknown" else ""
            line = f"- `{snippet.file_path}`{source}"
            if snippet.line_start:
                line += f" line {snippet.line_start}"
            lines.append(line)

        return "\n".join(lines)

    def _build_augmented_prompt(
        self,
        base_prompt: str,
        memory_hints: str,
        context_block: str,
        phase: str
    ) -> str:
        """Build the final augmented prompt.

        Args:
            base_prompt: The original prompt
            memory_hints: Hints from memory
            context_block: Formatted code context
            phase: Current phase

        Returns:
            Complete augmented prompt
        """
        # Phase-specific headers
        phase_headers = {
            "scout": "DISCOVERED CONTEXT",
            "plan": "PLANNING CONTEXT",
            "build": "IMPLEMENTATION CONTEXT",
        }
        header = phase_headers.get(phase, "CONTEXT")

        sections = [base_prompt]

        # Add memory section if we have hints
        if memory_hints:
            sections.append(f"""
## LEARNED PATTERNS (from past similar tasks)

{memory_hints}
""")

        # Add code context section
        sections.append(f"""
## {header} (from codebase search)

The following code snippets may be relevant to this task:

{context_block}

---
""")

        return "\n".join(sections)

    def _infer_framework(self, task: str) -> str:
        """Infer the framework from task description.

        Args:
            task: Task description

        Returns:
            Framework name or "general"
        """
        task_lower = task.lower()

        frameworks = {
            "react": ["react", "jsx", "component", "hook", "useState"],
            "fastapi": ["fastapi", "endpoint", "router", "pydantic"],
            "django": ["django", "model", "view", "template"],
            "flask": ["flask", "route", "blueprint"],
            "express": ["express", "middleware", "req", "res"],
            "python": ["python", "def ", "class ", ".py"],
            "typescript": ["typescript", ".ts", "interface"],
        }

        for framework, keywords in frameworks.items():
            if any(kw in task_lower for kw in keywords):
                return framework

        return "general"

    def get_stats(self) -> dict:
        """Get statistics about the augmentation layer.

        Returns:
            Dictionary with stats from memory and search
        """
        return {
            "project": self.project_name,
            "memory": self.memory.get_stats(),
            "search": {
                "gemini_enabled": self.search.gemini_enabled,
            }
        }


# =========================================================================
# Convenience Functions
# =========================================================================

_default_augmenter: Optional[ContextAugmenter] = None


def get_augmenter(project_name: Optional[str] = None) -> ContextAugmenter:
    """Get or create the default context augmenter.

    Args:
        project_name: Optional project identifier

    Returns:
        ContextAugmenter instance
    """
    global _default_augmenter

    if _default_augmenter is None:
        _default_augmenter = ContextAugmenter(project_name)

    return _default_augmenter


def augment_for_scout(task: str, base_prompt: str) -> str:
    """Quick augmentation for Scout phase.

    Args:
        task: The task description
        base_prompt: The base prompt

    Returns:
        Augmented prompt with context
    """
    augmenter = get_augmenter()
    result = augmenter.augment_prompt_with_context(task, base_prompt, phase="scout")
    return result.augmented_prompt


def augment_for_plan(task: str, base_prompt: str) -> str:
    """Quick augmentation for Plan phase.

    Args:
        task: The task description
        base_prompt: The base prompt

    Returns:
        Augmented prompt with context
    """
    augmenter = get_augmenter()
    result = augmenter.augment_prompt_with_context(task, base_prompt, phase="plan")
    return result.augmented_prompt


def augment_for_build(task: str, base_prompt: str) -> str:
    """Quick augmentation for Build phase.

    Args:
        task: The task description
        base_prompt: The base prompt

    Returns:
        Augmented prompt with context
    """
    augmenter = get_augmenter()
    result = augmenter.augment_prompt_with_context(task, base_prompt, phase="build")
    return result.augmented_prompt
