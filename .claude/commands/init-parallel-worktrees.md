# Initialize Parallel Worktrees

Create N parallel git worktrees for concurrent agent development.

**Pattern Source:** [IndyDevDan Git Worktree Parallelization](../../ai_docs/research/videos/idd-video-git-worktrees-f8RnRuaxee8-analysis.md)

## Arguments

- `FEATURE_NAME`: $ARGUMENTS[0] (required) - Name for the feature branch prefix
- `NUM_AGENTS`: $ARGUMENTS[1] (default: 3) - Number of parallel worktrees to create

## Example Usage

```bash
/init-parallel-worktrees ui-revamp 3
```

## Execution Steps

### 1. Validate Input

Validate FEATURE_NAME contains only alphanumeric characters, dashes, and underscores.
If invalid, report error and stop.

### 2. Check Prerequisites

```bash
# Ensure we're in a git repo
git rev-parse --git-dir

# Check for uncommitted changes
git status --porcelain
```

If uncommitted changes exist, warn user and ask to proceed or abort.

### 3. Create Trees Directory

```bash
mkdir -p trees
```

### 4. Create Parallel Worktrees

For each agent number 1 through NUM_AGENTS, execute IN PARALLEL:

```bash
# Create worktree with new branch
git worktree add -b ${FEATURE_NAME}-${N} ./trees/${FEATURE_NAME}-${N}

# Copy environment file if exists
if [ -f .env ]; then
    cp .env ./trees/${FEATURE_NAME}-${N}/.env
fi

# Detect and install dependencies
if [ -f ./trees/${FEATURE_NAME}-${N}/package.json ]; then
    cd ./trees/${FEATURE_NAME}-${N} && npm install
elif [ -f ./trees/${FEATURE_NAME}-${N}/pyproject.toml ]; then
    cd ./trees/${FEATURE_NAME}-${N} && uv sync
elif [ -f ./trees/${FEATURE_NAME}-${N}/requirements.txt ]; then
    cd ./trees/${FEATURE_NAME}-${N} && pip install -r requirements.txt
fi
```

### 5. Report Results

Output a summary table:

| Worktree | Branch | Path | Port (suggested) | Status |
|----------|--------|------|------------------|--------|
| Agent 1 | ${FEATURE_NAME}-1 | trees/${FEATURE_NAME}-1 | 5174 | Created |
| Agent 2 | ${FEATURE_NAME}-2 | trees/${FEATURE_NAME}-2 | 5175 | Created |
| Agent 3 | ${FEATURE_NAME}-3 | trees/${FEATURE_NAME}-3 | 5176 | Created |

### 6. Next Steps Hint

```
Worktrees ready! Next steps:

1. Create your spec: specs/${FEATURE_NAME}-spec.md
2. Run parallel agents: /run-parallel-agents specs/${FEATURE_NAME}-spec.md ${FEATURE_NAME}
3. Compare results: /compare-worktrees ${FEATURE_NAME}
4. Merge best: /merge-worktree trees/${FEATURE_NAME}-N
```

## Cleanup Command

To remove all worktrees for a feature:

```bash
git worktree list | grep ${FEATURE_NAME} | awk '{print $1}' | xargs -I {} git worktree remove {}
```
