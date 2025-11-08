# Agent Cleanup Analysis & Recommendations

## Current State
- **26 custom agents** in ~/.claude/agents/
- **17 created Sep 1** (bulk import from template)
- **Mixed quality** - some overlap with built-in agents
- **Confusion factor** - hard to know which to use when

## Agent Overlap Analysis

### 🔴 REDUNDANT - Delete These (Built-in is Better)
| Your Agent | Built-in Equivalent | Why Delete |
|------------|-------------------|------------|
| python-expert.md | Task(subagent_type="python-expert") | Exact duplicate |
| root-cause-analyst.md | Task(subagent_type="root-cause-analyst") | Exact duplicate |
| system-architect.md | Task(subagent_type="system-architect") | Exact duplicate |
| backend-architect.md | Task(subagent_type="backend-architect") | Exact duplicate |
| frontend-architect.md | Task(subagent_type="frontend-architect") | Exact duplicate |
| code-reviewer.md | Task(subagent_type="code-reviewer") | Exact duplicate |
| security-engineer.md | Task(subagent_type="security-engineer") | Exact duplicate |
| requirements-analyst.md | Task(subagent_type="requirements-analyst") | Exact duplicate |
| technical-writer.md | Task(subagent_type="technical-writer") | Exact duplicate |
| debugger.md | Task(subagent_type="debugger") | Exact duplicate |
| test-automator.md | Task(subagent_type="test-automator") | Exact duplicate |
| performance-engineer.md | Task(subagent_type="performance-engineer") | Exact duplicate |
| quality-engineer.md | Task(subagent_type="quality-engineer") | Exact duplicate |
| refactoring-expert.md | Task(subagent_type="refactoring-expert") | Exact duplicate |
| devops-architect.md | Task(subagent_type="devops-architect") | Exact duplicate |
| learning-guide.md | Task(subagent_type="learning-guide") | Exact duplicate |
| socratic-mentor.md | Task(subagent_type="socratic-mentor") | Exact duplicate |

### 🟡 UNIQUE - Keep These (No Built-in Equivalent)
| Your Agent | Purpose | Keep Because |
|------------|---------|--------------|
| duckdb-data-analyst.md | SQL analysis on CSV/Excel | Specialized for data analysis |
| interview-coach.md | Interview prep | Domain-specific |
| vsl-director.md | Video sales letters | Domain-specific |
| outreach-orchestrator.md | Marketing outreach | Domain-specific |
| frontend-debug.md | React/CSS debugging | More specific than generic debugger |

### 🟠 QUESTIONABLE - Review These
| Your Agent | Status | Notes |
|------------|--------|-------|
| security-auditor.md | Maybe redundant | Check if different from security-engineer |
| angular/ folder | Keep if doing Angular | 8 Angular-specific agents |
| wshobson/ folder | Unknown | 12 files - check if personal project |

## The Real Problem

**You're experiencing "Agent Proliferation Syndrome":**
1. Multiple versions of same capability
2. No clear selection criteria
3. Custom agents becoming stale as built-ins improve
4. Confusion leads to wrong choices (like root-cause for architecture)

## Cleanup Script

```bash
#!/bin/bash
# backup first!
mkdir -p ~/.claude/agents_backup
cp -r ~/.claude/agents/* ~/.claude/agents_backup/

# Remove redundant agents
cd ~/.claude/agents/
rm -f python-expert.md
rm -f root-cause-analyst.md
rm -f system-architect.md
rm -f backend-architect.md
rm -f frontend-architect.md
rm -f code-reviewer.md
rm -f security-engineer.md
rm -f requirements-analyst.md
rm -f technical-writer.md
rm -f debugger.md
rm -f test-automator.md
rm -f performance-engineer.md
rm -f quality-engineer.md
rm -f refactoring-expert.md
rm -f devops-architect.md
rm -f learning-guide.md
rm -f socratic-mentor.md
rm -f security-auditor.md  # likely duplicate

echo "Cleaned up 18 redundant agents"
echo "Kept 4-5 unique domain-specific agents"
```

## Best Practices Going Forward

### 1. Use Built-in Agents First
```python
# GOOD - Use built-in
Task(subagent_type="system-architect", prompt="analyze portability")

# BAD - Custom agent when built-in exists
Task(subagent_type="custom-architect", prompt="analyze portability")
```

### 2. Agent Selection Cheatsheet

| Task Type | Right Agent | Wrong Agent |
|-----------|------------|-------------|
| Architecture analysis | system-architect | root-cause-analyst |
| Debugging failures | root-cause-analyst | system-architect |
| Code review | code-reviewer | quality-engineer |
| Security audit | security-engineer | code-reviewer |
| Performance issues | performance-engineer | debugger |
| Requirements gathering | requirements-analyst | socratic-mentor |
| Teaching/explaining | learning-guide | technical-writer |

### 3. When to Create Custom Agents

**DO Create** for:
- Domain-specific tools (duckdb-data-analyst)
- Industry verticals (interview-coach)
- Company-specific workflows

**DON'T Create** for:
- General programming tasks
- Standard architectural patterns
- Common debugging scenarios

### 4. Agent Maintenance Strategy

```yaml
quarterly_review:
  - Compare custom vs built-in capabilities
  - Delete redundant agents
  - Update unique agents with new patterns

naming_convention:
  custom_agents: "domain-[name].md"  # e.g., domain-tax-analyzer.md
  project_agents: "proj-[name].md"   # e.g., proj-mvp-validator.md

documentation:
  - Keep AGENTS_INDEX.md listing what each does
  - Note which built-in agent it extends/replaces
```

## Recommendation

**Immediate Action:**
1. Run the cleanup script (after backup)
2. Keep only unique domain-specific agents
3. Create an index file for remaining agents

**For Portability Analysis:**
Use the correct built-in agent:
```python
Task(
    subagent_type="system-architect",  # NOT root-cause-analyst
    prompt="Analyze scout_plan_build_mvp for portability..."
)
```

**Result:**
- From 26 agents → 4-5 unique ones
- Clearer selection criteria
- Better use of built-in capabilities
- Less confusion, better results