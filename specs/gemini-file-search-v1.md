# Gemini File Search Integration v1.2

**Status**: Ready for Implementation
**Priority**: High (enhances Scout phase + context efficiency)
**Created**: 2025-11-28
**Updated**: 2025-11-29 (v1.2 - added mem0 persistent memory layer)
**ADW ID**: GEMINI-SEARCH-V1
**Research**: `ai_docs/research/implementations/gemini-file-search-integration-research.md`
**Memory Research**: `ai_docs/research/implementations/mem0-api-patterns.md`, `mem0-integration-patterns.md`
**Memory Synthesis**: `ai_docs/analyses/mem0-synthesis-2025-11-29.md`

---

## Overview

Integrate Gemini File Search as a **context augmentation layer** for the Scout-Plan-Build framework. This provides semantic code search that:
- Pre-fetches relevant context before agents start (reducing token waste)
- Combines semantic + literal search (hybrid approach)
- Works for both Claude agents AND human developers (CLI)
- Scales to 1M+ LOC monoliths with incremental indexing

---

## Problem Statement

**For large codebases (1M+ LOC)**:
- Agents waste tokens reading irrelevant files trying to find context
- `grep` can't answer conceptual questions ("How does billing work?")
- Semantic search alone misses literal matches
- Index staleness causes outdated results

**Key insight**: The goal isn't to "replace grep" but to **intelligently route queries** to the best tool and **pre-fetch context** so agents start with relevant knowledge.

---

## Solution Architecture

### Core Concept: Search as Context Layer, Not Just Tool

```
┌─────────────────────────────────────────────────────────┐
│  USER QUERY / TASK                                      │
│  "Add caching to UserService"                           │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  CONTEXT AUGMENTATION LAYER (automatic)                 │
│                                                         │
│  1. Smart Refresh Check                                 │
│     └─ If stale + many changes → refresh index          │
│                                                         │
│  2. Query Classification                                │
│     ├─ Conceptual ("How does X work?") → Gemini        │
│     ├─ Literal ("find TODO comments") → ripgrep        │
│     └─ Complex → BOTH, merge & rerank                  │
│                                                         │
│  3. Hybrid Search Execution                             │
│     ├─ Gemini File Search (semantic)                   │
│     └─ ripgrep (literal, fast)                         │
│                                                         │
│  4. Merge & Rank Results                                │
│     └─ Dedupe, weight by source, score by relevance    │
│                                                         │
│  5. Context Injection                                   │
│     └─ Top N snippets → Agent prompt as "CONTEXT"      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  AGENT (Scout / Plan / Build)                           │
│                                                         │
│  ✓ Starts with relevant context pre-loaded              │
│  ✓ Tool optionally available for deeper exploration     │
│  ✓ Better performance, 80%+ token reduction             │
└─────────────────────────────────────────────────────────┘
```

### Agent Integration Philosophy

**Prefer context augmentation over tool forcing**:

| Approach | Pros | Cons | Use When |
|----------|------|------|----------|
| **Pre-fetch (RAG-style)** | No tool overhead, agent starts informed | May inject irrelevant context | Always for Scout phase |
| **Optional Tool** | Agent controls depth | Agent might not call when needed | Available for Plan/Build |
| **Required Tool** | Guaranteed search | Adds latency, failure modes | Never - avoid forcing |

**Implementation**:
- Scout phase: ALWAYS pre-fetch context automatically
- Plan/Build phases: Inject scout results + tool available for deeper exploration
- Human CLI: Direct access via `spb search "query"`

---

## Query Tier System

Not all queries benefit equally from semantic search:

### Tier 1 - Massive Value (grep CAN'T do these)

```
┌─────────────────────────────────────────────────────────┐
│ "How does the billing system work?"                     │
│ "Find similar patterns to this auth implementation"     │
│ "What would break if I changed the User schema?"        │
│ "Show me error handling conventions in this project"    │
└─────────────────────────────────────────────────────────┘
→ Route to: Gemini File Search (semantic)
```

### Tier 2 - Good Value (grep is awkward)

```
┌─────────────────────────────────────────────────────────┐
│ "Where is JWT validation logic?"                        │
│ "Find all API endpoint definitions"                     │
│ "What files relate to payment processing?"              │
└─────────────────────────────────────────────────────────┘
→ Route to: Gemini + ripgrep (hybrid, merge results)
```

### Tier 3 - Marginal Value (grep is fine)

```
┌─────────────────────────────────────────────────────────┐
│ "Find usages of function X"                             │
│ "Find files named *_test.py"                            │
│ "Find the string 'API_KEY'"                             │
└─────────────────────────────────────────────────────────┘
→ Route to: ripgrep only (faster, exact)
```

### Query Classification Heuristic

```python
def classify_query(query: str) -> QueryType:
    """Simple heuristic for query routing."""

    # Literal indicators
    if '"' in query or "'" in query:
        return QueryType.LITERAL
    if re.search(r'[\*\?\[\]]', query):  # Glob/regex chars
        return QueryType.LITERAL
    if query.startswith(('find ', 'grep ', 'search for "', 'usages of ')):
        return QueryType.LITERAL

    # Conceptual indicators
    conceptual_patterns = [
        r'\bhow\b', r'\bwhat\b', r'\bwhy\b', r'\bwhere is\b',
        r'\bexplain\b', r'\bunderstand\b', r'\bsimilar to\b',
        r'\bpattern\b', r'\bconvention\b', r'\baffect\b',
    ]
    if any(re.search(p, query.lower()) for p in conceptual_patterns):
        return QueryType.CONCEPTUAL

    # Default to hybrid for ambiguous queries
    return QueryType.HYBRID
```

---

## Smart Refresh Strategy

**Principle**: Lazy refresh on demand, not scheduled jobs

```python
def should_refresh_index() -> tuple[bool, str]:
    """
    Determine if index needs refresh before query.

    Returns: (should_refresh, reason)
    """
    state = load_index_state()
    last_sha = state.get("last_commit_sha")
    current_sha = git_head_sha()

    # No changes since last index
    if last_sha == current_sha:
        return False, "index is current"

    # Calculate staleness
    commits_since = count_commits_between(last_sha, current_sha)
    changed_files = len(git_diff_files(last_sha, current_sha))
    days_since = days_since_last_index(state)

    # Refresh thresholds
    if commits_since > 50:
        return True, f"{commits_since} commits since last index"
    if changed_files > 100:
        return True, f"{changed_files} files changed"
    if days_since > 7:
        return True, f"{days_since} days since last index"

    return False, "within acceptable staleness"

def smart_search(query: str) -> SearchResult:
    """Search with automatic refresh if needed."""

    # Check if refresh needed
    should_refresh, reason = should_refresh_index()

    if should_refresh:
        # Option A: Refresh synchronously (slower, fresher)
        # Option B: Return stale results + trigger async refresh
        logger.info(f"Triggering index refresh: {reason}")
        refresh_index_incremental()

    return execute_search(query)
```

**Configuration** (`.scout/file_search.yaml`):
```yaml
refresh:
  # Automatic refresh thresholds
  max_commits_before_refresh: 50
  max_files_changed_before_refresh: 100
  max_days_before_refresh: 7

  # Refresh behavior
  mode: "sync"  # sync | async | manual

  # Manual override
  # Set to "manual" to only refresh via CLI command
```

---

## Scale Considerations (1M+ LOC)

**Target**: 1.2M LOC Java monolith, potentially multi-repo

### Sizing Estimates

| Metric | Estimate | Gemini Limit | Status |
|--------|----------|--------------|--------|
| Lines of Code | 1.2M | N/A | N/A |
| Source Files | ~40K (30 LOC avg) | N/A | N/A |
| Total Size | ~80-120 MB | 100 MB/file | ✅ OK |
| Index Tokens | ~30-50M | N/A | ~$5-8 one-time |
| Store Size | ~500 MB indexed | 20 GB recommended | ✅ OK |

### Multi-Repo Strategy

**Option A: One store per repo** (recommended for start)
- Pros: Clear isolation, simple
- Cons: Can't cross-repo search
- Use: `metadata_filter='repo="service-a"'`

**Option B: One store per domain** (future)
- Pros: Cross-repo semantic search
- Cons: More complex metadata management
- Use: `metadata_filter='domain="payments" AND repo="*"'`

### Index Performance

**Full reindex** (1.2M LOC, one-time):
- Upload time: ~30-60 minutes (parallel uploads)
- API cost: ~$5-8 (one-time embedding)

**Incremental reindex** (daily):
- Typical changes: 50-200 files
- Upload time: 1-5 minutes
- API cost: ~$0.01-0.05

---

## Implementation Plan

### Phase 1: Proof of Concept (Spike) ✅ READY

**Goal**: Validate API works and results are useful

**File**: `scripts/gemini_file_search_spike.py`

**Tasks**:
1. Create FileSearchStore via API
2. Upload 5 representative files with metadata
3. Run 3 test queries (conceptual, filtered, literal)
4. Parse grounding metadata for citations
5. Verify metadata filtering works

**Success Criteria**:
- [x] Spike script created
- [ ] Store creation works
- [ ] File upload with metadata works
- [ ] Queries return relevant results
- [ ] Grounding shows source files

**Estimated Time**: 1-2 hours

---

### Phase 2: Query Classification + Hybrid Search

**Goal**: Intelligent routing between Gemini and ripgrep

**Files to create**:
- `adws/adw_modules/gemini_search.py` (~300 LOC)

**Key Functions**:
```python
def classify_query(query: str) -> QueryType
def search_gemini(query: str, filters: dict) -> list[Snippet]
def search_ripgrep(query: str, path: str) -> list[Snippet]
def hybrid_search(query: str) -> SearchResult  # Combines both
```

**Estimated Time**: 2-3 hours

---

### Phase 2.5: Persistent Memory Layer (mem0)

**Goal**: Add agent memory for self-improvement across sessions

**Research**: `ai_docs/research/implementations/mem0-api-patterns.md`, `mem0-integration-patterns.md`
**Synthesis**: `ai_docs/analyses/mem0-synthesis-2025-11-29.md`

**Key Insight**: Gemini = code discovery ("where is auth?"), mem0 = agent memory ("what did we learn about auth in this project?"). Together they create a self-improving agent.

**Files to create**:
- `adws/adw_modules/memory.py` (~200 LOC)

**Dependencies**:
```
mem0ai>=1.0.1
openai>=1.0.0          # For embeddings
qdrant-client>=1.7.0   # Local vector store
```

**Environment**:
```bash
export OPENAI_API_KEY="sk-..."  # For embeddings (required)
```

**Key Classes**:
```python
class PersistentLearningsLayer:
    """Wraps mem0 for Scout-Plan-Build framework"""

    def __init__(self, project_name: str):
        self.memory = Memory.from_config({
            "llm": {"provider": "anthropic", "config": {"model": "claude-3-haiku-20240307"}},
            "embedder": {"provider": "openai", "config": {"model": "text-embedding-3-small"}},
            "vector_store": {"provider": "qdrant", "config": {"path": ".scout/qdrant"}}
        })

    # SCOUT PHASE
    def get_scout_hints(self, task: str) -> str
    def record_discovery(self, task: str, files: list, source: str)

    # PLAN PHASE
    def get_planning_lessons(self, task_type: str) -> str
    def record_decision(self, task: str, decision: str, rationale: str)

    # BUILD PHASE
    def record_pattern(self, framework: str, pattern: str)
    def record_failure(self, error: str, solution: str)
```

**What to Store (HIGH VALUE)**:
| Type | Confidence | Example |
|------|------------|---------|
| Decisions | 0.85 | "Use typer over argparse for CLI" |
| Patterns | 0.80 | "This project uses dataclasses, not Pydantic" |
| Discoveries | 0.75 | "Auth logic in middleware/auth.py" |
| Failures | 0.85 | "Error X → Solution Y" |

**What NOT to Store**: Generic knowledge, transient chat, speculation as fact, full code snippets

**Memory Lifecycle**:
- Session memories: Auto-expire after 1 day
- Task memories: Expire at task deadline
- Pattern memories: Permanent (immutable: true)

**Estimated Time**: 2-3 hours

---

### Phase 3: Context Augmentation Layer

**Goal**: Pre-fetch context before agent starts, using BOTH search AND memory

**Files to create**:
- `adws/adw_modules/context_augmentation.py` (~200 LOC)

**Dependencies**: Requires Phase 2 (gemini_search.py) and Phase 2.5 (memory.py)

**Integration Point**: Before Scout agent prompt assembly

**Architecture**:
```
User Query → Context Augmentation Layer
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    Query mem0            Classify Query
    "What patterns        (Conceptual/Literal/Hybrid)
     worked before?"            │
          │                     │
          └───────┬─────────────┘
                  ▼
         Augmented Query with Memory Hints
                  │
          ┌───────┴───────┐
          ▼               ▼
    Gemini Search     ripgrep
    (semantic)        (literal)
          │               │
          └───────┬───────┘
                  ▼
            Merge & Rank
                  │
                  ▼
         Store Learnings → mem0
         (What worked, what failed)
                  │
                  ▼
           Final Result → Inject into prompt
```

```python
class ContextAugmenter:
    """Orchestrates memory + search for context injection"""

    def __init__(self, project_name: str):
        self.memory = PersistentLearningsLayer(project_name)
        self.search = HybridSearchClient()

    def augment_prompt_with_context(self, task: str, base_prompt: str) -> str:
        """
        Full pipeline: memory hints → search → store learnings → inject context.
        """
        # 1. Get hints from past similar tasks
        memory_hints = self.memory.get_scout_hints(task)

        # 2. Augment query with memory context
        augmented_query = task
        if memory_hints:
            augmented_query = f"{task}\n\nPast patterns: {memory_hints}"

        # 3. Execute hybrid search
        results = self.search.hybrid_search(augmented_query)

        # 4. Store new learnings
        if results.success:
            self.memory.record_discovery(
                task=task,
                files=[s.file_path for s in results.snippets[:5]],
                source="hybrid_search"
            )

        # 5. Format and inject
        context_block = self._format_context_block(results.snippets[:10])
        learnings_block = memory_hints if memory_hints else ""

        return f"""
{base_prompt}

## LEARNED PATTERNS (from past similar tasks)

{learnings_block if learnings_block else "No prior patterns found."}

## RELEVANT CONTEXT (from codebase search)

The following code snippets may be relevant to this task:

{context_block}

---
"""
```

**Estimated Time**: 2-3 hours

---

### Phase 4: Smart Indexer

**Goal**: Git-aware incremental indexing with smart refresh

**Files to create**:
- `scripts/index_codebase.py` (~250 LOC)
- `.scout/file_search.yaml` (~50 LOC)

**Config Schema**:
```yaml
version: "1.0"

store:
  name: "spb-codebase"

index:
  include:
    - "**/*.py"
    - "**/*.java"  # For Java monoliths
    - "**/*.js"
    - "**/*.ts"
    - "**/*.md"
    - "**/*.yaml"
    - "**/*.json"

  exclude:
    - ".git/**"
    - "**/node_modules/**"
    - "**/build/**"
    - "**/target/**"  # Java build output
    - "**/__pycache__/**"
    - "**/generated/**"

metadata:
  repo: "auto"  # Auto-detect from git remote

refresh:
  max_commits_before_refresh: 50
  max_files_changed_before_refresh: 100
  max_days_before_refresh: 7
  mode: "sync"

state_file: "scout_outputs/.gemini_index_state.json"
```

**CLI Interface**:
```bash
# Incremental (default, with smart refresh check)
python scripts/index_codebase.py

# Full reindex
python scripts/index_codebase.py --full

# Check status only
python scripts/index_codebase.py --status

# Dry run
python scripts/index_codebase.py --dry-run
```

**Estimated Time**: 3-4 hours

---

### Phase 5: Human CLI + Agent Tool

**Goal**: Unified interface for humans and agents

**CLI** (`spb search`):
```bash
# Conceptual search
spb search "how does authentication work"

# With filters
spb search "error handling" --path src/api --lang python

# Literal search (bypasses Gemini)
spb search --literal "TODO: fix"

# Output format
spb search "billing" --format json
```

**Agent Tool** (optional, for deep dives):
```python
@tool
def code_search(query: str, path_prefix: str = None) -> str:
    """
    Search the codebase for relevant code.

    Use this when you need more context beyond what's provided,
    or to find specific implementation details.
    """
    result = hybrid_search(query, path_prefix=path_prefix)
    return format_for_agent(result)
```

**Files to create**:
- `.claude/commands/workflow/code_search.md`
- `scripts/spb_search.py` (CLI entry point)

**Estimated Time**: 2-3 hours

---

### Phase 6: Evaluation Harness

**Goal**: Track search quality over time

**Files**:
- `tests/eval/code_search_benchmark.json`
- `scripts/eval_code_search.py`

**Metrics**:
- Hit Rate @k (target: >80%)
- Mean Reciprocal Rank
- Query Classification Accuracy
- Fallback Rate

**Estimated Time**: 2 hours

---

## File Summary

### Files to Create

| File | Purpose | LOC Est | Status |
|------|---------|---------|--------|
| `scripts/gemini_file_search_spike.py` | Proof of concept | ~120 | ✅ Done |
| `scripts/index_codebase.py` | Smart indexer | ~450 | ✅ Done |
| `.scout/file_search.yaml` | Configuration | ~80 | ✅ Done |
| `adws/adw_modules/memory.py` | **Persistent learnings (mem0)** | **~200** | **Phase 2.5** |
| `adws/adw_modules/gemini_search.py` | Hybrid search module | ~300 | Phase 2 |
| `adws/adw_modules/context_augmentation.py` | Orchestrator (memory + search) | ~200 | Phase 3 |
| `scripts/spb_search.py` | Human CLI | ~100 | Phase 5 |
| `.claude/commands/workflow/code_search.md` | Agent command | ~30 | Phase 5 |
| `tests/eval/code_search_benchmark.json` | Eval dataset | ~100 | Phase 6 |
| `scripts/eval_code_search.py` | Eval runner | ~100 | Phase 6 |

### Files to Modify

| File | Change | LOC Est |
|------|--------|---------|
| `adws/scout_simple.py` | Add context augmentation | +30 |
| `adws/adw_modules/workflow_ops.py` | Pre-fetch before agents | +20 |

### Dependencies to Add

```
# requirements.txt or pyproject.toml
mem0ai>=1.0.1
openai>=1.0.0          # For embeddings
qdrant-client>=1.7.0   # Local vector store
google-genai>=1.48.0   # Gemini SDK (Python 3.10+)
```

### Total Estimated LOC: ~1,680

---

## Token Savings Analysis

**Without semantic search** (current):
```
Agent reads files to find context:
- Reads 10 files trying to find relevant ones
- Average 3K tokens per file
- Total: ~30K tokens just for exploration
```

**With context augmentation**:
```
System pre-fetches relevant snippets:
- Injects top 10 snippets (~300 tokens each)
- Total: ~3K tokens
- Agent starts informed, fewer file reads needed
```

**Estimated savings**: 80%+ reduction in exploration tokens

---

## Success Criteria

1. **Spike works**: Store creation, upload, query all succeed
2. **Query classification works**: Conceptual → Gemini, Literal → ripgrep
3. **Hybrid merge works**: Combined results are better than either alone
4. **Context augmentation works**: Agents get relevant snippets pre-loaded
5. **Indexer is incremental**: Only uploads changed files
6. **Search quality**: Hit rate >80% on benchmark
7. **Scale**: Works on 1M+ LOC codebase

---

## Rollback Plan

1. **Disable pre-fetch**: Set `SPB_DISABLE_CONTEXT_AUGMENTATION=1`
2. **Disable Gemini**: Set `SPB_DISABLE_GEMINI=1` (ripgrep only)
3. **Fallback automatic**: If Gemini API fails, ripgrep used automatically

No data loss possible - Gemini store is supplementary to git.

---

## Spike Results (2025-11-28)

**Status**: ✅ Validated

### Test Results

| Test | Query | Filter | Result |
|------|-------|--------|--------|
| Conceptual | "Where is Scout implemented?" | None | ✅ Found `scout_simple.py` |
| Language filter | "How are Claude agents executed?" | `language="python"` | ✅ Found `agent.py` |
| Path filter | "Configuration constants?" | `path_prefix="adws/*"` | ⚠️ Filter syntax issue |

### Key Findings

1. **Python 3.10+ required** - SDK v1.48+ dropped Python 3.9 support
2. **Semantic search works** - Correct files found from conceptual queries
3. **Grounding metadata works** - Source files returned with responses

### AIP-160 Filter Syntax (Corrected)

```python
# ✅ Correct wildcard syntax (quotes around value)
metadata_filter = 'path_prefix = "adws/*"'

# ✅ Exact match
metadata_filter = 'path_prefix = "adws/adw_modules"'

# ✅ Multiple values
metadata_filter = 'path_prefix: ANY("adws/adw_modules", "scripts")'

# ❌ Our broken syntax (no spaces around =)
metadata_filter = 'path_prefix="adws/*"'
```

**Note**: Slashes in paths may need escaping or dot notation in some contexts.

---

## Requirements

### Python Version

| Version | SDK | FileSearch |
|---------|-----|------------|
| 3.9 | ≤1.47.0 | ❌ |
| 3.10+ | ≥1.48.0 | ✅ |

**Recommendation**: Use Python 3.10+ or create dedicated venv:
```bash
python3.13 -m venv .venv-gemini
source .venv-gemini/bin/activate
pip install google-genai
```

### Environment

```bash
export GEMINI_API_KEY="your-key"
```

---

## Future Enhancements (v2+)

- [ ] Multi-repo search (unified store with repo metadata)
- [ ] AST-aware chunking (function/class boundaries)
- [ ] Learning from usage (track which queries work well)
- [ ] IDE extension (VS Code, JetBrains)
- [ ] Cost monitoring dashboard
- [ ] Background async refresh

---

## SOTA Comparison

| Feature | Our Approach | Sourcegraph | GitHub Search | Cursor |
|---------|--------------|-------------|---------------|--------|
| Semantic search | ✅ Gemini | ✅ | ❌ | ✅ |
| Literal search | ✅ ripgrep | ✅ | ✅ | ✅ |
| Hybrid merge | ✅ | ✅ | ❌ | ? |
| Query classification | ✅ | ❌ manual | ❌ | ? |
| Context augmentation | ✅ | ❌ | ❌ | ✅ |
| Cross-repo | 🔜 v2 | ✅ | ✅ | ❌ |
| Self-hosted | ✅ | $$$ | ❌ | ❌ |
| Cost | ~$5 + free queries | $$$$ | Free | $20/mo |

---

## References

- Research: `ai_docs/research/implementations/gemini-file-search-integration-research.md`
- Original spec: `ai_docs/research/llm-chats/gemini-file-search-repo-indexi-chad.md`
- [Gemini File Search Docs](https://ai.google.dev/gemini-api/docs/file-search)
- [AIP-160 Filter Syntax](https://google.aip.dev/160)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
