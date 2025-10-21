# CLAUDE.local.md - Local Environment Configuration

**Purpose:** Local overrides and custom configurations for your specific development environment.

## Local Tool Availability

Mark which tools are actually available in your environment:

```yaml
tools_available:
  # External AI Tools (usually not installed)
  gemini: false          # Google Gemini CLI
  opencode: false        # OpenCode CLI
  codex: false          # OpenAI Codex CLI
  claude_haiku: true     # Claude with haiku model

  # Standard Tools (usually available)
  gh_cli: true          # GitHub CLI
  git: true             # Git version control
  docker: false         # Docker containers

  # Custom Tools (your additions)
  mem0: false           # Memory system
  archon: false         # Kanban task management
  custom_skills: []     # List your custom skills here
```

## Environment Variables

```bash
# Core (Required)
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_PAT="ghp_..."
export GITHUB_REPO_URL="https://github.com/owner/repo"

# Optional Integrations
export MEM0_API_KEY=""           # If using mem0
export ARCHON_API_URL=""         # If using Archon
export ARCHON_API_KEY=""         # If using Archon

# Git Worktree Configuration
export GIT_WORKTREE_BASE="$HOME/worktrees"  # Base directory for worktrees
export GIT_AUTO_COMMIT_INTERVAL=300          # Auto-commit every 5 minutes
```

## Local Workflows

### Git Worktree Strategy

```bash
# Create worktree for each feature
git worktree add $GIT_WORKTREE_BASE/feature-auth feature/auth

# Work in isolated environment
cd $GIT_WORKTREE_BASE/feature-auth

# Auto-commit for undo history
git add . && git commit -m "WIP: $(date +%Y%m%d-%H%M%S)"
```

### Memory Integration Points

```yaml
memory_hooks:
  pre_scout: "mem0_recall_context"      # Load relevant memories
  post_plan: "mem0_save_plan"          # Save plan for future reference
  post_build: "mem0_save_patterns"     # Learn from implementations
  on_error: "mem0_save_failure"        # Remember what didn't work
```

## Custom Skills

Place your custom skills in `.claude/skills/`:

```yaml
skills:
  - name: "mem0_integration"
    trigger: "memory operations"
    path: ".claude/skills/mem0.md"

  - name: "archon_tasks"
    trigger: "task management"
    path: ".claude/skills/archon.md"

  - name: "worktree_manager"
    trigger: "branch operations"
    path: ".claude/skills/worktree.md"
```

## Local Parallel Execution

```python
# Configure parallelization based on your machine
parallel_config = {
    "max_concurrent_agents": 4,      # Adjust based on CPU/RAM
    "timeout_seconds": 180,          # 3 minutes per agent
    "retry_attempts": 2,              # Retry failed agents
    "use_async": True,                # Enable async execution
}
```

## Integration Preferences

```yaml
integrations:
  mem0:
    enabled: false
    auto_save: true
    recall_depth: 10

  archon:
    enabled: false
    auto_create_tasks: false
    sync_interval: 300

  git_worktrees:
    enabled: false
    auto_create: true
    cleanup_after_merge: true
```

## Override Scout Behavior

```python
# Custom scout implementation using available tools
def local_scout(task: str) -> dict:
    """Your local scout implementation"""
    # Use whatever tools you have available
    if tools_available["claude_haiku"]:
        return scout_with_haiku(task)
    else:
        return scout_with_native_tools(task)
```

## Notes

- This file is `.gitignore`d - it's for your local environment only
- Update `tools_available` based on what you actually have installed
- Configure integrations as you add them
- Override any behavior that doesn't work in your environment

---

*This file allows you to customize the workflow for your specific setup without affecting the shared repository.*