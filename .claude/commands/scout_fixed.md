---
description: FIXED Scout - uses Task agents instead of broken external tools
argument-hint: [user-prompt] [scale]
---

# Scout (FIXED VERSION)

## What Changed
- Commented out external tools (gemini, opencode, etc.) that don't exist
- Replaced with Task agent using "explore" subagent
- Kept all the good stuff: parallel execution, timeouts, git safety

## Variables
USER_PROMPT: $1
SCALE: $2 (defaults to 3)
RELEVANT_FILE_OUTPUT_DIR: "ai_docs/scout"

## Workflow

Kick off `SCALE` parallel subagents using Task tool with "explore" type:

```python
# Launch parallel exploration agents
agents = []
for i in range(int(SCALE)):
    agent = Task(
        subagent_type="explore",
        prompt=f"Find files related to: {USER_PROMPT} (search {i+1}/{SCALE})"
    )
    agents.append(agent)

# OLD CODE (commented out):
# gemini -p "[prompt]"  # Doesn't exist
# opencode run "[prompt]"  # Doesn't exist
# codex exec "[prompt]"  # Doesn't exist
```

After agents complete:
1. Run `git diff --stat` to check for changes
2. If changes detected: `git reset --hard`
3. Aggregate results to `ai_docs/scout/relevant_files.json`
4. Sort files for determinism

## Why This Works
- Task agents with "explore" type ACTUALLY EXIST in Claude Code
- Keeps parallel execution (good!)
- Keeps timeout management (good!)
- Keeps git safety (good!)
- Just replaces the broken tool calls