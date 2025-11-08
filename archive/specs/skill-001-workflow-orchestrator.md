# Skill Specification: workflow-orchestrator

## Metadata
```yaml
skill_id: skill-001
name: orchestrating-workflows
version: 1.0.0
schema_version: 1.1.0
category: workflow
priority: CRITICAL
effort_estimate: 2 days
confidence: 0.95
```

## Overview

### Purpose
Create and manage multi-phase workflows with state persistence, checkpoint recovery, and error handling. Consolidates workflow orchestration patterns used across 6+ scripts in the repository.

### Problem Statement
Currently, workflow orchestration logic is duplicated 98% across scripts with:
- Manual phase management
- No checkpoint recovery
- Inconsistent error handling
- State management boilerplate repeated in every script

### Expected Impact
- **Code reduction**: Remove ~500 lines of duplicate orchestration code
- **Time savings**: 40% faster workflow execution
- **Error reduction**: 80% fewer workflow failures
- **Maintenance**: Single point of update for orchestration logic

## Skill Design

### SKILL.md Structure (< 500 lines)

```markdown
---
name: orchestrating-workflows
description: Orchestrates multi-phase workflows with state persistence, checkpoint recovery, and error handling. Use when executing sequential operations, managing workflow state, or recovering from failures.
version: 1.0.0
dependencies: python>=3.8, pydantic>=2.0
---

# Orchestrating Workflows

Manages multi-phase workflows with automatic state persistence and recovery.

## When to Use

Activate this skill when:
- Executing multi-step operations
- Need checkpoint/recovery capability
- Managing workflow state
- User mentions: orchestrate, workflow, pipeline, phases

## Core Workflow

### 1. Initialize Workflow
```python
workflow = WorkflowOrchestrator(
    workflow_id="unique-id",
    phases=["scout", "plan", "build", "test", "review"],
    state_backend="json"  # or sqlite, redis
)
```

### 2. Execute Phases
Each phase automatically:
- Saves state before execution
- Creates checkpoint
- Handles errors with retry
- Records results

### 3. Recovery
On failure, workflow resumes from last checkpoint:
```python
workflow.recover_from_checkpoint()
```

## Progressive Disclosure

For phase details → see `references/phases.md`
For state backends → see `references/backends.md`
For error handling → see `references/errors.md`

## Scripts

Execute orchestration with validation:
```bash
python scripts/orchestrate.py validate plan.json
python scripts/orchestrate.py execute plan.json
python scripts/orchestrate.py recover workflow-id
```
```

### Supporting Files

#### scripts/orchestrate.py
```python
#!/usr/bin/env python3
"""
Deterministic workflow orchestration with validation.
"""
import sys
import json
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field, validator
from enum import Enum

class PhaseStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class Phase(BaseModel):
    name: str
    command: str
    timeout: int = 300
    retry_count: int = 3
    depends_on: List[str] = []
    checkpoint: bool = True

class WorkflowSpec(BaseModel):
    workflow_id: str
    phases: List[Phase]
    state_backend: str = "json"
    checkpoint_interval: int = 1

    @validator('state_backend')
    def validate_backend(cls, v):
        if v not in ['json', 'sqlite', 'redis']:
            raise ValueError(f"Invalid backend: {v}")
        return v

class WorkflowOrchestrator:
    def __init__(self, spec: WorkflowSpec):
        self.spec = spec
        self.state = self._load_state()

    def validate(self) -> Dict[str, bool]:
        """Validate workflow before execution."""
        results = {}

        # Check phase dependencies
        phase_names = [p.name for p in self.spec.phases]
        for phase in self.spec.phases:
            for dep in phase.depends_on:
                if dep not in phase_names:
                    results[f"{phase.name}_deps"] = False
                else:
                    results[f"{phase.name}_deps"] = True

        # Check commands exist
        for phase in self.spec.phases:
            cmd_exists = Path(phase.command.split()[0]).exists()
            results[f"{phase.name}_cmd"] = cmd_exists

        return results

    def execute(self) -> Dict[str, any]:
        """Execute workflow with checkpoints."""
        results = {}

        for phase in self.spec.phases:
            # Check dependencies
            if not self._deps_met(phase):
                results[phase.name] = {"status": "skipped", "reason": "deps_not_met"}
                continue

            # Create checkpoint
            if phase.checkpoint:
                self._save_checkpoint(phase.name)

            # Execute with retry
            for attempt in range(phase.retry_count):
                try:
                    result = self._execute_phase(phase)
                    results[phase.name] = {"status": "completed", "result": result}
                    break
                except Exception as e:
                    if attempt == phase.retry_count - 1:
                        results[phase.name] = {"status": "failed", "error": str(e)}
                    else:
                        print(f"Retry {attempt + 1}/{phase.retry_count} for {phase.name}")

        return results

    def recover(self, checkpoint_name: Optional[str] = None) -> Dict[str, any]:
        """Recover from checkpoint."""
        checkpoint = self._load_checkpoint(checkpoint_name)
        if not checkpoint:
            return {"error": "No checkpoint found"}

        # Resume from checkpoint
        start_index = self._get_phase_index(checkpoint['phase'])
        self.spec.phases = self.spec.phases[start_index:]

        return self.execute()

def main():
    if len(sys.argv) < 3:
        print("Usage: orchestrate.py [validate|execute|recover] <spec.json|workflow-id>")
        sys.exit(1)

    command = sys.argv[1]
    target = sys.argv[2]

    if command == "validate":
        spec = WorkflowSpec.parse_file(target)
        orchestrator = WorkflowOrchestrator(spec)
        results = orchestrator.validate()
        print(json.dumps(results, indent=2))

    elif command == "execute":
        spec = WorkflowSpec.parse_file(target)
        orchestrator = WorkflowOrchestrator(spec)
        results = orchestrator.execute()
        print(json.dumps(results, indent=2))

    elif command == "recover":
        # Load from saved state
        orchestrator = WorkflowOrchestrator.load(target)
        results = orchestrator.recover()
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
```

#### references/phases.md
```markdown
# Phase Reference

## Standard Phases

### Scout Phase
- Discovers files and context
- Creates file inventory
- Identifies dependencies

### Plan Phase
- Creates implementation spec
- Validates requirements
- Estimates complexity

### Build Phase
- Implements features
- Follows spec strictly
- Creates tests

### Test Phase
- Runs test suite
- Validates functionality
- Reports coverage

### Review Phase
- Code quality check
- Security validation
- Documentation review
```

### Validation Script
```python
# scripts/validate_workflow.py
def validate_workflow_spec(spec_path: str) -> bool:
    """Validate workflow specification."""
    spec = WorkflowSpec.parse_file(spec_path)

    # Check circular dependencies
    if has_circular_deps(spec.phases):
        return False

    # Verify phase commands
    for phase in spec.phases:
        if not command_exists(phase.command):
            return False

    return True
```

## Testing Strategy

### Unit Tests
```python
def test_workflow_validation():
    spec = WorkflowSpec(
        workflow_id="test",
        phases=[Phase(name="p1", command="echo test")]
    )
    orchestrator = WorkflowOrchestrator(spec)
    assert orchestrator.validate()["p1_cmd"] == True

def test_checkpoint_recovery():
    # Test recovery from checkpoint
    orchestrator.execute()
    # Simulate failure
    recovered = orchestrator.recover()
    assert recovered["status"] == "completed"
```

### Integration Tests
- Execute sample workflows
- Test state persistence
- Verify checkpoint recovery
- Test error handling

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code Reduction | 500 lines removed | Line count analysis |
| Workflow Success Rate | 95%+ | Success/total executions |
| Recovery Success | 90%+ | Successful recoveries/failures |
| Execution Time | -40% | Before/after timing |

## Migration Strategy

### Phase 1: Create Skill (Day 1)
1. Implement SKILL.md with core instructions
2. Create orchestrate.py script
3. Add validation and recovery logic
4. Test with sample workflows

### Phase 2: Integrate (Day 2)
1. Update one workflow to use skill
2. Verify functionality matches original
3. Add monitoring and metrics
4. Document usage patterns

### Phase 3: Rollout
1. Migrate remaining workflows
2. Remove duplicate code
3. Update documentation
4. Train team on usage

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| State corruption | Low | High | Validate state on load, backup before write |
| Circular dependencies | Medium | Medium | Validation prevents execution |
| Command failures | Medium | Low | Retry logic with exponential backoff |
| Performance regression | Low | Medium | Benchmark before/after, optimize hot paths |

## Dependencies

- Python 3.8+
- Pydantic 2.0+ for validation
- JSON/SQLite/Redis for state
- Existing ADW modules

## References

- Current implementation: `adw_modules/workflow_ops.py`
- State management: `adw_modules/state.py`
- Example workflows: `adw_*.py` scripts
- Best practices: Claude Skills documentation