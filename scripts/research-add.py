#!/usr/bin/env python3
"""
Research Document Manager - Add, analyze, and validate research documents.

This script provides deterministic operations for managing research documents:
- Extract metadata from markdown files
- Create research documents in the correct subfolder
- Update the research index (README.md)
- Validate index consistency
- Extract URLs to markdown via Gemini 3
- Synthesize structured analyses from raw content

Usage:
    python scripts/research-add.py analyze <file>       # Analyze file metadata
    python scripts/research-add.py analyze -            # Analyze from stdin
    python scripts/research-add.py create '<json>'      # Create from JSON metadata
    python scripts/research-add.py validate             # Validate index consistency
    python scripts/research-add.py add-url <url>        # Extract URL to markdown
    python scripts/research-add.py synthesize <file>    # Synthesize structured analysis
    python scripts/research-add.py add-url <url> --then synthesize --template <name>
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Lazy imports for optional dependencies
_gemini_client = None


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

# Source folders (raw inputs go here)
SOURCE_FOLDERS = {
    "video": "sources/videos",
    "paper": "sources/papers",
    "llm-chat": "sources/llm-chats",
    "article": "sources/articles",  # default for raw
}

# Synthesis output folder (processed outputs)
SYNTHESIS_FOLDER = "implementations"

# Legacy mapping for backwards compatibility
TYPE_FOLDERS = {
    "video": "sources/videos",
    "implementation": "implementations",  # Synthesis stays at root
    "paper": "sources/papers",
    "llm-chat": "sources/llm-chats",
    "article": "sources/articles",
}

# Synthesis templates (deterministic, predefined structures)
SYNTHESIS_TEMPLATES = {
    "mem0-deep-dive": {
        "name": "mem0 Deep Dive Analysis",
        "output_suffix": "mem0-patterns",
        "sections": [
            ("conceptual", "Conceptual Model & Role in Stack", "brief",
             "Extract the core mental model: what is mem0, where does it fit in the AI stack, "
             "how does it relate to other components (LLMs, vector DBs, agents)."),
            ("metadata", "Metadata & Schema Patterns", "deep",
             "Extract metadata schema patterns including: field types, multi-tenant patterns, "
             "multi-agent patterns, indexing strategies, and schema evolution."),
            ("lifecycle", "Memory Lifecycle & Policies", "deep",
             "Extract memory lifecycle details: creation, updates, decay/expiration, "
             "consolidation, archival, and deletion patterns."),
            ("retrieval", "Retrieval & Filtering Strategies", "deep",
             "Extract retrieval patterns: search methods, filtering syntax, ranking, "
             "relevance scoring, and query optimization."),
            ("types", "Memory Types & Usage Patterns", "deep",
             "Extract memory type taxonomy: what types exist, when to use each, "
             "recommended patterns, and type-specific configurations."),
            ("integration", "API & Integration Patterns", "deep",
             "Extract integration patterns: API usage, SDK patterns, framework integration, "
             "agent integration, MCP patterns if mentioned."),
            ("operations", "Operational Considerations", "brief",
             "Extract operational aspects: hosted vs self-hosted, scaling, monitoring, "
             "cost considerations, and deployment patterns."),
            ("pitfalls", "Pitfalls & Anti-patterns", "brief",
             "Extract common mistakes, anti-patterns, things to avoid, and lessons learned."),
        ]
    },
    "general": {
        "name": "General Analysis",
        "output_suffix": "analysis",
        "sections": [
            ("summary", "Executive Summary", "brief",
             "Provide a concise summary of the document's main points."),
            ("concepts", "Key Concepts", "deep",
             "Extract and explain the main concepts, terms, and ideas."),
            ("patterns", "Patterns & Best Practices", "deep",
             "Extract recommended patterns, practices, and approaches."),
            ("examples", "Examples & Use Cases", "deep",
             "Extract concrete examples, code snippets, and use cases."),
            ("pitfalls", "Pitfalls & Warnings", "brief",
             "Extract warnings, common mistakes, and things to avoid."),
        ]
    },
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


# =============================================================================
# GEMINI CLIENT & URL EXTRACTION
# =============================================================================

def get_gemini_client():
    """Get or create Gemini client (lazy initialization)."""
    global _gemini_client

    if _gemini_client is not None:
        return _gemini_client

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Get one from: https://aistudio.google.com/app/apikey"
        )

    try:
        from google import genai
        _gemini_client = genai.Client(api_key=api_key)
        return _gemini_client
    except ImportError:
        raise RuntimeError(
            "google-genai package not installed. Run: pip install google-genai"
        )


# Patterns for detecting LLM-ready sources
LLM_SOURCE_PATTERNS = [
    # Gist URLs with LLM-related keywords
    (r'https?://gist\.githubusercontent\.com/[^"\s]+(?:llm|context|raw)[^"\s]*', "gist"),
    (r'https?://gist\.github\.com/[^"\s]+', "gist"),
    # Raw markdown/text links
    (r'https?://[^"\s]+\.(?:md|txt|markdown)["\s]', "raw"),
    # llms.txt convention
    (r'https?://[^"\s]+/llms\.txt', "llms.txt"),
]


def detect_llm_ready_source(html_content: str, original_url: str) -> Optional[Dict[str, str]]:
    """
    Scan HTML for LLM-ready source links (gists, raw markdown, llms.txt).

    Returns:
        Dict with 'url', 'type', 'description' if found, None otherwise
    """
    import requests

    # Look for gist links with LLM-related context
    gist_pattern = r'href=["\']?(https?://gist\.(?:githubusercontent\.com|github\.com)/[^"\'\s>]+)["\']?'
    gist_matches = re.findall(gist_pattern, html_content, re.IGNORECASE)

    for gist_url in gist_matches:
        # Check if the surrounding context mentions LLM/context
        # Find the context around the URL
        url_pos = html_content.find(gist_url)
        context_start = max(0, url_pos - 200)
        context_end = min(len(html_content), url_pos + len(gist_url) + 200)
        context = html_content[context_start:context_end].lower()

        llm_keywords = ["llm", "context", "gist for", "easy to copy", "raw", "plain text"]
        if any(kw in context for kw in llm_keywords):
            # Convert gist.github.com to raw URL
            if "gist.github.com" in gist_url and "raw" not in gist_url:
                # Try to fetch and find raw link
                try:
                    gist_resp = requests.get(gist_url, timeout=10, headers={
                        "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
                    })
                    raw_match = re.search(r'href="(/[^"]+/raw/[^"]+)"', gist_resp.text)
                    if raw_match:
                        gist_url = "https://gist.githubusercontent.com" + raw_match.group(1).replace("/raw/", "/raw")
                except:
                    pass

            return {
                "url": gist_url,
                "type": "gist",
                "description": "LLM-ready gist found in article"
            }

    # Look for raw file patterns
    raw_pattern = r'href=["\']?(https?://[^"\'\s>]+\.(?:md|txt))["\']?'
    raw_matches = re.findall(raw_pattern, html_content, re.IGNORECASE)
    for raw_url in raw_matches:
        if "raw" in raw_url.lower() or "plain" in raw_url.lower():
            return {
                "url": raw_url,
                "type": "raw",
                "description": "Raw markdown/text link found"
            }

    return None


def fetch_llm_ready_content(source_url: str) -> str:
    """Fetch content from an LLM-ready source URL."""
    import requests

    response = requests.get(source_url, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
    })
    response.raise_for_status()
    return response.text


def extract_url_to_markdown(
    url: str,
    model: str = "gemini-2.0-flash",
    temperature: float = 0.2,
    auto_source: bool = False,
    no_detect: bool = False,
) -> Dict[str, str]:
    """
    Extract URL content to clean markdown using Gemini.

    Args:
        url: The URL to extract
        model: Gemini model to use (gemini-2.0-flash, gemini-2.5-pro, etc.)
        temperature: Generation temperature (lower = more deterministic)
        auto_source: Automatically use detected LLM-ready sources
        no_detect: Skip LLM-ready source detection

    Returns:
        Dict with 'title', 'content', 'source_url', 'extraction_method'
    """
    import requests

    # Fetch HTML
    print(f"⚙️ Fetching URL: {url}")
    try:
        response = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
        })
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch URL: {e}")

    # Try to detect LLM-ready source
    extraction_method = "gemini"
    if not no_detect:
        llm_source = detect_llm_ready_source(html_content, url)
        if llm_source:
            print(f"\n💡 Found LLM-ready source: {llm_source['type']}")
            print(f"   URL: {llm_source['url'][:80]}...")

            use_source = auto_source
            if not auto_source:
                # Ask user (in interactive mode)
                try:
                    answer = input("   Use this instead of HTML extraction? [Y/n]: ").strip().lower()
                    use_source = answer in ("", "y", "yes")
                except EOFError:
                    # Non-interactive, default to yes
                    use_source = True

            if use_source:
                print(f"⚙️ Fetching LLM-ready content...")
                try:
                    content = fetch_llm_ready_content(llm_source["url"])
                    print(f"✅ Got {len(content):,} chars from {llm_source['type']}")

                    # Extract title - try multiple patterns
                    title = None
                    # Pattern 1: YAML frontmatter title
                    yaml_title = re.search(r"^title:\s*(.+)$", content[:2000], re.MULTILINE)
                    if yaml_title:
                        title = yaml_title.group(1).strip().strip('"\'')
                    # Pattern 2: First H1 heading (but not code comments)
                    if not title:
                        h1_match = re.search(r"^#\s+([^#\n][^\n]+)$", content, re.MULTILINE)
                        if h1_match and not h1_match.group(1).startswith("Example"):
                            title = h1_match.group(1)
                    # Pattern 3: Markdown underline style
                    if not title:
                        underline_match = re.search(r"^(.{10,80})\n[=]+$", content[:2000], re.MULTILINE)
                        if underline_match:
                            title = underline_match.group(1)
                    # Fallback: derive from URL
                    if not title:
                        from urllib.parse import urlparse
                        path = urlparse(url).path
                        title = path.split("/")[-1].replace("-", " ").title() or "Extracted Article"

                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc.replace("www.", "")

                    return {
                        "title": title,
                        "content": content,
                        "source_url": url,
                        "source_domain": domain,
                        "extraction_method": f"direct-{llm_source['type']}",
                        "llm_source_url": llm_source["url"],
                    }
                except Exception as e:
                    print(f"  ⚠️ Failed to fetch LLM source: {e}")
                    print(f"  ⚠️ Falling back to HTML extraction...")

    # Truncate if very large (Gemini handles 1M tokens but be reasonable)
    if len(html_content) > 500000:
        html_content = html_content[:500000]
        print("  ⚠️ Content truncated to 500k chars")

    # Build extraction prompt
    extraction_prompt = """Convert this HTML article to clean, well-formatted Markdown.

INSTRUCTIONS:
1. Extract the COMPLETE article content - do not summarize or shorten
2. Preserve all headings, lists, code blocks, and formatting
3. Remove navigation, ads, comments, and non-article content
4. Keep all code examples with proper syntax highlighting markers
5. Preserve any important metadata (author, date, etc.) at the top
6. Output ONLY the markdown content, no explanations

HTML CONTENT:
"""

    print(f"⚙️ Extracting with {model} (temp={temperature})")
    client = get_gemini_client()

    # Map friendly names to model IDs
    model_map = {
        "flash": "gemini-2.0-flash",
        "pro": "gemini-2.5-pro-preview-05-06",
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-2.5-pro": "gemini-2.5-pro-preview-05-06",
        "gemini-3-pro": "gemini-2.5-pro-preview-05-06",  # Alias until 3.0 API available
    }
    model_id = model_map.get(model, model)

    response = client.models.generate_content(
        model=model_id,
        contents=extraction_prompt + html_content,
        config={
            "temperature": temperature,
            "max_output_tokens": 65536,  # Large output for full article
        }
    )

    markdown_content = response.text

    # Extract title from first H1
    title_match = re.search(r"^#\s+(.+)$", markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Extracted Article"

    # Extract domain for source
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.replace("www.", "")

    return {
        "title": title,
        "content": markdown_content,
        "source_url": url,
        "source_domain": domain,
        "extraction_method": "gemini",
    }


def cmd_add_url(args) -> dict:
    """Extract URL to markdown and save to sources/articles/."""
    try:
        url = args.url
        model = getattr(args, "model", "pro")
        temp = getattr(args, "temp", 0.2)
        auto_source = getattr(args, "auto_source", False)
        no_detect = getattr(args, "no_detect", False)

        # Extract content
        result = extract_url_to_markdown(
            url,
            model=model,
            temperature=temp,
            auto_source=auto_source,
            no_detect=no_detect
        )

        # Generate filename
        title_slug = slugify(result["title"])[:40]
        domain_slug = slugify(result["source_domain"])[:15]
        filename = f"{title_slug}-{domain_slug}.md"

        # Build output path
        project_root = find_project_root()
        output_dir = project_root / "ai_docs" / "research" / "sources" / "articles"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check for custom output path
        if hasattr(args, "output") and args.output:
            output_path = project_root / "ai_docs" / "research" / "sources" / "articles" / args.output
        else:
            output_path = output_dir / filename

        # Check if exists
        if output_path.exists():
            print(f"  ⚠️ File exists: {output_path}")
            # In non-interactive mode, add timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = output_dir / f"{title_slug}-{timestamp}.md"

        # Build frontmatter
        today = datetime.now().strftime("%Y-%m-%d")
        extraction_method = result.get("extraction_method", "gemini")
        llm_source_url = result.get("llm_source_url", "")

        frontmatter = f"""# {result['title']}

**Source**: {result['source_url']}
**Domain**: {result['source_domain']}
**Extracted**: {today}
**Method**: {extraction_method}
"""
        if llm_source_url:
            frontmatter += f"**LLM Source**: {llm_source_url}\n"
        if extraction_method == "gemini":
            frontmatter += f"**Model**: {model}\n"

        frontmatter += "\n---\n\n"

        # Write file
        full_content = frontmatter + result["content"]
        output_path.write_text(full_content, encoding="utf-8")

        print(f"✅ Extracted: {output_path.relative_to(project_root)}")

        output = {
            "success": True,
            "file_created": str(output_path),
            "title": result["title"],
            "source_url": url,
        }

        # Handle --then chaining
        if hasattr(args, "then_command") and args.then_command == "synthesize":
            print(f"\n🔄 Chaining to synthesize...")
            # Create a namespace for synthesize args
            synth_args = argparse.Namespace(
                file=str(output_path),
                template=getattr(args, "synth_template", "general"),
                temp=getattr(args, "synth_temp", 0.3),
                output=getattr(args, "synth_output", None),
            )
            synth_result = cmd_synthesize(synth_args)
            output["synthesis"] = synth_result

        print(json.dumps(output, indent=2))
        return output

    except Exception as e:
        error_output = {"success": False, "error": str(e)}
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


# =============================================================================
# SYNTHESIS COMMAND
# =============================================================================

def synthesize_content(
    content: str,
    template_name: str,
    model: str = "pro",
    temperature: float = 0.3
) -> str:
    """
    Synthesize structured analysis from raw content using a template.

    Args:
        content: Raw markdown content to analyze
        template_name: Name of synthesis template
        model: Gemini model to use
        temperature: Generation temperature

    Returns:
        Synthesized markdown content
    """
    if template_name not in SYNTHESIS_TEMPLATES:
        available = ", ".join(SYNTHESIS_TEMPLATES.keys())
        raise ValueError(f"Unknown template '{template_name}'. Available: {available}")

    template = SYNTHESIS_TEMPLATES[template_name]

    # Build section prompts
    sections_prompt = ""
    for section_id, title, depth, instruction in template["sections"]:
        depth_guidance = "Be thorough and detailed." if depth == "deep" else "Keep it concise (2-4 key points)."
        sections_prompt += f"""
## {title}
{instruction}
{depth_guidance}

"""

    synthesis_prompt = f"""Analyze this document and extract structured insights.

OUTPUT FORMAT:
- Use markdown with the exact section headers shown below
- For "deep" sections: be thorough, include examples and details
- For "brief" sections: be concise, focus on key points only
- Include relevant quotes or code snippets from the source
- If a section has no relevant content in the source, write "Not covered in source."

SECTIONS TO EXTRACT:
{sections_prompt}

SOURCE DOCUMENT:
{content}

Begin your analysis:"""

    print(f"⚙️ Synthesizing with {model} (temp={temperature})")
    client = get_gemini_client()

    model_map = {
        "flash": "gemini-2.0-flash",
        "pro": "gemini-2.5-pro-preview-05-06",
    }
    model_id = model_map.get(model, model)

    response = client.models.generate_content(
        model=model_id,
        contents=synthesis_prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": 32768,
        }
    )

    return response.text


def cmd_synthesize(args) -> dict:
    """Synthesize structured analysis from a raw file."""
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        template_name = getattr(args, "template", "general")
        model = getattr(args, "model", "pro")
        temp = getattr(args, "temp", 0.3)

        # Read source content
        content = file_path.read_text(encoding="utf-8")

        # Synthesize
        synthesis = synthesize_content(
            content=content,
            template_name=template_name,
            model=model,
            temperature=temp,
        )

        # Generate output path
        template = SYNTHESIS_TEMPLATES[template_name]
        source_stem = file_path.stem
        output_filename = f"{source_stem}-{template['output_suffix']}.md"

        project_root = find_project_root()
        output_dir = project_root / "ai_docs" / "research" / SYNTHESIS_FOLDER
        output_dir.mkdir(parents=True, exist_ok=True)

        if hasattr(args, "output") and args.output:
            output_path = output_dir / args.output
        else:
            output_path = output_dir / output_filename

        # Build frontmatter
        today = datetime.now().strftime("%Y-%m-%d")
        frontmatter = f"""# {template['name']}: {source_stem}

**Source File**: {file_path.name}
**Template**: {template_name}
**Synthesized**: {today}
**Model**: {model}

---

"""

        # Write file
        full_content = frontmatter + synthesis
        output_path.write_text(full_content, encoding="utf-8")

        print(f"✅ Synthesized: {output_path.relative_to(project_root)}")

        # Update index
        update_index(project_root)

        output = {
            "success": True,
            "file_created": str(output_path),
            "template": template_name,
            "source_file": str(file_path),
        }

        return output

    except Exception as e:
        error_output = {"success": False, "error": str(e)}
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


def cmd_templates() -> None:
    """List available synthesis templates."""
    print("Available Synthesis Templates:\n")
    for name, template in SYNTHESIS_TEMPLATES.items():
        print(f"  {name}")
        print(f"    {template['name']}")
        print(f"    Output suffix: {template['output_suffix']}")
        print(f"    Sections:")
        for section_id, title, depth, _ in template["sections"]:
            marker = "★" if depth == "deep" else "○"
            print(f"      {marker} {title} ({depth})")
        print()


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
    subparsers.add_parser(
        "validate",
        help="Validate index consistency",
        description="Check if research index is up to date. Exit 0 if consistent, 1 if needs update."
    )

    # Add-URL command
    add_url_parser = subparsers.add_parser(
        "add-url",
        help="Extract URL to markdown via Gemini",
        description="Fetch URL content and convert to clean markdown using Gemini 3."
    )
    add_url_parser.add_argument(
        "url",
        help="URL to extract"
    )
    add_url_parser.add_argument(
        "--model", "-m",
        default="pro",
        choices=["flash", "pro"],
        help="Gemini model: flash (fast/cheap) or pro (best quality). Default: pro"
    )
    add_url_parser.add_argument(
        "--temp", "-t",
        type=float,
        default=0.2,
        help="Temperature for extraction (0.0-1.0). Lower = more deterministic. Default: 0.2"
    )
    add_url_parser.add_argument(
        "--output", "-o",
        help="Custom output filename (saved to sources/articles/)"
    )
    # LLM-ready source detection
    add_url_parser.add_argument(
        "--auto-source",
        action="store_true",
        help="Automatically use detected LLM-ready sources (gists, raw markdown) without asking"
    )
    add_url_parser.add_argument(
        "--no-detect",
        action="store_true",
        help="Skip LLM-ready source detection, always use HTML extraction"
    )
    # Chaining options
    add_url_parser.add_argument(
        "--then",
        dest="then_command",
        choices=["synthesize"],
        help="Chain to another command after extraction"
    )
    add_url_parser.add_argument(
        "--template",
        dest="synth_template",
        default="general",
        help="Template for synthesis (used with --then synthesize). Default: general"
    )
    add_url_parser.add_argument(
        "--synth-temp",
        type=float,
        default=0.3,
        help="Temperature for synthesis. Default: 0.3"
    )

    # Synthesize command
    synthesize_parser = subparsers.add_parser(
        "synthesize",
        help="Synthesize structured analysis from raw file",
        description="Create structured analysis from raw content using predefined templates."
    )
    synthesize_parser.add_argument(
        "file",
        help="Source file to synthesize (typically from sources/)"
    )
    synthesize_parser.add_argument(
        "--template", "-T",
        default="general",
        choices=list(SYNTHESIS_TEMPLATES.keys()),
        help=f"Synthesis template. Available: {', '.join(SYNTHESIS_TEMPLATES.keys())}. Default: general"
    )
    synthesize_parser.add_argument(
        "--model", "-m",
        default="pro",
        choices=["flash", "pro"],
        help="Gemini model. Default: pro"
    )
    synthesize_parser.add_argument(
        "--temp", "-t",
        type=float,
        default=0.3,
        help="Temperature for synthesis. Default: 0.3"
    )
    synthesize_parser.add_argument(
        "--output", "-o",
        help="Custom output filename (saved to implementations/)"
    )

    # Templates command (list available templates)
    subparsers.add_parser(
        "templates",
        help="List available synthesis templates",
        description="Show all available synthesis templates and their sections."
    )

    args = parser.parse_args()

    if args.command == "analyze":
        cmd_analyze(args.file)
    elif args.command == "create":
        cmd_create(args.json)
    elif args.command == "validate":
        cmd_validate()
    elif args.command == "add-url":
        cmd_add_url(args)
    elif args.command == "synthesize":
        cmd_synthesize(args)
    elif args.command == "templates":
        cmd_templates()


if __name__ == "__main__":
    main()
