# 🛡️ Building Robust & Deterministic Skills

## The Core Principles

```python
# DETERMINISTIC: Same input → Same output EVERY time
# NON-BRITTLE: Failures are handled, not catastrophic
# IDEMPOTENT: Running twice = same result
# ATOMIC: All or nothing, no partial states
```

---

## 🎯 The VALID Pattern for Robust Skills

Every skill should follow the **VALID** pattern:

```markdown
V - Validate inputs and preconditions
A - Assert environment state
L - Log all operations with IDs
I - Isolate side effects
D - Deterministic execution paths
```

### Example Implementation

```markdown
---
name: robust-scout
version: 1.0.0
deterministic: true
retry_policy:
  max_attempts: 3
  backoff: exponential
validation:
  strict: true
---

# Robust Scout Implementation

## V - Validate Inputs
```python
# ALWAYS validate inputs first
def validate_inputs(task: str, depth: str) -> ValidationResult:
    errors = []

    # Check task is not empty
    if not task or not task.strip():
        errors.append("Task description cannot be empty")

    # Check depth is valid
    if depth not in ["1", "2", "3", "4", None]:
        errors.append(f"Invalid depth: {depth}. Must be 1-4")

    # Check we're in a git repo
    if not os.path.exists(".git"):
        errors.append("Not in a git repository")

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, normalized_inputs={
        "task": task.strip().lower(),  # Normalize for consistency
        "depth": int(depth) if depth else 3
    })
```

## A - Assert Environment State
```python
# Check environment before execution
def assert_environment() -> EnvironmentCheck:
    checks = {
        "git_clean": check_git_status(),
        "disk_space": check_disk_space() > 100_000_000,  # 100MB min
        "memory_available": check_memory() > 500_000_000,  # 500MB min
        "required_tools": check_tools_available(),
        "write_permissions": check_write_permissions()
    }

    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise EnvironmentError(f"Environment checks failed: {failed}")

    return EnvironmentCheck(ready=True, state=checks)
```

## L - Log with Unique IDs
```python
# Every operation gets a unique ID for traceability
operation_id = generate_operation_id()  # "op-20240120-143022-abc123"

log_operation({
    "id": operation_id,
    "operation": "scout",
    "input": validated_inputs,
    "timestamp": current_timestamp(),
    "environment": environment_state
})

# Use this ID throughout execution for correlation
```

## I - Isolate Side Effects
```python
# All side effects in isolated, reversible transactions
with TransactionContext(operation_id) as txn:
    try:
        # All file writes go through transaction
        txn.write_file("scout_outputs/relevant_files.json", data)

        # If anything fails, transaction auto-rollback
        txn.commit()
    except Exception as e:
        # Automatic rollback of all changes
        txn.rollback()
        raise
```

## D - Deterministic Execution
```python
# Remove all sources of non-determinism

# BAD - Non-deterministic
files = glob.glob("**/*.py")  # Random order!
selected = random.sample(files, 10)  # Random selection!

# GOOD - Deterministic
files = sorted(glob.glob("**/*.py"))  # Always same order
selected = files[:10]  # Always same selection

# Use seeds for any randomness
random.seed(hash(operation_id))  # Reproducible randomness
```
```

---

## 🔒 Making Skills Non-Brittle

### 1. **Graceful Degradation Pattern**

```python
def execute_scout_with_fallbacks(task: str) -> ScoutResult:
    """Try progressively simpler approaches"""

    # Level 1: Full intelligent scout
    try:
        return intelligent_scout(task)
    except AdvancedToolError:
        log.warning("Advanced tools failed, trying basic scout")

    # Level 2: Basic scout with native tools
    try:
        return basic_scout(task)
    except BasicToolError:
        log.warning("Basic tools failed, trying minimal scout")

    # Level 3: Minimal file listing
    try:
        return minimal_scout(task)
    except:
        log.error("All scout methods failed")

    # Level 4: Return empty but valid structure
    return ScoutResult(
        files=[],
        status="degraded",
        message="Scout degraded to empty result - manual search needed"
    )
```

### 2. **Defensive File Operations**

```python
def safe_read_file(path: str, default: Any = None) -> Any:
    """Never fail on file read"""
    try:
        # Check existence first
        if not os.path.exists(path):
            log.debug(f"File not found: {path}, using default")
            return default

        # Check permissions
        if not os.access(path, os.R_OK):
            log.warning(f"No read permission: {path}")
            return default

        # Check size (prevent huge file reads)
        size = os.path.getsize(path)
        if size > 10_000_000:  # 10MB limit
            log.warning(f"File too large: {path} ({size} bytes)")
            return default

        # Read with encoding fallback
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()

    except Exception as e:
        log.error(f"Failed to read {path}: {e}")
        return default
```

### 3. **State Validation Pattern**

```python
def validate_state_transitions(current_state: str, new_state: str) -> bool:
    """Ensure valid state transitions"""

    VALID_TRANSITIONS = {
        "init": ["scouting", "error"],
        "scouting": ["planning", "error", "degraded"],
        "planning": ["building", "error", "degraded"],
        "building": ["complete", "error", "rollback"],
        "error": ["init", "rollback"],
        "rollback": ["init"],
        "complete": ["init"]
    }

    valid_next = VALID_TRANSITIONS.get(current_state, [])
    if new_state not in valid_next:
        raise InvalidStateTransition(
            f"Cannot transition from {current_state} to {new_state}. "
            f"Valid: {valid_next}"
        )

    return True
```

---

## 🎲 Making Skills Deterministic

### 1. **Fixed Ordering**

```python
# BAD - Non-deterministic order
def find_files_bad(pattern: str):
    return glob.glob(pattern)  # Order varies by filesystem!

# GOOD - Deterministic order
def find_files_good(pattern: str):
    files = glob.glob(pattern)
    # Sort by multiple criteria for stability
    return sorted(files, key=lambda x: (
        os.path.dirname(x),  # Directory first
        os.path.basename(x)   # Then filename
    ))
```

### 2. **Explicit Random Seeds**

```python
# For any operation that needs randomness
def select_sample_files(files: List[str], n: int, seed: str) -> List[str]:
    """Deterministic sampling with seed"""
    import random

    # Use seed based on inputs for reproducibility
    random.seed(hash(f"{seed}{n}{len(files)}"))

    # Now random operations are deterministic
    return random.sample(files, min(n, len(files)))

# Same inputs = same outputs
sample1 = select_sample_files(["a.py", "b.py", "c.py"], 2, "test")
sample2 = select_sample_files(["a.py", "b.py", "c.py"], 2, "test")
assert sample1 == sample2  # Always true!
```

### 3. **Time-Independent Operations**

```python
# BAD - Time-dependent
def generate_id_bad():
    return f"id-{time.time()}"  # Different every microsecond!

# GOOD - Input-dependent
def generate_id_good(task: str, context: str):
    # Hash of inputs = same ID for same inputs
    content = f"{task}{context}"
    return f"id-{hashlib.sha256(content.encode()).hexdigest()[:8]}"
```

### 4. **Version Pinning**

```markdown
---
name: deterministic-skill
tools_version:
  grep: "3.11"
  glob: "2.0"
  task: "1.5"
model: claude-sonnet-4-5-20250929  # Pin model version!
temperature: 0.0  # Minimum randomness
---
```

---

## 🧪 Testing for Determinism

### Test Harness

```python
def test_skill_determinism(skill_name: str, inputs: dict):
    """Run skill multiple times and verify same output"""

    outputs = []
    for i in range(3):
        # Reset environment to same state
        reset_test_environment()

        # Execute skill
        output = execute_skill(skill_name, inputs)

        # Store normalized output
        outputs.append(normalize_output(output))

    # All outputs should be identical
    assert all(o == outputs[0] for o in outputs), \
        f"Skill {skill_name} is non-deterministic!"

    return True

def normalize_output(output: dict) -> dict:
    """Remove non-deterministic fields for comparison"""
    # Remove timestamps, random IDs, etc.
    normalized = copy.deepcopy(output)
    normalized.pop("timestamp", None)
    normalized.pop("execution_time", None)
    normalized.pop("temp_id", None)
    return normalized
```

### Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(
    task=st.text(min_size=1, max_size=100),
    depth=st.integers(min_value=1, max_value=4)
)
def test_scout_properties(task, depth):
    """Test scout maintains properties across all inputs"""

    result = scout_skill(task, depth)

    # Properties that must ALWAYS hold
    assert isinstance(result.files, list), "Files must be a list"
    assert len(result.files) <= depth * 10, "Files bounded by depth"
    assert all(os.path.exists(f.path) for f in result.files), "All files exist"
    assert result.confidence >= 0 and result.confidence <= 1, "Valid confidence"

    # Determinism check
    result2 = scout_skill(task, depth)
    assert result.files == result2.files, "Same input = same output"
```

---

## 🔄 Idempotency Patterns

### Make Operations Idempotent

```python
def idempotent_file_create(path: str, content: str):
    """Creating twice = same result"""

    # Check if already exists with same content
    if os.path.exists(path):
        existing = safe_read_file(path)
        if existing == content:
            log.debug(f"File already correct: {path}")
            return "unchanged"

    # Create or update
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Idempotent
    with open(path, 'w') as f:
        f.write(content)

    return "created" if not os.path.exists(path) else "updated"

# Running multiple times is safe
idempotent_file_create("test.txt", "hello")  # created
idempotent_file_create("test.txt", "hello")  # unchanged
idempotent_file_create("test.txt", "hello")  # unchanged
```

---

## 🏗️ Robust Skill Template

```markdown
---
name: robust-skill-template
version: 1.0.0
schema_version: 2
deterministic: true
idempotent: true
atomic: true
---

# Robust Skill Template

## Configuration
```python
CONFIG = {
    "max_retries": 3,
    "timeout": 300,  # 5 minutes
    "fallback_mode": "graceful",
    "validation": "strict",
    "state_tracking": True,
    "rollback_on_error": True
}
```

## Pre-Execution Validation
```python
# 1. Validate all inputs
validation = validate_inputs($1, $2, $3)
if not validation.valid:
    print(f"❌ Validation failed: {validation.errors}")
    exit(1)

# 2. Check environment
env_check = check_environment()
if not env_check.ready:
    print(f"❌ Environment not ready: {env_check.issues}")
    exit(1)

# 3. Verify preconditions
preconditions = [
    file_exists(".git"),
    has_disk_space(100_000_000),
    can_write_to("agents/"),
    git_is_clean() or user_confirms("Git has changes, continue?")
]
if not all(preconditions):
    print("❌ Preconditions not met")
    exit(1)
```

## Main Execution with Transaction
```python
operation_id = generate_operation_id(validation.normalized_inputs)

with Transaction(operation_id) as txn:
    try:
        # Phase 1: Scout (with fallback)
        scout_result = try_with_fallback([
            lambda: advanced_scout(task),
            lambda: basic_scout(task),
            lambda: minimal_scout(task)
        ])
        txn.checkpoint("scout_complete")

        # Phase 2: Validate scout results
        if not validate_scout_output(scout_result):
            raise ValidationError("Scout output invalid")
        txn.checkpoint("validation_complete")

        # Phase 3: Save results (idempotent)
        save_result = idempotent_save(
            "scout_outputs/relevant_files.json",
            scout_result
        )
        txn.checkpoint("save_complete")

        # Success - commit transaction
        txn.commit()
        return scout_result

    except Exception as e:
        # Automatic rollback
        log.error(f"Operation {operation_id} failed: {e}")
        txn.rollback()

        # Return safe default
        return SafeDefault(
            files=[],
            status="failed",
            error=str(e),
            operation_id=operation_id
        )
```

## Post-Execution Cleanup
```python
# Always runs, even on error
finally:
    # Clean temporary files
    cleanup_temp_files(operation_id)

    # Log final state
    log_final_state(operation_id, result)

    # Update metrics
    update_metrics(operation_id, result)
```
```

---

## 📊 Measuring Robustness

### Robustness Score

```python
def calculate_robustness_score(skill: Skill) -> float:
    """Score 0-100 for skill robustness"""

    score = 0

    # Input validation (20 points)
    if skill.has_input_validation():
        score += 20

    # Error handling (20 points)
    error_handlers = count_error_handlers(skill)
    score += min(20, error_handlers * 4)

    # Fallback mechanisms (20 points)
    fallbacks = count_fallback_patterns(skill)
    score += min(20, fallbacks * 5)

    # State management (15 points)
    if skill.has_transaction_support():
        score += 15

    # Determinism (15 points)
    if skill.passes_determinism_test():
        score += 15

    # Idempotency (10 points)
    if skill.is_idempotent():
        score += 10

    return score

# Score interpretation:
# 90-100: Production ready
# 70-89: Good, minor improvements needed
# 50-69: Needs work
# <50: Not ready for production
```

---

## 🎯 Best Practices Checklist

### Every Skill Should:

- [ ] **Validate ALL inputs** before execution
- [ ] **Check environment state** before operations
- [ ] **Use deterministic ordering** (sort everything)
- [ ] **Handle errors gracefully** (try/except/finally)
- [ ] **Provide fallback mechanisms** (3+ levels)
- [ ] **Be idempotent** (run twice = safe)
- [ ] **Use transactions** for multi-step operations
- [ ] **Log with unique IDs** for traceability
- [ ] **Clean up resources** in finally blocks
- [ ] **Return valid structure** even on failure
- [ ] **Test for determinism** (same input = same output)
- [ ] **Version pin dependencies** (tools, models)
- [ ] **Set temperature to 0** for determinism
- [ ] **Document failure modes** and recovery
- [ ] **Provide rollback capability** for changes

---

## 🚀 Putting It All Together

The ultimate robust, deterministic skill combines all patterns:

```python
@robust  # Decorator adds retry logic
@deterministic  # Ensures same input = same output
@idempotent  # Safe to run multiple times
@atomic  # All or nothing execution
@logged  # Full operation tracing
def ultimate_scout_skill(task: str, depth: int = 3) -> ScoutResult:
    """Production-ready scout implementation"""

    # The VALID pattern in action
    validation = validate(task, depth)  # V
    assert_environment_ready()          # A
    op_id = log_operation_start()       # L

    with isolated_transaction(op_id):   # I
        files = find_files_sorted(task) # D (deterministic)

        # Multi-level fallback
        return try_strategies([
            lambda: smart_scout(files),
            lambda: basic_scout(files),
            lambda: minimal_scout(files),
            lambda: empty_result()
        ])
```

This skill will:
- **Never crash** (graceful degradation)
- **Always return same results** (deterministic)
- **Run safely multiple times** (idempotent)
- **Complete fully or not at all** (atomic)
- **Be fully traceable** (logged)

That's how you build production-ready skills that won't break! 🛡️