---
description: Execute the ADW Python build script to implement a plan. Preferred build command for spec files in specs/.
argument-hint: <spec_file_path>
---

<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Build (ADW Runner)

## Purpose
Run the ADW Python build system to implement a plan from a spec file.

## Supported Modes

### Standalone Mode (spec file) - PREFERRED
```bash
uv run adws/adw_build.py <spec-file.md> [adw-id]
```
- Works with any spec file directly
- Extracts ADW ID from spec header (`**ADW ID**: XXX`)
- Creates feature branch from filename
- No GitHub issue required

### GitHub Mode (issue-driven)
```bash
uv run adws/adw_build.py <issue-number> <adw-id>
```
- Requires prior run of adw_plan.py
- Updates GitHub issue with progress
- Creates/updates PR

## Variables
SPEC_FILE_PATH: $1

## Instructions
1. Parse the spec file path from arguments
2. Run the build command:
   ```bash
   uv run adws/adw_build.py "[SPEC_FILE_PATH]"
   ```
3. The script will:
   - Extract ADW ID from spec header
   - Create/checkout feature branch
   - Implement the plan using Claude
   - Commit changes
   - Push branch (if remote configured)
4. On success, report:
   - Branch name
   - ADW ID
   - State file location
5. On failure, report the error and suggest fixes

## Examples
```bash
# Build from spec file (standalone mode)
uv run adws/adw_build.py specs/gemini-file-search-v1.md

# Build with explicit ADW ID
uv run adws/adw_build.py specs/my-feature.md MY-FEATURE-ID

# Build from GitHub issue (requires prior adw_plan.py)
uv run adws/adw_build.py 123 FEATURE-AUTH
```
