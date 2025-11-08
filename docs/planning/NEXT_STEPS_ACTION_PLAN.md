# 🎯 Next Steps Action Plan

## Immediate Actions (TODAY - 2-3 hours)

### ✅ 1. MIT License Added
```bash
git add LICENSE
git commit -m "Add MIT License for open source release"
```

### 🔴 2. Fix Critical Security Vulnerabilities (1 hour)

#### Command Injection in scout_simple.py
```python
# Line 42 - BEFORE (vulnerable):
grep_result = subprocess.run(
    ["grep", "-r", "-l", keyword, ".", "--include=*.py"],
    ...
)

# AFTER (secure):
import shlex
if not keyword or any(char in keyword for char in ['$', '`', ';', '|', '&', '>', '<']):
    return []  # Reject dangerous input
keyword_safe = shlex.quote(keyword)
grep_result = subprocess.run(
    ["grep", "-r", "-l", "--", keyword_safe, ".", "--include=*.py"],
    ...
)
```

#### Webhook Authentication
```python
# Add to webhook handler:
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify GitHub webhook signature."""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

# In webhook handler:
if not verify_webhook_signature(request.body, request.headers['X-Hub-Signature-256'], WEBHOOK_SECRET):
    return 401  # Unauthorized
```

### 📁 3. README Consolidation (30 minutes)

```bash
# Delete obsolete files
rm ai_docs/scout/README.md
rm specs/README_SKILLS_DELIVERABLES.md

# Rename non-standard READMEs
git mv scripts/README_WORKTREE_SYSTEM.md scripts/README.md
git mv archive/research/README_WORKFLOW_ANALYSIS.md archive/research/README.md

# Merge adws/README.md content into main README
# Then replace adws/README.md with minimal version (80 lines)
```

---

## This Week Actions (10-15 hours)

### 🚀 4. Agents SDK Integration - THE GAME CHANGER!

**Good News**: We already have COMPLETE documentation!
- `ai_docs/architecture/AGENTS_SDK_ARCHITECTURE.md` - Full architecture (1,764 lines!)
- `specs/agents-sdk-implementation-plan.md` - 8-week implementation plan
- `docs/AGENTS_SDK_INTEGRATION.md` - Integration guide

#### Quick Win Implementation (4-6 hours)

Replace subprocess.Popen() with proper Agents SDK:

**BEFORE (subprocess hack):**
```python
# adws/adw_sdlc.py:38-81 - Current 30-line solution
test_proc = subprocess.Popen(["python", "adws/adw_test.py", "--no-commit"])
review_proc = subprocess.Popen(["python", "adws/adw_review.py", "--no-commit"])
test_proc.wait(); review_proc.wait()
```

**AFTER (Agents SDK):**
```python
from anthropic import Agent, AgentSession
from agents_sdk import AgentOrchestrator, ParallelExecutor

# Initialize with memory persistence
orchestrator = AgentOrchestrator(
    memory_backend="serena",  # Persistent memory via Serena MCP!
    state_backend="sqlite"
)

# Launch parallel agents with proper coordination
async def run_parallel_qa():
    agents = await orchestrator.launch_parallel([
        Agent("test", memory=True),
        Agent("review", memory=True),
        Agent("document", memory=True)
    ])

    results = await orchestrator.wait_all(agents)
    return orchestrator.aggregate(results)
```

#### Benefits of Agents SDK + Serena MCP:
- **Persistent Memory**: Scouts remember previous discoveries!
- **True Parallelism**: Not just subprocess, real agent coordination
- **Error Recovery**: Built-in retry logic and fallbacks
- **Progress Streaming**: Real-time updates
- **Inter-Agent Communication**: Agents can share discoveries

### 🧠 5. Serena MCP Integration (2-3 hours)

**Best Practice**: Use Serena for BOTH main agent AND scouts!

```python
# Enhanced parallel scout with memory
class SmartScout:
    def __init__(self):
        self.memory = SerenaMCP()

    async def scout(self, task: str):
        # Check if we've scouted this before
        prior_knowledge = await self.memory.recall(task)

        if prior_knowledge:
            print(f"📚 Recalling prior discovery: {prior_knowledge}")

        # Launch scouts with memory
        scouts = await self.launch_squadron(task, prior_knowledge)

        # Save discoveries for future
        await self.memory.store(task, scouts.aggregate())

        return scouts

# Scouts now LEARN and REMEMBER across sessions!
```

### 🏗️ 6. Create Missing Critical READMEs (2-3 hours)

Priority order from haiku scouts:
1. `/docs/README.md` - Master documentation index (17 files need organizing!)
2. `/agents/README.md` - Explain this confusing directory name
3. `/ai_docs/analyses/README.md` - Index for 7 analysis docs
4. `/ai_docs/reference/README.md` - Quick reference guides

---

## Next Week Actions (15-20 hours)

### 7. Full Agents SDK Implementation

Following the 8-week plan from `specs/agents-sdk-implementation-plan.md`:

**Phase 1: Basic Orchestrator (Week 1-2)**
```
agents_sdk/
├── core/
│   ├── session.py      # AgentSession with memory
│   ├── orchestrator.py # Parallel coordination
│   └── response.py     # Enhanced responses
├── memory/
│   ├── serena.py       # Serena MCP backend
│   └── inmemory.py     # Fallback
└── state/
    ├── sqlite.py       # Persistent state
    └── json.py         # Current compatibility
```

**Phase 2: Parallel Execution (Week 3-4)**
- Replace ALL subprocess.Popen() calls
- Add progress streaming
- Implement retry logic
- Add inter-agent communication

### 8. CI/CD Pipeline (4 hours)

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=adws --cov-report=term
      - run: python -m mypy adws/
      - run: python -m black --check adws/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install bandit
      - run: bandit -r adws/
```

---

## Decision Points

### Should We Add Agents SDK Before Release?

**YES! But staged approach:**

1. **Quick Win (This Week)**:
   - Basic SDK wrapper around current subprocess
   - Add Serena MCP for memory
   - Test with parallel scouts
   - 4-6 hours work

2. **Full Implementation (4-6 weeks)**:
   - Complete SDK as per 8-week plan
   - Full parallel orchestration
   - Inter-agent communication
   - Progress streaming

### Serena MCP Usage

**Best Practice**: Use EVERYWHERE!
- ✅ Main orchestrator agent
- ✅ Individual scout agents
- ✅ Plan/Build/Test/Review agents
- ✅ Session persistence

This creates a **learning system** where every run improves future runs!

---

## Release Timeline with SDK

### Option A: Release v0.1.0 with Basic SDK (2 weeks)
- Week 1: Security fixes + Basic SDK wrapper
- Week 2: Testing + Documentation
- **Pros**: Earlier release, SDK foundation in place
- **Cons**: Not full SDK capabilities

### Option B: Release v1.0.0 with Full SDK (6 weeks)
- Week 1-2: Security + Basic SDK
- Week 3-4: Full parallel orchestration
- Week 5: Testing + Documentation
- Week 6: Beta testing
- **Pros**: Complete solution, true agent framework
- **Cons**: Longer wait

**Recommendation**: Option A - Release v0.1.0 with basic SDK, then v1.0.0 with full implementation

---

## The Vision: What SDK + Serena Enables

```python
# The future of Scout→Plan→Build with Agents SDK + Serena

# Scouts that learn and remember
smart_scout = SmartScout(memory="serena")
files = await smart_scout.discover("authentication",
    recall_previous=True,  # Remember past discoveries!
    learn_patterns=True    # Learn codebase patterns!
)

# Plans that improve over time
planner = SmartPlanner(memory="serena")
spec = await planner.create(
    task="authentication",
    learn_from_feedback=True,  # Gets better each time!
    recall_similar_plans=True  # Reuse successful patterns!
)

# Parallel execution with coordination
orchestrator = AgentOrchestrator(memory="serena")
results = await orchestrator.execute_parallel(
    agents=["test", "review", "document", "security-audit"],
    share_discoveries=True,  # Agents share findings!
    aggregate_insights=True  # Combine learnings!
)

# System that gets SMARTER with every run!
```

---

## Immediate Next Commands

```bash
# 1. Add MIT License (✅ DONE)
git add LICENSE
git commit -m "Add MIT License"

# 2. Fix security (DO NOW)
# Edit scout_simple.py line 42
# Add webhook authentication

# 3. Start Agents SDK wrapper
mkdir -p agents_sdk/core
touch agents_sdk/__init__.py
# Create basic wrapper around subprocess

# 4. Test Serena MCP
# Document how to enable/configure Serena

# 5. Consolidate READMEs
rm ai_docs/scout/README.md
git mv scripts/README_WORKTREE_SYSTEM.md scripts/README.md
```

---

## Key Insight

**We're closer than we thought!** The Agents SDK architecture is already fully documented. We just need to implement it. Combined with Serena MCP for persistent memory, this transforms the framework from "subprocess orchestration" to a true **learning, intelligent agent system**.

The parallel scouts + SDK + Serena = **Agents that learn and improve with every run!**

---

*With gratitude to indydevdan (tacticalengineering.com) for the foundational principles that made this possible.*