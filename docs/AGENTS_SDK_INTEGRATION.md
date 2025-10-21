# AGENTS_SDK_INTEGRATION

When to use it:
- **AFK delegation** or **parallel scouting** where multiple subagents call external coder tools via bash (Gemini/OpenCode/etc.).
- Long-running builds you want to offload from your in-the-loop Claude Code session.

How it fits:
- The slash commands here can be executed “locally” in Claude Code **or** wrapped as **Agent SDK Jobs** where the Task tool only invokes bash to run external coder tools.
- Ensure prompt safety (no `.env` access, guarded `rm -rf`) consistent with your hooks.

Minimal sketch:
```python
from anthropic import Client  # pseudo, adapt to actual SDK surface
client = Client(api_key=os.environ["ANTHROPIC_API_KEY"])

# Example: spawn a job that runs the SCOUT step with N parallel bash tools
job = client.jobs.create(
    name="scout_files",
    steps=[
        # Your implementation will queue sub-steps that call bash tools with timeouts
    ],
)
```

> Recommendation: Keep Agents SDK **optional** for MVP. Start in Claude Code; add Agent Jobs later for parallel scouting or AFK builds.
