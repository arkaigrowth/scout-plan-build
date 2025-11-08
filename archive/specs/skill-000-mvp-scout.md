# MVP Scout Determinism (Simplified)

## Metadata
```yaml
skill_id: skill-000-mvp
name: mvp-scout-determinism
version: 0.1.0
effort_estimate: 4 hours
status: MVP
```

## The Problem (Simple)
Scout returns files in random order. This breaks reproducibility.

## The Solution (Simple)
Sort the files alphabetically. That's it.

## Implementation (50 lines)

```python
#!/usr/bin/env python3
"""MVP Scout - Just make it deterministic."""

import json
import subprocess
from typing import List, Dict

def scout_files(task: str) -> Dict:
    """Find files and return them sorted."""

    # Use existing glob to find files
    result = subprocess.run(
        ["find", ".", "-type", "f", "-name", "*.py"],
        capture_output=True,
        text=True
    )

    files = result.stdout.strip().split('\n') if result.stdout else []

    # THE KEY FIX: Sort them!
    files = sorted([f for f in files if f])

    return {
        "task": task,
        "files": files,
        "count": len(files)
    }

def main():
    import sys
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Find relevant files"

    result = scout_files(task)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

## Testing (10 lines)

```python
def test_deterministic():
    """Verify scout is deterministic."""
    result1 = scout_files("test")
    result2 = scout_files("test")
    assert result1 == result2, "Scout not deterministic!"
    print("✓ Scout is deterministic")

test_deterministic()
```

## Usage

```bash
python mvp_scout.py "find auth code"
# Returns same sorted list every time
```

## What This Does NOT Include
- ❌ Cryptographic fingerprinting
- ❌ Cache invalidation
- ❌ Evolution tracking
- ❌ Cross-platform normalization
- ❌ Performance SLAs
- ❌ Distributed tracing
- ❌ Fallback levels (just works or doesn't)

## Future Scaffolding (TODOs only)

```python
class MVPScout:
    def __init__(self):
        # MVP: Nothing fancy
        self.version = "0.1.0"

        # TODO (v1.0): Add when slow
        self.cache = None

        # TODO (v2.0): Add when debugging sucks
        self.logger = None

    def scout(self, task):
        files = self._find_files(task)
        return sorted(files)  # That's literally it
```

## Time to Build
- Implementation: 2 hours
- Testing: 1 hour
- Integration: 1 hour
- **Total: 4 hours**

## Success Criteria
1. Run scout twice → get same files in same order ✓
2. Works with Python files ✓
3. Doesn't crash ✓

That's it. Ship it.