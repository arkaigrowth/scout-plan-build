#!/usr/bin/env python3
"""
VCS Provider Detection Module

Automatically detects version control system provider (GitHub or Bitbucket)
based on git remote URL. Provides abstraction layer for multi-VCS support.

Usage:
    from vcs_detection import detect_vcs_provider, get_repo_info

    provider = detect_vcs_provider()  # "github" or "bitbucket"
    repo_info = get_repo_info()       # {"provider": "github", "owner": "...", "repo": "..."}
"""

import os
import subprocess
from typing import Dict, Optional, Literal
from urllib.parse import urlparse


VCSProvider = Literal["github", "bitbucket"]


class VCSDetectionError(Exception):
    """Raised when VCS provider cannot be detected."""
    pass


def detect_vcs_provider() -> VCSProvider:
    """
    Detect VCS provider from git remote URL or environment variable.

    Checks in order:
    1. VCS_PROVIDER environment variable (manual override)
    2. Git remote URL pattern matching
    3. GitHub-specific commands (gh CLI)

    Returns:
        "github" or "bitbucket"

    Raises:
        VCSDetectionError: If provider cannot be determined

    Examples:
        >>> os.environ["VCS_PROVIDER"] = "bitbucket"
        >>> detect_vcs_provider()
        'bitbucket'

        >>> # With git remote: https://github.com/owner/repo.git
        >>> detect_vcs_provider()
        'github'

        >>> # With git remote: git@bitbucket.org:workspace/repo.git
        >>> detect_vcs_provider()
        'bitbucket'
    """
    # Check environment variable override
    env_provider = os.getenv("VCS_PROVIDER", "").lower()
    if env_provider in ["github", "bitbucket"]:
        return env_provider  # type: ignore

    # Try to detect from git remote
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        remote_url = result.stdout.strip()

        # Pattern matching
        if "github.com" in remote_url:
            return "github"
        elif "bitbucket.org" in remote_url:
            return "bitbucket"

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    # Default to GitHub if gh CLI is available (backward compatibility)
    try:
        subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            check=True,
            timeout=2
        )
        return "github"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    raise VCSDetectionError(
        "Cannot detect VCS provider. Set VCS_PROVIDER environment variable "
        "or ensure git remote is configured."
    )


def get_repo_info() -> Dict[str, str]:
    """
    Extract repository information from git remote URL.

    Returns normalized repository information for the detected provider.

    Returns:
        Dict containing:
        - provider: "github" or "bitbucket"
        - owner/workspace: Repository owner (GitHub) or workspace (Bitbucket)
        - repo: Repository name
        - url: Remote URL

    Raises:
        VCSDetectionError: If repo info cannot be extracted

    Examples:
        >>> # GitHub repo
        >>> get_repo_info()
        {
            "provider": "github",
            "owner": "myorg",
            "repo": "myrepo",
            "url": "https://github.com/myorg/myrepo.git"
        }

        >>> # Bitbucket repo
        >>> get_repo_info()
        {
            "provider": "bitbucket",
            "workspace": "myteam",
            "repo": "myproject",
            "url": "https://bitbucket.org/myteam/myproject.git"
        }
    """
    provider = detect_vcs_provider()

    try:
        # Get remote URL
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        remote_url = result.stdout.strip()

        # Parse URL based on provider
        if provider == "github":
            return _parse_github_url(remote_url)
        elif provider == "bitbucket":
            return _parse_bitbucket_url(remote_url)

    except subprocess.CalledProcessError as e:
        raise VCSDetectionError(f"Failed to get git remote: {e}")


def _parse_github_url(url: str) -> Dict[str, str]:
    """Parse GitHub URL to extract owner and repo."""
    # Handle both HTTPS and SSH formats
    # https://github.com/owner/repo.git
    # git@github.com:owner/repo.git

    if "github.com" in url:
        path = url.split("github.com")[-1]
        path = path.lstrip(":/").rstrip(".git")
        parts = path.split("/")

        if len(parts) >= 2:
            return {
                "provider": "github",
                "owner": parts[0],
                "repo": parts[1],
                "url": url
            }

    raise VCSDetectionError(f"Invalid GitHub URL format: {url}")


def _parse_bitbucket_url(url: str) -> Dict[str, str]:
    """Parse Bitbucket URL to extract workspace and repo."""
    # Handle both HTTPS and SSH formats
    # https://bitbucket.org/workspace/repo.git
    # git@bitbucket.org:workspace/repo.git

    if "bitbucket.org" in url:
        path = url.split("bitbucket.org")[-1]
        path = path.lstrip(":/").rstrip(".git")
        parts = path.split("/")

        if len(parts) >= 2:
            return {
                "provider": "bitbucket",
                "workspace": parts[0],  # Bitbucket uses "workspace" not "owner"
                "repo": parts[1],
                "url": url
            }

    raise VCSDetectionError(f"Invalid Bitbucket URL format: {url}")


def is_github() -> bool:
    """
    Check if current repository uses GitHub.

    Returns:
        True if GitHub, False otherwise
    """
    try:
        return detect_vcs_provider() == "github"
    except VCSDetectionError:
        return False


def is_bitbucket() -> bool:
    """
    Check if current repository uses Bitbucket.

    Returns:
        True if Bitbucket, False otherwise
    """
    try:
        return detect_vcs_provider() == "bitbucket"
    except VCSDetectionError:
        return False


def get_provider_specific_info() -> Dict[str, str]:
    """
    Get provider-specific information for API calls.

    This is a convenience function that returns the right fields
    based on the detected provider.

    Returns:
        For GitHub: {"owner": "...", "repo": "..."}
        For Bitbucket: {"workspace": "...", "repo": "..."}

    Raises:
        VCSDetectionError: If provider detection fails
    """
    info = get_repo_info()
    provider = info["provider"]

    if provider == "github":
        return {
            "owner": info["owner"],
            "repo": info["repo"]
        }
    elif provider == "bitbucket":
        return {
            "workspace": info["workspace"],
            "repo": info["repo"]
        }

    raise VCSDetectionError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    # CLI tool for testing VCS detection
    import sys

    try:
        provider = detect_vcs_provider()
        repo_info = get_repo_info()

        print(f"✓ Detected VCS provider: {provider}")
        print(f"✓ Repository info:")
        for key, value in repo_info.items():
            print(f"  {key}: {value}")

        sys.exit(0)

    except VCSDetectionError as e:
        print(f"✗ VCS detection failed: {e}", file=sys.stderr)
        print("\nTroubleshooting:")
        print("  1. Ensure you're in a git repository")
        print("  2. Check git remote: git remote -v")
        print("  3. Or set: export VCS_PROVIDER=github  (or bitbucket)")
        sys.exit(1)
