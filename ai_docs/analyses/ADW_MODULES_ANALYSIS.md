# ADW Modules Architecture Analysis

## Overview
Five core composable modules that orchestrate the AI Developer Workflow system. Each module handles a specific domain while maintaining clean integration points.

---

## 1. `workflow_ops.py` - Workflow Orchestration

### Agent Constants
```python
AGENT_PLANNER = "sdlc_planner"
AGENT_IMPLEMENTOR = "sdlc_implementor"
AGENT_CLASSIFIER = "issue_classifier"
AGENT_BRANCH_GENERATOR = "branch_generator"
AGENT_PR_CREATOR = "pr_creator"

AVAILABLE_ADW_WORKFLOWS = [
    "adw_plan", "adw_build", "adw_test", "adw_review",
    "adw_document", "adw_patch", "adw_plan_build",
    "adw_plan_build_test", "adw_plan_build_test_review", "adw_sdlc"
]
```

### Top-Level Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `format_issue_message()` | `(adw_id: str, agent_name: str, message: str, session_id: Optional[str])` → `str` | Format messages with ADW bot identifier to prevent webhook loops |
| `extract_adw_info()` | `(text: str, temp_adw_id: str)` → `Tuple[Optional[str], Optional[str]]` | Extract workflow command and ADW ID using classify_adw agent |
| `classify_issue()` | `(issue: GitHubIssue, adw_id: str, logger)` → `Tuple[Optional[IssueClassSlashCommand], Optional[str]]` | Classify issue as /chore, /bug, or /feature |
| `build_plan()` | `(issue: GitHubIssue, command: str, adw_id: str, logger)` → `AgentPromptResponse` | Build implementation plan for issue |
| `implement_plan()` | `(plan_file: str, adw_id: str, logger, agent_name: Optional[str])` → `AgentPromptResponse` | Execute /implement command on plan file |
| `generate_branch_name()` | `(issue: GitHubIssue, issue_class: IssueClassSlashCommand, adw_id: str, logger)` → `Tuple[Optional[str], Optional[str]]` | Generate and create git branch |
| `create_commit()` | `(agent_name: str, issue: GitHubIssue, issue_class: IssueClassSlashCommand, adw_id: str, logger)` → `Tuple[Optional[str], Optional[str]]` | Create formatted commit message |
| `create_pull_request()` | `(branch_name: str, issue: Optional[GitHubIssue], state: ADWState, logger)` → `Tuple[Optional[str], Optional[str]]` | Create PR for implemented changes |
| `ensure_plan_exists()` | `(state: ADWState, issue_number: str)` → `str` | Find plan file or error if missing |
| `ensure_adw_id()` | `(issue_number: str, adw_id: Optional[str], logger: Optional[logging.Logger])` → `str` | Get/create ADW ID and initialize state |
| `find_existing_branch_for_issue()` | `(issue_number: str, adw_id: Optional[str])` → `Optional[str]` | Find branch matching standardized pattern |
| `find_plan_for_issue()` | `(issue_number: str, adw_id: Optional[str])` → `Optional[str]` | Find plan file in agents/{adw_id} directory |
| `create_or_find_branch()` | `(issue_number: str, issue: GitHubIssue, state: ADWState, logger)` → `Tuple[str, Optional[str]]` | Create or locate branch with state checking |
| `find_spec_file()` | `(state: ADWState, logger)` → `Optional[str]` | Find spec from state or git diff |
| `create_and_implement_patch()` | `(adw_id: str, review_change_request: str, logger, agent_name_planner: str, agent_name_implementor: str, spec_path: Optional[str], issue_screenshots: Optional[str])` → `Tuple[Optional[str], AgentPromptResponse]` | Create and execute patch plan |

### Key Integration Points
- **Imports**: `data_types`, `agent`, `github`, `state`, `utils`
- **Exports**: All functions called by main ADW scripts (plan/build/review/patch)
- **Agent Chain**: Issue → Classify → Plan → Branch → Commit → PR
- **State Management**: Passes ADWState through workflow chain

---

## 2. `agent.py` - Claude Code Execution

### Model Mapping
```python
SLASH_COMMAND_MODEL_MAP = {
    "/classify_issue": "sonnet",
    "/classify_adw": "sonnet",
    "/generate_branch_name": "sonnet",
    "/implement": "opus",           # Heavy computation
    "/test": "sonnet",
    "/resolve_failed_test": "sonnet",
    "/review": "opus",              # Heavy computation
    "/document": "sonnet",
    "/commit": "sonnet",
    "/pull_request": "sonnet",
    "/chore": "sonnet",
    "/bug": "opus",                 # Heavy computation
    "/feature": "opus",             # Heavy computation
    "/patch": "opus",               # Heavy computation
}
```

### Top-Level Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `get_model_for_slash_command()` | `(slash_command: str, default: str = "sonnet")` → `str` | Get recommended model for command |
| `check_claude_installed()` | `()` → `Optional[str]` | Verify Claude CLI availability; return error msg if missing |
| `parse_jsonl_output()` | `(output_file: str)` → `Tuple[List[Dict], Optional[Dict]]` | Parse stream-json output; extract result message |
| `convert_jsonl_to_json()` | `(jsonl_file: str)` → `str` | Convert JSONL to JSON array file |
| `get_claude_env()` | `()` → `Dict[str, str]` | Get safe environment vars for subprocess (wrapper) |
| `save_prompt()` | `(prompt: str, adw_id: str, agent_name: str = "ops")` → `None` | Save prompt to agents/{adw_id}/{agent_name}/prompts/ |
| `prompt_claude_code()` | `(request: AgentPromptRequest)` → `AgentPromptResponse` | Execute Claude CLI with stream-json format |
| `execute_template()` | `(request: AgentTemplateRequest)` → `AgentPromptResponse` | Execute slash command template with model override |

### Key Integration Points
- **Imports**: `data_types` (request/response models)
- **Exports**: `execute_template()` called by workflow_ops for all agent tasks
- **Model Selection**: Automatic based on command type (lighter for classification, heavier for implementation)
- **Output Format**: Stream-JSON parsed to AgentPromptResponse
- **Prompt Storage**: Persisted in agents/{adw_id}/{agent_name}/prompts/ for debugging

---

## 3. `github.py` - GitHub Integration

### Constants
```python
ADW_BOT_IDENTIFIER = "[ADW-BOT]"  # Prevent webhook loops
```

### Top-Level Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `get_github_env()` | `()` → `Optional[dict]` | Get subprocess env with GH_TOKEN for CLI auth |
| `get_repo_url()` | `()` → `str` | Extract GitHub repo URL from git remote |
| `extract_repo_path()` | `(github_url: str)` → `str` | Parse owner/repo from GitHub URL |
| `fetch_issue()` | `(issue_number: str, repo_path: str)` → `GitHubIssue` | Fetch issue as typed Pydantic model |
| `make_issue_comment()` | `(issue_id: str, comment: str)` → `None` | Post comment to issue |
| `mark_issue_in_progress()` | `(issue_id: str)` → `None` | Add label and assign to self |
| `fetch_open_issues()` | `(repo_path: str)` → `List[GitHubIssueListItem]` | Fetch all open issues |
| `fetch_issue_comments()` | `(repo_path: str, issue_number: int)` → `List[Dict]` | Fetch all comments for issue |
| `find_keyword_from_comment()` | `(keyword: str, issue: GitHubIssue)` → `Optional[GitHubComment]` | Find latest comment with keyword (skip bot comments) |

### Key Integration Points
- **Imports**: `data_types` (GitHub models)
- **Exports**: Called by workflow_ops and git_ops for issue/comment operations
- **Bot Safety**: Uses ADW_BOT_IDENTIFIER to prevent webhook loops
- **Auth**: Reads GITHUB_PAT env var for gh CLI authentication
- **Data Types**: Pydantic models for type safety

---

## 4. `git_ops.py` - Git Operations

### Top-Level Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `get_current_branch()` | `()` → `str` | Get current git branch name |
| `push_branch()` | `(branch_name: str)` → `Tuple[bool, Optional[str]]` | Push branch to origin; return (success, error) |
| `check_pr_exists()` | `(branch_name: str)` → `Optional[str]` | Check if PR exists for branch; return URL or None |
| `create_branch()` | `(branch_name: str)` → `Tuple[bool, Optional[str]]` | Create and checkout branch; handle existing branch case |
| `commit_changes()` | `(message: str)` → `Tuple[bool, Optional[str]]` | Stage all changes and commit; return (success, error) |
| `finalize_git_operations()` | `(state: ADWState, logger)` → `None` | Standard finalization: push branch and create/update PR |

### Key Integration Points
- **Imports**: `github` (repo operations), `ADWState` type hint
- **Exports**: Called by main ADW scripts for git workflow
- **State Usage**: Pulls branch_name, issue_number, adw_id from ADWState
- **PR Creation**: Falls back to workflow_ops.create_pull_request() if PR doesn't exist
- **Error Handling**: Returns tuples for graceful error propagation

---

## 5. `state.py` - State Management

### Class: `ADWState`

#### Constructor & Properties
```python
class ADWState:
    STATE_FILENAME = "adw_state.json"

    def __init__(self, adw_id: str)
        # Requires non-empty adw_id
        # Initializes: self.data = {"adw_id": adw_id}
```

#### Instance Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `update()` | `(**kwargs) → None` | Update state with filtered core fields |
| `get()` | `(key: str, default=None) → Any` | Retrieve value by key with default |
| `get_state_path()` | `() → str` | Return path agents/{adw_id}/adw_state.json |
| `save()` | `(workflow_step: Optional[str]) → None` | Persist state to JSON file with workflow_step logging |
| `to_stdout()` | `() → None` | Print state as JSON (for piping) |

#### Class Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `load()` | `(adw_id: str, logger: Optional) → Optional[ADWState]` | Load state from file or return None |
| `from_stdin()` | `() → Optional[ADWState]` | Read state from stdin if piped; return None for tty |

#### Core Fields (Filtered in update/save)
- `adw_id` (required)
- `issue_number`
- `branch_name`
- `plan_file`
- `issue_class`

### Key Integration Points
- **Imports**: `data_types` (ADWStateData for validation)
- **Exports**: Instantiated/loaded by all main ADW scripts
- **Storage**: agents/{adw_id}/adw_state.json
- **Validation**: Pydantic ADWStateData enforces schema
- **Persistence**: Survives script execution; shared across workflow phases

---

## Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Main ADW Script (adw_plan.py, adw_build.py, etc.)          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │ state   │   │workflow │   │ github  │
   │ .py     │   │_ops.py  │   │  .py    │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │             │
        │        ┌────▼────┐        │
        └────────┤agent.py │◄───────┘
                 │         │
          (Execute template,
           run Claude CLI,
           parse output)
                 │
        ┌────────┼────────┐
        │        │        │
   ┌────▼───┐ ┌─▼──────┐ │
   │git_ops │ │github  │ │
   │  .py   │ │(post)  │ │
   └────────┘ └────────┘ │
                         │
          (Branch, commit,
           push, PR ops)
```

---

## Key Design Patterns

### 1. **State as First-Class Object**
- ADWState carries context through entire workflow
- Persisted in file system for cross-session recovery
- Supports both piped and file-based I/O

### 2. **Agent Template Abstraction**
- `execute_template()` wraps Claude CLI invocation
- Model selection automatic via SLASH_COMMAND_MODEL_MAP
- Prompt/output persisted for audit trail

### 3. **Composable Workflow Operations**
- Each function in workflow_ops is atomic and reusable
- Can be chained in different orders (plan → build, plan → review, etc.)
- Explicit error tuples enable graceful failure handling

### 4. **GitHub Bot Safety**
- ADW_BOT_IDENTIFIER prevents webhook loops
- Filters bot comments when searching for keywords
- Safe env handling for gh CLI authentication

### 5. **Error Propagation**
- Functions return `(result, error_message)` tuples
- Callers decide whether to propagate or handle
- Logging context maintained throughout

---

## Data Type Dependencies

All modules use:
- `AgentTemplateRequest` / `AgentPromptResponse` (agent.py)
- `GitHubIssue` / `GitHubComment` (github.py)
- `ADWState` (state.py)
- `IssueClassSlashCommand` (workflow_ops.py)

Defined in: `adw_modules/data_types.py`

---

## Cross-Module Imports Map

| Module | Imports From |
|--------|-------------|
| workflow_ops | agent, github, state, utils, data_types |
| agent | data_types, utils |
| github | data_types |
| git_ops | github (for repo operations) |
| state | data_types |

**No circular dependencies** ✓

---

## Environment Variables Required

- `CLAUDE_CODE_PATH` (agent.py) - Path to claude CLI
- `GITHUB_PAT` (github.py) - GitHub personal access token
- `.env` file loaded by agent.py via python-dotenv

