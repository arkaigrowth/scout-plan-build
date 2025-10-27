# Plan: Simple Parallel Execution (The Right Way)

## Summary

Enable Test + Review + Document phases to run in parallel using simple bash-style background processes. Each phase gets a `--no-commit` flag and commits are aggregated at the end to avoid git conflicts.

**Method**: `subprocess.Popen()` for background processes + single commit at end
**Time to Implement**: 30 minutes (vs 10-12 hours for async approach)
**Lines of Code**: ~30 lines (vs 150+ lines for async)
**Expected Speedup**: 1.4-1.5x (same as async, way simpler)

## Problem Statement

### Current State (100% Serial)
```python
# adws/adw_sdlc.py - Sequential execution
subprocess.run(["uv", "run", "adw_test.py", issue, adw_id])      # 3-4 min
subprocess.run(["uv", "run", "adw_review.py", issue, adw_id])    # 2-3 min
subprocess.run(["uv", "run", "adw_document.py", issue, adw_id])  # 2-3 min
# Total: 7-10 minutes wasted
```

### Why We Can't Just Use asyncio
**Critical Discovery**: All three phases commit to git independently!

```python
# This would cause git conflicts:
async def broken_approach():
    await asyncio.gather(
        run_test(),    # Tries to commit at 10:00:05
        run_review(),  # Tries to commit at 10:00:05  ❌ CONFLICT!
        run_docs()     # Tries to commit at 10:00:06  ❌ CONFLICT!
    )
```

Git can't handle multiple parallel commits to the same workspace. We need either:
1. **Simple**: Run parallel, commit once at end (THIS APPROACH)
2. **Complex**: Git worktrees for isolation (future enhancement)

## Architecture: The Simple Solution

### Before (Serial - 7-10 minutes)
```
Test (3-4m) → Review (2-3m) → Document (2-3m)
```

### After (Parallel - 3-4 minutes)
```
[Test (3-4m) || Review (2-3m) || Document (2-3m)] → Single Commit
Max(3-4m, 2-3m, 2-3m) = 3-4 minutes
```

### Key Insight
**Don't commit during phases** - commit once at the end with aggregated results.

## Implementation Steps

### Step 1: Add `--no-commit` Flags to Phases (15 minutes)

Each phase script needs to skip its final commit when flag is present.

**Pattern** (apply to adw_test.py, adw_review.py, adw_document.py):

```python
def parse_args():
    # Add this to existing argparse
    parser.add_argument("--no-commit", action="store_true",
                       help="Skip git commit (for parallel execution)")
    return parser.parse_args()

def main():
    args = parse_args()

    # ... existing work ...

    # At the end, conditionally commit
    if not args.no_commit:
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", commit_msg])
    else:
        print("Skipping commit (--no-commit flag set)")
```

**Files to Modify**:
- `adws/adw_test.py` - Add `--no-commit` flag
- `adws/adw_review.py` - Add `--no-commit` flag
- `adws/adw_document.py` - Add `--no-commit` flag

### Step 2: Modify SDLC Orchestrator (15 minutes)

**File**: `adws/adw_sdlc.py`

```python
def run_parallel(issue_number: str, adw_id: str) -> bool:
    """Execute test/review/document phases in parallel"""
    print("\n=== PARALLEL EXECUTION (Test + Review + Document) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Start all three phases in background (no commits)
    test_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_test.py"),
        issue_number, adw_id, "--no-commit", "--skip-e2e"
    ])

    review_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_review.py"),
        issue_number, adw_id, "--no-commit"
    ])

    document_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_document.py"),
        issue_number, adw_id, "--no-commit"
    ])

    # Wait for all to complete
    test_result = test_proc.wait()
    review_result = review_proc.wait()
    document_result = document_proc.wait()

    # Check if any failed
    if any(r != 0 for r in [test_result, review_result, document_result]):
        print("❌ One or more phases failed:")
        if test_result != 0: print("  - Test failed")
        if review_result != 0: print("  - Review failed")
        if document_result != 0: print("  - Document failed")
        return False

    # Single aggregated commit
    print("\n=== Creating aggregated commit ===")
    subprocess.run(["git", "add", "."])
    commit_msg = f"""Parallel execution results for #{issue_number}

- ✅ Tests passed
- ✅ Review completed
- ✅ Documentation updated

ADW ID: {adw_id}
"""
    subprocess.run(["git", "commit", "-m", commit_msg])
    subprocess.run(["git", "push"])

    print("✅ Parallel execution completed successfully")
    return True


def main():
    # ... existing arg parsing ...

    # Add parallel flag
    parser.add_argument("--parallel", action="store_true",
                       help="Run test/review/document in parallel")
    args = parser.parse_args()

    # ... existing plan and build phases (serial) ...

    # Parallel phases
    if args.parallel:
        success = run_parallel(issue_number, adw_id)
    else:
        # Existing serial execution
        success = run_serial(issue_number, adw_id)

    sys.exit(0 if success else 1)
```

**That's it!** ~30 lines of simple, readable code.

## Testing Strategy

### Quick Manual Test (5 minutes)
```bash
# Test parallel execution
uv run adws/adw_sdlc.py 123 test-adw-001 --parallel

# Expected behavior:
# 1. All three phases run concurrently
# 2. Output interleaved (shows parallelism)
# 3. Single commit at end
# 4. Total time ~3-4 minutes vs 7-10 minutes serial
```

### Validation Checklist
- [ ] All three phases execute without crashing
- [ ] Only one git commit created (not three)
- [ ] Commit message contains all three phase summaries
- [ ] Execution time ≤50% of serial time
- [ ] Git history is clean (no merge conflicts)

### Performance Test
```bash
# Measure speedup
time uv run adws/adw_sdlc.py 123 test-adw-001          # Serial baseline
time uv run adws/adw_sdlc.py 124 test-adw-002 --parallel  # Parallel

# Expected: 40-50% time reduction
```

## Success Criteria

### Functional Requirements
- [ ] `--parallel` flag works without crashing
- [ ] Only one git commit created (aggregated)
- [ ] All three phases complete successfully
- [ ] Git history remains clean

### Performance Requirements
- [ ] Execution time ≤60% of serial time (40%+ speedup)
- [ ] CPU utilization increases during parallel execution

### Quality Requirements
- [ ] No new bugs introduced in serial mode
- [ ] Error messages clear when phases fail
- [ ] Commit message shows all phase results

### Production Readiness
- [ ] Works on macOS (primary platform)
- [ ] Rollback: just remove `--parallel` flag
- [ ] Documentation updated

## Risks and Mitigation

### Risk 1: Output Interleaving Confusion
**Probability**: High
**Impact**: Low (cosmetic only)

**Example**:
```
Test: Running unit tests...
Review: Starting review...
Test: ✅ All tests passed
Document: Generating docs...
Review: ✅ Review complete
Document: ✅ Docs updated
```

**Mitigation**: Accept it! Interleaved output proves parallelism is working.

**Alternative**: Redirect each phase to separate log files if needed.

### Risk 2: Resource Contention
**Probability**: Low (only 3 processes)
**Impact**: Low (slight slowdown)

**Mitigation**: None needed - 3 processes is fine.

### Risk 3: One Phase Hangs
**Probability**: Low
**Impact**: Medium (whole workflow hangs)

**Mitigation**:
- Each phase already has timeout handling
- If issue occurs, add overall timeout to `run_parallel()`

### Risk 4: State File Conflicts
**Probability**: Very Low
**Impact**: Medium

**Analysis**: Each phase reads/writes different fields in adw_state.json:
- Test: `test_status`, `test_results`
- Review: `review_status`, `review_patches`
- Document: `doc_status`, `doc_path`

No overlapping writes = no conflicts.

**Mitigation**: If conflicts detected, add file locking.

## Future Enhancements (When Needed)

### Phase 2: Git Worktrees (When We Need True Isolation)
```bash
# Each phase in separate worktree
git worktree add ../wt-test HEAD
git worktree add ../wt-review HEAD
git worktree add ../wt-docs HEAD

# Parallel execution with isolation
(cd ../wt-test && uv run adws/adw_test.py $issue $adw_id) &
(cd ../wt-review && uv run adws/adw_review.py $issue $adw_id) &
(cd ../wt-docs && uv run adws/adw_document.py $issue $adw_id) &
wait

# Merge all changes
git merge wt-test wt-review wt-docs
git worktree remove ../wt-{test,review,docs}
```

**When to implement**: If we see workspace conflicts or want per-phase commits.

### Phase 3: Within-Phase Parallelization
- Run unit tests in parallel (pytest-xdist)
- Parallelize review checks
- Generate doc sections concurrently

**When to implement**: When individual phases become bottlenecks.

## Why This Beats Async

### Complexity Comparison

| Approach | Lines of Code | Concepts | Time to Implement |
|----------|---------------|----------|-------------------|
| **Simple (this)** | 30 lines | subprocess, Popen, wait | 30 minutes |
| **Async** | 150+ lines | asyncio, coroutines, gather, subprocess bridge | 10-12 hours |

### What Async Doesn't Solve
- ❌ Git conflicts (still need `--no-commit` or worktrees)
- ❌ Error aggregation (Popen.wait() gives return codes too)
- ❌ Timeout handling (phases already have timeouts)
- ❌ Output formatting (interleaved either way)

### What Simple Gives Us
- ✅ Easy to understand (junior devs can read it)
- ✅ Easy to debug (no async stack traces)
- ✅ Easy to test (just run and observe)
- ✅ Unix philosophy (compose simple tools)
- ✅ Same performance gains as async

## Implementation Checklist

### Before Starting
- [x] Marked async spec as `ABANDONED-async-parallel-execution-overengineered.md`
- [x] Created this simple spec
- [ ] Git branch: `feature/simple-parallel-execution`

### During Implementation
- [ ] Add `--no-commit` to adw_test.py
- [ ] Add `--no-commit` to adw_review.py
- [ ] Add `--no-commit` to adw_document.py
- [ ] Add `run_parallel()` to adw_sdlc.py
- [ ] Test manually with real issue

### Before Merge
- [ ] Performance test shows 40%+ speedup
- [ ] Serial mode still works (no regression)
- [ ] Git history is clean
- [ ] Code review passed

### After Merge
- [ ] Document in README.md
- [ ] Update WORKFLOW_ARCHITECTURE.md
- [ ] Demo to Catsy team

## Documentation for Catsy

### Usage
```bash
# Serial (safe, proven)
uv run adws/adw_sdlc.py <issue-number> <adw-id>

# Parallel (40-50% faster)
uv run adws/adw_sdlc.py <issue-number> <adw-id> --parallel
```

### When to Use Parallel
- ✅ Normal feature development
- ✅ Bug fixes with tests
- ✅ Documentation updates
- ⚠️ Complex reviews (may need serial for debugging)

### When to Use Serial
- When debugging phase failures
- When phases depend on each other (rare)
- When output needs to be perfectly ordered

## Next Steps

1. **Implement** (30 minutes) - Add flags and parallel function
2. **Test** (10 minutes) - Run with real issue
3. **Validate** (5 minutes) - Check speedup and git history
4. **Document** (15 minutes) - Update docs
5. **Ship** (5 minutes) - Merge to main

**Total Time**: 1 hour vs 10-12 hours for async approach

---

**Estimated Implementation Time**: 30 minutes

**Risk Level**: Very Low (opt-in, minimal code changes)

**Expected ROI**: 40-50% time savings, same as async but way simpler

**Generalizable to Catsy**: Yes - pattern works for any parallel independent tasks

**Key Lesson**: Simple solutions beat complex solutions when they deliver the same value.
