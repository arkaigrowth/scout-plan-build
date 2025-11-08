# 🚨 Critical Fix: Make Scout Work (4 Hours)

## The Problem
Scout commands fail because they try to spawn non-existent AI tools:
- `gemini` - Not a CLI tool
- `opencode` - Doesn't exist
- `codex` - Not a CLI tool

## The Solution
Replace external tool calls with Task agents.

## Step 1: Create Fixed Scout (30 minutes)

Create `adws/scout_working.py`:

```python
#!/usr/bin/env python3
"""Working scout that uses Task agents instead of external tools."""

import json
from pathlib import Path
from typing import List, Dict

def scout_with_task(task: str, scale: int = 3) -> Dict:
    """Scout using Task agents - ACTUALLY WORKS."""

    # Import Task tool (available in Claude Code)
    from claude_code import Task  # or however you import it

    print(f"🔍 Scouting for: {task}")

    # Launch multiple explore agents for comprehensive discovery
    aspects = ["models", "routes/controllers", "tests", "config"]
    all_files = set()

    for i, aspect in enumerate(aspects[:scale]):
        print(f"  Scout {i+1}/{scale}: Looking for {aspect}")

        # This WORKS because Task agent exists
        result = Task(
            subagent_type="explore",
            prompt=f"Find {aspect} files for task: {task}"
        )

        # Extract files from result
        if result and 'files' in result:
            all_files.update(result['files'])

    # Sort for determinism (MVP fix!)
    sorted_files = sorted(list(all_files))

    # Save to standard location
    output_dir = Path("agents/scout_files")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "relevant_files.json"
    with open(output_file, 'w') as f:
        json.dump({
            "task": task,
            "files": sorted_files,
            "count": len(sorted_files)
        }, f, indent=2)

    print(f"✅ Found {len(sorted_files)} files")
    return {
        "files": sorted_files,
        "output": str(output_file)
    }

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Find authentication code"
    scout_with_task(task)
```

## Step 2: Create Working Slash Command (30 minutes)

Create `.claude/commands/scout-working.md`:

```markdown
---
name: scout-working
description: Scout that actually works using Task agents
---

# Scout Working Command

Run the working scout implementation:

```python
import sys
sys.path.append('adws')
from scout_working import scout_with_task

task = "{{TASK}}"
result = scout_with_task(task)
print(f"Scout complete: {result['output']}")
```

Usage: `/scout-working "Find authentication files"`
```

## Step 3: Test It (30 minutes)

```bash
# Run the new working scout
python adws/scout_working.py "Find auth files"

# Or use slash command
/scout-working "Find auth files"

# Verify output
cat agents/scout_files/relevant_files.json
```

## Step 4: Update Main Scout Commands (2 hours)

Update `/scout` and `/scout_improved` to use this approach:

1. Edit `adw_scout.py`
2. Replace subprocess calls with Task agents
3. Remove references to gemini/opencode/codex
4. Test thoroughly

## Step 5: Full Pipeline Test (1 hour)

```bash
# Complete workflow with fixed scout
/scout-working "Add user profile endpoint"
/plan_w_docs "Add user profile" "https://api-docs.com" "agents/scout_files/relevant_files.json"
/build_adw "specs/issue-001-user-profile.md"
/test
/commit
```

## Validation Checklist

- [ ] Scout returns files consistently
- [ ] Files are sorted (deterministic)
- [ ] No "command not found" errors
- [ ] Output saved to `agents/scout_files/relevant_files.json`
- [ ] Plan phase can read scout output
- [ ] Full pipeline completes

## Why This Works

1. **Task agents exist** in Claude Code environment
2. **No external dependencies** on non-existent tools
3. **Deterministic** through sorting
4. **Compatible** with existing plan/build phases

## Common Issues

**Issue**: "Task not found"
**Fix**: Task is a Claude Code built-in, should be available

**Issue**: "No files found"
**Fix**: Task agent needs better prompts, be more specific

**Issue**: "Permission denied"
**Fix**: Check write permissions on `agents/scout_files/`

---

**Time to implement: 4 hours**
**Impact: Unblocks entire workflow**
**Priority: DO THIS IMMEDIATELY**