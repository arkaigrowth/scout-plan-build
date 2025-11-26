#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan, Build & Review - AI Developer Workflow for development with review (skipping tests)

Usage: uv run adw_plan_build_review.py <issue-number> [adw-id]

This script runs:
1. adw_plan.py - Planning phase
2. adw_build.py - Implementation phase
3. adw_review.py - Review phase

Note: This workflow skips the testing phase. The review phase will evaluate
implementation against the specification but without test results.

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
        print("Usage: uv run adw_plan_build_review.py <issue-number> [adw-id]")
        print("\nThis workflow runs:")
        print("  1. Plan")
        print("  2. Build")
        print("  3. Review (without test results)")
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

    # Run review with the ADW ID
    review_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_review.py"),
        issue_number,
        adw_id,
    ]
    print(f"\n=== REVIEW PHASE ===")
    print(f"Running: {' '.join(review_cmd)}")
    print("Note: Review is running without test results")
    review = subprocess.run(review_cmd)
    if review.returncode != 0:
        print("Review phase failed")
        sys.exit(1)

    print(f"\n✅ Plan-Build-Review workflow finished successfully for issue #{issue_number}")
    print(f"ADW ID: {adw_id}")


if __name__ == "__main__":
    main()