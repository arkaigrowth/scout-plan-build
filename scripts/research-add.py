#!/usr/bin/env python3
"""
Research Document Manager - Add, analyze, and validate research documents.

This script provides deterministic operations for managing research documents:
- Extract metadata from markdown files
- Create research documents in the correct subfolder
- Update the research index (README.md)
- Validate index consistency

Usage:
    python scripts/research-add.py --analyze <file>    # Analyze file metadata
    python scripts/research-add.py --analyze -          # Analyze from stdin
    python scripts/research-add.py --create '<json>'    # Create from JSON metadata
    python scripts/research-add.py --validate           # Validate index consistency
    python scripts/research-add.py --help               # Show this help
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Type detection patterns
TYPE_PATTERNS = {
    "video": [
        r"youtube\.com", r"youtu\.be", r"vimeo\.com", r"dailymotion\.com",
        r"video:", r"\*\*source\*\*:.*video"
    ],
    "implementation": [
        r"github\.com", r"gitlab\.com", r"bitbucket\.org",
        r"repository:", r"\*\*repository\*\*:"
    ],
    "paper": [
        r"doi\.org", r"arxiv\.org", r"acm\.org", r"ieee\.org",
        r"paper:", r"\*\*paper\*\*:", r"proceedings of"
    ],
    "llm-chat": [
        r"^Human:", r"^Assistant:", r"claude\.ai", r"chat\.openai\.com",
        r"chatgpt", r"\*\*model\*\*:", r"\*\*ai\*\*:"
    ],
}

# Frontmatter regex - handles both **Key:** Value AND **Key**: Value formats
FRONTMATTER_PATTERNS = [
    re.compile(r"\*\*([^*:]+):\*\*\s*(.+)"),    # **Key:** Value
    re.compile(r"\*\*([^*]+)\*\*:\s*(.+)"),      # **Key**: Value
]

# Type-specific subfolder mapping
TYPE_FOLDERS = {
    "video": "videos",
    "implementation": "implementations",
    "paper": "papers",
    "llm-chat": "llm-chats",
    "article": "articles",  # default
}


def find_project_root() -> Path:
    """Find the project root by looking for .git or CLAUDE.md"""
    current = Path(__file__).resolve().parent

    for _ in range(10):
        if (current / ".git").exists() or (current / "CLAUDE.md").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    return Path(__file__).resolve().parent.parent


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def extract_first_url(text: str) -> Optional[str]:
    """Extract the first URL from text."""
    url_pattern = r"https?://[^\s\)\]<]+"
    match = re.search(url_pattern, text)
    return match.group(0) if match else None


def detect_type(content: str) -> str:
    """Detect document type based on content patterns."""
    content_lower = content.lower()
    content_sample = content[:2000]  # First 2000 chars for efficiency

    for doc_type, patterns in TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content_sample, re.MULTILINE | re.IGNORECASE):
                return doc_type

    return "article"  # default


def parse_frontmatter(content: str) -> dict:
    """Parse **Key:** Value or **Key**: Value frontmatter from markdown content."""
    frontmatter = {}
    lines = content.split("\n")[:50]  # Only first 50 lines

    for line in lines:
        for pattern in FRONTMATTER_PATTERNS:
            match = pattern.search(line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                frontmatter[key.lower()] = value
                break

    # Extract title from first H1
    for line in lines:
        if line.startswith("# "):
            frontmatter["_title"] = line[2:].strip()
            break

    return frontmatter


def extract_metadata(content: str) -> dict:
    """
    Extract metadata from markdown content.
    Returns dict with title, source, topic, author, type.
    """
    frontmatter = parse_frontmatter(content)

    # Extract title (first # heading)
    title = frontmatter.get("_title", "")
    if not title:
        title = "Untitled Document"

    # Extract source (prefer explicit, fallback to first URL)
    source = frontmatter.get("source", "")
    if not source:
        url = extract_first_url(content[:1000])
        if url:
            # Clean up URL for source display
            source = re.sub(r"https?://(www\.)?", "", url)
            source = re.sub(r"/.*$", "", source)  # Remove path
        else:
            source = "Unknown"

    # Extract topic (prefer explicit, fallback to derived from title)
    topic = frontmatter.get("topic", "")
    if not topic:
        topic = derive_topic_from_title(title)

    # Extract author
    author = frontmatter.get("author", "")
    if not author:
        author = frontmatter.get("creator", "")

    # Detect type
    doc_type = detect_type(content)

    return {
        "title": title,
        "source": source,
        "topic": topic,
        "author": author,
        "type": doc_type,
    }


def derive_topic_from_title(title: str) -> str:
    """Derive a reasonable topic from a title string."""
    original = title

    # Remove common prefixes
    prefixes = [
        "Video Analysis:", "Analysis:", "Research:", "Paper:",
        "Article:", "Implementation:", "Chat:", "Conversation:"
    ]
    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            break

    # Look for "with X" pattern at the end
    with_match = re.search(r"\bwith\s+(.+)$", title, re.IGNORECASE)
    if with_match:
        potential_topic = with_match.group(1).strip()
        if 5 < len(potential_topic) < 40:
            return potential_topic

    # Pattern: "Topic - Subtitle" or "Topic: Subtitle"
    separators = [" - ", " | ", ": "]
    for sep in separators:
        if sep in title:
            parts = title.split(sep, 1)
            vague_prefixes = ["how", "why", "what", "guide to", "introduction to"]
            if any(parts[0].lower().startswith(v) for v in vague_prefixes):
                title = parts[1].strip()
            else:
                title = min(parts, key=lambda p: len(p)).strip()
            break

    # Truncate if too long
    if len(title) > 50:
        truncated = title[:47]
        last_space = truncated.rfind(" ")
        if last_space > 30:
            truncated = truncated[:last_space]
        title = truncated + "..."

    return title


def generate_filename(metadata: dict) -> str:
    """Generate a filename from metadata: {topic}-{source}.md"""
    topic_slug = slugify(metadata["topic"])[:30]
    source_slug = slugify(metadata["source"])[:20]

    # Combine, ensuring unique and readable
    filename = f"{topic_slug}-{source_slug}.md"
    return filename


def generate_suggested_path(metadata: dict) -> str:
    """Generate the suggested file path based on type."""
    folder = TYPE_FOLDERS.get(metadata["type"], "articles")
    filename = generate_filename(metadata)
    return f"ai_docs/research/{folder}/{filename}"


def create_file_with_frontmatter(filepath: Path, metadata: dict, content: str) -> None:
    """Create a research file with proper frontmatter."""
    # Generate frontmatter template
    today = datetime.now().strftime("%Y-%m-%d")

    frontmatter_lines = [
        f"# {metadata['title']}",
        "",
        f"**Source**: {metadata['source']}",
        f"**Topic**: {metadata['topic']}",
    ]

    if metadata.get("author"):
        frontmatter_lines.append(f"**Author**: {metadata['author']}")

    frontmatter_lines.extend([
        f"**Date Added**: {today}",
        "",
        "---",
        "",
    ])

    # Combine frontmatter with content (skip duplicate title if present)
    content_lines = content.split("\n")
    if content_lines[0].startswith("# "):
        content_lines = content_lines[1:]  # Skip duplicate title

    full_content = "\n".join(frontmatter_lines) + "\n".join(content_lines)

    # Write file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(full_content, encoding="utf-8")


def update_index(project_root: Path) -> None:
    """Update the research index using update-research-index.py script."""
    script_path = project_root / "scripts" / "update-research-index.py"

    if not script_path.exists():
        raise FileNotFoundError(f"Index updater not found: {script_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Index update failed: {result.stderr}")


def validate_index(project_root: Path) -> dict:
    """Validate index consistency using --check flag."""
    script_path = project_root / "scripts" / "update-research-index.py"

    if not script_path.exists():
        return {
            "success": False,
            "error": f"Index validator not found: {script_path}"
        }

    result = subprocess.run(
        [sys.executable, str(script_path), "--check"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return {"success": True, "message": "Index is consistent"}
    else:
        return {
            "success": False,
            "error": "Index is out of date",
            "details": result.stdout
        }


def cmd_analyze(file_path: str) -> None:
    """Analyze a file and output JSON metadata."""
    try:
        if file_path == "-":
            content = sys.stdin.read()
        else:
            path = Path(file_path)
            if not path.exists():
                print(json.dumps({"success": False, "error": f"File not found: {file_path}"}))
                sys.exit(1)
            content = path.read_text(encoding="utf-8")

        metadata = extract_metadata(content)
        metadata["suggested_filename"] = generate_filename(metadata)
        metadata["suggested_path"] = generate_suggested_path(metadata)

        output = {
            "success": True,
            "metadata": metadata
        }

        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


def cmd_create(json_str: str) -> None:
    """Create a research document from JSON metadata."""
    try:
        data = json.loads(json_str)

        if "metadata" not in data:
            raise ValueError("JSON must contain 'metadata' key")

        metadata = data["metadata"]
        content = data.get("content", "")

        # Support content_file as alternative to inline content
        if not content and "content_file" in data:
            content_path = Path(data["content_file"])
            if content_path.exists():
                content = content_path.read_text(encoding="utf-8")
            else:
                raise ValueError(f"content_file not found: {content_path}")

        # Validate required fields
        required = ["title", "source", "topic", "type"]
        missing = [f for f in required if not metadata.get(f)]
        if missing:
            raise ValueError(f"Missing required metadata fields: {missing}")

        # Generate path
        project_root = find_project_root()
        suggested_path = generate_suggested_path(metadata)
        filepath = project_root / suggested_path

        # Create file
        create_file_with_frontmatter(filepath, metadata, content)

        # Update index
        update_index(project_root)

        output = {
            "success": True,
            "file_created": str(filepath),
            "metadata": metadata
        }

        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


def cmd_validate() -> None:
    """Validate index consistency."""
    try:
        project_root = find_project_root()
        result = validate_index(project_root)
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Research document manager - add, analyze, validate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a file and extract metadata as JSON",
        description="Extract metadata from a markdown file or stdin. Returns JSON with type detection."
    )
    analyze_parser.add_argument(
        "file",
        help="File path to analyze (use '-' for stdin)"
    )

    # Create command
    create_parser = subparsers.add_parser(
        "create",
        help="Create research document from JSON metadata",
        description="Create a research document with frontmatter and update the index."
    )
    create_parser.add_argument(
        "json",
        help="JSON string with 'metadata' (title, source, topic, author, type) and optional 'content'"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate index consistency",
        description="Check if research index is up to date. Exit 0 if consistent, 1 if needs update."
    )

    args = parser.parse_args()

    if args.command == "analyze":
        cmd_analyze(args.file)
    elif args.command == "create":
        cmd_create(args.json)
    elif args.command == "validate":
        cmd_validate()


if __name__ == "__main__":
    main()
