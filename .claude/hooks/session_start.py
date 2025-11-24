#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

"""
Session Start Hook - Detects compacted session handoff files.

This hook runs on session start and after compaction to notify the user
if previous session context is available for resumption.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Handoff files location relative to project root
HANDOFFS_DIR = "ai_docs/sessions/handoffs"

# Pattern for handoff files: handoff-YYYY-MM-DD.md or handoff-YYYY-MM-DD-*.md
HANDOFF_PATTERN = re.compile(r"^handoff-(\d{4}-\d{2}-\d{2})(?:-\w+)?\.md$")


def parse_handoff_date(filename: str) -> datetime | None:
    """Extract date from handoff filename."""
    match = HANDOFF_PATTERN.match(filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
        except ValueError:
            return None
    return None


def get_handoff_files(handoffs_path: Path) -> list[tuple[Path, datetime]]:
    """
    Find all valid handoff files and their dates.

    Returns:
        List of (file_path, date) tuples, sorted by date descending (newest first)
    """
    if not handoffs_path.exists() or not handoffs_path.is_dir():
        return []

    handoff_files = []
    for file_path in handoffs_path.iterdir():
        if file_path.is_file():
            date = parse_handoff_date(file_path.name)
            if date:
                handoff_files.append((file_path, date))

    # Sort by date descending (newest first)
    handoff_files.sort(key=lambda x: x[1], reverse=True)
    return handoff_files


def format_age(date: datetime) -> str:
    """Format the age of a handoff file in human-readable form."""
    today = datetime.now()
    delta = today - date

    if delta.days == 0:
        return "today"
    elif delta.days == 1:
        return "yesterday"
    elif delta.days < 7:
        return f"{delta.days} days ago"
    elif delta.days < 30:
        weeks = delta.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        return date.strftime("%Y-%m-%d")


def main():
    try:
        # Read JSON input from stdin (contains session_id, cwd, etc.)
        input_data = json.load(sys.stdin)

        # Get project directory from input or use current working directory
        cwd = input_data.get("cwd", ".")
        project_dir = Path(cwd)

        # Build path to handoffs directory
        handoffs_path = project_dir / HANDOFFS_DIR

        # Find handoff files
        handoff_files = get_handoff_files(handoffs_path)

        if not handoff_files:
            # No handoff files found - exit silently
            sys.exit(0)

        # Check for recent handoffs (within last 7 days)
        today = datetime.now()
        cutoff = today - timedelta(days=7)
        recent_files = [(f, d) for f, d in handoff_files if d >= cutoff]

        # If we have handoff files, output notification
        if handoff_files:
            print("\nCOMPACTED_SESSION_AVAILABLE")
            print("=" * 40)
            print("Handoff files found:")

            # Show up to 5 most recent files
            for file_path, date in handoff_files[:5]:
                age = format_age(date)
                marker = " (most recent)" if file_path == handoff_files[0][0] else ""
                print(f"  - {file_path.name} [{age}]{marker}")

            if len(handoff_files) > 5:
                print(f"  ... and {len(handoff_files) - 5} more")

            print("")

            if recent_files:
                print("To resume your previous session context, run:")
                print("  /session:resume")
                print("")
                print("Or ask me which session to load if you have multiple.")
            else:
                print("Note: All handoff files are older than 7 days.")
                print("Run /session:resume to see available sessions.")

            print("=" * 40)
            print("")

        sys.exit(0)

    except json.JSONDecodeError:
        # No valid JSON input - exit silently
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully - exit silently
        sys.exit(0)


if __name__ == "__main__":
    main()
