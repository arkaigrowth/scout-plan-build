# Scout Plan Build MVP - Configuration & Setup Patterns Analysis

## Executive Summary

The scout_plan_build_mvp repository contains comprehensive configuration and validation patterns centered around:
- Pydantic-based security validation
- Environment variable management with required/optional tiers
- GitHub integration (gh CLI + GITHUB_PAT)
- R2 cloud storage configuration
- Agent configuration with model selection mapping
- Structured exception hierarchy for error handling

---

## 1. ENVIRONMENT VARIABLES & CONFIGURATION

### Source File
`/Users/alexkamysz/AI/scout_plan_build_mvp/.env.sample`

### Required Variables (MUST HAVE)
```
ANTHROPIC_API_KEY           - Anthropic API key for Claude Code execution
GITHUB_REPO_URL             - GitHub repository URL (https://github.com/owner/repo)
```

### Optional Variables (Nice to Have)
```
CLAUDE_CODE_PATH                         - Path to claude CLI (default: "claude")
CLAUDE_CODE_MAX_OUTPUT_TOKENS            - Token limit (default: 8192, recommended: 32768+)
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR - Keep working dir in bash (default: true)
GITHUB_PAT                               - GitHub Personal Access Token
AGENT_CLOUD_SANDBOX_KEY                  - E2B sandbox key (optional)
AGENT_CLOUD_SANDBOX_URL                  - E2B sandbox URL (optional)
```

### R2 Storage Configuration (Optional)
```
CLOUDFLARE_ACCOUNT_ID              - Cloudflare account ID
CLOUDFLARE_R2_ACCESS_KEY_ID        - R2 access key
CLOUDFLARE_R2_SECRET_ACCESS_KEY    - R2 secret key
CLOUDFLARE_R2_BUCKET_NAME          - R2 bucket name
CLOUDFLARE_R2_PUBLIC_DOMAIN        - Public domain for uploaded files
```

### Setup Sequence (CRITICAL ORDER)
1. **Start**: Copy `.env.sample` to `.env`
2. **First**: Set `ANTHROPIC_API_KEY` (blocks all Claude Code execution if missing)
3. **Second**: Set `GITHUB_REPO_URL` (blocks GitHub operations if missing)
4. **Third**: Set `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` (prevents token limit errors early)
5. **Fourth**: Set `GITHUB_PAT` if using non-default gh auth
6. **Optional**: Configure R2 storage if handling screenshots/uploads

### Common Configuration Mistakes
1. **Token limit not increased**: Default 8192 causes "token limit exceeded" errors
2. **GITHUB_PAT not set**: Falls back to local gh auth (may fail in CI/automation)
3. **ANTHROPIC_API_KEY missing**: All agent execution fails silently
4. **GITHUB_REPO_URL format wrong**: Must be full URL, not just owner/repo
5. **R2 partial config**: Some vars set but not all - uploader silently disables

---

## 2. PYDANTIC VALIDATION SCHEMAS

### Source File
`/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/validators.py`

### Security Constants (DO NOT CHANGE)
```python
MAX_PROMPT_LENGTH = 100000              # 100KB max for prompts
MAX_COMMIT_MESSAGE_LENGTH = 5000        # Git commit message limit
MAX_BRANCH_NAME_LENGTH = 255            # Git filename limit
MAX_FILE_PATH_LENGTH = 4096             # Filesystem limit
MAX_ADW_ID_LENGTH = 64                  # Identifier length
MAX_ISSUE_NUMBER_LENGTH = 10            # GitHub issue number digits
```

### Allowed Path Prefixes (Whitelist)
```python
ALLOWED_PATH_PREFIXES = [
    "specs/",
    "agents/",
    "ai_docs/",
    "docs/",
    "scripts/",
    "adws/",
    "app/",
]
```

### Validation Classes Provided
1. **SafeUserInput**: Prompt validation (max length, null bytes, shell chars)
2. **SafeDocsUrl**: URL validation (http/https only)
3. **SafeFilePath**: Directory traversal prevention, prefix whitelist
4. **SafeGitBranch**: Branch name validation (alphanumeric, no reserved names)
5. **SafeCommitMessage**: Shell injection prevention in commit messages
6. **SafeIssueNumber**: GitHub issue number validation
7. **SafeADWID**: ADW identifier format (ADW-XXXXX)
8. **SafeCommandArgs**: Subprocess command sanitization
9. **SafeAgentName**: Agent name validation (lowercase, underscores)
10. **SafeSlashCommand**: Slash command whitelist validation

### Whitelist of Allowed Slash Commands
```python
ALLOWED_COMMANDS = [
    "/chore", "/bug", "/feature",
    "/classify_issue", "/classify_adw",
    "/generate_branch_name", "/commit", "/pull_request",
    "/implement", "/test", "/resolve_failed_test",
    "/test_e2e", "/resolve_failed_e2e_test",
    "/review", "/patch", "/document",
]
```

### Validation Pitfalls
1. **Path traversal**: Use `SafeFilePath` for ALL file operations
2. **Shell injection**: Use `SafeCommitMessage` for git commits
3. **Branch name safety**: Cannot use "main", "master", "head"
4. **Metadata validation**: Always validate issue numbers, ADW IDs

---

## 3. GITHUB INTEGRATION SETUP

### Source Files
- `adws/adw_modules/github.py` (gh CLI operations)
- `adws/adw_modules/data_types.py` (GitHub models)

### Environment Setup
```python
# From github.py - get_github_env()
env = {
    "GH_TOKEN": os.getenv("GITHUB_PAT"),
    "PATH": os.environ.get("PATH", ""),
}
```

### GitHub Models (Pydantic)
```python
GitHubUser              # login, name, is_bot
GitHubLabel             # id, name, color, description
GitHubMilestone         # number, title, state
GitHubComment           # author, body, created_at, updated_at
GitHubIssue             # number, title, body, state, assignees, labels, comments
GitHubIssueListItem     # Simplified issue for list responses
```

### Core GitHub Operations
```python
fetch_issue(issue_number, repo_path)           # Fetch single issue with all metadata
make_issue_comment(issue_id, comment)          # Post comment to issue
mark_issue_in_progress(issue_id)               # Add label + assignment
fetch_open_issues(repo_path)                   # Get all open issues
fetch_issue_comments(repo_path, issue_number)  # Get comments for issue
```

### Critical Setup Requirements
1. **gh CLI must be installed**: `brew install gh` (macOS) or equivalent
2. **gh must be authenticated**: Run `gh auth login` before first use
3. **GITHUB_PAT optional**: gh will use local auth if not set
4. **Repo URL required**: Must be extractable from git remote

### GitHub Integration Pitfalls
1. **No gh CLI**: Silently fails, returns EnvironmentError
2. **Wrong GITHUB_PAT**: gh falls back to local auth
3. **GITHUB_REPO_URL format**: Must be https://github.com/owner/repo
4. **Rate limits**: gh CLI will enforce GitHub API limits
5. **Bot comment loops**: SafeGitHubComment filters "[ADW-BOT]" prefix

---

## 4. R2 STORAGE CONFIGURATION

### Source File
`adws/adw_modules/r2_uploader.py`

### Required Environment Variables (All or Nothing)
```python
CLOUDFLARE_ACCOUNT_ID              # Your Cloudflare account ID
CLOUDFLARE_R2_ACCESS_KEY_ID        # R2 API token access key
CLOUDFLARE_R2_SECRET_ACCESS_KEY    # R2 API token secret
CLOUDFLARE_R2_BUCKET_NAME          # Bucket name (required)
CLOUDFLARE_R2_PUBLIC_DOMAIN        # Optional: default = tac-public-imgs.iddagents.com
```

### Initialization Behavior
```python
# R2Uploader._initialize()
# - Checks if ALL required vars are present
# - If ANY missing → logs info message + disables uploads
# - If all present → creates boto3 S3 client to R2 endpoint
# - If connection fails → logs warning + disables uploads (graceful)
```

### Configuration Error Modes
1. **Partial config (1-3 vars missing)**: Silently disabled, no error
2. **All vars present but wrong values**: boto3 connection fails, logged as warning
3. **Bucket doesn't exist**: Will fail on upload attempt (not init time)
4. **Invalid credentials**: boto3 raises ClientError on upload

### R2 Uploader Methods
```python
upload_file(file_path, object_key)              # Single file upload
upload_screenshots(screenshots[], adw_id)       # Batch screenshots
```

### R2 Upload Pitfalls
1. **Graceful degradation**: Missing config doesn't error, just disables uploads
2. **Absolute paths required**: Relative paths auto-converted
3. **Default domain assumption**: Uses tac-public-imgs.iddagents.com if not set
4. **Object key pattern**: `adw/{adw_id}/review/{filename}`

---

## 5. AGENT CONFIGURATION PATTERNS

### Source File
`adws/adw_modules/agent.py`

### Claude Code CLI Setup
```python
CLAUDE_PATH = os.getenv("CLAUDE_CODE_PATH", "claude")
# - Default: "claude" (must be in PATH)
# - Can override with full path
# - Checked with `claude --version` on first use
```

### Agent Model Mapping
```python
SLASH_COMMAND_MODEL_MAP = {
    # Issue classification
    "/classify_issue": "sonnet",           # Lightweight
    "/classify_adw": "sonnet",
    
    # Implementation (use Opus for complexity)
    "/implement": "opus",                  # Heavyweight
    "/feature": "opus",
    "/bug": "opus",
    "/patch": "opus",
    
    # Testing/Reviews
    "/test": "sonnet",                     # Medium
    "/review": "opus",                     # Heavy
    "/resolve_failed_test": "sonnet",
    
    # Documentation
    "/document": "sonnet",                 # Lightweight
}
```

### Agent Configuration Models
```python
AgentPromptRequest
    ├── prompt: str                        # The prompt to execute
    ├── adw_id: str                        # Workflow ID for tracking
    ├── agent_name: str                    # Default: "ops"
    ├── model: Literal["sonnet"|"opus"]    # Default: "sonnet"
    ├── dangerously_skip_permissions: bool # Default: false
    └── output_file: str                   # Where to save JSONL output

AgentPromptResponse
    ├── output: str                        # Response text
    ├── success: bool                      # Execution success
    └── session_id: Optional[str]          # Claude Code session ID
```

### Agent Execution Flow
```
1. Check Claude Code installed (claude --version)
2. Create output directory (agents/{adw_id}/{agent_name}/)
3. Build command: [claude, -p, prompt, --model, model, --output-format, stream-json]
4. Execute with safe environment (filtered env vars)
5. Parse JSONL output file
6. Extract result message and convert to JSON
7. Return response with success status
```

### Agent Configuration Pitfalls
1. **Token limit in .env not respected**: Set CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
2. **Model not in mapping**: Defaults to "sonnet"
3. **Output directory not created**: Script creates automatically
4. **JSONL parsing fails**: Agent error, check output file format
5. **Timeout after 10 minutes**: Long operations may be killed

### Environment Variables Passed to Agent
```python
get_safe_subprocess_env() returns:
├── ANTHROPIC_API_KEY          # Required
├── GITHUB_PAT / GH_TOKEN       # Optional
├── CLAUDE_CODE_PATH            # Default: "claude"
├── CLAUDE_CODE_MAX_OUTPUT_TOKENS
├── CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR
├── E2B_API_KEY                 # Optional
├── CLOUDFLARED_TUNNEL_TOKEN    # Optional
├── HOME, USER, PATH, SHELL
├── LANG, LC_ALL, TERM
├── PYTHONPATH, PYTHONUNBUFFERED
└── PWD (current working directory)
```

---

## 6. STRUCTURED EXCEPTION HIERARCHY

### Source File
`adws/adw_modules/exceptions.py`

### Base Exception
```python
ADWError(message, context={}, correlation_id=None)
├── timestamp: datetime        # When error occurred
├── to_dict() → Dict          # Serialization for logging
└── context: Dict             # Structured error data
```

### Exception Types (All inherit from ADWError)

#### Validation & Input Errors
```python
ValidationError(message, field=None)     # Invalid input data
StateError(message, adw_id=None)         # State corruption
```

#### Git & GitHub Operations
```python
GitOperationError(message, command, returncode, stderr)
GitHubAPIError(message, status_code, api_endpoint)
```

#### Agent & Workflow
```python
AgentError(message, agent_name, slash_command, session_id)
WorkflowError(message, workflow_name, step)
```

#### Resource Limits
```python
TokenLimitError(message, tokens_requested, tokens_available)
RateLimitError(message, retry_after, limit_type)
```

#### System & Environment
```python
EnvironmentError(message, missing_vars=[])
FileSystemError(message, path, operation)
```

### Error Handling Utilities
```python
handle_error(error, logger, issue_number, adw_id)
├── Logs with appropriate level
├── Posts to GitHub if issue_number provided
└── Returns structured error dict

get_recovery_strategy(error) → str
├── Provides human-readable recovery instructions
└── Tailored to error type
```

### Exception Usage Patterns
1. **Always catch specific exceptions**: Not bare `except Exception`
2. **Include context**: Provide relevant details (file path, command, etc.)
3. **Correlation IDs**: Track multi-operation errors with correlation_id
4. **Recovery strategies**: Logged error should include recovery path

---

## 7. DATA TYPES & VALIDATION

### Source File
`adws/adw_modules/data_types.py`

### ADW Workflow Types
```python
ADWWorkflow = Literal[
    "adw_plan",                        # Planning only
    "adw_build",                       # Building only
    "adw_test",                        # Testing only
    "adw_review",                      # Review only
    "adw_document",                    # Documentation only
    "adw_patch",                       # Direct patch
    "adw_plan_build",                  # Plan + Build
    "adw_plan_build_test",             # Plan + Build + Test
    "adw_plan_build_test_review",      # Plan + Build + Test + Review
    "adw_sdlc",                        # Complete SDLC
]
```

### Core Data Models
```python
ADWStateData
├── adw_id: str
├── issue_number: Optional[str]
├── branch_name: Optional[str]
├── plan_file: Optional[str]
└── issue_class: Optional[IssueClassSlashCommand]

ReviewResult
├── success: bool
├── review_summary: str
├── review_issues: List[ReviewIssue]
├── screenshots: List[str]
└── screenshot_urls: List[str]

TestResult
├── test_name: str
├── passed: bool
├── execution_command: str
├── test_purpose: str
└── error: Optional[str]
```

### State File Location Pattern
```
agents/{adw_id}/adw_state.json
```

---

## 8. SETUP REQUIREMENTS & DEPENDENCIES

### Installation Order
1. **Python 3.8+**: Required for Pydantic, subprocess operations
2. **Required CLI Tools**:
   - `git` (for version control)
   - `gh` (GitHub CLI - brew install gh)
   - `claude` (Claude Code CLI)
3. **Python Dependencies**:
   - `pydantic` (validation)
   - `python-dotenv` (environment loading)
   - `boto3` (R2 uploads)
   - `botocore` (AWS SDK)

### Environment Variable Setup Validation
```python
# Before running any workflow:
1. Check ANTHROPIC_API_KEY is set
2. Check GITHUB_REPO_URL is set
3. Verify CLAUDE_CODE_MAX_OUTPUT_TOKENS >= 32768
4. Run: git remote -v (verify origin exists)
5. Run: gh auth status (verify gh authentication)
6. Run: claude --version (verify Claude Code CLI)
```

### Configuration Dependency Chain
```
ANTHROPIC_API_KEY
├── → Required for ALL agent execution
└── → Blocks: agent.py, adw_plan.py, adw_build.py

GITHUB_REPO_URL
├── → Required for GitHub operations
├── → Extracted from git remote if not set
└── → Blocks: github.py operations

CLAUDE_CODE_MAX_OUTPUT_TOKENS
├── → Prevents token limit errors
└── → Should be set FIRST (before any agent calls)

GITHUB_PAT
├── → Optional (gh uses local auth by default)
├── → Required in CI/automation without gh login
└── → Blocks: GitHub operations if auth fails

R2_* variables (all-or-nothing)
├── → Optional (gracefully disables if missing)
└── → Blocks: Upload functionality if incomplete
```

---

## 9. COMMON PITFALLS & SOLUTIONS

### Pitfall 1: Token Limit Errors
**Problem**: Agent execution fails with "token limit exceeded"
**Cause**: CLAUDE_CODE_MAX_OUTPUT_TOKENS not set or too low (default: 8192)
**Solution**: 
```bash
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
# Or in .env:
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
```

### Pitfall 2: GitHub Operations Fail Silently
**Problem**: gh commands return errors but workflow continues
**Cause**: GITHUB_PAT not set + gh not authenticated locally
**Solution**:
```bash
# Option 1: Authenticate locally
gh auth login

# Option 2: Set GITHUB_PAT
export GITHUB_PAT=ghp_xxxxx
```

### Pitfall 3: Path Traversal Security Errors
**Problem**: SafeFilePath validation fails with "not in allowed prefixes"
**Cause**: Trying to access files outside ALLOWED_PATH_PREFIXES
**Solution**: Only use files in: specs/, agents/, ai_docs/, docs/, scripts/, adws/, app/

### Pitfall 4: R2 Upload Fails Without Error
**Problem**: Uploads don't work but no error message
**Cause**: Partial R2 configuration (some vars set, not all)
**Solution**: Verify all R2 vars set:
```bash
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_R2_ACCESS_KEY_ID
CLOUDFLARE_R2_SECRET_ACCESS_KEY
CLOUDFLARE_R2_BUCKET_NAME
```

### Pitfall 5: Branch Name Validation Fails
**Problem**: SafeGitBranch rejects valid-looking branch names
**Cause**: Reserved names (main, master, head) or invalid chars
**Solution**: Use format: `feature/issue-123-description` (no special chars except /)

### Pitfall 6: Slash Command Not Recognized
**Problem**: AgentError with "Invalid slash command"
**Cause**: Command not in ALLOWED_COMMANDS whitelist
**Solution**: Use only whitelisted commands:
- /plan_w_docs, /build_adw, /scout
- /classify_issue, /implement, /test, /review, /document

### Pitfall 7: Environment Variables Not Visible to Subprocess
**Problem**: Claude Code agent can't find GITHUB_PAT or other vars
**Cause**: Not using get_safe_subprocess_env() to pass environment
**Solution**: All agent execution uses filtered env from utils.py

### Pitfall 8: State File Corruption
**Problem**: ADWStateData parsing fails
**Cause**: State file missing required fields (adw_id especially)
**Solution**: State files must have: adw_id (always), other fields optional

---

## 10. CONFIGURATION FILES SUMMARY

### Primary Configuration Files
| File | Purpose | Format |
|------|---------|--------|
| `.env` | Environment variables | KEY=VALUE |
| `.env.sample` | Template/documentation | KEY=value with comments |
| `adws/adw_modules/validators.py` | Validation schemas | Python/Pydantic |
| `adws/adw_modules/agent.py` | Agent configuration | Python constants |
| `adws/adw_modules/exceptions.py` | Error definitions | Python classes |
| `adws/adw_modules/data_types.py` | Data models | Pydantic models |

### State & Runtime Files
| Location | Purpose |
|----------|---------|
| `agents/{adw_id}/` | Per-workflow state directory |
| `agents/{adw_id}/adw_state.json` | Persistent state file |
| `agents/{adw_id}/raw_output.jsonl` | Agent execution output |
| `specs/` | Specification documents |

### Documentation Files
| File | Content |
|------|---------|
| `docs/SPEC_SCHEMA.md` | Specification validation rules |
| `CLAUDE.md` | Project-specific Claude instructions |
| `CLAUDE.local.md` | Local environment overrides |
| `README.md` | Quick start guide |

---

## 11. SKILLS RECOMMENDATIONS

Based on this analysis, the following Claude Skills would be valuable:

### Skill 1: Environment Validation Checker
- **Purpose**: Validate complete environment setup
- **Inputs**: Optional env var overrides
- **Outputs**: Report of missing/invalid vars, setup instructions
- **Key Logic**: Check required vars, verify CLI tools, test connections

### Skill 2: Configuration Helper
- **Purpose**: Generate correct .env from template
- **Inputs**: List of integration types (GitHub, R2, E2B)
- **Outputs**: Annotated .env file with setup instructions
- **Key Logic**: Only include needed vars, validate formats, provide setup URLs

### Skill 3: Error Recovery Guide
- **Purpose**: Provide recovery steps for specific error types
- **Inputs**: Error message + error type (from exceptions.py)
- **Outputs**: Step-by-step recovery instructions
- **Key Logic**: Match error to ADWError type, apply recovery_strategy

### Skill 4: GitHub Integration Setup
- **Purpose**: Configure and validate GitHub integration
- **Inputs**: repo_path, optional GITHUB_PAT
- **Outputs**: Validation report, test issue fetch
- **Key Logic**: Extract repo from git remote, test gh CLI, validate auth

### Skill 5: Validation Schema Reference
- **Purpose**: Quick reference for all validation rules
- **Inputs**: Field name or validator class name
- **Outputs**: Validation rules, allowed values, examples
- **Key Logic**: Map fields to SafeX classes, show constraints

### Skill 6: Agent Configuration Advisor
- **Purpose**: Recommend optimal model/settings for workflows
- **Inputs**: Task type, complexity level
- **Outputs**: Recommended model, token settings, command mapping
- **Key Logic**: Use SLASH_COMMAND_MODEL_MAP, adjust for complexity

### Skill 7: R2 Setup Wizard
- **Purpose**: Configure R2 storage for uploads
- **Inputs**: Cloudflare account info
- **Outputs**: .env snippet, boto3 test code, upload validation
- **Key Logic**: Validate all vars present, test connection, provide upload example

### Skill 8: State File Inspector
- **Purpose**: Debug and repair corrupted state files
- **Inputs**: State file path or adw_id
- **Outputs**: State validation report, repair options
- **Key Logic**: Load JSON, validate against ADWStateData model, suggest fixes

---

## 12. SETUP CHECKLIST

```
[ ] REQUIRED: Copy .env.sample to .env
[ ] REQUIRED: Set ANTHROPIC_API_KEY in .env
[ ] REQUIRED: Set GITHUB_REPO_URL in .env
[ ] REQUIRED: Set CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768 in .env
[ ] REQUIRED: Verify git remote configured: git remote -v
[ ] REQUIRED: Install gh CLI: brew install gh
[ ] REQUIRED: Authenticate gh: gh auth login
[ ] REQUIRED: Install Claude Code CLI

[ ] RECOMMENDED: Set GITHUB_PAT (for CI automation)
[ ] RECOMMENDED: Test agent execution: claude --version

[ ] OPTIONAL: Configure R2 storage (if handling uploads)
  [ ] Set CLOUDFLARE_ACCOUNT_ID
  [ ] Set CLOUDFLARE_R2_ACCESS_KEY_ID
  [ ] Set CLOUDFLARE_R2_SECRET_ACCESS_KEY
  [ ] Set CLOUDFLARE_R2_BUCKET_NAME
  [ ] Test R2 connection

[ ] OPTIONAL: Configure E2B sandbox (if using agents)
[ ] OPTIONAL: Configure Cloudflared tunnel (if needed)

[ ] VALIDATION: Run environment check script
[ ] VALIDATION: Test GitHub integration: gh issue list
[ ] VALIDATION: Create test spec and build
```

