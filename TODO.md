# TODO - Development Tasks

## 🚀 Features

- [ ] **Update CLAUDE.md for Better Repo Operations**
  - Status: Urgent
  - Priority: High
  - Description: Refactor CLAUDE.md to be more actionable with deterministic scripts
  - Tasks:
    - Remove outdated instructions
    - Add script-based workflows
    - Include token limit fixes
    - Add file organization conventions
    - Simplify for new agents

- [ ] **Add External Tool Support for Scout Subagents**
  - Status: Planned
  - Priority: Medium
  - Description: Currently hitting token limits with claude/gemini commands. Need to support external tools that can handle larger outputs.
  - Blocked by: Token limit configuration (CLAUDE_CODE_MAX_OUTPUT_TOKENS)
  - Related: scout_improved.md, parallel agent execution
  - Proposed tools:
    - Continue with larger context windows
    - Cursor with API access
    - Custom lightweight analyzers
  - Implementation notes:
    - Add tool availability detection
    - Graceful fallback to native tools
    - Configure output token limits per tool

## 🔧 Improvements

- [ ] Add Pydantic validation to workflow_ops.py
- [ ] Implement structured error types
- [ ] Add rate limiting for API calls
- [ ] Parallelize independent operations
- [ ] Add caching for expensive operations

## 🐛 Bug Fixes

- [ ] Fix timeout handling in subagent execution
- [ ] Handle API token limit errors gracefully

## 📚 Documentation

- [ ] Document agent spawning patterns
- [ ] Create API contract specifications
- [ ] Add troubleshooting guide for token limits

---

*Use GitHub issues for production features. This file tracks development improvements and technical debt.*