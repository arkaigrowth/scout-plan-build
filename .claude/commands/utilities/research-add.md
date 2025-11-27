---
description: Add a research document to ai_docs/research library. Accepts filepath or pasted content with metadata extraction.
argument-hint: <filepath.md> OR (paste markdown content)
allowed-tools: Bash(python scripts/research-add.py:*), AskUserQuestion
---

# Research Add - EXECUTE IMMEDIATELY

## Step 1: Run Analysis Script NOW

```bash
python scripts/research-add.py analyze "$ARGUMENTS"
```

If `$ARGUMENTS` is multi-line (not a filepath), first save to temp file:
```bash
echo '$ARGUMENTS' > /tmp/research_content.md && python scripts/research-add.py analyze /tmp/research_content.md
```

**Show the full JSON output to the user before proceeding.**

## Step 2: Confirm Metadata with User

After showing JSON, use AskUserQuestion with these options:
- **Type**: video / article / implementation / paper / llm-chat
- **Topic**: [extracted value] or custom
- **Source**: [extracted value] or custom
- **Author**: [extracted value] or custom

## Step 3: Create File with Confirmed Metadata

```bash
python scripts/research-add.py create '{"metadata":{"title":"...","source":"...","topic":"...","author":"...","type":"..."},"content":"..."}'
```

## Step 4: Report Success

Show the created file path from the JSON output.

---

**Determinism Pattern**: This command uses Pattern C (Bash Wrapper) - the script handles all logic deterministically. Claude only runs the script and mediates user interaction.
