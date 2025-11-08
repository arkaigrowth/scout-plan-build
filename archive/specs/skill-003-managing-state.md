# Skill Specification: managing-state

## Metadata
```yaml
skill_id: skill-003
name: managing-state
version: 1.0.0
schema_version: 1.1.0
category: infrastructure
priority: HIGH
effort_estimate: 1.5 days
confidence: 0.90
```

## Overview

### Purpose
Manage state across workflow executions with multi-backend support, atomic operations, and automatic recovery. Eliminates 100% duplication of state management code across all ADW scripts.

### Problem Statement
- State management duplicated in every workflow script
- No standard approach to persistence
- Lost state on failures
- Manual checkpoint management

### Expected Impact
- **Code reduction**: Remove ~200 lines per script
- **Reliability**: 99% state recovery success
- **Flexibility**: Switch backends without code changes
- **Performance**: 10x faster with caching

## Skill Design

### SKILL.md Structure (< 400 lines)

```markdown
---
name: managing-state
description: Manages workflow state with persistence, checkpoints, and recovery across JSON, SQLite, and Redis backends. Use when saving workflow state, creating checkpoints, recovering from failures, or switching storage backends.
version: 1.0.0
dependencies: python>=3.8, redis>=4.0
---

# Managing State

Reliable state management for workflows with automatic persistence and recovery.

## When to Use

Activate this skill when:
- Saving workflow progress
- Creating checkpoints
- Recovering from failures
- Managing distributed state
- User mentions: state, checkpoint, recover, persistence

## Quick Start

### Initialize State Manager
```python
# Choose backend based on needs
state = StateManager(
    backend="json",      # Development
    # backend="sqlite",  # Production
    # backend="redis",   # Distributed
    namespace="workflow-123"
)
```

### Save State
```python
# Save any JSON-serializable data
state.save("current_phase", "building")
state.save("completed_tasks", ["scout", "plan"])
state.save("metadata", {"timestamp": "2024-01-01", "user": "dev"})
```

### Load State
```python
# Retrieve saved state
phase = state.load("current_phase")  # "building"
tasks = state.load("completed_tasks")  # ["scout", "plan"]
```

### Checkpoints
```python
# Create named checkpoint
state.checkpoint("after_planning")

# List checkpoints
checkpoints = state.list_checkpoints()

# Recover from checkpoint
state.restore_checkpoint("after_planning")
```

## Backend Selection

| Backend | Use Case | Pros | Cons |
|---------|----------|------|------|
| JSON | Development | Simple, readable | Not concurrent-safe |
| SQLite | Production | ACID, queryable | Single machine |
| Redis | Distributed | Fast, scalable | Requires server |

For backend details → see `references/backends.md`
For migration guide → see `references/migration.md`

## Scripts

```bash
# Initialize state backend
python scripts/state_manager.py init --backend json --namespace workflow-123

# Save state
python scripts/state_manager.py save --key phase --value building

# Load state
python scripts/state_manager.py load --key phase

# Create checkpoint
python scripts/state_manager.py checkpoint --name after_planning

# Restore checkpoint
python scripts/state_manager.py restore --checkpoint after_planning

# Migrate backends
python scripts/state_manager.py migrate --from json --to sqlite
```

## Error Recovery

State operations are atomic with automatic recovery:

```python
try:
    state.save("key", value)
except StateException as e:
    # Automatic retry with exponential backoff
    state.recover()
    state.save("key", value)
```
```

### Supporting Files

#### scripts/state_manager.py
```python
#!/usr/bin/env python3
"""
Multi-backend state management with atomic operations.
"""
import sys
import json
import sqlite3
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

try:
    import redis
except ImportError:
    redis = None

class StateException(Exception):
    """State operation exceptions."""
    pass

class StateBackend(ABC):
    """Abstract state backend interface."""

    @abstractmethod
    def save(self, key: str, value: Any) -> None:
        """Save state value."""
        pass

    @abstractmethod
    def load(self, key: str) -> Any:
        """Load state value."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete state value."""
        pass

    @abstractmethod
    def list_keys(self) -> List[str]:
        """List all keys."""
        pass

    @abstractmethod
    def checkpoint(self, name: str) -> None:
        """Create checkpoint."""
        pass

    @abstractmethod
    def restore_checkpoint(self, name: str) -> None:
        """Restore from checkpoint."""
        pass

class JSONBackend(StateBackend):
    """JSON file-based state backend."""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.state_dir = Path(f".claude/state/{namespace}")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "state.json"
        self.checkpoint_dir = self.state_dir / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)

    def _read_state(self) -> Dict:
        """Read current state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {}

    def _write_state(self, state: Dict) -> None:
        """Write state atomically."""
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(state, f, indent=2)
        temp_file.replace(self.state_file)

    def save(self, key: str, value: Any) -> None:
        """Save state value."""
        state = self._read_state()
        state[key] = {
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._write_state(state)

    def load(self, key: str) -> Any:
        """Load state value."""
        state = self._read_state()
        if key not in state:
            raise StateException(f"Key not found: {key}")
        return state[key]['value']

    def delete(self, key: str) -> None:
        """Delete state value."""
        state = self._read_state()
        if key in state:
            del state[key]
            self._write_state(state)

    def list_keys(self) -> List[str]:
        """List all keys."""
        return list(self._read_state().keys())

    def checkpoint(self, name: str) -> None:
        """Create checkpoint."""
        checkpoint_file = self.checkpoint_dir / f"{name}.json"
        state = self._read_state()
        with open(checkpoint_file, 'w') as f:
            json.dump(state, f, indent=2)

    def restore_checkpoint(self, name: str) -> None:
        """Restore from checkpoint."""
        checkpoint_file = self.checkpoint_dir / f"{name}.json"
        if not checkpoint_file.exists():
            raise StateException(f"Checkpoint not found: {name}")
        with open(checkpoint_file) as f:
            state = json.load(f)
        self._write_state(state)

class SQLiteBackend(StateBackend):
    """SQLite database state backend."""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.db_path = Path(f".claude/state/{namespace}/state.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    name TEXT PRIMARY KEY,
                    state TEXT,
                    created_at TEXT
                )
            """)

    @contextmanager
    def _get_conn(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise StateException(f"Database error: {e}")
        finally:
            conn.close()

    def save(self, key: str, value: Any) -> None:
        """Save state value."""
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO state (key, value, timestamp)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.utcnow().isoformat()))

    def load(self, key: str) -> Any:
        """Load state value."""
        with self._get_conn() as conn:
            result = conn.execute(
                "SELECT value FROM state WHERE key = ?", (key,)
            ).fetchone()
            if not result:
                raise StateException(f"Key not found: {key}")
            return json.loads(result[0])

    def delete(self, key: str) -> None:
        """Delete state value."""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM state WHERE key = ?", (key,))

    def list_keys(self) -> List[str]:
        """List all keys."""
        with self._get_conn() as conn:
            results = conn.execute("SELECT key FROM state").fetchall()
            return [r[0] for r in results]

    def checkpoint(self, name: str) -> None:
        """Create checkpoint."""
        with self._get_conn() as conn:
            state = conn.execute("SELECT * FROM state").fetchall()
            state_json = json.dumps(state)
            conn.execute("""
                INSERT OR REPLACE INTO checkpoints (name, state, created_at)
                VALUES (?, ?, ?)
            """, (name, state_json, datetime.utcnow().isoformat()))

    def restore_checkpoint(self, name: str) -> None:
        """Restore from checkpoint."""
        with self._get_conn() as conn:
            result = conn.execute(
                "SELECT state FROM checkpoints WHERE name = ?", (name,)
            ).fetchone()
            if not result:
                raise StateException(f"Checkpoint not found: {name}")

            state = json.loads(result[0])
            conn.execute("DELETE FROM state")
            for row in state:
                conn.execute("""
                    INSERT INTO state (key, value, timestamp)
                    VALUES (?, ?, ?)
                """, row)

class RedisBackend(StateBackend):
    """Redis state backend for distributed systems."""

    def __init__(self, namespace: str):
        if redis is None:
            raise StateException("Redis not installed: pip install redis")
        self.namespace = namespace
        self.client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.key_prefix = f"state:{namespace}:"

    def save(self, key: str, value: Any) -> None:
        """Save state value."""
        redis_key = f"{self.key_prefix}{key}"
        self.client.set(redis_key, json.dumps(value))
        self.client.expire(redis_key, 86400)  # 24 hour TTL

    def load(self, key: str) -> Any:
        """Load state value."""
        redis_key = f"{self.key_prefix}{key}"
        value = self.client.get(redis_key)
        if value is None:
            raise StateException(f"Key not found: {key}")
        return json.loads(value)

    def delete(self, key: str) -> None:
        """Delete state value."""
        redis_key = f"{self.key_prefix}{key}"
        self.client.delete(redis_key)

    def list_keys(self) -> List[str]:
        """List all keys."""
        pattern = f"{self.key_prefix}*"
        keys = self.client.keys(pattern)
        return [k.replace(self.key_prefix, '') for k in keys]

    def checkpoint(self, name: str) -> None:
        """Create checkpoint."""
        checkpoint_key = f"checkpoint:{self.namespace}:{name}"
        state = {}
        for key in self.list_keys():
            state[key] = self.load(key)
        self.client.set(checkpoint_key, json.dumps(state))

    def restore_checkpoint(self, name: str) -> None:
        """Restore from checkpoint."""
        checkpoint_key = f"checkpoint:{self.namespace}:{name}"
        state_json = self.client.get(checkpoint_key)
        if state_json is None:
            raise StateException(f"Checkpoint not found: {name}")

        state = json.loads(state_json)
        for key, value in state.items():
            self.save(key, value)

class StateManager:
    """High-level state management interface."""

    def __init__(self, backend: str = "json", namespace: str = "default"):
        backends = {
            'json': JSONBackend,
            'sqlite': SQLiteBackend,
            'redis': RedisBackend
        }

        if backend not in backends:
            raise StateException(f"Unknown backend: {backend}")

        self.backend = backends[backend](namespace)
        self.cache = {}  # Local cache for performance

    def save(self, key: str, value: Any) -> None:
        """Save with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.backend.save(key, value)
                self.cache[key] = value
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise StateException(f"Save failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff

    def load(self, key: str, default: Any = None) -> Any:
        """Load with caching."""
        if key in self.cache:
            return self.cache[key]

        try:
            value = self.backend.load(key)
            self.cache[key] = value
            return value
        except StateException:
            if default is not None:
                return default
            raise

    def checkpoint(self, name: str = None) -> str:
        """Create checkpoint with auto-naming."""
        if name is None:
            name = f"auto_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.backend.checkpoint(name)
        return name

    def list_checkpoints(self) -> List[str]:
        """List available checkpoints."""
        checkpoint_dir = Path(f".claude/state/{self.backend.namespace}/checkpoints")
        if checkpoint_dir.exists():
            return [f.stem for f in checkpoint_dir.glob("*.json")]
        return []

def main():
    """CLI interface for state management."""
    if len(sys.argv) < 2:
        print("Usage: state_manager.py [init|save|load|checkpoint|restore|migrate] ...")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        backend = sys.argv[2] if len(sys.argv) > 2 else "json"
        namespace = sys.argv[3] if len(sys.argv) > 3 else "default"
        state = StateManager(backend, namespace)
        print(f"Initialized {backend} backend for {namespace}")

    elif command == "save":
        key = sys.argv[2]
        value = json.loads(sys.argv[3])
        state = StateManager()
        state.save(key, value)
        print(f"Saved {key}")

    elif command == "load":
        key = sys.argv[2]
        state = StateManager()
        value = state.load(key)
        print(json.dumps(value, indent=2))

    elif command == "checkpoint":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        state = StateManager()
        checkpoint_name = state.checkpoint(name)
        print(f"Created checkpoint: {checkpoint_name}")

    elif command == "restore":
        checkpoint = sys.argv[2]
        state = StateManager()
        state.backend.restore_checkpoint(checkpoint)
        print(f"Restored from: {checkpoint}")

if __name__ == "__main__":
    main()
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code Reduction | 200 lines/script | Line count before/after |
| Recovery Success | 99%+ | Successful recoveries/attempts |
| Performance | 10x with cache | Response time comparison |
| Backend Migration | <5 minutes | Time to switch backends |

## Migration Strategy

### Phase 1: Core Implementation (Day 1)
1. Implement StateManager with JSON backend
2. Add SQLite backend
3. Create comprehensive tests
4. Document usage patterns

### Phase 2: Advanced Features (Day 0.5)
1. Add Redis backend
2. Implement caching layer
3. Add migration tools
4. Performance optimization

## References

- Current state code: `adw_modules/state.py`
- All ADW scripts: `adw_*.py`
- Backend comparison: Architecture docs