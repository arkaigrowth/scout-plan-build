# Claude Code Skills System - Comprehensive Guide

**Version**: 2.0.20+
**Last Updated**: 2025-10-20
**Status**: Production-Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What Are Skills?](#what-are-skills)
3. [Skills vs Other Systems](#skills-vs-other-systems)
4. [Implementation Details](#implementation-details)
5. [Skill Structure & Format](#skill-structure--format)
6. [Creating Custom Skills](#creating-custom-skills)
7. [Integration with ADW Workflow](#integration-with-adw-workflow)
8. [Advanced Patterns](#advanced-patterns)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Executive Summary

**Claude Skills** are a powerful extensibility system introduced in Claude Code 2.0.20 that allows you to create reusable, parameterized prompt templates and workflows as **custom slash commands** and **custom agents**.

### Key Capabilities
- Create custom slash commands with YAML frontmatter configuration
- Define specialized agents with specific behavioral patterns
- Parameterize prompts for flexible reuse
- Integrate with MCP servers, hooks, and native tools
- Share skills across projects or keep them project-specific

### Skills Enable
- **Workflow Automation**: Scout→Plan→Build patterns as reusable commands
- **Specialized Agents**: Domain-specific agents (e.g., code reviewer, debugger)
- **Memory Integration**: Skills that work with mem0 and persistent memory
- **Git Worktree Management**: Custom commands for branch/worktree workflows
- **Parallel Orchestration**: Multi-agent coordination patterns

---

## What Are Skills?

Skills in Claude Code are **structured markdown files** that define:

1. **Slash Commands** (`/command-name`)
   - Reusable prompt templates
   - Parameterized workflows
   - Shell script execution wrappers
   - Multi-step automation sequences

2. **Custom Agents** (`@agent-name`)
   - Specialized behavioral personas
   - Domain-specific expertise patterns
   - Tool coordination strategies
   - Quality gates and validation logic

### How Skills Differ

| Feature | Skills | Slash Commands | MCP Tools | Hooks |
|---------|--------|----------------|-----------|-------|
| **Definition** | Markdown + YAML | Markdown only | JSON config | JSON config |
| **Invocation** | `/name` or `@name` | `/name` | Auto-available | Event-triggered |
| **Parameterization** | Full YAML support | Basic `$ARGUMENTS` | Tool parameters | Limited |
| **Scope** | User/Project/Global | User/Project | Project/User | Project/User |
| **Execution** | Prompt injection + scripts | Prompt injection | External server | Shell scripts |
| **State** | Stateless (per-call) | Stateless | Stateful (server) | Event-driven |

---

## Skills vs Other Systems

### Skills vs Slash Commands (Pre-2.0.20)

**Old Slash Commands** (still supported):
```markdown
---
description: "Simple description"
---

This is a prompt template.
! /path/to/script.sh $ARGUMENTS
```

**Skills** (Enhanced):
```markdown
---
name: my-skill
description: "Enhanced command with full metadata"
category: utility
complexity: basic
mcp-servers: [context7, sequential]
personas: [technical-writer]
tools: [Read, Write, Grep]
argument-hint: "<file> <action>"
---

# Structured Prompt Template

Behavioral instructions...
Tool coordination...
Validation logic...
```

### Skills vs Custom Agents

Custom agents **are** skills! An agent is a skill with behavioral focus:

```markdown
---
name: code-reviewer
description: "Thorough code review with security focus"
category: quality
tools: [Read, Grep, Bash]
---

# Code Reviewer Agent

## Triggers
- Pull request review requests
- Code quality assessment needs

## Behavioral Mindset
Focus on security, performance, and maintainability...

## Key Actions
1. Security analysis
2. Performance review
3. Best practices validation
```

### Skills vs MCP Servers

| Aspect | Skills | MCP Servers |
|--------|--------|-------------|
| **Purpose** | Prompt templates & workflows | External tool integration |
| **Language** | Markdown + Shell | Any (JSON protocol) |
| **State** | Stateless | Can be stateful |
| **Performance** | Instant | Network overhead |
| **Complexity** | Simple | Complex |
| **Best For** | Workflows, prompts, coordination | APIs, databases, external services |

**Use Together**: Skills can orchestrate MCP servers!

```markdown
---
name: enhanced-search
mcp-servers: [context7, serena]
---

Search using Context7 for docs, Serena for code...
```

---

## Implementation Details

### File System Structure

```
~/.claude/                          # User-level (global)
├── commands/                       # Slash commands
│   ├── custom/                     # Custom namespace
│   │   ├── my-command.md          # /custom:my-command
│   │   └── my-script.sh
│   ├── sc/                         # SuperClaude namespace
│   │   ├── analyze.md             # /sc:analyze
│   │   └── spawn.md
│   └── direct-command.md          # /direct-command
└── agents/                         # Custom agents
    ├── code-reviewer.md           # @code-reviewer
    └── debugger.md                # @debugger

.claude/                           # Project-level (local)
├── commands/
│   ├── project-specific.md
│   └── scripts/
└── agents/
    └── domain-expert.md
```

### Scoping Rules

1. **Global Skills** (`~/.claude/`)
   - Available in all projects
   - Personal productivity tools
   - Shared utilities

2. **Project Skills** (`.claude/`)
   - Only available in specific project
   - Team-shared workflows
   - Project-specific automation

3. **Priority**: Project > User > Built-in

### Loading & Discovery

Skills are loaded:
- **At startup**: All markdown files scanned
- **On restart**: After creating new skills
- **Hot reload**: Settings changes (but not new files)

Discovery pattern:
```bash
# Find all command definitions
find ~/.claude/commands -name "*.md"
find .claude/commands -name "*.md"

# Find all agent definitions
find ~/.claude/agents -name "*.md"
find .claude/agents -name "*.md"
```

---

## Skill Structure & Format

### YAML Frontmatter Schema

```yaml
---
# Required
name: skill-name                    # Command/agent identifier
description: "One-line description" # Shown in autocomplete

# Optional - Metadata
category: utility|quality|analysis|orchestration|communication
complexity: basic|intermediate|advanced|expert
version: "1.0.0"

# Optional - Integration
mcp-servers: [context7, sequential, magic]  # Enable specific MCPs
personas: [technical-writer, debugger]       # Invoke sub-agents
tools: [Read, Write, Grep, Bash]            # Tool access hints

# Optional - Command-specific
argument-hint: "<file> [options]"   # Usage hint
model: sonnet|opus|haiku           # Model preference

# Optional - Agent-specific
triggers: [pattern1, pattern2]      # Auto-activation patterns
---
```

### Markdown Body Structure

#### For Commands

```markdown
# Command Name

## Description
What this command does and when to use it.

## Usage
```
/command-name <arg1> [arg2] [--option]
```

## Behavioral Flow
1. Step 1: Action
2. Step 2: Action
3. Step 3: Action

## Tool Coordination
- **Tool1**: Purpose
- **Tool2**: Purpose

## Examples
[Usage examples...]

## Implementation
! /path/to/script.sh $ARGUMENTS
```

#### For Agents

```markdown
# Agent Name

## Triggers
- Situation 1
- Situation 2

## Behavioral Mindset
Core philosophy and approach...

## Focus Areas
- **Area 1**: Details
- **Area 2**: Details

## Key Actions
1. Action 1: Details
2. Action 2: Details

## Outputs
- **Output Type 1**: Description
- **Output Type 2**: Description

## Boundaries
**Will:**
- Do X
- Do Y

**Will Not:**
- Won't do A
- Won't do B
```

---

## Creating Custom Skills

### Example 1: Simple Utility Command

**File**: `~/.claude/commands/custom/git-status-check.md`

```markdown
---
name: git-status-check
description: "Check git status with enhanced formatting"
category: utility
complexity: basic
tools: [Bash]
---

# Git Status Check

Run enhanced git status check with branch info and uncommitted changes.

Run:
! ~/.claude/commands/custom/git-status-check.sh
```

**File**: `~/.claude/commands/custom/git-status-check.sh`

```bash
#!/bin/bash
set -e

echo "=== Git Status Check ==="
echo ""
echo "Branch: $(git branch --show-current)"
echo ""
git status --short
echo ""
echo "Commits ahead/behind:"
git status --branch --porcelain=v1 | head -1
```

```bash
chmod +x ~/.claude/commands/custom/git-status-check.sh
```

**Usage**: `/custom:git-status-check`

### Example 2: Parameterized Workflow Command

**File**: `~/.claude/commands/custom/scout-and-plan.md`

```markdown
---
name: scout-and-plan
description: "Run scout then generate plan for a feature"
category: orchestration
complexity: intermediate
mcp-servers: [serena]
tools: [Read, Write, Bash]
argument-hint: "<feature-description> [depth]"
---

# Scout and Plan Workflow

Executes scout→plan workflow for feature implementation.

## Usage
```
/custom:scout-and-plan "implement auth" 4
```

## Workflow
1. Scout relevant files for the feature
2. Analyze codebase context
3. Generate implementation plan
4. Save to specs/ directory

Run:
! ~/.claude/commands/custom/scout-and-plan.sh "$ARGUMENTS"
```

**Script**:
```bash
#!/bin/bash
FEATURE="$1"
DEPTH="${2:-4}"

echo "Scout→Plan Workflow for: $FEATURE"
echo "Depth: $DEPTH"

# Execute scout
python agents/scout.py "$FEATURE" "$DEPTH"

# Generate plan (would integrate with your ADW system)
echo "Plan generation complete"
```

### Example 3: Specialized Agent

**File**: `~/.claude/agents/mem0-integrator.md`

```markdown
---
name: mem0-integrator
description: "Integrate memory operations with workflow context"
category: orchestration
tools: [Read, Write, Bash]
mcp-servers: []
---

# Mem0 Integration Agent

## Triggers
- Memory persistence requests during workflows
- Cross-session context needs
- Knowledge graph operations

## Behavioral Mindset
Maintain context across sessions by strategically persisting and retrieving
memories. Balance between too much noise and missing critical context.

## Focus Areas
- **Memory Operations**: write_memory, read_memory, list_memories
- **Context Preservation**: Session state, task progress, decisions made
- **Knowledge Retrieval**: Relevant context loading at session start

## Key Actions
1. **Session Start**: list_memories() → read_memory("plan") → resume context
2. **During Work**: write_memory() for milestones and decisions
3. **Session End**: write_memory("summary") → checkpoint state

## Outputs
- **Memory Keys**: Structured keys (plan_*, task_*, checkpoint_*)
- **Session Summaries**: Progress reports with next actions
- **Context Files**: Persistent files in ai_docs/memory/

## Boundaries
**Will:**
- Persist critical context and decisions
- Load relevant memories at session start
- Maintain structured memory schema

**Will Not:**
- Persist verbose or redundant information
- Override user memory management
- Auto-delete memories without confirmation
```

**Usage**: `@mem0-integrator` or in prompts: "Use the mem0-integrator approach"

---

## Integration with ADW Workflow

### Pattern 1: Enhanced Scout Command

**File**: `.claude/commands/scout-enhanced.md`

```markdown
---
name: scout-enhanced
description: "Scout with memory persistence and MCP integration"
category: orchestration
complexity: advanced
mcp-servers: [serena]
tools: [Bash, Read, Write]
argument-hint: "<task> <depth>"
---

# Enhanced Scout with Memory

Scouts codebase and persists findings to memory for cross-session use.

## Workflow
1. Execute haiku scout subagent
2. Generate relevant_files.json
3. Persist findings to mem0
4. Create structured reference docs

Run:
! .claude/commands/scripts/scout-enhanced.sh "$ARGUMENTS"
```

**Script**:
```bash
#!/bin/bash
TASK="$1"
DEPTH="$2"

# Run scout
python agents/scout.py "$TASK" "$DEPTH"

# Persist to memory (if mem0 available)
if command -v mem0 &> /dev/null; then
  mem0 write "scout_$TASK" < agents/scout_files/relevant_files.json
fi

# Generate reference doc
echo "Scout complete: agents/scout_files/relevant_files.json"
```

### Pattern 2: Plan with Documentation

**File**: `.claude/commands/plan-w-docs.md`

```markdown
---
name: plan-w-docs
description: "Generate plan with official docs lookup"
category: orchestration
complexity: advanced
mcp-servers: [context7]
tools: [Read, Write, Bash]
argument-hint: "<task> <docs-url> <scout-file>"
---

# Plan with Documentation

Generates implementation plan using official documentation.

## Workflow
1. Load scout results
2. Query Context7 for relevant docs
3. Generate ADW-format plan
4. Save to specs/

Implementation:
! python adw/workflow_ops.py plan "$ARGUMENTS"
```

### Pattern 3: Build with Validation

**File**: `.claude/commands/build-validate.md`

```markdown
---
name: build-validate
description: "Build with automated testing and validation"
category: orchestration
complexity: advanced
tools: [Bash, Read, Write, Edit]
argument-hint: "<spec-file>"
---

# Build with Validation

Implements spec with automatic testing and quality gates.

## Workflow
1. Load spec from specs/
2. Implement changes
3. Run tests
4. Generate build report
5. Validate against acceptance criteria

Implementation:
! python adw/workflow_ops.py build "$ARGUMENTS" --validate
```

### Pattern 4: Git Worktree Skills

**File**: `~/.claude/commands/custom/worktree-feature.md`

```markdown
---
name: worktree-feature
description: "Create feature branch with git worktree"
category: utility
tools: [Bash]
argument-hint: "<feature-name>"
---

# Git Worktree Feature Setup

Creates new worktree for feature development.

Run:
! ~/.claude/commands/custom/worktree-feature.sh "$ARGUMENTS"
```

**Script**:
```bash
#!/bin/bash
FEATURE="$1"
BRANCH="feature/$FEATURE"
WORKTREE_DIR="../worktrees/$FEATURE"

# Create worktree
git worktree add "$WORKTREE_DIR" -b "$BRANCH"

echo "Worktree created: $WORKTREE_DIR"
echo "Branch: $BRANCH"
echo ""
echo "To work on it: cd $WORKTREE_DIR"
```

---

## Advanced Patterns

### Multi-Agent Orchestration

**File**: `.claude/commands/parallel-review.md`

```markdown
---
name: parallel-review
description: "Parallel code review using multiple agents"
category: quality
complexity: expert
personas: [code-reviewer, security-analyst, performance-engineer]
tools: [Read, Grep, Task]
argument-hint: "<file-or-dir>"
---

# Parallel Code Review

Spawns multiple review agents in parallel for comprehensive analysis.

## Workflow
1. Spawn @code-reviewer for general review
2. Spawn @security-analyst for security check
3. Spawn @performance-engineer for performance review
4. Aggregate findings
5. Generate unified report

[Detailed instructions for Claude to coordinate agents...]
```

### Memory-Driven Workflow

**File**: `.claude/commands/resume-work.md`

```markdown
---
name: resume-work
description: "Resume work from previous session using memory"
category: orchestration
tools: [Bash]
---

# Resume Work Session

Loads context from previous session and resumes work.

## Workflow
1. list_memories() - show all memories
2. read_memory("current_plan") - load plan
3. read_memory("last_session_summary") - understand context
4. think_about_collected_information() - assess where we are
5. Continue work with full context

Execute workflow and present status report with next actions.
```

### Conditional MCP Activation

**File**: `.claude/commands/smart-analyze.md`

```markdown
---
name: smart-analyze
description: "Context-aware analysis with conditional MCP use"
category: analysis
complexity: advanced
mcp-servers: [context7, sequential, serena]
---

# Smart Contextual Analysis

Analyzes code with intelligent MCP server selection:

- **Frontend code** → Enable @magic for UI patterns
- **Complex logic** → Enable @sequential for deep analysis
- **Documentation needed** → Enable @context7 for official docs
- **Large codebase** → Enable @serena for semantic search

[Instructions for conditional MCP activation based on analysis target...]
```

---

## Best Practices

### 1. Naming Conventions

**Commands**:
- Use kebab-case: `my-command`, `scout-enhanced`
- Prefix with namespace: `custom:`, `sc:`, `adw:`
- Be descriptive: `git-status-check` not `gsc`

**Agents**:
- Use kebab-case: `code-reviewer`, `security-analyst`
- Focus on role: `debugger` not `debug-helper`
- Domain-specific: `mem0-integrator` not `memory-thing`

### 2. Documentation Standards

Every skill should have:
- Clear one-line description
- Usage examples
- Input/output specifications
- Error handling notes

### 3. Parameterization Strategy

**Good**:
```markdown
argument-hint: "<required> [optional] [--flag]"
---
Process file: $1
Options: ${2:-default}
```

**Bad**:
```markdown
# No hints
# Hardcoded values
# No defaults
```

### 4. Tool Coordination

**Explicit**:
```markdown
tools: [Read, Write, Grep]
---
1. Read source files
2. Grep for patterns
3. Write results
```

**Implicit**: Let Claude decide (less control)

### 5. Error Handling

**Scripts must**:
- Use `set -e` for fail-fast
- Validate inputs
- Provide clear error messages
- Exit with proper codes

```bash
#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Error: Missing argument"
  echo "Usage: $0 <file>"
  exit 1
fi
```

### 6. Testing Skills

```bash
# Test command exists
/help | grep my-command

# Test agent exists
@my-agent --help

# Test script directly
bash ~/.claude/commands/custom/my-script.sh test-arg

# Test with Claude
/my-command test-input
```

### 7. Version Control

**Include in repo**:
```
.claude/
├── commands/
│   └── project-specific.md
├── agents/
└── README.md  # Document custom skills
```

**Exclude**:
```gitignore
.claude/mcp.env.json     # Secrets
.claude/settings.local.json  # Local preferences
```

### 8. Performance Optimization

- Use haiku for scouts and light tasks
- Use sonnet for complex workflows
- Use opus only for critical decisions
- Batch operations in scripts
- Avoid redundant tool calls

---

## Troubleshooting

### Skill Not Appearing

**Symptom**: `/my-command` not found

**Checks**:
1. File location correct? (`~/.claude/commands/` or `.claude/commands/`)
2. File extension `.md`?
3. YAML frontmatter valid?
4. Restarted Claude Code?

**Debug**:
```bash
# List all command files
find ~/.claude/commands -name "*.md"
find .claude/commands -name "*.md"

# Check YAML syntax
cat ~/.claude/commands/custom/my-command.md | head -10

# Check logs
tail -f ~/.claude/logs/latest.log
```

### Skill Fails to Execute

**Symptom**: Error when running skill

**Checks**:
1. Script executable? `chmod +x script.sh`
2. Shebang present? `#!/bin/bash`
3. Path absolute? `~/.claude/...` not `./...`
4. Arguments passed? `$ARGUMENTS` or `"$1"`

**Debug**:
```bash
# Test script directly
bash -x ~/.claude/commands/custom/my-script.sh test-arg

# Check permissions
ls -la ~/.claude/commands/custom/

# Validate shell syntax
bash -n ~/.claude/commands/custom/my-script.sh
```

### Agent Not Recognized

**Symptom**: `@my-agent` doesn't work

**Checks**:
1. File in `agents/` not `commands/`?
2. Name matches in frontmatter and invocation?
3. YAML frontmatter complete?

**Fix**:
```bash
# Verify location
ls -la ~/.claude/agents/my-agent.md

# Check name field
grep "^name:" ~/.claude/agents/my-agent.md

# Restart Claude Code
```

### MCP Servers Not Loading

**Symptom**: Skill with `mcp-servers:` doesn't enable them

**Reality Check**: `mcp-servers:` is **documentation only** - it doesn't auto-enable MCPs.

**Actual Approach**:
```markdown
In your skill prompt:
"Enable @context7 and @sequential MCPs for this operation..."
```

Or pre-enable in project settings:
```json
// .claude/settings.local.json
{
  "enabledMcpjsonServers": ["context7", "sequential"]
}
```

### Argument Passing Issues

**Symptom**: Arguments not received by script

**Common Issues**:
```bash
# Wrong - loses spacing
! script.sh $ARGUMENTS

# Right - preserves arguments
! script.sh "$ARGUMENTS"

# Best - explicit parameters
! script.sh "$1" "$2" "$3"
```

---

## Appendix A: Skills API Reference

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Skill identifier (kebab-case) |
| `description` | string | Yes | One-line description |
| `category` | enum | No | utility\|quality\|analysis\|orchestration\|communication |
| `complexity` | enum | No | basic\|intermediate\|advanced\|expert |
| `mcp-servers` | array | No | MCP servers to suggest (docs only) |
| `personas` | array | No | Agents to invoke |
| `tools` | array | No | Tool access hints (docs only) |
| `argument-hint` | string | No | Usage hint for arguments |
| `model` | enum | No | sonnet\|opus\|haiku |
| `version` | string | No | Semantic version |
| `triggers` | array | No | Auto-activation patterns (agents) |

### Special Variables

| Variable | Context | Description |
|----------|---------|-------------|
| `$ARGUMENTS` | Commands | All arguments as string |
| `$1, $2, $3...` | Scripts | Positional parameters |
| `$@` | Scripts | All arguments as array |
| `$#` | Scripts | Argument count |

### Execution Syntax

```markdown
! /absolute/path/to/script.sh "$ARGUMENTS"
```

The `!` prefix executes shell command and injects output into conversation.

---

## Appendix B: ADW Integration Examples

### Complete Scout→Plan→Build Skill Set

**1. Scout Skill**
```markdown
---
name: adw-scout
description: "Scout codebase for relevant files"
argument-hint: "<task> <depth>"
---
! python agents/scout.py "$1" "$2"
```

**2. Plan Skill**
```markdown
---
name: adw-plan
description: "Generate implementation plan from scout results"
mcp-servers: [context7]
argument-hint: "<task> [docs-url]"
---
! python adw/workflow_ops.py plan "$1" "${2:-}" agents/scout_files/relevant_files.json
```

**3. Build Skill**
```markdown
---
name: adw-build
description: "Implement plan from specs"
argument-hint: "<spec-file>"
---
! python adw/workflow_ops.py build "$1"
```

**4. Orchestrator Skill**
```markdown
---
name: adw-full
description: "Full scout→plan→build workflow"
complexity: expert
argument-hint: "<task> [docs-url] [depth]"
---

# ADW Full Workflow

Execute complete ADW pipeline:

1. Scout: /adw-scout "$1" "${3:-4}"
2. Plan: /adw-plan "$1" "${2:-}"
3. Build: /adw-build [generated-spec-file]
4. Report: Generate build report in ai_docs/build_reports/

[Detailed orchestration instructions...]
```

---

## Appendix C: Skill Template Library

### Minimal Command Template

```markdown
---
name: my-command
description: "What this does"
---

Brief instructions for Claude...

! /path/to/script.sh "$ARGUMENTS"
```

### Full-Featured Command Template

```markdown
---
name: my-command
description: "One-line description"
category: utility
complexity: intermediate
mcp-servers: [context7]
tools: [Read, Write, Bash]
argument-hint: "<arg1> [arg2]"
version: "1.0.0"
---

# Command Name

## Description
Detailed description...

## Usage
```
/my-command <arg1> [arg2]
```

## Behavioral Flow
1. Step 1
2. Step 2
3. Step 3

## Tool Coordination
- **Read**: Purpose
- **Write**: Purpose

## Examples
[Examples...]

## Implementation
! /path/to/script.sh "$ARGUMENTS"
```

### Agent Template

```markdown
---
name: my-agent
description: "Agent role description"
category: quality
tools: [Read, Grep]
triggers: [pattern1, pattern2]
---

# Agent Name

## Triggers
- When to activate

## Behavioral Mindset
Philosophy...

## Focus Areas
- **Area 1**: Details
- **Area 2**: Details

## Key Actions
1. Action 1
2. Action 2

## Outputs
- **Output Type**: Description

## Boundaries
**Will:**
- Do X

**Will Not:**
- Won't do Y
```

---

## Conclusion

The Claude Code Skills system is a powerful extensibility framework that enables:

1. **Custom Workflows**: Reusable scout→plan→build patterns
2. **Specialized Agents**: Domain experts for quality, security, performance
3. **Tool Orchestration**: Coordinated use of native tools and MCP servers
4. **Memory Integration**: Persistent context across sessions
5. **Team Collaboration**: Shared skills in version control

### Next Steps for ADW Integration

1. **Create Base Skills**:
   - `/adw-scout`
   - `/adw-plan`
   - `/adw-build`

2. **Create Domain Agents**:
   - `@adw-architect` - System design
   - `@adw-reviewer` - Code review
   - `@adw-tester` - Test generation

3. **Integrate Memory**:
   - Session resume skills
   - Context preservation
   - Decision logging

4. **Add Git Workflows**:
   - Worktree management
   - Branch coordination
   - PR automation

5. **Document Team Skills**:
   - Shared in `.claude/`
   - Versioned with repo
   - Documented in README

---

**Further Reading**:
- [Custom Commands Documentation](https://docs.claude.com/en/docs/claude-code/slash-commands)
- [Custom Agents Guide](https://docs.claude.com/en/docs/claude-code/agents)
- [MCP Integration](https://docs.claude.com/en/docs/claude-code/mcp)
- [Hooks System](https://docs.claude.com/en/docs/claude-code/hooks)

**Repository**: `/Users/alexkamysz/AI/scout_plan_build_mvp`
**Skills Location**: `.claude/commands/` and `.claude/agents/`
