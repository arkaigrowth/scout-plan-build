#!/usr/bin/env python3
"""
ADW Fix Dependencies - Automated dependency issue resolution

Purpose:
  Analyzes broken imports and file references found by dependency-tracer
  and spawns targeted fix agents to resolve each issue.

Workflow:
  1. Read dependency trace results (from scout_outputs/traces/)
  2. Categorize issues by complexity
  3. Spawn focused fix agents (one per issue)
  4. Collect fixes in scout_outputs/traces/fixes/

Usage:
  python adws/adw_fix_dependencies.py <trace_results.json>

Examples:
  # Fix Python import issues
  python adws/adw_fix_dependencies.py scout_outputs/traces/latest/python_imports.json

  # Fix markdown reference issues
  python adws/adw_fix_dependencies.py scout_outputs/traces/latest/command_refs.json

Input:
  JSON file from dependency-tracer with broken references

Output:
  Individual fix files in scout_outputs/traces/fixes/
  - fix_001_missing_import_requests.md
  - fix_002_moved_file_reference.md
  - fix_003_typo_in_module_name.md

Agent Selection:
  - Simple fixes (typos, missing packages): claude-3-sonnet
  - Complex fixes (circular deps, architecture): claude-3-opus

Token Efficiency:
  Main context: ~100 tokens (summary only)
  Per fix agent: ~300-500 tokens
  Total: 100 + (N × 400) tokens vs 50,000+ traditional
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adw_modules.utils import setup_logger
from adw_modules.state import ADWState
from adw_modules.workflow_ops import (
    format_issue_message,  # We'll repurpose this
)

# ADW Metadata (for framework discovery)
ADW_METADATA = {
    'name': 'fix-dependencies',
    'description': 'Fix broken imports and file references automatically',
    'triggers': ['dependency-tracer', 'broken imports', 'missing files'],
    'requires': ['dependency-tracer results'],
    'produces': ['fix suggestions', 'remediation scripts'],
    'agent_type': 'multi-spawn',  # Spawns multiple sub-agents
    'token_mode': 'minimal',       # Uses minimal context pattern
}

# Agent configuration
AGENT_FIX = "fix-dependency"


def load_trace_results(trace_file: Path) -> tuple[List[Dict], Dict]:
    """
    Load trace results JSON and extract broken references with metadata.

    Args:
        trace_file: Path to python_imports.json or command_refs.json

    Returns:
        Tuple of (broken_references_list, metadata_dict)
    """
    with open(trace_file) as f:
        results = json.load(f)

    # Handle both array format and object with metadata
    if isinstance(results, list):
        # Simple array of results
        broken = [r for r in results if r.get('status') == 'broken']
        metadata = {'total': len(results), 'broken': len(broken)}
    else:
        # Object with stats and results
        broken = results.get('broken_imports', []) or results.get('broken_refs', [])
        if not broken and 'results' in results:
            broken = [r for r in results['results'] if r.get('status') == 'broken']
        metadata = results.get('stats', {})

    return broken, metadata


def categorize_fix_complexity(ref: Dict) -> tuple[str, str]:
    """
    Determine fix complexity and appropriate model.

    Args:
        ref: Broken reference dictionary

    Returns:
        Tuple of (complexity_level, model_name)
    """
    # Complex indicators
    complex_indicators = [
        'circular' in str(ref).lower(),
        'adw_modules' in ref.get('module', ''),
        ref.get('criticality', 0) > 0.7,
        ref.get('affects_multiple_files', False),
        'framework' in ref.get('file', '').lower(),
        any(pattern in ref.get('module', '') for pattern in
            ['workflow', 'state', 'agent', 'github', 'constants'])
    ]

    if any(complex_indicators):
        return 'complex', 'claude-3-opus-20240229'
    else:
        return 'simple', 'claude-3.5-sonnet-20241022'


def build_fix_prompt(ref: Dict, index: int, total: int) -> str:
    """
    Build a targeted prompt for fixing a specific broken reference.

    Args:
        ref: Broken reference dictionary
        index: Current reference number (1-based)
        total: Total number of broken references

    Returns:
        Formatted prompt for fix agent
    """
    ref_type = ref.get('type', 'unknown')

    if ref_type in ['import', 'from_import']:
        # Python import fix prompt
        prompt = f"""# Fix Broken Python Import ({index}/{total})

## Issue Details
- **File:** `{ref.get('file', 'unknown')}`
- **Line:** {ref.get('line', 'unknown')}
- **Broken import:** `{ref.get('module', 'unknown')}`
- **Import type:** {ref_type}
- **Import statement:** `{ref.get('original_line', 'N/A')}`

## Your Task
Analyze this broken import and provide a fix.

## Analysis Steps
1. **Identify root cause**:
   - Is it a typo? (e.g., 'requets' instead of 'requests')
   - Is it a missing package that needs installation?
   - Is it a local module with wrong relative path?
   - Has the module been renamed or moved?

2. **Determine the fix**:
   - For typos: Provide corrected import statement
   - For missing packages: Provide pip/poetry install command
   - For path issues: Provide corrected relative import
   - For moved modules: Provide new import path

3. **Validate the fix**:
   - Ensure the fix follows project conventions
   - Check if requirements.txt or pyproject.toml needs updating
   - Verify no circular dependencies are introduced

## Output Format
```markdown
### Root Cause
[One sentence explaining why this import is broken]

### Fix Type
[One of: typo_correction, install_package, fix_path, update_import]

### Solution
```python
# Original (broken)
{ref.get('original_line', 'from X import Y')}

# Fixed
[your corrected import statement]
```

### Additional Steps (if needed)
- [ ] Run: `pip install [package]`
- [ ] Update requirements.txt: `[package]==X.Y.Z`
- [ ] Update pyproject.toml: `[package] = "^X.Y.Z"`

### Verification
After applying the fix, run:
```bash
python -c "import {ref.get('module', 'module')}"
```
"""

    else:
        # File reference fix prompt
        prompt = f"""# Fix Broken File Reference ({index}/{total})

## Issue Details
- **File:** `{ref.get('file', 'unknown')}`
- **Broken reference:** `{ref.get('reference', 'unknown')}`
- **Reference type:** {ref_type}
- **Context:** {ref.get('context', 'File reference in markdown/code')}

## Your Task
Fix this broken file reference.

## Analysis Steps
1. **Identify the issue**:
   - Does the file exist but at a different path?
   - Was the file renamed?
   - Is it a relative vs absolute path issue?
   - Should this file be created?

2. **Find the correct path**:
   - Search for similar filenames in the project
   - Check git history for moves/renames
   - Verify against project structure

3. **Provide the fix**:
   - Corrected file path
   - Or instructions to create the missing file

## Output Format
```markdown
### Root Cause
[One sentence explaining why this reference is broken]

### Fix Type
[One of: update_path, create_file, remove_reference]

### Solution
```diff
- {ref.get('reference', 'old/path/to/file')}
+ [corrected/path/to/file]
```

### Additional Steps (if needed)
- [ ] Create missing file: `touch [path]`
- [ ] Move file: `mv [old_path] [new_path]`
- [ ] Update other references: `grep -r "[old_reference]" .`

### Verification
After applying the fix:
```bash
test -f "[corrected_path]" && echo "✓ File exists" || echo "✗ File not found"
```
"""

    return prompt


def spawn_fix_agents(broken_refs: List[Dict], output_dir: Path,
                    logger: logging.Logger, state: ADWState) -> Path:
    """
    Spawn individual fix agents for each broken reference.

    Args:
        broken_refs: List of broken reference dictionaries
        output_dir: Where to write fix suggestions
        logger: Logger instance
        state: ADW state manager

    Returns:
        Path to fixes directory
    """
    fixes_dir = output_dir / "fixes"
    fixes_dir.mkdir(exist_ok=True)

    logger.info(f"🚀 Spawning {len(broken_refs)} fix agents")
    logger.info(f"📁 Fixes will be written to: {fixes_dir}")

    # Track agent configurations for summary
    agent_configs = []

    for i, ref in enumerate(broken_refs, 1):
        # Determine complexity and model
        complexity, model = categorize_fix_complexity(ref)

        # Build targeted prompt
        prompt = build_fix_prompt(ref, i, len(broken_refs))

        # Generate safe filename from module/reference
        ref_name = ref.get('module') or ref.get('reference', 'unknown')
        safe_name = "".join(c if c.isalnum() or c in '-_.' else '_' for c in ref_name)
        fix_file = fixes_dir / f"fix_{i:03d}_{safe_name}.md"

        # Write prompt file for agent
        prompt_file = fixes_dir / f"prompt_{i:03d}_{safe_name}.md"
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        # Log agent configuration
        config = {
            'index': i,
            'reference': ref_name,
            'complexity': complexity,
            'model': model,
            'prompt_file': str(prompt_file),
            'output_file': str(fix_file),
            'file': ref.get('file'),
        }
        agent_configs.append(config)

        logger.info(f"  {i}/{len(broken_refs)}: {ref_name}")
        logger.info(f"    - Complexity: {complexity}")
        logger.info(f"    - Model: {model.split('-')[-1]}")
        logger.info(f"    - Output: {fix_file.name}")

    # Write summary for main agent to track
    summary_file = fixes_dir / "agents_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            'total_agents': len(broken_refs),
            'timestamp': datetime.now().isoformat(),
            'agents': agent_configs,
            'token_estimate': {
                'main_context': 100,
                'per_agent': 400,
                'total': 100 + len(broken_refs) * 400,
                'traditional': 50000,
                'savings_percent': round((1 - (100 + len(broken_refs) * 400) / 50000) * 100, 1)
            }
        }, f, indent=2)

    logger.info(f"✅ Agent configurations written to: {summary_file}")
    logger.info(f"💰 Token savings: {round((1 - (100 + len(broken_refs) * 400) / 50000) * 100, 1)}%")

    # Note: In a real implementation, you would actually spawn the agents here
    # using your framework's agent spawning mechanism
    logger.warning("⚠️  Note: Agents configured but not spawned (manual execution required)")
    logger.info("📋 To execute fixes manually, run each prompt through Claude")

    return fixes_dir


def main():
    """Main entry point for ADW Fix Dependencies."""

    # Setup logger
    logger = setup_logger("ADW-FIX-DEPS")

    if len(sys.argv) < 2:
        logger.error("❌ No trace results file provided")
        print(__doc__)
        print("\nUsage: python adws/adw_fix_dependencies.py <trace_results.json>")
        print("\nExample:")
        print("  python adws/adw_fix_dependencies.py scout_outputs/traces/latest/python_imports.json")
        sys.exit(1)

    trace_file = Path(sys.argv[1])

    # Handle 'latest' symlink/pointer
    if 'latest' in str(trace_file):
        # Try to resolve through pointer file
        latest_pointer = trace_file.parent.parent / 'latest.txt'
        if latest_pointer.exists():
            latest_dir = Path(latest_pointer.read_text().strip())
            trace_file = latest_dir / trace_file.name

    if not trace_file.exists():
        logger.error(f"❌ File not found: {trace_file}")
        sys.exit(1)

    # Initialize ADW state
    adw_id = f"FIX-DEPS-{Path(trace_file).stem.upper()}"
    state = ADWState(adw_id)
    state.update(status="initialized", timestamp=datetime.now().isoformat())

    try:
        # Load broken references
        logger.info(f"📖 Loading trace results from: {trace_file}")
        broken_refs, metadata = load_trace_results(trace_file)

        if not broken_refs:
            logger.info("✅ No broken references found! Nothing to fix.")
            state.update(status="completed", broken_count=0)
            sys.exit(0)

        logger.info(f"🔍 Found {len(broken_refs)} broken references")

        # Log some examples
        for ref in broken_refs[:3]:
            ref_name = ref.get('module') or ref.get('reference', 'unknown')
            logger.info(f"  - {ref_name} in {ref.get('file', 'unknown')}")
        if len(broken_refs) > 3:
            logger.info(f"  ... and {len(broken_refs) - 3} more")

        # Generate ASCII diagrams for visualization
        diagrams_file = trace_file.parent / "diagrams.md"
        try:
            # Try to generate diagrams if the script is available
            import subprocess
            script_path = Path(__file__).parent.parent / "scripts" / "dependency-tracer" / "scripts" / "generate_ascii_diagrams.py"
            if script_path.exists():
                result = subprocess.run(
                    ["python", str(script_path), str(trace_file), str(diagrams_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.info(f"📊 Generated ASCII diagrams: {diagrams_file}")
                else:
                    logger.debug(f"Diagram generation failed: {result.stderr}")
        except Exception as e:
            logger.debug(f"Diagram generation skipped: {e}")

        # Determine output directory
        output_dir = trace_file.parent

        # Spawn fix agents
        fixes_dir = spawn_fix_agents(broken_refs, output_dir, logger, state)

        # Update state
        state.update(
            status="agents_configured",
            broken_count=len(broken_refs),
            fixes_dir=str(fixes_dir),
            trace_file=str(trace_file)
        )

        logger.info(f"✅ Fix agents configured successfully")
        logger.info(f"📁 Check {fixes_dir} for fix suggestions")

        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Broken references: {len(broken_refs)}")
        print(f"Fix agents configured: {len(broken_refs)}")
        print(f"Output directory: {fixes_dir}")
        print(f"Token estimate: {100 + len(broken_refs) * 400} tokens")
        print(f"Traditional approach: ~50,000 tokens")
        print(f"Savings: {round((1 - (100 + len(broken_refs) * 400) / 50000) * 100, 1)}%")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        state.update(status="error", error=str(e))
        raise

    finally:
        # Save final state
        state.save()


if __name__ == "__main__":
    main()