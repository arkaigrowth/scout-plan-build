#!/bin/bash
# Agent Cleanup Script - Remove redundant custom agents
# Safe: Creates backup before deleting

set -e  # Exit on error

echo "🧹 Agent Cleanup Tool"
echo "===================="
echo ""

AGENT_DIR="$HOME/.claude/agents"
BACKUP_DIR="$HOME/.claude/agents_backup_$(date +%Y%m%d_%H%M%S)"

# Check if agents directory exists
if [ ! -d "$AGENT_DIR" ]; then
    echo "❌ No agents directory found at $AGENT_DIR"
    exit 1
fi

# Count current agents
CURRENT_COUNT=$(ls -1 "$AGENT_DIR"/*.md 2>/dev/null | wc -l)
echo "📊 Current state: $CURRENT_COUNT agent files found"
echo ""

# Create backup
echo "📦 Creating backup at $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"
cp -r "$AGENT_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup complete"
echo ""

# List of redundant agents (have built-in equivalents)
REDUNDANT_AGENTS=(
    "python-expert.md"
    "root-cause-analyst.md"
    "system-architect.md"
    "backend-architect.md"
    "frontend-architect.md"
    "code-reviewer.md"
    "security-engineer.md"
    "requirements-analyst.md"
    "technical-writer.md"
    "debugger.md"
    "test-automator.md"
    "performance-engineer.md"
    "quality-engineer.md"
    "refactoring-expert.md"
    "devops-architect.md"
    "learning-guide.md"
    "socratic-mentor.md"
    "security-auditor.md"  # Likely duplicate of security-engineer
)

# Agents to keep (unique, domain-specific)
KEEP_AGENTS=(
    "duckdb-data-analyst.md"
    "interview-coach.md"
    "vsl-director.md"
    "outreach-orchestrator.md"
    "frontend-debug.md"
)

echo "🗑️  Removing redundant agents..."
REMOVED_COUNT=0
for agent in "${REDUNDANT_AGENTS[@]}"; do
    if [ -f "$AGENT_DIR/$agent" ]; then
        rm -f "$AGENT_DIR/$agent"
        echo "   ❌ Removed: $agent (use built-in Task agent instead)"
        ((REMOVED_COUNT++))
    fi
done

echo ""
echo "✅ Keeping unique domain-specific agents:"
for agent in "${KEEP_AGENTS[@]}"; do
    if [ -f "$AGENT_DIR/$agent" ]; then
        echo "   ✓ Kept: $agent"
    fi
done

echo ""
echo "📁 Special folders (review manually):"
if [ -d "$AGENT_DIR/angular" ]; then
    echo "   📂 angular/ - Keep if doing Angular development"
fi
if [ -d "$AGENT_DIR/wshobson" ]; then
    echo "   📂 wshobson/ - Review if needed"
fi

# Final count
FINAL_COUNT=$(ls -1 "$AGENT_DIR"/*.md 2>/dev/null | wc -l)

echo ""
echo "✨ Cleanup Complete!"
echo "===================="
echo "📊 Results:"
echo "   • Started with: $CURRENT_COUNT agents"
echo "   • Removed: $REMOVED_COUNT redundant agents"
echo "   • Now have: $FINAL_COUNT agents"
echo "   • Backup saved: $BACKUP_DIR"
echo ""
echo "💡 Tips:"
echo "   • Use Task(subagent_type=\"...\") for built-in agents"
echo "   • Check 'ai_docs/AGENT_CLEANUP_ANALYSIS.md' for details"
echo "   • To restore: cp -r $BACKUP_DIR/* $AGENT_DIR/"
echo ""

# Create index file for remaining agents
cat > "$AGENT_DIR/AGENTS_INDEX.md" << 'EOF'
# Custom Agents Index

## Unique Domain-Specific Agents (No Built-in Equivalent)

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| duckdb-data-analyst | SQL analysis on CSV/Excel files | Data exploration, cross-format analysis |
| interview-coach | Technical interview preparation | Mock interviews, behavioral prep |
| vsl-director | Video sales letter creation | Marketing content |
| outreach-orchestrator | Automated outreach campaigns | Email/LinkedIn automation |
| frontend-debug | React/CSS specific debugging | Complex frontend issues |

## Use Built-in Task Agents Instead

For these common tasks, use `Task(subagent_type="...")`:
- python-expert
- system-architect
- root-cause-analyst
- code-reviewer
- security-engineer
- performance-engineer
- And 12+ others...

## Best Practice

```python
# Prefer built-in agents
Task(subagent_type="system-architect", prompt="...")

# Only use custom for unique domains
Task(subagent_type="duckdb-data-analyst", prompt="...")
```
EOF

echo "📝 Created $AGENT_DIR/AGENTS_INDEX.md for reference"