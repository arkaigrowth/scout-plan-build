#!/usr/bin/env python3
"""
Research Index Auto-Updater

Scans ai_docs/research/ subfolders and updates the README.md index tables.
Parses **Key**: Value frontmatter format and rebuilds tables from structured data.

Usage:
    python scripts/update-research-index.py           # Apply updates
    python scripts/update-research-index.py --dry-run # Show what would change
    python scripts/update-research-index.py --check   # Exit 1 if changes needed (for CI)
    python scripts/update-research-index.py --verbose # Detailed output
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# Configuration
SUBFOLDERS = ["videos", "articles", "implementations", "papers", "llm-chats"]

# Marker patterns for finding index sections in README
MARKER_START = "<!-- INDEX:{folder}:start -->"
MARKER_END = "<!-- INDEX:{folder}:end -->"

# Frontmatter regex - handles both **Key:** Value AND **Key**: Value formats
# Pattern 1: **Key:** Value (colon inside bold)
# Pattern 2: **Key**: Value (colon outside bold)
FRONTMATTER_PATTERNS = [
    re.compile(r"\*\*([^*:]+):\*\*\s*(.+)"),    # **Key:** Value
    re.compile(r"\*\*([^*]+)\*\*:\s*(.+)"),      # **Key**: Value
]

# Table header configurations for each folder type
TABLE_CONFIGS = {
    "videos": {
        "headers": ["Source", "Topic", "File", "Date Added"],
        "source_keys": ["creator", "source", "author", "channel"],
        "topic_keys": ["topic", "title", "subject"],
        "date_keys": ["date analyzed", "date added", "date"],
    },
    "articles": {
        "headers": ["Source", "Topic", "File", "Date Added"],
        "source_keys": ["source", "author", "publication", "site"],
        "topic_keys": ["topic", "title", "subject"],
        "date_keys": ["date added", "date analyzed", "date"],
    },
    "implementations": {
        "headers": ["Repository", "Topic", "File", "Date Added"],
        "source_keys": ["repository", "source", "author", "repo"],
        "topic_keys": ["topic", "title", "subject"],
        "date_keys": ["date added", "date analyzed", "date"],
    },
    "papers": {
        "headers": ["Title", "Topic", "File", "Date Added"],
        "source_keys": ["title", "paper", "name"],
        "topic_keys": ["topic", "subject", "area"],
        "date_keys": ["date added", "date analyzed", "date"],
    },
    "llm-chats": {
        "headers": ["AI Model", "Topic", "File", "Date Added"],
        "source_keys": ["model", "ai", "assistant", "source", "llm"],
        "topic_keys": ["topic", "subject", "discussion", "title"],
        "date_keys": ["date added", "date", "date analyzed"],
    },
}


def find_project_root() -> Path:
    """Find the project root by looking for .git or CLAUDE.md"""
    current = Path(__file__).resolve().parent

    # Walk up directory tree
    for _ in range(10):  # Max 10 levels up
        if (current / ".git").exists() or (current / "CLAUDE.md").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    # Fallback: assume script is in scripts/ under project root
    return Path(__file__).resolve().parent.parent


def parse_frontmatter(file_path: Path, verbose: bool = False) -> dict[str, str]:
    """
    Parse **Key:** Value or **Key**: Value frontmatter from a markdown file.
    Returns dict of key -> value pairs (keys lowercased for consistency).
    """
    frontmatter = {}

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        if verbose:
            print(f"  Warning: Could not read {file_path}: {e}")
        return frontmatter

    # Only look at the first 50 lines for frontmatter
    lines = content.split("\n")[:50]

    for line in lines:
        # Try each pattern
        for pattern in FRONTMATTER_PATTERNS:
            match = pattern.search(line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                frontmatter[key.lower()] = value
                if verbose:
                    print(f"    Found: {key} = {value}")
                break  # Don't match same line twice

    # Also try to extract title from first H1
    for line in lines:
        if line.startswith("# "):
            frontmatter["_title"] = line[2:].strip()
            break

    return frontmatter


def extract_field(frontmatter: dict[str, str], keys: list[str], fallback: str = "") -> str:
    """Extract a field from frontmatter, trying multiple possible key names."""
    for key in keys:
        value = frontmatter.get(key.lower())
        if value:
            return value
    return fallback


def extract_topic_from_title(title: str) -> str:
    """Extract a reasonable topic from a title string."""
    original = title

    # Remove common prefixes
    prefixes = [
        "Video Analysis:",
        "Analysis:",
        "Research:",
        "Paper:",
        "Article:",
        "Implementation:",
    ]
    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            break

    # Look for "with X" pattern at the end - often the key topic
    with_match = re.search(r"\bwith\s+(.+)$", title, re.IGNORECASE)
    if with_match:
        potential_topic = with_match.group(1).strip()
        # Only use if it's reasonably short
        if 5 < len(potential_topic) < 40:
            return potential_topic

    # Try to extract key topic from common title patterns
    # Pattern: "Topic - Subtitle" or "Topic: Subtitle"
    separators = [" - ", " | "]
    for sep in separators:
        if sep in title:
            parts = title.split(sep, 1)
            # If first part looks like a vague intro, use second
            vague_prefixes = ["how", "why", "what", "guide to", "introduction to"]
            if any(parts[0].lower().startswith(v) for v in vague_prefixes):
                title = parts[1].strip()
            else:
                # Prefer shorter, more specific part
                title = min(parts, key=lambda p: len(p)).strip()
            break

    # Remove ellipsis-like patterns
    title = re.sub(r"\s*\.\.\.\s*", " ", title).strip()

    # Truncate if still too long, but try to break at word boundary
    if len(title) > 50:
        truncated = title[:47]
        # Try to break at last space
        last_space = truncated.rfind(" ")
        if last_space > 30:
            truncated = truncated[:last_space]
        title = truncated + "..."

    return title


def scan_folder(folder_path: Path, folder_type: str, verbose: bool = False) -> list[dict]:
    """
    Scan a research subfolder and return list of entry dicts.
    Each dict has: source, topic, file_path, date, sort_key
    """
    entries = []
    config = TABLE_CONFIGS.get(folder_type, TABLE_CONFIGS["articles"])

    if not folder_path.exists():
        if verbose:
            print(f"  Folder does not exist: {folder_path}")
        return entries

    for md_file in sorted(folder_path.glob("*.md")):
        if md_file.name.lower() == "readme.md":
            continue

        if verbose:
            print(f"  Scanning: {md_file.name}")

        frontmatter = parse_frontmatter(md_file, verbose)

        # Extract fields using config
        source = extract_field(frontmatter, config["source_keys"])
        topic = extract_field(frontmatter, config["topic_keys"])
        date = extract_field(frontmatter, config["date_keys"])

        # Fallbacks
        if not source:
            source = md_file.stem.replace("-", " ").replace("_", " ").title()
            if verbose:
                print(f"    Warning: No source found, using filename: {source}")

        if not topic:
            title = frontmatter.get("_title", "")
            if title:
                topic = extract_topic_from_title(title)
            else:
                topic = md_file.stem.replace("-", " ").replace("_", " ").title()
            if verbose:
                print(f"    Warning: No topic found, using: {topic}")

        if not date:
            date = "Unknown"
            if verbose:
                print(f"    Warning: No date found for {md_file.name}")

        # Relative path for the link
        rel_path = f"{folder_type}/{md_file.name}"

        entries.append({
            "source": source,
            "topic": topic,
            "file_path": rel_path,
            "file_name": md_file.name,
            "date": date,
            "sort_key": date if date != "Unknown" else "0000-00-00",
        })

    # Sort by date (newest first)
    entries.sort(key=lambda e: e["sort_key"], reverse=True)

    return entries


def generate_table(entries: list[dict], folder_type: str) -> str:
    """Generate a markdown table for the given entries."""
    config = TABLE_CONFIGS.get(folder_type, TABLE_CONFIGS["articles"])
    headers = config["headers"]

    if not entries:
        # Return placeholder row
        lines = [
            f"| {' | '.join(headers)} |",
            f"| {' | '.join(['---' + '-' * (len(h) - 3) for h in headers])} |",
            f"| *Coming soon* | {'| '.join(['' for _ in headers[1:]])}|",
        ]
        return "\n".join(lines)

    # Build header
    lines = [
        f"| {' | '.join(headers)} |",
        f"|{' | '.join(['-' * (len(h) + 2) for h in headers])}|",
    ]

    # Build rows
    for entry in entries:
        if folder_type == "papers":
            # Papers use Title as first column
            row = [
                entry["source"],  # Title for papers
                entry["topic"],
                f"[Analysis]({entry['file_path']})",
                entry["date"],
            ]
        else:
            row = [
                entry["source"],
                entry["topic"],
                f"[Analysis]({entry['file_path']})",
                entry["date"],
            ]
        lines.append(f"| {' | '.join(row)} |")

    return "\n".join(lines)


def update_readme_section(
    readme_content: str,
    folder_type: str,
    new_table: str,
    verbose: bool = False
) -> tuple[str, bool]:
    """
    Update a section of the README between markers.
    Returns (new_content, changed).

    If markers don't exist, we need to inject them around the existing table.
    """
    start_marker = MARKER_START.format(folder=folder_type)
    end_marker = MARKER_END.format(folder=folder_type)

    # Check if markers exist
    if start_marker in readme_content and end_marker in readme_content:
        # Extract everything between markers
        start_idx = readme_content.index(start_marker) + len(start_marker)
        end_idx = readme_content.index(end_marker)

        old_section = readme_content[start_idx:end_idx].strip()

        # Replace section
        new_section = f"\n{new_table}\n"
        new_content = (
            readme_content[:start_idx] +
            new_section +
            readme_content[end_idx:]
        )

        changed = old_section != new_table
        return new_content, changed

    # Markers don't exist - we need to find the section and add markers
    # Look for the section header (e.g., ### Videos)
    section_header = f"### {folder_type.title()}"

    if section_header not in readme_content:
        if verbose:
            print(f"  Warning: Could not find section '{section_header}' in README")
        return readme_content, False

    # Find the section header
    header_idx = readme_content.index(section_header)

    # Find the next section header or end of file
    remaining = readme_content[header_idx + len(section_header):]
    next_section_match = re.search(r"\n###? ", remaining)

    if next_section_match:
        section_end_idx = header_idx + len(section_header) + next_section_match.start()
    else:
        section_end_idx = len(readme_content)

    # Build new section with markers
    new_section = f"""{section_header}

{start_marker}
{new_table}
{end_marker}

"""

    new_content = (
        readme_content[:header_idx] +
        new_section +
        readme_content[section_end_idx:].lstrip()
    )

    return new_content, True


def main():
    parser = argparse.ArgumentParser(
        description="Update research index tables in README.md"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying files"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if changes needed (for CI/pre-commit)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress"
    )
    args = parser.parse_args()

    # Find project root and paths
    project_root = find_project_root()
    research_dir = project_root / "ai_docs" / "research"
    readme_path = research_dir / "README.md"

    if args.verbose:
        print(f"Project root: {project_root}")
        print(f"Research dir: {research_dir}")
        print(f"README path: {readme_path}")

    # Validate paths
    if not research_dir.exists():
        print(f"Error: Research directory not found: {research_dir}")
        sys.exit(1)

    if not readme_path.exists():
        print(f"Error: README.md not found: {readme_path}")
        sys.exit(1)

    # Read current README
    readme_content = readme_path.read_text(encoding="utf-8")
    original_content = readme_content

    any_changes = False

    # Process each subfolder
    for folder_type in SUBFOLDERS:
        folder_path = research_dir / folder_type

        if args.verbose:
            print(f"\nProcessing: {folder_type}/")

        # Scan folder for entries
        entries = scan_folder(folder_path, folder_type, args.verbose)

        if args.verbose:
            print(f"  Found {len(entries)} entries")

        # Generate new table
        new_table = generate_table(entries, folder_type)

        # Update README section
        readme_content, changed = update_readme_section(
            readme_content, folder_type, new_table, args.verbose
        )

        if changed:
            any_changes = True
            if args.verbose:
                print(f"  Changes detected in {folder_type} section")

    # Handle output based on mode
    if args.check:
        if any_changes:
            print("Research index is out of date!")
            print("Run 'python scripts/update-research-index.py' to update it.")
            print("")
            print("Or run with --dry-run to see what would change.")
            sys.exit(1)
        else:
            if args.verbose:
                print("\nResearch index is up to date.")
            sys.exit(0)

    if args.dry_run:
        if any_changes:
            print("Changes would be made to README.md:")
            print("-" * 60)
            # Show a simple diff-like output
            old_lines = original_content.split("\n")
            new_lines = readme_content.split("\n")

            # Find changed sections
            for i, (old, new) in enumerate(zip(old_lines, new_lines)):
                if old != new:
                    print(f"Line {i + 1}:")
                    print(f"  - {old[:80]}")
                    print(f"  + {new[:80]}")

            # Handle different lengths
            if len(new_lines) > len(old_lines):
                print(f"\n{len(new_lines) - len(old_lines)} new lines added")
            elif len(old_lines) > len(new_lines):
                print(f"\n{len(old_lines) - len(new_lines)} lines removed")
        else:
            print("No changes needed - index is up to date.")
        sys.exit(0)

    # Default mode: apply changes
    if any_changes:
        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"Updated: {readme_path}")
    else:
        if args.verbose:
            print("\nNo changes needed.")


if __name__ == "__main__":
    main()
