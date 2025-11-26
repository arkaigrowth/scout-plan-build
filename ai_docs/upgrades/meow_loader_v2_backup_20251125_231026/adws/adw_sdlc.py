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


def run_parallel(issue_number: str, adw_id: str, script_dir: str) -> bool:
    """Execute test/review/document phases in parallel with --no-commit flags.

    Returns True if all phases succeed, False otherwise.
    """
    print("\n=== PARALLEL EXECUTION (Test + Review + Document) ===")

    # Start all three phases in background with --no-commit
    test_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_test.py"),
        issue_number, adw_id, "--no-commit", "--skip-e2e"
    ])

    review_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_review.py"),
        issue_number, adw_id, "--no-commit"
    ])

    document_proc = subprocess.Popen([
        "uv", "run",
        os.path.join(script_dir, "adw_document.py"),
        issue_number, adw_id, "--no-commit"
    ])

    # Wait for all to complete
    print("Waiting for parallel phases to complete...")
    test_result = test_proc.wait()
    review_result = review_proc.wait()
    document_result = document_proc.wait()

    # Check if any failed
    if any(r != 0 for r in [test_result, review_result, document_result]):
        print("\n❌ One or more phases failed:")
        if test_result != 0: print("  - Test phase failed")
        if review_result != 0: print("  - Review phase failed")
        if document_result != 0: print("  - Document phase failed")
        return False

    # Single aggregated commit
    print("\n=== Creating aggregated commit ===")
    subprocess.run(["git", "add", "."])
    commit_msg = f"""Parallel execution results for #{issue_number}

- ✅ Tests passed
- ✅ Review completed
- ✅ Documentation updated

ADW ID: {adw_id}
"""
    subprocess.run(["git", "commit", "-m", commit_msg])
    subprocess.run(["git", "push"])

    print("✅ Parallel execution completed successfully")
    return True


def main():
    """Main entry point."""
    # Check for --parallel flag
    parallel = "--parallel" in sys.argv
    if parallel:
        sys.argv.remove("--parallel")

    if len(sys.argv) < 2:
        print("Usage: uv run adw_sdlc.py <issue-number> [adw-id] [--parallel]")
        print("\nThis runs the complete Software Development Life Cycle:")
        print("  1. Plan")
        print("  2. Build")
        print("  3. Test (parallel if --parallel)")
        print("  4. Review (parallel if --parallel)")
        print("  5. Document (parallel if --parallel)")
        print("\nOptions:")
        print("  --parallel  Run Test/Review/Document phases in parallel (40-50% faster)")
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

    # Run Test/Review/Document either in parallel or serial
    if parallel:
        # Run test, review, and document in parallel
        success = run_parallel(issue_number, adw_id, script_dir)
        if not success:
            print("Parallel execution failed")
            sys.exit(1)
    else:
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