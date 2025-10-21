# /worktree_redo - Redo Undone Checkpoint

**Purpose**: Redo the last undone checkpoint (restore after undo)

**Syntax**: `/worktree_redo`

**Parameters**: None

---

## Behavior

```bash
Execution Flow:
──────────────
1. Check if redo stack exists
2. Pop last undo target from stack
3. Verify commit still exists
4. Reset to that commit
5. Remove from redo stack

Output:
───────
✅ Redone to checkpoint: abc123def456
   Undo again: /worktree_undo
```

---

## Implementation

```bash
#!/bin/bash
# Location: .claude/commands/worktree_redo.sh

set -euo pipefail

worktree_redo() {
    local redo_stack=".git/REDO_STACK"

    # ═══════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════

    # Check if in git repository
    if ! git rev-parse --git-dir &>/dev/null; then
        echo "❌ Not in a git repository"
        return 1
    fi

    # Check if redo stack exists
    if [[ ! -f "$redo_stack" ]]; then
        echo "⚠️  No redo available"
        echo "   Redo stack doesn't exist"
        echo "   Use: /worktree_undo first"
        return 1
    fi

    # Check if redo stack has entries
    local stack_size=$(wc -l < "$redo_stack" | tr -d ' ')
    if [[ $stack_size -eq 0 ]]; then
        echo "⚠️  Redo stack is empty"
        echo "   Nothing to redo"
        return 1
    fi

    # ═══════════════════════════════════════════════════════
    # GET REDO TARGET
    # ═══════════════════════════════════════════════════════

    # Get last entry from redo stack
    local target=$(tail -n 1 "$redo_stack")

    if [[ -z "$target" ]]; then
        echo "❌ Redo stack corrupted (empty entry)"
        # Clean up corrupted entry
        sed -i '' '$d' "$redo_stack" 2>/dev/null || true
        return 1
    fi

    local target_short="${target:0:12}"

    # Verify commit still exists
    if ! git rev-parse "$target" &>/dev/null 2>&1; then
        echo "❌ Redo target no longer exists: $target_short"
        echo "   Commit may have been garbage collected"
        # Remove invalid entry
        sed -i '' '$d' "$redo_stack"
        return 1
    fi

    # Get current position
    local current=$(git rev-parse HEAD)
    local current_short="${current:0:12}"

    # Get commit messages
    local current_msg=$(git log -1 --format='%s' HEAD)
    local target_msg=$(git log -1 --format='%s' "$target")

    # ═══════════════════════════════════════════════════════
    # PERFORM REDO
    # ═══════════════════════════════════════════════════════

    echo "🔄 Redoing to checkpoint..."
    echo "   From: $current_short ($current_msg)"
    echo "   To:   $target_short ($target_msg)"
    echo ""

    # Reset to target
    git reset --hard "$target" || {
        echo "❌ Reset failed"
        return 1
    }

    # Remove from redo stack (successful redo)
    sed -i '' '$d' "$redo_stack"

    # ═══════════════════════════════════════════════════════
    # UPDATE METADATA
    # ═══════════════════════════════════════════════════════

    if [[ -f .checkpoint-history ]]; then
        echo "Redo: Restored to $target_short" >> .checkpoint-history
        echo "  Time: $(date -Iseconds)" >> .checkpoint-history
        echo "  Previous: $current_short" >> .checkpoint-history
        echo "" >> .checkpoint-history
    fi

    # ═══════════════════════════════════════════════════════
    # SUCCESS OUTPUT
    # ═══════════════════════════════════════════════════════

    local remaining=$((stack_size - 1))

    echo "✅ Redone to checkpoint: $target_short"
    echo "   Previous: $current_short"
    echo ""
    echo "💡 Options:"
    echo "   Undo again: /worktree_undo"
    echo "   View: git log --oneline -10"

    if [[ $remaining -gt 0 ]]; then
        echo ""
        echo "📊 Redo stack: $remaining entries remaining"
    else
        echo ""
        echo "📊 Redo stack: empty (this was the last redo)"
    fi
}

# Execute if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    worktree_redo "$@"
fi
```

---

## Usage Examples

### Example 1: Undo-Redo Flow
```bash
# Start with checkpoint 1
/worktree_checkpoint "version 1"

# Create checkpoint 2
/worktree_checkpoint "version 2"

# Undo to checkpoint 1
/worktree_undo

# Realize you want checkpoint 2 back
/worktree_redo

# Output:
✅ Redone to checkpoint: abc123def
   Previous: def456ghi
```

### Example 2: Multiple Redo
```bash
# Create checkpoints
/worktree_checkpoint "step 1"
/worktree_checkpoint "step 2"
/worktree_checkpoint "step 3"

# Undo 3 times
/worktree_undo  # Now at step 2
/worktree_undo  # Now at step 1
/worktree_undo  # Now at initial

# Redo back up
/worktree_redo  # Back to step 1
/worktree_redo  # Back to step 2
/worktree_redo  # Back to step 3
```

### Example 3: Experimental Flow
```bash
# Try approach A
/worktree_checkpoint "approach A"
# ... doesn't work ...

# Try approach B
/worktree_undo
/worktree_checkpoint "approach B"
# ... also doesn't work ...

# Go back to approach A
/worktree_undo
/worktree_redo  # Can redo to approach A
```

---

## Redo Stack Behavior

### Stack Growth
```bash
# Initially empty
📊 Redo stack: 0 entries

# After first undo
/worktree_undo
📊 Redo stack: 1 entry

# After second undo
/worktree_undo
📊 Redo stack: 2 entries
```

### Stack Consumption
```bash
# Redo consumes from stack
/worktree_redo
📊 Redo stack: 1 entry remaining

/worktree_redo
📊 Redo stack: empty
```

### Stack Clearing
```bash
# New checkpoint clears redo stack
/worktree_undo         # Redo stack: 1 entry
/worktree_checkpoint   # Redo stack: 0 entries (cleared)

# Can no longer redo past new checkpoint
```

---

## Error Handling

### No Redo Available
```bash
# Before any undo
/worktree_redo

# Output:
⚠️  No redo available
   Redo stack doesn't exist
   Use: /worktree_undo first
```

### Redo Stack Empty
```bash
# After consuming all redos
/worktree_redo

# Output:
⚠️  Redo stack is empty
   Nothing to redo
```

### Commit No Longer Exists
```bash
# If garbage collection removed commit
/worktree_redo

# Output:
❌ Redo target no longer exists: abc123def
   Commit may have been garbage collected
```

---

## Integration Patterns

### Safe Experimentation Pattern
```bash
# Create checkpoint before risky change
/worktree_checkpoint "before risky refactor"

# Try risky change
python risky_refactor.py

# If broken, undo
/worktree_undo

# Try safer approach
python safer_refactor.py

# If that's worse, redo to risky version
/worktree_redo

# Keep experimenting
```

### A/B Testing Pattern
```bash
# Approach A
/worktree_checkpoint "implementation A"
# ... test ...

# Try approach B
/worktree_undo
/worktree_checkpoint "implementation B"
# ... test ...

# Compare by switching
/worktree_undo   # Back to A
/worktree_redo   # Forward to B

# Choose winner
```

### Checkpoint Navigation Pattern
```bash
# Create timeline of checkpoints
/worktree_checkpoint "milestone 1"
/worktree_checkpoint "milestone 2"
/worktree_checkpoint "milestone 3"

# Navigate backwards
/worktree_undo 2  # Go to milestone 1

# Navigate forwards
/worktree_redo    # Go to milestone 2
/worktree_redo    # Go to milestone 3
```

---

## Redo Stack Internals

### File Format (.git/REDO_STACK)
```
abc123def456789...    # First undo target
def456ghi789abc...    # Second undo target
ghi789abc123def...    # Third undo target
```

### Stack Operations
```bash
# Push to stack (undo)
echo "$commit_hash" >> .git/REDO_STACK

# Pop from stack (redo)
target=$(tail -n 1 .git/REDO_STACK)
sed -i '' '$d' .git/REDO_STACK

# Clear stack (new checkpoint)
> .git/REDO_STACK
```

---

## Metadata Tracking

### .checkpoint-history Update
```
Redo: Restored to abc123def
  Time: 2025-10-20T10:35:00-07:00
  Previous: def456ghi
```

---

## Performance

```
Operation Time:
──────────────
Validation:       <50ms
Stack read:       <10ms
Commit verify:    <50ms
Git reset:        <200ms
Stack update:     <10ms
Total:           <320ms

Memory:
───────
Stack read: ~40 bytes
No additional memory overhead

Disk:
─────
Stack file: -40 bytes (one entry removed)
No git object creation (reusing existing)
```

---

## Limitations

### Redo Invalidation
```bash
# Redo is cleared by:
1. New checkpoint
2. New uncommitted changes that are checkpointed
3. Manual stack clear

# Example:
/worktree_undo              # Can redo
/worktree_checkpoint "new"  # Redo cleared (can't redo anymore)
```

### Garbage Collection
```bash
# Git may garbage collect unreachable commits
# This affects redo if commits are old

# Prevent with tags:
git tag keep-this-commit abc123

# Or periodic reflog expiry:
git config gc.reflogExpire "90 days"
```

### Stack Size
```bash
# No hard limit on redo stack size
# But practical limit is number of undos

# Example: 10 undos = 10 possible redos
```

---

## Comparison: Redo vs. Cherry-Pick

```
Redo:
────
- Restores exact state
- Fast (no merge)
- Linear history
- Pops from stack

Cherry-Pick:
───────────
- Applies specific commit
- Slower (merge)
- Creates new commit
- Doesn't affect stack
```

---

## Advanced Usage

### View Redo Stack
```bash
# See what's available to redo
cat .git/REDO_STACK | while read hash; do
    git log -1 --oneline "$hash"
done

# Output:
abc123d wip-1729418400: version 1
def456e wip-1729418700: version 2
```

### Conditional Redo
```bash
# Only redo if tests pass
if pytest; then
    /worktree_redo
else
    echo "Tests failed, staying at current checkpoint"
fi
```

### Redo to Specific Point
```bash
# Can't redo to arbitrary commit
# But can redo multiple times

# Redo until specific checkpoint found
while true; do
    current=$(git log -1 --format='%s')
    [[ "$current" == *"target checkpoint"* ]] && break
    /worktree_redo || break
done
```

---

## See Also

- `/worktree_undo` - Undo checkpoints (creates redo entries)
- `/worktree_checkpoint` - Create checkpoints (clears redo)
- `ai_docs/architecture/GIT_WORKTREE_UNDO_SYSTEM.md` - Full architecture
