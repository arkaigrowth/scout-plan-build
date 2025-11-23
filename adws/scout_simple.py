#!/usr/bin/env python3
"""
WORKING Scout - Uses native tools instead of broken external ones.
This actually works because it uses Glob and Grep instead of gemini/opencode.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict

# Import canonical path constants
try:
    from adw_modules.constants import get_scout_output_path
except ImportError:
    # Fallback for when running outside of framework
    def get_scout_output_path():
        path = Path("scout_outputs/relevant_files.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

def scout_files(task: str, max_files: int = 50) -> Dict:
    """
    Scout for files using WORKING native tools.
    No external AI tools needed - just glob and grep.
    """
    print(f"🔍 Scouting for: {task}")

    all_files = set()

    # Extract keywords from task for searching
    keywords = task.lower().split()[:3]  # First 3 words

    # Method 1: Find Python files with glob
    print("  → Finding Python files...")
    result = subprocess.run(
        ["find", ".", "-type", "f", "-name", "*.py", "-o", "-name", "*.md"],
        capture_output=True,
        text=True,
        cwd="."
    )

    if result.stdout:
        files = result.stdout.strip().split('\n')
        all_files.update([f for f in files if f and '.git' not in f][:max_files//2])

    # Method 2: Grep for keywords (if we have any meaningful ones)
    if any(len(k) > 3 for k in keywords):  # Only search for words > 3 chars
        keyword = next(k for k in keywords if len(k) > 3)

        # SECURITY: Validate keyword to prevent command injection
        # Only allow alphanumeric, underscore, hyphen, dot
        import re
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', keyword):
            print(f"  ⚠️ Skipping unsafe keyword: {keyword}")
        else:
            print(f"  → Searching for '{keyword}'...")

            grep_result = subprocess.run(
                ["grep", "-r", "-l", "--", keyword, ".", "--include=*.py", "--include=*.js"],
                capture_output=True,
                text=True,
                cwd=".",
                timeout=5  # Don't hang
            )

            if grep_result.returncode == 0 and grep_result.stdout:
                files = grep_result.stdout.strip().split('\n')
                all_files.update([f for f in files if f and '.git' not in f][:max_files//2])

    # CRITICAL: Sort for determinism (MVP fix!)
    sorted_files = sorted(list(all_files))[:max_files]

    # Save to canonical location (single source of truth!)
    output_file = get_scout_output_path()

    output_data = {
        "task": task,
        "files": sorted_files,
        "count": len(sorted_files),
        "method": "native_tools"
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✅ Found {len(sorted_files)} files")
    print(f"📁 Saved to: {output_file}")

    return output_data

def main():
    """CLI interface."""
    import sys

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Find relevant files"

    result = scout_files(task)

    # Print first few files
    print("\nFirst 5 files found:")
    for f in result['files'][:5]:
        print(f"  - {f}")

    print(f"\nTotal: {result['count']} files")
    print(f"Output: scout_outputs/relevant_files.json")

if __name__ == "__main__":
    main()