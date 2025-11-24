# Plan: Claude Agent SDK Deep Research Feature

## Summary

Implement a `/research` slash command that uses the Claude Agent SDK to perform deep, structured research on any topic. The feature will support multiple depth levels (quick/standard/deep), use Anthropic's OODA loop pattern, and auto-write outputs to canonical paths in `ai_docs/research/`.

## Problem Statement

Currently, research tasks in the framework rely on the Task tool which:
- Returns text to main agent (doesn't write files directly)
- Has no depth/budget controls
- Lacks structured research methodology
- Requires manual output routing

The SDK enables purpose-built research agents with budget limits, streaming, and direct file output.

## Inputs

### Scout Results
- **File**: `scout_outputs/sdk-research-files.json`
- **Key Research**:
  - `ai_docs/research/implementations/claude-agent-sdk-analysis.md`
  - `ai_docs/analyses/sdk-integration-assessment.md`

### Documentation References
- Claude Agent SDK: `pip install claude-agent-sdk`
- Authentication: Uses existing `ANTHROPIC_API_KEY`
- Anthropic Multi-Agent Research: OODA loop pattern

### Constraints
- Must coexist with Claude Code CLI
- Output to canonical `ai_docs/research/` paths
- Budget limits required (prevent runaway costs)
- AskUserQuestion has bypass bug - need plain text fallback

## Architecture/Approach

```
┌─────────────────────────────────────────────────────────────┐
│  /research "topic" --depth standard                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  .claude/commands/utilities/research.md                     │
│  - Parse arguments                                          │
│  - If no depth specified, ask user (with fallback)          │
│  - Call: python scripts/sdk_research_agent.py               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  scripts/sdk_research_agent.py                              │
│  - ClaudeAgentOptions with depth-based limits               │
│  - OODA loop system prompt                                  │
│  - WebSearch, WebFetch, Read, Grep tools                    │
│  - Async query loop                                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Output: ai_docs/research/articles/{topic-slug}.md          │
│  - Structured markdown with frontmatter                     │
│  - Sources and citations                                    │
│  - Auto-update research index                               │
└─────────────────────────────────────────────────────────────┘
```

### Depth Configurations

| Depth | Turns | Budget | Time | Use Case |
|-------|-------|--------|------|----------|
| quick | 5 | $0.50 | ~2 min | Quick fact check |
| standard | 10 | $1.00 | ~5 min | Normal research |
| deep | 20 | $3.00 | ~15 min | Comprehensive |

### OODA Loop Pattern

```
OBSERVE → What information exists?
ORIENT  → What's most relevant?
DECIDE  → What gaps need filling?
ACT     → Search, fetch, analyze
REPEAT  → Until confident or max turns
```

## Implementation Steps

### Step 1: Create SDK Research Script

**File**: `scripts/sdk_research_agent.py`

```python
#!/usr/bin/env python3
"""
Deep research agent using Claude Agent SDK.
Implements OODA loop pattern from Anthropic's multi-agent research system.
"""

import asyncio
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    TextBlock,
    ResultMessage
)

# Depth configurations
DEPTH_CONFIG = {
    "quick": {"turns": 5, "budget": 0.50, "thinking": 2000},
    "standard": {"turns": 10, "budget": 1.00, "thinking": 5000},
    "deep": {"turns": 20, "budget": 3.00, "thinking": 10000},
}

RESEARCH_SYSTEM_PROMPT = """You are a deep research agent. Follow the OODA loop methodology:

**OBSERVE**: What information currently exists about the topic?
- Search for authoritative, recent sources
- Note what has been covered vs. gaps

**ORIENT**: What is most relevant to the user's query?
- Filter noise, prioritize signal
- Identify conflicting information
- Consider multiple perspectives

**DECIDE**: What should be pursued next?
- If significant gaps exist, search more specifically
- If information conflicts, find authoritative resolution
- If sufficient coverage, move to synthesis

**ACT**: Execute the decision
- Use WebSearch for broad discovery
- Use WebFetch for specific page content
- Document all findings with source URLs

**SYNTHESIS**: When research is complete
- Organize findings into clear sections
- Include all source URLs
- Highlight key insights and conclusions
- Note any remaining uncertainties

Output format: Structured markdown with frontmatter, sections, and sources."""

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]  # Limit length

async def research(
    topic: str,
    depth: str = "standard",
    output_dir: Path = None,
    cwd: Path = None
) -> Path:
    """Execute deep research on a topic."""

    config = DEPTH_CONFIG[depth]
    cwd = cwd or Path.cwd()
    output_dir = output_dir or (cwd / "ai_docs" / "research" / "articles")
    output_dir.mkdir(parents=True, exist_ok=True)

    options = ClaudeAgentOptions(
        allowed_tools=["WebSearch", "WebFetch", "Read", "Grep", "Glob"],
        max_turns=config["turns"],
        max_budget_usd=config["budget"],
        max_thinking_tokens=config["thinking"],
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        cwd=str(cwd),
    )

    print(f"🔍 Starting {depth} research on: {topic}")
    print(f"   Max turns: {config['turns']}, Budget: ${config['budget']:.2f}")

    findings = []
    total_cost = 0.0

    prompt = f"""Research the following topic thoroughly:

**Topic**: {topic}

Follow the OODA loop. Search multiple sources. Synthesize findings into a comprehensive report with:
1. Executive summary
2. Key findings (organized by theme)
3. Sources (with URLs)
4. Conclusions and insights

Begin your research."""

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    findings.append(block.text)
        elif isinstance(message, ResultMessage):
            total_cost = getattr(message, 'total_cost_usd', 0.0)

    # Generate output
    slug = slugify(topic)
    output_file = output_dir / f"{slug}.md"

    # Create frontmatter
    frontmatter = f"""---
title: "{topic}"
date_researched: "{datetime.now().strftime('%Y-%m-%d')}"
depth: "{depth}"
cost_usd: {total_cost:.4f}
generated_by: "Claude Agent SDK Research Agent"
---

"""

    content = frontmatter + "\n\n".join(findings)
    output_file.write_text(content)

    print(f"✅ Research complete!")
    print(f"   Output: {output_file}")
    print(f"   Cost: ${total_cost:.4f}")

    return output_file

def main():
    parser = argparse.ArgumentParser(description="Deep research using Claude Agent SDK")
    parser.add_argument("topic", help="Topic to research")
    parser.add_argument(
        "--depth",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Research depth (default: standard)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: ai_docs/research/articles/)"
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        help="Working directory (default: current)"
    )

    args = parser.parse_args()

    result = asyncio.run(research(
        topic=args.topic,
        depth=args.depth,
        output_dir=args.output_dir,
        cwd=args.cwd
    ))

    # Output result path for script integration
    print(f"\nRESULT_PATH:{result}")

if __name__ == "__main__":
    main()
```

### Step 2: Create Slash Command

**File**: `.claude/commands/utilities/research.md`

```markdown
---
description: Deep research using Claude Agent SDK with OODA loop methodology
argument-hint: <topic> [--depth quick|standard|deep]
---

# Deep Research Command

Execute structured research using the Claude Agent SDK.

## Usage

```
/research "topic to research"
/research "topic" --depth deep
/research "React Server Components" --depth quick
```

## Depth Levels

| Depth | Time | Cost | Best For |
|-------|------|------|----------|
| quick | ~2 min | ~$0.50 | Quick fact checks |
| standard | ~5 min | ~$1.00 | Normal research |
| deep | ~15 min | ~$3.00 | Comprehensive analysis |

## Execution

If no depth is specified, ask the user:

**Research Depth Selection**

What depth of research do you need?

1. **Quick** (~2 min, $0.50) - Fast fact-finding
2. **Standard** (~5 min, $1.00) - Balanced coverage [default]
3. **Deep** (~15 min, $3.00) - Comprehensive analysis

Then execute:

```bash
python scripts/sdk_research_agent.py "$1" --depth {selected_depth}
```

## Output

Results saved to: `ai_docs/research/articles/{topic-slug}.md`

The output includes:
- Frontmatter with metadata
- Executive summary
- Key findings by theme
- All sources with URLs
- Conclusions and insights
```

### Step 3: Add SDK Dependency

**File**: `pyproject.toml` or `requirements.txt`

Add:
```
claude-agent-sdk>=0.1.0
```

Or install directly:
```bash
pip install claude-agent-sdk
```

### Step 4: Update CLAUDE.md

Add to command menu:

```markdown
### Research
| Command | Purpose |
|---------|---------|
| `/research` | Deep research with SDK (OODA loop) |
```

## Testing Strategy

### Unit Tests
- Test `slugify()` function with various inputs
- Test depth configuration loading
- Test output path generation

### Integration Tests
1. **Quick research**: `/research "Python GIL" --depth quick`
   - Verify completes in < 3 minutes
   - Verify output file created
   - Verify frontmatter present

2. **Standard research**: `/research "WebAssembly use cases"`
   - Verify multiple sources cited
   - Verify structured output

3. **Deep research**: `/research "Kubernetes networking" --depth deep`
   - Verify comprehensive coverage
   - Verify budget respected

### Validation Criteria
- [ ] SDK installs without errors
- [ ] Script runs with existing ANTHROPIC_API_KEY
- [ ] Output written to correct canonical path
- [ ] Frontmatter includes all required fields
- [ ] Budget limits enforced
- [ ] Errors handled gracefully

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK not installed | Low | High | Check at script start, helpful error |
| API key missing | Low | High | Validate env var, clear error message |
| Budget exceeded | Medium | Medium | Hard limits in ClaudeAgentOptions |
| Network failures | Medium | Low | Retry logic, partial save |
| Output path issues | Low | Medium | Create dirs, validate paths |

### Rollback Plan
If issues arise:
1. The `/research` command is isolated - won't affect other commands
2. SDK script is standalone - can be deleted without impact
3. No framework changes required for basic implementation

## Success Criteria

### Must Have
- [ ] `/research "topic"` executes SDK research agent
- [ ] Output saved to `ai_docs/research/articles/`
- [ ] Three depth levels working (quick/standard/deep)
- [ ] Budget limits enforced
- [ ] Clean error handling

### Should Have
- [ ] Depth selection prompt if not specified
- [ ] Progress output during research
- [ ] Cost reported at completion

### Nice to Have
- [ ] Auto-update research index
- [ ] Integration with `/research-add` for manual imports
- [ ] Parallel subagent support for deep mode

## Files to Create/Modify

| File | Action | Priority |
|------|--------|----------|
| `scripts/sdk_research_agent.py` | Create | High |
| `.claude/commands/utilities/research.md` | Create | High |
| `requirements.txt` or `pyproject.toml` | Modify | Medium |
| `CLAUDE.md` | Modify | Low |

## Estimated Effort

| Task | Hours |
|------|-------|
| Create sdk_research_agent.py | 1.5 |
| Create research.md command | 0.5 |
| Testing and iteration | 1.0 |
| Documentation updates | 0.5 |
| **Total** | **3.5** |
