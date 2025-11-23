"""
Agents package: Run management and orchestration.

This package provides tools for managing agent runs with:
- State tracking (ACTIVE → DONE/CRASHED/STALLED)
- Session correlation (links runs to Claude sessions)
- Git provenance (captures commit hash at run start)
- Artifact management (output files, logs)

Usage:
    from agents.run_manager import RunManager, start_run

    # Start a tracked run
    run = start_run("scout", "find auth files")

    # Do work...
    run.update_state(progress=50)

    # Complete
    run.complete(output_path="scout_outputs/relevant_files.json")
"""

from agents.run_manager import (
    RunManager,
    RunState,
    start_run,
    get_latest_run,
)

__all__ = [
    "RunManager",
    "RunState",
    "start_run",
    "get_latest_run",
]
