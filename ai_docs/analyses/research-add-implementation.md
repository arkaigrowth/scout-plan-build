# research-add.py Implementation Analysis

**Created**: 2025-11-26
**File**: `/scripts/research-add.py`
**Lines**: 447
**Purpose**: Deterministic Python script for managing research documents

## Architecture Overview

```
research-add.py
│
├── CLI Commands (argparse)
│   ├── analyze <file|->    → Extract metadata as JSON
│   ├── create '<json>'      → Create file + update index
│   └── validate             → Check index consistency
│
├── Metadata Extraction
│   ├── parse_frontmatter()  → Extract **Key**: Value pairs
│   ├── detect_type()        → Auto-detect document type
│   ├── extract_metadata()   → Combine all metadata
│   └── derive_topic()       → Smart topic extraction
│
├── File Operations
│   ├── generate_filename()  → Slugified naming
│   ├── create_file()        → Add frontmatter template
│   └── update_index()       → Call update-research-index.py
│
└── Type Detection (5 types)
    ├── video            → videos/
    ├── implementation   → implementations/
    ├── paper            → papers/
    ├── llm-chat         → llm-chats/
    └── article          → articles/ (default)
```

## Type Detection Patterns

### Video
```python
Triggers: youtube.com, youtu.be, vimeo.com, video:, **source**: ...video
Output: ai_docs/research/videos/
```

### Implementation
```python
Triggers: github.com, gitlab.com, bitbucket.org, repository:, **repository**:
Output: ai_docs/research/implementations/
```

### Paper
```python
Triggers: doi.org, arxiv.org, acm.org, ieee.org, paper:, **paper**:
Output: ai_docs/research/papers/
```

### LLM Chat
```python
Triggers: Human:, Assistant:, claude.ai, chatgpt, **model**:
Output: ai_docs/research/llm-chats/
```

### Article (Default)
```python
Fallback: Any content not matching above patterns
Output: ai_docs/research/articles/
```

## Metadata Extraction Logic

1. **Title**: First `# ` heading
2. **Source**:
   - `**Source**:` field
   - First URL found in content
   - Fallback: "Unknown"
3. **Topic**:
   - `**Topic**:` field
   - Smart derivation from title:
     - Remove prefixes: "Video Analysis:", "Paper:", etc.
     - Extract "with X" patterns
     - Parse "Topic - Subtitle" patterns
     - Truncate intelligently at word boundaries
4. **Author**: `**Author**:` or `**Creator**:` field
5. **Type**: Auto-detected via pattern matching

## Filename Generation

**Format**: `{topic-slug}-{source-slug}.md`

**Slugification**:
- Lowercase conversion
- Remove special characters except `-`
- Replace spaces with `-`
- Truncate: topic (30 chars), source (20 chars)

**Examples**:
```
Input:  Topic: "Git Worktree Patterns", Source: "youtube.com"
Output: git-worktree-patterns-youtubecom.md

Input:  Topic: "Server Components Implementation", Source: "github.com/vercel/next.js"
Output: server-components-implementation-githubcomvercel.md
```

## CLI Usage Patterns

### 1. Analyze File
```bash
python scripts/research-add.py analyze path/to/file.md
```

### 2. Analyze from Stdin
```bash
cat content.md | python scripts/research-add.py analyze -
```

### 3. Create Document
```bash
python scripts/research-add.py create '{
  "metadata": {
    "title": "...",
    "source": "...",
    "topic": "...",
    "author": "...",
    "type": "article|video|implementation|paper|llm-chat"
  },
  "content": "..."
}'
```

### 4. Validate Index
```bash
python scripts/research-add.py validate
```

## JSON Output Format

### Success (analyze)
```json
{
  "success": true,
  "metadata": {
    "title": "Document Title",
    "source": "example.com",
    "topic": "Main Topic",
    "author": "Author Name",
    "type": "article",
    "suggested_filename": "main-topic-examplecom.md",
    "suggested_path": "ai_docs/research/articles/main-topic-examplecom.md"
  }
}
```

### Success (create)
```json
{
  "success": true,
  "file_created": "/absolute/path/to/file.md",
  "metadata": { ... }
}
```

### Success (validate)
```json
{
  "success": true,
  "message": "Index is consistent"
}
```

### Error (any command)
```json
{
  "success": false,
  "error": "Error message description"
}
```

## Integration Points

### With update-research-index.py
```python
def update_index(project_root: Path) -> None:
    """Call existing index updater after file creation"""
    script_path = project_root / "scripts" / "update-research-index.py"
    subprocess.run([sys.executable, str(script_path)])
```

### With Slash Command Wrapper
The `/research-add` slash command should:

1. Accept filepath OR pasted content
2. Call `analyze` to extract metadata
3. Display metadata to user
4. Ask for confirmation
5. Call `create` with confirmed metadata
6. Display success message with file path

## Frontmatter Template

Generated frontmatter structure:
```markdown
# {title}

**Source**: {source}
**Topic**: {topic}
**Author**: {author}
**Date Added**: {YYYY-MM-DD}

---

{content}
```

## Error Handling

All commands use try-except with JSON error output:
```python
try:
    # Operation
    print(json.dumps({"success": True, ...}))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
    sys.exit(1)
```

**Exit Codes**:
- 0 = Success
- 1 = Error or validation failure

## Testing Results

All type detections verified:
```bash
✓ Video detection      → videos/
✓ Paper detection      → papers/
✓ Implementation       → implementations/
✓ LLM chat detection   → llm-chats/
✓ Article fallback     → articles/
✓ File creation        → Frontmatter + content
✓ Index update         → Automatic
✓ Validation check     → Exit codes correct
```

## Design Decisions

### Why Subcommands vs Flags?
- **Clarity**: Each operation is distinct
- **Composability**: Can pipe between commands
- **Safety**: Explicit intent required

### Why JSON Output?
- **Deterministic**: Machine-readable
- **Composable**: Can pipe to jq, other tools
- **Consistent**: Same format for all commands

### Why Separate create Step?
- **Confirmation**: User can review metadata first
- **Flexibility**: Metadata can be edited before creation
- **Safety**: No accidental file creation

### Why Call update-research-index.py?
- **DRY**: Reuse existing index logic
- **Consistency**: Same index format
- **Maintainability**: Single source of truth

## Future Enhancements

Possible improvements (not implemented):
1. Interactive mode with prompts
2. Bulk import from directory
3. Metadata validation rules
4. Duplicate detection
5. Category/tag support
6. Full-text search integration

## Code Quality

- **Lines**: 447 (comprehensive but focused)
- **Functions**: 15 (well-separated concerns)
- **Comments**: Extensive docstrings
- **Error handling**: JSON-formatted, never crashes
- **Dependencies**: stdlib only (argparse, json, re, subprocess, pathlib)
- **Compatibility**: Python 3.9+

## Usage Examples in Practice

### Adding a YouTube Video
```bash
# Step 1: Analyze
echo '# Git Worktree Tutorial
**Source**: https://youtube.com/watch?v=abc
**Topic**: Git Worktrees
**Author**: DevChannel' | python scripts/research-add.py analyze -

# Step 2: Review output, then create
python scripts/research-add.py create '{"metadata": {...}}'
```

### Adding GitHub Repository Study
```bash
python scripts/research-add.py create '{
  "metadata": {
    "title": "Next.js App Router",
    "source": "github.com/vercel/next.js",
    "topic": "Server Components",
    "author": "Vercel",
    "type": "implementation"
  },
  "content": "\n\n## Analysis\n\n..."
}'
```

### Validating Before Commit
```bash
# In pre-commit hook
python scripts/research-add.py validate || exit 1
```

## Conclusion

The `research-add.py` script provides a robust, deterministic interface for managing research documents with:

- **5 document types** with auto-detection
- **3 CLI commands** for all operations
- **JSON output** for composability
- **Zero manual index updates** required
- **Extensible architecture** for future enhancements

Total implementation: **~450 lines** of well-tested Python.
