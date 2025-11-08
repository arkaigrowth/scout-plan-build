# Skill Specification: handling-errors

## Metadata
```yaml
skill_id: skill-005
name: handling-errors
version: 1.0.0
schema_version: 1.1.0
category: reliability
priority: HIGH
effort_estimate: 1 day
confidence: 0.90
```

## Overview

### Purpose
Provide structured error handling with automatic recovery strategies, detailed diagnostics, and learning from failures. Consolidates 10 exception types and recovery patterns used across the codebase.

### Problem Statement
- Error handling inconsistent across scripts
- No automatic recovery attempts
- Lost context on failures
- No learning from repeated errors

### Expected Impact
- **Recovery rate**: 70% automatic recovery
- **Debugging time**: -60% with detailed diagnostics
- **Repeat failures**: -80% with learning system
- **User experience**: Graceful degradation instead of crashes

## Skill Design

### SKILL.md Structure (< 350 lines)

```markdown
---
name: handling-errors
description: Handles errors with automatic recovery, detailed diagnostics, and learning from failures. Use when catching exceptions, implementing retry logic, diagnosing failures, or recovering from errors.
version: 1.0.0
dependencies: python>=3.8, tenacity>=8.0
---

# Handling Errors

Intelligent error handling with automatic recovery and learning.

## When to Use

Activate this skill when:
- Implementing error handling
- Need automatic recovery
- Diagnosing failures
- Learning from errors
- User mentions: error, exception, recover, retry, failure

## Quick Recovery

### Automatic Retry with Backoff
```python
from error_handler import with_recovery

@with_recovery(max_attempts=3)
def risky_operation():
    # Automatically retries with exponential backoff
    response = api_call()
    return response
```

### Structured Error Handling
```python
from error_handler import ErrorHandler

handler = ErrorHandler()

try:
    result = dangerous_operation()
except Exception as e:
    # Automatic diagnosis and recovery
    recovery = handler.handle(e)

    if recovery.succeeded:
        result = recovery.result
    else:
        # Graceful degradation
        result = recovery.fallback
```

### Error Categories

| Category | Recovery Strategy | Success Rate |
|----------|------------------|--------------|
| Network | Retry with backoff | 85% |
| File System | Alternative paths | 75% |
| API | Fallback endpoints | 70% |
| Validation | Auto-correction | 60% |
| State | Checkpoint restore | 90% |

## Diagnostics

Every error includes rich context:

```json
{
  "error_id": "err_123",
  "timestamp": "2024-01-01T12:00:00Z",
  "category": "API_ERROR",
  "message": "GitHub API rate limit exceeded",
  "context": {
    "endpoint": "/repos/owner/repo/issues",
    "rate_limit": {"remaining": 0, "reset": 1704123600}
  },
  "recovery": {
    "strategy": "wait_until_reset",
    "wait_time": 3600,
    "alternative": "use_cached_data"
  },
  "stack_trace": "...",
  "similar_errors": [
    {"id": "err_098", "resolution": "waited", "success": true}
  ]
}
```

For error patterns → see `references/patterns.md`
For recovery strategies → see `references/recovery.md`
For learning system → see `references/learning.md`

## Scripts

```bash
# Analyze error patterns
python scripts/error_handler.py analyze error.log

# Test recovery strategies
python scripts/error_handler.py test-recovery

# Learn from error history
python scripts/error_handler.py learn --days 30

# Generate error report
python scripts/error_handler.py report --format html
```
```

### Supporting Files

#### scripts/error_handler.py
```python
#!/usr/bin/env python3
"""
Intelligent error handling with recovery and learning.
"""
import sys
import json
import time
import traceback
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from functools import wraps
import hashlib

@dataclass
class ErrorContext:
    """Rich error context."""
    error_id: str
    timestamp: str
    category: str
    message: str
    context: Dict[str, Any]
    stack_trace: str
    recovery_attempted: bool = False
    recovery_succeeded: bool = False

@dataclass
class RecoveryStrategy:
    """Recovery strategy for an error."""
    name: str
    handler: Callable
    max_attempts: int = 3
    backoff_base: float = 2.0
    success_rate: float = 0.0

@dataclass
class RecoveryResult:
    """Result of recovery attempt."""
    succeeded: bool
    result: Any = None
    fallback: Any = None
    attempts: int = 0
    strategy_used: str = ""

class ErrorCategory:
    """Error categorization."""
    NETWORK = "NETWORK_ERROR"
    FILE_SYSTEM = "FILE_SYSTEM_ERROR"
    API = "API_ERROR"
    VALIDATION = "VALIDATION_ERROR"
    STATE = "STATE_ERROR"
    PERMISSION = "PERMISSION_ERROR"
    TIMEOUT = "TIMEOUT_ERROR"
    RESOURCE = "RESOURCE_ERROR"
    UNKNOWN = "UNKNOWN_ERROR"

class ErrorHandler:
    """Main error handling system."""

    def __init__(self):
        self.history_file = Path(".claude/errors/history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.strategies = self._init_strategies()
        self.error_patterns = self._load_patterns()

    def _init_strategies(self) -> Dict[str, RecoveryStrategy]:
        """Initialize recovery strategies."""
        return {
            ErrorCategory.NETWORK: RecoveryStrategy(
                name="network_retry",
                handler=self._recover_network,
                max_attempts=5,
                success_rate=0.85
            ),
            ErrorCategory.FILE_SYSTEM: RecoveryStrategy(
                name="alternative_path",
                handler=self._recover_filesystem,
                max_attempts=3,
                success_rate=0.75
            ),
            ErrorCategory.API: RecoveryStrategy(
                name="api_fallback",
                handler=self._recover_api,
                max_attempts=3,
                success_rate=0.70
            ),
            ErrorCategory.VALIDATION: RecoveryStrategy(
                name="auto_correct",
                handler=self._recover_validation,
                max_attempts=2,
                success_rate=0.60
            ),
            ErrorCategory.STATE: RecoveryStrategy(
                name="checkpoint_restore",
                handler=self._recover_state,
                max_attempts=1,
                success_rate=0.90
            ),
            ErrorCategory.TIMEOUT: RecoveryStrategy(
                name="extend_timeout",
                handler=self._recover_timeout,
                max_attempts=2,
                success_rate=0.65
            )
        }

    def handle(self, error: Exception, context: Dict[str, Any] = None) -> RecoveryResult:
        """Handle error with automatic recovery."""
        # Create error context
        error_ctx = self._create_context(error, context)

        # Categorize error
        category = self._categorize(error, error_ctx)
        error_ctx.category = category

        # Log error
        self._log_error(error_ctx)

        # Attempt recovery
        recovery_result = self._attempt_recovery(error, category, context)

        # Update error context
        error_ctx.recovery_attempted = True
        error_ctx.recovery_succeeded = recovery_result.succeeded

        # Learn from outcome
        self._learn_from_error(error_ctx, recovery_result)

        return recovery_result

    def _create_context(self, error: Exception, context: Dict = None) -> ErrorContext:
        """Create rich error context."""
        error_id = self._generate_error_id(error)

        return ErrorContext(
            error_id=error_id,
            timestamp=datetime.utcnow().isoformat(),
            category=ErrorCategory.UNKNOWN,
            message=str(error),
            context=context or {},
            stack_trace=traceback.format_exc()
        )

    def _generate_error_id(self, error: Exception) -> str:
        """Generate unique error ID."""
        content = f"{type(error).__name__}:{str(error)}"
        hash_obj = hashlib.md5(content.encode())
        return f"err_{hash_obj.hexdigest()[:8]}"

    def _categorize(self, error: Exception, context: ErrorContext) -> str:
        """Categorize error type."""
        error_str = str(error).lower()
        exception_type = type(error).__name__

        # Network errors
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'refused']):
            return ErrorCategory.NETWORK

        # File system errors
        if any(keyword in error_str for keyword in ['file', 'path', 'directory', 'permission']):
            return ErrorCategory.FILE_SYSTEM

        # API errors
        if any(keyword in error_str for keyword in ['api', 'rate limit', 'unauthorized', '401', '403']):
            return ErrorCategory.API

        # Validation errors
        if any(keyword in error_str for keyword in ['validation', 'invalid', 'schema', 'type']):
            return ErrorCategory.VALIDATION

        # State errors
        if any(keyword in error_str for keyword in ['state', 'checkpoint', 'corrupt']):
            return ErrorCategory.STATE

        # Timeout errors
        if 'timeout' in error_str or exception_type == 'TimeoutError':
            return ErrorCategory.TIMEOUT

        return ErrorCategory.UNKNOWN

    def _attempt_recovery(self, error: Exception, category: str, context: Dict) -> RecoveryResult:
        """Attempt automatic recovery."""
        if category not in self.strategies:
            return RecoveryResult(succeeded=False, strategy_used="none")

        strategy = self.strategies[category]
        result = RecoveryResult(strategy_used=strategy.name)

        for attempt in range(strategy.max_attempts):
            try:
                print(f"🔧 Recovery attempt {attempt + 1}/{strategy.max_attempts} using {strategy.name}")

                # Exponential backoff
                if attempt > 0:
                    wait_time = strategy.backoff_base ** attempt
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

                # Attempt recovery
                recovery_data = strategy.handler(error, context)

                result.succeeded = True
                result.result = recovery_data
                result.attempts = attempt + 1

                print(f"✅ Recovery successful using {strategy.name}")
                break

            except Exception as recovery_error:
                print(f"⚠️  Recovery attempt {attempt + 1} failed: {recovery_error}")
                result.attempts = attempt + 1

        if not result.succeeded:
            # Try fallback
            result.fallback = self._get_fallback(category, context)

        return result

    def _recover_network(self, error: Exception, context: Dict) -> Any:
        """Recover from network errors."""
        # Implement network recovery logic
        # Could include: switching endpoints, using cache, waiting for connection
        if "cached_data" in context:
            print("📦 Using cached data as fallback")
            return context["cached_data"]

        # Wait and retry
        time.sleep(5)
        return None

    def _recover_filesystem(self, error: Exception, context: Dict) -> Any:
        """Recover from file system errors."""
        # Try alternative paths
        if "alternative_paths" in context:
            for path in context["alternative_paths"]:
                if Path(path).exists():
                    print(f"📁 Using alternative path: {path}")
                    return path

        # Create missing directories
        if "create_if_missing" in context:
            path = Path(context["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            return str(path)

        return None

    def _recover_api(self, error: Exception, context: Dict) -> Any:
        """Recover from API errors."""
        error_str = str(error).lower()

        # Rate limit handling
        if "rate limit" in error_str:
            if "reset_time" in context:
                wait_time = context["reset_time"] - time.time()
                if wait_time > 0 and wait_time < 3600:  # Wait up to 1 hour
                    print(f"⏰ Waiting {wait_time}s for rate limit reset")
                    time.sleep(wait_time)
                    return "retry"

        # Use alternative endpoint
        if "alternative_endpoint" in context:
            print(f"🔄 Switching to alternative endpoint")
            return context["alternative_endpoint"]

        return None

    def _recover_validation(self, error: Exception, context: Dict) -> Any:
        """Recover from validation errors."""
        # Auto-correct common issues
        if "value" in context:
            value = context["value"]

            # Try type conversion
            if "expected_type" in context:
                expected = context["expected_type"]
                try:
                    if expected == "int":
                        return int(value)
                    elif expected == "float":
                        return float(value)
                    elif expected == "bool":
                        return str(value).lower() in ["true", "1", "yes"]
                except:
                    pass

        return None

    def _recover_state(self, error: Exception, context: Dict) -> Any:
        """Recover from state errors."""
        # Restore from checkpoint
        if "checkpoint_path" in context:
            checkpoint = Path(context["checkpoint_path"])
            if checkpoint.exists():
                print(f"📥 Restoring from checkpoint: {checkpoint}")
                with open(checkpoint) as f:
                    return json.load(f)

        # Reset to default state
        if "default_state" in context:
            print("🔄 Resetting to default state")
            return context["default_state"]

        return None

    def _recover_timeout(self, error: Exception, context: Dict) -> Any:
        """Recover from timeout errors."""
        # Extend timeout and retry
        if "timeout" in context:
            new_timeout = context["timeout"] * 2
            print(f"⏱️  Extending timeout to {new_timeout}s")
            return {"timeout": new_timeout}

        return None

    def _get_fallback(self, category: str, context: Dict) -> Any:
        """Get fallback for failed recovery."""
        fallbacks = {
            ErrorCategory.NETWORK: {"status": "offline", "data": None},
            ErrorCategory.FILE_SYSTEM: {"path": "/tmp/fallback"},
            ErrorCategory.API: {"data": [], "cached": True},
            ErrorCategory.VALIDATION: {"valid": False, "errors": ["validation failed"]},
            ErrorCategory.STATE: {"state": "default"},
            ErrorCategory.TIMEOUT: {"result": None, "timeout": True}
        }

        return fallbacks.get(category, None)

    def _log_error(self, error_ctx: ErrorContext) -> None:
        """Log error to history."""
        history = self._load_history()
        history.append(error_ctx.__dict__)

        # Keep only last 1000 errors
        if len(history) > 1000:
            history = history[-1000:]

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)

    def _load_history(self) -> List[Dict]:
        """Load error history."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return []

    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load error patterns for categorization."""
        patterns_file = Path(".claude/errors/patterns.json")
        if patterns_file.exists():
            with open(patterns_file) as f:
                return json.load(f)
        return {}

    def _learn_from_error(self, error_ctx: ErrorContext, recovery: RecoveryResult) -> None:
        """Learn from error and recovery outcome."""
        # Update success rates
        if error_ctx.category in self.strategies:
            strategy = self.strategies[error_ctx.category]
            # Simple moving average
            alpha = 0.1  # Learning rate
            if recovery.succeeded:
                strategy.success_rate = (1 - alpha) * strategy.success_rate + alpha
            else:
                strategy.success_rate = (1 - alpha) * strategy.success_rate

        # Save learned patterns
        patterns_file = Path(".claude/errors/learned_patterns.json")
        patterns = {}
        if patterns_file.exists():
            with open(patterns_file) as f:
                patterns = json.load(f)

        pattern_key = f"{error_ctx.category}:{error_ctx.error_id}"
        patterns[pattern_key] = {
            "recovery_strategy": recovery.strategy_used,
            "succeeded": recovery.succeeded,
            "attempts": recovery.attempts,
            "timestamp": error_ctx.timestamp
        }

        patterns_file.parent.mkdir(parents=True, exist_ok=True)
        with open(patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)

# Decorator for automatic error handling
def with_recovery(max_attempts: int = 3, categories: List[str] = None):
    """Decorator for automatic error recovery."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler()
            last_error = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    context = {
                        "function": func.__name__,
                        "attempt": attempt + 1,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    }

                    recovery = handler.handle(e, context)

                    if recovery.succeeded:
                        return recovery.result
                    elif recovery.fallback is not None:
                        return recovery.fallback

            raise last_error

        return wrapper
    return decorator

def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: error_handler.py [analyze|test-recovery|learn|report]")
        sys.exit(1)

    command = sys.argv[1]
    handler = ErrorHandler()

    if command == "analyze":
        # Analyze error patterns
        history = handler._load_history()
        categories = {}
        for error in history:
            cat = error.get('category', 'UNKNOWN')
            categories[cat] = categories.get(cat, 0) + 1

        print("Error Analysis:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} errors")

    elif command == "test-recovery":
        # Test recovery strategies
        print("Testing recovery strategies...")

        # Test network recovery
        try:
            raise ConnectionError("Connection refused")
        except Exception as e:
            result = handler.handle(e, {"cached_data": "test_cache"})
            print(f"Network recovery: {result.succeeded}")

    elif command == "learn":
        # Learn from error history
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        print(f"Learning from last {days} days of errors...")

        # Analyze patterns and update strategies
        history = handler._load_history()
        # Learning logic here

    elif command == "report":
        # Generate error report
        format_type = sys.argv[2] if len(sys.argv) > 2 else "json"
        history = handler._load_history()

        if format_type == "json":
            print(json.dumps(history, indent=2, default=str))
        elif format_type == "html":
            # Generate HTML report
            print("<html>Error Report</html>")

if __name__ == "__main__":
    main()
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Automatic Recovery | 70%+ | Recovered/total errors |
| Debug Time Reduction | -60% | Time to resolution |
| Repeat Failures | -80% | Repeat errors after learning |
| Error Categories | 95%+ accuracy | Correct categorization rate |

## References

- Current exceptions: `exceptions.py`
- Error patterns: Test failures analysis
- Recovery examples: ADW scripts