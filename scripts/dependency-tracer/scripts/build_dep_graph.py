#!/usr/bin/env python3
"""
Build dependency graph from trace results.
v2: Improved circular dependency detection and stats.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

def build_graph(traces: List[Dict]) -> Dict:
    """Build directed graph: file -> [dependencies]."""
    graph = defaultdict(lambda: {'depends_on': [], 'broken': [], 'depended_by': []})
    
    for trace in traces:
        file = trace.get('file', '')
        ref = trace.get('reference') or trace.get('module')
        
        if not file or not ref:
            continue
        
        if trace.get('status') == 'valid':
            graph[file]['depends_on'].append(ref)
            graph[ref]['depended_by'].append(file)
        else:
            graph[file]['broken'].append(ref)
    
    # Convert defaultdict to regular dict
    return dict(graph)

def find_circular_deps(graph: Dict) -> List[List[str]]:
    """Find circular dependencies using DFS."""
    cycles = []
    visited = set()
    rec_stack = []
    
    def dfs(node: str, path: List[str]):
        if node in path:
            # Found cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            # Avoid duplicate cycles
            cycle_sorted = tuple(sorted(cycle))
            if cycle_sorted not in visited:
                cycles.append(cycle)
                visited.add(cycle_sorted)
            return
        
        if node not in graph:
            return
        
        path.append(node)
        
        for dep in graph[node].get('depends_on', []):
            dfs(dep, path.copy())
        
        path.pop()
    
    for node in graph:
        dfs(node, [])
    
    return cycles

def analyze_criticality(graph: Dict) -> Dict[str, int]:
    """Calculate how many files depend on each module (criticality score)."""
    criticality = defaultdict(int)
    
    for node, data in graph.items():
        depended_by_count = len(data.get('depended_by', []))
        if depended_by_count > 0:
            criticality[node] = depended_by_count
    
    return dict(sorted(criticality.items(), key=lambda x: x[1], reverse=True))

def main():
    if len(sys.argv) < 2:
        print("Usage: build_dep_graph.py <trace_results.json> [output.json]", file=sys.stderr)
        sys.exit(1)
    
    trace_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not trace_file.exists():
        print(f"Error: File not found: {trace_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(trace_file) as f:
        traces = json.load(f)
    
    # Build graph
    graph = build_graph(traces)
    cycles = find_circular_deps(graph)
    criticality = analyze_criticality(graph)
    
    # Calculate stats
    total_files = len(graph)
    total_deps = sum(len(v['depends_on']) for v in graph.values())
    total_broken = sum(len(v['broken']) for v in graph.values())
    
    # Find orphaned files (no dependencies, no dependents)
    orphaned = [
        node for node, data in graph.items()
        if not data['depends_on'] and not data['depended_by']
    ]
    
    # Find leaf nodes (no dependencies)
    leaves = [
        node for node, data in graph.items()
        if not data['depends_on'] and data['depended_by']
    ]
    
    # Find root nodes (no dependents)
    roots = [
        node for node, data in graph.items()
        if data['depends_on'] and not data['depended_by']
    ]
    
    result = {
        'stats': {
            'files': total_files,
            'dependencies': total_deps,
            'broken': total_broken,
            'circular_dependencies': len(cycles),
            'orphaned_files': len(orphaned),
            'leaf_nodes': len(leaves),
            'root_nodes': len(roots)
        },
        'criticality': criticality,
        'circular_dependencies': cycles,
        'orphaned_files': orphaned,
        'leaf_nodes': leaves,
        'root_nodes': roots,
        'graph': graph
    }
    
    # Output
    output_json = json.dumps(result, indent=2)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output_json)
        print(f"✅ Dependency graph saved to: {output_file}")
        
        # Print summary to stdout
        print(f"\n📊 Graph Statistics:")
        print(f"  Files: {total_files}")
        print(f"  Dependencies: {total_deps}")
        print(f"  Broken: {total_broken}")
        print(f"  Circular: {len(cycles)}")
        
        if criticality:
            print(f"\n🎯 Most Critical Dependencies:")
            for dep, count in list(criticality.items())[:5]:
                print(f"  {dep}: {count} files depend on it")
    else:
        print(output_json)

if __name__ == '__main__':
    main()
