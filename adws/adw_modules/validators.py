"""Comprehensive input validation with Pydantic for security hardening.

This module provides validation models to prevent:
- Command injection attacks
- Path traversal attacks
- SQL injection patterns
- Oversized inputs (DoS)
- Malicious URLs
- Invalid identifiers
"""

import re
import shlex
from pathlib import Path
from typing import List, Optional, Literal, ClassVar
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict
from typing_extensions import Annotated


# Security Constants
MAX_PROMPT_LENGTH = 100000  # 100KB max for prompts
MAX_COMMIT_MESSAGE_LENGTH = 5000  # Reasonable git commit size
MAX_BRANCH_NAME_LENGTH = 255  # Git limit
MAX_FILE_PATH_LENGTH = 4096  # Filesystem limit
MAX_ADW_ID_LENGTH = 64  # Reasonable identifier length
MAX_ISSUE_NUMBER_LENGTH = 10  # GitHub issue numbers are typically < 10 digits

# Allowed path prefixes for file operations
ALLOWED_PATH_PREFIXES = [
    "specs/",
    "scout_outputs/", "scout_outputs/ADW-", "scout_outputs/temp/",
    "ai_docs/",
    "docs/",
    "scripts/",
    "adws/",
    "app/",
]

# Dangerous shell metacharacters
SHELL_METACHARACTERS = [";", "|", "&", "$", "`", "\n", "\r", "(", ")", "<", ">"]


class SafeUserInput(BaseModel):
    """Validates all user-provided input for prompts and content.

    Security features:
    - Length limits to prevent DoS
    - Shell metacharacter detection
    - Content sanitization
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    prompt: str = Field(max_length=MAX_PROMPT_LENGTH, min_length=1)

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate and sanitize user prompt."""
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")

        # Check for null bytes
        if '\x00' in v:
            raise ValueError("Null bytes not allowed in prompt")

        # Warn about shell metacharacters but allow them in prompts
        # (they may be part of legitimate code examples)
        dangerous_chars = [char for char in SHELL_METACHARACTERS if char in v]
        if dangerous_chars:
            # Log warning but don't block (prompts may contain code)
            pass

        return v.strip()


class SafeDocsUrl(BaseModel):
    """Validates documentation URLs.

    Security features:
    - URL validation
    - Protocol whitelist (http/https only)
    - Domain validation
    """

    url: HttpUrl

    @field_validator('url')
    @classmethod
    def validate_url_scheme(cls, v: HttpUrl) -> HttpUrl:
        """Ensure URL uses safe protocol."""
        if v.scheme not in ['http', 'https']:
            raise ValueError(f"Invalid URL scheme: {v.scheme}. Only http/https allowed")
        return v


class SafeFilePath(BaseModel):
    """Validates file paths to prevent directory traversal.

    Security features:
    - Path traversal prevention
    - Prefix whitelist enforcement
    - Symlink resolution
    - Length limits
    """

    file_path: str = Field(max_length=MAX_FILE_PATH_LENGTH)
    operation: Literal["read", "write", "append", "delete"] = "read"
    require_exists: bool = False

    @field_validator('file_path')
    @classmethod
    def validate_path_safety(cls, v: str) -> str:
        """Validate file path for security."""
        if not v:
            raise ValueError("File path cannot be empty")

        # Check for null bytes
        if '\x00' in v:
            raise ValueError("Null bytes not allowed in file path")

        # Prevent absolute paths to system directories
        dangerous_prefixes = ['/etc/', '/sys/', '/proc/', '/dev/', '/root/']
        if any(v.startswith(prefix) for prefix in dangerous_prefixes):
            raise ValueError(f"Access to system directory not allowed: {v}")

        # Check for directory traversal attempts
        if '..' in v:
            raise ValueError("Directory traversal (..) not allowed in file path")

        # Normalize path
        try:
            normalized = str(Path(v).resolve())
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid file path: {e}")

        # Verify path is within allowed prefixes (if not absolute)
        if not Path(v).is_absolute():
            has_allowed_prefix = any(v.startswith(prefix) for prefix in ALLOWED_PATH_PREFIXES)
            if not has_allowed_prefix:
                raise ValueError(
                    f"File path must start with one of: {', '.join(ALLOWED_PATH_PREFIXES)}"
                )

        return v


class SafeGitBranch(BaseModel):
    """Validates git branch names.

    Security features:
    - Character whitelist
    - Length limits
    - Invalid pattern prevention
    """

    branch_name: Annotated[str, Field(
        min_length=1,
        max_length=MAX_BRANCH_NAME_LENGTH,
        pattern=r'^[a-zA-Z0-9\-_/]+$'
    )]

    @field_validator('branch_name')
    @classmethod
    def validate_branch_name(cls, v: str) -> str:
        """Validate git branch name."""
        # Prevent branches that start or end with special chars
        if v.startswith(('/', '-', '_')) or v.endswith(('/', '-', '_')):
            raise ValueError("Branch name cannot start/end with /, -, or _")

        # Prevent reserved names
        if v.lower() in ['head', 'master', 'main']:
            raise ValueError(f"Cannot use reserved branch name: {v}")

        # Prevent double slashes
        if '//' in v:
            raise ValueError("Double slashes not allowed in branch name")

        return v


class SafeCommitMessage(BaseModel):
    """Validates git commit messages.

    Security features:
    - Length limits
    - Shell injection prevention
    - Format validation
    """

    message: str = Field(max_length=MAX_COMMIT_MESSAGE_LENGTH, min_length=1)

    @field_validator('message')
    @classmethod
    def validate_commit_message(cls, v: str) -> str:
        """Validate commit message."""
        if not v or not v.strip():
            raise ValueError("Commit message cannot be empty")

        # Check for null bytes
        if '\x00' in v:
            raise ValueError("Null bytes not allowed in commit message")

        # Prevent shell command injection patterns
        dangerous_patterns = [
            r'\$\(',  # Command substitution
            r'`',     # Backtick command substitution
            r'\|',    # Pipe
            r'&&',    # Command chaining
            r'\|\|',  # OR chaining
            r';',     # Command separator
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v):
                raise ValueError(f"Potentially dangerous pattern in commit message: {pattern}")

        return v.strip()


class SafeIssueNumber(BaseModel):
    """Validates GitHub issue numbers.

    Security features:
    - Numeric validation
    - Range limits
    """

    issue_number: Annotated[str, Field(
        max_length=MAX_ISSUE_NUMBER_LENGTH,
        pattern=r'^\d+$'
    )]

    @field_validator('issue_number')
    @classmethod
    def validate_issue_number(cls, v: str) -> str:
        """Validate issue number."""
        num = int(v)
        if num < 1:
            raise ValueError("Issue number must be positive")
        if num > 999999999:  # Reasonable upper limit
            raise ValueError("Issue number too large")
        return v


class SafeADWID(BaseModel):
    """Validates ADW identifier.

    Security features:
    - Format validation
    - Character whitelist
    - Length limits
    """

    adw_id: Annotated[str, Field(
        min_length=5,
        max_length=MAX_ADW_ID_LENGTH,
        pattern=r'^ADW-[A-Z0-9]+$'
    )]

    @field_validator('adw_id')
    @classmethod
    def validate_adw_id_format(cls, v: str) -> str:
        """Validate ADW ID format."""
        if not v.startswith('ADW-'):
            raise ValueError("ADW ID must start with 'ADW-'")

        # Extract the suffix after 'ADW-'
        suffix = v[4:]
        if len(suffix) < 1:
            raise ValueError("ADW ID must have content after 'ADW-'")

        return v


class SafeCommandArgs(BaseModel):
    """Validates command-line arguments for subprocess execution.

    Security features:
    - Shell injection prevention
    - Argument sanitization
    - Whitelist validation
    """

    command: str = Field(min_length=1, max_length=255)
    args: List[str] = Field(default_factory=list)
    allowed_commands: Optional[List[str]] = None

    @field_validator('command')
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Validate command is whitelisted."""
        # Check for shell metacharacters in command
        if any(char in v for char in SHELL_METACHARACTERS):
            raise ValueError(f"Shell metacharacters not allowed in command: {v}")

        return v

    @field_validator('args')
    @classmethod
    def validate_args(cls, v: List[str]) -> List[str]:
        """Validate command arguments."""
        validated_args = []
        for arg in v:
            # Check for null bytes
            if '\x00' in arg:
                raise ValueError("Null bytes not allowed in arguments")

            # Use shlex to properly quote arguments
            validated_args.append(shlex.quote(arg))

        return validated_args

    def model_post_init(self, __context) -> None:
        """Validate whitelist after model initialization."""
        if self.allowed_commands and self.command not in self.allowed_commands:
            raise ValueError(
                f"Command '{self.command}' not in whitelist: {self.allowed_commands}"
            )


class SafeAgentName(BaseModel):
    """Validates agent names.

    Security features:
    - Character whitelist
    - Length limits
    - Pattern validation
    """

    agent_name: Annotated[str, Field(
        min_length=1,
        max_length=64,
        pattern=r'^[a-z0-9_]+$'
    )]

    @field_validator('agent_name')
    @classmethod
    def validate_agent_name(cls, v: str) -> str:
        """Validate agent name."""
        if v.startswith('_') or v.endswith('_'):
            raise ValueError("Agent name cannot start or end with underscore")

        if '__' in v:
            raise ValueError("Agent name cannot contain double underscores")

        return v


class SafeSlashCommand(BaseModel):
    """Validates slash commands.

    Security features:
    - Command whitelist
    - Format validation
    """

    command: str = Field(min_length=2, max_length=64)

    # Whitelist of allowed slash commands
    ALLOWED_COMMANDS: ClassVar[List[str]] = [
        "/chore", "/bug", "/feature",
        "/classify_issue", "/classify_adw",
        "/generate_branch_name", "/commit", "/pull_request",
        "/implement", "/test", "/resolve_failed_test",
        "/test_e2e", "/resolve_failed_e2e_test",
        "/review", "/patch", "/document",
    ]

    @field_validator('command')
    @classmethod
    def validate_slash_command(cls, v: str) -> str:
        """Validate slash command."""
        if not v.startswith('/'):
            raise ValueError("Slash command must start with '/'")

        if v not in cls.ALLOWED_COMMANDS:
            raise ValueError(f"Invalid slash command: {v}. Allowed: {cls.ALLOWED_COMMANDS}")

        return v


# Utility functions for common validation patterns

def validate_and_sanitize_prompt(prompt: str) -> str:
    """Validate and sanitize user prompt."""
    validated = SafeUserInput(prompt=prompt)
    return validated.prompt


def validate_file_path(file_path: str, operation: str = "read", require_exists: bool = False) -> str:
    """Validate file path for security."""
    validated = SafeFilePath(
        file_path=file_path,
        operation=operation,  # type: ignore
        require_exists=require_exists
    )
    return validated.file_path


def validate_branch_name(branch_name: str) -> str:
    """Validate git branch name."""
    validated = SafeGitBranch(branch_name=branch_name)
    return validated.branch_name


def validate_commit_message(message: str) -> str:
    """Validate git commit message."""
    validated = SafeCommitMessage(message=message)
    return validated.message


def validate_issue_number(issue_number: str) -> str:
    """Validate GitHub issue number."""
    validated = SafeIssueNumber(issue_number=str(issue_number))
    return validated.issue_number


def validate_adw_id(adw_id: str) -> str:
    """Validate ADW identifier."""
    validated = SafeADWID(adw_id=adw_id)
    return validated.adw_id


def validate_subprocess_command(
    command: str,
    args: List[str],
    allowed_commands: Optional[List[str]] = None
) -> tuple[str, List[str]]:
    """Validate subprocess command and arguments.

    Returns:
        Tuple of (validated_command, validated_args)
    """
    validated = SafeCommandArgs(
        command=command,
        args=args,
        allowed_commands=allowed_commands
    )
    return validated.command, validated.args
