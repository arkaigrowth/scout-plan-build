# Scout-Plan-Build

Claude Code slash commands and helper scripts for a three-step way of working on a codebase: **scout** for the files a task touches, **plan** a written spec from them, then **build** from the spec. Around that loop sit git worktree checkpoints with undo and redo, parallel agent runs in separate worktrees, session handoff across context compaction, and a dependency tracer for broken references.

## Credit and what is in this repository

The scout, plan and build method, and the habit of running agents in git worktrees, come from IndyDevDan's Tactical Agentic Coding course ([agenticengineer.com](https://agenticengineer.com)) and his public videos (the worktree pattern is credited in the two parallel-worktree commands). **Course materials are not included.** Earlier versions of this repository carried the course's AI Developer Workflow code (`adws/` scripts and modules), hooks, slash commands and shell scripts; those were removed from the repository and its full history in October 2026.

Everything left was written by Alex Kamysz, with Claude Code as a coding assistant:

| Area | Files | What it does |
|---|---|---|
| Workflow commands | `.claude/commands/workflow/` | `scout_improved`, `scout_parallel`, `build`, and `scout_plan_build`, which chains the three steps and stops at the first failure |
| Planning | `.claude/commands/planning/plan_w_docs_improved.md` | Writes an implementation spec to `specs/` from a task, optional doc URLs, and the scout's file list |
| Worktrees | `.claude/commands/git/`, `scripts/worktree_manager.sh` | Create a worktree, checkpoint it, undo and redo checkpoints; run N agents on one spec in N worktrees, compare them, merge the winner |
| Session continuity | `.claude/commands/session/`, `.claude/hooks/session_start.py` | Write a handoff file before `/compact`, and detect it on the next session start |
| Coach mode | `.claude/commands/coach.md` | Has the agent narrate which step it is in and why |
| Parallel scout | `adws/adw_scout_parallel.py`, `adws/scout_simple.py` | Runs several scouts with different focus areas as subprocesses and merges their file lists into `scout_outputs/relevant_files.json` |
| Context augmentation | `adws/adw_modules/context_augmentation.py`, `memory.py`, `gemini_search.py` | Optional mem0 memory and Gemini File Search, with ripgrep as the fallback, to enrich scout results |
| Input validation | `adws/adw_modules/validators.py` | Pydantic models that check prompts, file paths, branch names and IDs (length limits, path traversal, shell metacharacters) before they reach a subprocess |
| VCS support | `adws/adw_modules/vcs_detection.py`, `bitbucket_ops.py` | Detects GitHub vs Bitbucket from the remote and wraps the Bitbucket REST API |
| Run tracking | `agents/run_manager.py` | Records each agent run's state and outputs |
| Dependency tracer | `scripts/dependency-tracer/` | A Claude skill plus shell and Python scripts that find broken slash-command references and Python imports, with ASCII dependency diagrams |
| Research and search | `scripts/research-add.py`, `scripts/update-research-index.py`, `scripts/spb_search.py` | Add documents to a local research library and keep its index current; `spb_search.py` is a CLI over the Gemini plus ripgrep code search |

## Use it in a project

Nothing here needs installing. Copy what you want into the target repository:

```bash
cp -r scout-plan-build/.claude/commands  your-repo/.claude/
cp -r scout-plan-build/adws scout-plan-build/scripts  your-repo/   # only if you want the Python scout and worktree tools
```

Then, inside Claude Code in that repository:

```text
/workflow:scout_plan_build "Add rate limiting to the login endpoint"
```

or step by step:

```text
/workflow:scout_improved "Add rate limiting to the login endpoint" "4"
/planning:plan_w_docs_improved "Add rate limiting to the login endpoint" "" "scout_outputs/relevant_files.json"
/workflow:build "specs/<the spec it wrote>.md"
```

To try several approaches at once:

```text
/git:init-parallel-worktrees rate-limit 3
/git:run-parallel-agents "specs/rate-limit.md" rate-limit
/git:compare-worktrees rate-limit
/git:merge-worktree trees/rate-limit-2
```

The session handoff hook only runs if you register `.claude/hooks/session_start.py` as a `SessionStart` hook in your `.claude/settings.json`.

Python pieces need Python 3.10+ and `pydantic`; `requests`, `psutil`, `typer` and `rich` are used by some scripts; mem0 and Gemini File Search are optional.

## Tests

```bash
python3 -m pytest adws/adw_tests/test_validators.py tests/test_bitbucket_integration.py
```

70 tests, all passing as of 2026-10-10.

## Limitations

- This started as an extension of the course framework and was cut down to the parts Alex wrote. A few modules still contain optional calls into framework pieces that are no longer here: `exceptions.py` and `memory_hooks.py` import GitHub issue-comment helpers inside functions, and those code paths will raise `ImportError` if reached. The scout, validators, VCS detection and Bitbucket modules do not depend on them.
- `.claude/skills/adw-complete.md` and `adw-scout.md` are design drafts for skills, not tested packages.
- The commands target Claude Code as of late 2025; command namespacing and hook formats may have moved since.

## License

MIT for the files in this repository; see [LICENSE](LICENSE). `scripts/dependency-tracer/` carries its own MIT notice.
