#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW SDLC - Complete Software Development Life Cycle workflow

Usage: uv run adw_sdlc.py <issue-number> [adw-id]

This script runs the complete ADW SDLC pipeline:
1. adw_plan.py - Planning phase
2. adw_build.py - Implementation phase
3. adw_test.py - Testing phase
4. adw_review.py - Review phase
5. adw_document.py - Documentation phase

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
        print("Usage: uv run adw_sdlc.py <issue-number> [adw-id]")
        print("\nThis runs the complete Software Development Life Cycle:")
        print("  1. Plan")
        print("  2. Build")
        print("  3. Test")
        print("  4. Review")
        print("  5. Document")
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

    # Run test with the ADW ID
    test_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_test.py"),
        issue_number,
        adw_id,
        "--skip-e2e",
    ]
    print(f"\n=== TEST PHASE ===")
    print(f"Running: {' '.join(test_cmd)}")
    test = subprocess.run(test_cmd)
    if test.returncode != 0:
        print("Test phase failed")
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
    review = subprocess.run(review_cmd)
    if review.returncode != 0:
        print("Review phase failed")
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
    document = subprocess.run(document_cmd)
    if document.returncode != 0:
        print("Document phase failed")
        sys.exit(1)

    print(f"\n✅ Complete SDLC workflow finished successfully for issue #{issue_number}")
    print(f"ADW ID: {adw_id}")


if __name__ == "__main__":
    main()