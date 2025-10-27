#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
GitHub Operations Module - AI Developer Workflow (ADW)

This module contains all GitHub-related operations including:
- Issue fetching and manipulation
- Comment posting
- Repository path extraction
- Issue status management
"""

import subprocess
import sys
import os
import json
from typing import Dict, List, Optional
from .data_types import GitHubIssue, GitHubIssueListItem, GitHubComment
from .exceptions import GitHubAPIError, EnvironmentError

# Bot identifier to prevent webhook loops and filter bot comments
ADW_BOT_IDENTIFIER = "[ADW-BOT]"


def get_github_env() -> Optional[dict]:
    """Get environment with GitHub token set up. Returns None if no GITHUB_PAT.
    
    Subprocess env behavior:
    - env=None → Inherits parent's environment (default)
    - env={} → Empty environment (no variables)
    - env=custom_dict → Only uses specified variables
    
    So this will work with gh authentication:
    # These are equivalent:
    result = subprocess.run(cmd, capture_output=True, text=True)
    result = subprocess.run(cmd, capture_output=True, text=True, env=None)
    
    But this will NOT work (no PATH, no auth):
    result = subprocess.run(cmd, capture_output=True, text=True, env={})
    """
    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        return None
    
    # Only create minimal env with GitHub token
    env = {
        "GH_TOKEN": github_pat,
        "PATH": os.environ.get("PATH", ""),
    }
    return env


def get_repo_url() -> str:
    """Get GitHub repository URL from git remote.

    Raises:
        GitHubAPIError: If git remote cannot be retrieved
        EnvironmentError: If git is not installed
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise GitHubAPIError(
            "No git remote 'origin' found",
            api_endpoint="git remote get-url origin",
            stderr=e.stderr,
            instruction="Ensure you're in a git repository with a remote configured"
        ) from e
    except FileNotFoundError as e:
        raise EnvironmentError(
            "git command not found",
            required_tools=["git"],
            instruction="Install git: https://git-scm.com/downloads"
        ) from e


def extract_repo_path(github_url: str) -> str:
    """Extract owner/repo from GitHub URL."""
    # Handle both https://github.com/owner/repo and https://github.com/owner/repo.git
    return github_url.replace("https://github.com/", "").replace(".git", "")


def fetch_issue(issue_number: str, repo_path: str) -> GitHubIssue:
    """Fetch GitHub issue using gh CLI and return typed model.

    Raises:
        EnvironmentError: If gh CLI is not installed
        GitHubAPIError: If issue fetch fails
    """
    # Return mock issue for testing
    if issue_number == "999":
        return GitHubIssue(
            number=999,
            title="Add simple parallel execution for Test/Review/Document phases",
            body="Implement subprocess.Popen() based parallel execution with --no-commit flags",
            labels=["enhancement", "performance"],
            state="open"
        )

    # Use JSON output for structured data
    cmd = [
        "gh",
        "issue",
        "view",
        issue_number,
        "-R",
        repo_path,
        "--json",
        "number,title,body,state,author,assignees,labels,milestone,comments,createdAt,updatedAt,closedAt,url",
    ]

    # Set up environment with GitHub token if available
    env = get_github_env()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            check=True
        )

        # Parse JSON response into Pydantic model
        issue_data = json.loads(result.stdout)
        issue = GitHubIssue(**issue_data)
        return issue

    except FileNotFoundError as e:
        raise EnvironmentError(
            "GitHub CLI (gh) is not installed",
            required_tools=["gh"],
            instruction=(
                "Install gh:\n"
                "  - macOS: brew install gh\n"
                "  - Linux/Windows: https://github.com/cli/cli#installation\n"
                "After installation: gh auth login"
            )
        ) from e

    except subprocess.CalledProcessError as e:
        raise GitHubAPIError(
            f"Failed to fetch issue #{issue_number}",
            api_endpoint=f"gh issue view {issue_number}",
            stderr=e.stderr,
            issue_number=issue_number,
            repo_path=repo_path
        ) from e

    except json.JSONDecodeError as e:
        raise GitHubAPIError(
            "Failed to parse issue response",
            api_endpoint=f"gh issue view {issue_number}",
            parse_error=str(e)
        ) from e

    except Exception as e:
        raise GitHubAPIError(
            f"Unexpected error fetching issue #{issue_number}",
            api_endpoint=f"gh issue view {issue_number}",
            error=str(e)
        ) from e


def make_issue_comment(issue_id: str, comment: str) -> None:
    """Post a comment to a GitHub issue using gh CLI.

    Raises:
        GitHubAPIError: If comment posting fails
    """
    # Skip GitHub operations for local testing
    if issue_id == "999":
        print(f"[MOCK GitHub Comment] Issue #{issue_id}: {comment[:200]}...")
        return

    try:
        # Get repo information from git remote
        github_repo_url = get_repo_url()
        repo_path = extract_repo_path(github_repo_url)

        # Build command
        cmd = [
            "gh",
            "issue",
            "comment",
            issue_id,
            "-R",
            repo_path,
            "--body",
            comment,
        ]

        # Set up environment with GitHub token if available
        env = get_github_env()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            check=True
        )

        print(f"Successfully posted comment to issue #{issue_id}")

    except subprocess.CalledProcessError as e:
        raise GitHubAPIError(
            f"Failed to post comment to issue #{issue_id}",
            api_endpoint=f"gh issue comment {issue_id}",
            stderr=e.stderr,
            issue_id=issue_id,
            comment_preview=comment[:100]
        ) from e

    except Exception as e:
        raise GitHubAPIError(
            f"Unexpected error posting comment to issue #{issue_id}",
            api_endpoint=f"gh issue comment {issue_id}",
            error=str(e)
        ) from e


def mark_issue_in_progress(issue_id: str) -> None:
    """Mark issue as in progress by adding label and comment."""
    # Get repo information from git remote
    github_repo_url = get_repo_url()
    repo_path = extract_repo_path(github_repo_url)

    # Add "in_progress" label
    cmd = [
        "gh",
        "issue",
        "edit",
        issue_id,
        "-R",
        repo_path,
        "--add-label",
        "in_progress",
    ]

    # Set up environment with GitHub token if available
    env = get_github_env()

    # Try to add label (may fail if label doesn't exist)
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Note: Could not add 'in_progress' label: {result.stderr}")

    # Post comment indicating work has started
    # make_issue_comment(issue_id, "🚧 ADW is working on this issue...")

    # Assign to self (optional)
    cmd = [
        "gh",
        "issue",
        "edit",
        issue_id,
        "-R",
        repo_path,
        "--add-assignee",
        "@me",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode == 0:
        print(f"Assigned issue #{issue_id} to self")


def fetch_open_issues(repo_path: str) -> List[GitHubIssueListItem]:
    """Fetch all open issues from the GitHub repository."""
    try:
        cmd = [
            "gh",
            "issue",
            "list",
            "--repo",
            repo_path,
            "--state",
            "open",
            "--json",
            "number,title,body,labels,createdAt,updatedAt",
            "--limit",
            "1000",
        ]

        # Set up environment with GitHub token if available
        env = get_github_env()

        # DEBUG level - not printing command
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env
        )

        issues_data = json.loads(result.stdout)
        issues = [GitHubIssueListItem(**issue_data) for issue_data in issues_data]
        print(f"Fetched {len(issues)} open issues")
        return issues

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to fetch issues: {e.stderr}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse issues JSON: {e}", file=sys.stderr)
        return []


def fetch_issue_comments(repo_path: str, issue_number: int) -> List[Dict]:
    """Fetch all comments for a specific issue."""
    try:
        cmd = [
            "gh",
            "issue",
            "view",
            str(issue_number),
            "--repo",
            repo_path,
            "--json",
            "comments",
        ]

        # Set up environment with GitHub token if available
        env = get_github_env()

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env
        )
        data = json.loads(result.stdout)
        comments = data.get("comments", [])

        # Sort comments by creation time
        comments.sort(key=lambda c: c.get("createdAt", ""))

        # DEBUG level - not printing
        return comments

    except subprocess.CalledProcessError as e:
        print(
            f"ERROR: Failed to fetch comments for issue #{issue_number}: {e.stderr}",
            file=sys.stderr,
        )
        return []
    except json.JSONDecodeError as e:
        print(
            f"ERROR: Failed to parse comments JSON for issue #{issue_number}: {e}",
            file=sys.stderr,
        )
        return []


def find_keyword_from_comment(keyword: str, issue: GitHubIssue) -> Optional[GitHubComment]:
    """Find the latest comment containing a specific keyword.
    
    Args:
        keyword: The keyword to search for in comments
        issue: The GitHub issue containing comments
        
    Returns:
        The latest GitHubComment containing the keyword, or None if not found
    """
    # Sort comments by created_at date (newest first)
    sorted_comments = sorted(issue.comments, key=lambda c: c.created_at, reverse=True)
    
    # Search through sorted comments (newest first)
    for comment in sorted_comments:
        # Skip ADW bot comments to prevent loops
        if ADW_BOT_IDENTIFIER in comment.body:
            continue
            
        if keyword in comment.body:
            return comment
    
    return None
