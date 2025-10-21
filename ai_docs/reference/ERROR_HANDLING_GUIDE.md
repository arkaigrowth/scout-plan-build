# ADW Error Handling Guide

## Overview

The ADW system uses a structured exception hierarchy instead of generic `Exception` catches. This provides:
- Type-safe error handling
- Rich error context for debugging
- Automatic recovery strategies
- GitHub issue integration
- Structured logging

## Exception Hierarchy

```
ADWError (base exception)
├── ValidationError - Input validation failures
├── StateError - State management issues
├── GitOperationError - Git command failures
├── GitHubAPIError - GitHub API/CLI failures
├── AgentError - Claude Code agent failures
├── WorkflowError - Workflow execution failures
├── TokenLimitError - API token limits exceeded
├── RateLimitError - API rate limits hit
├── EnvironmentError - Missing tools/config
└── FileSystemError - File operation failures
```

## Usage Examples

### Basic Error Handling

```python
from adw_modules.exceptions import GitOperationError, ValidationError, handle_error

def my_git_operation(branch_name: str, logger: logging.Logger):
    try:
        # Validate input
        if not branch_name:
            raise ValidationError(
                "Branch name is required",
                field="branch_name"
            )

        # Perform git operation
        result = subprocess.run(
            ["git", "checkout", branch_name],
            capture_output=True,
            text=True,
            check=True
        )

        return True

    except subprocess.CalledProcessError as e:
        # Convert to typed exception
        raise GitOperationError(
            f"Failed to checkout branch {branch_name}",
            command=f"git checkout {branch_name}",
            returncode=e.returncode,
            stderr=e.stderr,
            branch_name=branch_name
        ) from e

    except ValidationError:
        # Re-raise validation errors
        raise

    except Exception as e:
        # Catch unexpected errors
        raise WorkflowError(
            "Unexpected error in git operation",
            operation="checkout",
            branch=branch_name
        ) from e
```

### Error Context

All exceptions carry context:

```python
try:
    validate_issue_number(issue_num)
except ValidationError as e:
    # Access error details
    print(e.message)              # Human-readable message
    print(e.context)              # Dict with field, expected_type, etc.
    print(e.correlation_id)       # Optional tracking ID
    print(e.timestamp)            # When error occurred
    print(e.to_dict())            # Full serialization
```

### Centralized Error Handler

```python
from adw_modules.exceptions import handle_error, get_recovery_strategy

try:
    perform_workflow_step()
except ADWError as e:
    # Centralized handling
    error_info = handle_error(
        error=e,
        logger=logger,
        issue_number=issue_number,
        adw_id=adw_id
    )

    # Get recovery guidance
    recovery = get_recovery_strategy(e)
    logger.info(f"Recovery: {recovery}")

    # Decide whether to continue or fail
    if error_info["recoverable"]:
        # Implement retry logic
        retry_operation()
    else:
        # Fail and exit
        sys.exit(1)
```

### Specific Exception Types

#### ValidationError

```python
from adw_modules.exceptions import ValidationError

# Field validation
if not issue_number.isdigit():
    raise ValidationError(
        "Issue number must be numeric",
        field="issue_number",
        actual_value=issue_number,
        expected_type="integer"
    )

# Schema validation
try:
    data = parse_json(response.output, dict)
except ValueError as e:
    raise ValidationError(
        "Failed to parse response",
        field="response_output",
        parse_error=str(e),
        response=response.output
    ) from e
```

#### GitOperationError

```python
from adw_modules.exceptions import GitOperationError

try:
    result = subprocess.run(
        ["git", "push", "-u", "origin", branch_name],
        capture_output=True,
        text=True,
        check=True
    )
except subprocess.CalledProcessError as e:
    raise GitOperationError(
        f"Failed to push branch {branch_name}",
        command=f"git push -u origin {branch_name}",
        returncode=e.returncode,
        stderr=e.stderr,
        branch_name=branch_name
    ) from e
```

#### AgentError

```python
from adw_modules.exceptions import AgentError

response = execute_template(request)
if not response.success:
    raise AgentError(
        "Agent execution failed",
        agent_name=request.agent_name,
        slash_command=request.slash_command,
        session_id=response.session_id,
        output=response.output
    )
```

#### TokenLimitError

```python
from adw_modules.exceptions import TokenLimitError

# Automatic detection in agent.py
if "token" in result_text.lower() and "limit" in result_text.lower():
    raise TokenLimitError(
        "Agent hit token limit during execution",
        agent_name=request.agent_name,
        session_id=session_id,
        result=result_text
    )

# Manual detection
if input_size > MAX_TOKENS:
    raise TokenLimitError(
        "Input exceeds token limit",
        tokens_requested=input_size,
        tokens_available=MAX_TOKENS,
        model=model_name
    )
```

#### StateError

```python
from adw_modules.exceptions import StateError

# State validation failure
try:
    state_data = ADWStateData(**data)
except Exception as e:
    raise StateError(
        "State validation failed",
        adw_id=adw_id,
        validation_error=str(e),
        state_data=data
    ) from e

# Missing required state
if not state.get("plan_file"):
    raise StateError(
        "Plan file not found in state",
        adw_id=adw_id,
        required_field="plan_file",
        instruction="Run adw_plan.py first"
    )
```

#### FileSystemError

```python
from adw_modules.exceptions import FileSystemError

try:
    os.makedirs(output_dir, exist_ok=True)
except OSError as e:
    raise FileSystemError(
        f"Failed to create directory: {output_dir}",
        path=output_dir,
        operation="mkdir",
        error=str(e)
    ) from e
```

## Recovery Strategies

### GitOperationError Recovery

```python
try:
    push_branch(branch_name)
except GitOperationError as e:
    logger.error(f"Push failed: {e.message}")
    recovery = get_recovery_strategy(e)
    # "Run 'git status' to check repository state..."

    # Attempt recovery
    subprocess.run(["git", "status"], check=True)
    # Optionally: git reset --hard
```

### TokenLimitError Recovery

```python
try:
    process_large_input(data)
except TokenLimitError as e:
    logger.warning(f"Token limit hit: {e.message}")
    recovery = get_recovery_strategy(e)
    # "Reduce input size or chunk operation..."

    # Chunk the operation
    chunks = chunk_data(data, size=e.context["tokens_available"])
    for chunk in chunks:
        process_large_input(chunk)
```

### AgentError Recovery

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        response = execute_template(request)
        break
    except AgentError as e:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Agent failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
        else:
            logger.error("Agent failed after all retries")
            handle_error(e, logger, issue_number, adw_id)
            raise
```

## Best Practices

### 1. Always Use Specific Exceptions

```python
# ❌ BAD
try:
    git_operation()
except Exception as e:
    logger.error(f"Error: {e}")

# ✅ GOOD
try:
    git_operation()
except GitOperationError as e:
    logger.error(f"Git failed: {e.message}", extra=e.to_dict())
    handle_error(e, logger, issue_number, adw_id)
except ValidationError as e:
    logger.error(f"Validation failed: {e.message}")
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise WorkflowError("Operation failed") from e
```

### 2. Preserve Error Chains

```python
# ✅ GOOD - Preserves original exception
try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    raise GitOperationError(
        "Git command failed",
        command=cmd,
        returncode=e.returncode
    ) from e  # ← Preserves stack trace
```

### 3. Add Rich Context

```python
# ✅ GOOD - Rich context for debugging
raise ValidationError(
    "Invalid branch name format",
    field="branch_name",
    actual_value=branch_name,
    expected_pattern=r"^[a-zA-Z0-9/_-]+$",
    adw_id=adw_id,
    issue_number=issue_number
)
```

### 4. Use handle_error() for Consistency

```python
# ✅ GOOD - Consistent error handling
try:
    workflow_step()
except ADWError as e:
    error_info = handle_error(e, logger, issue_number, adw_id)
    if not error_info["recoverable"]:
        sys.exit(1)
```

### 5. Document Exceptions in Docstrings

```python
def create_branch(branch_name: str) -> Tuple[bool, Optional[str]]:
    """Create and checkout a new branch.

    Args:
        branch_name: Name of branch to create

    Returns:
        Tuple of (success, error_message)

    Raises:
        ValidationError: If branch name is invalid
        GitOperationError: If git command fails
    """
```

## Migration Guide

### Converting Existing Code

**Step 1**: Import exceptions
```python
from adw_modules.exceptions import (
    GitOperationError,
    ValidationError,
    WorkflowError,
    handle_error
)
```

**Step 2**: Replace generic catches
```python
# Before
try:
    operation()
except Exception as e:
    logger.error(f"Error: {e}")

# After
try:
    operation()
except GitOperationError as e:
    handle_error(e, logger, issue_number, adw_id)
    raise
```

**Step 3**: Add validation
```python
# Before
def process(data):
    # Direct processing

# After
def process(data):
    if not data:
        raise ValidationError("Data is required", field="data")
    # Processing
```

## Error Logging

### Structured Logging

```python
import logging

logger = logging.getLogger(__name__)

try:
    operation()
except ADWError as e:
    # Structured log with context
    logger.error(
        f"{e.__class__.__name__}: {e.message}",
        extra={
            "error_type": e.__class__.__name__,
            "context": e.context,
            "correlation_id": e.correlation_id,
            "timestamp": e.timestamp.isoformat()
        }
    )
```

### GitHub Integration

```python
# Automatic posting to GitHub issues
try:
    workflow_step()
except ADWError as e:
    # handle_error posts to GitHub automatically
    error_info = handle_error(
        error=e,
        logger=logger,
        issue_number=issue_number,  # Required for GitHub posting
        adw_id=adw_id                # Required for GitHub posting
    )
```

## Testing

### Testing Exception Handling

```python
import pytest
from adw_modules.exceptions import ValidationError

def test_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        validate_input("")

    error = exc_info.value
    assert error.message == "Input is required"
    assert error.context["field"] == "input"
    assert "timestamp" in error.to_dict()
```

### Mocking Error Handlers

```python
from unittest.mock import patch

def test_error_handling():
    with patch('adw_modules.exceptions.handle_error') as mock_handler:
        try:
            failing_operation()
        except ADWError as e:
            handle_error(e, logger, "123", "test-id")

        mock_handler.assert_called_once()
        call_args = mock_handler.call_args
        assert isinstance(call_args[0][0], ADWError)
```

## FAQ

**Q: When should I use handle_error() vs direct logging?**

A: Use `handle_error()` for all ADWError exceptions in workflow operations that have an associated GitHub issue. It provides consistent logging, GitHub posting, and recovery guidance.

**Q: Should all functions raise exceptions or return (success, error)?**

A: Core validation and agent operations should raise exceptions. Git/GitHub operations may return tuples for backward compatibility. New code should prefer exceptions.

**Q: How do I add a new exception type?**

A:
1. Add class to `exceptions.py` inheriting from `ADWError`
2. Add recovery strategy to `get_recovery_strategy()`
3. Import and use in relevant modules
4. Update this guide with examples

**Q: What about backward compatibility?**

A: Functions that previously returned None on error (like `ADWState.load()`) maintain that behavior. New code uses exceptions.

**Q: How do I handle transient vs permanent errors?**

A: Check `error_info["recoverable"]` from `handle_error()`. Implement retry logic for recoverable errors with exponential backoff.

---

**See Also**:
- `/adws/adw_modules/exceptions.py` - Exception definitions
- `/ai_docs/build_reports/structured-error-handling-build-report.md` - Implementation details
- `/adws/adw_modules/workflow_ops.py` - Example usage in workflows
