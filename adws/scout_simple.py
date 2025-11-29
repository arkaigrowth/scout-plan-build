#!/usr/bin/env python3
"""
Enhanced Scout - Combines context augmentation with native tools.

Uses hybrid search (Gemini + ripgrep) when available, falls back to native tools.
Also leverages mem0 for persistent learnings across sessions.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Import canonical path constants
try:
    from adw_modules.constants import get_scout_output_path
except ImportError:
    # Fallback for when running outside of framework
    def get_scout_output_path():
        path = Path("scout_outputs/relevant_files.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

# Try to import context augmentation (optional dependency)
_context_augmentation_available = False
try:
    from adw_modules.context_augmentation import ContextAugmenter, get_augmenter
    from adw_modules.gemini_search import HybridSearchClient, quick_search
    _context_augmentation_available = True
except ImportError:
    pass


def scout_with_context(task: str, max_files: int = 50) -> Dict:
    """
    Scout using context augmentation (hybrid search + memory).

    This is the preferred method when context augmentation is available.
    Falls back to scout_files_native() if not configured.
    """
    if not _context_augmentation_available:
        print("  ℹ️  Context augmentation not available, using native tools")
        return scout_files_native(task, max_files)

    print(f"🔍 Scouting with context augmentation: {task}")

    try:
        # Get augmenter instance
        augmenter = get_augmenter()

        # Check what's available
        stats = augmenter.get_stats()
        memory_enabled = stats.get("memory", {}).get("enabled", False)
        gemini_enabled = stats.get("search", {}).get("gemini_enabled", False)

        print(f"  → Memory: {'✅' if memory_enabled else '❌'}")
        print(f"  → Gemini: {'✅' if gemini_enabled else '❌ (using ripgrep only)'}")

        # Execute hybrid search
        result = augmenter.search.hybrid_search(task, limit=max_files)

        # Extract file paths from snippets
        files = []
        for snippet in result.snippets:
            if snippet.file_path and snippet.file_path not in files:
                files.append(snippet.file_path)

        # If we found files via context augmentation, use them
        if files:
            print(f"  → Found {len(files)} files via {', '.join(result.sources_used)}")

            # Record the discovery for future reference
            if result.snippets:
                augmenter.memory.record_discovery(
                    task=task,
                    files=files[:10],
                    source="scout_with_context"
                )

            # Sort for determinism
            sorted_files = sorted(files)[:max_files]

            output_data = {
                "task": task,
                "files": sorted_files,
                "count": len(sorted_files),
                "method": "context_augmentation",
                "sources": result.sources_used,
                "query_type": result.query_type.value,
            }

            # Save to canonical location
            output_file = get_scout_output_path()
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"✅ Found {len(sorted_files)} files")
            print(f"📁 Saved to: {output_file}")

            return output_data

        else:
            # Fallback to native tools if hybrid search found nothing
            print("  ⚠️  No results from hybrid search, falling back to native tools")
            return scout_files_native(task, max_files)

    except Exception as e:
        print(f"  ⚠️  Context augmentation failed: {e}")
        print("  → Falling back to native tools")
        return scout_files_native(task, max_files)


def scout_files_native(task: str, max_files: int = 50) -> Dict:
    """
    Scout for files using native tools (find + grep).

    This is the fallback when context augmentation is not available.
    No external AI tools needed - just glob and grep.
    """
    print(f"🔍 Scouting (native): {task}")

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

def scout_files(task: str, max_files: int = 50) -> Dict:
    """
    Main entry point for scouting - uses context augmentation when available.

    This is the primary function to call. It will:
    1. Try context augmentation (hybrid search + memory) if configured
    2. Fall back to native tools (find + grep) if not

    Args:
        task: Description of what to search for
        max_files: Maximum number of files to return

    Returns:
        Dict with task, files, count, and method used
    """
    return scout_with_context(task, max_files)


def main():
    """CLI interface."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Scout for relevant files")
    parser.add_argument("task", nargs="*", default=["Find relevant files"],
                        help="Task description to search for")
    parser.add_argument("--native", action="store_true",
                        help="Force native tools only (skip context augmentation)")
    parser.add_argument("--max-files", type=int, default=50,
                        help="Maximum files to return")

    args = parser.parse_args()
    task = " ".join(args.task)

    if args.native:
        result = scout_files_native(task, args.max_files)
    else:
        result = scout_files(task, args.max_files)

    # Print first few files
    print("\nFirst 5 files found:")
    for f in result['files'][:5]:
        print(f"  - {f}")

    print(f"\nTotal: {result['count']} files")
    print(f"Output: scout_outputs/relevant_files.json")

if __name__ == "__main__":
    main()