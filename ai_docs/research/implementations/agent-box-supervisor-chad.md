# Agent Box v6.2: Supervisor Wrapper Implementation Spec

**Source**: Chad (ChatGPT) & Gemini 3.0
**Author**: Chad & Gemini
**Date Analyzed**: 2025-11-22
**Analyzed By**: Claude

---

**Context:** Implement a Supervisor wrapper for Claude Code to manage agent artifacts, safety, parallelism, resumability, and lifecycle.
**Goal:** "Build the system that builds the system." Agents are fallible/untrusted ... the wrapper enforces order.

---

## 0) Non-negotiable realities (late-2025 Claude Code)

1) **Claude Code can auto-invoke custom slash commands** via the `SlashCommand` tool unless blocked.

   - Use frontmatter `disable-model-invocation: true` for human-only / risky commands.
   - Only commands with `description:` frontmatter are eligible for model command context.
2) **SlashCommand context budget is capped (~15k chars by default).**

   - If budget is exceeded, Claude sees only a subset of commands.
   - Therefore generate run-scoped commands and garbage-collect them after runs finish.
   - Budget can be raised via `SLASH_COMMAND_TOOL_CHAR_BUDGET` if ever needed.
3) **Sessions are resumable by ID**: `claude --resume <session_id>`.

   - Capture `session_id` from structured JSON streaming (`--output-format stream-json`), not stdout regex.
4) **Parallel runs are normal.**

   - Single shared temp command folder is unsafe (overwrites).
   - Commands must be run-scoped **and command names must be unique per run** to avoid collisions if names flatten in discovery.
5) **Agents must not read their own artifacts** (self-poisoning).

   - Invoke Claude with ignore patterns for `.agents/` and optionally `.claude/commands/run_*/`.

---

## 1) Directory specification (The Agent Box)

**Root:** `.agents/` (git-ignored)

```text
.agents/
├── INDEX.md              # [Human] Recent-first dashboard
├── INDEX.jsonl           # [Machine] Append-only ledger
├── latest -> runs/YY...
├── pointers/             # Optional semantic symlinks (e.g., last-fail)
└── runs/
    └── YY-MM-DD_HHmm__slug__hash/
        ├── meta.yaml      # [IMMUTABLE-ish] request + safety snapshot
        ├── state.json     # [MUTABLE] supervisor truth
        ├── plan.md        # strategy (if applicable)
        ├── report.md      # final narrative
        ├── changes.patch  # single-agent patch output
        ├── patches/       # multi-agent only (optional)
        │   ├── agent_1.patch
        │   └── agent_2.patch
        └── raw/           # heavy evidence + stream logs
            └── stream.jsonl
```

**Run naming:** `YY-MM-DD_HHmm__<slug>__<hash>`

- Chronological sort
- Human glanceable
- Collision-safe

---

## 2) Supervisor wrapper (PETER + Watchdog)

Users never call claude directly. They call:

```bash
./agent scout "why is db latency high?"
./agent fix "optimize auth middleware"
./agent resume latest
./agent merge latest     # human gate
```

### Phase 1: Setup & Safety (Airlock)

1. **Init run folder**

   - Generate run name + create `.agents/runs/<run_name>/`.
2. **Write meta.yaml** (immutable-ish snapshot)

Include:

- `run_name`, `task`, `slug`
- `run_type`: scout|plan|fix|review|benchmark|ops
- `repo_sha_start`
- `model` + version
- `tools_allowlist` (tiered)
- run-specific safe command names
- run-specific human-only command names
- `config_hash` = hash(allowlist + safe/human-only command sets)

Example:

```yaml
run_name: 2025-11-22_1430__fix-auth__a1b2
type: fix
task: "fix auth bug in login"
repo_sha_start: "9f13c2..."
model: "claude-sonnet-4.5"
tools_allowlist: ["ReadFile","Grep","Ls","EditFile","GitDiff"]
safe_commands: ["scout_a1b2","plan_a1b2","summarize_a1b2"]
human_only_commands: ["merge_a1b2","apply_a1b2"]
config_hash: "a1b2c3d4"
```

3. **Worktree Airlock** (Tier-3 fix only)

   - If `run_type == fix`:
   - Create isolated git worktree, e.g. `agent_box/trees/<run_name>/`.
   - Agent edits only inside that worktree.
   - Patch exported to run folder.
4. **Concurrency-safe command generation** (unique names per run)

   - Create run-specific folder: `.claude/commands/run_<short_id>/`
   - Generate commands whose filenames include the run short id so the slash name is unique:
     - `scout_a1b2.md` → `/scout_a1b2` (invokable)
     - `merge_a1b2.md` → `/merge_a1b2` (human-only)

**Invokable safe command** (`.claude/commands/run_a1b2/scout_a1b2.md`):

```yaml
---
description: Read-only repo investigation (run a1b2)
disable-model-invocation: false
allowed-tools: Grep, ReadFile, Ls, Bash(ls:*), Bash(cat:*)
argument-hint: [question]
---
You are in sandbox run {RUN_DIR}. READ-ONLY.
Investigate: $ARGUMENTS
Output final to {RUN_DIR}/report.md.
Raw evidence to {RUN_DIR}/raw/.
Never write reports to repo root.
```

**Human-only risky command** (`.claude/commands/run_a1b2/merge_a1b2.md`):

```yaml
---
description: Human-only patch apply (run a1b2)
disable-model-invocation: true
allowed-tools: Bash(git apply:*), Bash(git checkout:*), Bash(git status:*)
argument-hint: [optional target]
---
HUMAN ONLY.
Apply patch from {RUN_DIR}/changes.patch (or patches/) to main.
Do NOT invoke automatically.
```

5. **Write initial state.json** (wrapper-owned truth)

```json
{
  "status": "ACTIVE",
  "pid": null,
  "session_id": null,
  "worktree_path": "agent_box/trees/2025-11-22_1430__fix-auth__a1b2",
  "started_at": "2025-11-22T14:30:00Z",
  "last_heartbeat": null,
  "config_hash": "a1b2c3d4",
  "failure": null
}
```

---

### Phase 2: Execution (Stream Processor)

Launch Claude with streaming JSON and ignore patterns:

- `--output-format stream-json`
- `--ignore-patterns .agents/`
- optionally: `--ignore-patterns .claude/commands/run_*/`

System prompt must inject:

- `RUN_DIR`
- exact safe command names (`/scout_a1b2`, `/plan_a1b2`, …)
- human-only commands are forbidden to auto-invoke
- all artifacts must be written to `RUN_DIR`

**Supervisor loop** (pseudo):

```python
process = Popen(["claude", ..., "--output-format", "stream-json",
                 "--ignore-patterns", ".agents/"], stdout=PIPE)

state.pid = process.pid
state.save()

for line in process.stdout:
    event = json.loads(line)

    if event["type"] == "init" and not state.session_id:
        state.session_id = event["session_id"]
        state.save()

    state.last_heartbeat = now_iso()
    state.save()

    append(run_dir/"raw/stream.jsonl", line)

exit_code = process.wait()
if exit_code == 0:
    state.status = "REVIEW"
else:
    state.status = "CRASHED"
    state.failure = {
      "kind": "oom|timeout|tool_error|agent_abort|tests_failed",
      "message": "...",
      "last_safe_artifact": "plan.md"
    }
state.save()

cleanup_run_specific_commands(run_short_id)
update_index_files(...)
```

---

### Phase 3: Watchdog (Zombie Reaping + Garbage Collection)

On every wrapper invocation:

1. Scan `.agents/runs/*/state.json` where `status == ACTIVE`.
2. If PID is dead → mark `CRASHED`.
3. If heartbeat stale (>5m) → mark `STALLED`.
4. Garbage collect run command folders for non-ACTIVE runs:
   - Delete `.claude/commands/run_<short_id>/`
   - Prevents SlashCommand budget bloat.

**Rule:** only ACTIVE runs keep their run-specific commands.

---

### Phase 4: Resumability

Command:

```bash
./agent resume latest
```

Steps:

1. Load `meta.yaml` (safety snapshot).
2. Load `state.json` (`session_id`, `config_hash`).
3. Re-generate `.claude/commands/run_<short_id>/` and the same safe/human-only set.
4. Verify regenerated `config_hash` matches stored one.
5. Resume with same envelope:

```bash
claude --resume <session_id> --output-format stream-json \
       --ignore-patterns .agents/ \
       --allowed-tools <same allowlist>
```

---

## 3) Permission matrix (Tiered autonomy)

Wrapper enforces by run type:

| Tier | Type  | Allowed tools                     | Mutate?    | Safe cmds auto-invokable? |
| ---- | ----- | --------------------------------- | ---------- | ------------------------- |
| 1    | scout | Grep, Ls, ReadFile, cat           | NO         | YES                       |
| 2    | plan  | Tier 1 only                       | NO         | YES                       |
| 3    | fix   | Tier 1 + EditFile (worktree only) | LOCAL ONLY | YES (safe only)           |

Human-only commands (`merge_*`, `apply_*`) must always have:
`disable-model-invocation: true`.

---

## 4) User workflow examples

### A) Scout (autopilot, read-only)

```bash
./agent scout "why is db latency high?"
```

Outputs:

- `.agents/latest/report.md`
- `.agents/latest/raw/stream.jsonl`

INDEX shows DONE when finished.

### B) Fix (airlocked, patch only)

```bash
./agent fix "optimize auth middleware"
```

Agent edits inside worktree, outputs:

- `.agents/latest/changes.patch`
- `.agents/latest/report.md`

Human gate:

```bash
./agent merge latest
```

### C) Crash + resume

Agent OOMs → wrapper marks CRASHED.
You resume:

```bash
./agent resume latest
```

Wrapper recreates run commands + resumes session.

---

## 5) Final hard rules / gotchas

- No prod secrets in agent env. `.env.test` only.
- Keep run-specific command descriptions tiny.
- Garbage-collect commands aggressively after runs finish.
- Don't let Claude read `.agents/` (self-poison risk).
- Store enough local artifacts to debug even if session retention expires.

---

## 6) Implementation note

Use Python for `./agent` supervisor (`agents/core.py`):

- robust JSON streaming
- signal/atexit cleanup traps
- safe git worktree ops
- hashing + ledgers + watchdog

---

*End of spec.*
