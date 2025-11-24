# Claude Agent SDK (Python) - Comprehensive Analysis

**Source**: Claude Agent SDK Documentation, GitHub, Context7
**Topic**: SDK Installation, Configuration, and Custom Agents
**Author**: Claude (Research Agent)
**Date Analyzed**: 2025-11-24

## Executive Summary

The Claude Agent SDK is surprisingly simple to integrate. Key findings:

- **Installation**: `pip install claude-agent-sdk` - that's it
- **Authentication**: Uses same `ANTHROPIC_API_KEY` - no new setup
- **Minimal Script**: ~10 lines of Python
- **Custom Agents**: Built-in support via `agents={}` parameter
- **Coexistence**: No conflicts with Claude Code CLI

## 1. Installation Requirements

### Basic Installation
```bash
pip install claude-agent-sdk
```

### System Requirements
| Requirement | Details |
|------------|---------|
| Python | 3.10+ |
| Node.js | Required (for bundled CLI) |
| OS | macOS, Linux, Windows |
| Claude CLI | **Auto-bundled** |

## 2. Authentication

Uses the **same** `ANTHROPIC_API_KEY` environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

No additional authentication setup if Claude Code already works.

## 3. Minimal Working Example

```python
#!/usr/bin/env python3
import anyio
from claude_agent_sdk import query

async def main():
    async for msg in query(prompt="Say hello"):
        print(msg)

anyio.run(main)
```

**That's 8 lines to get a working SDK script.**

## 4. Custom Agent Definition

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    agents={
        "researcher": {
            "description": "Deep research agent",
            "prompt": "You research topics thoroughly using OODA loop",
            "tools": ["WebSearch", "WebFetch", "Read", "Grep"],
            "model": "sonnet"
        }
    }
)

async def main():
    async for msg in query(prompt="@researcher Investigate X", options=options):
        print(msg)
```

## 5. Full Options Reference

```python
ClaudeAgentOptions(
    # Tools
    allowed_tools=["Read", "Write", "Bash", "Edit", "Glob", "Grep"],
    permission_mode="acceptEdits",  # or "bypassPermissions"

    # Limits
    max_turns=10,
    max_budget_usd=5.0,
    max_thinking_tokens=10000,

    # Context
    cwd="/path/to/project",
    system_prompt="You are...",

    # Custom agents
    agents={"name": {"description": "...", "prompt": "...", "tools": [...]}},

    # MCP servers
    mcp_servers={"name": {...}},

    # Hooks
    hooks={"PreToolUse": [...], "PostToolUse": [...]}
)
```

## 6. Coexistence with Claude Code

| Aspect | Compatibility |
|--------|---------------|
| Same API Key | ✅ Yes |
| Same Repo | ✅ Yes |
| File Operations | ✅ Yes (be careful of race conditions) |
| MCP Servers | ✅ Can share |
| Sessions | Independent (feature, not bug) |

## Sources

- GitHub: https://github.com/anthropics/claude-agent-sdk-python
- PyPI: https://pypi.org/project/claude-agent-sdk/
- Context7: /anthropics/claude-agent-sdk-python
