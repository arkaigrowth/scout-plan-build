# Plan: Add plan-summarize Command and Standardize Spec Schema + Versioning

## Summary
Add a new `plan-summarize` command to generate concise summaries of implementation plans, and establish a standardized schema with versioning for all spec documents across the repository.

## Inputs

### Scout Results
- **scout_outputs/relevant_files.json**: Identified 10 key files for modification
- **Key findings**:
  - No existing plan-summarize command in `.claude/commands/`
  - specs/ directory needs creation (done)
  - No versioning scheme in current ADW data structures
  - PlanDoc dataclass exists but lacks schema validation
  - ReviewResult has summary capability but not used for plans

### Documentation References
- **docs/SCOUT_PLAN_BUILD_WORKFLOW.md**: Main workflow patterns
- **docs/ADW_INTEGRATION.md**: ADW system integration
- **docs/SETUP.md**: Setup and configuration

## Architecture/Approach

### 1. Command Structure
Create `/plan-summarize` slash command that:
- Accepts a plan file path or spec directory scan
- Extracts key sections using PlanDoc parser
- Generates concise summary with key deliverables
- Outputs to `ai_docs/summaries/` or inline

### 2. Schema Standardization
Define versioned spec schema:
```yaml
version: "1.0.0"
metadata:
  created_at: ISO-8601
  updated_at: ISO-8601
  adw_id: string
  issue_number: optional[int]
  author: string
sections:
  summary: required
  inputs: required
  architecture: required
  implementation_steps: required
  tests: optional
  risks: optional
  done_criteria: required
```

### 3. Versioning Strategy
- Add `spec_version` field to ADWStateData in data_types.py
- Add `SPEC_VERSION = "1.0.0"` constant in adw_common.py
- Implement version migration logic in state.py
- Add version validation in PlanDoc parser

## Implementation Steps

### Step 1: Create plan-summarize command
1. Create `.claude/commands/plan-summarize.md` with slash command definition
2. Implement summarization logic using existing PlanDoc parser
3. Add formatting templates for different summary styles

### Step 2: Add schema versioning to data types
1. Update `adws/adw_modules/data_types.py`:
   - Add `spec_version: str = "1.0.0"` to ADWStateData
   - Add SpecMetadata pydantic model
2. Update `adws/adw_common.py`:
   - Add SPEC_VERSION constant
   - Enhance PlanDoc with version awareness

### Step 3: Implement schema validation
1. Create `adws/adw_modules/schema_validator.py`:
   - Validate spec files against schema
   - Handle version migrations
   - Report validation errors
2. Integrate validation into adw_plan.py and adw_build.py

### Step 4: Update existing workflows
1. Modify `adws/adw_plan.py`:
   - Include version in generated specs
   - Add metadata section to plans
2. Modify `adws/adw_build.py`:
   - Validate spec version before processing
   - Handle version mismatches gracefully

### Step 5: Create migration utilities
1. Add `adws/adw_modules/migrations.py`:
   - Migrate existing specs to new format
   - Version upgrade/downgrade logic
2. Create migration script for existing specs

## Tests

### Unit Tests
- Test plan-summarize command with various input formats
- Test schema validation with valid/invalid specs
- Test version migration logic
- Test PlanDoc parser with versioned specs

### Integration Tests
- End-to-end scout → plan → build with versioned specs
- Test backward compatibility with existing specs
- Test version mismatch handling

## Risks/Rollback

### Risks
1. **Breaking existing workflows**: Mitigated by backward compatibility
2. **Schema too rigid**: Start with minimal required fields
3. **Version migration complexity**: Keep migrations simple initially

### Rollback Plan
1. Keep original files backed up before migration
2. Version flag to disable validation temporarily
3. Ability to work with unversioned specs via compatibility mode

## Done Criteria

✅ `/plan-summarize` command functional and tested
✅ All new specs include version metadata
✅ Existing specs migrated to v1.0.0 format
✅ Schema validation integrated into plan/build workflows
✅ Documentation updated with schema specification
✅ Migration script available for future version changes
✅ Tests passing for all modified components