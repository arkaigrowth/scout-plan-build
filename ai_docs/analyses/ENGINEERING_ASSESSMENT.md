# 🎯 Scout Plan Build MVP - Engineering Assessment

*Senior AI Dev Analysis | 2025-01-20 | Brutal bias for shipping*

## Executive Summary

**🟡 Current State: Early MVP with solid foundation but needs hardening**

The repository implements a functional **Agentic Development Workflow (ADW)** system that successfully chains GitHub issues → Plans → Implementation → PRs. Core architecture is sound, but significant gaps exist in type safety, error handling, and production readiness.

**Key Verdict**: Ship-ready for internal use, needs 2-3 weeks of hardening for production.

---

## 🏗️ Architecture Assessment

### ✅ What's Working Well

1. **Clean Separation of Concerns**
   - Modular design with clear boundaries (workflow_ops, state, git_ops, github)
   - Each module has single responsibility
   - Composable pipeline pattern (plan → build → test → review)

2. **State Management**
   - ADWState pattern provides good workflow persistence
   - JSON-based state files enable session recovery
   - Isolated workspaces per ADW ID prevent conflicts

3. **Safety Mechanisms**
   - No `shell=True` in subprocess calls (good security practice)
   - Git safety checks (`git diff --stat` → `git reset --hard`)
   - Environment variable usage for secrets

### ⚠️ Critical Gaps

1. **Type Safety (60% coverage)**
   ```python
   # Current state - many untyped functions
   def build_plan(issue_data, adw_id, logger):  # No type hints!

   # Should be:
   def build_plan(
       issue_data: GitHubIssue,
       adw_id: str,
       logger: logging.Logger
   ) -> Tuple[bool, str]:
   ```

2. **Error Handling**
   ```python
   # Current: Generic exceptions mask issues
   except Exception as e:
       logger.error(f"Error: {e}")

   # Needed: Structured error types
   class ADWError(Exception): pass
   class ValidationError(ADWError): pass
   class GitOperationError(ADWError): pass
   ```

3. **No Input Validation**
   ```python
   # Current: Direct subprocess with user input
   subprocess.run(['git', 'commit', '-m', user_message])

   # Needed: Sanitization
   import shlex
   safe_message = shlex.quote(user_message)
   ```

---

## 🔧 Engineering Best Practices Audit

### ✅ Present

- **Atomic Commits**: Each operation = separate commit
- **Validation Gates**: Check requirements before proceeding
- **Timeout Limits**: 3-minute subagent, 5-minute Claude Code
- **Structured Output**: JSON for data, Markdown for docs
- **Environment Variables**: No hardcoded secrets

### ❌ Missing

- **Rate Limiting**: No protection against API abuse
- **Retry Logic**: Single attempt, no exponential backoff
- **Caching**: Repeated expensive operations
- **Parallelization**: Sequential execution only
- **Monitoring**: No metrics, traces, or alerts
- **Circuit Breakers**: No failure isolation

---

## 🆔 Slug Generation Analysis

### Current Implementation
```python
# ADW ID: Simple random generation
adw_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
# Example: "a3f7k9m2"

# Branch naming
branch = f"feature/issue-{issue_number}-adw-{adw_id}"
# Example: "feature/issue-42-adw-a3f7k9m2"

# Slugification
def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
# "Fix Auth Bug!" → "fix-auth-bug"
```

### ⚠️ Issues
- No collision detection for ADW IDs
- No semantic meaning in IDs
- Branch names can exceed Git limits (255 chars)

### 💡 Recommendation
```python
# Better: Semantic + unique
adw_id = f"{issue_number[:4]}-{timestamp[:4]}-{random[:4]}"
# Example: "0042-1220-k9m2"
```

---

## 🛡️ Security & Failsafes

### ✅ Good Security Practices

1. **No shell=True**: Prevents command injection
2. **Environment Variables**: Secrets not in code
3. **Git Hooks**: Block dangerous operations
4. **Pydantic Validation**: Input type checking (where used)

### 🚨 Security Gaps

1. **No Input Sanitization**
   ```python
   # Vulnerable to path traversal
   plan_file = f"specs/{user_input}.md"

   # Fix:
   safe_input = os.path.basename(user_input)
   plan_file = os.path.join("specs", f"{safe_input}.md")
   ```

2. **No Rate Limiting**
   ```python
   # Add rate limiting
   from functools import wraps
   from time import time, sleep

   def rate_limit(calls_per_minute=10):
       # Implementation
   ```

3. **Insufficient Error Information Hiding**
   - Stack traces exposed to users
   - Internal paths in error messages

---

## 🤖 Agents SDK Integration

### Current Pattern
```python
# Agent invocation via Claude Code CLI
def prompt_claude_code(request: AgentPromptRequest) -> AgentPromptResponse:
    cmd = [
        CLAUDE_PATH,
        "prompt",
        request.prompt,
        "--model", request.model,
        "--output", request.output_file
    ]
    result = subprocess.run(cmd, capture_output=True)
```

### Gaps
1. **No Agent State Management**: Each invocation is stateless
2. **No Agent Coordination**: Can't run multiple agents in parallel
3. **No Agent Memory**: No context preservation between calls
4. **Basic Error Handling**: Subprocess failures not gracefully handled

### Recommendation: Basic Agent Loop
```python
class AgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.state = {}

    async def run_agent(self, agent_name: str, task: str):
        """Basic agent execution loop"""
        while not task.is_complete():
            response = await self.execute_agent(agent_name, task)
            self.state[agent_name] = response
            task = self.evaluate_progress(task, response)
        return self.state
```

---

## 📦 Pydantic Strategy

### Current Usage (Limited)
- ✅ `data_types.py`: 22 models for GitHub/Agent data
- ✅ Type validation for API responses
- ❌ Missing in core workflow functions
- ❌ No validation for file paths, commands, user input

### Where to Add Pydantic (Priority Order)

1. **User Input Validation** (CRITICAL)
   ```python
   class UserPrompt(BaseModel):
       text: str = Field(max_length=5000)
       docs_urls: List[HttpUrl] = []

       @validator('text')
       def sanitize_text(cls, v):
           return shlex.quote(v)
   ```

2. **File Operations** (HIGH)
   ```python
   class FileOperation(BaseModel):
       path: Path
       operation: Literal["read", "write", "delete"]

       @validator('path')
       def validate_path(cls, v):
           if ".." in str(v):
               raise ValueError("Path traversal detected")
           return v
   ```

3. **Workflow State** (MEDIUM)
   ```python
   class WorkflowState(BaseModel):
       phase: Literal["plan", "build", "test", "review"]
       status: Literal["pending", "running", "success", "failed"]
       started_at: datetime
       completed_at: Optional[datetime]
   ```

---

## 🚀 Ship-Ready Checklist

### 🔥 Must Fix Before Production (1 week)

- [ ] Add input sanitization for all user inputs
- [ ] Implement structured error types
- [ ] Add Pydantic validation to workflow_ops.py
- [ ] Create integration test suite
- [ ] Add rate limiting to API calls
- [ ] Implement retry logic with exponential backoff

### 💪 Should Have (2nd week)

- [ ] Parallelize independent operations
- [ ] Add caching layer for expensive operations
- [ ] Implement comprehensive logging
- [ ] Create health check endpoints
- [ ] Add metrics collection
- [ ] Document API contracts

### 🎯 Nice to Have (3rd week)

- [ ] Move to async/await pattern
- [ ] Implement circuit breakers
- [ ] Add observability (traces)
- [ ] Create plugin architecture
- [ ] Build admin dashboard

---

## 💊 Fat to Trim (Brutal Bias for Shipping)

### Remove/Defer

1. **Over-engineered test files**: 1088 lines in adw_test.py → Split or simplify
2. **Duplicate commands**: scout.md vs scout_improved.md → Pick one
3. **ARCHIVE_OLD directory**: Remove or move to separate repo
4. **Unused triggers**: If webhooks not used, remove trigger_webhook.py

### Simplify

```python
# Current: 8 orchestrator variants
adw_plan.py, adw_build.py, adw_plan_build.py, adw_plan_build_test.py...

# Better: Single configurable pipeline
class Pipeline:
    def run(self, phases: List[str]):
        # Dynamic phase execution
```

---

## 🎯 Final Recommendations

### Immediate Actions (Ship This Week)

1. **Add This Validation Layer**
   ```python
   # validators.py
   from pydantic import BaseModel, validator

   class SafeInput(BaseModel):
       user_prompt: str
       file_path: Optional[Path]

       @validator('file_path')
       def safe_path(cls, v):
           if v and '..' in str(v):
               raise ValueError("Invalid path")
           return v
   ```

2. **Implement Basic Retry**
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential

   @retry(stop=stop_after_attempt(3), wait=wait_exponential())
   def api_call():
       # Your API call
   ```

3. **Add Security Headers**
   ```python
   # For any web endpoints
   headers = {
       "X-Content-Type-Options": "nosniff",
       "X-Frame-Options": "DENY",
       "Content-Security-Policy": "default-src 'self'"
   }
   ```

### Architecture Evolution Path

```
Current: Synchronous Pipeline
Phase 1: Add validation + error handling (1 week)
Phase 2: Parallelize + cache (2 weeks)
Phase 3: Async + observability (1 month)
Phase 4: Plugin architecture (2 months)
```

---

## 🏁 Bottom Line

**Ship it with Phase 1 fixes**. The core architecture is solid, and the ADW pattern works. Focus on:

1. **Input validation** (Pydantic everywhere)
2. **Error handling** (structured exceptions)
3. **Basic security** (sanitization, rate limiting)

This gets you to production-ready for internal use. Iterate from there based on real usage.

**Remember**: Perfect is the enemy of shipped. This codebase is 70% there - one sprint of focused hardening makes it 90% production-ready.

---

*Analysis complete. Ready to ship with recommended fixes.*