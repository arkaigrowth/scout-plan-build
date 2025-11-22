# Run Parallel Agents

Execute N Claude agents in parallel, each implementing the same spec in their own worktree.

**Pattern Source:** [IndyDevDan Git Worktree Parallelization](../../ai_docs/research/videos/idd-video-git-worktrees-f8RnRuaxee8-analysis.md)

## Arguments

- `SPEC_FILE`: $ARGUMENTS[0] (required) - Path to the spec/plan file
- `FEATURE_NAME`: $ARGUMENTS[1] (required) - Feature name matching worktree prefix

## Example Usage

```bash
/run-parallel-agents specs/ui-revamp-spec.md ui-revamp
```

## Execution Steps

### 1. Validate Inputs

- Verify SPEC_FILE exists and is readable
- Verify worktrees exist matching pattern `trees/${FEATURE_NAME}-*`

### 2. Read Spec Content

```bash
SPEC_CONTENT=$(cat ${SPEC_FILE})
```

### 3. Detect Available Worktrees

```bash
WORKTREES=$(ls -d trees/${FEATURE_NAME}-* 2>/dev/null)
```

If no worktrees found, error: "No worktrees found. Run /init-parallel-worktrees first."

### 4. Launch Parallel Agents

For each worktree, spawn a Claude agent using the Task tool with parallel execution:

```
Use the Task tool to spawn N parallel agents:

For each worktree in WORKTREES:
  Task(
    subagent_type="general-purpose",
    description="Implement spec in ${worktree}",
    prompt="""
    Working directory: ${worktree}

    Implement the following specification:

    ${SPEC_CONTENT}

    Requirements:
    1. Work ONLY within this worktree directory
    2. Make all necessary code changes
    3. Run tests if available
    4. Commit your changes with message: "feat: ${FEATURE_NAME} - agent implementation"
    5. Report what you implemented and any issues encountered
    """
  )
```

### 5. Monitor Progress

Display progress as agents work:

```
Parallel Agent Execution
========================

[Agent 1] trees/${FEATURE_NAME}-1: Working...
[Agent 2] trees/${FEATURE_NAME}-2: Working...
[Agent 3] trees/${FEATURE_NAME}-3: Working...

Waiting for all agents to complete...
```

### 6. Collect Results

After all agents complete, gather results:

```bash
# For each worktree
cd trees/${FEATURE_NAME}-${N}
git diff --stat HEAD~1  # Show what changed
git log -1 --oneline    # Show commit message
```

### 7. Report Summary

| Agent | Worktree | Commits | Files Changed | Status |
|-------|----------|---------|---------------|--------|
| 1 | trees/${FEATURE_NAME}-1 | 1 | 5 files | Success |
| 2 | trees/${FEATURE_NAME}-2 | 1 | 7 files | Success |
| 3 | trees/${FEATURE_NAME}-3 | 0 | - | Failed |

### 8. Next Steps

```
Parallel execution complete!

Next steps:
1. Compare implementations: /compare-worktrees ${FEATURE_NAME}
2. Test each version:
   - cd trees/${FEATURE_NAME}-1 && npm run dev  # port 5174
   - cd trees/${FEATURE_NAME}-2 && npm run dev  # port 5175
3. Merge the best: /merge-worktree trees/${FEATURE_NAME}-N
```

## Key Insight

> "LLMs are non-deterministic probabilistic machines. Same prompt → different results.
> This is a FEATURE, not a bug. Run N agents, get N futures, pick the best."
> — IndyDevDan

## Error Handling

- If an agent fails, continue with others (don't abort all)
- Log failures to `trees/${worktree}/agent_error.log`
- Include failure reason in final summary
