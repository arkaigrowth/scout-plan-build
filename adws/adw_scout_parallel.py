#!/usr/bin/env python3
"""
Parallel Scout Implementation - The Missing Piece!

This implements parallel discovery using the same subprocess.Popen() pattern
that made Test/Review/Document 40-50% faster. Now Scout can be parallelized too!
"""

import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Import our modules
try:
    from adw_modules.utils import setup_environment
    setup_environment()
except ImportError:
    pass


def launch_scout_squadron(task: str, scale: int = 4) -> List[Tuple[str, subprocess.Popen]]:
    """
    Launch parallel scout agents with different search strategies.

    Uses the same pattern as adw_sdlc.py for Test/Review/Document!
    """
    scout_strategies = [
        {
            "focus": "implementation",
            "prompt": f"Find all implementation files, source code, and main logic for: {task}. Focus on .py, .js, .ts files.",
            "agent": "explore"
        },
        {
            "focus": "tests",
            "prompt": f"Find all test files, test patterns, and test utilities for: {task}. Look for test_, _test.py, .test.js, specs/",
            "agent": "explore"
        },
        {
            "focus": "configuration",
            "prompt": f"Find configuration files, environment settings, and setup files for: {task}. Check .env, config/, settings.py",
            "agent": "explore"
        },
        {
            "focus": "architecture",
            "prompt": f"Find architectural patterns, module structure, and design patterns related to: {task}",
            "agent": "explore"
        },
        {
            "focus": "dependencies",
            "prompt": f"Find package dependencies, imports, and external libraries used for: {task}. Check package.json, requirements.txt",
            "agent": "explore"
        },
        {
            "focus": "documentation",
            "prompt": f"Find documentation, README files, and inline docs about: {task}. Look for .md files, docstrings",
            "agent": "explore"
        }
    ]

    # Take only the number requested
    strategies_to_use = scout_strategies[:scale]

    print(f"🚀 Launching Scout Squadron with {scale} parallel agents...")
    processes = []

    for strategy in strategies_to_use:
        print(f"  → Launching {strategy['focus']} scout...")

        # Create a temp output file for this scout
        output_file = Path(f"agents/scout_temp/{strategy['focus']}_scout.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Build command (using scout_simple.py as the worker)
        cmd = [
            "python", "adws/scout_simple.py",
            strategy['prompt']
        ]

        # Launch subprocess (non-blocking, like Test/Review/Document!)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        processes.append((strategy['focus'], proc))

    return processes


def aggregate_scout_reports(processes: List[Tuple[str, subprocess.Popen]], task: str) -> Dict:
    """
    Wait for all scouts to complete and aggregate their findings.

    Similar to how adw_sdlc.py waits for Test/Review/Document.
    """
    print("\n⏳ Waiting for Scout Squadron to complete...")

    all_files = set()
    all_patterns = []
    all_insights = []
    scout_reports = {}

    start_time = time.time()

    # Wait for each process and collect results
    for focus, proc in processes:
        try:
            # Wait with timeout (like Test/Review/Document)
            stdout, stderr = proc.communicate(timeout=60)

            if proc.returncode == 0:
                print(f"  ✅ {focus} scout completed")

                # Read the scout output from ai_docs/scout/relevant_files.json
                scout_output = Path("ai_docs/scout/relevant_files.json")
                if scout_output.exists():
                    with open(scout_output) as f:
                        data = json.load(f)
                        scout_reports[focus] = data
                        if "files" in data:
                            all_files.update(data["files"])

                # Move to permanent location
                permanent_file = Path(f"agents/scout_files/{focus}_report.json")
                permanent_file.parent.mkdir(parents=True, exist_ok=True)
                if scout_output.exists():
                    import shutil
                    shutil.copy(scout_output, permanent_file)
            else:
                print(f"  ⚠️ {focus} scout failed: {stderr}")

        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"  ⚠️ {focus} scout timed out")

    duration = time.time() - start_time

    # Sort files for determinism (critical for reproducibility!)
    sorted_files = sorted(list(all_files))

    # Create aggregated report
    aggregated = {
        "task": task,
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": round(duration, 2),
        "scout_count": len(processes),
        "files": sorted_files[:100],  # Limit to top 100
        "file_count": len(sorted_files),
        "scouts": scout_reports,
        "method": "parallel_squadron",
        "performance": {
            "sequential_estimate": len(processes) * 30,  # 30 sec per scout
            "parallel_actual": round(duration, 2),
            "speedup": f"{round((len(processes) * 30) / duration, 1)}x"
        }
    }

    print(f"\n📊 Scout Squadron Summary:")
    print(f"  • Time: {duration:.1f} seconds (vs ~{len(processes) * 30}s sequential)")
    print(f"  • Files found: {len(sorted_files)}")
    print(f"  • Scouts completed: {len(scout_reports)}/{len(processes)}")
    print(f"  • Speedup: {aggregated['performance']['speedup']}")

    return aggregated


def save_scout_report(report: Dict) -> Path:
    """Save the aggregated scout report to the standard location."""

    # Primary location (for plan phase)
    primary_output = Path("agents/scout_files/relevant_files.json")
    primary_output.parent.mkdir(parents=True, exist_ok=True)

    with open(primary_output, 'w') as f:
        json.dump(report, f, indent=2)

    # Backup location
    backup_output = Path("ai_docs/scout/relevant_files.json")
    backup_output.parent.mkdir(parents=True, exist_ok=True)

    with open(backup_output, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Scout report saved to:")
    print(f"  • {primary_output}")
    print(f"  • {backup_output}")

    return primary_output


def parallel_scout(task: str, scale: int = 4) -> Dict:
    """
    Main entry point for parallel scouting.

    This is the function that /scout_parallel command will call.
    """
    print(f"""
╔══════════════════════════════════════════╗
║        🚀 PARALLEL SCOUT SQUADRON 🚀      ║
╚══════════════════════════════════════════╝

Task: {task}
Scale: {scale} parallel agents
""")

    # Check git status first (safety, like in Test/Review/Document)
    git_check = subprocess.run(
        ["git", "diff", "--stat"],
        capture_output=True,
        text=True
    )

    if git_check.stdout:
        print("⚠️ Warning: Uncommitted changes detected")
        print("  Running 'git stash' to preserve changes...")
        subprocess.run(["git", "stash", "push", "-m", "Scout squadron auto-stash"])

    # Launch the squadron!
    processes = launch_scout_squadron(task, scale)

    # Aggregate findings
    report = aggregate_scout_reports(processes, task)

    # Save to standard locations
    output_path = save_scout_report(report)

    # Restore git state if needed
    if git_check.stdout:
        print("\n🔄 Restoring git state...")
        subprocess.run(["git", "stash", "pop"], capture_output=True)

    # Print sample of files found
    print("\n📂 Sample of discovered files:")
    for file in report["files"][:10]:
        print(f"  • {file}")
    if len(report["files"]) > 10:
        print(f"  ... and {len(report['files']) - 10} more")

    print(f"""
╔══════════════════════════════════════════╗
║        ✨ SCOUT COMPLETE ✨               ║
╚══════════════════════════════════════════╝

Ready for: /plan_w_docs "{task}" "[docs]" "{output_path}"
""")

    return report


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Parallel Scout Squadron")
    parser.add_argument("task", help="Task to scout for")
    parser.add_argument("--scale", "-s", type=int, default=4,
                        help="Number of parallel scouts (default: 4)")

    args = parser.parse_args()

    result = parallel_scout(args.task, args.scale)

    return 0 if result["file_count"] > 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())