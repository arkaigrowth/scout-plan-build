#!/usr/bin/env python3
"""
RunManager: Centralized agent run tracking and state management.

Integrates with session tracking (.current_session) to provide full
traceability from runs → sessions → git commits.

Usage:
    from agents.run_manager import RunManager

    # Start a new run
    run = RunManager.start("scout", "authentication files")

    # Update state
    run.update_state("ACTIVE", progress=50)

    # Complete the run
    run.complete(output_path="scout_outputs/relevant_files.json")

    # Or mark as failed
    run.fail("Connection timeout")
"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import our session tracking utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from adws.adw_common import (
    generate_run_id,
    get_current_session,
    get_provenance_block,
    ensure_dir,
    ROOT,
)
from adws.adw_modules.constants import AGENT_RUNS_DIR, get_run_dir


class RunState(Enum):
    """Possible states for an agent run."""
    ACTIVE = "ACTIVE"       # Currently running
    DONE = "DONE"           # Completed successfully
    CRASHED = "CRASHED"     # Process died unexpectedly
    STALLED = "STALLED"     # No heartbeat for too long
    CANCELLED = "CANCELLED" # User cancelled


@dataclass
class RunMetadata:
    """Immutable metadata about a run (captured at start)."""
    run_id: str
    task_type: str
    task_description: str
    started_at: str

    # Provenance (from session tracking)
    session_id: str
    session_short: str
    git_hash: str
    git_branch: str

    # Optional
    model: str = "claude-sonnet-4"
    parent_run_id: Optional[str] = None
    config_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_type": self.task_type,
            "task_description": self.task_description,
            "started_at": self.started_at,
            "session_id": self.session_id,
            "session_short": self.session_short,
            "git_hash": self.git_hash,
            "git_branch": self.git_branch,
            "model": self.model,
            "parent_run_id": self.parent_run_id,
            "config_hash": self.config_hash,
        }

    def to_yaml(self) -> str:
        """Generate YAML representation for meta.yaml file."""
        lines = [
            "# Run Metadata (immutable)",
            f"run_id: {self.run_id}",
            f"task_type: {self.task_type}",
            f"task_description: \"{self.task_description}\"",
            f"started_at: {self.started_at}",
            "",
            "# Provenance",
            f"session_id: {self.session_id}",
            f"session_short: {self.session_short}",
            f"git_hash: {self.git_hash}",
            f"git_branch: {self.git_branch}",
            "",
            "# Execution",
            f"model: {self.model}",
            f"parent_run_id: {self.parent_run_id or 'null'}",
            f"config_hash: {self.config_hash or 'null'}",
        ]
        return "\n".join(lines)


@dataclass
class RunState_Data:
    """Mutable state of a run (updated throughout lifecycle)."""
    status: RunState = RunState.ACTIVE
    progress: int = 0  # 0-100
    last_heartbeat: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_path: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "progress": self.progress,
            "last_heartbeat": self.last_heartbeat,
            "completed_at": self.completed_at,
            "error": self.error,
            "output_path": self.output_path,
            "artifacts": self.artifacts,
        }


class RunManager:
    """
    Manages the lifecycle of an agent run.

    Creates run directory, tracks state, and provides provenance.
    """

    def __init__(self, run_id: str, run_dir: Path, metadata: RunMetadata):
        self.run_id = run_id
        self.run_dir = run_dir
        self.metadata = metadata
        self.state = RunState_Data()

        # File paths
        self.meta_path = run_dir / "meta.yaml"
        self.state_path = run_dir / "state.json"
        self.output_path = run_dir / "output.md"
        self.artifacts_dir = run_dir / "artifacts"

    @classmethod
    def start(
        cls,
        task_type: str,
        task_description: str,
        parent_run_id: Optional[str] = None,
        model: str = "claude-sonnet-4",
    ) -> "RunManager":
        """
        Start a new run with automatic session tracking.

        Args:
            task_type: Type of task (scout, plan, build, review)
            task_description: Human-readable description
            parent_run_id: If spawned by another run
            model: Model being used

        Returns:
            RunManager instance for the new run
        """
        # Generate unique run ID
        run_id = generate_run_id(task_type, task_description)

        # Get session info (from .current_session or fallback)
        session = get_current_session()

        # Create metadata
        metadata = RunMetadata(
            run_id=run_id,
            task_type=task_type,
            task_description=task_description,
            started_at=datetime.now().isoformat(),
            session_id=session.get("session_id", "unknown"),
            session_short=session.get("short_id", "unknown"),
            git_hash=session.get("git_hash", "unknown"),
            git_branch=session.get("git_branch", "unknown"),
            model=model,
            parent_run_id=parent_run_id,
        )

        # Create run directory
        run_dir = get_run_dir(run_id)
        ensure_dir(run_dir / "artifacts")

        # Create instance
        manager = cls(run_id, run_dir, metadata)

        # Write initial files
        manager._write_metadata()
        manager._write_state()
        manager._update_latest_symlink()

        return manager

    @classmethod
    def load(cls, run_id: str) -> Optional["RunManager"]:
        """Load an existing run by ID."""
        run_dir = AGENT_RUNS_DIR / run_id
        if not run_dir.exists():
            return None

        meta_path = run_dir / "meta.yaml"
        state_path = run_dir / "state.json"

        if not meta_path.exists() or not state_path.exists():
            return None

        # Parse metadata (simple YAML parsing)
        meta_dict = {}
        for line in meta_path.read_text().splitlines():
            if ":" in line and not line.startswith("#"):
                key, value = line.split(":", 1)
                value = value.strip().strip('"')
                if value == "null":
                    value = None
                meta_dict[key.strip()] = value

        metadata = RunMetadata(
            run_id=meta_dict.get("run_id", run_id),
            task_type=meta_dict.get("task_type", "unknown"),
            task_description=meta_dict.get("task_description", ""),
            started_at=meta_dict.get("started_at", ""),
            session_id=meta_dict.get("session_id", "unknown"),
            session_short=meta_dict.get("session_short", "unknown"),
            git_hash=meta_dict.get("git_hash", "unknown"),
            git_branch=meta_dict.get("git_branch", "unknown"),
            model=meta_dict.get("model", "claude-sonnet-4"),
            parent_run_id=meta_dict.get("parent_run_id"),
        )

        manager = cls(run_id, run_dir, metadata)

        # Load state
        state_dict = json.loads(state_path.read_text())
        manager.state = RunState_Data(
            status=RunState(state_dict.get("status", "ACTIVE")),
            progress=state_dict.get("progress", 0),
            last_heartbeat=state_dict.get("last_heartbeat"),
            completed_at=state_dict.get("completed_at"),
            error=state_dict.get("error"),
            output_path=state_dict.get("output_path"),
            artifacts=state_dict.get("artifacts", []),
        )

        return manager

    @classmethod
    def list_runs(cls, status: Optional[RunState] = None) -> List[str]:
        """List all runs, optionally filtered by status."""
        runs = []
        if not AGENT_RUNS_DIR.exists():
            return runs

        for item in AGENT_RUNS_DIR.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if status is None:
                    runs.append(item.name)
                else:
                    state_path = item / "state.json"
                    if state_path.exists():
                        state = json.loads(state_path.read_text())
                        if state.get("status") == status.value:
                            runs.append(item.name)

        return sorted(runs, reverse=True)  # Most recent first

    def update_state(
        self,
        status: Optional[RunState] = None,
        progress: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update run state and write to disk."""
        if status is not None:
            self.state.status = status
        if progress is not None:
            self.state.progress = progress
        if error is not None:
            self.state.error = error

        self.state.last_heartbeat = datetime.now().isoformat()
        self._write_state()

    def heartbeat(self) -> None:
        """Update heartbeat timestamp."""
        self.state.last_heartbeat = datetime.now().isoformat()
        self._write_state()

    def complete(self, output_path: Optional[str] = None) -> None:
        """Mark run as successfully completed."""
        self.state.status = RunState.DONE
        self.state.progress = 100
        self.state.completed_at = datetime.now().isoformat()
        if output_path:
            self.state.output_path = output_path
        self._write_state()

    def fail(self, error: str) -> None:
        """Mark run as failed."""
        self.state.status = RunState.CRASHED
        self.state.error = error
        self.state.completed_at = datetime.now().isoformat()
        self._write_state()

    def add_artifact(self, name: str, content: str) -> Path:
        """Add an artifact file to the run."""
        artifact_path = self.artifacts_dir / name
        artifact_path.write_text(content)
        self.state.artifacts.append(name)
        self._write_state()
        return artifact_path

    def write_output(self, content: str) -> None:
        """Write the primary output file."""
        # Add provenance header
        provenance = get_provenance_block("markdown")
        full_content = f"{provenance}\n---\n\n{content}"
        self.output_path.write_text(full_content)
        self.state.output_path = str(self.output_path)
        self._write_state()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the run for display."""
        return {
            "run_id": self.run_id,
            "task_type": self.metadata.task_type,
            "task_description": self.metadata.task_description,
            "status": self.state.status.value,
            "progress": self.state.progress,
            "session": self.metadata.session_short,
            "git": self.metadata.git_hash,
            "started": self.metadata.started_at,
            "completed": self.state.completed_at,
        }

    def _write_metadata(self) -> None:
        """Write metadata to meta.yaml."""
        self.meta_path.write_text(self.metadata.to_yaml())

    def _write_state(self) -> None:
        """Write state to state.json."""
        self.state_path.write_text(json.dumps(self.state.to_dict(), indent=2))

    def _update_latest_symlink(self) -> None:
        """Update the 'latest' symlink to point to this run."""
        latest_link = AGENT_RUNS_DIR / "latest"
        if latest_link.is_symlink():
            latest_link.unlink()
        elif latest_link.exists():
            # It's a regular file/dir, remove it
            if latest_link.is_dir():
                shutil.rmtree(latest_link)
            else:
                latest_link.unlink()

        # Create relative symlink
        latest_link.symlink_to(self.run_id)


# Convenience functions for simple usage
def start_run(task_type: str, description: str) -> RunManager:
    """Start a new run (convenience function)."""
    return RunManager.start(task_type, description)


def get_latest_run() -> Optional[RunManager]:
    """Get the most recent run."""
    latest_link = AGENT_RUNS_DIR / "latest"
    if latest_link.is_symlink():
        run_id = latest_link.resolve().name
        return RunManager.load(run_id)
    return None


if __name__ == "__main__":
    # Demo usage
    print("=== RunManager Demo ===\n")

    # Start a new run
    run = RunManager.start("scout", "find authentication files")
    print(f"Started run: {run.run_id}")
    print(f"Session: {run.metadata.session_short}")
    print(f"Git: {run.metadata.git_hash}")

    # Update progress
    run.update_state(progress=50)
    print(f"Progress: {run.state.progress}%")

    # Complete
    run.complete(output_path="scout_outputs/relevant_files.json")
    print(f"Status: {run.state.status.value}")

    # Show summary
    print("\n=== Run Summary ===")
    for key, value in run.get_summary().items():
        print(f"  {key}: {value}")
