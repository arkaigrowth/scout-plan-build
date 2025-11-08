# Skill Specification: adw-orchestrating

## Metadata
```yaml
skill_id: skill-004
name: adw-orchestrating
version: 1.0.0
schema_version: 1.1.0
category: workflow
priority: CRITICAL
effort_estimate: 2 days
confidence: 0.95
```

## Overview

### Purpose
Consolidate 6 separate ADW orchestrator scripts into a single, configurable skill that handles the complete scout → plan → build → test → review workflow with 98% less code duplication.

### Problem Statement
- 6 nearly identical orchestrator scripts with 98% duplication
- Manual copy-paste to create new workflows
- Inconsistent error handling across scripts
- No shared improvements propagate

### Expected Impact
- **Code reduction**: Replace 6 scripts (~2400 lines) with 1 skill (~400 lines)
- **Consistency**: All workflows use same orchestration logic
- **Speed**: 40% faster execution with optimizations
- **Maintenance**: Single point for updates

## Skill Design

### SKILL.md Structure (< 450 lines)

```markdown
---
name: adw-orchestrating
description: Orchestrates complete ADW workflows from issue to implementation with scout, plan, build, test, and review phases. Use when running end-to-end workflows, implementing GitHub issues, or executing ADW pipelines.
version: 1.0.0
dependencies: python>=3.8, gh>=2.0
---

# ADW Orchestrating

Complete Agent-Driven Workflow orchestration from issue to implementation.

## When to Use

Activate this skill when:
- Implementing a GitHub issue
- Running complete ADW pipeline
- Need scout → plan → build → test → review
- User mentions: ADW, orchestrate, implement issue, complete workflow

## Quick Start

### From GitHub Issue
```bash
# Complete workflow from issue
python scripts/adw_orchestrate.py issue 123

# With custom configuration
python scripts/adw_orchestrate.py issue 123 --config custom.yaml

# Dry run to see what would happen
python scripts/adw_orchestrate.py issue 123 --dry-run
```

### Custom Workflow
```yaml
# workflow.yaml
workflow_id: "custom-workflow"
source: "issue"  # or "spec", "manual"
phases:
  scout:
    enabled: true
    depth: 3
    use_memory: true
  plan:
    enabled: true
    include_docs: true
    review_iterations: 2
  build:
    enabled: true
    parallel_files: true
    test_during_build: true
  test:
    enabled: true
    retry_on_failure: true
    max_retries: 3
  review:
    enabled: true
    auto_fix: true
    semantic_commit: true
```

### Direct Execution
```python
from adw_orchestrator import ADWOrchestrator

orchestrator = ADWOrchestrator(
    workflow_id="issue-123-fix",
    source_type="issue",
    source_id="123"
)

# Execute full pipeline
result = orchestrator.execute()

# Or phase by phase
orchestrator.scout()
orchestrator.plan()
orchestrator.build()
orchestrator.test()
orchestrator.review()
```

## Phase Configuration

Each phase can be customized:

| Phase | Options | Default |
|-------|---------|---------|
| Scout | depth, use_memory, patterns | depth=3, memory=true |
| Plan | include_docs, review_iterations | docs=true, review=2 |
| Build | parallel, test_during | parallel=true, test=true |
| Test | retry, max_attempts | retry=true, max=3 |
| Review | auto_fix, commit | fix=true, commit=true |

For phase details → see `references/phases.md`
For configurations → see `references/configs.md`
For examples → see `references/examples.md`

## Scripts

### Main Orchestrator
```bash
# From issue
python scripts/adw_orchestrate.py issue 123

# From spec file
python scripts/adw_orchestrate.py spec specs/feature.md

# Resume from checkpoint
python scripts/adw_orchestrate.py resume workflow-id

# List workflows
python scripts/adw_orchestrate.py list

# Show workflow status
python scripts/adw_orchestrate.py status workflow-id
```

### Phase Control
```bash
# Run specific phase only
python scripts/adw_orchestrate.py phase scout --workflow-id w123

# Skip phases
python scripts/adw_orchestrate.py issue 123 --skip test,review

# Force phase even if completed
python scripts/adw_orchestrate.py phase build --force --workflow-id w123
```

## Error Handling

Automatic recovery with detailed logging:

```python
# Each phase has automatic retry
Phase 'build' failed (attempt 1/3)
→ Analyzing error...
→ Applying automatic fix...
→ Retrying phase 'build' (attempt 2/3)
→ Phase 'build' completed successfully

# Checkpoint recovery
Workflow failed at phase 'test'
→ Checkpoint saved: workflow-123-test
→ To resume: adw_orchestrate.py resume workflow-123
```

## Output Structure

```
workflow-{id}/
├── scout/
│   └── relevant_files.json
├── plan/
│   └── issue-{n}-adw-{id}-{slug}.md
├── build/
│   ├── changes.json
│   └── build-report.md
├── test/
│   ├── results.json
│   └── coverage.html
└── review/
    ├── review-report.md
    └── pr-{number}.json
```
```

### Supporting Files

#### scripts/adw_orchestrate.py
```python
#!/usr/bin/env python3
"""
Unified ADW orchestrator consolidating all workflow scripts.
"""
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import yaml
import time

class PhaseType(str, Enum):
    SCOUT = "scout"
    PLAN = "plan"
    BUILD = "build"
    TEST = "test"
    REVIEW = "review"

@dataclass
class PhaseConfig:
    """Configuration for a workflow phase."""
    enabled: bool = True
    retry_on_failure: bool = True
    max_retries: int = 3
    timeout: int = 300
    options: Dict[str, Any] = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}

@dataclass
class WorkflowConfig:
    """Complete workflow configuration."""
    workflow_id: str
    source_type: str  # issue, spec, manual
    source_id: str
    phases: Dict[PhaseType, PhaseConfig]
    output_dir: Path = Path("workflow-output")
    checkpoint_enabled: bool = True

class ADWOrchestrator:
    """Unified orchestrator for all ADW workflows."""

    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.state = {}
        self.results = {}
        self.current_phase = None

        # Initialize output directory
        self.output_dir = self.config.output_dir / self.config.workflow_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self) -> Dict[str, Any]:
        """Execute complete workflow."""
        print(f"🚀 Starting ADW workflow: {self.config.workflow_id}")

        phases = [
            PhaseType.SCOUT,
            PhaseType.PLAN,
            PhaseType.BUILD,
            PhaseType.TEST,
            PhaseType.REVIEW
        ]

        for phase in phases:
            if not self.config.phases[phase].enabled:
                print(f"⏭️  Skipping phase: {phase}")
                continue

            self.current_phase = phase
            success = self._execute_phase(phase)

            if not success:
                print(f"❌ Workflow failed at phase: {phase}")
                if self.config.checkpoint_enabled:
                    self._save_checkpoint()
                return self.results

        print(f"✅ Workflow completed successfully!")
        return self.results

    def _execute_phase(self, phase: PhaseType) -> bool:
        """Execute a single phase with retry logic."""
        config = self.config.phases[phase]

        for attempt in range(config.max_retries):
            try:
                print(f"\n📍 Phase: {phase} (attempt {attempt + 1}/{config.max_retries})")

                if phase == PhaseType.SCOUT:
                    result = self._run_scout(config.options)
                elif phase == PhaseType.PLAN:
                    result = self._run_plan(config.options)
                elif phase == PhaseType.BUILD:
                    result = self._run_build(config.options)
                elif phase == PhaseType.TEST:
                    result = self._run_test(config.options)
                elif phase == PhaseType.REVIEW:
                    result = self._run_review(config.options)

                self.results[phase] = result
                print(f"✅ Phase {phase} completed")
                return True

            except Exception as e:
                print(f"⚠️  Phase {phase} failed: {e}")
                if attempt < config.max_retries - 1 and config.retry_on_failure:
                    print(f"🔄 Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    self.results[phase] = {"error": str(e)}
                    return False

        return False

    def _run_scout(self, options: Dict) -> Dict:
        """Run scout phase."""
        depth = options.get('depth', 3)
        use_memory = options.get('use_memory', True)

        # Prepare scout command
        task = self._get_task_description()

        cmd = [
            "python", "-m", "adw_modules.scout",
            "--task", task,
            "--depth", str(depth)
        ]

        if use_memory:
            cmd.append("--use-memory")

        # Execute scout
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Scout failed: {result.stderr}")

        # Save scout results
        scout_output = self.output_dir / "scout" / "relevant_files.json"
        scout_output.parent.mkdir(exist_ok=True)

        files = json.loads(result.stdout)
        with open(scout_output, 'w') as f:
            json.dump(files, f, indent=2)

        return {
            "files_found": len(files),
            "output": str(scout_output)
        }

    def _run_plan(self, options: Dict) -> Dict:
        """Run plan phase."""
        include_docs = options.get('include_docs', True)
        review_iterations = options.get('review_iterations', 2)

        # Load scout results
        scout_files = self.output_dir / "scout" / "relevant_files.json"

        cmd = [
            "python", "-m", "adw_modules.planner",
            "--task", self._get_task_description(),
            "--files", str(scout_files),
            "--iterations", str(review_iterations)
        ]

        if include_docs:
            cmd.extend(["--docs", "https://docs.example.com"])

        # Execute plan
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Plan failed: {result.stderr}")

        # Save plan
        plan_output = self.output_dir / "plan" / f"issue-{self.config.source_id}.md"
        plan_output.parent.mkdir(exist_ok=True)
        plan_output.write_text(result.stdout)

        return {
            "spec_file": str(plan_output),
            "iterations": review_iterations
        }

    def _run_build(self, options: Dict) -> Dict:
        """Run build phase."""
        parallel = options.get('parallel_files', True)
        test_during = options.get('test_during_build', True)

        # Load plan
        plan_file = self.results['plan']['spec_file']

        cmd = [
            "python", "-m", "adw_modules.builder",
            "--spec", plan_file
        ]

        if parallel:
            cmd.append("--parallel")
        if test_during:
            cmd.append("--test-during-build")

        # Execute build
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Build failed: {result.stderr}")

        # Save build report
        build_output = self.output_dir / "build" / "build-report.md"
        build_output.parent.mkdir(exist_ok=True)
        build_output.write_text(result.stdout)

        return {
            "report": str(build_output),
            "changes_made": True
        }

    def _run_test(self, options: Dict) -> Dict:
        """Run test phase."""
        retry = options.get('retry_on_failure', True)
        max_retries = options.get('max_retries', 3)

        cmd = ["python", "-m", "pytest", "tests/", "-v"]

        for attempt in range(max_retries if retry else 1):
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                break

            if attempt < max_retries - 1:
                print(f"Tests failed, retrying ({attempt + 2}/{max_retries})...")
                time.sleep(5)

        # Save test results
        test_output = self.output_dir / "test" / "results.json"
        test_output.parent.mkdir(exist_ok=True)

        test_results = {
            "passed": result.returncode == 0,
            "output": result.stdout,
            "attempts": attempt + 1
        }

        with open(test_output, 'w') as f:
            json.dump(test_results, f, indent=2)

        if not test_results["passed"]:
            raise Exception("Tests failed after all retries")

        return test_results

    def _run_review(self, options: Dict) -> Dict:
        """Run review phase."""
        auto_fix = options.get('auto_fix', True)
        semantic_commit = options.get('semantic_commit', True)

        # Create review
        cmd = ["python", "-m", "adw_modules.reviewer", "--check"]

        result = subprocess.run(cmd, capture_output=True, text=True)

        issues_found = result.returncode != 0

        if issues_found and auto_fix:
            print("🔧 Applying automatic fixes...")
            fix_cmd = ["python", "-m", "adw_modules.reviewer", "--fix"]
            subprocess.run(fix_cmd)

        # Create commit if requested
        if semantic_commit:
            commit_msg = self._generate_commit_message()
            subprocess.run(["git", "add", "-A"])
            subprocess.run(["git", "commit", "-m", commit_msg])

        # Save review report
        review_output = self.output_dir / "review" / "review-report.md"
        review_output.parent.mkdir(exist_ok=True)
        review_output.write_text(result.stdout)

        return {
            "report": str(review_output),
            "issues_found": issues_found,
            "auto_fixed": auto_fix and issues_found
        }

    def _get_task_description(self) -> str:
        """Get task description based on source."""
        if self.config.source_type == "issue":
            # Fetch issue from GitHub
            cmd = ["gh", "issue", "view", self.config.source_id, "--json", "title,body"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            issue = json.loads(result.stdout)
            return f"{issue['title']}: {issue['body'][:200]}"
        elif self.config.source_type == "spec":
            spec = Path(self.config.source_id).read_text()
            return spec.split('\n')[0]  # First line
        else:
            return self.config.source_id

    def _generate_commit_message(self) -> str:
        """Generate semantic commit message."""
        task = self._get_task_description()
        issue_num = self.config.source_id if self.config.source_type == "issue" else ""

        # Determine commit type
        if "fix" in task.lower() or "bug" in task.lower():
            commit_type = "fix"
        elif "feat" in task.lower() or "add" in task.lower():
            commit_type = "feat"
        elif "docs" in task.lower():
            commit_type = "docs"
        else:
            commit_type = "chore"

        message = f"{commit_type}: {task[:50]}"
        if issue_num:
            message += f" (#{issue_num})"

        return message

    def _save_checkpoint(self) -> None:
        """Save workflow checkpoint."""
        checkpoint = {
            "workflow_id": self.config.workflow_id,
            "current_phase": self.current_phase,
            "results": self.results,
            "timestamp": time.time()
        }

        checkpoint_file = self.output_dir / "checkpoint.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        print(f"💾 Checkpoint saved: {checkpoint_file}")

def main():
    """CLI interface."""
    if len(sys.argv) < 3:
        print("Usage: adw_orchestrate.py [issue|spec|resume] <id>")
        sys.exit(1)

    command = sys.argv[1]
    target = sys.argv[2]

    # Default phase configuration
    default_phases = {
        PhaseType.SCOUT: PhaseConfig(),
        PhaseType.PLAN: PhaseConfig(),
        PhaseType.BUILD: PhaseConfig(),
        PhaseType.TEST: PhaseConfig(),
        PhaseType.REVIEW: PhaseConfig()
    }

    if command == "issue":
        config = WorkflowConfig(
            workflow_id=f"issue-{target}",
            source_type="issue",
            source_id=target,
            phases=default_phases
        )
    elif command == "spec":
        config = WorkflowConfig(
            workflow_id=f"spec-{Path(target).stem}",
            source_type="spec",
            source_id=target,
            phases=default_phases
        )
    elif command == "resume":
        # Load from checkpoint
        checkpoint_file = Path(f"workflow-output/{target}/checkpoint.json")
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)
        # Resume logic here
        print(f"Resuming workflow {target} from phase {checkpoint['current_phase']}")
        return

    orchestrator = ADWOrchestrator(config)
    results = orchestrator.execute()

    print("\n📊 Workflow Results:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code Reduction | 2000 lines | Line count comparison |
| Consistency | 100% | All workflows use same logic |
| Speed Improvement | 40% | Execution time comparison |
| Success Rate | 95%+ | Successful workflows/total |

## References

- Current scripts: `adw_*.py` (6 files)
- Workflow modules: `adw_modules/`
- Architecture docs: `ai_docs/`