#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic", "boto3>=1.26.0"]
# ///

"""
ADW Review - AI Developer Workflow for agentic review

Usage:
  uv run adw_review.py <issue-number> <adw-id> [--skip-resolution]

Workflow:
1. Find spec file from current branch
2. Review implementation against specification
3. Capture screenshots of critical functionality
4. If issues found and --skip-resolution not set:
   - Create patch plans for issues
   - Implement resolutions
5. Post results as commit message
6. Commit review results
7. Push and update PR
"""

import sys
import os
import logging
import json
import subprocess
from typing import Optional, List, Tuple
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.git_ops import commit_changes, finalize_git_operations
from adw_modules.github import (
    fetch_issue,
    make_issue_comment,
    get_repo_url,
    extract_repo_path,
)
from adw_modules.workflow_ops import (
    create_commit,
    format_issue_message,
    ensure_adw_id,
    implement_plan,
    create_and_implement_patch,
    find_spec_file,
    AGENT_IMPLEMENTOR,
)
from adw_modules.utils import setup_logger, parse_json
from adw_modules.data_types import (
    GitHubIssue,
    AgentTemplateRequest,
    ReviewResult,
    ReviewIssue,
    AgentPromptResponse,
)
from adw_modules.agent import execute_template
from adw_modules.r2_uploader import R2Uploader

# Agent name constants
AGENT_REVIEWER = "reviewer"
AGENT_REVIEW_PATCH_PLANNER = "review_patch_planner"
AGENT_REVIEW_PATCH_IMPLEMENTOR = "review_patch_implementor"

# Maximum number of review retry attempts after resolution
MAX_REVIEW_RETRY_ATTEMPTS = 3


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


def run_review(
    spec_file: str,
    adw_id: str,
    logger: logging.Logger,
) -> ReviewResult:
    """Run the review using the /review command."""
    request = AgentTemplateRequest(
        agent_name=AGENT_REVIEWER,
        slash_command="/review",
        args=[adw_id, spec_file, AGENT_REVIEWER],
        adw_id=adw_id,
    )

    logger.debug(f"Review request: {request.model_dump_json(indent=2, by_alias=True)}")

    response = execute_template(request)

    logger.debug(
        f"Review response: {response.model_dump_json(indent=2, by_alias=True)}"
    )

    if not response.success:
        logger.error(f"Error running review: {response.output}")
        # Return a failed review result
        return ReviewResult(
            success=False,
            review_issues=[
                ReviewIssue(
                    review_issue_number=1,
                    screenshot_path="",
                    issue_description=f"Review execution failed: {response.output}",
                    issue_resolution="Fix the review execution error",
                    issue_severity="blocker",
                )
            ],
        )

    # Parse the review result
    try:
        result = parse_json(response.output, ReviewResult)
        return result
    except Exception as e:
        logger.error(f"Error parsing review result: {e}")
        return ReviewResult(
            success=False,
            review_issues=[
                ReviewIssue(
                    review_issue_number=1,
                    screenshot_path="",
                    issue_description=f"Failed to parse review result: {str(e)}",
                    issue_resolution="Fix the review output format",
                    issue_severity="blocker",
                )
            ],
        )


def resolve_review_issues(
    review_issues: List[ReviewIssue],
    spec_file: str,
    state: ADWState,
    logger: logging.Logger,
    issue_number: str,
    iteration: int = 1,
) -> Tuple[int, int]:
    """Resolve review issues by creating and implementing patch plans.
    Returns (resolved_count, failed_count)."""

    resolved_count = 0
    failed_count = 0
    adw_id = state.get("adw_id")

    # Filter to only handle blocker issues
    blocker_issues = [i for i in review_issues if i.issue_severity == "blocker"]

    if not blocker_issues:
        logger.info("No blocker issues to resolve")
        return 0, 0

    logger.info(f"Found {len(blocker_issues)} blocker issues to resolve")
    make_issue_comment(
        issue_number,
        format_issue_message(
            adw_id,
            "ops",
            f"🔧 Attempting to resolve {len(blocker_issues)} blocker issues",
        ),
    )

    for idx, issue in enumerate(blocker_issues):
        logger.info(
            f"\n=== Resolving blocker issue {idx + 1}/{len(blocker_issues)}: Issue #{issue.review_issue_number} ==="
        )

        # Create and implement patch
        # Prepare unique agent names with iteration and issue number for tracking
        agent_name_planner = f"{AGENT_REVIEW_PATCH_PLANNER}_{iteration}_{issue.review_issue_number}"
        agent_name_implementor = f"{AGENT_REVIEW_PATCH_IMPLEMENTOR}_{iteration}_{issue.review_issue_number}"
        
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                agent_name_planner,
                f"📝 Creating patch plan for issue #{issue.review_issue_number}: {issue.issue_description}",
            ),
        )

        # Format the review change request from the issue
        review_change_request = f"{issue.issue_description}\n\nSuggested resolution: {issue.issue_resolution}"

        # Prepare screenshots
        screenshots = issue.screenshot_path if issue.screenshot_path else None

        # Use the shared method to create and implement patch
        patch_file, implement_response = create_and_implement_patch(
            adw_id=adw_id,
            review_change_request=review_change_request,
            logger=logger,
            agent_name_planner=agent_name_planner,
            agent_name_implementor=agent_name_implementor,
            spec_path=spec_file,
            issue_screenshots=screenshots,
        )

        if not patch_file:
            failed_count += 1
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    agent_name_planner,
                    f"❌ Failed to create patch plan for issue #{issue.review_issue_number}",
                ),
            )
            continue

        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, agent_name_planner, f"✅ Created patch plan: {patch_file}"
            ),
        )

        # Check implementation result
        if implement_response.success:
            resolved_count += 1
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    agent_name_implementor,
                    f"✅ Successfully resolved issue #{issue.review_issue_number}",
                ),
            )
            logger.info(f"Successfully resolved issue #{issue.review_issue_number}")
        else:
            failed_count += 1
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    agent_name_implementor,
                    f"❌ Failed to implement patch for issue #{issue.review_issue_number}: {implement_response.output}",
                ),
            )
            logger.error(
                f"Failed to implement patch for issue #{issue.review_issue_number}"
            )

    return resolved_count, failed_count


def upload_and_map_screenshots(
    review_result: ReviewResult,
    r2_uploader: R2Uploader,
    adw_id: str,
    state: ADWState,
    logger: logging.Logger,
) -> None:
    """
    Upload screenshots to R2 and populate URL fields in the review result.
    
    Preserves original file paths and adds public URLs in separate fields:
    - ReviewResult.screenshot_urls (indexed-aligned with screenshots)
    - ReviewIssue.screenshot_url
    
    Args:
        review_result: The review result containing screenshots to upload
        r2_uploader: R2Uploader instance
        adw_id: ADW workflow ID
        state: ADWState instance for saving screenshot URLs
        logger: Logger instance
    """
    # Upload screenshots to R2 if available
    if review_result.screenshots or any(
        issue.screenshot_path for issue in review_result.review_issues
    ):
        logger.info("Uploading review screenshots to R2")

        # Collect all screenshot paths
        all_screenshots = list(review_result.screenshots)
        for review_issue in review_result.review_issues:
            if review_issue.screenshot_path:
                all_screenshots.append(review_issue.screenshot_path)

        # Upload and get URL mapping
        url_mapping = r2_uploader.upload_screenshots(all_screenshots, adw_id)

        # Populate screenshot_urls for ReviewResult (indexed-aligned with screenshots)
        review_result.screenshot_urls = [
            url_mapping.get(path, "") for path in review_result.screenshots
        ]

        # Populate screenshot_url for each ReviewIssue
        for review_issue in review_result.review_issues:
            if review_issue.screenshot_path:
                review_issue.screenshot_url = url_mapping.get(
                    review_issue.screenshot_path, None
                )

        logger.info(
            f"Screenshot upload complete - {len(url_mapping)} files processed"
        )

    # Save screenshot URLs to state for documentation workflow
    if review_result.screenshot_urls:
        state.update(review_screenshots=review_result.screenshot_urls)
        state.save("adw_review")
        logger.info(
            f"Saved {len(review_result.screenshot_urls)} screenshot URLs to state for documentation"
        )


def format_review_comment(review_result: ReviewResult) -> str:
    """Format review result for GitHub issue comment."""
    parts = []

    if review_result.success:
        parts.append("## ✅ Review Passed")
        parts.append("")
        parts.append("The implementation matches the specification.")
        parts.append("")

        if review_result.screenshot_urls:
            parts.append("### Screenshots")
            parts.append("")
            for i, screenshot_url in enumerate(review_result.screenshot_urls):
                if screenshot_url:  # Only show if URL was successfully generated
                    filename = screenshot_url.split("/")[-1]
                    parts.append(f"![{filename}]({screenshot_url})")
            parts.append("")
    else:
        parts.append("## ❌ Review Issues Found")
        parts.append("")
        parts.append(f"Found {len(review_result.review_issues)} issues during review:")
        parts.append("")

        # Group by severity
        blockers = [
            i for i in review_result.review_issues if i.issue_severity == "blocker"
        ]
        tech_debts = [
            i for i in review_result.review_issues if i.issue_severity == "tech_debt"
        ]
        skippables = [
            i for i in review_result.review_issues if i.issue_severity == "skippable"
        ]

        if blockers:
            parts.append("### 🚨 Blockers")
            parts.append("")
            for issue in blockers:
                parts.append(
                    f"**Issue #{issue.review_issue_number}**: {issue.issue_description}"
                )
                parts.append(f"- **Resolution**: {issue.issue_resolution}")
                if issue.screenshot_url:
                    filename = issue.screenshot_url.split("/")[-1]
                    parts.append(f"- **Screenshot**:")
                    parts.append(f"  ![{filename}]({issue.screenshot_url})")
                parts.append("")

        if tech_debts:
            parts.append("### ⚠️ Tech Debt")
            parts.append("")
            for issue in tech_debts:
                parts.append(
                    f"**Issue #{issue.review_issue_number}**: {issue.issue_description}"
                )
                parts.append(f"- **Resolution**: {issue.issue_resolution}")
                if issue.screenshot_url:
                    filename = issue.screenshot_url.split("/")[-1]
                    parts.append(f"- **Screenshot**:")
                    parts.append(f"  ![{filename}]({issue.screenshot_url})")
                parts.append("")

        if skippables:
            parts.append("### ℹ️ Skippable")
            parts.append("")
            for issue in skippables:
                parts.append(
                    f"**Issue #{issue.review_issue_number}**: {issue.issue_description}"
                )
                parts.append(f"- **Resolution**: {issue.issue_resolution}")
                if issue.screenshot_url:
                    filename = issue.screenshot_url.split("/")[-1]
                    parts.append(f"- **Screenshot**:")
                    parts.append(f"  ![{filename}]({issue.screenshot_url})")
                parts.append("")

    # Add JSON payload
    parts.append("### Review Data")
    parts.append("")
    parts.append("```json")
    parts.append(review_result.model_dump_json(indent=2))
    parts.append("```")

    return "\n".join(parts)


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Check for --skip-resolution flag
    skip_resolution = "--skip-resolution" in sys.argv
    if skip_resolution:
        sys.argv.remove("--skip-resolution")

    # Parse command line args
    # adw-id is REQUIRED for review to find the correct state and spec
    if len(sys.argv) < 3:
        print("Usage: uv run adw_review.py <issue-number> <adw-id> [--skip-resolution]")
        print("\nError: adw-id is required to locate the spec file and state")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2]

    # Try to load existing state
    temp_logger = setup_logger(adw_id, "adw_review")
    state = ADWState.load(adw_id, temp_logger)
    if state:
        # Found existing state
        issue_number = state.get("issue_number", issue_number)
        make_issue_comment(
            issue_number,
            f"{adw_id}_ops: 🔍 Found existing state - starting review\n```json\n{json.dumps(state.data, indent=2)}\n```",
        )
    else:
        # No existing state found
        logger = setup_logger(adw_id, "adw_review")
        logger.error(f"No state found for ADW ID: {adw_id}")
        logger.error("Run adw_plan.py first to create the state")
        print(f"\nError: No state found for ADW ID: {adw_id}")
        print("Run adw_plan.py first to create the state")
        sys.exit(1)

    # Set up logger with ADW ID from command line
    logger = setup_logger(adw_id, "adw_review")
    logger.info(f"ADW Review starting - ID: {adw_id}, Issue: {issue_number}")

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
            issue_number, format_issue_message(adw_id, "ops", f"❌ {error_msg}")
        )
        sys.exit(1)

    # Checkout the branch from state
    branch_name = state.get("branch_name")
    result = subprocess.run(
        ["git", "checkout", branch_name], capture_output=True, text=True
    )
    if result.returncode != 0:
        logger.error(f"Failed to checkout branch {branch_name}: {result.stderr}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, "ops", f"❌ Failed to checkout branch {branch_name}"
            ),
        )
        sys.exit(1)
    logger.info(f"Checked out branch: {branch_name}")

    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting review phase")
    )

    # Find the spec file
    spec_file = find_spec_file(state, logger)
    if not spec_file:
        error_msg = "Could not find spec file for review"
        logger.error(error_msg)
        make_issue_comment(
            issue_number, format_issue_message(adw_id, "ops", f"❌ {error_msg}")
        )
        sys.exit(1)

    logger.info(f"Using spec file: {spec_file}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, "ops", f"✅ Found spec file: {spec_file}"),
    )

    # Initialize R2 uploader
    r2_uploader = R2Uploader(logger)

    # Run review with resolution retry loop
    attempt = 0
    max_attempts = MAX_REVIEW_RETRY_ATTEMPTS if not skip_resolution else 1

    while attempt < max_attempts:
        attempt += 1
        logger.info(f"\n=== Review Attempt {attempt}/{max_attempts} ===")

        # Run the review
        logger.info("Running review against specification")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                AGENT_REVIEWER,
                f"✅ Reviewing implementation against specification (attempt {attempt}/{max_attempts})",
            ),
        )

        review_result = run_review(spec_file, adw_id, logger)

        # Upload screenshots and update URLs
        upload_and_map_screenshots(review_result, r2_uploader, adw_id, state, logger)

        # Format and post review results
        review_comment = format_review_comment(review_result)
        make_issue_comment(
            issue_number, format_issue_message(adw_id, AGENT_REVIEWER, review_comment)
        )

        # Log summary
        if review_result.success:
            logger.info(
                "Review passed - implementation matches specification (no blocking issues)"
            )
            break
        else:
            blocker_count = sum(
                1 for i in review_result.review_issues if i.issue_severity == "blocker"
            )
            logger.warning(
                f"Review found {len(review_result.review_issues)} issues ({blocker_count} blockers)"
            )

            # If this is the last attempt or no blockers or resolution is skipped, stop
            if attempt == max_attempts or blocker_count == 0 or skip_resolution:
                if skip_resolution and blocker_count > 0:
                    logger.info(
                        f"Skipping resolution workflow for {blocker_count} blocker issues (--skip-resolution flag set)"
                    )
                    make_issue_comment(
                        issue_number,
                        format_issue_message(
                            adw_id,
                            "ops",
                            f"⚠️ Skipping resolution for {blocker_count} blocker issues",
                        ),
                    )
                break

            # Resolution workflow
            logger.info("\n=== Starting resolution workflow ===")
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    "ops",
                    f"🔧 Starting resolution workflow for {blocker_count} blocker issues",
                ),
            )

            # Resolve the issues
            resolved_count, failed_count = resolve_review_issues(
                review_result.review_issues,
                spec_file,
                state,
                logger,
                issue_number,
                iteration=attempt,
            )

            # Report resolution results
            if resolved_count > 0:
                make_issue_comment(
                    issue_number,
                    format_issue_message(
                        adw_id,
                        "ops",
                        f"✅ Resolution complete: {resolved_count} issues resolved, {failed_count} failed",
                    ),
                )

                # Commit the resolution changes
                logger.info("Committing resolution changes")
                review_issue = fetch_issue(issue_number, repo_path)
                issue_command = state.get("issue_class", "/chore")

                # Use a generic review patch implementor name for the commit
                commit_msg, error = create_commit(
                    AGENT_REVIEW_PATCH_IMPLEMENTOR, review_issue, issue_command, adw_id, logger
                )

                if not error:
                    success, error = commit_changes(commit_msg)
                    if success:
                        logger.info(f"Committed resolution: {commit_msg}")
                        make_issue_comment(
                            issue_number,
                            format_issue_message(
                                adw_id,
                                AGENT_REVIEW_PATCH_IMPLEMENTOR,
                                "✅ Resolution changes committed",
                            ),
                        )
                    else:
                        logger.error(f"Error committing resolution: {error}")
                        make_issue_comment(
                            issue_number,
                            format_issue_message(
                                adw_id,
                                AGENT_REVIEW_PATCH_IMPLEMENTOR,
                                f"❌ Error committing resolution: {error}",
                            ),
                        )

                # Continue to next iteration to re-review
                logger.info(
                    f"\n=== Preparing for re-review after resolving {resolved_count} issues ==="
                )
                make_issue_comment(
                    issue_number,
                    format_issue_message(
                        adw_id,
                        AGENT_REVIEWER,
                        f"🔄 Re-running review (attempt {attempt + 1}/{max_attempts})...",
                    ),
                )
            else:
                # No issues were resolved, no point in retrying
                logger.info("No issues were resolved, stopping retry attempts")
                make_issue_comment(
                    issue_number,
                    format_issue_message(
                        adw_id,
                        "ops",
                        f"❌ Resolution failed: Could not resolve any of the {blocker_count} blocker issues",
                    ),
                )
                break

    # Log final attempt status
    if attempt == max_attempts and not review_result.success:
        blocker_count = sum(
            1 for i in review_result.review_issues if i.issue_severity == "blocker"
        )
        if blocker_count > 0:
            logger.warning(
                f"Reached maximum retry attempts ({max_attempts}) with {blocker_count} blocking issues remaining"
            )
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    "ops",
                    f"⚠️ Reached maximum retry attempts ({max_attempts}) with {blocker_count} blocking issues",
                ),
            )

    logger.info("Fetching issue data for commit message")
    review_issue = fetch_issue(issue_number, repo_path)

    # Get issue classification from state
    issue_command = state.get("issue_class", "/chore")

    # Create commit message
    logger.info("Creating review commit")
    commit_msg, error = create_commit(
        AGENT_REVIEWER, review_issue, issue_command, adw_id, logger
    )

    if error:
        logger.error(f"Error creating commit message: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, AGENT_REVIEWER, f"❌ Error creating commit message: {error}"
            ),
        )
        sys.exit(1)

    # Commit the review results
    success, error = commit_changes(commit_msg)

    if not success:
        logger.error(f"Error committing review: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, AGENT_REVIEWER, f"❌ Error committing review: {error}"
            ),
        )
        sys.exit(1)

    logger.info(f"Committed review: {commit_msg}")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_REVIEWER, "✅ Review committed"),
    )

    # Finalize git operations (push and PR)
    finalize_git_operations(state, logger)

    logger.info("Review phase completed successfully")
    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Review phase completed")
    )

    # Save final state
    state.save("adw_review")

    # Output state for chaining
    state.to_stdout()

    # Exit with appropriate code based on review result
    if not review_result.success:
        blocker_count = sum(
            1 for i in review_result.review_issues if i.issue_severity == "blocker"
        )
        if blocker_count > 0:
            logger.error(f"Review failed with {blocker_count} blocking issues")
            sys.exit(1)
        else:
            logger.warning("Review found non-blocking issues")
            # Exit successfully since no blockers


if __name__ == "__main__":
    main()
