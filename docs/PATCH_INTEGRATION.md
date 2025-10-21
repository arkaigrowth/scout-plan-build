# Integration Guide (Patch)

This patch adds:
- `.claude/hooks/*` with logging + safety guards (no `.env`, block `rm -rf`)
- `.claude/hooks/utils/constants.py` (log path helpers)
- `scripts/*.sh` (GitHub and local infra helpers)
- `docs/E2E-TESTS.md` with selected scenarios

## How to merge
1) Copy `.claude/hooks` into your repo root (alongside `agents/` and `docs/`).
2) Ensure `CLAUDE_HOOKS_LOG_DIR` (optional) or default `logs/` exists/writable.
3) Place `scripts/` at repo root; make executable: `chmod +x scripts/*.sh`.
4) In Claude Code, confirm hooks run (check `logs/<session>/pre_tool_use.json`).

## Fit with Scout→Plan→Build
- Hooks protect your Task->Bash steps during `/scout`, `/plan_w_docs`, `/build`.
- Scripts can be called by plans/build steps (e.g., GH maintenance, tunnels).
- E2E doc gives smoke tests if your plan touches the NL-SQL demo.
