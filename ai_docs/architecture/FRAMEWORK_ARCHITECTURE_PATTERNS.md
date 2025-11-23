# Scout Plan Build MVP - Architecture Patterns & Code Deep Dives

**Purpose**: Understand HOW the framework works internally - patterns, flows, and implementation details

---

## PART 1: Natural Language Pipeline - Issue Classification

### The Complete Flow: GitHub Issue → Command Selection

```
GitHub Issue Created
       ↓
  fetch_issue() → GitHubIssue object (number, title, body)
       ↓
  classify_issue() → Claude LLM reasoning
       ↓
  Parsed output: /bug | /feature | /chore | 0
       ↓
  Load appropriate command template
       ↓
  Execute: /bug.md | /feature.md | /chore.md | reject
```

### Stage 1: Issue Fetching (What Data Gets Used)

**File**: `adws/adw_modules/github.py:92-120`

```python
def fetch_issue(issue_number: str, repo_path: str) -> GitHubIssue:
    """Fetch GitHub issue using gh CLI and return typed model."""
    
    # Key insight: Uses structured gh CLI output
    result = subprocess.run(
        ["gh", "issue", "view", issue_number, "--repo", repo_path, "--json", 
         "number,title,body,state,createdAt"],
        capture_output=True,
        text=True,
        env=get_github_env()  # Passes GitHub PAT
    )
    
    return GitHubIssue.model_validate_json(result.stdout)
```

**Why only title + body?**
- Full issue object too large for token budget
- Comments create noise (not needed for classification)
- Minimal payload approach reduces inference cost

### Stage 2: Classification - The LLM Decision Point

**File**: `adws/adw_modules/workflow_ops.py:164-212`

```python
def classify_issue(issue: GitHubIssue, adw_id: str, logger: logging.Logger):
    """Key function that determines issue type"""
    
    # Minimal payload: only number, title, body
    minimal_issue_json = issue.model_dump_json(
        by_alias=True, 
        include={"number", "title", "body"}  # Only these 3 fields
    )
    
    # Create request to /classify_issue command
    request = AgentTemplateRequest(
        agent_name=AGENT_CLASSIFIER,  # "issue_classifier"
        slash_command="/classify_issue",
        args=[minimal_issue_json],  # Pass as JSON string
        adw_id=adw_id,  # For tracking/logging
    )
    
    # Execute via Claude Code CLI
    response = execute_template(request)
    
    # Parse response - look for classification pattern
    # Claude might add explanation, so extract just the command
    classification_match = re.search(r"(/chore|/bug|/feature|0)", output)
    
    if classification_match:
        issue_command = classification_match.group(1)
    else:
        issue_command = output
    
    # Validate classification
    if issue_command == "0":
        return None, f"No command selected: {response.output}"
    
    if issue_command not in ["/chore", "/bug", "/feature"]:
        return None, f"Invalid command selected: {response.output}"
    
    return issue_command, None
```

### Stage 3: Template Loading - Dynamic Command Selection

**File**: `.claude/commands/classify_issue.md`

```markdown
# Github Issue Command Selection

Based on the `Github Issue` below, select the appropriate command.

## Command Mapping
- Respond with `/chore` if the issue is a chore.
- Respond with `/bug` if the issue is a bug.
- Respond with `/feature` if the issue is a feature.
- Respond with `/patch` if the issue is a patch.
- Respond with `0` if the issue isn't any of the above.

## Github Issue
$ARGUMENTS  # This gets replaced with issue JSON
```

**How it works**:
1. User creates GitHub issue with title + body
2. Framework extracts title + body → JSON string
3. Calls `/classify_issue` with that JSON as `$ARGUMENTS`
4. Claude reads the prompt + JSON → determines category
5. Returns one of 5 options

**Example Input**:
```json
{
  "number": 123,
  "title": "Add JWT authentication to API endpoints",
  "body": "Currently the API is unprotected. Need to add JWT-based auth..."
}
```

**Example Output** (Claude's response):
```
Based on the issue description, this is a new feature request.
/feature
```

**Parser extracts**: `/feature` (regex: `r"(/chore|/bug|/feature|0)"`)

---

## PART 2: State Management - How Work Survives Interruptions

### The State Object Pattern

**File**: `adws/adw_modules/state.py`

```python
class ADWState:
    """Persistent state that survives process interruptions"""
    
    def __init__(self, adw_id: str):
        self.adw_id = adw_id
        self.data = {}
        self.file_path = f"agents/{adw_id}/adw_state.json"
    
    @staticmethod
    def load(adw_id: str, logger: Optional[logging.Logger]) -> "ADWState":
        """Load existing state or create new"""
        instance = ADWState(adw_id)
        
        if os.path.exists(instance.file_path):
            with open(instance.file_path, 'r') as f:
                instance.data = json.load(f)
            logger.info(f"Loaded existing state for {adw_id}")
        else:
            instance.data = {}
            logger.info(f"Created new state for {adw_id}")
        
        return instance
    
    def get(self, key: str, default=None):
        """Get value from state"""
        return self.data.get(key, default)
    
    def update(self, **kwargs):
        """Update state and persist to disk"""
        self.data.update(kwargs)
        self.save()
    
    def save(self):
        """Write state to disk"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2)
```

### State Flow Through SDLC Phases

```
Phase 1: Plan
├─ ensure_adw_id() → creates ADWState
├─ state.update(issue_number=123)
├─ state.update(plan_file="specs/...")
└─ save() → agents/abc123/adw_state.json

Phase 2: Build
├─ ADWState.load(adw_id) → reads plan_file from state
├─ Implements plan
├─ state.update(build_report="ai_docs/...")
└─ save()

Phase 3: Test
├─ ADWState.load(adw_id) → knows what was built
├─ Runs tests
├─ state.update(test_results="...")
└─ save()

Phase 4: Review
├─ ADWState.load(adw_id) → knows tests passed/failed
├─ Analyzes code quality
├─ state.update(review="...")
└─ save()

Phase 5: Document
├─ ADWState.load(adw_id) → has full history
├─ Generates documentation
└─ save()
```

**Key insight**: Each phase is independent but all access the same state file
- If Phase 3 (test) fails, Phase 4 (review) can see failure reason
- Can restart from any phase
- No shared memory needed between subprocess calls

---

## PART 3: Parallel Execution - The 40-50% Speedup

### Sequential vs Parallel Execution

**File**: `adws/adw_sdlc.py:30-85`

```python
def run_parallel(issue_number: str, adw_id: str, script_dir: str) -> bool:
    """Execute test/review/document phases in parallel.
    
    Key insight: These 3 phases are INDEPENDENT
    - Don't depend on each other's outputs
    - Only depend on state from Build phase
    - Can write to different output files safely
    """
    
    print("\n=== PARALLEL EXECUTION (Test + Review + Document) ===")
    
    # Start all three as background processes
    # subprocess.Popen() = fire and forget (no wait)
    test_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_test.py"),
        issue_number, adw_id, "--no-commit", "--skip-e2e"
    ])
    
    review_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_review.py"),
        issue_number, adw_id, "--no-commit"
    ])
    
    document_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_document.py"),
        issue_number, adw_id, "--no-commit"
    ])
    
    # Wait for ALL to complete (blocking)
    # This is a barrier - nothing proceeds until all done
    print("Waiting for parallel phases to complete...")
    test_result = test_proc.wait()        # Block until done
    review_result = review_proc.wait()    # Block until done
    document_result = document_proc.wait() # Block until done
    
    # Check if any failed
    if any(r != 0 for r in [test_result, review_result, document_result]):
        print("\n❌ One or more phases failed")
        return False
    
    # All passed - create single aggregated commit
    # This is critical: avoid N commits that could conflict
    print("\n=== Creating aggregated commit ===")
    subprocess.run(["git", "add", "."])
    commit_msg = f"""Parallel execution results for #{issue_number}

- ✅ Tests passed
- ✅ Review completed
- ✅ Documentation updated

ADW ID: {adw_id}
"""
    subprocess.run(["git", "commit", "-m", commit_msg])
    subprocess.run(["git", "push"])
    
    return True
```

### Why This Works (Dependency Analysis)

```
Build outputs files:
- app/server/auth.py (implementation)
- app/tests/test_auth.py (tests)
- Updated requirements.txt

Test reads:
- app/server/auth.py ✓ (can read)
- app/tests/test_auth.py ✓ (can read)
- requirements.txt ✓ (can read)
- BUT doesn't modify them ✓ (SAFE in parallel)

Review reads:
- app/server/auth.py ✓ (can read)
- BUT doesn't modify it ✓ (SAFE in parallel)

Document reads:
- app/server/auth.py ✓ (can read)
- Test results from Test phase ✗ (depends on Test!)
- PROBLEM: Document might start before Test finishes
- SOLUTION: Each writes to own file, no cross-reads
```

**The key**: Each phase writes to **different files**:
- Test → `test_report_123.json`
- Review → `review_report_123.json`
- Document → `documentation_123.md`

No file conflicts = safe to parallelize

### Speedup Calculation

```
Sequential:
Test: 1m
Review: 2m
Document: 1m
Total: 4m

Parallel:
All 3 start at t=0
All finish at t=max(1m, 2m, 1m) = 2m
Total: 2m

Speedup: 4m / 2m = 2x faster (for these 3 phases)
```

**Real-world**: 12 min → 10 min = 17% speedup (not 2x) because Plan + Build are sequential

---

## PART 4: Natural Language Limitations & Why They Exist

### The 4-Pattern Constraint

**Why only 4 types?**

```
Framework design decision:
├─ /feature - Adds new functionality
├─ /bug - Fixes broken functionality  
├─ /chore - Maintains/improves existing
├─ /patch - Quick one-off fix
└─ 0 (unknown) - Doesn't fit above

Why limited to 4?
1. Token efficiency - fewer templates = less context
2. Quality assurance - each template fully tested
3. User UX - clear categories users understand
4. Scalability - adding templates doubles complexity
```

### Examples That DON'T Fit

```
Issue: "Refactor authentication module"
Classification: 0 (unknown)
Why: Doesn't clearly add feature or fix bug
Workaround: "Fix auth security issues"  → /bug
           "Improve auth performance"  → /feature

Issue: "Migrate database to PostgreSQL"  
Classification: 0 (unknown)
Why: Too complex for single category
Workaround: Break into issues:
           Issue 1: "Add PostgreSQL support" → /feature
           Issue 2: "Remove MySQL code" → /chore

Issue: "Update dependencies in package.json"
Classification: /chore
Why: Fits maintenance category
Success: Works as expected
```

### How to Extend (Hypothetically)

To add new issue type `/optimization`:

1. Create `.claude/commands/optimization.md`
2. Add to classify_issue command mapping
3. Update AGENT_CLASSIFIER to recognize it
4. Create tests for new type

**But you wouldn't do this because**:
- Each new type needs its own template + tests
- Classification accuracy decreases with more options
- Users need to learn new categories
- Better: Stretch existing 4 to cover more cases

---

## PART 5: GitHub API Integration - What Actually Happens

### The gh CLI Pattern

**File**: `adws/adw_modules/github.py:44-84`

```python
def get_github_env() -> Optional[dict]:
    """Get environment with GitHub token for subprocess.
    
    Key insight: subprocess.Popen() doesn't inherit parent's environment
    Must explicitly pass env dict with GH_TOKEN
    """
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        return None
    
    # Minimal env - only what gh needs
    env = {
        "GH_TOKEN": github_pat,      # GitHub CLI uses this env var
        "PATH": os.environ.get("PATH", ""),  # gh command needs PATH
    }
    return env


def fetch_issue(issue_number: str, repo_path: str) -> GitHubIssue:
    """Fetch issue from GitHub using gh CLI."""
    
    # Use gh CLI with JSON output
    result = subprocess.run(
        ["gh", "issue", "view", issue_number, 
         "--repo", repo_path, 
         "--json", "number,title,body,state,createdAt"],
        capture_output=True,
        text=True,
        check=True,
        env=get_github_env()  # Pass auth explicitly
    )
    
    # Parse JSON response
    return GitHubIssue.model_validate_json(result.stdout)


def make_issue_comment(issue_number: str, message: str) -> None:
    """Add comment to GitHub issue."""
    
    # Extract repo from git remote
    github_url = get_repo_url()
    repo_path = extract_repo_path(github_url)
    
    # Use gh CLI to comment
    subprocess.run(
        ["gh", "issue", "comment", issue_number,
         "--repo", repo_path,
         "--body", message],
        env=get_github_env(),
        check=True
    )
```

### Why Use gh CLI Instead of Python Library?

```
Option 1: Use pygithub library
├─ Pros: Better Python integration
├─ Cons: Another dependency to manage
├─ Cons: Must handle auth differently
└─ Cons: Error handling less reliable

Option 2: Use gh CLI (chosen)
├─ Pros: Already installed with GitHub Desktop
├─ Pros: Standard across CLI tools
├─ Pros: Works in more environments
├─ Cons: Subprocess overhead
└─ Cons: Must pass auth via env
```

**Framework chose gh CLI because**:
- It's already available on most developer machines
- No new Python dependencies
- Reliable error handling
- Works in CI/CD environments (GitHub Actions)

---

## PART 6: Issue Handling - How Errors Propagate

### Exception Architecture

**File**: `adws/adw_modules/exceptions.py`

```python
class ADWException(Exception):
    """Base exception for all ADW errors"""
    
    def __init__(self, message: str, **context):
        self.message = message
        self.context = context
        super().__init__(message)


class ValidationError(ADWException):
    """Raised when input validation fails"""
    pass


class AgentError(ADWException):
    """Raised when Claude Code agent fails"""
    pass


class GitOperationError(ADWException):
    """Raised when git command fails"""
    pass


class GitHubAPIError(ADWException):
    """Raised when GitHub API call fails"""
    pass
```

### Error Flow Example

```
User runs: uv run adws/adw_plan.py 999 abc

Execution:
1. fetch_issue("999", "owner/repo")
   └─ gh CLI fails: issue not found
   └─ Raises: GitHubAPIError("Issue 999 not found")
   └─ Caught by: main() error handler
   └─ Logs: "Error: Issue not found - check issue number"
   └─ Exits: sys.exit(1)

2. classify_issue(issue, "abc")
   └─ Claude response invalid
   └─ Raises: ValidationError("Invalid classification")
   └─ Caught by: main() error handler
   └─ Logs: "Error: Could not classify issue"
   └─ Exits: sys.exit(1)

3. All succeed
   └─ Creates state file
   └─ Commits plan
   └─ Exits: sys.exit(0)
```

### Key Design: Fail Fast, Log Everything

```python
# Don't try to recover from errors
if not state.get("issue_number"):
    logger.error("Missing issue_number in state")
    raise ValidationError("State corruption detected")
    # Don't try to infer issue_number from file name
    # Don't try to continue without it
    # Just fail loudly

# Log context for debugging
try:
    issue = fetch_issue(issue_number, repo_path)
except GitHubAPIError as e:
    logger.error(
        f"Failed to fetch issue {issue_number}",
        extra={
            "repo_path": repo_path,
            "github_url": github_url,
            "error": str(e)
        }
    )
    raise
```

---

## SUMMARY: Architectural Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **State Machine** | `adw_modules/state.py` | Survives interruptions, no shared memory |
| **Pipeline** | `adw_sdlc.py` | Orchestrate 5 phases sequentially |
| **Template Method** | `.claude/commands/*.md` | Each issue type uses its template |
| **Strategy** | `classify_issue` | Select template based on issue type |
| **Facade** | `workflow_ops.py` | Hide complexity of agent execution |
| **Subprocess Pattern** | `adw_sdlc.py:30-85` | Parallel execution with Popen() |
| **Minimal Payload** | `github.py` | Only send needed data to reduce tokens |
| **Fail Fast** | `exceptions.py` | Stop on error, log context, exit cleanly |

