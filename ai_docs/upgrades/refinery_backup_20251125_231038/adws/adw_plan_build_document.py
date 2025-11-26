#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan, Build & Document - AI Developer Workflow for development with documentation

Usage: uv run adw_plan_build_document.py <issue-number> [adw-id]

This script runs:
1. adw_plan.py - Planning phase
2. adw_build.py - Implementation phase
3. adw_document.py - Documentation phase

Note: This workflow skips both testing and review phases. Documentation will be
generated based on the implementation and specification only, without test results
or review artifacts (screenshots).

The scripts are chained together via persistent state (adw_state.json).
"""

import subprocess
import sys
import os

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adw_modules.workflow_ops import ensure_adw_id


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run adw_plan_build_document.py <issue-number> [adw-id]")
        print("\nThis workflow runs:")
        print("  1. Plan")
        print("  2. Build")
        print("  3. Document (without test results or review)")
        print("\nWarning: Documentation quality may be limited without review artifacts")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Ensure ADW ID exists with initialized state
    adw_id = ensure_adw_id(issue_number, adw_id)
    print(f"Using ADW ID: {adw_id}")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Run plan with the ADW ID
    plan_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_plan.py"),
        issue_number,
        adw_id,
    ]
    print(f"\n=== PLAN PHASE ===")
    print(f"Running: {' '.join(plan_cmd)}")
    plan = subprocess.run(plan_cmd)
    if plan.returncode != 0:
        print("Plan phase failed")
        sys.exit(1)

    # Run build with the ADW ID
    build_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_build.py"),
        issue_number,
        adw_id,
    ]
    print(f"\n=== BUILD PHASE ===")
    print(f"Running: {' '.join(build_cmd)}")
    build = subprocess.run(build_cmd)
    if build.returncode != 0:
        print("Build phase failed")
        sys.exit(1)

    # Run document with the ADW ID
    document_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_document.py"),
        issue_number,
        adw_id,
    ]
    print(f"\n=== DOCUMENT PHASE ===")
    print(f"Running: {' '.join(document_cmd)}")
    print("Note: Documentation is being generated without test results or review artifacts")
    print("This may result in limited documentation quality (no screenshots)")
    document = subprocess.run(document_cmd)
    if document.returncode != 0:
        print("Document phase failed")
        print("Tip: The document phase typically expects review artifacts (screenshots)")
        print("Consider running adw_sdlc.py for complete documentation with visuals")
        sys.exit(1)

    print(f"\n✅ Plan-Build-Document workflow finished successfully for issue #{issue_number}")
    print(f"ADW ID: {adw_id}")
    print("\nNote: Documentation was generated without review screenshots")
    print("For richer documentation, use adw_sdlc.py which includes all phases")


if __name__ == "__main__":
    main()