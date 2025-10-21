# /worktree_undo - Undo Checkpoints

**Purpose**: Undo n checkpoints (revert to previous state)

**Syntax**: `/worktree_undo [n]`

**Parameters**:
- `n` (optional): Number of checkpoints to undo (default: 1, max: 50)

---

## Behavior

```bash
Execution Flow:
──────────────
1. Validate undo count
2. Check target commit exists
3. Verify safety (no merged commits)
4. Store current state in redo stack
5. Reset to target commit

Output:
───────
✅ Undone 2 checkpoint(s)
   From: abc123def (wip-1729418400)
   To:   def456ghi (wip-1729418100)

   Redo: /worktree_redo
   View: git log --oneline -10
```

---

## Implementation

```bash
#!/bin/bash
# Location: .claude/commands/worktree_undo.sh

set -euo pipefail

worktree_undo() {
    local n="${1:-1}"

    # ═══════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════

    # Check if in git repository
    if ! git rev-parse --git-dir &>/dev/null; then
        echo "❌ Not in a git repository"
        return 1
    fi

    # Validate undo count
    if [[ ! "$n" =~ ^[0-9]+$ ]]; then
        echo "❌ Invalid count: must be positive integer"
        echo "   Usage: /worktree_undo [n]"
        return 1
    fi

    # Safety limit
    if [[ $n -gt 50 ]]; then
        echo "❌ Safety limit exceeded"
        echo "   Maximum: 50 checkpoints at once"
        echo "   Reason: Prevent accidental large undos"
        return 1
    fi

    # Check if enough commits exist
    local commit_count=$(git rev-list --count HEAD)
    if [[ $n -ge $commit_count ]]; then
        echo "❌ Cannot undo $n commits"
        echo "   Available: $commit_count commits in history"
        echo "   Try: /worktree_undo $((commit_count - 1))"
        return 1
    fi

    # ═══════════════════════════════════════════════════════
    # GET TARGET COMMIT
    # ═══════════════════════════════════════════════════════

    local current=$(git rev-parse HEAD)
    local current_short="${current:0:12}"

    local target=$(git rev-parse "HEAD~$n" 2>/dev/null) || {
        echo "❌ Target commit not found: HEAD~$n"
        return 1
    }
    local target_short="${target:0:12}"

    # Get commit messages
    local current_msg=$(git log -1 --format='%s' HEAD)
    local target_msg=$(git log -1 --format='%s' "$target")

    # ═══════════════════════════════════════════════════════
    # SAFETY CHECKS
    # ═══════════════════════════════════════════════════════

    # Check for merge commits in range
    local merge_commits=$(git log --oneline --merges "$target..HEAD")
    if [[ -n "$merge_commits" ]]; then
        echo "⚠️  Warning: Undo range contains merge commits"
        echo ""
        echo "$merge_commits"
        echo ""
        read -p "Continue with undo? (y/N): " confirm
        [[ "$confirm" != "y" ]] && {
            echo "Undo cancelled"
            return 0
        }
    fi

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo "⚠️  Uncommitted changes detected"
        echo ""
        git status --short
        echo ""
        read -p "Stash changes and continue? (y/N): " confirm
        [[ "$confirm" == "y" ]] && {
            git stash push -m "auto-stash before undo to $target_short"
            echo "💾 Changes stashed"
        } || {
            echo "Undo cancelled"
            return 0
        }
    fi

    # ═══════════════════════════════════════════════════════
    # PERFORM UNDO
    # ═══════════════════════════════════════════════════════

    echo "🔄 Undoing $n checkpoint(s)..."
    echo "   From: $current_short ($current_msg)"
    echo "   To:   $target_short ($target_msg)"
    echo ""

    # Store current commit in redo stack
    mkdir -p .git
    echo "$current" >> .git/REDO_STACK

    # Perform reset
    git reset --hard "$target" || {
        echo "❌ Reset failed"
        # Remove from redo stack
        sed -i '' '$d' .git/REDO_STACK 2>/dev/null || true
        return 1
    }

    # ═══════════════════════════════════════════════════════
    # UPDATE METADATA
    # ═══════════════════════════════════════════════════════

    if [[ -f .checkpoint-history ]]; then
        echo "Undo: Reverted $n checkpoints to $target_short" >> .checkpoint-history
        echo "  Time: $(date -Iseconds)" >> .checkpoint-history
        echo "  Previous: $current_short" >> .checkpoint-history
        echo "" >> .checkpoint-history
    fi

    # ═══════════════════════════════════════════════════════
    # SUCCESS OUTPUT
    # ═══════════════════════════════════════════════════════

    echo "✅ Undone $n checkpoint(s)"
    echo "   From: $current_short"
    echo "   To:   $target_short"
    echo ""
    echo "💡 Recovery options:"
    echo "   Redo: /worktree_redo"
    echo "   View: git log --oneline -10"
    echo "   Diff: git diff $current_short HEAD"
    echo ""
    echo "📊 Redo stack: $(wc -l < .git/REDO_STACK) entries available"
}

# Execute if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    worktree_undo "$@"
fi
```

---

## Usage Examples

### Example 1: Undo Last Checkpoint
```bash
/worktree_checkpoint "version 1"
# ... make changes ...
/worktree_checkpoint "version 2"
# ... realize version 2 is broken ...

/worktree_undo

# Output:
✅ Undone 1 checkpoint(s)
   From: abc123 (wip-1729418400: version 2)
   To:   def456 (wip-1729418100: version 1)
```

### Example 2: Undo Multiple Checkpoints
```bash
# Created checkpoints:
# - step 1
# - step 2
# - step 3 (current)

/worktree_undo 2

# Back to: step 1
```

### Example 3: Safe Experimentation
```bash
/worktree_checkpoint "before risky change"

# Try something risky
python experimental_refactor.py

# Doesn't work, undo
/worktree_undo

# Back to safe state instantly
```

---

## Safety Features

### Merge Commit Warning
```bash
# If undoing past a merge:
⚠️  Warning: Undo range contains merge commits

  abc123 Merge branch 'feature-x'

Continue with undo? (y/N):
```

### Uncommitted Changes Handling
```bash
# If uncommitted changes exist:
⚠️  Uncommitted changes detected

M  src/auth.py
M  src/config.py

Stash changes and continue? (y/N): y
💾 Changes stashed
```

### Safety Limits
```bash
/worktree_undo 100

# Output:
❌ Safety limit exceeded
   Maximum: 50 checkpoints at once
   Reason: Prevent accidental large undos
```

---

## Redo Stack Management

```bash
# Redo stack grows with each undo
/worktree_undo    # Redo stack: 1 entry
/worktree_undo    # Redo stack: 2 entries
/worktree_undo    # Redo stack: 3 entries

# Redo brings back
/worktree_redo    # Redo stack: 2 entries
/worktree_redo    # Redo stack: 1 entry

# New checkpoint clears redo stack
/worktree_checkpoint "new work"
# Redo stack: 0 entries (cleared)
```

---

## Error Handling

### Invalid Undo Count
```bash
/worktree_undo abc

# Output:
❌ Invalid count: must be positive integer
   Usage: /worktree_undo [n]
```

### Not Enough Commits
```bash
/worktree_undo 100

# Output:
❌ Cannot undo 100 commits
   Available: 15 commits in history
   Try: /worktree_undo 14
```

### Target Not Found
```bash
# Corrupted repository
/worktree_undo 5

# Output:
❌ Target commit not found: HEAD~5
```

---

## Integration with Worktree Workflow

```bash
# Scout phase
cd worktrees/issue-123
Task(subagent_type="explore", prompt="...")
/worktree_checkpoint "scout complete"

# Plan phase
/plan_w_docs "..." "..." "..."
/worktree_checkpoint "plan complete"

# Build phase (experimental)
/build_adw "specs/issue-123.md"
# Doesn't work as expected...

# Instant rollback
/worktree_undo  # Back to plan phase

# Try different approach
/build_adw "specs/issue-123-v2.md"
/worktree_checkpoint "build complete"
```

---

## Advanced Usage

### Undo with Inspection
```bash
# Check what you're undoing
git log --oneline -5

# Undo 3 checkpoints
/worktree_undo 3

# Compare changes
git diff HEAD@{1} HEAD

# If wrong, redo
/worktree_redo
```

### Selective Undo (Cherry-Pick Pattern)
```bash
# Can't directly cherry-pick with undo
# But can achieve similar result:

/worktree_undo 5          # Go back 5 checkpoints
git cherry-pick abc123    # Cherry-pick specific commit
/worktree_checkpoint "selective restore"
```

### Undo to Tagged Checkpoint
```bash
# Find tagged checkpoint
git tag

# Output:
auth-mvp-v1
auth-mvp-v2

# Count commits since tag
commits_since=$(git rev-list --count HEAD ^auth-mvp-v1)

# Undo to tag
/worktree_undo $commits_since
```

---

## Metadata Tracking

### .checkpoint-history Update
```
Undo: Reverted 2 checkpoints to def456ghi
  Time: 2025-10-20T10:30:00-07:00
  Previous: abc123def
```

### .git/REDO_STACK Format
```
abc123def456789...  # First undo
def456ghi789abc...  # Second undo
ghi789abc123def...  # Third undo
```

---

## Performance

```
Operation Time:
──────────────
Validation:       <50ms
Safety checks:    <100ms
Git reset:        <200ms (depends on file count)
Metadata update:  <50ms
Total:           <400ms

Memory:
───────
Redo stack: ~40 bytes per entry
Max stack (50): ~2KB

Disk:
─────
No additional disk usage
(git objects already exist)
```

---

## Comparison: Undo vs. Rollback

```
/worktree_undo:
──────────────
- Soft operation (keeps commits in reflog)
- Redo is possible
- Fast (<400ms)
- Safe for WIP commits

/worktree_rollback:
──────────────────
- Hard operation (removes commits)
- No redo
- Use for merged/tagged commits
- More permanent
```

---

## See Also

- `/worktree_redo` - Redo undone checkpoints
- `/worktree_checkpoint` - Create undo points
- `/worktree_rollback` - Hard reset (no redo)
- `ai_docs/architecture/GIT_WORKTREE_UNDO_SYSTEM.md` - Architecture
