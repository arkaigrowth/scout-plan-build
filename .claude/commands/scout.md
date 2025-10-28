# Scout

# Purpose
Search the codebase for files needed to complete the task using a fast, token-efficient agent.

# Variables
USER_PROMPT: $1
SCALE: $2 (defaults to 4)
RELEVANT_FILE_OUTPUT_DIR: "ai_docs/scout"

# Workflow
- Kick off `SCALE` subagents via Task tool; each **only** calls Bash to run an external agentic coding tool quickly.
- Enforce a 3-minute timeout per subagent; skip timeouts, do not restart.
- Require a return format per file: `<path> (offset: N, limit: M)` — enough to retrieve the relevant ranges.
- After subagents finish, run `git diff --stat`; if any file changed, `git reset --hard`.
- Write the aggregated file list to `${RELEVANT_FILE_OUTPUT_DIR}/relevant_files.json` and return that path.

# Use Task agents (THESE ACTUALLY WORK)
- Task(subagent_type="explore", prompt="[prompt] - focus on models/schemas")
- Task(subagent_type="explore", prompt="[prompt] - focus on routes/controllers")
- Task(subagent_type="explore", prompt="[prompt] - focus on tests")
- Task(subagent_type="python-expert", prompt="[prompt] - find implementation files")

# OLD BROKEN TOOLS (commented out):
# - `gemini-g "[prompt]"` - doesn't exist
# - `opencode run "[prompt]"` - doesn't exist
# - `codex exec "[prompt]"` - doesn't exist

# Output
- Path to `relevant_files.json`
