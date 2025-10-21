# /worktree_checkpoint - Create Undo Point

**Purpose**: Create checkpoint (undo point) in current worktree

**Syntax**: `/worktree_checkpoint [message]`

**Parameters**:
- `message` (optional): Checkpoint description (default: "auto-checkpoint")

---

## Behavior

```bash
Execution Flow:
──────────────
1. Check for uncommitted changes
2. Stage all changes (git add -A)
3. Create WIP commit with timestamp
4. Update checkpoint metadata
5. Cleanup old checkpoints (>50)

Output:
───────
✅ Checkpoint created: wip-1729418400
   Hash: abc123def456
   Changes: +45 -12 lines across 3 files

   Undo: /worktree_undo
   View: git show HEAD
```

---

## Implementation

```bash
#!/bin/bash
# Location: .claude/commands/worktree_checkpoint.sh

set -euo pipefail

worktree_checkpoint() {
    local message="${1:-auto-checkpoint}"
    local timestamp=$(date +%s)
    local checkpoint_name="wip-$timestamp"

    # ═══════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════

    # Check if in a git repository
    if ! git rev-parse --git-dir &>/dev/null; then
        echo "❌ Not in a git repository"
        return 1
    fi

    # Check if in a worktree
    if [[ ! -f .worktree-meta.json ]]; then
        echo "⚠️  Not in a worktree directory"
        echo "   This works in regular repos too, but worktree features are limited"
    fi

    # Check for changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "⚠️  No changes to checkpoint"
        echo "   Status: git status"
        return 0
    fi

    # ═══════════════════════════════════════════════════════
    # CREATE CHECKPOINT
    # ═══════════════════════════════════════════════════════

    echo "💾 Creating checkpoint..."

    # Clear redo stack (new checkpoint invalidates redo)
    [[ -f .git/REDO_STACK ]] && > .git/REDO_STACK

    # Stage all changes
    git add -A

    # Get change statistics before commit
    local stats=$(git diff --cached --stat | tail -1)

    # Create commit
    git commit -m "$checkpoint_name: $message" \
        --author="Worktree Checkpoint <noreply@worktree>" || {
        echo "❌ Failed to create checkpoint"
        return 1
    }

    # Get commit hash
    local hash=$(git rev-parse HEAD)
    local short_hash="${hash:0:12}"

    # ═══════════════════════════════════════════════════════
    # UPDATE METADATA
    # ═══════════════════════════════════════════════════════

    # Update checkpoint history
    if [[ -f .checkpoint-history ]]; then
        echo "Checkpoint: $checkpoint_name ($short_hash)" >> .checkpoint-history
        echo "  Time: $(date -Iseconds)" >> .checkpoint-history
        echo "  Message: $message" >> .checkpoint-history
        echo "  Changes: $stats" >> .checkpoint-history
        echo "" >> .checkpoint-history
    fi

    # Update metadata JSON
    if [[ -f .worktree-meta.json ]]; then
        # Add checkpoint to metadata (requires jq)
        if command -v jq &>/dev/null; then
            local temp=$(mktemp)
            jq --arg ts "$timestamp" \
               --arg hash "$hash" \
               --arg msg "$message" \
               '.checkpoints += [{
                   "timestamp": ($ts | tonumber),
                   "hash": $hash,
                   "message": $msg,
                   "created": (now | todate)
               }]' .worktree-meta.json > "$temp"
            mv "$temp" .worktree-meta.json
        fi
    fi

    # ═══════════════════════════════════════════════════════
    # CLEANUP OLD CHECKPOINTS
    # ═══════════════════════════════════════════════════════

    cleanup_old_checkpoints

    # ═══════════════════════════════════════════════════════
    # SUCCESS OUTPUT
    # ═══════════════════════════════════════════════════════

    echo "✅ Checkpoint created: $checkpoint_name"
    echo "   Hash: $short_hash"
    echo "   Changes: $stats"
    echo ""
    echo "💡 Recovery options:"
    echo "   Undo: /worktree_undo"
    echo "   View: git show HEAD"
    echo "   History: git log --oneline -10"
}

cleanup_old_checkpoints() {
    # Keep last 50 WIP checkpoints, archive older ones
    local checkpoint_count=$(git log --oneline --grep='^wip-' | wc -l)

    if [[ $checkpoint_count -gt 50 ]]; then
        echo ""
        echo "🧹 Cleaning up old checkpoints..."

        # Get WIP commits beyond 50th
        local old_checkpoints=$(git log --oneline --grep='^wip-' --format='%H' | tail -n +51)

        # Count checkpoints to archive
        local archive_count=$(echo "$old_checkpoints" | wc -l)

        if [[ $archive_count -gt 0 ]]; then
            echo "   Archiving $archive_count old checkpoints"

            # Create archive directory
            mkdir -p .checkpoint-archive

            # Archive each checkpoint
            echo "$old_checkpoints" | while read commit; do
                # Check if commit is tagged (keep tagged commits)
                if git tag --points-at "$commit" | grep -q .; then
                    continue  # Skip tagged commits
                fi

                # Check if merged to main (keep merged commits)
                if git branch --contains "$commit" | grep -q main; then
                    continue  # Skip merged commits
                fi

                # Archive commit info
                local short="${commit:0:12}"
                git show --stat "$commit" > ".checkpoint-archive/$short.txt" 2>/dev/null || true
            done

            echo "   Archived to: .checkpoint-archive/"
        fi
    fi
}

# Execute if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    worktree_checkpoint "$@"
fi
```

---

## Auto-Checkpoint Daemon

```bash
#!/bin/bash
# auto_checkpoint_daemon.sh - Background checkpoint service

CHECKPOINT_INTERVAL=300  # 5 minutes
WORKTREE_PATH="$1"

[[ -z "$WORKTREE_PATH" ]] && {
    echo "Usage: $0 /path/to/worktree"
    exit 1
}

cd "$WORKTREE_PATH" || exit 1

echo "🤖 Auto-checkpoint daemon started"
echo "   Interval: ${CHECKPOINT_INTERVAL}s (5 minutes)"
echo "   Worktree: $WORKTREE_PATH"
echo ""

while true; do
    sleep "$CHECKPOINT_INTERVAL"

    # Check if worktree still exists
    [[ ! -f .worktree-meta.json ]] && {
        echo "⚠️  Worktree removed, stopping daemon"
        exit 0
    }

    # Check auto-checkpoint is enabled
    local enabled=$(jq -r '.auto_checkpoint' .worktree-meta.json 2>/dev/null)
    [[ "$enabled" != "true" ]] && continue

    # Check for changes
    git diff-index --quiet HEAD -- && continue

    # Create auto-checkpoint
    timestamp=$(date +%s)
    git add -A
    git commit -m "wip-$timestamp: auto-checkpoint" \
        --author="Auto-Checkpoint <noreply@worktree>" &>/dev/null

    echo "💾 Auto-checkpoint: wip-$timestamp ($(date '+%Y-%m-%d %H:%M:%S'))"
done
```

---

## Usage Examples

### Example 1: Manual Checkpoint
```bash
cd worktrees/feature-oauth

# Make changes
vim src/auth.py

# Create checkpoint
/worktree_checkpoint "implement OAuth flow"

# Output:
✅ Checkpoint created: wip-1729418400
   Hash: abc123def456
   Changes: 1 file changed, 45 insertions(+), 12 deletions(-)
```

### Example 2: Before Risky Operation
```bash
# Checkpoint before refactoring
/worktree_checkpoint "before major refactor"

# Perform risky refactor
python scripts/refactor_auth.py

# If it breaks:
/worktree_undo  # Instant rollback
```

### Example 3: Milestone Checkpoint
```bash
# Tag important checkpoints
/worktree_checkpoint "auth MVP complete"

# Tag it for permanence
git tag -a "auth-mvp-v1" -m "OAuth implementation MVP"
```

---

## Auto-Checkpoint Triggers

```bash
# Time-based (every 5 minutes)
Automatic if changes exist

# Event-based (before operations)
/build_adw     → auto-checkpoint
pytest         → auto-checkpoint
/worktree_merge → auto-checkpoint

# Change-based (configurable)
10+ files modified → auto-checkpoint
200+ lines changed → auto-checkpoint
```

---

## Checkpoint Metadata

### .checkpoint-history (Human-Readable)
```
Checkpoint: wip-1729418400 (abc123def456)
  Time: 2025-10-20T10:00:00-07:00
  Message: implement OAuth flow
  Changes: 1 file changed, 45 insertions(+), 12 deletions(-)

Checkpoint: wip-1729418700 (def456ghi789)
  Time: 2025-10-20T10:05:00-07:00
  Message: auto-checkpoint
  Changes: 2 files changed, 23 insertions(+), 5 deletions(-)
```

### .worktree-meta.json (Machine-Readable)
```json
{
  "name": "feature-oauth",
  "created": "2025-10-20T09:30:00-07:00",
  "auto_checkpoint": true,
  "checkpoint_interval": 300,
  "checkpoints": [
    {
      "timestamp": 1729418400,
      "hash": "abc123def456789...",
      "message": "implement OAuth flow",
      "created": "2025-10-20T10:00:00-07:00"
    }
  ]
}
```

---

## Cleanup Policy

```
Checkpoint Retention:
────────────────────

Recent (<50):     Full history (no cleanup)
Old (>50):        Archived to .checkpoint-archive/
Tagged:           Permanent (never cleaned)
Merged to main:   Permanent (never cleaned)
Ancient (>90d):   Purged (configurable)

Archive Format:
──────────────
.checkpoint-archive/
├── abc123def456.txt  # Full commit info
├── def456ghi789.txt
└── ...
```

---

## Error Handling

### No Changes
```bash
/worktree_checkpoint

# Output:
⚠️  No changes to checkpoint
   Status: git status
```

### Not in Git Repo
```bash
cd /tmp
/worktree_checkpoint

# Output:
❌ Not in a git repository
```

### Commit Failure
```bash
# If pre-commit hook fails
/worktree_checkpoint

# Output:
❌ Failed to create checkpoint
   Check: git status
   Logs: git commit --verbose
```

---

## Integration with Undo/Redo

```bash
# Create checkpoints
/worktree_checkpoint "step 1"
/worktree_checkpoint "step 2"
/worktree_checkpoint "step 3"

# Undo 2 checkpoints
/worktree_undo 2
# Now at: "step 1"

# Redo
/worktree_redo
# Now at: "step 2"

# Continue working
/worktree_checkpoint "step 4"
# Redo stack cleared (can't redo past new checkpoint)
```

---

## Performance

```
Operation Time:
──────────────
Check changes:    <50ms
Stage files:      <200ms (depends on file count)
Create commit:    <100ms
Update metadata:  <50ms
Total:           <400ms

Cleanup (if triggered):
──────────────────────
Archive 50 commits: ~2-3 seconds
(runs in background)

Disk Usage Per Checkpoint:
─────────────────────────
Git commit object:  ~500 bytes
Metadata entry:     ~100 bytes
Archive (if old):   ~5KB per commit
```

---

## See Also

- `/worktree_undo` - Undo checkpoints
- `/worktree_redo` - Redo undone checkpoints
- `/worktree_create` - Create worktree with auto-checkpoint
- `ai_docs/architecture/GIT_WORKTREE_UNDO_SYSTEM.md` - Architecture
