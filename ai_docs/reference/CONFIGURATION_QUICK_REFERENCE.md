# Scout Plan Build MVP - Configuration Quick Reference

## Minimal Setup (5 Minutes)

```bash
# 1. Copy environment template
cp .env.sample .env

# 2. Edit .env with your values (required)
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_REPO_URL="https://github.com/owner/repo"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# 3. Verify tools installed
git --version
gh --version
claude --version

# 4. Test GitHub auth
gh auth login
gh issue list
```

---

## Environment Variables at a Glance

### Must Have
| Variable | Value | Example |
|----------|-------|---------|
| ANTHROPIC_API_KEY | Your API key | sk-ant-... |
| GITHUB_REPO_URL | Repository URL | https://github.com/owner/repo |
| CLAUDE_CODE_MAX_OUTPUT_TOKENS | Token limit | 32768 |

### Optional (Recommended)
| Variable | Value | Default |
|----------|-------|---------|
| GITHUB_PAT | GitHub token | Uses gh login |
| CLAUDE_CODE_PATH | Path to claude | "claude" |

### Optional (R2 Uploads)
| Variables | Purpose |
|-----------|---------|
| CLOUDFLARE_* (4 vars) | R2 storage configuration |

---

## Validation Rules

### Branch Names
✅ Valid: `feature/issue-123-fix`, `bugfix/auth-token`
❌ Invalid: `main`, `master`, `feature/..--test`, `feature/_start`

### File Paths
✅ Valid: `specs/plan.md`, `scout_outputs/workflows/abc123/output.json`
❌ Invalid: `../../../etc/passwd`, `/etc/passwd`, `other/path.txt`

### Commit Messages
✅ Valid: `feat: Add authentication`
❌ Invalid: `fix; $(rm -rf /)`, `update && reboot`

### ADW IDs
✅ Valid: `ADW-ABC123`
❌ Invalid: `ADW-abc123`, `ABC123`

### Issue Numbers
✅ Valid: `123`, `456789`
❌ Invalid: `-123`, `abc123`

---

## Common Environment Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Token limit exceeded" | CLAUDE_CODE_MAX_OUTPUT_TOKENS too low | Set to 32768 |
| "GitHub CLI not found" | gh not installed | `brew install gh` |
| "ANTHROPIC_API_KEY not set" | Missing env var | Set in .env |
| "Not in allowed prefixes" | File path security | Use `specs/`, `agents/`, etc |
| "R2 upload disabled" | Partial R2 config | Verify all 4 R2 vars |
| "gh: command not found" | gh not in PATH | Install or set full path |

---

## Configuration Dependencies

```
ANTHROPIC_API_KEY (Required)
  ├─ Blocks: All agent execution
  ├─ Location: .env or environment
  └─ Status: Check with: [[ -n "$ANTHROPIC_API_KEY" ]]

GITHUB_REPO_URL (Required)
  ├─ Blocks: GitHub operations
  ├─ Fallback: git remote get-url origin
  └─ Status: Check with: git remote -v

CLAUDE_CODE_MAX_OUTPUT_TOKENS (Highly Recommended)
  ├─ Prevents: Token limit errors
  ├─ Default: 8192 (too low)
  ├─ Recommended: 32768
  └─ Status: Check with: echo $CLAUDE_CODE_MAX_OUTPUT_TOKENS

GITHUB_PAT (Optional for local, Required for CI)
  ├─ Fallback: gh auth login (local machine)
  ├─ Required: Automation/CI environments
  └─ Status: Check with: gh auth status

R2_* variables (All-or-Nothing)
  ├─ Required: ALL 4 CLOUDFLARE_* variables
  ├─ Behavior: Silently disabled if incomplete
  └─ Required for: Screenshot/file uploads
```

---

## Setup Validation Commands

```bash
# Check all required variables
echo "ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY" | grep -q sk-ant && echo "✓" || echo "✗"
echo "GITHUB_REPO_URL: $GITHUB_REPO_URL" | grep -q github.com && echo "✓" || echo "✗"
echo "MAX_OUTPUT_TOKENS: $CLAUDE_CODE_MAX_OUTPUT_TOKENS" | grep -q 3276 && echo "✓" || echo "✗"

# Test CLI tools
git --version >/dev/null && echo "git ✓" || echo "git ✗"
gh --version >/dev/null && echo "gh ✓" || echo "gh ✗"
claude --version >/dev/null && echo "claude ✓" || echo "claude ✗"

# Test GitHub auth
gh auth status 2>/dev/null && echo "gh auth ✓" || echo "gh auth ✗"

# Test Anthropic API
curl -s https://api.anthropic.com/v1/models \
  -H "x-api-key: ${ANTHROPIC_API_KEY}" | grep -q claude && echo "Anthropic API ✓" || echo "Anthropic API ✗"
```

---

## File Organization

```
.env                              # Your local config (git-ignored)
.env.sample                       # Template (in repo)
├─ REQUIRED: ANTHROPIC_API_KEY
├─ REQUIRED: GITHUB_REPO_URL
├─ RECOMMENDED: CLAUDE_CODE_MAX_OUTPUT_TOKENS
└─ OPTIONAL: GITHUB_PAT, R2_*

adws/adw_modules/
├─ validators.py                  # Security validation (READ-ONLY)
├─ agent.py                       # Agent config (READ-ONLY)
├─ exceptions.py                  # Error types (READ-ONLY)
├─ data_types.py                  # Data models (READ-ONLY)
└─ github.py                      # GitHub integration

agents/{adw_id}/                  # Runtime state (generated)
├─ adw_state.json                 # State persistence
├─ raw_output.jsonl               # Agent execution logs
└─ specs/                         # Specification files

specs/                            # Implementation plans
├─ issue-{num}-adw-{id}-{slug}.md
└─ {naming convention strictly enforced}
```

---

## Model Selection Rules

Use **Opus** for:
- Implementation (`/implement`)
- Complex bugs (`/bug`)
- New features (`/feature`)
- Code patches (`/patch`)
- Code reviews (`/review`)

Use **Sonnet** for:
- Classifications (`/classify_issue`, `/classify_adw`)
- Simple tests (`/test`)
- Documentation (`/document`)
- Branches (`/generate_branch_name`)

---

## R2 Configuration (If Needed)

All 4 required or upload feature disables silently:

```bash
# Get from Cloudflare R2 console
CLOUDFLARE_ACCOUNT_ID=...          # Your account ID
CLOUDFLARE_R2_ACCESS_KEY_ID=...    # API token access key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=...# API token secret
CLOUDFLARE_R2_BUCKET_NAME=...      # Bucket name
CLOUDFLARE_R2_PUBLIC_DOMAIN=...    # Custom domain (optional)
```

Upload object key pattern: `adw/{adw_id}/review/{filename}`

---

## Allowed Slash Commands

```
Issue classification:
  /chore, /bug, /feature

ADW workflows:
  /classify_issue, /classify_adw, /generate_branch_name
  /commit, /pull_request, /implement, /test
  /resolve_failed_test, /test_e2e, /resolve_failed_e2e_test
  /review, /patch, /document
```

---

## Error Recovery Quick Guide

| Error | Recovery |
|-------|----------|
| TokenLimitError | Reduce prompt size, increase token limit |
| RateLimitError | Wait retry_after seconds before retry |
| GitOperationError | Run `git status`, consider `git reset` |
| GitHubAPIError | Check gh auth, verify repo URL |
| EnvironmentError | Set missing variables from .env.sample |
| StateError | Check adw_state.json integrity |
| ValidationError | Check field constraints in validators.py |

---

## Passwords & Secrets

**NEVER** commit to git:
- `.env` (contains API keys)
- `.env.local` (personal overrides)
- `agents/*/secrets.json` (if storing secrets)

**Always** use:
- Environment variables from `.env`
- GitHub secrets for CI/CD
- Cloudflare API tokens (time-limited if possible)

---

## Testing Your Setup

```bash
# 1. Create test spec
echo '# Test
Plan for basic test' > specs/test-001-adw-xxx-test.md

# 2. Try agent execution
claude -p "summarize this: hello world" --model sonnet --output-format stream-json

# 3. Test GitHub
gh issue list --limit 5

# 4. Validate spec schema
python -m adws.adw_modules.schema_validator specs/test-001-adw-xxx-test.md

# 5. Check R2 (if configured)
python -c "from adws.adw_modules.r2_uploader import R2Uploader; logger=__import__('logging').getLogger(); r2=R2Uploader(logger); print('R2 enabled' if r2.enabled else 'R2 disabled')"
```

---

## Setup Patterns

### Setup Sequence (CRITICAL ORDER)

1. **Start**: Copy `.env.sample` to `.env`
2. **First**: Set `ANTHROPIC_API_KEY` (blocks all Claude Code execution if missing)
3. **Second**: Set `GITHUB_REPO_URL` (blocks GitHub operations if missing)
4. **Third**: Set `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` (prevents token limit errors early)
5. **Fourth**: Set `GITHUB_PAT` if using non-default gh auth
6. **Optional**: Configure R2 storage if handling screenshots/uploads

### Common Configuration Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Token limit not increased | Default 8192 causes errors | Set to 32768 |
| GITHUB_PAT not set | Falls back to local gh auth | May fail in CI |
| ANTHROPIC_API_KEY missing | Agent execution fails | Set in .env |
| GITHUB_REPO_URL format wrong | Must be full URL | Use https://github.com/owner/repo |
| R2 partial config | Uploader silently disables | Set all 4 R2 vars |

### Validation Constants (DO NOT CHANGE)

```python
MAX_PROMPT_LENGTH = 100000         # 100KB max for prompts
MAX_COMMIT_MESSAGE_LENGTH = 5000   # Git commit message limit
MAX_BRANCH_NAME_LENGTH = 255       # Git filename limit
MAX_FILE_PATH_LENGTH = 4096        # Filesystem limit
MAX_ADW_ID_LENGTH = 64             # Identifier length
MAX_ISSUE_NUMBER_LENGTH = 10       # GitHub issue number digits
```

### Allowed Path Prefixes (Whitelist)

Files can only be accessed in these directories:
- `specs/`
- `agents/`
- `ai_docs/`
- `docs/`
- `scripts/`
- `adws/`
- `app/`

### GitHub Integration Pitfalls

1. **No gh CLI**: Silently fails, returns EnvironmentError
2. **Wrong GITHUB_PAT**: gh falls back to local auth
3. **GITHUB_REPO_URL format**: Must be https://github.com/owner/repo
4. **Rate limits**: gh CLI will enforce GitHub API limits
5. **Bot comment loops**: SafeGitHubComment filters "[ADW-BOT]" prefix

### R2 Configuration Behavior

- **Partial config (1-3 vars missing)**: Silently disabled, no error
- **All vars present but wrong values**: boto3 connection fails, logged as warning
- **Bucket doesn't exist**: Will fail on upload attempt (not init time)
- **Invalid credentials**: boto3 raises ClientError on upload

### Agent Model Mapping

| Command | Model | Use Case |
|---------|-------|----------|
| `/classify_issue`, `/classify_adw` | sonnet | Lightweight classification |
| `/implement`, `/feature`, `/bug`, `/patch` | opus | Complex implementation |
| `/test`, `/resolve_failed_test` | sonnet | Testing |
| `/review` | opus | Thorough review |
| `/document` | sonnet | Documentation |

### Environment Variables Passed to Agent

```
ANTHROPIC_API_KEY          # Required
GITHUB_PAT / GH_TOKEN      # Optional
CLAUDE_CODE_PATH           # Default: "claude"
CLAUDE_CODE_MAX_OUTPUT_TOKENS
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR
HOME, USER, PATH, SHELL
LANG, LC_ALL, TERM
PYTHONPATH, PYTHONUNBUFFERED
PWD (current working directory)
```

### Setup Checklist

```
[ ] REQUIRED: Copy .env.sample to .env
[ ] REQUIRED: Set ANTHROPIC_API_KEY
[ ] REQUIRED: Set GITHUB_REPO_URL
[ ] REQUIRED: Set CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
[ ] REQUIRED: Verify git remote: git remote -v
[ ] REQUIRED: Install gh CLI: brew install gh
[ ] REQUIRED: Authenticate gh: gh auth login
[ ] REQUIRED: Install Claude Code CLI

[ ] RECOMMENDED: Set GITHUB_PAT (for CI automation)
[ ] RECOMMENDED: Test: claude --version

[ ] OPTIONAL: Configure R2 storage (if handling uploads)
  [ ] CLOUDFLARE_ACCOUNT_ID
  [ ] CLOUDFLARE_R2_ACCESS_KEY_ID
  [ ] CLOUDFLARE_R2_SECRET_ACCESS_KEY
  [ ] CLOUDFLARE_R2_BUCKET_NAME
```

---

## Further Reading

- **Spec Schema**: `docs/SPEC_SCHEMA.md`
- **Validation Rules**: `adws/adw_modules/validators.py`
- **Error Handling**: `adws/adw_modules/exceptions.py`
- **Agent Config**: `adws/adw_modules/agent.py`

