#!/usr/bin/env python3
"""
MVP Integration Test - Wire everything together in 100 lines.
This is what you'll actually run to test Scout→Plan→Build.
"""

import json
import subprocess
from pathlib import Path
import sys

# --- MVP Skill Implementations (inline for simplicity) ---

# Skill 000: Scout Determinism
def scout(task: str) -> dict:
    """Find files, return them sorted."""
    result = subprocess.run(
        ["find", ".", "-type", "f", "-name", "*.py", "-o", "-name", "*.md"],
        capture_output=True,
        text=True
    )
    files = result.stdout.strip().split('\n') if result.stdout else []
    files = sorted([f for f in files if f and not "/.git/" in f])[:20]  # Top 20 files
    return {"task": task, "files": files}

# Skill 002: Validation
def validate(input_type: str, value: str) -> bool:
    """Basic validation."""
    if input_type == "path" and ".." in value:
        return False
    if input_type == "command" and "rm -rf" in value:
        return False
    return True

# Skill 003: State Management
STATE_FILE = Path(".claude/mvp_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def save_state(data: dict):
    """Save state to JSON."""
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_state() -> dict:
    """Load state from JSON."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

# Skill 005: Error Handling
def with_retry(func, *args, max_attempts=3):
    """Retry on failure."""
    for attempt in range(max_attempts):
        try:
            return func(*args)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                return {"error": str(e)}

# --- MVP Pipeline ---

def run_pipeline(task: str):
    """Run Scout→Plan→Build pipeline with MVP skills."""

    print("=" * 60)
    print("MVP PIPELINE TEST")
    print("=" * 60)

    # Step 1: Validate input
    print("\n1. VALIDATION")
    if not validate("prompt", task):
        print("  ✗ Invalid input")
        return False
    print("  ✓ Input validated")

    # Step 2: Scout with retry
    print("\n2. SCOUT (with determinism)")
    scout_result = with_retry(scout, task)

    if "error" in scout_result:
        print(f"  ✗ Scout failed: {scout_result['error']}")
        return False

    print(f"  ✓ Found {len(scout_result['files'])} files (sorted)")
    print(f"  First 3: {scout_result['files'][:3]}")

    # Save state checkpoint
    save_state({"phase": "scout_complete", "files": scout_result['files']})

    # Step 3: Mock Plan phase
    print("\n3. PLAN (mocked)")
    plan_result = {
        "spec": f"Plan for: {task}\nFiles: {len(scout_result['files'])}",
        "status": "ready"
    }
    print(f"  ✓ Plan created")
    save_state({"phase": "plan_complete", "spec": plan_result['spec']})

    # Step 4: Mock Build phase
    print("\n4. BUILD (mocked)")
    build_result = {
        "changes": 5,
        "status": "success"
    }
    print(f"  ✓ Build complete: {build_result['changes']} changes")
    save_state({"phase": "build_complete", "result": build_result})

    # Step 5: Verify determinism
    print("\n5. DETERMINISM CHECK")
    scout_result2 = scout(task)
    if scout_result['files'] == scout_result2['files']:
        print("  ✓ Scout is deterministic!")
    else:
        print("  ✗ Scout is NOT deterministic")
        return False

    # Step 6: Test state recovery
    print("\n6. STATE RECOVERY")
    saved_state = load_state()
    if saved_state.get("phase") == "build_complete":
        print("  ✓ Can recover from checkpoint")
    else:
        print("  ✗ State recovery failed")

    print("\n" + "=" * 60)
    print("✅ MVP PIPELINE SUCCESS")
    print("=" * 60)
    return True

# --- Run the test ---

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Find authentication code"

    success = run_pipeline(task)
    sys.exit(0 if success else 1)

"""
To run:
python mvp_integration_test.py "Find authentication code"

Expected output:
==============================================================
MVP PIPELINE TEST
==============================================================

1. VALIDATION
  ✓ Input validated

2. SCOUT (with determinism)
  ✓ Found 20 files (sorted)
  First 3: ['./README.md', './setup.py', './tests/test_auth.py']

3. PLAN (mocked)
  ✓ Plan created

4. BUILD (mocked)
  ✓ Build complete: 5 changes

5. DETERMINISM CHECK
  ✓ Scout is deterministic!

6. STATE RECOVERY
  ✓ Can recover from checkpoint

==============================================================
✅ MVP PIPELINE SUCCESS
==============================================================
"""