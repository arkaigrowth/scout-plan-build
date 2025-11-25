#!/usr/bin/env python3
"""
Generate ASCII diagrams from dependency trace results.
Creates visual representations of import trees, reference maps, and broken dependencies.

Usage:
    python generate_ascii_diagrams.py <trace_results.json> [output_format]

Output formats:
    tree     - Hierarchical import tree (default)
    matrix   - Cross-reference matrix
    broken   - Broken references visualization
    summary  - Combined overview diagram
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional

def load_trace_results(trace_file: Path) -> List[Dict]:
    """Load trace results from JSON file."""
    with open(trace_file) as f:
        return json.load(f)

def generate_import_tree(results: List[Dict]) -> str:
    """Generate ASCII tree showing import hierarchy."""
    # Build import graph
    imports_by_file = defaultdict(list)
    for item in results:
        if item.get('type') in ['import', 'from_import']:
            file = item['file'].replace('~/AI/scout_plan_build_mvp/', '')
            module = item.get('module', 'unknown')
            status = '✓' if item.get('status') == 'valid' else '✗'
            imports_by_file[file].append(f"{status} {module}")

    # Generate tree
    tree_lines = ["═══ Python Import Tree ═══\n"]
    for file, imports in sorted(imports_by_file.items()):
        if not imports:
            continue
        tree_lines.append(f"📁 {file}")
        for i, imp in enumerate(imports[:10]):  # Limit to 10 per file
            if i == len(imports) - 1 or i == 9:
                tree_lines.append(f"    └── {imp}")
            else:
                tree_lines.append(f"    ├── {imp}")
        if len(imports) > 10:
            tree_lines.append(f"    └── ... (+{len(imports)-10} more)")
        tree_lines.append("")

    return "\n".join(tree_lines)

def generate_reference_matrix(results: List[Dict]) -> str:
    """Generate cross-reference matrix for file dependencies."""
    # Collect unique files
    files = set()
    refs = defaultdict(set)

    for item in results:
        if 'file' in item and 'reference' in item:
            from_file = Path(item['file']).name
            to_file = Path(item['reference']).name if '/' in item['reference'] else item['reference']
            files.add(from_file)
            files.add(to_file)
            refs[from_file].add(to_file)

    # Limit matrix size
    file_list = sorted(list(files))[:15]

    # Generate matrix
    matrix_lines = ["═══ Reference Matrix ═══\n"]

    # Header
    header = "            "
    for f in file_list:
        header += f[:8].center(9)
    matrix_lines.append(header)
    matrix_lines.append("─" * len(header))

    # Rows
    for from_file in file_list:
        row = f"{from_file[:10]:11}"
        for to_file in file_list:
            if from_file == to_file:
                row += "    ·    "
            elif to_file in refs.get(from_file, set()):
                row += "    ▶    "
            else:
                row += "         "
        matrix_lines.append(row)

    matrix_lines.append("\n▶ = references")
    return "\n".join(matrix_lines)

def generate_broken_visualization(results: List[Dict]) -> str:
    """Visualize broken references with context."""
    broken = [r for r in results if r.get('status') == 'broken']

    if not broken:
        return "═══ No Broken References Found! ═══"

    # Group by type
    broken_imports = [b for b in broken if b.get('type') in ['import', 'from_import']]
    broken_refs = [b for b in broken if b.get('type') not in ['import', 'from_import']]

    viz_lines = ["═══ Broken Dependencies ═══\n"]

    # Import issues
    if broken_imports:
        viz_lines.append("🔴 Broken Imports:")
        viz_lines.append("┌" + "─" * 78 + "┐")

        for i, item in enumerate(broken_imports[:10]):
            file = Path(item['file']).name
            module = item.get('module', 'unknown')
            viz_lines.append(f"│ {file:30} ✗→ {module:43} │")

        if len(broken_imports) > 10:
            viz_lines.append(f"│ ... and {len(broken_imports)-10} more{' '*59}│")

        viz_lines.append("└" + "─" * 78 + "┘")
        viz_lines.append("")

    # File reference issues
    if broken_refs:
        viz_lines.append("🔴 Broken File References:")
        viz_lines.append("┌" + "─" * 78 + "┐")

        for i, item in enumerate(broken_refs[:10]):
            file = Path(item['file']).name
            ref = item.get('reference', 'unknown')
            if len(ref) > 43:
                ref = "..." + ref[-40:]
            viz_lines.append(f"│ {file:30} ✗→ {ref:43} │")

        if len(broken_refs) > 10:
            viz_lines.append(f"│ ... and {len(broken_refs)-10} more{' '*59}│")

        viz_lines.append("└" + "─" * 78 + "┘")

    return "\n".join(viz_lines)

def generate_summary_diagram(results: List[Dict]) -> str:
    """Generate combined summary diagram with statistics."""
    total = len(results)
    valid = len([r for r in results if r.get('status') == 'valid'])
    broken = len([r for r in results if r.get('status') == 'broken'])

    # Count by type
    type_counts = Counter(r.get('type', 'unknown') for r in results)

    # Most imported modules
    module_counts = Counter(r.get('module', '') for r in results if r.get('module'))
    top_modules = module_counts.most_common(5)

    # Most referenced files
    file_counts = Counter(Path(r.get('file', '')).name for r in results if r.get('file'))
    top_files = file_counts.most_common(5)

    diagram = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                       DEPENDENCY ANALYSIS SUMMARY                          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Total References: {total:4}     Valid: {valid:4} ✓     Broken: {broken:4} ✗           ║
║                                                                             ║
║  ┌─────────────────────┐     ┌─────────────────────┐                      ║
║  │   Reference Types   │     │    Health Status    │                      ║
║  ├─────────────────────┤     ├─────────────────────┤                      ║
"""

    # Add type breakdown
    for ref_type, count in sorted(type_counts.items())[:3]:
        diagram += f"║  │ {ref_type[:15]:15} {count:4} │     "

    # Add health bar
    if total > 0:
        health_pct = (valid / total) * 100
        bar_width = 20
        filled = int((valid / total) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        diagram += f"│ Health: {bar} {health_pct:.0f}% │                      ║\n"

    diagram += f"""║  └─────────────────────┘     └─────────────────────┘                      ║
║                                                                             ║
║  Top Imported Modules:            Most Active Files:                       ║
║  ┌──────────────────────────┐     ┌──────────────────────────┐            ║"""

    # Add top modules and files
    for i in range(5):
        left_content = ""
        right_content = ""

        if i < len(top_modules):
            mod, count = top_modules[i]
            if len(mod) > 20:
                mod = mod[:17] + "..."
            left_content = f"{i+1}. {mod[:20]:20} ({count})"

        if i < len(top_files):
            file, count = top_files[i]
            if len(file) > 20:
                file = file[:17] + "..."
            right_content = f"{i+1}. {file[:20]:20} ({count})"

        diagram += f"\n║  │ {left_content:26} │     │ {right_content:26} │            ║"

    diagram += """
║  └──────────────────────────┘     └──────────────────────────┘            ║
║                                                                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

    return diagram

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    trace_file = Path(sys.argv[1])
    if not trace_file.exists():
        print(f"Error: File not found: {trace_file}")
        sys.exit(1)

    output_format = sys.argv[2] if len(sys.argv) > 2 else 'summary'

    # Load results
    results = load_trace_results(trace_file)

    # Generate requested diagram
    if output_format == 'tree':
        print(generate_import_tree(results))
    elif output_format == 'matrix':
        print(generate_reference_matrix(results))
    elif output_format == 'broken':
        print(generate_broken_visualization(results))
    else:  # summary
        print(generate_summary_diagram(results))
        if any(r.get('status') == 'broken' for r in results):
            print("\nRun with 'broken' format to see detailed broken references:")
            print(f"  python {sys.argv[0]} {trace_file} broken")

if __name__ == "__main__":
    main()