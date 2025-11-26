#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Patch - AI Developer Workflow for single-issue patches

Usage:
  uv run adw_patch.py <issue-number> [adw-id]

Workflow:
1. Fetch GitHub issue details
2. Check for 'adw_patch' keyword in comments or issue body
3. Create patch plan based on content containing 'adw_patch'
4. Implement the patch plan
5. Commit changes
6. Push and create/update PR

This workflow requires 'adw_patch' keyword to be present either in:
- A comment on the issue (uses latest comment containing keyword)
- The issue body itself (uses issue title + body)
"""

import sys
import os
import logging
import json
import subprocess
from typing import Optional
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.git_ops import commit_changes, finalize_git_operations
from adw_modules.github import (
    fetch_issue,
    make_issue_comment,
    get_repo_url,
    extract_repo_path,
    find_keyword_from_comment,
)
from adw_modules.workflow_ops import (
    create_commit,
    format_issue_message,
    ensure_adw_id,
    implement_plan,
    create_and_implement_patch,
    create_or_find_branch,
    AGENT_IMPLEMENTOR,
)
from adw_modules.utils import setup_logger
from adw_modules.data_types import (
    GitHubIssue,
    AgentTemplateRequest,
    AgentPromptResponse,
)
from adw_modules.agent import execute_template

# Agent name constants
AGENT_PATCH_PLANNER = "patch_planner"
AGENT_PATCH_IMPLEMENTOR = "patch_implementor"


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


def get_patch_content(
    issue: GitHubIssue, issue_number: str, adw_id: str, logger: logging.Logger
) -> str:
    """Get patch content from either issue comments or body containing 'adw_patch'.

    Args:
        issue: The GitHub issue
        issue_number: Issue number for comments
        adw_id: ADW ID for formatting messages
        logger: Logger instance

    Returns:
        The patch content to use for creating the patch plan

    Raises:
        SystemExit: If 'adw_patch' keyword is not found
    """
    # First, check for the latest comment containing 'adw_patch'
    keyword_comment = find_keyword_from_comment("adw_patch", issue)

    if keyword_comment:
        # Use the comment body as the review change request
        logger.info(
            f"Found 'adw_patch' in comment, using comment body: {keyword_comment.body}"
        )
        review_change_request = keyword_comment.body
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                AGENT_PATCH_PLANNER,
                f"✅ Creating patch plan from comment containing 'adw_patch':\n\n```\n{keyword_comment.body}\n```",
            ),
        )
        return review_change_request
    elif "adw_patch" in issue.body:
        # Use issue title and body as the review change request
        logger.info("Found 'adw_patch' in issue body, using issue title and body")
        review_change_request = f"Issue #{issue.number}: {issue.title}\n\n{issue.body}"
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                AGENT_PATCH_PLANNER,
                "✅ Creating patch plan from issue containing 'adw_patch'",
            ),
        )
        return review_change_request
    else:
        # No 'adw_patch' keyword found, exit
        logger.error("No 'adw_patch' keyword found in issue body or comments")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                "ops",
                "❌ No 'adw_patch' keyword found in issue body or comments. Add 'adw_patch' to trigger patch workflow.",
            ),
        )
        sys.exit(1)


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage: uv run adw_patch.py <issue-number> [adw-id]")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Ensure ADW ID exists with initialized state
    temp_logger = setup_logger(adw_id, "adw_patch") if adw_id else None
    adw_id = ensure_adw_id(issue_number, adw_id, temp_logger)

    # Load the state that was created/found by ensure_adw_id
    state = ADWState.load(adw_id, temp_logger)

    # Ensure state has the adw_id field
    if not state.get("adw_id"):
        state.update(adw_id=adw_id)

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_patch")
    logger.info(f"ADW Patch starting - ID: {adw_id}, Issue: {issue_number}")

    # Validate environment
    check_env_vars(logger)

    # Get repo information
    try:
        github_repo_url = get_repo_url()
        repo_path = extract_repo_path(github_repo_url)
    except ValueError as e:
        logger.error(f"Error getting repository URL: {e}")
        sys.exit(1)

    # Fetch issue details
    issue: GitHubIssue = fetch_issue(issue_number, repo_path)

    logger.debug(f"Fetched issue: {issue.model_dump_json(indent=2, by_alias=True)}")
    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting patch workflow")
    )

    make_issue_comment(
        issue_number,
        f"{adw_id}_ops: 🔍 Using state\n```json\n{json.dumps(state.data, indent=2)}\n```",
    )

    # Create or find branch for the issue
    branch_name, error = create_or_find_branch(issue_number, issue, state, logger)

    if error:
        logger.error(f"Error with branch: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", f"❌ Error with branch: {error}"),
        )
        sys.exit(1)

    # State is already updated by create_or_find_branch
    state.save("adw_patch")
    logger.info(f"Working on branch: {branch_name}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Working on branch: {branch_name}"),
    )

    # Get patch content from issue or comments containing 'adw_patch'
    logger.info("Checking for 'adw_patch' keyword")
    review_change_request = get_patch_content(issue, issue_number, adw_id, logger)

    # Use the shared method to create and implement patch
    patch_file, implement_response = create_and_implement_patch(
        adw_id=adw_id,
        review_change_request=review_change_request,
        logger=logger,
        agent_name_planner=AGENT_PATCH_PLANNER,
        agent_name_implementor=AGENT_PATCH_IMPLEMENTOR,
        spec_path=None,  # No spec file for direct issue patches
    )

    if not patch_file:
        logger.error("Failed to create patch plan")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, AGENT_PATCH_PLANNER, "❌ Failed to create patch plan"
            ),
        )
        sys.exit(1)

    state.update(patch_file=patch_file)
    state.save("adw_patch")
    logger.info(f"Patch plan created: {patch_file}")
    make_issue_comment(
        issue_number,
        format_issue_message(
            adw_id, AGENT_PATCH_PLANNER, f"✅ Patch plan created: {patch_file}"
        ),
    )

    if not implement_response.success:
        logger.error(f"Error implementing patch: {implement_response.output}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                AGENT_PATCH_IMPLEMENTOR,
                f"❌ Error implementing patch: {implement_response.output}",
            ),
        )
        sys.exit(1)

    logger.debug(f"Implementation response: {implement_response.output}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_PATCH_IMPLEMENTOR, "✅ Patch implemented"),
    )

    # Create commit message
    logger.info("Creating patch commit")

    issue_command = "/patch"
    commit_msg, error = create_commit(
        AGENT_PATCH_IMPLEMENTOR, issue, issue_command, adw_id, logger
    )

    if error:
        logger.error(f"Error creating commit message: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, AGENT_PATCH_IMPLEMENTOR, f"❌ Error creating commit message: {error}"
            ),
        )
        sys.exit(1)

    # Commit the patch
    success, error = commit_changes(commit_msg)

    if not success:
        logger.error(f"Error committing patch: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, AGENT_PATCH_IMPLEMENTOR, f"❌ Error committing patch: {error}"
            ),
        )
        sys.exit(1)

    logger.info(f"Committed patch: {commit_msg}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_PATCH_IMPLEMENTOR, "✅ Patch committed"),
    )

    # Finalize git operations (push and PR)
    finalize_git_operations(state, logger)

    logger.info("Patch workflow completed successfully")
    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Patch workflow completed")
    )

    # Save final state
    state.save("adw_patch")

    # Post final state summary to issue
    make_issue_comment(
        issue_number,
        f"{adw_id}_ops: 📋 Final patch state:\n```json\n{json.dumps(state.data, indent=2)}\n```",
    )


if __name__ == "__main__":
    main()
