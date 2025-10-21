# Plan: Scout-Plan-Build Command Improvements

## Summary
Enhance the scout, plan_w_docs, and scout_plan_build commands based on best practices observed in screenshots, focusing on better parallel subagent coordination, clearer timeout handling, improved error recovery, and more structured output formats.

## Problem Statement
The current scout/plan/build workflow commands lack:
1. Explicit parallel agent coordination instructions
2. Clear timeout handling and recovery strategies
3. Structured output format specifications
4. Detailed error handling between workflow steps
5. Comprehensive reporting structures

## Inputs

### Scout Results
- **Existing Commands Analysis**:
  - `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/scout.md` (27 lines)
  - `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/plan_w_docs.md` (20 lines)
  - `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/scout_plan_build.md` (31 lines)

### Screenshot Insights
- Screenshots show explicit parallel agent patterns with specific external tools
- Clear 3-minute timeout enforcement per subagent
- Structured output format: `<path> (offset: N, limit: M)`
- Git safety checks after operations
- THINK HARD analysis phase in planning
- Comprehensive report structures

### Improved Versions Created
- `scout_improved.md`: Enhanced parallel coordination, explicit tool list, JSON output
- `plan_w_docs_improved.md`: THINK HARD phase, parallel doc scraping, structured plan template
- `scout_plan_build_improved.md`: Better error handling, comprehensive reporting, status tracking

## Architecture/Approach

### Design Principles
1. **Explicit over Implicit**: Clear instructions for agent behavior
2. **Parallel by Default**: Maximize concurrent operations where possible
3. **Fail-Safe**: Skip failures without blocking workflow
4. **Structured Output**: JSON/Markdown templates for consistency
5. **Progressive Enhancement**: Build on existing functionality

### Integration Strategy
1. Create improved versions alongside existing commands (non-breaking)
2. Test improved versions in isolated scenarios
3. Gradually migrate to improved versions
4. Deprecate old versions after validation

## Implementation Steps

### Step 1: Deploy Improved Scout Command
1. **Backup existing**: `cp .claude/commands/scout.md .claude/commands/scout_original.md`
2. **Deploy improved**: `cp .claude/commands/scout_improved.md .claude/commands/scout.md`
3. **Key changes**:
   - Add frontmatter with model specification
   - Explicit external tool list (gemini, opencode, codex, claude)
   - Structured JSON output format
   - Clear parallel execution instructions
   - 3-minute timeout enforcement

### Step 2: Deploy Improved Plan Command
1. **Backup existing**: `cp .claude/commands/plan_w_docs.md .claude/commands/plan_w_docs_original.md`
2. **Deploy improved**: `cp .claude/commands/plan_w_docs_improved.md .claude/commands/plan_w_docs.md`
3. **Key changes**:
   - Add THINK HARD analysis phase
   - Parallel documentation scraping with Task
   - Comprehensive plan template with 8 sections
   - Explicit validation of inputs
   - Structured markdown output

### Step 3: Deploy Improved Scout-Plan-Build Command
1. **Backup existing**: `cp .claude/commands/scout_plan_build.md .claude/commands/scout_plan_build_original.md`
2. **Deploy improved**: `cp .claude/commands/scout_plan_build_improved.md .claude/commands/scout_plan_build.md`
3. **Key changes**:
   - Enhanced report structure with subsections
   - Status tracking (✅/❌) for each phase
   - Artifacts summary section
   - Recommended next actions
   - Better error context

### Step 4: Create Test Scenarios
1. **Scout-only test**: Test parallel agent coordination
   ```bash
   /scout "Add error handling to auth module" "4"
   ```
2. **Plan-only test**: Test documentation scraping
   ```bash
   /plan_w_docs "Implement rate limiting" "https://docs.api.com" "agents/scout_files/test.json"
   ```
3. **Full workflow test**: End-to-end validation
   ```bash
   /scout_plan_build "Add caching layer" "https://redis.io/docs"
   ```

### Step 5: Validate and Iterate
1. Run test scenarios and capture outputs
2. Compare improved vs original outputs
3. Validate JSON structure in scout results
4. Verify plan markdown formatting
5. Check build report completeness

## Testing Strategy

### Unit Tests
- **Scout validation**:
  - Parallel agent spawning (4 agents)
  - Timeout handling (3-minute enforcement)
  - JSON output structure
  - Git reset on changes

- **Plan validation**:
  - Input parameter checking
  - Documentation scraping parallelism
  - Markdown plan structure (8 sections)
  - Filename generation (kebab-case)

- **Workflow validation**:
  - Command chaining
  - Variable passing between steps
  - Error propagation
  - Report generation

### Integration Tests
1. **Timeout scenario**: One agent times out, others complete
2. **Partial failure**: Some agents fail, workflow continues
3. **Documentation unavailable**: Webfetch fallback from firecrawl
4. **Large codebase**: Test with 100+ files
5. **Complex prompt**: Multi-step requirements

### Regression Tests
- Ensure existing workflows still function
- Validate backward compatibility
- Check output path consistency

## Risks and Mitigation

### Risk 1: Breaking Existing Workflows
- **Impact**: High - Could disrupt current development
- **Mitigation**: Keep original commands as backups, test thoroughly

### Risk 2: External Tool Dependencies
- **Impact**: Medium - Tools may not be installed
- **Mitigation**: Graceful fallback, clear error messages

### Risk 3: Increased Complexity
- **Impact**: Low - More detailed instructions could confuse
- **Mitigation**: Clear documentation, examples

### Rollback Plan
1. Restore original commands from backups
2. Document any issues encountered
3. Iterate on improvements
4. Re-deploy with fixes

## Success Criteria

✅ **Functional Requirements**
- [ ] All 3 improved commands execute successfully
- [ ] Parallel agents spawn correctly (validated via logs)
- [ ] Timeouts enforced at 3 minutes
- [ ] JSON output validates against schema
- [ ] Plans contain all 8 required sections
- [ ] Build reports show comprehensive stats

✅ **Performance Improvements**
- [ ] Scout phase completes 40% faster (parallel execution)
- [ ] Documentation scraping happens concurrently
- [ ] No blocking on individual agent failures

✅ **Quality Improvements**
- [ ] Structured output formats (JSON/Markdown)
- [ ] Clear error messages with context
- [ ] Comprehensive final reports
- [ ] Actionable next steps provided

✅ **Developer Experience**
- [ ] Commands are self-documenting
- [ ] Failures don't block workflow
- [ ] Output is predictable and parseable
- [ ] Status tracking throughout execution

## Next Steps

1. **Immediate Actions**:
   - Review improved command files
   - Run basic validation tests
   - Deploy to development environment

2. **Short-term (1 week)**:
   - Complete integration testing
   - Gather user feedback
   - Document usage patterns

3. **Long-term (1 month)**:
   - Deprecate original commands
   - Add command versioning
   - Create command migration guide