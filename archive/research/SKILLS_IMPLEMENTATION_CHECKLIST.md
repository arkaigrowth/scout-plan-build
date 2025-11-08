# Skills Implementation Checklist

Complete reference for implementing the 5 highest-priority skills.

## Skill 1: validate-adw-input

**Status**: 95% ready (code exists, just wrap it)  
**Effort**: 4 hours  
**Leverage**: 9/10 (used by every operation)

### Source Code Locations
- Implementation: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/validators.py` (100+ lines)
- Key Classes:
  - `SafeUserInput` - Prompt validation
  - `SafeDocsUrl` - URL validation
  - `SafeFilePath` - Path traversal prevention
  - `SafeCommitMessage` - Semantic commit validation
  - `SafeBranchName` - Git branch name validation

### Implementation Steps
- [ ] Create `.claude/skills/validate-adw-input.md`
- [ ] Copy validator classes into skill
- [ ] Add deterministic error sorting
- [ ] Create test cases:
  - [ ] Valid prompt (max 100KB)
  - [ ] Null bytes in prompt (should reject)
  - [ ] Path traversal attempt (should reject)
  - [ ] Valid file path
  - [ ] Shell injection attempt (should warn/reject)
- [ ] Document all validators
- [ ] Add to skill README

### Expected Outcome
Reusable validation skill used by all ADW operations before execution.

---

## Skill 2: git-safe-operations

**Status**: 90% ready (code exists, needs integration)  
**Effort**: 6 hours  
**Leverage**: 8/10 (every build/push operation)

### Source Code Locations
- Implementation: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/git_ops.py` (150+ lines)
- Key Functions:
  - `get_current_branch()` - Get active branch
  - `create_branch(branch_name)` - Create feature branch
  - `push_branch(branch_name)` - Push to remote
  - `check_pr_exists(branch_name)` - Check for existing PR
  - `commit_changes(...)` - Atomic commit

### Implementation Steps
- [ ] Create `.claude/skills/git-safe-operations.md`
- [ ] Document each function with examples
- [ ] Add error recovery strategies:
  - [ ] Retry logic for transient failures
  - [ ] GitHub auth fallback
  - [ ] Workspace state verification
- [ ] Create test cases:
  - [ ] Create branch successfully
  - [ ] Push branch with retry
  - [ ] Check non-existent PR
  - [ ] Git command validation
- [ ] Add security notes (command injection prevention)

### Expected Outcome
Safe git operations skill for all workflow phases.

---

## Skill 3: scout-deterministic

**Status**: 40% ready (structure exists, needs determinism)  
**Effort**: 16 hours  
**Leverage**: 6/10 (planning operations)  
**CRITICAL**: Must fix determinism issues

### Source Code Locations
- Current Implementation: `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/skills/adw-scout.md` (342 lines)
- Reference: `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/ROBUST_DETERMINISTIC_SKILLS_GUIDE.md` (614 lines)

### Determinism Issues to Fix
1. **Line 312-315**: Unsorted glob results
   ```python
   # ❌ Current
   files = glob.glob(pattern)
   selected = files[:10]
   
   # ✅ Fixed
   files = sorted(glob.glob(pattern))
   selected = files[:10]
   ```

2. **Line 159-160**: Unsorted grep results
   ```python
   # ❌ Current
   content_matches = parse_grep_results(results)
   
   # ✅ Fixed
   content_matches = sorted(parse_grep_results(results), key=lambda x: x.path)
   ```

3. **Line 136**: Unsorted parallel results
   ```python
   # ❌ Current
   all_files = set(file_patterns + content_matches + results.files)
   
   # ✅ Fixed
   all_files = sorted(set(...), key=lambda x: x.path)
   ```

4. **Line 173-175**: Non-deterministic selection
   ```python
   # ❌ Current
   relevant_files = validated_files[:max_files]
   
   # ✅ Fixed - Already sorted, but ensure deterministic ordering
   relevant_files.sort(key=lambda x: (-x["confidence"], x["path"]))
   relevant_files = relevant_files[:max_files]
   ```

### Implementation Steps
- [ ] Rewrite Phase 2.1: Pattern-Based Search
  - Sort glob results
  - Document sorting order
  
- [ ] Rewrite Phase 2.2: Content-Based Search
  - Sort grep results by path
  - Add confidence scoring
  
- [ ] Rewrite Phase 2.3: Parallel Exploration
  - Sort parallel results deterministically
  - Use fixed seeds for random sampling
  
- [ ] Rewrite Phase 3: Validation and Ranking
  - Sort by confidence then alphabetically
  - Ensure deterministic selection
  
- [ ] Create comprehensive tests:
  - [ ] Run scout twice, verify identical output
  - [ ] Test with 5 different queries
  - [ ] Verify file order consistency
  
- [ ] Document determinism guarantees
- [ ] Add performance metrics

### Expected Outcome
Deterministic scout that always produces identical results for same input.

---

## Skill 4: memory-learn-patterns

**Status**: 60% ready (infrastructure exists, needs integration)  
**Effort**: 12 hours  
**Leverage**: 7/10 (enables 30% performance gain)

### Source Code Locations
- Implementation: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/memory_manager.py` (100+ lines)
- Memory Hooks Reference: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/memory_hooks.py`
- Architecture Docs: `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/SKILLS_AND_MEMORY_ARCHITECTURE.md`

### Key Classes
- `MemoryManager` - Singleton wrapper for mem0.Memory
  - `get_instance()` - Get/create singleton
  - `add(messages, user_id)` - Save memories
  - `search(query, user_id)` - Recall memories
  - `is_available()` - Check mem0 status

### Implementation Steps
- [ ] Create `.claude/skills/memory-learn-patterns.md`
- [ ] Document 4 memory layers:
  - [ ] Session memory (immediate)
  - [ ] Project memory (3-30 days)
  - [ ] Long-term memory (embeddings)
  - [ ] Cross-project memory (global)

- [ ] Implement memory hooks:
  - [ ] Pre-execution: Recall similar tasks
  - [ ] Post-execution: Save successful patterns
  - [ ] Error handling: Save failure patterns
  
- [ ] Add determinism layer:
  - [ ] Confidence threshold (>0.7)
  - [ ] Sort results by relevance
  - [ ] Seed-based sampling
  
- [ ] Create tests:
  - [ ] Save pattern successfully
  - [ ] Recall pattern from memory
  - [ ] Verify performance improvement (30% speedup)
  - [ ] Test graceful degradation (no mem0)
  
- [ ] Document memory file locations
- [ ] Add memory cleanup/archival

### Expected Outcome
Learning system that improves with each execution, 30% faster on repeated tasks.

---

## Skill 5: adw-state-manager

**Status**: 95% ready (code exists, just wrap it)  
**Effort**: 4 hours  
**Leverage**: 7/10 (enables workflow composition)

### Source Code Locations
- Implementation: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/state.py` (120+ lines)
- Data Types: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/data_types.py` (ADWStateData)
- Usage Examples: `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan.py` lines 1-100

### Key Classes
- `ADWState` - Persistent state management
  - `update(**kwargs)` - Update state
  - `get(key, default)` - Get value
  - `save()` - Persist to disk
  - `load(adw_id)` - Load from disk
  - `get_state_path()` - Get state file location

### State Contents (Pydantic validated)
- `adw_id` - Unique workflow ID
- `issue_number` - GitHub issue number
- `branch_name` - Feature branch name
- `plan_file` - Path to implementation spec
- `issue_class` - Issue type (bug/feature/chore)

### Implementation Steps
- [ ] Create `.claude/skills/adw-state-manager.md`
- [ ] Document state lifecycle:
  - [ ] Initialization
  - [ ] Updating between phases
  - [ ] Persistence
  - [ ] Loading in next phase
  
- [ ] Document workflow composition:
  - [ ] Planning → Building
  - [ ] Building → Testing
  - [ ] Testing → Review
  - [ ] Review → Documentation
  
- [ ] Create test cases:
  - [ ] Initialize state
  - [ ] Update and save
  - [ ] Load in new context
  - [ ] Validate schema
  - [ ] Handle missing fields
  
- [ ] Document state file location
- [ ] Add state history tracking
- [ ] Add state debugging commands

### Expected Outcome
State management skill enabling workflow composition and resumption.

---

## Phase 1 Tasks (Week 1-2): Determinism Foundation

### Task 1: Fix Scout Determinism
- [ ] Analyze `adw-scout.md` for non-determinism sources
- [ ] Sort all file discoveries (glob, grep, parallel results)
- [ ] Update confidence scoring to be deterministic
- [ ] Create determinism test (run 5x, verify identical)
- [ ] Update documentation with sorting guarantees
- **Time**: 8 hours
- **Priority**: CRITICAL

### Task 2: Create Determinism Test Framework
- [ ] Design test structure (5 runs, JSON comparison)
- [ ] Create helper functions for output comparison
- [ ] Implement pytest fixtures
- [ ] Document testing methodology
- **Time**: 6 hours
- **Priority**: HIGH

### Task 3: Document Current Gaps
- [ ] Create issues for each pain point
- [ ] Prioritize by impact and effort
- [ ] Estimate effort for fixes
- [ ] Assign to implementation phases
- **Time**: 4 hours
- **Priority**: MEDIUM

**Phase 1 Total**: 18 hours (2-3 days intensive work)

---

## Phase 2 Tasks (Week 3-4): Skill Extraction

### Task 1: Extract validate-adw-input
- [ ] Create skill markdown
- [ ] Add usage examples
- [ ] Write tests
- **Time**: 4 hours

### Task 2: Extract git-safe-operations
- [ ] Create skill markdown
- [ ] Add error recovery examples
- [ ] Write tests
- **Time**: 6 hours

### Task 3: Extract adw-state-manager
- [ ] Create skill markdown
- [ ] Add workflow composition examples
- [ ] Write tests
- **Time**: 4 hours

### Task 4: Create Skill Testing Framework
- [ ] Design test structure
- [ ] Create base test classes
- [ ] Document testing approach
- **Time**: 5 hours

**Phase 2 Total**: 19 hours (2-3 days intensive work)

---

## Phase 3 Tasks (Week 5-6): Memory Integration

### Task 1: Implement Memory Hooks
- [ ] Pre-execution recall hook
- [ ] Post-execution save hook
- [ ] Error pattern tracking
- **Time**: 8 hours

### Task 2: Populate Memory Files
- [ ] Create workflow_history.json
- [ ] Create error_patterns.json
- [ ] Create embeddings directory
- **Time**: 4 hours

### Task 3: Test Memory Speedup
- [ ] Run scout on repeated tasks
- [ ] Measure time differences
- [ ] Verify 30% improvement
- **Time**: 4 hours

**Phase 3 Total**: 16 hours (2-3 days intensive work)

---

## Phase 4 Tasks (Week 7-8): Testing & Validation

### Task 1: Determinism Test Suite
- [ ] Run all skills 5x with identical input
- [ ] Verify identical outputs
- [ ] Document any non-determinism
- **Time**: 8 hours

### Task 2: Robustness Scoring
- [ ] Score each skill 0-100
- [ ] Test error recovery
- [ ] Test fallback levels
- **Time**: 8 hours

### Task 3: Performance Benchmarking
- [ ] Measure scout performance
- [ ] Measure memory speedup
- [ ] Measure parallel gains
- **Time**: 6 hours

### Task 4: Documentation Updates
- [ ] Update README files
- [ ] Create implementation guides
- [ ] Document recovery strategies
- **Time**: 6 hours

**Phase 4 Total**: 28 hours (3-4 days intensive work)

---

## File Checklist

### Skills to Create
- [ ] `.claude/skills/validate-adw-input.md`
- [ ] `.claude/skills/git-safe-operations.md`
- [ ] `.claude/skills/scout-deterministic.md` (rewrite from adw-scout)
- [ ] `.claude/skills/memory-learn-patterns.md`
- [ ] `.claude/skills/adw-state-manager.md`

### Memory Files to Create
- [ ] `.claude/memory/workflow_history.json`
- [ ] `.claude/memory/error_patterns.json`
- [ ] `.claude/memory/embeddings/` (directory)

### Tests to Create
- [ ] `tests/test_determinism_scout.py`
- [ ] `tests/test_determinism_validators.py`
- [ ] `tests/test_git_safe_ops.py`
- [ ] `tests/test_memory_recall.py`
- [ ] `tests/test_state_manager.py`

### Documentation to Create
- [ ] `DETERMINISM_GUIDE.md` - How to ensure determinism
- [ ] `SKILL_TESTING_GUIDE.md` - How to test skills
- [ ] `SKILL_EXTRACTION_GUIDE.md` - How to create new skills
- [ ] `MEMORY_INTEGRATION_GUIDE.md` - How to integrate memory

---

## Success Criteria

### Determinism
- Same input always produces same output
- Run skill 5x, all outputs identical (except timestamps)
- No file operation randomness
- No memory recall variability

### Performance
- Scout with memory 30% faster than without
- Parallel execution 50% faster than sequential
- Overall workflow 2-3x faster on repeated tasks

### Robustness
- All skills score 85+ on robustness scale
- Zero catastrophic failures
- Graceful degradation on all errors
- All error types documented

### Code Quality
- Full test coverage (>90%)
- All validators working
- All error handlers tested
- Complete documentation

---

## Implementation Order

**Recommended sequence for maximum value**:

1. **First**: Fix scout determinism (critical blocker)
2. **Second**: Extract validate-adw-input skill (high leverage, easy)
3. **Third**: Extract git-safe-operations skill (high leverage, easy)
4. **Fourth**: Extract adw-state-manager skill (enables composition)
5. **Fifth**: Implement memory integration (performance boost)
6. **Sixth**: Extract scout-deterministic skill (main rewrite)
7. **Seventh**: Complete testing framework
8. **Eighth**: Performance optimization and documentation

---

**Total Estimated Effort**: 130 hours / 8 weeks of part-time work  
**Expected Value**: 2-3x performance improvement + production-ready reliability

