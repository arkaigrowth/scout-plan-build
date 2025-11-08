# MVP Error Handling (Simplified)

## Metadata
```yaml
skill_id: skill-005-mvp
name: mvp-error-handling
version: 0.1.0
effort_estimate: 3 hours
```

## The Problem
Things fail. Need to retry and not crash.

## The Solution
Try/except. Retry 3 times. Log to file. Return something valid.

## Implementation (40 lines)

```python
#!/usr/bin/env python3
"""MVP Error Handling - Just don't crash."""

import time
import json
import traceback
from pathlib import Path

ERROR_LOG = Path(".claude/errors.log")
ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)

def with_retry(func, *args, max_attempts=3, **kwargs):
    """Retry a function with exponential backoff."""
    last_error = None

    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_attempts - 1:
                wait = 2 ** attempt  # 1, 2, 4 seconds
                print(f"Attempt {attempt + 1} failed, retrying in {wait}s...")
                time.sleep(wait)
            else:
                log_error(e)

    # All attempts failed, return safe default
    return get_safe_default(func.__name__)

def log_error(error: Exception):
    """Log error to file."""
    with open(ERROR_LOG, 'a') as f:
        f.write(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"Error: {str(error)}\n")
        f.write(traceback.format_exc())
        f.write("\n")

def get_safe_default(operation: str):
    """Return safe default for operation."""
    defaults = {
        "scout": {"files": [], "error": "Scout failed"},
        "plan": {"spec": "", "error": "Plan failed"},
        "build": {"success": False, "error": "Build failed"},
        "default": {"error": "Operation failed"}
    }
    return defaults.get(operation, defaults["default"])

def safe_operation(operation_name: str):
    """Decorator for safe operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(e)
                print(f"Error in {operation_name}: {e}")
                return get_safe_default(operation_name)
        return wrapper
    return decorator

# Example usage
@safe_operation("scout")
def scout_files(task):
    # This might fail
    result = some_risky_operation()
    return result

def main():
    # Example of retry
    def risky_function():
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Random failure!")
        return "Success!"

    result = with_retry(risky_function)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
```

## Testing

```python
# Test retry succeeds eventually
attempts = []
def fails_twice():
    attempts.append(1)
    if len(attempts) < 3:
        raise Exception("Not yet!")
    return "Success!"

result = with_retry(fails_twice)
assert result == "Success!"
assert len(attempts) == 3

# Test safe default on total failure
def always_fails():
    raise Exception("Always fails!")

result = with_retry(always_fails)
assert "error" in result  # Got safe default

print("✓ Error handling works")
```

## What This Does NOT Include
- ❌ Error categorization
- ❌ Smart recovery strategies
- ❌ Learning from failures
- ❌ Distributed error tracking
- ❌ Error metrics
- ❌ Alert systems

## Time to Build
- Basic retry: 1 hour
- Error logging: 1 hour
- Safe defaults: 1 hour
- **Total: 3 hours**

## Philosophy
```
1. Try the thing
2. If it fails, try again (up to 3x)
3. If still fails, log it
4. Return something valid
5. Never crash
```

That's MVP error handling. Ship it.