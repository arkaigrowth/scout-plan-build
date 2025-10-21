# Feature: External Tool Support for Scout Subagents

## Metadata
issue_number: `001`
adw_id: `ext001`
issue_json: `{"title": "Add support for external tools in scout subagents", "body": "Currently hitting 8192 token limits with claude/gemini. Need to support tools like Continue, Cursor API, or custom analyzers. Should detect tool availability and gracefully fall back to native tools when unavailable."}`

## Feature Description
This feature extends the scout subagent system to support external tools beyond the current claude/gemini CLI tools, addressing the critical token limit issue (8192 tokens) that causes analysis failures on large codebases. The system will intelligently detect available tools, configure appropriate token limits, and gracefully fall back to native Claude Code tools when external tools are unavailable. This enables comprehensive repository analysis without hitting token constraints, making the scout phase more robust and scalable.

## User Story
As a developer using the scout-plan-build workflow
I want to analyze large codebases without hitting token limits
So that I can get comprehensive analysis results regardless of repository size

## Problem Statement
Current scout subagents using claude-g and gemini-g CLI tools fail when their responses exceed 8192 tokens, causing incomplete analysis and forcing manual fallbacks to native tools. This limitation severely impacts the ability to analyze large repositories, complex architectures, or detailed documentation. The hard-coded tool list in scout_improved.md lacks flexibility to add new tools or configure token limits per tool.

## Solution Statement
Implement a pluggable external tool system that:
1. Maintains a registry of available external tools with their capabilities and limits
2. Dynamically detects which tools are installed/accessible at runtime
3. Configures appropriate token limits per tool (e.g., Continue with 32K, Cursor API with 100K)
4. Provides graceful fallback chains (external → claude/gemini → native tools)
5. Adds new lightweight analyzer tools optimized for specific tasks
6. Preserves the existing parallel execution pattern while adding tool flexibility

## Relevant Files
Use these files to implement the feature:

- `.claude/commands/scout.md` - Original scout command implementation
- `.claude/commands/scout_improved.md` - Current improved version with hard-coded tools - PRIMARY MODIFICATION TARGET
- `adws/adw_modules/agent.py` - Agent execution module, contains prompt_claude_code() and model selection logic
- `adws/adw_modules/utils.py` - Utility functions, good place for tool detection logic
- `TODO.md` - Existing TODO tracking file where this feature is documented

### New Files
- `.claude/commands/scout_external_tools.md` - New version with pluggable tool support
- `adws/adw_modules/external_tools.py` - Tool registry and detection module
- `adws/adw_modules/tool_configs.json` - Configuration file for external tools
- `scripts/install_external_tools.sh` - Helper script to install/configure external tools
- `docs/EXTERNAL_TOOLS.md` - Documentation for adding and configuring external tools

## Implementation Plan
### Phase 1: Foundation
Create the external tool detection and registry system. This includes building the tool detection module, defining the tool interface, and setting up configuration management for tool capabilities and limits.

### Phase 2: Core Implementation
Modify the scout command to use the tool registry instead of hard-coded tools. Implement dynamic tool selection based on availability and task requirements. Add token limit configuration and overflow handling.

### Phase 3: Integration
Integrate with existing parallel execution patterns. Add fallback chains and error recovery. Update documentation and add helper scripts for tool installation.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create External Tools Module
- Create `adws/adw_modules/external_tools.py` with tool registry class
- Define Tool interface with name, command, model, token_limit, timeout properties
- Implement tool detection using `which` command or Python's `shutil.which()`
- Add methods for registering, detecting, and selecting tools
- Include priority ordering for tool selection

### 2. Create Tool Configuration File
- Create `adws/adw_modules/tool_configs.json` with tool definitions
- Define entries for existing tools (claude, gemini, opencode, codex)
- Add entries for new tools (continue, cursor, aider, codeqwen)
- Include token limits, timeouts, and model specifications per tool
- Add capability flags (e.g., supports_streaming, supports_context_window)

### 3. Update Utils Module for Tool Detection
- Add function to `adws/adw_modules/utils.py` to check tool availability
- Implement platform-specific detection (macOS, Linux, Windows)
- Add caching to avoid repeated detection calls
- Include version checking for tools that require specific versions

### 4. Create Unit Tests for Tool Detection
- Create `adws/adw_tests/test_external_tools.py`
- Test tool detection with mocked commands
- Test fallback chain logic
- Test configuration loading and validation
- Test priority ordering and selection logic

### 5. Create New Scout Command with External Tools
- Copy `scout_improved.md` to `scout_external_tools.md`
- Replace hard-coded tool list with dynamic tool selection
- Add tool detection phase before agent spawning
- Implement fallback logic when preferred tools unavailable
- Add configuration for max tokens per tool

### 6. Implement Token Limit Configuration
- Add CLAUDE_CODE_MAX_OUTPUT_TOKENS environment variable handling
- Create per-tool token limit configuration
- Implement response truncation with continuation markers
- Add warning messages when approaching token limits

### 7. Add Lightweight Analyzer Tools
- Create simple Python scripts for targeted analysis:
  - `file_mapper.py` - Quick file tree with function signatures
  - `import_analyzer.py` - Dependency graph generator
  - `complexity_scorer.py` - Identify complex areas needing attention
- Place in `scripts/analyzers/` directory
- Add to tool registry with appropriate limits

### 8. Create Installation Helper Script
- Create `scripts/install_external_tools.sh`
- Add installation commands for each supported tool
- Include platform detection and appropriate package managers
- Add verification steps to confirm successful installation
- Create update mechanism for tool versions

### 9. Update Agent Module for External Tools
- Modify `adws/adw_modules/agent.py` to use tool registry
- Add external tool invocation alongside claude_code
- Implement timeout and error handling per tool
- Add logging for tool selection and fallback decisions

### 10. Create Integration Tests
- Add tests to verify scout works with various tool combinations
- Test fallback scenarios when tools are unavailable
- Test token limit handling and truncation
- Test parallel execution with mixed tool types

### 11. Create Documentation
- Create `docs/EXTERNAL_TOOLS.md` with:
  - List of supported tools and their capabilities
  - Installation instructions per platform
  - Configuration guide for adding new tools
  - Troubleshooting common issues
  - Performance comparison of different tools

### 12. Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Test scout command with external tools
- Verify fallback to native tools
- Check token limit handling

## Testing Strategy
### Unit Tests
- Tool detection module: Mock command availability checks
- Configuration loading: Validate JSON parsing and schema
- Tool selection logic: Priority ordering and capability matching
- Fallback chains: Ensure graceful degradation
- Token limit handling: Truncation and continuation

### Edge Cases
- No external tools available (full fallback to native)
- All tools timing out simultaneously
- Token limits exceeded mid-response
- Malformed tool configuration file
- Platform-specific tool availability
- Network failures for API-based tools
- Concurrent tool execution limits
- Invalid tool responses/formats

## Acceptance Criteria
- [x] External tools can be dynamically detected and used by scout subagents
- [x] Token limits are configurable per tool with appropriate defaults
- [x] Fallback chain works correctly (external → claude/gemini → native)
- [x] No regression in existing scout functionality
- [x] New tools can be added via configuration without code changes
- [x] Performance improves for large codebase analysis (no token limit errors)
- [x] Clear documentation for adding and configuring external tools
- [x] Installation helper script successfully installs tools on major platforms
- [x] Error messages clearly indicate tool failures and fallback decisions
- [x] Parallel execution continues to work with mixed tool types

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `python adws/adw_tests/test_external_tools.py` - Run unit tests for tool detection module
- `python -c "from adws.adw_modules.external_tools import ToolRegistry; print(ToolRegistry().detect_tools())"` - Verify tool detection works
- `/scout "test external tools" "4"` - Run scout with external tools to verify integration
- `CLAUDE_CODE_MAX_OUTPUT_TOKENS=16384 /scout "large analysis" "4"` - Test with increased token limit
- `mv $(which gemini) $(which gemini).bak 2>/dev/null; /scout "test fallback" "4"; mv $(which gemini).bak $(which gemini) 2>/dev/null` - Test fallback when tool unavailable
- `cd adws && uv run pytest adw_tests/test_external_tools.py` - Run tests in ADW environment
- `cat agents/scout_files/relevant_files.json | jq '.files | length'` - Verify scout produces valid output
- `git diff --stat` - Ensure no unintended changes to codebase

## Notes
**Future Considerations:**
- Consider adding tool performance metrics to optimize selection
- May want to add cost tracking for API-based tools
- Could implement tool pools for rate limit management
- Consider caching tool outputs for repeated analyses
- May need platform-specific installers (brew, apt, winget)

**Implementation Tips:**
- Start with Continue and Cursor as they have the largest context windows
- Use subprocess with proper timeout handling for all external tools
- Consider using asyncio for truly parallel tool execution
- Keep tool configurations in JSON for easy updates without code changes
- Add prometheus metrics for tool usage and performance monitoring

**Security Notes:**
- Validate all tool outputs before processing
- Sanitize file paths from tool responses
- Never execute code returned by external tools
- Use subprocess with shell=False for security
- Implement rate limiting for API-based tools