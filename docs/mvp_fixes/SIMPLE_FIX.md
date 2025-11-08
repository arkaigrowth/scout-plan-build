# The 5-Minute Fix (What We Should Have Done)

## For Scout Commands

Just comment out the external tool calls in `.claude/commands/scout.md`:

```markdown
# OLD (broken):
- `gemini-g "[prompt]"`
- `opencode run "[prompt]"`
- `codex exec "[prompt]"`

# NEW (working):
# Just use Task agents instead:
Task(subagent_type="explore", prompt="[prompt]")
```

## For Plan Command

The issue: `adw_plan.py` expects issue numbers, not descriptions.

Quick fix options:

1. **Use a fake issue number**:
   ```bash
   python adws/adw_plan.py "001" "task-id"
   ```

2. **Use the slash command** (recommended):
   ```
   /plan_w_docs "your task" "docs" "files.json"
   ```

3. **Modify adw_plan.py** to accept task descriptions:
   ```python
   # Change line 80 from:
   issue_number = sys.argv[1]
   # To:
   task_description = sys.argv[1]
   ```

## The Real Lesson

**Don't create new code when you can fix existing code with a comment!**

The original scout commands have:
- ✅ Parallel execution (we lost this!)
- ✅ Timeout management (we lost this!)
- ✅ Git safety checks (we lost this!)
- ❌ Broken external tools (easy to comment out)

We threw out the baby with the bathwater!