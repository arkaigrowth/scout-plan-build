# MCP, Hooks & Agent Fixes - Action Plan

## 🔴 Issue 1: Hooks Not Installed

### Can You Manually Copy?
**YES** - but with dependencies:

```bash
# From THIS repo to tax-prep (or test repo)
cp -r .claude/hooks /path/to/target-repo/.claude/

# Requirements for hooks to work:
# 1. Python 3.11+ ✓ (you have this)
# 2. uv installed ✓ (you have this)
# 3. python-dotenv (hooks will install via uv run)
```

### Will They Work?
✅ **YES** - Hooks use `#!/usr/bin/env -S uv run --script` with inline dependencies.

Each hook file has this header:
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///
```

**uv automatically installs dependencies** when the script runs!

### What Hooks Provide
- **Logging**: Session logs in `logs/[session-id]/`
- **Validation**: Pre-execution input validation
- **Debugging**: Post-execution audit trails
- **Observability**: Complete workflow tracking

---

## 🔴 Issue 2: No MCP Servers Enabled

### What Claude Doctor Shows
```
Agent Parse Errors
└ Failed to parse 6 agent file(s):
  └ interview-coach.md: Missing required "name" field
  └ vsl-director.md: Missing required "name" field
  └ outreach-orchestrator.md: Missing required "name" field
```

**This is why we're getting duplicates** - same 3 agents listed twice!

### Recommended MCP Servers for This Repo

Based on what scout-plan-build does, here's the optimal MCP configuration:

| MCP Server | Priority | Why You Need It |
|------------|----------|-----------------|
| **sequential-thinking** | 🔴 CRITICAL | Complex multi-step analysis (portability, architecture) |
| **context7** | 🟡 RECOMMENDED | Looking up official docs (Python, Git, Claude) |
| **serena** | 🟢 OPTIONAL | Symbol operations, project memory (nice-to-have) |
| **playwright** | 🟢 OPTIONAL | If testing web UIs (not core to this repo) |
| **morphllm** | 🟢 OPTIONAL | Bulk edits (could help with refactoring) |

**Minimum for scout-plan-build**: `sequential-thinking` + `context7`

### Global vs Repo-Level MCP Control

**Architecture**:
```
~/.claude/settings.json          # Global defaults
project/.claude/settings.json     # Project overrides (gitignored)
project/.claude/settings.local.json  # User-specific (gitignored)
```

**Recommended Setup**:

#### Global (~/.claude/settings.json)
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "context7-mcp"]
    }
  }
}
```

#### Per-Repo (.claude/settings.local.json)
```json
{
  "mcpServers": {
    "serena": {
      "command": "npx",
      "args": ["-y", "serena-mcp"]
    }
  }
}
```

This merges: global + repo-specific

### How to Enable Now

**Option 1: Interactive (Easy)**
```bash
claude mcp add sequential-thinking
claude mcp add context7
```

**Option 2: Manual (Precise)**
Edit `~/.claude/settings.json`:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "context7-mcp"]
    }
  }
}
```

Then restart Claude Code.

---

## 🔴 Issue 3: Agent Parse Errors

### The Problem
3 agents missing `name` field in frontmatter:
- `interview-coach.md`
- `vsl-director.md`
- `outreach-orchestrator.md`

### The Fix

Each agent file needs frontmatter like:
```markdown
---
name: interview-coach
description: Technical interview preparation specialist
---

# Interview Coach
...
```

**Current format** (missing `name`):
```markdown
# Interview Coach
...
```

### Quick Fix Script

```bash
# Fix interview-coach.md
cat > ~/.claude/agents/interview-coach.md << 'EOF'
---
name: interview-coach
description: Technical interview preparation and behavioral coaching
---

[existing content...]
EOF
```

Or I can fix them programmatically.

---

## 📋 Recommended Actions (Priority Order)

### 1. Fix Agent Frontmatter (2 minutes)
**Why First**: Causing parser errors every session

```bash
# I can create a fix script for you
./scripts/fix_agent_frontmatter.sh
```

### 2. Enable MCP Servers (3 minutes)
**Why Second**: Needed for complex analysis tasks

```bash
claude mcp add sequential-thinking
claude mcp add context7
# Restart Claude Code
```

### 3. Copy Hooks Manually (1 minute)
**Why Third**: Test if they work before adding to installer

```bash
# To test repo
cp -r .claude/hooks /tmp/test-tax-repo/.claude/

# Test if they work
cd /tmp/test-tax-repo
# Run any command and check logs/ directory appears
```

### 4. Update Installer (5 minutes)
**Why Last**: After we verify hooks work

Add hooks + skills to `scripts/install_to_new_repo.sh`

---

## 🎯 Best Practices for MCP

### Global Default MCPs (Recommended)

For **all your projects**, enable these globally:

```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "context7-mcp"]
    }
  }
}
```

**Why these two?**
- **sequential-thinking**: Universal need for multi-step reasoning
- **context7**: Universal need for documentation lookup

### Project-Specific MCPs

Add to `.claude/settings.local.json` (gitignored) when needed:

**For frontend projects**:
```json
{
  "mcpServers": {
    "playwright": {...}  // Browser testing
  }
}
```

**For data projects**:
```json
{
  "mcpServers": {
    "duckdb": {...}  // Data analysis
  }
}
```

**For large refactoring**:
```json
{
  "mcpServers": {
    "morphllm": {...},  // Bulk edits
    "serena": {...}     // Symbol operations
  }
}
```

### Simple Control Pattern

**Enable globally** = Always available, all projects
**Enable locally** = Only when project needs it
**Disable** = Add to local settings with `"disabled": true`

```json
// .claude/settings.local.json
{
  "mcpServers": {
    "playwright": {
      "disabled": true  // Disable global MCP for this project
    }
  }
}
```

---

## ⚡ Quick Start (Do This Now)

```bash
# 1. Fix agents (I'll create the script)
./scripts/fix_agent_frontmatter.sh

# 2. Enable essential MCPs
claude mcp add sequential-thinking
claude mcp add context7

# 3. Verify
claude doctor

# 4. Test hooks manually
cp -r .claude/hooks /tmp/test-tax-repo/.claude/
```

---

## 📊 Context Budget

You have **28% remaining** (56K tokens).

**Priority for context**:
1. Fix agent errors (quick)
2. Enable MCPs (quick)
3. Test hooks (medium)
4. Update installer (can do in next session)

**Estimated usage**:
- Agent fixes: ~2K tokens
- MCP setup: ~3K tokens
- Hooks testing: ~5K tokens
- **Total**: ~10K tokens (leaves 18% buffer)

We're good to proceed!