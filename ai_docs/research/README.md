# AI Research Library

External resources analyzed to inform framework development decisions.

## Purpose

This directory contains **analyses of external content** — videos, articles, reference implementations, and papers that provide learning and inspiration for the Scout-Plan-Build framework.

> **Important**: These are analyses/summaries of external sources, not original work.
> Original creators retain all rights to their content.

## Directory Structure

```
research/
├── README.md           ← This file (index + attribution)
├── videos/             ← Video transcript analyses
├── articles/           ← Article summaries and notes
├── implementations/    ← Notes on reference codebases/repos
└── papers/             ← Academic papers (if any)
```

## Semantic Clarification

| Folder                 | Contains            | Purpose                           |
| ---------------------- | ------------------- | --------------------------------- |
| `ai_docs/reference/` | Internal quick refs | Generated docs about THIS project |
| `ai_docs/research/`  | External analyses   | Learning from EXTERNAL sources    |

**Research = INPUT** (external knowledge coming in)
**Reference = OUTPUT** (internal knowledge distilled out)

## Index

### Videos

| Source               | Topic                                        | File                                                            | Date Added |
| -------------------- | -------------------------------------------- | --------------------------------------------------------------- | ---------- |
| IndyDevDan (YouTube) | Git Worktree Parallelization for Claude Code | [Analysis](videos/idd-video-git-worktrees-f8RnRuaxee8-analysis.md) | 2024-11-21 |

### Articles

| Source          | Topic | File | Date Added |
| --------------- | ----- | ---- | ---------- |
| *Coming soon* |       |      |            |

### Implementations

| Repository | Topic | File | Date Added |
|------------|-------|------|------------|
| Chad/Claude Code | Claude Code Slash Commands + Chaining | [Analysis](implementations/slash-commands-chaining-chad.md) | 2025-11-22 |

### Papers

| Title           | Topic | File | Date Added |
| --------------- | ----- | ---- | ---------- |
| *Coming soon* |       |      |            |

## Adding New Research

When adding a new analysis:

1. **Place in appropriate subfolder** (videos/, articles/, etc.)
2. **Name clearly**: `topic-source.md` (e.g., `git-worktree-parallelization-indydevdan.md`)
3. **Include attribution** at the top of the file:
   ```markdown
   # [Topic]

   **Source**: [URL or citation]
   **Author**: [Original creator]
   **Date Analyzed**: YYYY-MM-DD
   **Analyzed By**: [Your name/AI]
   ```
4. **Update this README** index table

## Why This Exists

In agentic engineering, AI assistants benefit from curated external knowledge:

- Patterns from successful implementations
- Best practices from industry experts
- Academic foundations for complex features

This research library gives Claude context for informed recommendations.
