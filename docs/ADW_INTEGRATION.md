# ADW shims integration

This patch adds:
- `adws/adw_common.py` — helpers for git, parsing, reporting
- `adws/adw_plan.py` — writes a spec under `specs/`
- `adws/adw_build.py` — consumes a plan, emits `ai_docs/build_reports/<slug>-build-report.md`
- `adws/adw_review.py` — summarizes diff + plan; emits `ai_docs/reviews/<slug>-review.md`
- `agents/commands/build_adw.md` — a build command that calls the shim

## How to use
1) Generate a plan:
   ```bash
   uv run adws/adw_plan.py --prompt "Your task" --docs "https://docs..." --relevant agents/scout_files/relevant_files.json
   ```
   → returns `specs/<kebab>.md`

2) Build via Claude Code slash command **/build_adw** or by hand:
   ```bash
   uv run adws/adw_build.py specs/<kebab>.md
   ```
   → returns path to the build report

3) Optional review:
   ```bash
   uv run adws/adw_review.py specs/<kebab>.md
   ```

## Wire into your macro
- Replace the `/build` step in `/scout_plan_build` with `/build_adw` to run the shim:
  1) /scout → relevant_files.json
  2) /plan_w_docs → specs/<kebab>.md
  3) /build_adw → ai_docs/build_reports/<slug>-build-report.md

## Notes
- The shim is intentionally conservative: it logs intent, captures diffs, and creates reports. 
- Extend `adw_build.py` to call your editor/LLM subagents with atomic edits and commit boundaries.
