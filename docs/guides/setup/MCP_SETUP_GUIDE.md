# MCP Setup Guide - Essential Servers

## 🎯 Recommended Global MCP Configuration

For scout-plan-build and most development projects, enable these **globally**:

### 1. Sequential Thinking (CRITICAL)
**Why**: Complex multi-step analysis, architecture decisions, debugging

```bash
claude mcp add sequential-thinking
```

Or manually in `~/.claude/settings.json`:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

### 2. Context7 (RECOMMENDED)
**Why**: Official documentation lookup (Python, Git, frameworks)

```bash
claude mcp add context7
```

Or manually:
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "context7-mcp"]
    }
  }
}
```

## 📋 Complete Global Configuration

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

**After editing**: Restart Claude Code

## 🔧 Project-Specific MCP Overrides

For repos that need additional MCPs, create `.claude/settings.local.json` (gitignored):

### Example: Frontend Project
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"]
    }
  }
}
```

### Example: Data Analysis Project
```json
{
  "mcpServers": {
    "duckdb": {
      "command": "npx",
      "args": ["-y", "duckdb-mcp-server"]
    }
  }
}
```

### Example: Disable Global MCP
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "disabled": true
    }
  }
}
```

## ✅ Verification

After setup, run:
```bash
claude doctor
```

You should see:
```
✓ MCP Servers
  └ sequential-thinking: Connected
  └ context7: Connected
```

## 🎓 Best Practices

### When to Use Which MCP

| MCP Server | Use When | Example |
|------------|----------|---------|
| sequential-thinking | Complex analysis, multi-step reasoning | Architecture decisions, debugging |
| context7 | Need official docs | Python API lookup, framework patterns |
| playwright | Browser testing, E2E | Testing web UIs, visual validation |
| serena | Symbol operations, memory | Refactoring, code understanding |
| morphllm | Bulk code changes | Pattern-based edits across many files |

### Configuration Patterns

**Global** (`~/.claude/settings.json`):
- Universal tools (sequential, context7)
- Always-needed capabilities
- Shared across all projects

**Local** (`.claude/settings.local.json`):
- Project-specific needs
- Temporary additions
- User preferences (gitignored)

**Committed** (`.claude/settings.json` in repo):
- Team-wide MCP requirements
- Project conventions
- Shared across team members

## 📊 For Scout-Plan-Build Repo

**Minimum**:
- ✅ sequential-thinking
- ✅ context7

**Optional**:
- serena (if doing heavy symbol refactoring)
- morphllm (if doing bulk pattern changes)

**Not Needed**:
- playwright (no web UI in this repo)
- magic (no UI generation needed)

## 🚀 Quick Setup Now

```bash
# 1. Add essential MCPs
claude mcp add sequential-thinking
claude mcp add context7

# 2. Restart Claude Code
# (Exit and reopen)

# 3. Verify
claude doctor
```

Done! You now have the essential MCP servers enabled.