---
description: Compare all parallel agent implementations for a feature, showing diff stats and test status.
argument-hint: <feature_name>
---

<!-- risk: read-only -->
<!-- auto-invoke: safe -->

# Compare Parallel Worktree Results

Display comparison of all parallel agent implementations for a feature.

## Arguments

- `FEATURE_NAME`: $ARGUMENTS[0] (required) - Feature name matching worktree prefix

## Example Usage

```bash
/compare-worktrees ui-revamp
```

## Execution Steps

### 1. Find All Worktrees

```bash
WORKTREES=$(ls -d trees/${FEATURE_NAME}-* 2>/dev/null)
```

If no worktrees found, error: "No worktrees found for feature: ${FEATURE_NAME}"

### 2. Gather Statistics for Each Worktree

For each worktree, collect:

```bash
cd ${worktree}

# Branch name
BRANCH=$(git branch --show-current)

# Diff stats vs main
DIFF_STATS=$(git diff main --stat | tail -1)

# Files changed count
FILES_CHANGED=$(git diff main --name-only | wc -l)

# Lines added/removed
LINES=$(git diff main --shortstat)

# Last commit
LAST_COMMIT=$(git log -1 --oneline)

# Test status (if tests exist)
if [ -f package.json ]; then
    npm test 2>/dev/null && TEST_STATUS="Pass" || TEST_STATUS="Fail"
elif [ -f pyproject.toml ]; then
    pytest 2>/dev/null && TEST_STATUS="Pass" || TEST_STATUS="Fail"
else
    TEST_STATUS="N/A"
fi
```

### 3. Display Comparison Table

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL IMPLEMENTATION COMPARISON                     │
│                         Feature: ${FEATURE_NAME}                          │
└──────────────────────────────────────────────────────────────────────────┘

| # | Worktree | Branch | Files | Lines +/- | Tests | Status |
|---|----------|--------|-------|-----------|-------|--------|
| 1 | trees/${FEATURE_NAME}-1 | ${FEATURE_NAME}-1 | 5 | +120/-30 | Pass | Ready |
| 2 | trees/${FEATURE_NAME}-2 | ${FEATURE_NAME}-2 | 7 | +200/-50 | Pass | Ready |
| 3 | trees/${FEATURE_NAME}-3 | ${FEATURE_NAME}-3 | 4 | +80/-20 | Fail | Issues |
```

### 4. Show Detailed Diffs

For each worktree, show what files changed:

```
Agent 1 (trees/${FEATURE_NAME}-1):
────────────────────────────────
  src/components/Dashboard.tsx  | 45 +++++++++----
  src/styles/theme.css          | 22 +++++++
  src/utils/format.ts           | 15 +++++
  tests/Dashboard.test.tsx      | 38 +++++++++++

Agent 2 (trees/${FEATURE_NAME}-2):
────────────────────────────────
  src/components/Dashboard.tsx  | 62 ++++++++++++++----
  src/components/Card.tsx       | 35 ++++++++++
  src/hooks/useTheme.ts         | 28 +++++++++
  ...
```

### 5. Suggest Actions

```
Comparison complete!

Quick exploration commands:
──────────────────────────
# View Agent 1's changes
cd trees/${FEATURE_NAME}-1 && git diff main

# Run Agent 2's version (port 5175)
cd trees/${FEATURE_NAME}-2 && npm run dev

# View side-by-side diff
diff -r trees/${FEATURE_NAME}-1/src trees/${FEATURE_NAME}-2/src

Next steps:
───────────
1. Test each version visually (run on different ports)
2. Review code quality in each
3. Merge the best: /merge-worktree trees/${FEATURE_NAME}-N
```

### 6. Optional: AI Analysis

If requested, use Claude to analyze the differences:

```
Task: Analyze the three implementations and recommend which to merge based on:
- Code quality and readability
- Test coverage
- Architectural patterns
- Performance implications
```

## Output Files

Optionally save comparison to:
```
ai_docs/reviews/${FEATURE_NAME}-parallel-comparison.md
```
