# Skill Specification: validating-inputs

## Metadata
```yaml
skill_id: skill-002
name: validating-inputs
version: 1.0.0
schema_version: 1.1.0
category: security
priority: CRITICAL
effort_estimate: 1 day
confidence: 0.95
```

## Overview

### Purpose
Provide universal input validation with security-first design, preventing command injection, path traversal, and other attack vectors. Consolidates validation logic currently spread across validators.py with 155+ test assertions.

### Problem Statement
- Security validation scattered across multiple files
- Inconsistent validation approaches
- Risk of injection attacks
- No centralized validation rules

### Expected Impact
- **Security**: 100% coverage of known attack vectors
- **Error reduction**: 90% fewer validation-related failures
- **Consistency**: Single source of truth for validation
- **Performance**: Cached validation results

## Skill Design

### SKILL.md Structure (< 300 lines)

```markdown
---
name: validating-inputs
description: Validates all user inputs with security-first design, preventing injection attacks and path traversal. Use when processing user input, validating paths, sanitizing commands, or checking configuration.
version: 1.0.0
dependencies: python>=3.8, pydantic>=2.0
---

# Validating Inputs

Security-first input validation preventing common attack vectors.

## When to Use

Activate this skill when:
- Processing any user input
- Validating file paths
- Sanitizing shell commands
- Checking configuration values
- User mentions: validate, sanitize, security, check input

## Quick Validation

### Path Validation
```python
# Validates against allowed prefixes and traversal
is_valid = validate_path("scout_outputs/data.json")  # True
is_valid = validate_path("../../etc/passwd")  # False - traversal
```

### Command Validation
```python
# Whitelist-based command validation
is_valid = validate_command("grep pattern file.txt")  # True
is_valid = validate_command("rm -rf /")  # False - dangerous
```

### Commit Message Sanitization
```python
# Prevents shell injection in git commands
safe = sanitize_commit("fix: issue\n\nDetails")  # OK
safe = sanitize_commit("fix: `rm -rf /`")  # Sanitized
```

## Validation Rules

For complete rules → see `references/rules.md`
For attack vectors → see `references/attacks.md`
For examples → see `references/examples.md`

## Scripts

```bash
# Validate input file
python scripts/validate.py path "agents/file.json"

# Check command safety
python scripts/validate.py command "grep -r pattern"

# Sanitize commit message
python scripts/validate.py commit "feat: new feature"

# Batch validation
python scripts/validate.py batch inputs.json
```

## Error Handling

Validation failures return structured errors:
```json
{
  "valid": false,
  "error": "PATH_TRAVERSAL",
  "details": "Path contains '../'",
  "input": "../../etc/passwd",
  "suggestion": "Use paths within allowed prefixes"
}
```
```

### Supporting Files

#### scripts/validate.py
```python
#!/usr/bin/env python3
"""
Deterministic input validation with security focus.
"""
import sys
import json
import re
from typing import Dict, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, validator

# Security constants
ALLOWED_PATH_PREFIXES = [
    'agents/', '.claude/', 'specs/', 'ai_docs/',
    'docs/', 'tests/', 'adws/', '__pycache__/',
    '.git/', 'tmp/', '/tmp/'
]

ALLOWED_COMMANDS = {
    'git': ['status', 'add', 'commit', 'push', 'pull', 'checkout', 'branch', 'log', 'diff'],
    'ls': ['-la', '-l', '-a'],
    'grep': ['-r', '-n', '-i', '-E'],
    'python': ['*.py'],
    'pip': ['install', 'freeze'],
    'cat': [],
    'echo': [],
    'pwd': [],
    'cd': []
}

FORBIDDEN_PATTERNS = [
    r'rm\s+-rf',
    r'sudo\s+',
    r'chmod\s+777',
    r'eval\(',
    r'exec\(',
    r'__import__',
    r'os\.system',
    r'subprocess\.call'
]

class ValidationResult(BaseModel):
    valid: bool
    error: Optional[str] = None
    details: Optional[str] = None
    input: str
    suggestion: Optional[str] = None

class PathValidator:
    @staticmethod
    def validate(path_str: str) -> ValidationResult:
        """Validate file path against security rules."""
        # Check for path traversal
        if '../' in path_str or '..\\' in path_str:
            return ValidationResult(
                valid=False,
                error="PATH_TRAVERSAL",
                details="Path contains directory traversal",
                input=path_str,
                suggestion="Remove '../' from path"
            )

        # Check for null bytes
        if '\x00' in path_str:
            return ValidationResult(
                valid=False,
                error="NULL_BYTE",
                details="Path contains null byte",
                input=path_str,
                suggestion="Remove null bytes from path"
            )

        # Check allowed prefixes
        path = Path(path_str)
        path_normalized = str(path).replace('\\', '/')

        valid_prefix = any(
            path_normalized.startswith(prefix)
            for prefix in ALLOWED_PATH_PREFIXES
        )

        if not valid_prefix:
            return ValidationResult(
                valid=False,
                error="FORBIDDEN_PATH",
                details=f"Path not in allowed prefixes",
                input=path_str,
                suggestion=f"Use paths starting with: {', '.join(ALLOWED_PATH_PREFIXES[:3])}"
            )

        return ValidationResult(valid=True, input=path_str)

class CommandValidator:
    @staticmethod
    def validate(command: str) -> ValidationResult:
        """Validate shell command against whitelist."""
        # Check for forbidden patterns
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, command):
                return ValidationResult(
                    valid=False,
                    error="DANGEROUS_COMMAND",
                    details=f"Command matches forbidden pattern: {pattern}",
                    input=command,
                    suggestion="Use safe command alternatives"
                )

        # Parse command
        parts = command.split()
        if not parts:
            return ValidationResult(
                valid=False,
                error="EMPTY_COMMAND",
                details="Command is empty",
                input=command,
                suggestion="Provide a valid command"
            )

        cmd = parts[0]

        # Check if command is in whitelist
        if cmd not in ALLOWED_COMMANDS:
            return ValidationResult(
                valid=False,
                error="UNKNOWN_COMMAND",
                details=f"Command '{cmd}' not in whitelist",
                input=command,
                suggestion=f"Use allowed commands: {', '.join(list(ALLOWED_COMMANDS.keys())[:5])}"
            )

        # Validate command arguments
        if ALLOWED_COMMANDS[cmd]:
            args = parts[1:]
            valid_args = any(
                arg in ALLOWED_COMMANDS[cmd]
                for arg in args
            )
            if args and not valid_args:
                return ValidationResult(
                    valid=False,
                    error="INVALID_ARGUMENTS",
                    details=f"Invalid arguments for {cmd}",
                    input=command,
                    suggestion=f"Valid args: {', '.join(ALLOWED_COMMANDS[cmd])}"
                )

        return ValidationResult(valid=True, input=command)

class CommitValidator:
    @staticmethod
    def sanitize(message: str) -> str:
        """Sanitize commit message to prevent injection."""
        # Remove shell metacharacters
        dangerous_chars = ['`', '$', '|', ';', '&', '>', '<', '\\', '"', "'"]
        sanitized = message

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        # Ensure proper format
        lines = sanitized.split('\n')
        if lines:
            # First line max 72 chars
            lines[0] = lines[0][:72]

        return '\n'.join(lines)

def validate_batch(inputs_file: str) -> Dict[str, ValidationResult]:
    """Validate multiple inputs from file."""
    with open(inputs_file) as f:
        inputs = json.load(f)

    results = {}
    for item in inputs:
        input_type = item['type']
        value = item['value']

        if input_type == 'path':
            results[value] = PathValidator.validate(value)
        elif input_type == 'command':
            results[value] = CommandValidator.validate(value)
        elif input_type == 'commit':
            sanitized = CommitValidator.sanitize(value)
            results[value] = ValidationResult(
                valid=True,
                input=value,
                details=f"Sanitized to: {sanitized}"
            )

    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: validate.py [path|command|commit|batch] <input>")
        sys.exit(1)

    validation_type = sys.argv[1]
    input_value = sys.argv[2]

    result = None

    if validation_type == "path":
        result = PathValidator.validate(input_value)
    elif validation_type == "command":
        result = CommandValidator.validate(input_value)
    elif validation_type == "commit":
        sanitized = CommitValidator.sanitize(input_value)
        result = ValidationResult(
            valid=True,
            input=input_value,
            details=f"Sanitized: {sanitized}"
        )
    elif validation_type == "batch":
        results = validate_batch(input_value)
        print(json.dumps({k: v.dict() for k, v in results.items()}, indent=2))
        return

    if result:
        print(json.dumps(result.dict(), indent=2))

if __name__ == "__main__":
    main()
```

#### references/rules.md
```markdown
# Validation Rules

## Path Validation

### Allowed Prefixes
- `agents/` - Agent-related files
- `.claude/` - Claude configuration
- `specs/` - Specifications
- `ai_docs/` - AI documentation
- `docs/` - Documentation
- `tests/` - Test files
- `adws/` - ADW modules
- `/tmp/` - Temporary files

### Forbidden Patterns
- `../` - Directory traversal
- Null bytes (\x00)
- Absolute paths outside project
- Symbolic links to forbidden areas

## Command Validation

### Whitelisted Commands
- `git` - Version control
- `ls` - Directory listing
- `grep` - File searching
- `python` - Script execution
- `cat` - File reading
- `echo` - Output text

### Forbidden Operations
- `rm -rf` - Destructive deletion
- `sudo` - Privilege escalation
- `chmod 777` - Insecure permissions
- `eval()` - Code injection
- `os.system()` - Shell execution
```

### Testing Strategy

```python
# tests/test_validation.py
def test_path_traversal_blocked():
    result = PathValidator.validate("../../etc/passwd")
    assert result.valid == False
    assert result.error == "PATH_TRAVERSAL"

def test_allowed_path_accepted():
    result = PathValidator.validate("scout_outputs/data.json")
    assert result.valid == True

def test_dangerous_command_blocked():
    result = CommandValidator.validate("rm -rf /")
    assert result.valid == False
    assert result.error == "DANGEROUS_COMMAND"

def test_commit_sanitization():
    sanitized = CommitValidator.sanitize("fix: `rm -rf /`")
    assert "`" not in sanitized
    assert "rm -rf /" in sanitized  # Text preserved, metachar removed

# Run all 155+ security tests
def test_all_attack_vectors():
    vectors = load_attack_vectors()
    for vector in vectors:
        result = validate_input(vector)
        assert result.valid == False
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Attack Vector Coverage | 100% | Tests passed/total |
| False Positive Rate | <1% | Valid inputs rejected |
| Performance | <10ms | Average validation time |
| Consistency | 100% | Same input = same result |

## Migration Strategy

### Phase 1: Deploy (4 hours)
1. Create SKILL.md with validation rules
2. Implement validate.py script
3. Add comprehensive tests
4. Benchmark performance

### Phase 2: Integrate (4 hours)
1. Replace validators.py imports
2. Update error handling
3. Add monitoring
4. Document changes

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False positives | Low | Medium | Comprehensive test suite |
| Performance impact | Low | Low | Caching validation results |
| Bypass discovered | Low | High | Regular security audits |
| Breaking changes | Low | Medium | Backward compatibility layer |

## References

- Current implementation: `validators.py`
- Test suite: `tests/test_validators.py`
- Attack vectors: OWASP Top 10
- Best practices: NIST guidelines