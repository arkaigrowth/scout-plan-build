#!/usr/bin/env python3
"""
ASCII Diagram Generator for Dependency Tracer
Generates visual representations of import dependencies and broken references.

Usage:
    python generate_ascii_diagrams.py <trace_results.json> [output.md]

Diagram Types:
    1. Import Tree - Shows file → module dependencies
    2. Broken Reference Map - Highlights problematic imports
    3. Module Hierarchy - Package structure visualization
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Tuple

# Box drawing characters for trees
BOX_CHARS = {
    'vertical': '│',
    'horizontal': '─',
    'top_left': '┌',
    'top_right': '┐',
    'bottom_left': '└',
    'bottom_right': '┘',
    'branch': '├',
    'last_branch': '└',
    'tee': '├',
    'cross': '┼'
}

# Status indicators
STATUS_SYMBOLS = {
    'valid': '✓',
    'broken': '✗',
    'warning': '⚠',
    'unknown': '?'
}


def load_trace_results(trace_file: Path) -> List[Dict]:
    """Load and parse trace results JSON."""
    with open(trace_file) as f:
        return json.load(f)


def generate_import_tree(imports: List[Dict]) -> str:
    """Generate a tree showing import relationships grouped by file."""
    # Group imports by file
    by_file = defaultdict(list)
    for imp in imports:
        by_file[imp['file']].append(imp)

    output = []
    output.append("# Import Dependency Tree\n")
    output.append("```")

    files = sorted(by_file.keys())
    for i, file in enumerate(files):
        is_last_file = (i == len(files) - 1)
        file_prefix = BOX_CHARS['last_branch'] if is_last_file else BOX_CHARS['branch']

        # Show file with import count
        import_count = len(by_file[file])
        broken_count = sum(1 for imp in by_file[file] if imp.get('status') == 'broken')

        status = '✗' if broken_count > 0 else '✓'
        output.append(f"{file_prefix}─ {status} {Path(file).name} ({import_count} imports, {broken_count} broken)")

        # Show imports for this file
        continuation = "   " if is_last_file else "│  "
        imports_list = by_file[file]

        for j, imp in enumerate(imports_list):
            is_last_import = (j == len(imports_list) - 1)
            import_prefix = BOX_CHARS['last_branch'] if is_last_import else BOX_CHARS['branch']

            status = STATUS_SYMBOLS.get(imp.get('status', 'unknown'), '?')
            module = imp['module']
            imp_type = "from" if imp['type'] == 'from_import' else "import"
            location = imp.get('location', 'unknown')

            # Color broken imports differently (using markdown syntax)
            if imp.get('status') == 'broken':
                output.append(f"{continuation}{import_prefix}─ {status} **{module}** [{imp_type}] (BROKEN - {location})")
            else:
                output.append(f"{continuation}{import_prefix}─ {status} {module} [{imp_type}] ({location})")

    output.append("```\n")
    return '\n'.join(output)


def generate_broken_reference_map(imports: List[Dict]) -> str:
    """Generate a focused view of broken imports and their relationships."""
    broken = [imp for imp in imports if imp.get('status') == 'broken']

    if not broken:
        return "# Broken Reference Map\n\nNo broken references found! ✓\n"

    # Group by module to see which modules are commonly broken
    by_module = defaultdict(list)
    for imp in broken:
        by_module[imp['module']].append(imp['file'])

    output = []
    output.append("# Broken Reference Map\n")
    output.append(f"Found {len(broken)} broken imports across {len(set(imp['file'] for imp in broken))} files\n")
    output.append("```")
    output.append("BROKEN MODULES")
    output.append("│")

    modules = sorted(by_module.keys(), key=lambda m: len(by_module[m]), reverse=True)

    for i, module in enumerate(modules):
        is_last = (i == len(modules) - 1)
        prefix = BOX_CHARS['last_branch'] if is_last else BOX_CHARS['branch']

        files = by_module[module]
        output.append(f"{prefix}─ ✗ {module} ({len(files)} file{'s' if len(files) > 1 else ''})")

        continuation = "   " if is_last else "│  "
        for j, file in enumerate(sorted(set(files))):
            is_last_file = (j == len(set(files)) - 1)
            file_prefix = BOX_CHARS['last_branch'] if is_last_file else BOX_CHARS['branch']
            output.append(f"{continuation}{file_prefix}─ {Path(file).name}")

    output.append("```\n")
    return '\n'.join(output)


def generate_module_hierarchy(imports: List[Dict]) -> str:
    """Generate a hierarchy showing package structure from imports."""
    # Extract unique local modules (starting with project packages)
    local_modules = set()

    for imp in imports:
        module = imp['module']
        # Focus on local/project modules (e.g., adw_modules.*)
        if not module.startswith(('.', '/')):
            if imp.get('location') == 'local' or 'adw' in module or module.startswith('scripts'):
                local_modules.add(module)

    if not local_modules:
        return "# Module Hierarchy\n\nNo local modules detected.\n"

    # Build hierarchy tree
    tree = {}
    for module in local_modules:
        parts = module.split('.')
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    output = []
    output.append("# Module Hierarchy\n")
    output.append("```")
    output.append("Local Module Structure:")
    output.append("│")

    def render_tree(node: Dict, prefix: str = "", is_last: bool = False) -> None:
        items = list(node.items())
        for i, (key, subtree) in enumerate(items):
            is_last_item = (i == len(items) - 1)

            # Determine if this module is imported anywhere
            full_path = prefix.replace("│  ", "").replace("├─ ", "").replace("└─ ", "").replace("   ", "").strip()
            if full_path:
                full_path = full_path.replace(" ", ".") + "." + key
            else:
                full_path = key

            # Check if this module appears in broken imports
            is_broken = any(imp['module'] == full_path and imp.get('status') == 'broken'
                          for imp in imports)

            symbol = '✗' if is_broken else '✓'
            branch = BOX_CHARS['last_branch'] if is_last_item else BOX_CHARS['branch']

            output.append(f"{prefix}{branch}─ {symbol} {key}")

            if subtree:
                extension = "   " if is_last_item else "│  "
                render_tree(subtree, prefix + extension, is_last_item)

    render_tree(tree, "")
    output.append("```\n")
    return '\n'.join(output)


def generate_statistics_summary(imports: List[Dict]) -> str:
    """Generate a statistical summary of the trace results."""
    total = len(imports)
    broken = sum(1 for imp in imports if imp.get('status') == 'broken')
    valid = sum(1 for imp in imports if imp.get('status') == 'valid')

    # Group by location
    by_location = defaultdict(int)
    for imp in imports:
        by_location[imp.get('location', 'unknown')] += 1

    # Most imported modules
    module_counts = defaultdict(int)
    for imp in imports:
        module_counts[imp['module']] += 1

    output = []
    output.append("# Import Statistics Summary\n")
    output.append("```")
    output.append(f"Total Imports: {total}")
    output.append(f"├─ ✓ Valid: {valid} ({valid*100//total if total else 0}%)")
    output.append(f"└─ ✗ Broken: {broken} ({broken*100//total if total else 0}%)")
    output.append("")
    output.append("By Location:")

    locations = sorted(by_location.items(), key=lambda x: x[1], reverse=True)
    for i, (location, count) in enumerate(locations):
        is_last = (i == len(locations) - 1)
        prefix = BOX_CHARS['last_branch'] if is_last else BOX_CHARS['branch']
        output.append(f"{prefix}─ {location}: {count} ({count*100//total if total else 0}%)")

    output.append("")
    output.append("Top 5 Most Imported Modules:")
    top_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (module, count) in enumerate(top_modules):
        is_last = (i == len(top_modules) - 1)
        prefix = BOX_CHARS['last_branch'] if is_last else BOX_CHARS['branch']
        output.append(f"{prefix}─ {module}: {count} times")

    output.append("```\n")
    return '\n'.join(output)


def main():
    """Main entry point for diagram generation."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python generate_ascii_diagrams.py <trace_results.json> [output.md]")
        sys.exit(1)

    trace_file = Path(sys.argv[1])
    if not trace_file.exists():
        print(f"Error: File not found: {trace_file}")
        sys.exit(1)

    # Load trace results
    try:
        imports = load_trace_results(trace_file)
        print(f"Loaded {len(imports)} import records from {trace_file}")
    except Exception as e:
        print(f"Error loading trace results: {e}")
        sys.exit(1)

    # Generate diagrams
    diagrams = []
    diagrams.append(generate_statistics_summary(imports))
    diagrams.append(generate_import_tree(imports))
    diagrams.append(generate_broken_reference_map(imports))
    diagrams.append(generate_module_hierarchy(imports))

    # Combine all diagrams
    output = '\n'.join(diagrams)

    # Save or print output
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"✓ Diagrams saved to: {output_file}")
    else:
        print("\n" + output)


if __name__ == "__main__":
    main()