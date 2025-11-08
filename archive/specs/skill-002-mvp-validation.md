# MVP Input Validation (Simplified)

## Metadata
```yaml
skill_id: skill-002-mvp
name: mvp-input-validation
version: 0.1.0
effort_estimate: 2 hours
```

## The Problem
User inputs need validation to prevent injection attacks.

## The Solution
Wrap the existing `validators.py`. Don't reinvent it.

## Implementation (20 lines)

```python
#!/usr/bin/env python3
"""MVP Validation - Just wrap existing validators."""

from adws.adw_modules.validators import (
    SafeUserInput,
    SafeFilePath,
    SafeCommand
)

def validate_input(input_type: str, value: str) -> bool:
    """Validate input using existing validators."""
    try:
        if input_type == "path":
            SafeFilePath(path=value)
        elif input_type == "command":
            SafeCommand(command=value)
        elif input_type == "prompt":
            SafeUserInput(prompt=value)
        else:
            return True  # Unknown type, allow for now
        return True
    except Exception:
        return False

def main():
    import sys
    if len(sys.argv) >= 3:
        input_type = sys.argv[1]
        value = " ".join(sys.argv[2:])
        if validate_input(input_type, value):
            print(f"✓ Valid {input_type}: {value}")
        else:
            print(f"✗ Invalid {input_type}: {value}")

if __name__ == "__main__":
    main()
```

## Testing

```python
# Test it blocks bad stuff
assert not validate_input("path", "../../etc/passwd")
assert not validate_input("command", "rm -rf /")

# Test it allows good stuff
assert validate_input("path", "agents/file.txt")
assert validate_input("command", "ls -la")

print("✓ Validation works")
```

## What This Does NOT Include
- ❌ New validation logic (reuses existing)
- ❌ Caching
- ❌ Performance optimization
- ❌ Complex error messages

## Time to Build
- Wrap existing validators: 1 hour
- Test it works: 1 hour
- **Total: 2 hours**

That's it. Reuse what works.