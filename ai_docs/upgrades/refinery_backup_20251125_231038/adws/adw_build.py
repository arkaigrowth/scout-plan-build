#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Build - AI Developer Workflow for agentic building

Usage: 
  uv run adw_build.py <issue-number> <adw-id>

Workflow:
1. Find existing plan (from state or by searching)
2. Implement the solution based on plan
3. Commit implementation
4. Push and update PR
"""

import sys
import os
import logging
import json
import subprocess
from typing import Optional
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
        "CLAUDE_CODE_PATH",
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


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line args
    # INTENTIONAL: adw-id is REQUIRED - we cannot search for it because:
    # 1. The plan file is stored in state and identified by adw-id
    # 2. Multiple ADW runs for the same issue could exist
    # 3. We need to know exactly which plan to implement
    if len(sys.argv) < 3:
        print("Usage: uv run adw_build.py <issue-number> <adw-id>")
        print("\nError: adw-id is required to locate the plan file created by adw_plan.py")
        print("The plan file is stored at: specs/issue-{issue_number}-adw-{adw_id}-*.md")
        sys.exit(1)
    
    issue_number = sys.argv[1]
    adw_id = sys.argv[2]
    
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
        sys.exit(1)
    
    # Set up logger with ADW ID from command line
    logger = setup_logger(adw_id, "adw_build")
    logger.info(f"ADW Build starting - ID: {adw_id}, Issue: {issue_number}")
    
    # Validate environment
    check_env_vars(logger)
    
    # Get repo information
    try:
        github_repo_url = get_repo_url()
        repo_path = extract_repo_path(github_repo_url)
    except ValueError as e:
        logger.error(f"Error getting repository URL: {e}")
        sys.exit(1)
    
    # Ensure we have required state fields
    if not state.get("branch_name"):
        error_msg = "No branch name in state - run adw_plan.py first"
        logger.error(error_msg)
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", f"❌ {error_msg}")
        )
        sys.exit(1)
    
    if not state.get("plan_file"):
        error_msg = "No plan file in state - run adw_plan.py first"
        logger.error(error_msg)
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", f"❌ {error_msg}")
        )
        sys.exit(1)
    
    # Checkout the branch from state
    branch_name = state.get("branch_name")
    result = subprocess.run(["git", "checkout", branch_name], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Failed to checkout branch {branch_name}: {result.stderr}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", f"❌ Failed to checkout branch {branch_name}")
        )
        sys.exit(1)
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
        sys.exit(1)
    
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
        sys.exit(1)
    
    # Commit the implementation
    success, error = commit_changes(commit_msg)
    
    if not success:
        logger.error(f"Error committing implementation: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_IMPLEMENTOR, f"❌ Error committing implementation: {error}")
        )
        sys.exit(1)
    
    # Log commit (don't store in state as it's not a core field)
    
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


if __name__ == "__main__":
    main()