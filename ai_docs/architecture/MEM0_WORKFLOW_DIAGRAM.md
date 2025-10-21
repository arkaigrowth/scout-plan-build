# Mem0 Integration Workflow Diagram

## Scout → Plan → Build Flow with Memory Enhancement

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SCOUT PHASE                                  │
└─────────────────────────────────────────────────────────────────────┘

User Request: "Add JWT authentication"
     │
     ▼
┌─────────────────────────────────────────┐
│  PRE-SCOUT RECALL                        │
│  memory.search(                          │
│    query="Add JWT authentication",       │
│    category="file_patterns"              │
│  )                                       │
└─────────────────────────────────────────┘
     │
     │ Returns:
     │  - adws/adw_modules/validators.py (90% confidence)
     │  - adws/adw_modules/state.py (85% confidence)
     │  - "Auth tasks typically involve validation & state"
     │
     ▼
┌─────────────────────────────────────────┐
│  SCOUT EXECUTION                         │
│  - Spawn 4 parallel agents               │
│  - Search codebase                       │
│  - Return file list                      │
└─────────────────────────────────────────┘
     │
     │ Scout Results:
     │  files: [validators.py, state.py, exceptions.py, ...]
     │  key_findings: "Found auth-related modules"
     │
     ▼
┌─────────────────────────────────────────┐
│  POST-SCOUT LEARN                        │
│  memory.add(                             │
│    messages="Auth task → validators.py", │
│    category="file_patterns",             │
│    metadata={files: [...]}               │
│  )                                       │
└─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                         PLAN PHASE                                   │
└─────────────────────────────────────────────────────────────────────┘

Scout Results + Issue Description
     │
     ▼
┌─────────────────────────────────────────┐
│  PRE-PLAN RECALL                         │
│  memory.search(                          │
│    query="JWT authentication",           │
│    category="design_decisions",          │
│    issue_type="feature"                  │
│  )                                       │
└─────────────────────────────────────────┘
     │
     │ Returns:
     │  - "Use Pydantic for input validation" (92% confidence)
     │  - "JWT patterns: passport.js library" (78% confidence)
     │  - "Always validate tokens server-side"
     │
     ▼
┌─────────────────────────────────────────┐
│  PLAN GENERATION                         │
│  - Analyze requirements                  │
│  - Design architecture                   │
│  - Create 8-section plan                 │
│  - Save to specs/                        │
└─────────────────────────────────────────┘
     │
     │ Plan File: specs/issue-001-adw-ext001-jwt-auth.md
     │  - Architecture: Use Pydantic validators
     │  - Risks: Token expiration handling
     │  - Implementation: 5 steps
     │
     ▼
┌─────────────────────────────────────────┐
│  POST-PLAN LEARN                         │
│  memory.add(                             │
│    messages="Architecture: Pydantic...", │
│    category="design_decisions",          │
│    metadata={issue_type: "feature"}      │
│  )                                       │
│  memory.add(                             │
│    messages="Risk: token expiration...", │
│    category="design_decisions",          │
│    tags=["risk", "mitigation"]           │
│  )                                       │
└─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                         BUILD PHASE                                  │
└─────────────────────────────────────────────────────────────────────┘

Plan File: specs/issue-001-adw-ext001-jwt-auth.md
     │
     ▼
┌─────────────────────────────────────────┐
│  BUILD EXECUTION                         │
│  - Implement plan                        │
│  - Create/modify files                   │
│  - Run tests                             │
│  - Generate build report                 │
└─────────────────────────────────────────┘
     │
     │ Build Report: ai_docs/build_reports/jwt-auth-build-report.md
     │  - Files changed: validators.py, state.py, auth.py
     │  - Libraries used: pydantic, jwt, bcrypt
     │  - Tests: 15 passed
     │
     ▼
┌─────────────────────────────────────────┐
│  POST-BUILD LEARN                        │
│  memory.add(                             │
│    messages="JWT auth: pydantic, jwt",   │
│    category="implementation_patterns",   │
│    metadata={files: [...], tags: [...]}  │
│  )                                       │
└─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING                                  │
└─────────────────────────────────────────────────────────────────────┘

Exception Raised: TokenLimitError
     │
     ▼
┌─────────────────────────────────────────┐
│  ON-ERROR LEARN                          │
│  memory.add(                             │
│    messages="TokenLimitError: set...",   │
│    category="error_resolutions",         │
│    resolution="Set MAX_OUTPUT_TOKENS"    │
│  )                                       │
└─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                    CROSS-SESSION RECALL                              │
└─────────────────────────────────────────────────────────────────────┘

Next Task (1 week later): "Add OAuth2 support"
     │
     ▼
┌─────────────────────────────────────────┐
│  PRE-SCOUT RECALL                        │
│  memory.search(                          │
│    query="Add OAuth2 support",           │
│    category="file_patterns"              │
│  )                                       │
└─────────────────────────────────────────┘
     │
     │ Returns (learns from JWT task):
     │  - adws/adw_modules/validators.py (95% confidence)
     │  - adws/adw_modules/auth.py (90% confidence) ← NEW from JWT task
     │  - "Auth tasks involve validators, state, and auth modules"
     │
     ▼
Faster, smarter workflow with learned context!
```

## Memory Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Memory Storage Layer                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Qdrant Vector DB: /tmp/qdrant/                                 │
│  ├─ Collection: adw_memories                                     │
│  ├─ Embeddings: text-embedding-ada-002 (1536 dims)              │
│  └─ Vectors: ~5,400 memories/year                               │
│                                                                   │
│  SQLite History: ~/.mem0/history.db                             │
│  └─ Transaction log + metadata                                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            │ Read/Write
                            │
┌──────────────────────────────────────────────────────────────────┐
│                  MemoryManager (Singleton)                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  • Lazy initialization                                           │
│  • Graceful degradation                                          │
│  • Error handling (never crashes)                                │
│  • Metrics tracking                                              │
│                                                                   │
│  Methods:                                                         │
│    add(messages, user_id, agent_id, metadata)                   │
│    search(query, filters, threshold)                            │
│    get_all(user_id, filters)                                    │
│    delete(memory_id)                                             │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            │ Hook Calls
                            │
┌──────────────────────────────────────────────────────────────────┐
│                    Memory Hooks Layer                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Pre-Execution Hooks (Recall):                                   │
│    pre_scout_recall() → Suggest files                           │
│    pre_plan_recall() → Suggest patterns                         │
│                                                                   │
│  Post-Execution Hooks (Learn):                                   │
│    post_scout_learn() → Save file discoveries                   │
│    post_plan_learn() → Save design decisions                    │
│    post_build_learn() → Save implementation patterns            │
│                                                                   │
│  Error Hooks (Learn):                                            │
│    on_error_learn() → Save error resolutions                    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            │ Integrated Into
                            │
┌──────────────────────────────────────────────────────────────────┐
│                  ADW Workflow Layer                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Slash Commands:                                                  │
│    /scout → pre_scout_recall() + post_scout_learn()            │
│    /plan_w_docs → pre_plan_recall() + post_plan_learn()        │
│    /build_adw → post_build_learn()                             │
│                                                                   │
│  Workflow Scripts:                                               │
│    adw_plan.py → Hooks integrated                               │
│    adw_build.py → Hooks integrated                              │
│    exception handlers → on_error_learn()                        │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Memory Scoping Strategy

```
┌────────────────────────────────────────────────────────────────────┐
│  Project Scope (user_id = "project_scout_mvp")                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Workflow Scope (agent_id = "adw_scout")                    │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │                                                             │  │
│  │  ┌───────────────────────────────────────────────────┐    │  │
│  │  │  Session Scope (run_id = "ext001")                │    │  │
│  │  ├───────────────────────────────────────────────────┤    │  │
│  │  │                                                    │    │  │
│  │  │  Memory: "Task X → files [a.py, b.py]"           │    │  │
│  │  │  Metadata: {category: "file_patterns", ...}      │    │  │
│  │  │                                                    │    │  │
│  │  └───────────────────────────────────────────────────┘    │  │
│  │                                                             │  │
│  │  ┌───────────────────────────────────────────────────┐    │  │
│  │  │  Session Scope (run_id = "ext002")                │    │  │
│  │  │  Memory: "Task Y → files [c.py, d.py]"           │    │  │
│  │  └───────────────────────────────────────────────────┘    │  │
│  │                                                             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Workflow Scope (agent_id = "adw_plan")                     │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │  Memory: "Design pattern: Use Pydantic"                    │  │
│  │  Metadata: {category: "design_decisions", ...}             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘

Search Behavior:
  • search(user_id="project_scout_mvp") → All project memories
  • search(agent_id="adw_scout") → Only scout workflow memories
  • search(run_id="ext001") → Only session-specific memories
  • Combine filters for precise scoping
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────────┐
│  Memory Operation Latency (Local Qdrant)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  add():      100-300ms  (OpenAI embed + Qdrant write)          │
│  search():   50-150ms   (OpenAI embed + Qdrant query)          │
│  get_all():  20-50ms    (Qdrant scan only, no embed)           │
│  delete():   10-30ms    (Qdrant delete only)                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Workflow Phase Impact                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Scout Phase:                                                    │
│    Baseline:     60s (parallel agents)                         │
│    + Memory:     60.4s (1 recall + 1 learn = 400ms)           │
│    Overhead:     0.7%                                          │
│                                                                  │
│  Plan Phase:                                                    │
│    Baseline:     150s (analysis + design)                      │
│    + Memory:     150.4s (1 recall + 1 learn = 400ms)          │
│    Overhead:     0.3%                                          │
│                                                                  │
│  Build Phase:                                                   │
│    Baseline:     120s (implement + tests)                      │
│    + Memory:     120.2s (1 learn = 200ms)                     │
│    Overhead:     0.2%                                          │
│                                                                  │
│  Total Workflow:                                                │
│    Baseline:     330s (5.5 minutes)                           │
│    + Memory:     331s (5.5 minutes)                           │
│    Overhead:     0.3% (effectively zero)                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## ROI Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│  Value Delivered                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Week 1 (Initial Learning):                                     │
│    Recall accuracy: 30-40%                                      │
│    Time saved: Minimal (learning phase)                        │
│                                                                  │
│  Month 1 (Pattern Recognition):                                 │
│    Recall accuracy: 60-70%                                      │
│    Time saved: 10-20% on similar tasks                        │
│    - Faster file discovery (skip redundant search)            │
│    - Pattern suggestions reduce design time                    │
│                                                                  │
│  Month 3+ (Mature Knowledge):                                   │
│    Recall accuracy: 75-85%                                      │
│    Time saved: 20-30% on related tasks                        │
│    - Cross-task learning (auth → OAuth2 → SSO)                │
│    - Error prevention (remember past failures)                 │
│    - Decision consistency (follow established patterns)        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Cost Analysis (per year, 1,200 tasks)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OpenAI Embeddings:  $0.09/year                                │
│  Storage:            5.4 MB (negligible)                       │
│  Time Investment:    2-3 days initial setup                    │
│                                                                  │
│  Time Saved:         20-30% on 50% of tasks                    │
│                      = 300-450 hours/year                      │
│                                                                  │
│  ROI: ~300x return on investment                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

**Diagram Created**: 2025-10-20
**For Architecture**: Mem0 Integration
**See Also**: MEM0_INTEGRATION_ARCHITECTURE.md
