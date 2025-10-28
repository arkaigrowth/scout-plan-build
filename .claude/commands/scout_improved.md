---
description: Search the codebase for files needed to complete the task
argument-hint: [user-prompt] [scale]
model: claude-sonnet-4-5-20250929
---

# Purpose

Search the codebase for files needed to complete the task using a fast, token-efficient agent.

# Variables
USER_PROMPT: $1
SCALE: $2 (defaults to 4)
RELEVANT_FILE_OUTPUT_DIR: "ai_docs/scout"

# Instructions
- We're executing a three step engineering workflow to deliver on the `USER_PROMPT`.
- Execute each step in order, top to bottom.
- If you're returned an unexpected result, stop and notify the user.
- Place each argument for the SlashCommands arguments within double quotes and convert any nested double quotes to single quotes.
- Do not alter the `USER_PROMPT` variable in anyway, pass it in as is.
- IMPORTANT: Flow through each step in the workflow in order, top to bottom. Only waiting for the previous step to complete before starting the next step. Do not stop in between steps. Complete every step in the workflow before stopping.

## Workflow

- Write a prompt for `SCALE` number of agents to the Task tool that will immediately call the Bash tool to run these commands to kick off your agents to conduct the search:
  - `gemini -p "[prompt]" --model gemini-2.5-flash-preview-09-2025` (if count >= 2)
  - `opencode run [prompt] --model cerebras/qwen-3-coder-480b` (if count >= 2)
  - `gemini -p "[prompt]" --model gemini-2.5-flash-lite-preview-09-2025` (if count >= 3)
  - `codex exec -m gpt-5-codex -s read-only -c model_reasoning_effort="low" "[prompt]"` (if count >= 4)
  - `claude -p "[prompt]" --model haiku` (if count >= 5)
- How to prompt the agents:
  - IMPORTANT: Kick these agents off in parallel using the Task tool.
  - IMPORTANT: These agents are calling OTHER agentic coding tools to search the codebase. DO NOT call any search tools yourself.
  - IMPORTANT: That means with the Task tool, you'll immediately call the Bash tool to run the respective agentic coding tool (gemini, opencode, claude, etc.)
  - IMPORTANT: Instruct the agents to quickly search the codebase for files needed to complete the task. This isn't about a full blown search, just a quick search to find the files needed to complete the task.
  - Instruct the subagent to use a timeout of 3 minutes for each agent's bash call. Skip any agents that don't return within the timeout, don't restart them.
  - Make it absolutely clear that the Task tool is ONLY going to call the Bash tool and pass in the appropriate prompt, replacing the [prompt] with the actual prompt you want to run.
  - Make it absolutely clear the agent is NOT implementing the task, the agent is ONLY searching the codebase for files needed to complete the task.
  - Prompt the agent to return a structured list of files with specific line ranges in this format:
    - `- <path to file> (offset: N, limit: M)` where offset is the starting line number and limit is the number of lines to read
    - If there are multiple relevant sections in the same file, repeat the entry with different offset/limit values
  - Execute additional agent calls in round robin fashion.
  - Give them the relevant information needed to complete the task.
  - Skip any agent outputs that are not relevant to the task including failures and errors.
  - If any agent doesn't return in the proper format, don't try to fix it for them, just ignore their output and continue with the next agents responses.
  - IMPORTANT: Again, don't search for the agents themselves, just call the Bash tool with the appropriate prompt.
- After the agents complete, run `git diff --stat` to make sure no files were changed. If there are any changes run `git reset --hard` to reset the changes.
- Follow the `Report` section to manage and report the results. We're going to create a file to store the results.

## Report
- Store the results of the scout in a JSON file at `${RELEVANT_FILE_OUTPUT_DIR}/relevant_files.json`
- The JSON should have this structure:
  ```json
  {
    "task": "[USER_PROMPT]",
    "timestamp": "ISO-8601 timestamp",
    "files": [
      {
        "path": "relative/path/to/file.ext",
        "reason": "Why this file is relevant",
        "offset": 0,
        "limit": 100
      }
    ],
    "key_findings": {
      "summary": "High-level insights from scouting",
      "gaps": "What was not found",
      "recommendations": "Suggested next steps"
    }
  }
  ```
- Return the path to `relevant_files.json`