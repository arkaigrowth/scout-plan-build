#!/usr/bin/env python3
"""Tests for Bitbucket integration."""

import pytest
from unittest.mock import patch, MagicMock
from adws.adw_modules import bitbucket_ops, vcs_detection


class TestVCSDetection:
    """Test VCS provider detection."""

    @patch('subprocess.run')
    def test_detect_github(self, mock_run):
        """Test GitHub detection from remote URL."""
        mock_run.return_value = MagicMock(
            stdout="https://github.com/owner/repo.git\n",
            returncode=0
        )
        assert vcs_detection.detect_vcs_provider() == "github"

    @patch('subprocess.run')
    def test_detect_bitbucket(self, mock_run):
        """Test Bitbucket detection from remote URL."""
        mock_run.return_value = MagicMock(
            stdout="https://bitbucket.org/workspace/repo.git\n",
            returncode=0
        )
        assert vcs_detection.detect_vcs_provider() == "bitbucket"

    @patch.dict('os.environ', {'VCS_PROVIDER': 'bitbucket'})
    def test_env_override(self):
        """Test environment variable override."""
        assert vcs_detection.detect_vcs_provider() == "bitbucket"


class TestBitbucketOps:
    """Test Bitbucket API operations."""

    @patch('requests.get')
    @patch('adws.adw_modules.bitbucket_ops.get_bitbucket_client')
    def test_fetch_issue(self, mock_client, mock_get):
        """Test fetching issue from Bitbucket."""
        mock_client.return_value = {
            "base_url": "https://api.bitbucket.org/2.0",
            "auth": ("user", "pass"),
            "workspace": "test"
        }
        mock_get.return_value.json.return_value = {
            "id": 123,
            "title": "Test Issue",
            "content": {"raw": "Description"},
            "state": "new"
        }

        result = bitbucket_ops.fetch_issue("workspace", "repo", 123)
        assert result["id"] == 123
        assert result["title"] == "Test Issue"

    @patch('requests.post')
    @patch('adws.adw_modules.bitbucket_ops.get_bitbucket_client')
    def test_create_pr(self, mock_client, mock_post):
        """Test creating PR in Bitbucket."""
        mock_client.return_value = {
            "base_url": "https://api.bitbucket.org/2.0",
            "auth": ("user", "pass")
        }
        mock_post.return_value.json.return_value = {
            "id": 456,
            "links": {"html": {"href": "https://bitbucket.org/pr/456"}}
        }

        result = bitbucket_ops.create_pull_request(
            "workspace", "repo", "Title", "Desc", "feature", "main"
        )
        assert result["id"] == 456
        assert "bitbucket.org" in result["url"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
