# Mem0 Integration Patterns for AI Agent Frameworks

**Date:** November 29, 2025  
**Status:** Research Complete  
**Focus:** Direct API Integration Patterns for Scout/Plan/Build MVP

---

## Executive Summary

Mem0 is a **universal memory layer** for LLM-based AI agents that complements code search (like Gemini File Search) by providing **persistent, context-aware memory across sessions**. While Gemini File Search excels at semantic code discovery, mem0 specializes in capturing and retrieving **agent learnings, decisions, patterns, and behavioral context**.

### Key Findings

| Aspect | Finding |
|--------|---------|
| **Architecture** | Modular, plug-and-play; works with 16+ LLM providers, 10+ embeddings |
| **Performance** | 66.9% accuracy, 0.20s median latency, 91% lower p95 latency than baseline |
| **Memory Types** | Episodic, semantic, procedural, associative (4+ types supported) |
| **Lifecycle Control** | Expiration dates, immutability flags, confidence thresholds, decay mechanisms |
| **Integration** | Native support for LangGraph, CrewAI, LangChain, AutoGen, Google ADK, Agno |
| **Cost Impact** | 90% token savings vs. full-context approach; 26% accuracy improvement over OpenAI baseline |

---

## Part 1: Mem0 vs. Gemini File Search - Complementary Roles

### Gemini File Search: Code Discovery
**Purpose:** Semantic search over source code repository  
**Strengths:**
- Finds relevant files by intent (e.g., "where is auth validation?")
- Semantic similarity matching for code patterns
- Stateless, read-only access to codebase
- Low latency, high precision for code lookup

**Limitations:**
- No persistent learning across calls
- No agent behavioral context
- No decision history
- Cannot track what the agent tried and failed

### Mem0: Agent Memory
**Purpose:** Persistent behavioral and decision context  
**Strengths:**
- Remembers agent decisions, patterns, preferences
- Learns what works/fails for this specific task
- User/session-aware context
- Cross-session continuity
- Self-improving through experience

**Limitations:**
- Not designed for large codebase discovery
- Better for behavioral patterns than code structure
- Requires explicit extraction and storage

### Complementary Workflow

```
Scout Phase:
  1. Use Gemini File Search → Find relevant code files
  2. Cache results in Mem0 → "For task X, these files are relevant"

Plan Phase:
  1. Query Mem0 → "What did we learn last time planning similar tasks?"
  2. Use learnings to shape planning approach
  3. Store planning decisions in Mem0 → "Tried approach A, failed because..."

Build Phase:
  1. Query Mem0 → "What patterns worked for similar code?"
  2. Execute build with prior learnings
  3. Update Mem0 → "Pattern X works for this framework"

Analysis Phase:
  1. Query Mem0 → "What assumptions did we make?"
  2. Validate against learnings
  3. Update confidence scores
```

---

## Part 2: What Memories are Most Valuable?

### High-Value Memory Patterns (STORE THESE)

#### 1. **Decisions & Reasoning** (Priority: CRITICAL)
What to store: Major architectural choices, trade-off analysis, chosen patterns  
Example memory:
```
{
  "type": "decision",
  "content": "For Scout phase in Python codebases, prefer ast-grep over ripgrep for semantic matching",
  "confidence": 0.95,
  "tags": ["scout", "python", "file-search"],
  "source_task": "gemini-file-search-v1",
  "timestamp": "2025-11-29"
}
```

#### 2. **Learned Patterns** (Priority: CRITICAL)
What to store: Code patterns that work, framework conventions, idioms  
Example memory:
```
{
  "type": "pattern",
  "content": "This codebase uses .claude/commands/ for custom slash commands with YAML metadata",
  "framework": "scout_plan_build",
  "tags": ["architecture", "command-routing"],
  "reusable_across": ["similar python projects"],
  "confidence": 0.9
}
```

#### 3. **Failures & Debug Paths** (Priority: HIGH)
What to store: What didn't work and why; helps avoid repeating mistakes  
Example memory:
```
{
  "type": "failure",
  "content": "Scout command failed: Task tool not available. Fix: Use native Grep/Glob instead",
  "error_code": "MISSING_TOOL",
  "workaround": "Native tools",
  "timestamp": "2025-11-29",
  "tags": ["scout", "troubleshooting"]
}
```

#### 4. **Task Context** (Priority: HIGH)
What to store: User preferences, project structure, conventions discovered  
Example memory:
```
{
  "type": "context",
  "content": "User prefers absolute paths over relative; dislikes emojis in technical output",
  "tags": ["user-preference", "output-format"],
  "immutable": true,
  "applies_to": ["all-tasks"]
}
```

#### 5. **Framework/Tool Capabilities** (Priority: MEDIUM)
What to store: What each tool can do, limitations, best approaches  
Example memory:
```
{
  "type": "capability",
  "content": "Sequential thinking MCP best for: complex debugging (3+ components), architectural analysis, hypothesis testing",
  "framework": "SuperClaude",
  "tags": ["mcp", "tool-selection"],
  "source": "FLAGS.md"
}
```

#### 6. **Code Structure Insights** (Priority: MEDIUM)
What to store: Critical architectural patterns, module relationships  
Example memory:
```
{
  "type": "architecture",
  "content": "adw_modules/ contains: agent.py (core), github.py (GH integration), orchestrate.py (workflow)",
  "project": "scout_plan_build_mvp",
  "tags": ["architecture", "module-map"],
  "timestamp": "2025-11-29"
}
```

### Low-Value Memory Patterns (DON'T STORE)

#### 1. **Generic Knowledge**
❌ "What is machine learning?"  
❌ "How does Python import work?"  
❌ "What is REST API?"  
*Reason:* LLM already knows this; doesn't personalize or improve agent

#### 2. **Transient Conversation**
❌ "Hi there" / "Thanks!" / "Got it"  
❌ Casual greetings, acknowledgments  
*Reason:* No value after session ends; pollutes memory

#### 3. **Speculation as Fact**
❌ "I think the user might want X"  
❌ "Possibly should implement Y"  
❌ "Maybe this is the issue"  
*Reason:* Creates false memories; dangerous in decision-critical contexts

#### 4. **Full Conversation Transcripts**
❌ Storing every message from a chat session  
*Reason:* Mem0's extraction already summarizes; raw transcripts waste storage

#### 5. **Duplicate Information**
❌ Same fact stated multiple ways  
*Reason:* Mem0's update phase handles consolidation automatically

---

## Part 3: Integration Architecture

### Direct API Integration Pattern

```python
from mem0 import Memory
from anthropic import Anthropic

class AgentWithMemory:
    def __init__(self, user_id: str, agent_name: str):
        self.user_id = user_id
        self.agent_name = agent_name
        
        # Initialize Mem0 with direct API
        self.memory = Memory.from_config({
            "llm": {
                "provider": "anthropic",
                "config": {
                    "model": "claude-3-5-sonnet",
                    "api_key": os.getenv("ANTHROPIC_API_KEY")
                }
            },
            "embedder": {
                "provider": "openai",  # Or use local embeddings
                "config": {"model": "text-embedding-3-small"}
            },
            "vector_store": {
                "provider": "qdrant",  # Self-hosted or cloud
                "config": {"host": "localhost", "port": 6333}
            }
        })
        
        self.client = Anthropic()
    
    def scout_phase(self, task_description: str) -> dict:
        """Scout phase with memory injection"""
        # Retrieve relevant patterns from past scout operations
        memories = self.memory.search(
            query=f"Scout patterns for: {task_description}",
            user_id=self.user_id,
            limit=5
        )
        
        memory_context = self._format_memories(memories)
        
        # Inject memories into system prompt
        system_prompt = f"""You are a Scout agent for code exploration.
Your role: Find relevant files using semantic search.

LEARNED PATTERNS (from past scouts):
{memory_context}

Instructions: Use these patterns to guide your search strategy."""
        
        # Execute scout
        response = self.client.messages.create(
            model="claude-3-5-sonnet",
            system=system_prompt,
            messages=[{"role": "user", "content": task_description}]
        )
        
        result = {"files": response.content[0].text}
        
        # Store new learnings
        self.memory.add(
            messages=[
                {"role": "user", "content": task_description},
                {"role": "assistant", "content": response.content[0].text}
            ],
            user_id=self.user_id,
            metadata={
                "agent": self.agent_name,
                "phase": "scout",
                "type": "discovery"
            }
        )
        
        return result
    
    def _format_memories(self, search_results) -> str:
        """Convert memory search results into readable context"""
        if not search_results["results"]:
            return "No relevant patterns found."
        
        formatted = []
        for result in search_results["results"]:
            formatted.append(f"- {result['memory']} (confidence: {result['hash']})")
        
        return "\n".join(formatted)
```

### Integration Points

| Phase | Mem0 Integration | Purpose |
|-------|------------------|---------|
| **Scout** | Pre-prompt: Ask "What patterns worked before?" | Improve file discovery strategy |
| **Plan** | Pre-prompt: Ask "What decisions failed?" | Avoid bad patterns; reuse good ones |
| **Build** | Context injection: "Learned code patterns" | Guide implementation decisions |
| **Test** | Post-execution: Store "What broke, what worked" | Build failure/success patterns |
| **Session End** | Store consolidated learnings | Enable cross-session improvement |

---

## Part 4: Memory Lifecycle Management

### Adding Memories (When)

```python
# 1. After successful operations (BUILD PATTERNS)
memory.add(
    messages=[user_msg, assistant_msg],
    user_id=user_id,
    metadata={
        "type": "success_pattern",
        "phase": "build",
        "framework": "scout_plan_build"
    }
)

# 2. After failures (LEARN FROM ERRORS)
memory.add(
    messages=[{"role": "system", "content": f"Error: {error_msg}"}],
    user_id=user_id,
    metadata={
        "type": "failure_recovery",
        "error_code": error_code,
        "workaround": solution,
        "priority": "high"
    }
)

# 3. For decisions made (AUDIT TRAIL)
memory.add(
    messages=[{"role": "system", "content": f"Decision: {decision}"}],
    user_id=user_id,
    metadata={
        "type": "decision",
        "rationale": reasoning,
        "confidence": 0.9
    }
)

# 4. For user preferences (ONE-TIME SETUP)
memory.add(
    messages=[{"role": "system", "content": "User preferences: prefers absolute paths"}],
    user_id=user_id,
    metadata={
        "type": "preference",
        "immutable": True,  # Don't auto-update
        "scope": "all"
    }
)
```

### Updating Memories (When & How)

Mem0 automatically updates memories if:
- New fact is related to existing memory (vector similarity > threshold)
- LLM determines UPDATE is appropriate operation

Manual update triggers:
```python
# 1. Confidence score changes
memory.update(
    memory_id="mem-123",
    data={"confidence": 0.95},  # Was 0.8
    user_id=user_id
)

# 2. Validity range changes
memory.update(
    memory_id="mem-456",
    data={"expiration_date": "2025-12-31"},
    user_id=user_id
)
```

### Expiring Memories (When)

```python
# 1. Temporary context (expires automatically)
memory.add(
    messages=[...],
    user_id=user_id,
    metadata={
        "type": "session_context",
        "expiration_date": "2025-11-30"  # Today + 1 day
    }
)

# 2. Contextual facts (expire on condition)
memory.add(
    messages=[...],
    user_id=user_id,
    metadata={
        "type": "task_specific",
        "expiration_date": "2025-12-15",  # Task deadline
        "scope": "task-gemini-file-search"
    }
)
```

### Deleting Memories (When)

```python
# 1. Explicitly wrong/harmful memories
memory.delete(memory_id="mem-bad", user_id=user_id)

# 2. Outdated patterns
memory.delete(memory_id="mem-old", user_id=user_id)

# 3. Privacy/compliance reasons
memory.search_delete(
    query="user-pii-pattern",
    user_id=user_id,
    filter={"type": "pii"}
)
```

### Lifecycle Timeline

```
Addition → Validation → Active Use → Decay/Expiry → Deletion

Addition:
  - Confidence threshold (default 0.6+)
  - Custom rules apply
  - Metadata tagged

Active Use (Days 1-30):
  - Retrieved in relevant queries
  - Confidence may increase with reinforcement
  - Updated if new related facts arrive

Decay Phase (Days 30-90):
  - Relevance scores gradually decrease
  - Retrieved less frequently
  - Can be manually refreshed

Expiration:
  - Date-based: Automatic
  - Decay-based: Low relevance = stopped retrieval
  - Manual: Explicit deletion

Deletion:
  - After expiration window
  - On manual request
  - On privacy/compliance triggers
```

---

## Part 5: Anti-Patterns to Avoid

### 1. **Storing Speculation as Fact**

❌ **ANTI-PATTERN**
```python
# BAD: Uncertain facts without confidence marking
memory.add(
    messages=[{
        "role": "assistant",
        "content": "User probably wants authentication because they mentioned security"
    }],
    user_id=user_id
)
```

✅ **BEST PRACTICE**
```python
# GOOD: Mark speculation clearly, use low confidence
memory.add(
    messages=[{
        "role": "system",
        "content": "HYPOTHESIS (low confidence): User may prioritize security features"
    }],
    user_id=user_id,
    metadata={
        "type": "hypothesis",
        "confidence": 0.4,
        "requires_validation": True
    }
)
```

### 2. **No Filtering - Everything Goes In**

❌ **ANTI-PATTERN**
```python
# BAD: Raw conversation transcript stored as-is
memory.add(
    messages=full_conversation_history,  # 1000 messages!
    user_id=user_id
)
```

✅ **BEST PRACTICE**
```python
# GOOD: Let Mem0's extraction do the filtering
memory.add(
    messages=[
        {"role": "user", "content": "How should we implement auth?"},
        {"role": "assistant", "content": "Use JWT with refresh tokens..."}
    ],
    user_id=user_id,
    metadata={
        "type": "decision",
        "phase": "planning",
        "min_confidence": 0.75  # Only store if LLM confidence > 75%
    }
)
# Mem0 will extract relevant facts, ignore greetings/small talk
```

### 3. **Duplicate Information Accumulation**

❌ **ANTI-PATTERN**
```python
# BAD: Same fact added multiple times
for i in range(10):
    memory.add(
        messages=[{"role": "system", "content": "User prefers absolute paths"}],
        user_id=user_id
    )
```

✅ **BEST PRACTICE**
```python
# GOOD: Add once, let Mem0's update phase consolidate
memory.add(
    messages=[{"role": "system", "content": "User prefers absolute paths"}],
    user_id=user_id,
    metadata={
        "type": "preference",
        "immutable": True,
        "scope": "all"
    }
)
# Mem0's consolidation = (ADD | UPDATE | DELETE | MERGE) automatically
```

### 4. **No Confidence Threshold**

❌ **ANTI-PATTERN**
```python
# BAD: Accept all memories regardless of quality
memory.add(messages=[...], user_id=user_id)
# Uses internal default (0.6) without control
```

✅ **BEST PRACTICE**
```python
# GOOD: Set explicit thresholds per memory type
HIGH_CONFIDENCE = 0.85  # Decisions, architecture
MEDIUM_CONFIDENCE = 0.7  # Patterns, learnings
LOW_CONFIDENCE = 0.4    # Hypotheses, exploration

memory.add(
    messages=[...],
    user_id=user_id,
    metadata={
        "type": "decision",
        "min_confidence": HIGH_CONFIDENCE
    }
)
```

### 5. **Storing Full Context Instead of Summaries**

❌ **ANTI-PATTERN**
```python
# BAD: Store entire code snippet
memory.add(
    messages=[{
        "role": "assistant",
        "content": """
        def complex_function():
            # 200 lines of code...
        """
    }],
    user_id=user_id
)
```

✅ **BEST PRACTICE**
```python
# GOOD: Store the insight, not the code
memory.add(
    messages=[{
        "role": "system",
        "content": "Pattern: For file discovery, semantic similarity search is 40% faster than regex patterns"
    }],
    user_id=user_id,
    metadata={
        "type": "performance_pattern",
        "applies_to": ["scout_phase"],
        "source_file": "agent.py",
        "benchmark": "40% faster"
    }
)
```

### 6. **No Scope/Expiration - Everything Permanent**

❌ **ANTI-PATTERN**
```python
# BAD: Session-specific data becomes permanent clutter
memory.add(
    messages=[{"role": "system", "content": "Current task: Implement auth"}],
    user_id=user_id
    # No expiration_date = permanent!
)
```

✅ **BEST PRACTICE**
```python
# GOOD: Set scope and expiration appropriately
memory.add(
    messages=[{"role": "system", "content": "Current task: Implement auth"}],
    user_id=user_id,
    metadata={
        "type": "session_context",
        "scope": "current_task",
        "expiration_date": "2025-11-29",  # Today
        "task_id": "task-123"
    }
)
```

### 7. **Memory Bloat from Redundant Extraction**

❌ **ANTI-PATTERN**
```python
# BAD: Extract from conversation at every turn
for turn in conversation:
    memory.add(messages=[turn], user_id=user_id)
    # Creates 100s of minor memories
```

✅ **BEST PRACTICE**
```python
# GOOD: Batch extraction, let consolidation handle duplicates
memory.add(
    messages=conversation_segment,  # 5-10 turns
    user_id=user_id,
    metadata={"type": "batch_extraction"}
)
# Mem0 UPDATE phase = consolidates duplicates automatically
```

---

## Part 6: Concrete Integration Plan for Scout/Plan/Build

### Phase 1: Foundation (Week 1)

**Objective:** Basic mem0 integration with direct API calls

```python
# .claude/commands/mem0_bootstrap.py
import os
from mem0 import Memory
from anthropic import Anthropic

class ScoutPlanBuildMemory:
    """Mem0 integration for agent framework"""
    
    def __init__(self):
        self.memory = Memory.from_config({
            "llm": {
                "provider": "anthropic",
                "config": {"model": "claude-3-5-sonnet"}
            },
            "embedder": {
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            },
            "vector_store": {
                "provider": "sqlite",  # Local for MVP
                "config": {"db_path": "ai_docs/.mem0/memory.db"}
            }
        })
    
    def add_discovery(self, task: str, files: list, source: str):
        """Store file discovery patterns"""
        self.memory.add(
            messages=[{
                "role": "system",
                "content": f"For task '{task}', discovered files: {files}"
            }],
            user_id="default_user",
            metadata={
                "type": "discovery_pattern",
                "phase": "scout",
                "source": source,
                "framework": "scout_plan_build"
            }
        )
    
    def add_planning_decision(self, task: str, decision: str, rationale: str):
        """Store planning decisions"""
        self.memory.add(
            messages=[{
                "role": "system",
                "content": f"Decision: {decision}\nRationale: {rationale}"
            }],
            user_id="default_user",
            metadata={
                "type": "planning_decision",
                "phase": "plan",
                "task": task,
                "confidence": 0.85
            }
        )
    
    def get_relevant_patterns(self, query: str, limit: int = 5):
        """Retrieve relevant patterns for current task"""
        results = self.memory.search(
            query=query,
            user_id="default_user",
            limit=limit
        )
        return results["results"]

# Usage in agent
mem = ScoutPlanBuildMemory()

# After scout phase
mem.add_discovery(
    task="Implement auth",
    files=["auth.py", "models.py", "views.py"],
    source="gemini_file_search"
)

# Before planning
patterns = mem.get_relevant_patterns("Similar auth implementations")
```

**Deliverables:**
- Mem0 config with local SQLite backend
- Scout phase → discovery pattern storage
- Query API for retrieving patterns
- Documentation of what gets stored

### Phase 2: Integration (Week 2-3)

**Objective:** Full lifecycle integration with all phases

```python
# adws/adw_modules/memory.py
class AgentMemoryManager:
    """Manages agent learnings across Scout/Plan/Build"""
    
    def __init__(self, project_name: str, user_id: str = "default"):
        self.mem = ScoutPlanBuildMemory()
        self.project = project_name
        self.user = user_id
    
    # SCOUT PHASE
    def record_file_discovery(self, task_id: str, files_found: list):
        """Store file discovery for future scout operations"""
        self.mem.add_discovery(
            task=task_id,
            files=files_found,
            source="agent_scout"
        )
    
    def get_scout_hints(self, task_id: str) -> str:
        """Get hints for scout phase from prior learnings"""
        patterns = self.mem.get_relevant_patterns(
            f"File discovery for: {task_id}", limit=3
        )
        return self._format_as_prompt(patterns)
    
    # PLAN PHASE
    def record_plan_decision(self, plan_id: str, decision: str, why: str):
        """Store planning decisions with rationale"""
        self.mem.add_planning_decision(
            task=plan_id,
            decision=decision,
            rationale=why
        )
    
    def get_plan_lessons(self, task_type: str) -> str:
        """Get lessons learned from past planning"""
        patterns = self.mem.get_relevant_patterns(
            f"Planning patterns for {task_type}", limit=5
        )
        return self._format_as_prompt(patterns)
    
    # BUILD PHASE
    def record_implementation_pattern(self, framework: str, pattern: str):
        """Store successful implementation patterns"""
        self.mem.memory.add(
            messages=[{
                "role": "system",
                "content": f"{framework}: {pattern}"
            }],
            user_id=self.user,
            metadata={
                "type": "implementation_pattern",
                "phase": "build",
                "framework": framework,
                "confidence": 0.9
            }
        )
    
    def record_build_failure(self, error: str, solution: str):
        """Store failure patterns and solutions"""
        self.mem.memory.add(
            messages=[{
                "role": "system",
                "content": f"Error: {error}\nSolution: {solution}"
            }],
            user_id=self.user,
            metadata={
                "type": "failure_recovery",
                "phase": "build",
                "confidence": 0.85,
                "priority": "high"
            }
        )
    
    def _format_as_prompt(self, results: list) -> str:
        """Convert memory results to usable prompt text"""
        if not results:
            return ""
        return "\n".join([f"- {r['memory']}" for r in results])
```

**Deliverables:**
- Memory manager for all 3 phases
- Per-phase query methods
- Failure/success pattern recording
- Prompt injection utilities

### Phase 3: Optimization (Week 4)

**Objective:** Advanced features: decay, confidence, custom rules

```python
# Implementation includes:
# 1. Confidence scoring system (0.4-0.95 scale)
# 2. Memory decay mechanisms (automatic relevance reduction)
# 3. Custom extraction rules (what to remember per phase)
# 4. Memory consolidation triggers
# 5. Analytics: Most useful memories, decay rates
# 6. Privacy controls: Memory deletion, archiving
```

---

## Part 7: Quick Reference - Memory Types by Framework Phase

### Scout Phase Memories

```python
HIGH_VALUE = [
    "File patterns for specific task types",
    "Semantic search strategies that worked",
    "Code structure insights (module relationships)",
    "Tool capabilities (what works, what doesn't)"
]

LOW_VALUE = [
    "Individual file paths (changes every project)",
    "Full file contents",
    "Transient conversation",
    "Generic search queries"
]

STORAGE_RULE = "Store patterns & learnings, not data"
EXPIRATION = "Keep indefinitely; update if framework changes"
```

### Plan Phase Memories

```python
HIGH_VALUE = [
    "Planning decisions & trade-offs",
    "Architecture patterns chosen & why",
    "Failed planning approaches",
    "Framework/tool selection reasoning",
    "Risk assessments & mitigations"
]

LOW_VALUE = [
    "Step-by-step plans (too detailed, changes)",
    "Draft planning notes",
    "Brainstorm ideas (not decisions)",
    "Full meeting transcripts"
]

STORAGE_RULE = "Store decisions, not plans"
EXPIRATION = "Keep for task lifetime; review after task"
```

### Build Phase Memories

```python
HIGH_VALUE = [
    "Code patterns that worked",
    "Implementation approaches per framework",
    "Common errors & how to fix them",
    "Performance optimizations discovered",
    "Debugging techniques that worked"
]

LOW_VALUE = [
    "Individual code snippets",
    "Line-by-line implementation steps",
    "Syntax/API reference (LLM knows this)",
    "Build output logs"
]

STORAGE_RULE = "Store insights, not code"
EXPIRATION = "Keep indefinitely; refresh if framework updates"
```

---

## Part 8: Implementation Checklist

### Setup
- [ ] Initialize Mem0 with direct API (no MCP)
- [ ] Configure embeddings (OpenAI or local)
- [ ] Set up vector store (SQLite for MVP, Qdrant for prod)
- [ ] Create memory schema with metadata
- [ ] Set confidence thresholds per memory type

### Integration
- [ ] Add memory recording to Scout phase
- [ ] Add memory retrieval to Planning phase
- [ ] Add memory recording to Build phase
- [ ] Implement failure → learning pipeline
- [ ] Create success → pattern documentation

### Optimization
- [ ] Set up expiration dates for session memories
- [ ] Implement confidence decay mechanism
- [ ] Create memory consolidation triggers
- [ ] Add memory analytics/reporting
- [ ] Set up memory pruning (remove low-value)

### Testing
- [ ] Memory retrieval accuracy (>80%)
- [ ] Latency benchmarks (<200ms retrieval)
- [ ] Consolidation works (duplicates merge)
- [ ] Expiration works (memories auto-remove)
- [ ] Privacy controls work (selective deletion)

### Documentation
- [ ] Memory types & what to store guide
- [ ] Integration examples per phase
- [ ] Troubleshooting guide
- [ ] Best practices & anti-patterns
- [ ] Query examples & patterns

---

## Part 9: Key Sources & Further Reading

### Official Documentation
- [Mem0 Official Site](https://mem0.ai/)
- [Mem0 GitHub Repository](https://github.com/mem0ai/mem0)
- [Mem0 Documentation](https://docs.mem0.ai/integrations)
- [Mem0 Framework Integrations](https://docs.mem0.ai/open-source/features/async-memory)

### Research & Performance
- [Mem0 Research Paper - ArXiv](https://arxiv.org/abs/2504.19413)
- [Mem0 Scalability Research](https://mem0.ai/research)
- [Mem0 vs RAG Comparison](https://www.walturn.com/insights/enhancing-ai-applications-with-mem0-and-rag)
- [Building Production AI Agents with Mem0](https://medium.com/@EleventhHourEnthusiast/mem0-building-production-ready-ai-agents-with-scalable-long-term-memory-9c534cd39264)

### Integration Guides
- [Mem0 + LangGraph Integration](https://blog.futuresmart.ai/ai-agents-memory-mem0-langgraph-agent-integration)
- [Mem0 + LangChain Integration](https://blog.futuresmart.ai/integrating-mem0-with-langchain)
- [AutoGen + Mem0 Memory](https://microsoft.github.io/autogen/0.2/docs/ecosystem/mem0/)
- [Mem0 + Redis for Scalability](https://redis.io/blog/smarter-memory-management-for-ai-agents-with-mem0-and-redis/)

### Best Practices
- [Controlling Memory Ingestion](https://docs.mem0.ai/cookbooks/essentials/controlling-memory-ingestion)
- [Memory Types in Mem0](https://docs.mem0.ai/core-concepts/memory-types)
- [Mem0's add() Operation Guide](https://mem0.ai/blog/understanding-mem0-s-add()-operation)
- [AI Agent Memory: What, Why, How](https://mem0.ai/blog/memory-in-agents-what-why-and-how)

### Case Studies
- [AWS & Mem0 Partnership - Strands](https://mem0.ai/blog/aws-and-mem0-partner-to-bring-persistent-memory-to-next-gen-ai-agents-with-strands)
- [Building Agentic AI with CrewAI, Mem0, and Prompt Caching](https://medium.com/@jegannathrajangam_59720/building-an-agentic-ai-system-with-crewai-mem0-prompt-caching-strong-guardrails-langfuse-and-036cacea9c16)
- [AWS ElastiCache + Neptune Analytics + Mem0](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptucse-analytics/)

---

## Conclusion

Mem0 provides the **persistent behavioral memory** that complements Gemini File Search's **code discovery capabilities**. By storing high-value learnings (decisions, patterns, failures) while avoiding low-value data (speculation, duplicates, transient info), the Scout/Plan/Build framework can become increasingly effective across iterations.

**Key Takeaway:** Mem0 is not a code search tool—it's an agent learning system. Use Gemini File Search for "what code exists?" and Mem0 for "what did we learn about how to work with this codebase?"

---

**Generated:** November 29, 2025  
**Framework:** Scout Plan Build MVP  
**Integration Type:** Direct API (no MCP)  
**Status:** Ready for Phase 1 Implementation
