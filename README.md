# Scout–Plan–Build MVP (Claude Code + Anthropic Agents SDK)

This is a minimal, runnable scaffold that reconstructs IndyDevDan's **Scout → Plan → Build** workflow and bridges it into an **ADW** (AI Developer Workflow) style pipeline suitable for **Claude Code**. It includes:

- Slash-command style prompts for `/scout`, `/plan_w_docs`, `/build`, and the orchestrator `/scout_plan_build`.
- Clear, opinionated instructions for running in **Claude Code** (with hooks) and optionally with the **Anthropic Agents SDK** for delegated/parallelized tasks.
- Documentation describing architecture, setup, and next steps.

> Scope: This is an MVP scaffold to kickstart end-to-end loops. You can iterate inside Claude Code to flesh out agents, add tests, and wire to your real ADW apps.

## Quick Start

```bash
# Set up environment
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
export ANTHROPIC_API_KEY="your-key-here"
export GITHUB_REPO_URL="https://github.com/owner/repo"

# Run the complete workflow
/scout_plan_build "Add user authentication" "https://docs.auth.com"
```

## Documentation

- **Setup Guide**: See [`docs/SETUP.md`](docs/SETUP.md) for installation and configuration
- **Workflow Guide**: See [`docs/SCOUT_PLAN_BUILD_WORKFLOW.md`](docs/SCOUT_PLAN_BUILD_WORKFLOW.md) for usage patterns
- **ADW Integration**: See [`docs/ADW_INTEGRATION.md`](docs/ADW_INTEGRATION.md) for webhook and automation setup
- **Spec Standards**: See [`docs/SPEC_SCHEMA.md`](docs/SPEC_SCHEMA.md) for specification schema and validation

## Spec Standards

This project uses versioned specification documents (specs) as the contract between planning and building phases. All specs follow a standardized schema for consistency and validation.

### Current Schema Version: 1.1.0

Key requirements for all specs:
- **Version field**: Must declare schema version (e.g., `**Version**: 1.1.0`)
- **Metadata section**: Includes ADW ID, timestamps, author, and status
- **Required sections**: Summary, Step by Step Tasks, Acceptance Criteria, Done Criteria
- **File naming**: `issue-{number}-adw-{id}-{slug}.md`

### Validation

```bash
# Validate a single spec
python -m adws.adw_modules.schema_validator specs/my-spec.md

# Validate all specs
python scripts/validate_all_specs.py

# Migrate specs to latest version
python scripts/migrate_specs.py --from 1.0.0 --to 1.1.0 --apply
```

### Creating New Specs

Use the slash command to generate properly formatted specs:
```bash
/plan_w_docs "[task description]" "[docs url]" "agents/scout_files/relevant_files.json"
```

For detailed schema documentation, validation rules, and migration procedures, see [`docs/SPEC_SCHEMA.md`](docs/SPEC_SCHEMA.md).

## Repository Structure

```
scout_plan_build_mvp/
├── .claude/commands/      # Slash command definitions
├── specs/                  # Implementation plans (versioned specs)
├── agents/                 # Runtime data and state
├── ai_docs/               # AI-generated documentation
│   ├── analyses/          # System analysis reports
│   ├── architecture/      # Architecture documentation
│   ├── build_reports/     # Build execution reports
│   ├── reference/         # Reference documentation
│   └── reviews/           # Implementation reviews
├── docs/                  # Human-written documentation
├── adws/                  # ADW system implementation
│   ├── adw_modules/       # Core modules
│   └── adw_triggers/      # Webhook and cron triggers
└── scripts/               # Utility scripts
```

## Analysis and Reference

For comprehensive system analysis and reference documentation, see:
- [`ai_docs/ANALYSIS_INDEX.md`](ai_docs/ANALYSIS_INDEX.md) - Index of all analysis documents
- [`ai_docs/reference/REPOSITORY_REFERENCE.md`](ai_docs/reference/REPOSITORY_REFERENCE.md) - Complete codebase reference
- [`ai_docs/analyses/ENGINEERING_ASSESSMENT.md`](ai_docs/analyses/ENGINEERING_ASSESSMENT.md) - Production readiness assessment

## Contributing

When creating or modifying specs:
1. Follow the schema standards in [`docs/SPEC_SCHEMA.md`](docs/SPEC_SCHEMA.md)
2. Validate specs before committing
3. Use semantic versioning for schema changes
4. Document any custom sections added

## License

[Your License Here]
