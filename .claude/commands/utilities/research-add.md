---
description: Add a research document to ai_docs/research library. Accepts filepath or pasted content with metadata extraction.
argument-hint: <filepath.md> OR (paste markdown content)
---

<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Add Research Document (Smart Import)

<!-- scope: ai_docs/research/** -->

Add a new research document to the ai_docs/research library. Accepts either a **filepath** to an existing file OR **pasted content**. Uses interactive confirmation before creating.

## Arguments

`$ARGUMENTS` can be:
- **A filepath**: `/path/to/file.md`, `./file.md`, `~/file.md`, or any path ending in `.md`
- **Pasted content**: Multi-line markdown content to be saved as a new research doc

## Workflow

### Step 1: Detect Input Type

Check `$ARGUMENTS`:
- If starts with `/`, `./`, `~/`, or ends with `.md` → **Read as filepath**
- If contains markdown headers (`#`) or is multi-line → **Treat as pasted content**
- If ambiguous → Ask user to clarify

### Step 2: Analyze Content

Extract metadata from the content:
- **Title**: From first `# ` heading
- **Source**: From `**Source**:` field, or first URL found, or filename
- **Topic**: From `**Topic**:` field, or derive from title
- **Author**: From `**Author**:` field, or infer from source
- **Type hint**:
  - YouTube/Vimeo URL → `video`
  - GitHub/GitLab URL → `implementation`
  - DOI/arXiv → `paper`
  - Otherwise → `article` (default)

### Step 3: Interactive Confirmation

**Try AskUserQuestion first**, but if it returns instantly without user interaction (known bug with permission bypass modes), **fall back to plain text confirmation**:

#### Option A: AskUserQuestion Tool (if working)
Use the AskUserQuestion tool to confirm metadata with pre-filled options.

#### Option B: Plain Text Fallback (if AskUserQuestion fails)
If AskUserQuestion returns empty or instant response, ask in plain text:

```
Please confirm the following metadata (reply with changes or "OK"):

| Field    | Extracted Value           |
|----------|---------------------------|
| Type     | [detected type]           |
| Topic    | [extracted topic]         |
| Source   | [extracted source]        |
| Author   | [extracted author]        |
```

Wait for user response before proceeding.

**Note**: AskUserQuestion may auto-skip if `--dangerously-skip-permissions` or similar bypass mode is enabled. See: ai_docs/feedback/corrections/askuserquestion-bypass-bug.json

### Step 4: Create the File

1. **Determine subfolder** based on confirmed type:
   - video → `ai_docs/research/videos/`
   - article → `ai_docs/research/articles/`
   - implementation → `ai_docs/research/implementations/`
   - paper → `ai_docs/research/papers/`

2. **Generate filename**: `topic-source.md`
   - Lowercase, hyphenated, URL-safe
   - Example: `agent-box-supervisor-chad.md`

3. **Create file with frontmatter**:
```markdown
# [Title from content]

**Source**: [Confirmed source]
**Topic**: [Confirmed topic]
**Author**: [Confirmed author]
**Date Analyzed**: [Today's date: YYYY-MM-DD]
**Analyzed By**: Claude

---

[Original content here]
```

### Step 5: Update Index

1. Open `ai_docs/research/README.md`
2. Find the appropriate section based on type
3. Add entry between marker comments:
   - `<!-- INDEX:type:start -->` and `<!-- INDEX:type:end -->`
4. Entry format: `| Source | Topic | [Analysis](subfolder/filename.md) | YYYY-MM-DD |`

### Step 6: Validate

Run: `python scripts/update-research-index.py --check`
- If passes → Report success
- If fails → Run without `--check` to auto-fix, then report

## Example Usage

### Example 1: Filepath Input
```
User: /research-add ./my-notes/agent-box-spec.md

Claude: [Reads file, extracts metadata]
Claude: [Shows AskUserQuestion with pre-filled options]
User: [Confirms or modifies via interactive UI]
Claude: [Creates file, updates index]
```

### Example 2: Pasted Content
```
User: /research-add
# My Research Title

**Source**: https://example.com/article
**Author**: Jane Doe

Content here...

Claude: [Parses pasted content, extracts metadata]
Claude: [Shows AskUserQuestion with pre-filled options]
User: [Confirms or modifies via interactive UI]
Claude: [Creates file, updates index]
```

### Example 3: Just Content (No Frontmatter)
```
User: /research-add
# Interesting Patterns in Agentic Systems

This article discusses...

Claude: [Extracts title as topic, prompts for source/author]
Claude: [Shows AskUserQuestion - source/author will need user input]
User: [Provides missing info via "Other" option]
Claude: [Creates file with complete frontmatter, updates index]
```

## Frontmatter Template

```markdown
# [Title]

**Source**: [URL or citation]
**Topic**: [Brief topic description - used for index]
**Author**: [Original creator]
**Date Analyzed**: [YYYY-MM-DD]
**Analyzed By**: [Claude or Human name]

---

[Content]
```

## Important Notes

- **Always use AskUserQuestion** to confirm before creating files
- **Never skip the interactive step** - user must approve metadata
- **Topic field is required** - the index script uses it for the table
- **Validate after creation** - run the check script to ensure consistency
- If filepath doesn't exist, report error and ask for correct path
