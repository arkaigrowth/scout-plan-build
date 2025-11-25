# ASCII Diagram Examples

Generated from actual trace results of the scout_plan_build_mvp project.

## Import Statistics Summary

Shows high-level health metrics of your dependencies:

```
Total Imports: 324
├─ ✓ Valid: 316 (97%)
└─ ✗ Broken: 8 (2%)

By Location:
├─ installed: 235 (72%)
├─ local: 81 (25%)
└─ unknown: 8 (2%)

Top 5 Most Imported Modules:
├─ os: 31 times
├─ typing: 30 times
├─ sys: 28 times
├─ subprocess: 23 times
└─ json: 22 times
```

## Import Dependency Tree

Shows file-by-file imports with status indicators:

```
├─ ✓ adw_build.py (13 imports, 0 broken)
│  ├─ ✓ sys [import] (installed)
│  ├─ ✓ os [import] (installed)
│  ├─ ✓ logging [import] (installed)
│  ├─ ✓ json [import] (installed)
│  ├─ ✓ subprocess [import] (installed)
│  ├─ ✓ typing [from] (installed)
│  ├─ ✓ dotenv [from] (installed)
│  ├─ ✓ adw_modules.state [from] (local)
│  ├─ ✓ adw_modules.git_ops [from] (local)
│  ├─ ✓ adw_modules.github [from] (local)
│  ├─ ✓ adw_modules.utils [from] (local)
│  ├─ ✓ adw_modules.data_types [from] (local)
│  └─ ✓ adw_modules.workflow_ops [from] (local)
├─ ✗ adw_fix_dependencies.py (8 imports, 1 broken)
│  ├─ ✓ json [import] (installed)
│  ├─ ✓ sys [import] (installed)
│  ├─ ✓ logging [import] (installed)
│  ├─ ✓ pathlib [from] (installed)
│  ├─ ✓ typing [from] (installed)
│  ├─ ✓ datetime [from] (installed)
│  ├─ ✓ adws.adw_modules.utils [from] (installed)
│  └─ ✗ **adws.adw_modules.state** [from] (BROKEN - unknown)
└─ ✓ agent.py (9 imports, 0 broken)
   ├─ ✓ subprocess [import] (installed)
   ├─ ✓ sys [import] (installed)
   ├─ ✓ os [import] (installed)
   ├─ ✓ json [import] (installed)
   ├─ ✓ re [import] (installed)
   ├─ ✓ logging [import] (installed)
   ├─ ✓ typing [from] (installed)
   ├─ ✓ dotenv [from] (installed)
   └─ ✓ adw_modules.utils [from] (local)
```

### Legend
- `✓` - Valid import
- `✗` - Broken import (needs fixing)
- `**text**` - Emphasized broken module
- Numbers in parentheses show import counts

## Broken Reference Map

Focused view showing only the problems that need fixing:

```
BROKEN MODULES
│
├─ ✗ schedule (1 file)
│  └─ trigger_cron.py
├─ ✗ pytest (1 file)
│  └─ test_validators.py
├─ ✗ boto3 (1 file)
│  └─ r2_uploader.py
├─ ✗ e2b_code_interpreter (1 file)
│  └─ sandbox_poc.py
├─ ✗ adws.adw_modules.state (1 file)
│  └─ adw_fix_dependencies.py
├─ ✗ fastapi (1 file)
│  └─ trigger_webhook.py
├─ ✗ botocore.client (1 file)
│  └─ r2_uploader.py
└─ ✗ botocore.exceptions (1 file)
   └─ r2_uploader.py
```

This view makes it easy to see:
1. Which modules are missing
2. Which files are affected
3. Patterns (e.g., boto3/botocore both missing)

## Module Hierarchy

Shows the structure of local project modules:

```
Local Module Structure:
│
├─ ✓ adw_modules
│  ├─ ✓ agent
│  ├─ ✓ bitbucket_ops
│  ├─ ✓ constants
│  ├─ ✓ data_types
│  ├─ ✓ exceptions
│  ├─ ✓ file_organization
│  ├─ ✓ git_ops
│  ├─ ✓ github
│  ├─ ✓ memory_manager
│  ├─ ✓ r2_uploader
│  ├─ ✓ state
│  ├─ ✓ utils
│  ├─ ✓ validators
│  ├─ ✓ vcs_detection
│  └─ ✓ workflow_ops
└─ ✓ scripts
   └─ ✓ dependency-tracer
```

## Usage

Generate these diagrams from any trace result:

```bash
# From Python imports
python scripts/generate_ascii_diagrams.py scout_outputs/traces/latest/python_imports.json

# From command references
python scripts/generate_ascii_diagrams.py scout_outputs/traces/latest/command_refs.json

# Save to file
python scripts/generate_ascii_diagrams.py trace_results.json output.md
```

## Benefits

1. **Visual Pattern Recognition**: Quickly spot problem areas
2. **No External Dependencies**: Pure ASCII works everywhere
3. **Token Efficient**: Visual representation uses fewer tokens than raw JSON
4. **Git-Friendly**: Text-based diagrams work well in version control
5. **Terminal-Native**: View directly in terminal without leaving CLI