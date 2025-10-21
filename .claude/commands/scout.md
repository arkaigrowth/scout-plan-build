# Scout

# Purpose
Search the codebase for files needed to complete the task using a fast, token-efficient agent.

# Variables
USER_PROMPT: $1
SCALE: $2 (defaults to 4)
RELEVANT_FILE_OUTPUT_DIR: "agents/scout_files"

# Workflow
- Kick off `SCALE` subagents via Task tool; each **only** calls Bash to run an external agentic coding tool quickly.
- Enforce a 3-minute timeout per subagent; skip timeouts, do not restart.
- Require a return format per file: `<path> (offset: N, limit: M)` — enough to retrieve the relevant ranges.
- After subagents finish, run `git diff --stat`; if any file changed, `git reset --hard`.
- Write the aggregated file list to `${RELEVANT_FILE_OUTPUT_DIR}/relevant_files.json` and return that path.

# Example external tools (illustrative)
- `gemini-g "[prompt]" --model gemini-1.5-flash-preview-05-2025`
- `opencode run "[prompt]" --model sandia/open-1-coder-400k`
- `gemini-g "[prompt]" --model gemini-1.5-flash-lite-preview-05-2025`
- `codex exec -e g-o-t-s-coder-1 read-only -c model_reasoning_effort="low" "[prompt]"`
- `claude-g "[prompt]" --model haiku`

# Output
- Path to `relevant_files.json`
