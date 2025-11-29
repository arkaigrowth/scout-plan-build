#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Build - AI Developer Workflow for agentic building

Supports two modes:

STANDALONE MODE (spec file):
  uv run adw_build.py <spec-file.md>
  uv run adw_build.py specs/gemini-file-search-v1.md

  - Extracts ADW ID from spec file header (looks for "ADW ID:" line)
  - Creates branch from spec filename
  - Implements the spec directly
  - No GitHub issue required

GITHUB MODE (issue-driven):
  uv run adw_build.py <issue-number> <adw-id>
  uv run adw_build.py 123 FEATURE-AUTH

  - Requires prior run of adw_plan.py
  - Uses state from agents/{adw-id}/adw_state.json
  - Updates GitHub issue with progress
  - Creates/updates PR

Workflow:
1. Find existing plan (from state or spec file)
2. Implement the solution based on plan
3. Commit implementation
4. Push and update PR (GitHub mode only)
"""

import sys
import os
import re
import logging
import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.git_ops import commit_changes, finalize_git_operations, get_current_branch
from adw_modules.github import fetch_issue, make_issue_comment, get_repo_url, extract_repo_path
from adw_modules.workflow_ops import (
    implement_plan,
    create_commit,
    format_issue_message,
    AGENT_IMPLEMENTOR,
)
from adw_modules.utils import setup_logger
from adw_modules.data_types import GitHubIssue


def check_env_vars(logger: Optional[logging.Logger] = None) -> None:
    """Check that all required environment variables are set."""
    required_vars = [
        "ANTHROPIC_API_KEY",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = "Error: Missing required environment variables:"
        if logger:
            logger.error(error_msg)
            for var in missing_vars:
                logger.error(f"  - {var}")
        else:
            print(error_msg, file=sys.stderr)
            for var in missing_vars:
                print(f"  - {var}", file=sys.stderr)
        sys.exit(1)


def extract_adw_id_from_spec(spec_file: str) -> Optional[str]:
    """Extract ADW ID from spec file header.

    Looks for a line like "**ADW ID**: GEMINI-SEARCH-V1" or "ADW ID: FEATURE-123"

    Returns:
        ADW ID string if found, None otherwise
    """
    try:
        with open(spec_file, 'r') as f:
            # Only check first 30 lines (header area)
            for i, line in enumerate(f):
                if i > 30:
                    break
                # Match patterns like "ADW ID: XXX" or "**ADW ID**: XXX"
                match = re.search(r'\*?\*?ADW\s*ID\*?\*?\s*[:=]\s*[`"]?([A-Z0-9_-]+)[`"]?', line, re.IGNORECASE)
                if match:
                    return match.group(1).upper()
    except (OSError, IOError):
        pass

    # Fallback: try to extract from filename pattern like "issue-42-adw-FEATURE-123-name.md"
    basename = Path(spec_file).stem
    if '-adw-' in basename.lower():
        parts = basename.lower().split('-adw-')
        if len(parts) > 1:
            # Take the part after -adw- up to the next dash or end
            adw_part = parts[1].split('-')[0]
            return adw_part.upper()

    return None


def generate_branch_name_from_spec(spec_file: str) -> str:
    """Generate a branch name from the spec filename.

    Examples:
        specs/gemini-file-search-v1.md -> feature/gemini-file-search-v1
        specs/issue-42-adw-AUTH-login.md -> feature/issue-42-adw-AUTH-login
    """
    basename = Path(spec_file).stem
    # Sanitize for git branch name
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '-', basename)
    return f"feature/{safe_name}"


def generate_adw_id() -> str:
    """Generate a new unique ADW ID."""
    import uuid
    return f"STANDALONE-{uuid.uuid4().hex[:8].upper()}"


def detect_mode(args: list) -> Tuple[str, dict]:
    """Detect whether we're in standalone or github mode.

    Returns:
        Tuple of (mode, context_dict) where mode is 'standalone' or 'github'
    """
    if len(args) < 2:
        return ('error', {'message': 'Not enough arguments'})

    arg1 = args[1]

    # Check if first arg looks like a file path
    if arg1.endswith('.md'):
        # Standalone mode - spec file provided
        if not os.path.exists(arg1):
            return ('error', {'message': f'Spec file not found: {arg1}'})

        adw_id = None
        if len(args) > 2:
            adw_id = args[2]  # Optional ADW ID override

        if not adw_id:
            adw_id = extract_adw_id_from_spec(arg1)

        if not adw_id:
            adw_id = generate_adw_id()

        return ('standalone', {
            'spec_file': arg1,
            'adw_id': adw_id,
            'branch_name': generate_branch_name_from_spec(arg1),
        })

    # Check if first arg is a path that exists (might not end in .md)
    if os.path.exists(arg1) and os.path.isfile(arg1):
        # Treat as standalone mode
        adw_id = args[2] if len(args) > 2 else extract_adw_id_from_spec(arg1) or generate_adw_id()
        return ('standalone', {
            'spec_file': arg1,
            'adw_id': adw_id,
            'branch_name': generate_branch_name_from_spec(arg1),
        })

    # GitHub mode - issue number and adw-id
    if len(args) < 3:
        return ('error', {'message': 'GitHub mode requires: <issue-number> <adw-id>'})

    return ('github', {
        'issue_number': arg1,
        'adw_id': args[2],
    })


def ensure_branch(branch_name: str, logger: logging.Logger) -> bool:
    """Ensure we're on the correct branch, creating it if needed.

    Returns:
        True if successful, False otherwise
    """
    current = get_current_branch()

    if current == branch_name:
        logger.info(f"Already on branch: {branch_name}")
        return True

    # Try to checkout existing branch
    result = subprocess.run(
        ["git", "checkout", branch_name],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        logger.info(f"Checked out existing branch: {branch_name}")
        return True

    # Branch doesn't exist, create it
    result = subprocess.run(
        ["git", "checkout", "-b", branch_name],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        logger.info(f"Created and checked out new branch: {branch_name}")
        return True

    logger.error(f"Failed to create branch {branch_name}: {result.stderr}")
    return False


def run_standalone_mode(context: dict) -> int:
    """Run build in standalone mode (from spec file, no GitHub issue).

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    spec_file = context['spec_file']
    adw_id = context['adw_id']
    branch_name = context['branch_name']

    logger = setup_logger(adw_id, "adw_build_standalone")
    logger.info(f"ADW Build (Standalone Mode)")
    logger.info(f"  Spec file: {spec_file}")
    logger.info(f"  ADW ID: {adw_id}")
    logger.info(f"  Branch: {branch_name}")

    # Validate environment
    check_env_vars(logger)

    # Load or create state
    state = ADWState.load(adw_id, logger)
    if state:
        logger.info("Found existing state - resuming build")
        # Use branch from state if available
        branch_name = state.get("branch_name") or branch_name
    else:
        logger.info("Creating new state for standalone build")
        state = ADWState(adw_id)
        state.update(
            adw_id=adw_id,
            issue_number=None,
            plan_file=spec_file,
            branch_name=branch_name,
            issue_class="/feature"
        )
        state.save("adw_build_standalone_init")

    # Ensure we're on the correct branch
    if not ensure_branch(branch_name, logger):
        logger.error("Failed to checkout/create branch")
        return 1

    # Implement the plan
    logger.info(f"Implementing plan from: {spec_file}")
    implement_response = implement_plan(spec_file, adw_id, logger)

    if not implement_response.success:
        logger.error(f"Implementation failed: {implement_response.output}")
        return 1

    logger.info("Implementation completed successfully")

    # Create commit message
    commit_msg = f"""feat: Implement {Path(spec_file).stem}

ADW ID: {adw_id}
Spec: {spec_file}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )

    if result.stdout.strip():
        # Stage all changes
        subprocess.run(["git", "add", "-A"], capture_output=True)

        # Commit
        success, error = commit_changes(commit_msg)
        if not success:
            logger.error(f"Commit failed: {error}")
            return 1
        logger.info("Changes committed successfully")
    else:
        logger.info("No changes to commit")

    # Push branch (optional, don't fail if remote not configured)
    result = subprocess.run(
        ["git", "push", "-u", "origin", branch_name],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        logger.info(f"Pushed branch to origin: {branch_name}")
    else:
        logger.warning(f"Could not push to origin (may not be configured): {result.stderr}")

    # Save final state
    state.save("adw_build_standalone_complete")

    print(f"\n✅ Build complete!")
    print(f"   Branch: {branch_name}")
    print(f"   ADW ID: {adw_id}")
    print(f"   State: agents/{adw_id}/adw_state.json")

    return 0


def run_github_mode(context: dict) -> int:
    """Run build in GitHub mode (from issue, with PR updates).

    This is the original adw_build.py behavior.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    issue_number = context['issue_number']
    adw_id = context['adw_id']

    # Try to load existing state
    temp_logger = setup_logger(adw_id, "adw_build")
    state = ADWState.load(adw_id, temp_logger)
    if state:
        # Found existing state - use the issue number from state if available
        issue_number = state.get("issue_number", issue_number)
        make_issue_comment(
            issue_number,
            f"{adw_id}_ops: 🔍 Found existing state - resuming build\n```json\n{json.dumps(state.data, indent=2)}\n```"
        )
    else:
        # No existing state found
        logger = setup_logger(adw_id, "adw_build")
        logger.error(f"No state found for ADW ID: {adw_id}")
        logger.error("Run adw_plan.py first to create the plan and state")
        print(f"\nError: No state found for ADW ID: {adw_id}")
        print("Run adw_plan.py first to create the plan and state")
        print("\nAlternatively, use standalone mode with a spec file:")
        print(f"  uv run adw_build.py specs/your-spec.md")
        return 1

    # Set up logger with ADW ID from command line
    logger = setup_logger(adw_id, "adw_build")
    logger.info(f"ADW Build (GitHub Mode) - ID: {adw_id}, Issue: {issue_number}")

    # Validate environment
    check_env_vars(logger)

    # Get repo information
    try:
        github_repo_url = get_repo_url()
        repo_path = extract_repo_path(github_repo_url)
    except ValueError as e:
        logger.error(f"Error getting repository URL: {e}")
        return 1

    # Ensure we have required state fields
    if not state.get("branch_name"):
        error_msg = "No branch name in state - run adw_plan.py first"
        logger.error(error_msg)
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", f"❌ {error_msg}")
        )
        return 1

    if not state.get("plan_file"):
        error_msg = "No plan file in state - run adw_plan.py first"
        logger.error(error_msg)
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", f"❌ {error_msg}")
        )
        return 1

    # Checkout the branch from state
    branch_name = state.get("branch_name")
    result = subprocess.run(["git", "checkout", branch_name], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Failed to checkout branch {branch_name}: {result.stderr}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", f"❌ Failed to checkout branch {branch_name}")
        )
        return 1
    logger.info(f"Checked out branch: {branch_name}")

    # Get the plan file from state
    plan_file = state.get("plan_file")
    logger.info(f"Using plan file: {plan_file}")

    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", "✅ Starting implementation phase")
    )

    # Implement the plan
    logger.info("Implementing solution")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Implementing solution")
    )

    implement_response = implement_plan(plan_file, adw_id, logger)

    if not implement_response.success:
        logger.error(f"Error implementing solution: {implement_response.output}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_IMPLEMENTOR, f"❌ Error implementing solution: {implement_response.output}")
        )
        return 1

    logger.debug(f"Implementation response: {implement_response.output}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Solution implemented")
    )

    # Fetch issue data for commit message generation
    logger.info("Fetching issue data for commit message")
    issue = fetch_issue(issue_number, repo_path)

    # Get issue classification from state or classify if needed
    issue_command = state.get("issue_class")
    if not issue_command:
        logger.info("No issue classification in state, running classify_issue")
        from adw_modules.workflow_ops import classify_issue
        issue_command, error = classify_issue(issue, adw_id, logger)
        if error:
            logger.error(f"Error classifying issue: {error}")
            # Default to feature if classification fails
            issue_command = "/feature"
            logger.warning("Defaulting to /feature after classification error")
        else:
            # Save the classification for future use
            state.update(issue_class=issue_command)
            state.save("adw_build")

    # Create commit message
    logger.info("Creating implementation commit")
    commit_msg, error = create_commit(AGENT_IMPLEMENTOR, issue, issue_command, adw_id, logger)

    if error:
        logger.error(f"Error creating commit message: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_IMPLEMENTOR, f"❌ Error creating commit message: {error}")
        )
        return 1

    # Commit the implementation
    success, error = commit_changes(commit_msg)

    if not success:
        logger.error(f"Error committing implementation: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_IMPLEMENTOR, f"❌ Error committing implementation: {error}")
        )
        return 1

    logger.info(f"Committed implementation: {commit_msg}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_IMPLEMENTOR, "✅ Implementation committed")
    )

    # Finalize git operations (push and PR)
    finalize_git_operations(state, logger)

    logger.info("Implementation phase completed successfully")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", "✅ Implementation phase completed")
    )

    # Save final state
    state.save("adw_build")

    return 0


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Detect mode from arguments
    mode, context = detect_mode(sys.argv)

    if mode == 'error':
        print("Usage:")
        print("  STANDALONE: uv run adw_build.py <spec-file.md> [adw-id]")
        print("  GITHUB:     uv run adw_build.py <issue-number> <adw-id>")
        print("")
        print("Examples:")
        print("  uv run adw_build.py specs/gemini-file-search-v1.md")
        print("  uv run adw_build.py specs/my-feature.md MY-FEATURE-ID")
        print("  uv run adw_build.py 123 FEATURE-AUTH")
        print("")
        if 'message' in context:
            print(f"Error: {context['message']}")
        sys.exit(1)

    if mode == 'standalone':
        exit_code = run_standalone_mode(context)
    else:  # mode == 'github'
        exit_code = run_github_mode(context)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
