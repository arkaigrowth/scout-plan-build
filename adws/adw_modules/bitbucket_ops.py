#!/usr/bin/env python3
"""
Bitbucket Operations Module

Provides Bitbucket API integration for the Scout-Plan-Build framework.
Mirrors github.py functionality for Bitbucket Cloud repositories.

Environment Variables:
    BITBUCKET_WORKSPACE: Your Bitbucket workspace name
    BITBUCKET_REPO: Repository slug (optional, can detect from git)
    BITBUCKET_USERNAME: Your Bitbucket username/email
    BITBUCKET_APP_PASSWORD: App password from Bitbucket settings
"""

import os
import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse


class BitbucketAPIError(Exception):
    """Raised when Bitbucket API calls fail."""
    pass


def get_bitbucket_client() -> Dict[str, str]:
    """
    Initialize Bitbucket API client configuration.

    Returns:
        Dict containing:
        - base_url: Bitbucket API base URL
        - auth: Tuple of (username, app_password)
        - workspace: Workspace name

    Raises:
        BitbucketAPIError: If required credentials missing
    """
    username = os.getenv("BITBUCKET_USERNAME")
    app_password = os.getenv("BITBUCKET_APP_PASSWORD")
    workspace = os.getenv("BITBUCKET_WORKSPACE")

    if not username or not app_password:
        raise BitbucketAPIError(
            "Missing Bitbucket credentials. Set BITBUCKET_USERNAME and "
            "BITBUCKET_APP_PASSWORD environment variables."
        )

    if not workspace:
        raise BitbucketAPIError(
            "Missing BITBUCKET_WORKSPACE environment variable."
        )

    return {
        "base_url": "https://api.bitbucket.org/2.0",
        "auth": (username, app_password),
        "workspace": workspace
    }


def fetch_issue(workspace: str, repo: str, issue_id: int) -> Dict[str, Any]:
    """
    Fetch issue details from Bitbucket.

    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        issue_id: Issue number

    Returns:
        Dict containing issue details in normalized format:
        - id: Issue number
        - title: Issue title
        - body: Issue description
        - state: Issue state (new, open, resolved, etc.)
        - author: Reporter username
        - created_at: ISO timestamp
        - url: Issue URL

    Raises:
        BitbucketAPIError: If API call fails
    """
    client = get_bitbucket_client()
    url = f"{client['base_url']}/repositories/{workspace}/{repo}/issues/{issue_id}"

    try:
        response = requests.get(url, auth=client["auth"], timeout=10)
        response.raise_for_status()
        data = response.json()

        # Normalize to common format
        return {
            "id": data.get("id"),
            "title": data.get("title", ""),
            "body": data.get("content", {}).get("raw", ""),
            "state": data.get("state", "new"),
            "author": data.get("reporter", {}).get("display_name", ""),
            "created_at": data.get("created_on", ""),
            "url": data.get("links", {}).get("html", {}).get("href", ""),
        }
    except requests.exceptions.RequestException as e:
        raise BitbucketAPIError(f"Failed to fetch issue #{issue_id}: {e}")


def create_pull_request(
    workspace: str,
    repo: str,
    title: str,
    description: str,
    source_branch: str,
    dest_branch: str = "main",
    reviewers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a pull request in Bitbucket.

    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        title: PR title
        description: PR description (supports Markdown)
        source_branch: Source branch name
        dest_branch: Destination branch (default: main)
        reviewers: Optional list of reviewer UUIDs

    Returns:
        Dict containing:
        - id: PR ID
        - url: PR URL
        - state: PR state (OPEN)

    Raises:
        BitbucketAPIError: If PR creation fails
    """
    client = get_bitbucket_client()
    url = f"{client['base_url']}/repositories/{workspace}/{repo}/pullrequests"

    payload = {
        "title": title,
        "description": description,
        "source": {
            "branch": {
                "name": source_branch
            }
        },
        "destination": {
            "branch": {
                "name": dest_branch
            }
        },
        "close_source_branch": False
    }

    # Add reviewers if provided
    if reviewers:
        payload["reviewers"] = [{"uuid": uuid} for uuid in reviewers]

    try:
        response = requests.post(
            url,
            json=payload,
            auth=client["auth"],
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        return {
            "id": data.get("id"),
            "url": data.get("links", {}).get("html", {}).get("href", ""),
            "state": data.get("state", "OPEN"),
        }
    except requests.exceptions.RequestException as e:
        raise BitbucketAPIError(f"Failed to create PR: {e}")


def add_reviewers(
    workspace: str,
    repo: str,
    pr_id: int,
    reviewers: List[str]
) -> bool:
    """
    Add reviewers to an existing pull request.

    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        pr_id: Pull request ID
        reviewers: List of reviewer UUIDs

    Returns:
        True if successful

    Raises:
        BitbucketAPIError: If adding reviewers fails
    """
    client = get_bitbucket_client()

    # Bitbucket adds reviewers individually
    for reviewer_uuid in reviewers:
        url = (
            f"{client['base_url']}/repositories/{workspace}/{repo}/"
            f"pullrequests/{pr_id}/reviewers/{reviewer_uuid}"
        )

        try:
            response = requests.put(url, auth=client["auth"], timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise BitbucketAPIError(
                f"Failed to add reviewer {reviewer_uuid}: {e}"
            )

    return True


def add_comment(
    workspace: str,
    repo: str,
    issue_id: int,
    comment: str
) -> Dict[str, Any]:
    """
    Add a comment to a Bitbucket issue.

    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        issue_id: Issue number
        comment: Comment text (supports Markdown)

    Returns:
        Dict containing comment details

    Raises:
        BitbucketAPIError: If comment creation fails
    """
    client = get_bitbucket_client()
    url = (
        f"{client['base_url']}/repositories/{workspace}/{repo}/"
        f"issues/{issue_id}/comments"
    )

    payload = {
        "content": {
            "raw": comment
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            auth=client["auth"],
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        return {
            "id": data.get("id"),
            "created_at": data.get("created_on"),
            "url": data.get("links", {}).get("html", {}).get("href", "")
        }
    except requests.exceptions.RequestException as e:
        raise BitbucketAPIError(f"Failed to add comment: {e}")


def trigger_pipeline(
    workspace: str,
    repo: str,
    branch: str,
    custom_vars: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Trigger a Bitbucket pipeline for a branch.

    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        branch: Branch name to build
        custom_vars: Optional custom pipeline variables

    Returns:
        Dict containing:
        - uuid: Pipeline UUID
        - build_number: Build number
        - url: Pipeline URL

    Raises:
        BitbucketAPIError: If pipeline trigger fails
    """
    client = get_bitbucket_client()
    url = f"{client['base_url']}/repositories/{workspace}/{repo}/pipelines/"

    payload = {
        "target": {
            "ref_type": "branch",
            "ref_name": branch,
            "type": "pipeline_ref_target"
        }
    }

    # Add custom variables if provided
    if custom_vars:
        payload["variables"] = [
            {"key": k, "value": v} for k, v in custom_vars.items()
        ]

    try:
        response = requests.post(
            url,
            json=payload,
            auth=client["auth"],
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        return {
            "uuid": data.get("uuid"),
            "build_number": data.get("build_number"),
            "url": data.get("links", {}).get("self", {}).get("href", ""),
        }
    except requests.exceptions.RequestException as e:
        raise BitbucketAPIError(f"Failed to trigger pipeline: {e}")


def get_repo_from_remote() -> tuple[str, str]:
    """
    Extract workspace and repo from git remote URL.

    Returns:
        Tuple of (workspace, repo)

    Example:
        git remote: https://bitbucket.org/myteam/myrepo.git
        returns: ("myteam", "myrepo")
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()

        # Parse Bitbucket URL
        if "bitbucket.org" in remote_url:
            # Handle both HTTPS and SSH formats
            # https://bitbucket.org/workspace/repo.git
            # git@bitbucket.org:workspace/repo.git
            path = remote_url.split("bitbucket.org")[-1]
            path = path.lstrip(":/").rstrip(".git")
            parts = path.split("/")

            if len(parts) >= 2:
                return parts[0], parts[1]

        raise ValueError("Not a Bitbucket repository")

    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
        raise BitbucketAPIError(
            f"Failed to detect Bitbucket repository from git remote: {e}"
        )


# Convenience wrapper for common workflow
def create_pr_from_current_branch(
    title: str,
    description: str,
    dest_branch: str = "main"
) -> str:
    """
    Create PR from current git branch (convenience function).

    Args:
        title: PR title
        description: PR description
        dest_branch: Target branch (default: main)

    Returns:
        PR URL
    """
    import subprocess

    # Get current branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True
    )
    current_branch = result.stdout.strip()

    # Get repo info from remote
    workspace, repo = get_repo_from_remote()

    # Create PR
    pr = create_pull_request(
        workspace=workspace,
        repo=repo,
        title=title,
        description=description,
        source_branch=current_branch,
        dest_branch=dest_branch
    )

    return pr["url"]


if __name__ == "__main__":
    # Example usage
    print("Bitbucket Operations Module")
    print("===========================")
    print()
    print("Environment variables needed:")
    print("  BITBUCKET_WORKSPACE")
    print("  BITBUCKET_USERNAME")
    print("  BITBUCKET_APP_PASSWORD")
    print()
    print("Example:")
    print("  from bitbucket_ops import create_pr_from_current_branch")
    print("  pr_url = create_pr_from_current_branch('feat: New feature', 'Description')")
