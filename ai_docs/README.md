# AI-Generated Documentation Structure

All AI-generated artifacts are organized here for clarity and consistency.

## Directory Structure

```
ai_docs/
├── scout/              # Scout exploration outputs
│   └── relevant_files.json
├── build_reports/      # Build phase reports
├── analyses/           # System analyses
├── reviews/            # Code reviews
├── architecture/       # Architecture documentation
└── reference/          # Reference guides
```

## Workflow Outputs

1. **Scout Phase** → `ai_docs/scout/relevant_files.json`
2. **Plan Phase** → `specs/` (separate top-level for visibility)
3. **Build Phase** → `ai_docs/build_reports/`

## Why This Organization?

- **Consistency**: All AI outputs in one place
- **Clarity**: Clear separation from human-written code
- **Discoverability**: Easy to find all AI artifacts
- **Gitignore-friendly**: Can exclude all AI outputs with one pattern

## Usage

```bash
# Scout saves to:
ai_docs/scout/relevant_files.json

# Plan reads from scout and saves to:
specs/issue-XXX-*.md

# Build reads spec and saves to:
ai_docs/build_reports/*-report.md
```
