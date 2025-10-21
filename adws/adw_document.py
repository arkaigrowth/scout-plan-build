#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Document - AI Developer Workflow for documentation generation

Usage: 
  uv run adw_document.py <issue-number> <adw-id>

Workflow:
1. Find spec file from current branch
2. Analyze git changes
3. Generate feature documentation
4. Update conditional docs
5. Commit documentation
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
from adw_modules.github import fetch_issue, make_issue_comment, get_repo_url, extract_repo_path
from adw_modules.workflow_ops import (
    create_commit,
    format_issue_message,
    find_spec_file,
)
from adw_modules.utils import setup_logger
from adw_modules.data_types import GitHubIssue, AgentTemplateRequest, DocumentationResult, IssueClassSlashCommand
from adw_modules.agent import execute_template

# Agent name constant
AGENT_DOCUMENTER = "documenter"


def check_env_vars(logger: Optional[logging.Logger] = None) -> None:
    """Check that all required environment variables are set."""
    required_vars = [
        "ANTHROPIC_API_KEY",
        "CLAUDE_CODE_PATH",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        if logger:
            logger.error(msg)
        else:
            print(f"Error: {msg}")
        sys.exit(1)



def check_for_changes(logger: logging.Logger) -> bool:
    """Check if there are any changes between current branch and origin/main.
    
    Returns:
        bool: True if changes exist, False if no changes
    """
    try:
        # Check for changes against origin/main
        result = subprocess.run(
            ["git", "diff", "origin/main", "--stat"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # If output is empty or only whitespace, no changes
        has_changes = bool(result.stdout.strip())
        
        if not has_changes:
            logger.info("No changes detected between current branch and origin/main")
        else:
            logger.info(f"Found changes:\n{result.stdout}")
        
        return has_changes
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to check for changes: {e}")
        # If we can't check, assume there are changes and let the agent handle it
        return True


def generate_documentation(
    issue_number: str,
    adw_id: str,
    logger: logging.Logger,
    state: ADWState,
) -> DocumentationResult:
    """Generate documentation for completed feature.
    
    Returns:
        DocumentationResult: Result object containing success status and documentation details
    """
    try:
        # Check for changes first
        if not check_for_changes(logger):
            logger.info("No changes to document - skipping documentation generation")
            
            # Post comment about no changes
            try:
                make_issue_comment(
                    issue_number,
                    format_issue_message(
                        adw_id, 
                        "ops", 
                        "ℹ️ No changes detected between current branch and origin/main - skipping documentation generation"
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to post no-changes comment: {e}")
            
            return DocumentationResult(
                success=True,
                documentation_created=False,
                documentation_path=None,
                error_message=None
            )
        
        # Find spec file from state
        spec_path = find_spec_file(state, logger)
        
        # Get screenshots from state or find review_img directory
        screenshots = state.get("review_screenshots", [])
        screenshots_dir = ""
        
        if screenshots:
            # Extract directory from first screenshot path
            first_screenshot = screenshots[0]
            screenshots_dir = os.path.dirname(first_screenshot)
            logger.info(f"Found {len(screenshots)} screenshots in state, directory: {screenshots_dir}")
        else:
            # Fallback to checking review_img directory
            review_img_dir = f"agents/{adw_id}/reviewer/review_img"
            if os.path.exists(review_img_dir) and os.listdir(review_img_dir):
                screenshots_dir = review_img_dir
                logger.info(f"Found screenshots in fallback directory: {review_img_dir}")
        
        # Prepare arguments for document command
        args = [adw_id]
        if spec_path:
            args.append(spec_path)
        else:
            args.append("")  # Empty spec_path
        
        if screenshots_dir:
            args.append(screenshots_dir)
        
        # Execute document command
        request = AgentTemplateRequest(
            agent_name=AGENT_DOCUMENTER,
            slash_command="/document",
            args=args,
            adw_id=adw_id,
        )
        
        logger.info(f"Executing /document command with args: {args}")
        response = execute_template(request)
        
        if response.success:
            # Extract documentation path from response
            documentation_path = response.output.strip()
            logger.info(f"Documentation generated successfully: {documentation_path}")
            
            # Documentation generated successfully - commit will happen in main()
            
            return DocumentationResult(
                success=True,
                documentation_created=True,
                documentation_path=documentation_path,
                error_message=None
            )
        else:
            logger.error(f"Documentation generation failed: {response.output}")
            return DocumentationResult(
                success=False,
                documentation_created=False,
                documentation_path=None,
                error_message=f"Documentation generation failed: {response.output}"
            )
            
    except Exception as e:
        logger.error(f"Error generating documentation: {e}", exc_info=True)
        return DocumentationResult(
            success=False,
            documentation_created=False,
            documentation_path=None,
            error_message=f"Error generating documentation: {str(e)}"
        )


def main():
    """Main entry point."""
    load_dotenv()
    
    # Parse arguments
    # INTENTIONAL: adw-id is REQUIRED - we cannot create documentation without prior workflow
    if len(sys.argv) < 3:
        print("Usage: uv run adw_document.py <issue-number> <adw-id>")
        print("\nError: adw-id is required to locate the review and implementation artifacts")
        print("Documentation can only be generated after plan/build/test/review workflows")
        sys.exit(1)
    
    issue_number = sys.argv[1]
    adw_id = sys.argv[2]
    
    # Try to load existing state
    temp_logger = setup_logger(adw_id, "adw_document")
    state = ADWState.load(adw_id, temp_logger)
    if state:
        # Found existing state - use the issue number from state if available
        issue_number = state.get("issue_number", issue_number)
        make_issue_comment(
            issue_number,
            f"{adw_id}_ops: 🔍 Found existing state - starting documentation\n```json\n{json.dumps(state.data, indent=2)}\n```"
        )
    else:
        # No existing state found
        logger = setup_logger(adw_id, "adw_document")
        logger.error(f"No state found for ADW ID: {adw_id}")
        logger.error("Run adw_plan_build_test_review.py first to complete the workflow")
        print(f"\nError: No state found for ADW ID: {adw_id}")
        print("Run adw_plan_build_test_review.py first to complete the workflow")
        sys.exit(1)
    
    # Set up logger with ADW ID from command line
    logger = setup_logger(adw_id, "adw_document")
    logger.info(f"ADW Document starting - ID: {adw_id}, Issue: {issue_number}")
    
    # Check environment
    check_env_vars(logger)
    
    # Ensure we have required state fields
    if not state.get("branch_name"):
        error_msg = "No branch name in state - run adw_plan.py first"
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
    
    # Post initial comment
    try:
        initial_comment = (
            f"📚 **Documentation Generation Started**\n\n"
            f"ADW ID: `{adw_id}`\n"
            f"Checking for changes against origin/main..."
        )
        make_issue_comment(issue_number, initial_comment)
    except Exception as e:
        logger.warning(f"Failed to post initial comment: {e}")
    
    # Generate documentation
    result = generate_documentation(issue_number, adw_id, logger, state)
    
    if result.success:
        # Only commit and push if documentation was created
        if result.documentation_created:
            # Get repo information
            try:
                github_repo_url = get_repo_url()
                repo_path = extract_repo_path(github_repo_url)
            except ValueError as e:
                logger.error(f"Error getting repository URL: {e}")
                make_issue_comment(
                    issue_number,
                    format_issue_message(adw_id, "ops", f"❌ Failed to get repository info: {e}")
                )
                sys.exit(1)
            
            # Fetch issue details for commit message
            try:
                issue = fetch_issue(issue_number, repo_path)
                logger.info(f"Fetched issue #{issue_number} for commit message")
            except Exception as e:
                logger.error(f"Failed to fetch issue: {e}")
                make_issue_comment(
                    issue_number,
                    format_issue_message(adw_id, "ops", f"❌ Failed to fetch issue for commit: {e}")
                )
                sys.exit(1)
            
            # Get issue classification from state
            issue_command = state.get("issue_class", "/chore")
            
            # Create commit message
            logger.info("Creating documentation commit")
            commit_msg, error = create_commit(AGENT_DOCUMENTER, issue, issue_command, adw_id, logger)
            
            if error:
                logger.error(f"Error creating commit message: {error}")
                make_issue_comment(
                    issue_number,
                    format_issue_message(adw_id, "ops", f"❌ Error creating commit: {error}")
                )
                sys.exit(1)
            
            # Commit the changes
            logger.info(f"Committing documentation: {commit_msg.split(chr(10))[0]}")
            success, error = commit_changes(commit_msg)
            if not success:
                logger.error(f"Failed to commit changes: {error}")
                make_issue_comment(
                    issue_number,
                    format_issue_message(adw_id, "ops", f"❌ Failed to commit documentation: {error}")
                )
                sys.exit(1)
            
            # Finalize git operations (push and PR)
            finalize_git_operations(state, logger)
            
            message = f"Documentation has been created at `{result.documentation_path}` and committed."
        else:
            message = "No changes detected between current branch and origin/main - documentation was not needed."
        
        # Post success comment
        try:
            success_comment = (
                f"✅ **Documentation Workflow Completed**\n\n"
                f"ADW ID: `{adw_id}`\n"
                f"{message}"
            )
            make_issue_comment(issue_number, success_comment)
        except Exception as e:
            logger.warning(f"Failed to post success comment: {e}")
        
        logger.info("Documentation workflow completed successfully")
        
        # Save state and output for chaining
        if result.documentation_path:
            state.update(documentation_path=result.documentation_path)
        state.save("adw_document")
        state.to_stdout()
        
        sys.exit(0)
    else:
        # Post failure comment
        try:
            failure_comment = (
                f"❌ **Documentation Generation Failed**\n\n"
                f"ADW ID: `{adw_id}`\n"
                f"Error: {result.error_message or 'Please check the logs for details.'}"
            )
            make_issue_comment(issue_number, failure_comment)
        except Exception as e:
            logger.warning(f"Failed to post failure comment: {e}")
        
        logger.error(f"Documentation workflow failed: {result.error_message}")
        
        # Save state even on failure
        state.save("adw_document")
        state.to_stdout()
        
        sys.exit(1)


if __name__ == "__main__":
    main()