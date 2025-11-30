# Gemini File Search for Repo Indexing

**Source**: Chad
**Topic**: Gemini File Search Repo Indexing
**Author**: Chad
**Date Added**: 2025-11-28

---
**Draft architecture for Scout–Plan–Build + Claude Code**

_Last updated: 2025-11-28_

---

## 1. Purpose & high-level goal

This document proposes a **minimal, non-brittle architecture** for using **Gemini File Search** as the primary codebase index, while keeping **Claude Code** (and your Scout–Plan–Build agents) as the main “brain” for reasoning and editing.

Goals:

- **Frictionless dev experience**: you stay in your normal git + editor + Claude Code flow; Gemini handles indexing.  
- **Non-brittle**: no hand-rolled vector DBs, minimal custom infra, graceful failure modes.  
- **Modular & extensible**: can grow into multi-repo, multi-agent setups without rewrites.  
- **Agentic-native**: retrieval is exposed as a **tool primitive** that any agent (Scout, Planner, Builder, Tester, Reviewer) can call.

This is written so you can hand it directly to an agent (Claude Code or SPB “Orchestrator”) as an implementation spec.

---

## 2. Background: what Gemini File Search actually gives you

### 2.1 File Search in a nutshell

**Gemini File Search** is a fully managed RAG service built into the Gemini API:

- You create a **File Search Store**.
- You upload files (code, docs, config) to the store.
- Google handles **chunking, embeddings, storage, vector search, and context assembly**. citeturn0search0turn0search5turn0search16  
- At query time, Gemini retrieves relevant chunks and can inject them directly into the model’s context, with citations. citeturn0search1turn0news40  

Key properties relevant for code:

- Supports general text formats (TXT, JSON, etc.) which is enough for source code files. citeturn0news40turn0search27  
- Storage and query‑time embeddings are currently **free**; you pay **$0.15 per 1M tokens for initial indexing**. citeturn0search3turn0search16turn0news40  
- There’s a **simple public API** (`FileSearchStores` + `media.uploadToFileSearchStore`) and demos (e.g. “Ask the Manual” in AI Studio) that show end‑to‑end examples. citeturn0search5turn0search14turn0search27  

Multiple practitioners are already replacing multi‑table RAG stacks (chunk table, embedding table, doc table, etc.) with a single File Search Store, drastically simplifying infra. citeturn0search4turn0search6turn0search12turn0search18  

### 2.2 RAG on codebases: what the literature says

Recent work on RAG for software development and large codebases converges on a few themes: citeturn1search7turn1search10turn1search13turn1search17turn1search23  

1. **Retrieval quality, not model size, is usually the bottleneck**.  
2. **Structure‑aware chunks** (functions/classes, not arbitrary windows) are more useful for code editing.  
3. **Hybrid retrieval** (symbolic / grep + semantic) beats pure embedding search.  
4. **Incremental indexing** (git‑aware, update-on-change) avoids stale context and brittleness.  
5. You should **evaluate retrieval** with a small benchmark, not just vibes.

We’ll borrow these ideas but let Gemini take care of the embedding/indexing heavy lifting.

### 2.3 Agentic engineering primitives we’ll lean on

Anthropic and others describe agentic systems as “LLMs augmented with tools, retrieval, and memory,” and emphasize **simple, composable patterns** over over‑frameworking. citeturn1search9turn1search0turn1search19turn1search18turn1search15  

We’ll explicitly treat “code search via Gemini File Search” as a **first‑class tool primitive** that can be composed in:

- **Prompt chaining** (Scout → Plan → Build → Test → Review)  
- **Routing** (only call search when needed)  
- **Orchestrator/worker pattern** (a small orchestrator decides when workers call search).

---

## 3. Design principles

1. **Single Source of Truth (SSOT)**:  
   - Git repo(s) remain the **truth**. Gemini’s File Search Store is a **cache/index view**, never an authority.  

2. **Simplicity over cleverness**:  
   - Offload chunking/embeddings/storage to File Search. No homebrew vector DB, no multi-service zoo unless strictly necessary.  

3. **Non-brittle by design**:  
   - Treat File Search as **optional but powerful**:
     - If it’s slow/down, fall back to **local grep / language server**.  
     - Never make the pipeline “all or nothing” on remote retrieval.  

4. **Tool-first, model-second**:  
   - Gemini = **index + retrieval**.  
   - Claude = **planner/actor** that consumes retrieved snippets and edits code.  

5. **Evaluated, not assumed**:  
   - Build a tiny **code RAG eval set** early (tasks → expected files/snippets) and keep it under version control.  

---

## 4. Target UX: “Claude Code, but with a superpower”

From your POV as a dev:

- You run Claude Code (or SPB CLI) in a repo.  
- When an agent needs context (“Where is JWT auth implemented?”), it calls a **`code_search` tool**.  
- Under the hood, `code_search` hits your **Gemini File Search Store** for that repo and returns ranked code snippets + filepaths.  
- Claude then reasons over those snippets and emits **surgical patches**, not “rewrite the whole file” changes (following Anthropic’s agentic coding best practices). citeturn1search1turn0search24  

The entire indexing lifecycle is automated via CI / git hooks; you never manually “rebuild the index”.

---

## 5. MVP architecture

### 5.1 Component overview

**Core components:**

1. **File Search Store (Gemini)**  
   - One store per “project domain” (e.g. `spb-core`, `client-x-backend`, etc.), or per repo if that’s simpler. citeturn0search5turn0search0  

2. **Indexer service / script**  
   - Git‑aware job that:
     - Detects changed files.  
     - Uploads them to the correct File Search Store with metadata (repo, path, language, commit hash).  
   - Triggered by CI, or a local CLI command (`spb index`).

3. **Code Search Tool (orchestrator microservice)**  
   - Thin HTTP (or MCP) service that:
     - Accepts natural language queries + filters.  
     - Calls Gemini File Search API.  
     - Normalizes results into a stable JSON shape for agents.

4. **SPB/Claude harness**  
   - Your existing **Scout–Plan–Build loop** extended with a `code_search` tool definition and prompt instructions on *when* and *how* to use it.

5. **Logging + Eval harness (v1.5)**  
   - Lightweight logging of queries and retrieved filepaths.  
   - Small YAML/JSON dataset for retrieval evaluation.

### 5.2 High-level data flow

```text
+--------------------+           +--------------------------+
|  Git repo(s)       |           |  Gemini File Search      |
|  (SSOT)            |           |  Store(s)                |
+----------+---------+           +------------+-------------+
           |                                   ^
           | (CI / CLI: diff-based upload)     |
           v                                   |
+-------------------------+   queries   +------|---------------+
| Indexer script/service  +-----------> | File Search API     |
| - detect changes        |            | - vector retrieval   |
| - upload code files     |            | - chunking/embeds    |
+------------+------------+            +-----------+----------+
             |                                     |
             |                                     |
             v                                     |
+------------------------------+                  |
|  Code Search Tool (HTTP/MCP) | <----------------+
|  - normalize results         |
|  - apply repo/path filters   |
+--------------+---------------+
               |
               | tool calls
               v
+------------------------------+
|  SPB / Claude Code harness   |
|  - Scout / Planner / Builder |
|  - uses code_search tool     |
+------------------------------+
```

---

## 6. Indexing pipeline (MVP spec)

### 6.1 Store layout

**Option A (simple, recommended initially)**  
- 1 File Search Store per repo:
  - `spb-repo-store`  
  - `clientX-backend-store`  
- Metadata on each document:
  - `repo_name`  
  - `rel_path` (e.g. `src/agents/orchestrator.py`)  
  - `language` (`python`, `ts`, `yaml`, etc.)  
  - `commit_sha` (last indexed commit)

**Option B (for later)**  
- 1 Store per “domain” spanning multiple repos (e.g. “Catsy AI infra”).  
- Extra metadata: `service`, `layer` (api/domain/infra), `sensitivity`.

Start with **Option A** to avoid cross-repo overreach.

### 6.2 What to index

Default include:

- `src/**`, `app/**`, `lib/**`, `services/**`, `config/**`, `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.md` (for design docs).  

Default exclude:

- `node_modules`, `.git`, `.venv`, `dist`, `build`, compiled artifacts, large binaries.  

You can encode this as a `file_search.include` / `file_search.exclude` section in a repo config file, e.g. `SPB_RAG.yaml`.

### 6.3 Incremental indexing (git-aware)

**Trigger**:  

- CI job on `main` and/or `develop` branches, plus an optional local CLI (`spb index`) for experimental branches.

**Algorithm sketch:**

1. Determine changed files since last indexed commit:
   - Store last indexed `commit_sha` in a small config file or in the File Search Store metadata.  
   - Use `git diff --name-only <last_sha> HEAD` to list candidate files.  
2. Filter with include/exclude rules.  
3. For each remaining file:
   - Read file content.  
   - Call `media.uploadToFileSearchStore` to upload/update a document:
     - Use a deterministic document ID (e.g. hash of repo + path) so re‑uploads overwrite. citeturn0search5turn0search19turn0search25  
     - Attach metadata: repo, path, language, commit_sha.  
4. Update “last indexed commit” marker.

This keeps your index aligned with git without ever “rebuilding the world” unless you want to.

### 6.4 Failure handling

To keep it non-brittle:

- If upload fails for a file:
  - Log + continue; don’t fail the entire CI job unless a threshold (e.g. >20% of files) fails.  
- If **File Search API** is temporarily unavailable:
  - Mark the CI job as **warning** rather than hard fail, so deploys aren’t blocked.  
- Periodic **full resync** (e.g. weekly) can be a separate job that:
  - Re-sends all in-scope files, in batches, when pipeline load is low.

---

## 7. Code Search Tool: interface and behavior

### 7.1 Tool contract (conceptual)

Define a single generic tool (HTTP endpoint or MCP tool):

- **Name**: `code_search`  
- **Input**:
  - `query: string` – natural language or code-like query.  
  - `repo: string` – logical repo ID (`"spb-core"`, `"client-x-backend"`).  
  - `path_prefix?: string` – optional subdir filter (`"src/agents"`).  
  - `language?: string` – optional language filter.  
  - `k?: int` – max number of snippets (default 8–12).  
- **Output** (array of “evidence” objects):
  - `repo: string`  
  - `rel_path: string`  
  - `language: string`  
  - `score: float` (File Search ranking score if available)  
  - `snippet: string` (code snippet)  
  - `start_line?: int`  
  - `end_line?: int`  
  - `metadata?: object` (e.g. `commit_sha`, tags)

### 7.2 Implementation outline

1. **Normalize repo → File Search Store ID**  
   - e.g. `spb-core` → `projects/.../locations/.../fileSearchStores/spb-core-store`.

2. **Build query for File Search API**  
   - Use the natural language `query` as-is.  
   - Use `repo`, `path_prefix`, `language` as metadata filters if supported, otherwise filter client-side. citeturn0search0turn0search5turn0search19  

3. **Call File Search**  
   - Use the `fileSearch.query` endpoint for text search.  
   - Request top `k` results.

4. **Post-process results**  
   - Slice snippets to a manageable size (e.g. 40–80 lines) keeping function boundaries where possible.  
   - Populate `start_line` / `end_line` if the API exposes offsets; otherwise approximate.

5. **Return normalized JSON**  
   - Designed so Claude tools / MCP can map onto it easily.

### 7.3 Non-brittle fallbacks

If the File Search API call fails or times out:

- Return a structured `error` object, **plus** optional fallback results from:
  - A local **ripgrep** search (`rg "jwt" src/`)  
  - Or a simple text search over a local on-disk cache.
- The Claude tool schema should clearly distinguish:
  - `results: Evidence[]`  
  - `fallback_used: bool`  
  - `error?: string`

Claude’s prompt will tell it to proceed even if `results` is empty (e.g. “If no code_search results are returned, explain the limitation and ask for more precise guidance or fall back to user-provided files”).

---

## 8. Integrating with Scout–Plan–Build (agent patterns)

### 8.1 General agent pattern

Based on Anthropic’s guidance for agentic coding, we want: citeturn1search1turn1search3turn1search24turn1search9turn1search18  

1. **Initializer / Environment Setup**  
   - Loads repo summary, important constraints, and instructions (similar to `GEMINI.md` concepts used with Gemini CLI). citeturn0search9turn0search17  
2. **Scout** – uses `code_search` to gather relevant files/snippets.  
3. **Planner** – writes a concrete plan (files to edit, functions to touch, tests to run).  
4. **Builder** – applies edits patch-by-patch.  
5. **Tester/Reviewer** – runs tests, reviews diffs, and may call `code_search` to verify related usage sites.

### 8.2 Suggested tool usage per phase

- **Scout**  
  - Always allowed to call `code_search`.  
  - Typical queries:
    - “Where is <concept> implemented?”  
    - “Show me the middleware that handles authentication.”  
    - “Find all references to the `JobHunterConfig` type.”

- **Planner**  
  - May call `code_search` when it needs to confirm the scope of impact:
    - “Before refactoring, find all modules importing `legacy_feature_flag`.”

- **Builder**  
  - Should use `code_search` for:
    - Locating the exact function to edit if not already in context.  
    - Finding similar patterns (e.g. “other validators in this codebase”).

- **Tester/Reviewer**  
  - Uses `code_search` to:
    - Find tests to update.  
    - Ensure logging/metrics follow existing patterns.

### 8.3 Prompting guidance for Claude

In your SPB harness prompt, add a section like:

> You have access to a `code_search` tool that queries an up-to-date index of the current repo via Gemini File Search.  
>  
> **When to use it:**  
> - When you need to locate where a feature, type, or behavior is implemented.  
> - When you’re unsure about the impact of a change and want to find related call sites.  
> - When the code visible in this context doesn’t include all relevant definitions.  
>  
> **How to use it:**  
> - Write short, specific queries (e.g. “JWT auth middleware,” “feature flag rollout config”).  
> - Prefer using `path_prefix` when you already know a subsystem (e.g. `src/agents`).  
> - Keep `k` small (5–10) to avoid overloading context.  
>  
> **If the tool fails or returns nothing:**  
> - Explain the limitation.  
> - Ask for more specific guidance or suggest manual search commands (like `rg` or editor search).

---

## 9. Evaluation & non-brittleness guardrails

### 9.1 Tiny retrieval eval set

Borrowing from enterprise RAG-on-code evaluations, you should keep a small dataset that pairs **natural language tasks** with **expected files/snippets**. citeturn1search13turn1search7turn1search10turn1search17  

Example `rag_eval/code_search_spb.json`:

```json
[
  {
    "id": "jwt-middleware",
    "query": "Where do we validate JWTs for API requests?",
    "expected_paths": ["src/auth/jwt_middleware.py"]
  },
  {
    "id": "spb-plan-schema",
    "query": "Find the Pydantic schema that defines the Plan object.",
    "expected_paths": ["src/models/plan.py"]
  }
]
```

Eval harness behavior:

- For each query:
  - Call `code_search` with `k=8`.  
  - Check if any `rel_path` starts with an expected path.  
- Track:
  - **Hit rate @k** (ideal ≥ 80–90% for core tasks).  
  - **Average rank** of first correct result.

Run this periodically (e.g. nightly or on CI for infra changes).

### 9.2 Operational guardrails

1. **Timeouts & retries**  
   - File Search requests should have a sane timeout (e.g. 5–10s) and limited retries.  
2. **Circuit breaker**  
   - If File Search fails repeatedly:
     - Flip a flag in your orchestrator (`file_search_enabled = false`) until health checks pass.  
     - Claude should see this in its system prompt and avoid relying on the tool.  
3. **Token budget discipline**  
   - Limit snippet sizes and `k` to avoid blowing up context windows.  
   - For SPB, ensure each stage’s prompt budget leaves room for retrieved code and artifacts.

---

## 10. Implementation checklist (for Claude / dev agent)

This is the actionable “do list” you can hand to Claude Code or a SPB dev agent.

### Phase 1 – Prototype on a single repo

1. **Create File Search Store**
   - In Google AI Studio or via API, create a File Search Store for one repo (e.g. `spb-core-store`). citeturn0search14turn0search19turn0search15  

2. **Write a local indexing script**
   - CLI script `spb_rag_index.py` that:
     - Reads repo config (include/exclude).  
     - Scans current working tree.  
     - Uploads all in-scope files to the store with metadata. citeturn0search5turn0search10turn0search25  

3. **Build a minimal Code Search Tool**
   - Small FastAPI/Flask app or MCP server exposing `POST /code_search`.  
   - Internally calls File Search, normalizes results.

4. **Add `code_search` tool to SPB harness**
   - Define tool schema (JSON) for Claude.  
   - Update prompts for Scout/Planner/Builder with guidance from §8.3.

5. **Manual smoke tests**
   - In a dev session, run a few scenarios:
     - “Where is the SPB orchestrator loop implemented?”  
     - “Find the config that controls max concurrent scouts.”  
   - Check that results and code edits feel sane.

### Phase 2 – Automation & evaluation

6. **CI-based incremental indexing**
   - Add a CI job (GitHub Actions, etc.) that:
     - On `push` to main, runs a diff-based index update.  
     - Updates a `last_indexed_commit` marker.  

7. **RAG retrieval eval harness**
   - Create `rag_eval/code_search_spb.json` with 10–20 key tasks.  
   - Write a `python -m rag_eval` script to compute hit rate@k.  

8. **Health checks & circuit breaker**
   - Simple health endpoint on Code Search Tool.  
   - Orchestrator reads a flag to decide if `code_search` is allowed.

### Phase 3 – Hardening & extensions

9. **Hybrid search**
   - Optionally extend Code Search Tool to:
     - Combine File Search results with local grep results.  
10. **Language-/AST-aware enhancements (v2)**
    - For frequently-edited languages (Python, TS), add optional AST parsing to align snippet cuts with function/class boundaries before upload.  
11. **Multi-repo / multi-tenant support**
    - Expand `repo` abstraction to support multiple stores and enforce isolation.

---

## 11. Future directions

Once the MVP is stable, you can explore:

- **Multi-agent orchestration with retrieval specialization**  
  - E.g. a dedicated “Code Librarian” agent whose only job is to formulate good `code_search` queries and synthesize retrieved snippets for other agents. citeturn1search18turn1search21turn1search22  
- **Deeper code-graph awareness**  
  - Supplement File Search with a lightweight call graph / dependency graph (e.g. tree-sitter or LSP output) stored separately and fetched as a different tool. citeturn1search17turn1search26turn1search23  
- **More fine-grained evaluation**  
  - Borrow ideas like LLM-as-a-judge for answer correctness and regression testing of agentic coding flows. citeturn1search13turn1search7turn1search17  

---

## 12. Summary

- Gemini File Search is a **production-ready, low‑maintenance RAG backend** that can act as the canonical index for your repos. citeturn0search1turn0search16turn0search20turn0news40  
- By wrapping it in a small **Code Search Tool** and plugging that into your existing **Scout–Plan–Build + Claude Code** harness, you get a robust “Gemini index, Claude brain” architecture with minimal new moving parts.  
- The MVP here intentionally favors **simplicity, incremental indexing, and clear failure modes**, plus a small eval harness so you can trust it rather than hoping it works.

This document should be enough for a capable agent (or you) to implement a first version inside your SPB repo, and then iteratively harden it as you see where it breaks in the real world.
