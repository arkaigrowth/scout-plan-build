"""Hybrid Search Module - Gemini File Search + ripgrep.

This module provides intelligent query routing between semantic search (Gemini)
and literal search (ripgrep), with result merging and ranking.

Query Tier System:
- Tier 1 (Massive Value): Conceptual queries → Gemini only
  "How does billing work?", "Find similar patterns to auth"
- Tier 2 (Good Value): Navigational queries → Hybrid (both)
  "Where is JWT validation?", "Find API endpoints"
- Tier 3 (Marginal Value): Literal queries → ripgrep only
  "Find function X", "Find string 'API_KEY'"

Dependencies:
    - google-genai>=1.48.0 (Python 3.10+ required)
    - ripgrep (system install)

Environment:
    - GEMINI_API_KEY: Required for Gemini File Search
"""

import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

# Lazy imports for optional dependencies
_gemini_available: Optional[bool] = None


def _check_gemini_available() -> bool:
    """Check if Gemini SDK is available and configured."""
    global _gemini_available

    if _gemini_available is not None:
        return _gemini_available

    try:
        from google import genai  # noqa: F401
        if not os.getenv("GEMINI_API_KEY"):
            logging.warning("GEMINI_API_KEY not set - Gemini search disabled")
            _gemini_available = False
            return False
        _gemini_available = True
        return True
    except ImportError:
        logging.debug("google-genai not installed - Gemini search disabled")
        _gemini_available = False
        return False


class QueryType(Enum):
    """Classification of query types for routing."""
    CONCEPTUAL = "conceptual"  # Semantic understanding needed
    LITERAL = "literal"        # Exact text match
    HYBRID = "hybrid"          # Both approaches useful


@dataclass
class Snippet:
    """A code snippet result from search."""
    file_path: str
    content: str
    line_start: int = 0
    line_end: int = 0
    score: float = 1.0
    source: str = "unknown"  # "gemini", "ripgrep", or "merged"
    metadata: dict = field(default_factory=dict)

    def __hash__(self):
        return hash((self.file_path, self.line_start, self.line_end))


@dataclass
class SearchResult:
    """Result of a hybrid search operation."""
    query: str
    query_type: QueryType
    snippets: list[Snippet]
    success: bool = True
    error_message: str = ""
    sources_used: list[str] = field(default_factory=list)
    gemini_response_text: str = ""


# Query classification patterns
CONCEPTUAL_PATTERNS = [
    r'\bhow\s+(does|do|is|are|can|to)\b',  # "how does X work"
    r'\bwhat\s+(is|are|does)\b',            # "what is X"
    r'\bwhy\s+(is|does|do)\b',              # "why is X"
    r'\bwhere\s+is\b',                       # "where is X"
    r'\bexplain\b',
    r'\bunderstand\b',
    r'\bsimilar\s+to\b',
    r'\bpatterns?\b',
    r'\bconventions?\b',
    r'\baffects?\b',
    r'\bworks?\b',                           # "how X works"
    r'\barchitecture\b',
    r'\bdesign\b',
    r'\bimplemented\b',
    r'\brelated\s+to\b',
]

LITERAL_PATTERNS = [
    r'^["\'].*["\']$',             # Entire query is quoted
    r'[\*\?\[\]]',                 # Glob/regex chars
    r'^(grep|rg|find)\s+',         # Explicit CLI commands
    r'\busages?\s+of\s+\w+',       # "usages of X"
    r'^function\s+\w+$',           # Just "function foo"
    r'^class\s+\w+$',              # Just "class Foo"
    r'^def\s+\w+$',                # Just "def foo"
]


def classify_query(query: str) -> QueryType:
    """Classify a query to determine routing strategy.

    Args:
        query: The search query string

    Returns:
        QueryType indicating how to route the query
    """
    query_lower = query.lower().strip()

    # Check for conceptual indicators FIRST (questions, understanding)
    for pattern in CONCEPTUAL_PATTERNS:
        if re.search(pattern, query_lower):
            return QueryType.CONCEPTUAL

    # Check for literal indicators (explicit patterns, quotes)
    for pattern in LITERAL_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            return QueryType.LITERAL

    # Default to hybrid for ambiguous queries
    return QueryType.HYBRID


class HybridSearchClient:
    """Client for hybrid semantic + literal code search."""

    # Default state file location
    DEFAULT_STATE_FILE = "scout_outputs/.gemini_index_state.json"

    def __init__(
        self,
        state_file: Optional[str] = None,
        project_root: Optional[str] = None
    ):
        """Initialize the hybrid search client.

        Args:
            state_file: Path to the Gemini index state file
            project_root: Root directory for ripgrep searches
        """
        self.project_root = project_root or os.getcwd()
        self.state_file = state_file or os.path.join(
            self.project_root, self.DEFAULT_STATE_FILE
        )

        self._gemini_client = None
        self._store_name = None
        self._gemini_enabled = _check_gemini_available()

        if self._gemini_enabled:
            self._init_gemini()

    def _init_gemini(self) -> None:
        """Initialize the Gemini client and load store info."""
        try:
            from google import genai

            api_key = os.getenv("GEMINI_API_KEY")
            self._gemini_client = genai.Client(api_key=api_key)

            # Load store name from state file
            if os.path.exists(self.state_file):
                with open(self.state_file) as f:
                    state = json.load(f)
                    self._store_name = state.get("store_resource_name")
                    logging.debug(f"Loaded Gemini store: {self._store_name}")
            else:
                logging.warning(f"No index state file found at {self.state_file}")

        except Exception as e:
            logging.warning(f"Failed to initialize Gemini: {e}")
            self._gemini_enabled = False

    @property
    def gemini_enabled(self) -> bool:
        """Check if Gemini search is available."""
        return (
            self._gemini_enabled and
            self._gemini_client is not None and
            self._store_name is not None
        )

    def search_gemini(
        self,
        query: str,
        metadata_filter: Optional[str] = None,
        limit: int = 10
    ) -> list[Snippet]:
        """Search using Gemini File Search.

        Args:
            query: The search query
            metadata_filter: Optional AIP-160 filter (e.g., 'language = "python"')
            limit: Maximum number of results

        Returns:
            List of Snippet results
        """
        if not self.gemini_enabled:
            logging.debug("Gemini not available, skipping semantic search")
            return []

        try:
            from google.genai import types

            # Build file search config
            file_search_config = types.FileSearch(
                file_search_store_names=[self._store_name]
            )
            if metadata_filter:
                file_search_config = types.FileSearch(
                    file_search_store_names=[self._store_name],
                    metadata_filter=metadata_filter
                )

            # Execute search
            response = self._gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(file_search=file_search_config)]
                )
            )

            snippets = []

            # Parse grounding metadata for source files
            if (response.candidates and
                hasattr(response.candidates[0], 'grounding_metadata') and
                response.candidates[0].grounding_metadata):

                grounding = response.candidates[0].grounding_metadata

                if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                    for i, chunk in enumerate(grounding.grounding_chunks[:limit]):
                        if hasattr(chunk, 'retrieved_context'):
                            ctx = chunk.retrieved_context
                            title = getattr(ctx, 'title', 'Unknown')
                            uri = getattr(ctx, 'uri', '')
                            text = getattr(ctx, 'text', '')

                            snippets.append(Snippet(
                                file_path=title,
                                content=text[:500] if text else "",
                                score=1.0 - (i * 0.1),  # Decay by position
                                source="gemini",
                                metadata={"uri": uri}
                            ))

            # Also extract any file mentions from the response text
            if response.text:
                # Simple heuristic: look for file paths in response
                file_pattern = r'[`"]?([a-zA-Z_][a-zA-Z0-9_/.-]+\.(py|js|ts|md|yaml|json))[`"]?'
                matches = re.findall(file_pattern, response.text)
                for match in matches[:limit - len(snippets)]:
                    file_path = match[0]
                    if not any(s.file_path == file_path for s in snippets):
                        snippets.append(Snippet(
                            file_path=file_path,
                            content="(mentioned in response)",
                            score=0.5,
                            source="gemini",
                        ))

            logging.debug(f"Gemini search returned {len(snippets)} results")
            return snippets

        except Exception as e:
            logging.warning(f"Gemini search failed: {e}")
            return []

    def search_ripgrep(
        self,
        query: str,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 10
    ) -> list[Snippet]:
        """Search using ripgrep for literal matches.

        Args:
            query: The search pattern (can be regex)
            path: Optional subdirectory to search in
            file_type: Optional file type filter (e.g., "py", "js")
            limit: Maximum number of results

        Returns:
            List of Snippet results
        """
        try:
            # Build ripgrep command
            cmd = ["rg", "--json", "-m", str(limit)]

            # Add file type filter
            if file_type:
                cmd.extend(["-t", file_type])

            # Add case insensitivity for convenience
            cmd.append("-i")

            # Add the pattern
            cmd.append(query)

            # Add path
            search_path = path or self.project_root
            cmd.append(search_path)

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            snippets = []

            # Parse JSON output
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data.get("data", {})
                        path_data = match_data.get("path", {})
                        lines_data = match_data.get("lines", {})
                        submatches = match_data.get("submatches", [])

                        file_path = path_data.get("text", "")
                        line_num = match_data.get("line_number", 0)
                        text = lines_data.get("text", "").strip()

                        # Make path relative to project root
                        if file_path.startswith(self.project_root):
                            file_path = file_path[len(self.project_root):].lstrip('/')

                        snippets.append(Snippet(
                            file_path=file_path,
                            content=text,
                            line_start=line_num,
                            line_end=line_num,
                            score=1.0 if submatches else 0.8,
                            source="ripgrep",
                            metadata={"submatches": len(submatches)}
                        ))

                        if len(snippets) >= limit:
                            break

                except json.JSONDecodeError:
                    continue

            logging.debug(f"ripgrep search returned {len(snippets)} results")
            return snippets

        except subprocess.TimeoutExpired:
            logging.warning("ripgrep search timed out")
            return []
        except FileNotFoundError:
            logging.warning("ripgrep not installed, skipping literal search")
            return []
        except Exception as e:
            logging.warning(f"ripgrep search failed: {e}")
            return []

    def hybrid_search(
        self,
        query: str,
        path_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
        limit: int = 10
    ) -> SearchResult:
        """Execute hybrid search with intelligent routing.

        Args:
            query: The search query
            path_filter: Optional path prefix filter
            language_filter: Optional language filter (e.g., "python")
            limit: Maximum number of results per source

        Returns:
            SearchResult with merged and ranked snippets
        """
        query_type = classify_query(query)
        all_snippets: list[Snippet] = []
        sources_used: list[str] = []
        gemini_response = ""

        # Build metadata filter for Gemini
        metadata_parts = []
        if path_filter:
            metadata_parts.append(f'path_prefix = "{path_filter}"')
        if language_filter:
            metadata_parts.append(f'language = "{language_filter}"')
        metadata_filter = " AND ".join(metadata_parts) if metadata_parts else None

        # Route based on query type
        if query_type in (QueryType.CONCEPTUAL, QueryType.HYBRID):
            gemini_results = self.search_gemini(
                query,
                metadata_filter=metadata_filter,
                limit=limit
            )
            if gemini_results:
                all_snippets.extend(gemini_results)
                sources_used.append("gemini")

        if query_type in (QueryType.LITERAL, QueryType.HYBRID):
            # Extract literal pattern from query
            literal_pattern = self._extract_literal_pattern(query)

            ripgrep_results = self.search_ripgrep(
                literal_pattern,
                path=path_filter,
                file_type=self._language_to_type(language_filter),
                limit=limit
            )
            if ripgrep_results:
                all_snippets.extend(ripgrep_results)
                sources_used.append("ripgrep")

        # Merge and rank results
        merged = self._merge_and_rank(all_snippets, limit)

        return SearchResult(
            query=query,
            query_type=query_type,
            snippets=merged,
            success=len(merged) > 0 or len(sources_used) > 0,
            sources_used=sources_used,
            gemini_response_text=gemini_response,
        )

    def _extract_literal_pattern(self, query: str) -> str:
        """Extract a literal search pattern from a natural language query.

        Args:
            query: The original query

        Returns:
            A pattern suitable for ripgrep
        """
        # If already quoted, extract the quoted content
        quoted = re.search(r'["\']([^"\']+)["\']', query)
        if quoted:
            return quoted.group(1)

        # Look for common patterns
        patterns = [
            r'function\s+(\w+)',     # "function foo"
            r'class\s+(\w+)',        # "class Foo"
            r'def\s+(\w+)',          # "def foo"
            r'usages?\s+of\s+(\w+)', # "usages of foo"
            r'find\s+(\w+)',         # "find foo"
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)

        # Fall back to using key words from the query
        # Remove common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'where', 'what', 'how',
                      'find', 'search', 'for', 'in', 'of', 'to', 'and', 'or'}
        words = query.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return '|'.join(keywords) if keywords else query

    def _language_to_type(self, language: Optional[str]) -> Optional[str]:
        """Convert language name to ripgrep type.

        Args:
            language: Language name (e.g., "python")

        Returns:
            ripgrep type string (e.g., "py")
        """
        if not language:
            return None

        mapping = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rust",
            "c": "c",
            "cpp": "cpp",
            "markdown": "md",
        }
        return mapping.get(language.lower(), language)

    def _merge_and_rank(
        self,
        snippets: list[Snippet],
        limit: int
    ) -> list[Snippet]:
        """Merge and rank snippets from multiple sources.

        Deduplicates by file path and combines scores.

        Args:
            snippets: All snippets from all sources
            limit: Maximum number of results to return

        Returns:
            Ranked list of unique snippets
        """
        # Group by file path
        by_file: dict[str, list[Snippet]] = {}
        for snippet in snippets:
            if snippet.file_path not in by_file:
                by_file[snippet.file_path] = []
            by_file[snippet.file_path].append(snippet)

        # Merge scores - files found by both sources rank higher
        merged: list[Snippet] = []
        for file_path, file_snippets in by_file.items():
            sources = set(s.source for s in file_snippets)

            # Boost score if found by multiple sources
            base_score = max(s.score for s in file_snippets)
            if len(sources) > 1:
                base_score += 0.3  # Boost for appearing in both

            # Combine content from multiple snippets
            contents = []
            for s in file_snippets:
                if s.content and s.content not in contents:
                    contents.append(s.content)

            merged.append(Snippet(
                file_path=file_path,
                content="\n---\n".join(contents[:3]),  # Max 3 snippets
                line_start=min(s.line_start for s in file_snippets) or 0,
                line_end=max(s.line_end for s in file_snippets) or 0,
                score=min(base_score, 1.5),  # Cap at 1.5
                source="merged" if len(sources) > 1 else list(sources)[0],
                metadata={"sources": list(sources)}
            ))

        # Sort by score descending
        merged.sort(key=lambda s: s.score, reverse=True)

        return merged[:limit]


# Convenience functions for quick searches
def quick_search(query: str, limit: int = 10) -> SearchResult:
    """Execute a quick hybrid search with defaults.

    Args:
        query: The search query
        limit: Maximum results

    Returns:
        SearchResult with merged results
    """
    client = HybridSearchClient()
    return client.hybrid_search(query, limit=limit)


def semantic_search(query: str, limit: int = 10) -> list[Snippet]:
    """Execute semantic-only search via Gemini.

    Args:
        query: The search query
        limit: Maximum results

    Returns:
        List of Snippet results
    """
    client = HybridSearchClient()
    return client.search_gemini(query, limit=limit)


def literal_search(pattern: str, path: Optional[str] = None, limit: int = 10) -> list[Snippet]:
    """Execute literal-only search via ripgrep.

    Args:
        pattern: The search pattern
        path: Optional path to search in
        limit: Maximum results

    Returns:
        List of Snippet results
    """
    client = HybridSearchClient()
    return client.search_ripgrep(pattern, path=path, limit=limit)
