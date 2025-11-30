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
├── papers/             ← Academic papers (if any)
└── llm-chats/          ← LLM conversation transcripts (Claude, GPT, etc.)
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

<!-- INDEX:videos:start -->
| Source | Topic | File | Date Added |
| ------ | ----- | ---- | ---------- |
| *Coming soon* | | | |
<!-- INDEX:videos:end -->

### Articles

<!-- INDEX:articles:start -->
| Source | Topic | File | Date Added |
| ------ | ----- | ---- | ---------- |
| *Coming soon* | | | |
<!-- INDEX:articles:end -->

### Implementations

<!-- INDEX:implementations:start -->
| Repository | Topic | File | Date Added |
|------------ | ------- | ------ | ------------|
| Mem0 Integration Patterns | Mem0 Integration Patterns for AI Agent Frameworks | [Analysis](implementations/mem0-integration-patterns.md) | November 29, 2025 |
| Mem0 Api Patterns | Mem0 Direct API/SDK Usage Research | [Analysis](implementations/mem0-api-patterns.md) | 2025-11-29 |
| Multi-agent research synthesis | Gemini File Search API for Scout-Plan-Build Framework | [Analysis](implementations/gemini-file-search-integration-research.md) | 2025-11-28 |
| Claude Agent SDK Documentation, GitHub, Context7 | SDK Installation, Configuration, and Custom Agents | [Analysis](implementations/claude-agent-sdk-analysis.md) | 2025-11-24 |
| Analysis compiled by Chad (ChatGPT) | Claude Code Slash Commands + Chaining Patterns | [Analysis](implementations/slash-commands-chaining-chad.md) | 2025-11-22 18:54 |
| Chad (ChatGPT) & Gemini 3.0 | Agent Box v6.2: Supervisor Wrapper... | [Analysis](implementations/agent-box-supervisor-chad.md) | 2025-11-22 |
| Mem0 Comprehensive Guide Full Mem0 Patterns | mem0 Deep Dive Analysis: mem0-comprehensive-gui... | [Analysis](implementations/mem0-comprehensive-guide-full-mem0-patterns.md) | Unknown |
<!-- INDEX:implementations:end -->

### Papers

<!-- INDEX:papers:start -->
| Title | Topic | File | Date Added |
| ----- | ----- | ---- | ---------- |
| *Coming soon* | | | |
<!-- INDEX:papers:end -->

### LLM Chats

Valuable insights from conversations with AI assistants (Claude, ChatGPT, Gemini, etc.).

<!-- INDEX:llm-chats:start -->
| AI Model | Topic | File | Date Added |
| -------- | ----- | ---- | ---------- |
| *Coming soon* | | | |
<!-- INDEX:llm-chats:end -->

## Adding New Research

When adding a new analysis:

1. **Place in appropriate subfolder** (videos/, articles/, etc.)
2. **Name clearly**: `topic-source.md` (e.g., `git-worktree-parallelization-indydevdan.md`)
3. **Include attribution** at the top of the file:
   ```markdown
   # [Title]

   **Source**: [URL or citation]
   **Topic**: [Brief topic description]
   **Author**: [Original creator]
   **Date Analyzed**: YYYY-MM-DD
   **Analyzed By**: [Your name/AI]
   ```
4. **Update this README** index table
5. **Use the slash command**: `/research-add <filepath-or-content>`
   - Accepts a filepath to existing file OR pasted content
   - Interactive wizard confirms metadata before creating

## Why This Exists

In agentic engineering, AI assistants benefit from curated external knowledge:

- Patterns from successful implementations
- Best practices from industry experts
- Academic foundations for complex features

This research library gives Claude context for informed recommendations.
