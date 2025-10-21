# SETUP

## Requirements
- Python 3.11+ (recommend `uv` or `pipx`)
- Node 18+ (if your app includes a front-end)
- Claude Code (with hooks enabled, if you use the provided hook patterns)
- (Optional) Anthropic Agents SDK and an agent runtime/device

## Quick Start (Claude Code-first)
1) Open this folder in **Claude Code**.
2) Ensure your hooks (if using) write logs under `logs/<session_id>` (see `AGENTS_SDK_INTEGRATION.md` for the rationale).
3) Use `/scout_plan_build` with two args: `USER_PROMPT`, `DOCUMENTATION_URLS` (comma-separated or space-delimited).

## Optional: Agents SDK
If you’re delegating out-of-the-loop jobs to an agent device (AFK delegation), see `docs/AGENTS_SDK_INTEGRATION.md` and wire the slash commands to Jobs that spawn bash tools invoking your agent fleet.
