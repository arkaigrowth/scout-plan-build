# Mem0 Research Synthesis - Integration Strategy

**Date:** 2025-11-29
**Status:** Analysis Complete → Ready for Implementation
**Sources:** `ai_docs/research/implementations/mem0-api-patterns.md`, `mem0-integration-patterns.md`

---

## Executive Summary

Mem0 and Gemini File Search are **COMPLEMENTARY**, not competing:

| Layer | Purpose | Question Answered |
|-------|---------|-------------------|
| **Gemini File Search** | Code discovery | "Where is auth code?" |
| **mem0** | Agent memory | "What did we learn about auth in this project?" |

Together, they create a **self-improving agent** that gets smarter with each task.

---

## Key Insight: Memory Makes Search Smarter

**Without mem0:**
```
Query: "How does authentication work?"
→ Gemini returns generic auth files
→ Agent might miss project-specific patterns
```

**With mem0:**
```
Query: "How does authentication work?"
→ First, mem0: "What do we know about auth here?"
→ Returns: "This project uses JWT in middleware/auth.py"
→ Augmented query includes this context
→ Gemini returns MORE relevant files
→ Store new learnings after
```

---

## Architecture Decision: Separate Modules

```
adws/adw_modules/
├── memory.py               # mem0 wrapper (standalone)
├── gemini_search.py        # Hybrid search (Gemini + ripgrep)
└── context_augmentation.py # Orchestrator (uses both)
```

**Rationale:**
- Single responsibility per module
- Memory serves ALL phases (Scout, Plan, Build)
- Clear dependency graph: memory.py → gemini_search.py → context_augmentation.py

---

## What to Store (HIGH VALUE)

| Memory Type | Example | Confidence | Phase |
|-------------|---------|------------|-------|
| **Decisions** | "Use typer over argparse for CLI" | 0.85 | Plan |
| **Patterns** | "This project uses dataclasses, not Pydantic" | 0.80 | Build |
| **Discoveries** | "Auth logic in middleware/auth.py, tokens in User model" | 0.75 | Scout |
| **Failures** | "ModuleNotFoundError: Install mem0ai, not mem0" | 0.85 | Any |
| **Capabilities** | "Sequential MCP for complex debugging (3+ components)" | 0.70 | Any |

---

## What NOT to Store (LOW VALUE)

| Anti-Pattern | Why Bad |
|--------------|---------|
| Generic knowledge | LLM already knows "what is REST" |
| Transient chat | "Hi", "Thanks" = noise |
| Speculation as fact | Creates false memories |
| Full transcripts | mem0 auto-extracts, don't dump raw |
| Full code snippets | Gemini handles code, mem0 handles insights |

---

## Confidence Thresholds

```python
CONFIDENCE_LEVELS = {
    "decision": 0.85,      # Strong architectural choices
    "pattern": 0.80,       # Code patterns that work
    "discovery": 0.75,     # File discovery results
    "hypothesis": 0.40,    # Unverified ideas
}
```

**Boost confidence for:**
- Validated by tests: +0.10
- User confirmed: +0.05

---

## Memory Lifecycle

```
Addition → Active Use (Days 1-30) → Decay (Days 30-90) → Expiration

Session memories:  expiration_date = today + 1 day
Task memories:     expiration_date = task deadline
Pattern memories:  No expiration (immutable: true)
```

---

## Integration Flow

```
SESSION START
     │
     ▼
[Load project context from mem0]
     │
     ▼
SCOUT PHASE
├── Query mem0: "Scout patterns for {task}"
├── Augment Gemini query with hints
├── Execute hybrid search
└── Store: "For {task}, found {files}"
     │
     ▼
PLAN PHASE
├── Query mem0: "Planning lessons for {type}"
├── Inject into planning prompt
└── Store: "Chose {approach} because {rationale}"
     │
     ▼
BUILD PHASE
├── Query mem0: "Implementation patterns"
├── Inject into build prompt
├── On success: Store pattern
└── On failure: Store error + solution
     │
     ▼
SESSION END
├── mem0 auto-consolidates (dedupes, merges)
└── Session memories expire
```

---

## Updated Spec Phases

| Phase | Description | LOC | Status |
|-------|-------------|-----|--------|
| 1 | Spike | ~120 | ✅ Done |
| 2 | Hybrid Search | ~300 | Ready |
| **2.5** | **Memory Layer (NEW)** | **~200** | **NEW** |
| 3 | Context Augmentation | ~200 | Ready |
| 4 | Smart Indexer | ~450 | ✅ Done |
| 5-6 | CLI + Eval | ~200 | Deferred |

---

## Dependencies

```
# requirements.txt additions
mem0ai>=1.0.1
openai>=1.0.0          # For embeddings
qdrant-client>=1.7.0   # Local vector store (or use sqlite)
```

**Environment:**
```bash
export OPENAI_API_KEY="sk-..."       # For embeddings
export ANTHROPIC_API_KEY="sk-ant-..."  # For LLM extraction (already have)
```

---

## Cost Analysis

| Operation | Cost |
|-----------|------|
| 100 memories stored | ~$0.01 (embeddings) |
| 50 searches/day | ~$0.005 |
| LLM extraction (Haiku) | ~$0.01/session |
| **Total per session** | **~$0.02** |

---

## Implementation Order

1. **memory.py** (~200 LOC) - Standalone mem0 wrapper
2. **gemini_search.py** (~300 LOC) - Hybrid search (works without memory)
3. **context_augmentation.py** (~200 LOC) - Orchestrator (ties them together)
4. **Integration** - Wire into scout_simple.py

---

## Quick Start Template

```python
# memory.py skeleton
from mem0 import Memory

class PersistentLearningsLayer:
    def __init__(self, project_name: str):
        self.project = project_name
        self.memory = Memory.from_config({
            "llm": {"provider": "anthropic", "config": {"model": "claude-3-haiku-20240307"}},
            "embedder": {"provider": "openai", "config": {"model": "text-embedding-3-small"}},
            "vector_store": {"provider": "qdrant", "config": {"path": ".scout/qdrant"}}
        })

    def get_scout_hints(self, task: str) -> str:
        results = self.memory.search(f"Scout patterns for: {task}", user_id=self.project, limit=5)
        return self._format_hints(results)

    def record_discovery(self, task: str, files: list, source: str):
        self.memory.add(
            messages=[{"role": "system", "content": f"For '{task}', key files: {files}"}],
            user_id=self.project,
            metadata={"type": "discovery_pattern", "phase": "scout", "source": source, "confidence": 0.75}
        )

    def record_failure(self, error: str, solution: str):
        self.memory.add(
            messages=[{"role": "system", "content": f"Error: {error}\nSolution: {solution}"}],
            user_id=self.project,
            metadata={"type": "failure_recovery", "priority": "high", "confidence": 0.85}
        )
```

---

## Next Steps

1. ✅ Research synthesis complete (this document)
2. 🔄 Update spec with Phase 2.5
3. ⏳ Build memory.py
4. ⏳ Build gemini_search.py
5. ⏳ Build context_augmentation.py
6. ⏳ Integration test

---

**Generated:** 2025-11-29
**Framework:** Scout Plan Build MVP
