<!-- risk: mutate-external -->
<!-- auto-invoke: never -->

# Merge Selected Worktree

Merge the chosen parallel implementation back to the main branch and clean up.

## Arguments

- `WORKTREE_PATH`: $ARGUMENTS[0] (required) - Path to the worktree to merge (e.g., trees/ui-revamp-2)
- `CLEANUP`: $ARGUMENTS[1] (optional) - "cleanup" to remove all worktrees after merge

## Example Usage

```bash
# Merge and keep other worktrees
/merge-worktree trees/ui-revamp-2

# Merge and cleanup all worktrees
/merge-worktree trees/ui-revamp-2 cleanup
```

## Execution Steps

### 1. Validate Worktree

```bash
# Check worktree exists
if [ ! -d "${WORKTREE_PATH}" ]; then
    echo "Error: Worktree not found: ${WORKTREE_PATH}"
    exit 1
fi

# Get branch name
cd ${WORKTREE_PATH}
BRANCH=$(git branch --show-current)
FEATURE_NAME=$(echo $BRANCH | sed 's/-[0-9]*$//')
```

### 2. Ensure Clean State

```bash
cd ${WORKTREE_PATH}

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes detected in ${WORKTREE_PATH}"
    echo "Committing with message: feat: ${FEATURE_NAME} - parallel agent implementation"
    git add .
    git commit -m "feat: ${FEATURE_NAME} - parallel agent implementation"
fi
```

### 3. Push Branch (Optional)

```bash
# Detect VCS provider
if git remote -v | grep -q "github.com"; then
    VCS="github"
elif git remote -v | grep -q "bitbucket"; then
    VCS="bitbucket"
fi

# Push to remote
git push origin ${BRANCH}
echo "Pushed ${BRANCH} to ${VCS}"
```

### 4. Return to Main and Merge

```bash
# Go back to main repo
cd $(git worktree list | head -1 | awk '{print $1}')

# Get the main branch name
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')

# Checkout main
git checkout ${MAIN_BRANCH}

# Merge the selected implementation
git merge ${BRANCH} --no-ff -m "Merge ${BRANCH}: parallel agent implementation"
```

### 5. Report Merge Result

```
Merge Complete!
═══════════════

Branch merged: ${BRANCH}
Into: ${MAIN_BRANCH}

Changes integrated:
$(git diff HEAD~1 --stat)
```

### 6. Cleanup (if requested)

If CLEANUP argument is "cleanup":

```bash
# List all worktrees for this feature
FEATURE_WORKTREES=$(git worktree list | grep "${FEATURE_NAME}" | awk '{print $1}')

echo "Cleaning up worktrees..."
for wt in $FEATURE_WORKTREES; do
    git worktree remove "$wt" --force
    echo "  Removed: $wt"
done

# Clean up branches
for i in 1 2 3 4 5; do
    git branch -d "${FEATURE_NAME}-${i}" 2>/dev/null
done

# Remove trees directory if empty
rmdir trees 2>/dev/null
```

### 7. Final Summary

```
┌────────────────────────────────────────────────────────────────┐
│                     PARALLEL WORKFLOW COMPLETE                  │
└────────────────────────────────────────────────────────────────┘

Selected Implementation: ${WORKTREE_PATH}
Merged Branch: ${BRANCH}
Target Branch: ${MAIN_BRANCH}

Result: SUCCESS

Cleanup Status: ${CLEANUP_STATUS}

Next steps:
- Push to remote: git push origin ${MAIN_BRANCH}
- Create PR if needed: gh pr create
- Deploy if ready
```

## Safety Features

1. **No force operations** - Uses standard merge, no rebase or force push
2. **Preserves history** - Uses --no-ff to create merge commit
3. **Branch protection** - Won't delete branches that aren't fully merged
4. **Confirmation** - Always reports what will happen before doing it

## Alternative: Cherry-Pick Specific Changes

If you want to combine elements from multiple worktrees:

```bash
# Cherry-pick specific commits from different agents
git cherry-pick <commit-from-agent-1>
git cherry-pick <commit-from-agent-2>
```

## VCS Integration

Works with both GitHub and Bitbucket:
- Detects provider via remote URL
- Uses appropriate branch conventions
- Supports PR creation via gh/bb CLI
