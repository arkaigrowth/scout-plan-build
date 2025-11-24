# Claude Agent SDK Integration Assessment

**Date**: 2025-11-24
**Framework**: scout_plan_build_mvp v4.0
**Analyst**: Claude (Backend Architect Agent)

## Executive Summary

**Total Effort: 10-16 hours (2-3 days focused work)**

SDK integration is NOT that hard. The SDK is designed to work alongside Claude Code with no conflicts.

## Effort Breakdown

| Task | Hours | Notes |
|------|-------|-------|
| **Basic SDK Working** | **1-2** | Install, configure, test |
| - Install package | 0.1 | `pip install claude-agent-sdk` |
| - Minimal script | 0.5 | 8 lines of Python |
| - Test flow | 0.5 | Verify auth, tools |
| **Custom Researcher** | **5-8** | Full-featured agent |
| - Define tools | 1-2 | @tool decorators |
| - Configure options | 1 | Prompts, permissions |
| - Add hooks | 1 | Output capture |
| - Test/iterate | 2-3 | Edge cases |
| **Full Integration** | **4-6** | Framework connected |
| - Slash command | 1 | `/research` |
| - Output routing | 0.5 | Canonical paths |
| - Documentation | 0.5 | CLAUDE.md |
| - E2E testing | 1-2 | Validation |

## Recommended Approach

### Option B: Slash Command → Bash → SDK Script (RECOMMENDED)

```
/research "topic" --> Bash --> sdk_research_agent.py --> ai_docs/research/
```

**Why this works:**
- Fits existing patterns (like adw_build.py)
- Output path controlled by command
- Minimal framework changes
- Can evolve to native module later

## Key Gotchas

| Risk | Mitigation |
|------|------------|
| Auth differences | Both use ANTHROPIC_API_KEY |
| Session isolation | Design self-contained agents |
| Token limits | Set max_turns, max_budget_usd |
| Async complexity | Use asyncio.run() wrapper |
| MCP servers | Explicitly configure needed ones |

## Phase Plan

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| 1 | Day 1 | Standalone `scripts/sdk_research_agent.py` |
| 2 | Day 2-3 | Native `adw_modules/sdk_agent.py` |
| 3 | Future | Full SDK migration |

## Architecture

```
Current:
  ADW Scripts → subprocess → Claude CLI

With SDK:
  ADW Scripts → subprocess → Claude CLI (unchanged)
       ↓
  sdk_agent.py → async → Anthropic API (new path)
       ↓
  /research command (specialized research)
```

## Conclusion

**Integration is straightforward.** The main work is prompt engineering for the research agent, not SDK complexity. Start with a standalone script, prove it works, then evolve.
