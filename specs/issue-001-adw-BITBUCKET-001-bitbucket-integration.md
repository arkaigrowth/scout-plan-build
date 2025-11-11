# Bitbucket Integration Implementation Plan

**Issue:** #001
**ADW ID:** BITBUCKET-001
**Type:** feature
**Status:** planned
**Created:** 2024-11-09

## Summary

Add native Bitbucket support to the Scout-Plan-Build framework, enabling programmatic PR creation, issue management, and webhook integration for Bitbucket repositories. This parallels the existing GitHub integration.

## Objectives

1. Create Bitbucket API client module (`bitbucket_ops.py`)
2. Add VCS provider detection and abstraction
3. Enable Bitbucket PR creation from ADW workflows
4. Support Bitbucket webhooks for issue-driven automation
5. Maintain backward compatibility with GitHub

## Architecture

### Current State (GitHub-only)
```
workflow_ops.py → github.py → gh CLI
                           → GitHub API
```

### Target State (Multi-VCS)
```
workflow_ops.py → VCS Provider Detection
                ├─→ github.py → gh CLI / GitHub API
                └─→ bitbucket_ops.py → Bitbucket API v2.0
```

## Implementation Plan

### Phase 1: Core Bitbucket Module (Day 1)

**File:** `adws/adw_modules/bitbucket_ops.py` (NEW)

**Functions to implement:**

1. **`get_bitbucket_client()` - Lines 1-25**
   - Initialize Bitbucket API client
   - Load credentials from environment
   - Set base URL: `https://api.bitbucket.org/2.0`

2. **`fetch_issue(workspace, repo, issue_id)` - Lines 27-75**
   - GET `/repositories/{workspace}/{repo}/issues/{issue_id}`
   - Parse response to standard format
   - Handle errors gracefully

3. **`create_pull_request(workspace, repo, title, description, source_branch, dest_branch)` - Lines 77-135**
   - POST `/repositories/{workspace}/{repo}/pullrequests`
   - Request body:
     ```json
     {
       "title": "...",
       "description": "...",
       "source": {"branch": {"name": "feature/xyz"}},
       "destination": {"branch": {"name": "main"}}
     }
     ```
   - Return PR URL

4. **`add_reviewers(workspace, repo, pr_id, reviewers)` - Lines 137-175**
   - PUT `/repositories/{workspace}/{repo}/pullrequests/{pr_id}/default-reviewers`
   - Accept list of usernames/UUIDs

5. **`add_comment(workspace, repo, issue_id, comment)` - Lines 177-210**
   - POST `/repositories/{workspace}/{repo}/issues/{issue_id}/comments`
   - Support markdown formatting

6. **`trigger_pipeline(workspace, repo, branch)` - Lines 212-245**
   - POST `/repositories/{workspace}/{repo}/pipelines/`
   - Trigger build for branch
   - Return pipeline URL

**Environment Variables:**
```bash
BITBUCKET_WORKSPACE="team-workspace"
BITBUCKET_REPO="project-repo"
BITBUCKET_USERNAME="user@example.com"
BITBUCKET_APP_PASSWORD="xxx"  # From Bitbucket settings
```

### Phase 2: VCS Provider Abstraction (Day 1-2)

**File:** `adws/adw_modules/vcs_detection.py` (NEW)

**Functions:**

1. **`detect_vcs_provider()` - Lines 1-40**
   - Check git remote URL
   - Patterns:
     - `github.com` → "github"
     - `bitbucket.org` → "bitbucket"
   - Check `VCS_PROVIDER` env var override
   - Return provider name

2. **`get_repo_info()` - Lines 42-80**
   - Parse remote URL for repo details
   - GitHub: owner/repo
   - Bitbucket: workspace/repo
   - Return normalized dict

**File:** `adws/adw_modules/git_ops.py` (MODIFY)

**Changes:**

1. **`check_pr_exists()` - Lines 80-131 → 80-160**
   - Add VCS detection
   - Route to appropriate provider:
     ```python
     provider = detect_vcs_provider()
     if provider == "github":
         return _check_pr_github(branch)
     elif provider == "bitbucket":
         return _check_pr_bitbucket(branch)
     ```

2. **`finalize_git_operations()` - Lines 256-351 → 256-380**
   - Add provider-specific PR creation
   - Pass repo info to appropriate module

### Phase 3: Workflow Integration (Day 2)

**File:** `adws/adw_modules/workflow_ops.py` (MODIFY)

**Changes:**

1. **`create_pull_request()` - Lines 462-512 → 462-550**
   - Detect VCS provider at start
   - Build provider-specific PR body
   - Call appropriate PR creation function:
     ```python
     if provider == "github":
         result = github.create_pr_via_cli(...)
     elif provider == "bitbucket":
         result = bitbucket_ops.create_pull_request(...)
     ```

2. **New function: `format_pr_body()` - Lines 552-590**
   - Provider-agnostic PR description formatter
   - Support both GitHub and Bitbucket markdown

### Phase 4: Webhook Support (Day 3)

**File:** `adws/adw_triggers/trigger_webhook.py` (MODIFY)

**Changes:**

1. **New endpoint: `/bb-webhook` - Lines 350-450**
   - Handle Bitbucket webhook POST requests
   - Parse event types:
     - `issue:created`
     - `issue:comment_created`
     - `issue:updated`
   - Extract issue details from payload
   - Call appropriate ADW workflow

2. **New function: `verify_bitbucket_signature()` - Lines 452-480**
   - Optional signature verification
   - Use `X-Hook-UUID` header
   - Support custom webhook secrets

### Phase 5: Data Models (Day 3)

**File:** `adws/adw_modules/data_types.py` (MODIFY)

**New models:**

1. **`BitbucketUser` - Lines 125-135**
   ```python
   class BitbucketUser(BaseModel):
       uuid: str
       display_name: str
       account_id: str
   ```

2. **`BitbucketIssue` - Lines 137-160**
   ```python
   class BitbucketIssue(BaseModel):
       id: int
       title: str
       content: dict
       state: str
       reporter: BitbucketUser
   ```

3. **`BitbucketPR` - Lines 162-185**
   ```python
   class BitbucketPR(BaseModel):
       id: int
       title: str
       description: str
       state: str  # OPEN, MERGED, DECLINED
       source: dict
       destination: dict
   ```

## Testing Strategy

### Manual Testing Checklist

1. **PR Creation**
   ```bash
   # Set Bitbucket environment
   export BITBUCKET_WORKSPACE="test-workspace"
   export BITBUCKET_APP_PASSWORD="xxx"

   # Run build with Bitbucket repo
   uv run adws/adw_sdlc.py 1 BITBUCKET-001 --parallel

   # Verify: PR created in Bitbucket
   ```

2. **Webhook Testing**
   ```bash
   # Start webhook server
   uv run adws/adw_triggers/trigger_webhook.py

   # Configure Bitbucket webhook to http://your-server/bb-webhook
   # Create test issue in Bitbucket
   # Verify: ADW workflow triggered
   ```

### Automated Tests

**File:** `tests/test_bitbucket_ops.py` (NEW)

```python
def test_fetch_issue():
    """Test fetching issue from Bitbucket"""
    # Mock API response
    # Call fetch_issue()
    # Assert correct parsing

def test_create_pr():
    """Test PR creation"""
    # Mock API response
    # Call create_pull_request()
    # Assert correct payload

def test_vcs_detection():
    """Test provider detection"""
    # Mock git remote
    # Call detect_vcs_provider()
    # Assert correct provider
```

## Files to Create

1. ✅ `adws/adw_modules/bitbucket_ops.py` (~250 lines)
2. ✅ `adws/adw_modules/vcs_detection.py` (~80 lines)
3. ✅ `tests/test_bitbucket_ops.py` (~150 lines)

## Files to Modify

1. ✅ `adws/adw_modules/git_ops.py` (+30 lines)
2. ✅ `adws/adw_modules/workflow_ops.py` (+40 lines)
3. ✅ `adws/adw_modules/data_types.py` (+60 lines)
4. ✅ `adws/adw_triggers/trigger_webhook.py` (+100 lines)

## Success Criteria

- [ ] Can create PRs in Bitbucket repository
- [ ] VCS provider auto-detected from git remote
- [ ] Bitbucket webhooks trigger ADW workflows
- [ ] All existing GitHub functionality still works
- [ ] Tests pass for both providers
- [ ] Documentation updated with Bitbucket setup

## Risk Assessment

**Medium Risk:**
- Bitbucket API differences might require adjustments
- Authentication flow differs from GitHub
- No CLI tool equivalent to `gh`

**Mitigation:**
- Use official Bitbucket API v2.0 documentation
- Create comprehensive error handling
- Extensive testing with real Bitbucket repository

## Dependencies

- Python `requests` library (already installed)
- Bitbucket account with app password
- Test repository in Bitbucket workspace

## Timeline

- Day 1: Phase 1-2 (Core module + VCS abstraction)
- Day 2: Phase 3 (Workflow integration)
- Day 3: Phase 4-5 (Webhooks + data models)
- Day 4: Testing and documentation

**Total Estimate:** 3-4 days

## Notes

- Maintains backward compatibility with GitHub
- No changes to core Scout/Plan/Build logic
- Provider selection automatic based on git remote
- Can override with `VCS_PROVIDER` env var

---

**Plan Schema Version:** 1.1.0
**Framework Version:** 1.0
**Status:** Ready for implementation