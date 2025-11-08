# MVP State Management (Simplified)

## Metadata
```yaml
skill_id: skill-003-mvp
name: mvp-state-management
version: 0.1.0
effort_estimate: 3 hours
```

## The Problem
Need to save and restore workflow state for recovery.

## The Solution
JSON files. That's it. No Redis, no SQLite, just JSON.

## Implementation (30 lines)

```python
#!/usr/bin/env python3
"""MVP State - Just JSON files."""

import json
import os
from pathlib import Path
from datetime import datetime

STATE_DIR = Path(".claude/state")
STATE_DIR.mkdir(parents=True, exist_ok=True)

def save_state(key: str, value: any) -> bool:
    """Save state to JSON file."""
    try:
        state_file = STATE_DIR / f"{key}.json"
        with open(state_file, 'w') as f:
            json.dump({
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            }, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save state: {e}")
        return False

def load_state(key: str, default=None):
    """Load state from JSON file."""
    try:
        state_file = STATE_DIR / f"{key}.json"
        if state_file.exists():
            with open(state_file) as f:
                data = json.load(f)
                return data["value"]
        return default
    except Exception as e:
        print(f"Failed to load state: {e}")
        return default

def checkpoint(name: str = None) -> str:
    """Create checkpoint of all state."""
    if not name:
        name = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    checkpoint_dir = STATE_DIR / "checkpoints" / name
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Copy all state files to checkpoint
    for state_file in STATE_DIR.glob("*.json"):
        if state_file.is_file():
            (checkpoint_dir / state_file.name).write_text(
                state_file.read_text()
            )

    return name

def restore_checkpoint(name: str) -> bool:
    """Restore from checkpoint."""
    checkpoint_dir = STATE_DIR / "checkpoints" / name
    if not checkpoint_dir.exists():
        return False

    # Copy checkpoint files back
    for checkpoint_file in checkpoint_dir.glob("*.json"):
        (STATE_DIR / checkpoint_file.name).write_text(
            checkpoint_file.read_text()
        )

    return True

def main():
    # Example usage
    save_state("current_phase", "building")
    save_state("files_processed", ["file1.py", "file2.py"])

    phase = load_state("current_phase")
    print(f"Current phase: {phase}")

    # Create checkpoint
    cp = checkpoint("before_build")
    print(f"Created checkpoint: {cp}")

if __name__ == "__main__":
    main()
```

## Testing

```python
# Test save/load
save_state("test", {"data": 123})
assert load_state("test") == {"data": 123}

# Test default
assert load_state("nonexistent", "default") == "default"

# Test checkpoint
save_state("phase", "scout")
cp = checkpoint("test_cp")
save_state("phase", "build")  # Change it
restore_checkpoint(cp)
assert load_state("phase") == "scout"  # Restored!

print("✓ State management works")
```

## What This Does NOT Include
- ❌ Redis backend
- ❌ SQLite backend
- ❌ Atomic transactions
- ❌ Distributed state
- ❌ State migration
- ❌ Encryption

## Scaffolding for Future

```python
class FutureState:
    def __init__(self):
        # MVP: Just JSON
        self.backend = "json"

        # TODO (v1.0): When you need it
        # self.backend = "sqlite"  # When JSON gets slow
        # self.backend = "redis"   # When distributed
```

## Time to Build
- Basic save/load: 1 hour
- Checkpoint/restore: 1 hour
- Testing: 1 hour
- **Total: 3 hours**

Good enough for MVP. Ship it.