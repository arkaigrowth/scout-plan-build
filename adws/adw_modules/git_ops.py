"""Git operations for ADW composable architecture.

Provides centralized git operations that build on top of github.py module.

Security: All git commands are validated to prevent command injection.
"""

import subprocess
import json
import logging
from typing import Optional, Tuple

# Import GitHub functions from existing module
from adw_modules.github import get_repo_url, extract_repo_path, make_issue_comment
from adw_modules.exceptions import GitOperationError, GitHubAPIError, ValidationError
from adw_modules.validators import validate_branch_name, validate_commit_message
from adw_modules.vcs_detection import detect_vcs_provider, get_repo_info


def get_current_branch() -> str:
    """Get current git branch name.

    Raises:
        GitOperationError: If git command fails
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise GitOperationError(
            "Failed to get current branch",
            command="git rev-parse --abbrev-ref HEAD",
            returncode=e.returncode,
            stderr=e.stderr
        ) from e


def push_branch(branch_name: str) -> Tuple[bool, Optional[str]]:
    """Push current branch to remote. Returns (success, error_message).

    Args:
        branch_name: Branch name to push (will be validated)

    Returns:
        Tuple of (success, error_message)

    Raises:
        ValidationError: If branch name fails validation
    """
    try:
        # Validate branch name to prevent command injection
        validated_branch_name = validate_branch_name(branch_name)

        result = subprocess.run(
            ["git", "push", "-u", "origin", validated_branch_name],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise GitOperationError(
                f"Failed to push branch {validated_branch_name}",
                command=f"git push -u origin {validated_branch_name}",
                returncode=result.returncode,
                stderr=result.stderr,
                branch_name=validated_branch_name
            )
        return True, None
    except ValidationError as e:
        return False, e.message
    except GitOperationError as e:
        return False, e.message
    except Exception as e:
        return False, str(e)


def check_pr_exists(branch_name: str) -> Optional[str]:
    """Check if PR exists for branch. Returns PR URL if exists.

    Supports both GitHub (via gh CLI) and Bitbucket (via API).

    Args:
        branch_name: Branch name to check (will be validated)

    Returns:
        PR URL if exists, None otherwise

    Raises:
        ValidationError: If branch name fails validation
        GitHubAPIError: If command/API fails (except for "no PR found")
    """
    # Validate branch name to prevent command injection
    validated_branch_name = validate_branch_name(branch_name)

    # Detect VCS provider
    try:
        provider = detect_vcs_provider()
    except Exception:
        provider = "github"  # Default to GitHub for backward compatibility

    if provider == "github":
        return _check_pr_github(validated_branch_name)
    elif provider == "bitbucket":
        return _check_pr_bitbucket(validated_branch_name)
    else:
        raise GitHubAPIError(f"Unsupported VCS provider: {provider}")


def _check_pr_github(branch_name: str) -> Optional[str]:
    """Check for PR on GitHub using gh CLI."""
    try:
        repo_url = get_repo_url()
        repo_path = extract_repo_path(repo_url)
    except Exception as e:
        raise GitHubAPIError(
            "Failed to get repository information",
            api_endpoint="git remote get-url"
        ) from e

    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", repo_path, "--head", branch_name, "--json", "url"],
            capture_output=True,
            text=True,
            check=True
        )
        prs = json.loads(result.stdout)
        if prs:
            return prs[0]["url"]
        return None
    except subprocess.CalledProcessError as e:
        if "no pull requests" in e.stderr.lower():
            return None
        raise GitHubAPIError(
            f"Failed to check for existing PR on branch {branch_name}",
            api_endpoint=f"gh pr list --repo {repo_path}",
            branch_name=branch_name,
            stderr=e.stderr
        ) from e
    except json.JSONDecodeError as e:
        raise GitHubAPIError(
            "Failed to parse PR list response",
            api_endpoint=f"gh pr list --repo {repo_path}",
            parse_error=str(e)
        ) from e


def _check_pr_bitbucket(branch_name: str) -> Optional[str]:
    """Check for PR on Bitbucket using API."""
    import requests
    from adw_modules import bitbucket_ops

    try:
        repo_info = get_repo_info()
        workspace = repo_info.get("workspace")
        repo = repo_info.get("repo")

        client = bitbucket_ops.get_bitbucket_client()
        url = f"{client['base_url']}/repositories/{workspace}/{repo}/pullrequests"
        params = {"state": "OPEN", "q": f'source.branch.name="{branch_name}"'}

        response = requests.get(url, auth=client["auth"], params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("values"):
            return data["values"][0].get("links", {}).get("html", {}).get("href")
        return None

    except Exception as e:
        # Bitbucket PR check failure is non-critical
        logging.warning(f"Bitbucket PR check failed: {e}")
        return None


def create_branch(branch_name: str) -> Tuple[bool, Optional[str]]:
    """Create and checkout a new branch. Returns (success, error_message).

    Args:
        branch_name: Branch name to create (will be validated)

    Returns:
        Tuple of (success, error_message)

    Raises:
        ValidationError: If branch name fails validation
    """
    try:
        # Validate branch name to prevent command injection
        validated_branch_name = validate_branch_name(branch_name)

        # Create branch
        result = subprocess.run(
            ["git", "checkout", "-b", validated_branch_name],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            # Check if error is because branch already exists
            if "already exists" in result.stderr:
                # Try to checkout existing branch
                result = subprocess.run(
                    ["git", "checkout", validated_branch_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise GitOperationError(
                        f"Failed to checkout existing branch {validated_branch_name}",
                        command=f"git checkout {validated_branch_name}",
                        returncode=result.returncode,
                        stderr=result.stderr,
                        branch_name=validated_branch_name
                    )
                return True, None

            raise GitOperationError(
                f"Failed to create branch {validated_branch_name}",
                command=f"git checkout -b {validated_branch_name}",
                returncode=result.returncode,
                stderr=result.stderr,
                branch_name=validated_branch_name
            )
        return True, None
    except ValidationError as e:
        return False, e.message
    except GitOperationError as e:
        return False, e.message
    except Exception as e:
        return False, str(e)


def commit_changes(message: str) -> Tuple[bool, Optional[str]]:
    """Stage all changes and commit. Returns (success, error_message).

    Args:
        message: Commit message (will be validated)

    Returns:
        Tuple of (success, error_message)

    Raises:
        ValidationError: If commit message fails validation
    """
    try:
        # Validate commit message to prevent command injection
        validated_message = validate_commit_message(message)

        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stdout.strip():
            return True, None  # No changes to commit

        # Stage all changes
        result = subprocess.run(
            ["git", "add", "-A"],
            capture_output=True,
            text=True,
            check=True
        )

        # Commit with validated message
        result = subprocess.run(
            ["git", "commit", "-m", validated_message],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise GitOperationError(
                "Failed to commit changes",
                command="git commit",
                returncode=result.returncode,
                stderr=result.stderr,
                commit_message=validated_message
            )
        return True, None
    except ValidationError as e:
        return False, e.message
    except subprocess.CalledProcessError as e:
        error = GitOperationError(
            f"Git operation failed during commit",
            command=str(e.cmd),
            returncode=e.returncode,
            stderr=e.stderr
        )
        return False, error.message
    except GitOperationError as e:
        return False, e.message
    except Exception as e:
        return False, str(e)


def finalize_git_operations(state: 'ADWState', logger: logging.Logger) -> None:
    """Standard git finalization: push branch and create/update PR.

    Raises:
        GitOperationError: If git operations fail
        GitHubAPIError: If GitHub operations fail
    """
    from adw_modules.exceptions import StateError, handle_error

    branch_name = state.get("branch_name")
    if not branch_name:
        # Fallback: use current git branch if not main
        try:
            current_branch = get_current_branch()
            if current_branch and current_branch != "main":
                logger.warning(f"No branch name in state, using current branch: {current_branch}")
                branch_name = current_branch
            else:
                raise StateError(
                    "No branch name in state and current branch is main",
                    adw_id=state.get("adw_id"),
                    current_branch=current_branch
                )
        except GitOperationError as e:
            logger.error(f"Failed to get current branch: {e.message}")
            handle_error(e, logger, state.get("issue_number"), state.get("adw_id"))
            return
        except StateError as e:
            logger.error(f"Invalid state for git operations: {e.message}")
            handle_error(e, logger, state.get("issue_number"), state.get("adw_id"))
            return

    # Always push
    success, error = push_branch(branch_name)
    if not success:
        logger.error(f"Failed to push branch: {error}")
        return

    logger.info(f"Pushed branch: {branch_name}")

    # Handle PR
    try:
        pr_url = check_pr_exists(branch_name)
    except GitHubAPIError as e:
        logger.error(f"Failed to check for existing PR: {e.message}")
        handle_error(e, logger, state.get("issue_number"), state.get("adw_id"))
        return

    issue_number = state.get("issue_number")
    adw_id = state.get("adw_id")

    if pr_url:
        logger.info(f"Found existing PR: {pr_url}")
        # Post PR link for easy reference
        if issue_number and adw_id:
            try:
                make_issue_comment(
                    issue_number,
                    f"{adw_id}_ops: ✅ Pull request: {pr_url}"
                )
            except Exception as e:
                logger.warning(f"Failed to post PR comment: {e}")
    else:
        # Create new PR - fetch issue data first
        if issue_number:
            try:
                repo_url = get_repo_url()
                repo_path = extract_repo_path(repo_url)
                from adw_modules.github import fetch_issue
                issue = fetch_issue(issue_number, repo_path)

                from adw_modules.workflow_ops import create_pull_request
                pr_url, error = create_pull_request(branch_name, issue, state, logger)
            except GitHubAPIError as e:
                logger.error(f"Failed to fetch issue for PR creation: {e.message}")
                handle_error(e, logger, issue_number, adw_id)
                pr_url, error = None, e.message
            except Exception as e:
                logger.error(f"Failed to fetch issue for PR creation: {e}")
                pr_url, error = None, str(e)
        else:
            pr_url, error = None, "No issue number in state"

        if pr_url:
            logger.info(f"Created PR: {pr_url}")
            # Post new PR link
            if issue_number and adw_id:
                try:
                    make_issue_comment(
                        issue_number,
                        f"{adw_id}_ops: ✅ Pull request created: {pr_url}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to post PR comment: {e}")
        else:
            logger.error(f"Failed to create PR: {error}")