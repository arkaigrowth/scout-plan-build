#!/usr/bin/env python3
"""
Canonical Path Constants - Single Source of Truth

This module defines the ONE TRUE LOCATION for each type of framework output.
No more ambiguity, no more duplicate writes, no more confusion.

All modules MUST import from here rather than hardcoding paths.
"""

from pathlib import Path

# =============================================================================
# Scout Output Locations (CANONICAL)
# =============================================================================

SCOUT_OUTPUT_DIR = Path("scout_outputs")
"""Primary directory for all scout discovery results."""

SCOUT_TEMP_DIR = SCOUT_OUTPUT_DIR / "temp"
"""Temporary working directory for scout operations."""

SCOUT_FINAL_FILE = SCOUT_OUTPUT_DIR / "relevant_files.json"
"""Aggregated scout results - this is the file plan phase reads."""

SCOUT_WORKFLOW_DIR = SCOUT_OUTPUT_DIR / "workflows"
"""Workflow execution state (replaces agents/ directory)."""


# =============================================================================
# Build Output Locations (CANONICAL)
# =============================================================================

AI_DOCS_DIR = Path("ai_docs")
"""Base directory for AI-generated documentation."""

BUILD_REPORTS_DIR = AI_DOCS_DIR / "build_reports"
"""Build execution reports and logs."""

REVIEWS_DIR = AI_DOCS_DIR / "reviews"
"""Code review reports."""

OUTPUTS_DIR = AI_DOCS_DIR / "outputs"
"""Timestamped output directory (FileOrganizer)."""


# =============================================================================
# Specification Locations (CANONICAL)
# =============================================================================

SPECS_DIR = Path("specs")
"""Implementation plans and specifications."""


# =============================================================================
# Legacy Locations (DEPRECATED - Read-only for backward compatibility)
# =============================================================================

LEGACY_SCOUT_DIR = Path("ai_docs/scout")
"""
DEPRECATED: Old scout output location.
Only use for reading old files during migration.
DO NOT WRITE new files here.
"""

LEGACY_AGENTS_DIR = Path("agents")
"""
DEPRECATED: Renamed to scout_outputs/workflows/
Only use for reading old state files during migration.
DO NOT WRITE new files here.
"""


# =============================================================================
# Agent Runs (NEW - Phase 1)
# =============================================================================

AGENT_RUNS_DIR = Path("agent_runs")
"""Centralized directory for all agent run tracking."""

AGENT_RUNS_TEMPLATE_DIR = AGENT_RUNS_DIR / ".template"
"""Templates for run metadata and state."""

def get_run_dir(run_id: str) -> Path:
    """Get the directory for a specific run."""
    run_dir = AGENT_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def get_latest_run() -> Optional[Path]:
    """Get the most recent run directory."""
    from typing import Optional
    latest = AGENT_RUNS_DIR / "latest"
    if latest.is_symlink():
        return latest.resolve()
    return None

# =============================================================================
# Validation Constants
# =============================================================================

ALLOWED_OUTPUT_PREFIXES = [
    "specs/",
    "scout_outputs/",
    "scout_outputs/temp/",
    "scout_outputs/workflows/",
    "ai_docs/build_reports/",
    "ai_docs/reviews/",
    "ai_docs/outputs/",
    "docs/",
    "scripts/",
    "adws/",
]
"""
Paths that framework is allowed to write to.
These are enforced by validators.py to prevent writing to unsafe locations.

NOTE: ai_docs/scout/ is intentionally REMOVED - use scout_outputs/ instead.
NOTE: agents/ is intentionally REMOVED - use scout_outputs/workflows/ instead.
"""


# =============================================================================
# Helper Functions
# =============================================================================

def ensure_canonical_dirs() -> None:
    """
    Create all canonical directories if they don't exist.
    Call this at framework initialization.
    """
    for path_obj in [
        SCOUT_OUTPUT_DIR,
        SCOUT_TEMP_DIR,
        SCOUT_WORKFLOW_DIR,
        BUILD_REPORTS_DIR,
        REVIEWS_DIR,
        OUTPUTS_DIR,
        SPECS_DIR,
    ]:
        path_obj.mkdir(parents=True, exist_ok=True)


def get_scout_output_path() -> Path:
    """
    Get the canonical scout output file path.
    Use this instead of hardcoding paths.

    Returns:
        Path to scout_outputs/relevant_files.json
    """
    SCOUT_FINAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    return SCOUT_FINAL_FILE


def get_workflow_state_path(adw_id: str) -> Path:
    """
    Get the canonical workflow state directory.

    Args:
        adw_id: Workflow identifier (e.g., "ADW-001")

    Returns:
        Path to scout_outputs/workflows/{adw_id}/
    """
    workflow_dir = SCOUT_WORKFLOW_DIR / adw_id
    workflow_dir.mkdir(parents=True, exist_ok=True)
    return workflow_dir


def get_build_report_path(task_name: str, adw_id: str) -> Path:
    """
    Get the canonical build report path.

    Args:
        task_name: Task description (will be slugified)
        adw_id: Workflow identifier

    Returns:
        Path to ai_docs/build_reports/{slug}-build-report.md
    """
    # Slugify task name
    slug = "".join(c if c.isalnum() or c in "-_" else "-"
                   for c in task_name.lower())[:50]

    BUILD_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return BUILD_REPORTS_DIR / f"{slug}-{adw_id}-build-report.md"


# =============================================================================
# Usage Examples (for documentation)
# =============================================================================

"""
CORRECT USAGE:

    from adw_modules.constants import SCOUT_FINAL_FILE, get_scout_output_path

    # Writing scout results
    output_path = get_scout_output_path()
    with open(output_path, 'w') as f:
        json.dump(data, f)

    # Reading scout results
    with open(SCOUT_FINAL_FILE) as f:
        data = json.load(f)

INCORRECT USAGE (DON'T DO THIS):

    # ❌ Hardcoded path
    output_path = Path("ai_docs/scout/relevant_files.json")

    # ❌ String concatenation
    output_path = "scout_outputs/" + "relevant_files.json"
"""
