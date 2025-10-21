"""Structured exception hierarchy for ADW system.

This module provides a comprehensive exception hierarchy that replaces generic
Exception catches throughout the codebase. Each exception type includes context
tracking and recovery strategies.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging


class ADWError(Exception):
    """Base exception for all ADW operations.

    All ADW exceptions inherit from this base class and include:
    - Structured error context
    - Timestamp tracking
    - Optional correlation ID for multi-operation tracking
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        """Initialize ADW error with context.

        Args:
            message: Human-readable error description
            context: Additional contextual data about the error
            correlation_id: Optional ID to track related operations
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.correlation_id = correlation_id
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "context": self.context,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Validation & Input Errors
# =============================================================================

class ValidationError(ADWError):
    """Input validation failures.

    Raised when:
    - Required parameters are missing or invalid
    - Data doesn't match expected schema
    - Configuration is malformed

    Recovery: Return error to user with specific field information
    """

    def __init__(self, message: str, field: Optional[str] = None, **context):
        """Initialize validation error.

        Args:
            message: Description of validation failure
            field: Name of field that failed validation
            **context: Additional context (expected_type, actual_value, etc.)
        """
        if field:
            context["field"] = field
        super().__init__(message, context)


class StateError(ADWError):
    """ADW state management issues.

    Raised when:
    - State file is corrupted or missing required fields
    - State transitions are invalid
    - State persistence fails

    Recovery: Attempt to rebuild state from git history or fail gracefully
    """

    def __init__(self, message: str, adw_id: Optional[str] = None, **context):
        """Initialize state error.

        Args:
            message: Description of state issue
            adw_id: ADW ID associated with problematic state
            **context: Additional context (state_path, missing_fields, etc.)
        """
        if adw_id:
            context["adw_id"] = adw_id
        super().__init__(message, context)


# =============================================================================
# Git & GitHub Operations
# =============================================================================

class GitOperationError(ADWError):
    """Git command failures.

    Raised when:
    - Git commands return non-zero exit codes
    - Repository is in invalid state
    - Merge conflicts or detached HEAD

    Recovery: Attempt git reset or provide rollback instructions
    """

    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        returncode: Optional[int] = None,
        stderr: Optional[str] = None,
        **context
    ):
        """Initialize git operation error.

        Args:
            message: Description of git failure
            command: Git command that failed
            returncode: Exit code from git command
            stderr: Error output from git
            **context: Additional context (branch_name, commit_sha, etc.)
        """
        if command:
            context["command"] = command
        if returncode is not None:
            context["returncode"] = returncode
        if stderr:
            context["stderr"] = stderr
        super().__init__(message, context)


class GitHubAPIError(ADWError):
    """GitHub API and CLI failures.

    Raised when:
    - GitHub CLI (gh) commands fail
    - API rate limits are exceeded
    - Authentication issues

    Recovery: Retry with exponential backoff for rate limits
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_endpoint: Optional[str] = None,
        **context
    ):
        """Initialize GitHub API error.

        Args:
            message: Description of API failure
            status_code: HTTP status code if available
            api_endpoint: GitHub API endpoint that failed
            **context: Additional context (repo_path, issue_number, etc.)
        """
        if status_code:
            context["status_code"] = status_code
        if api_endpoint:
            context["api_endpoint"] = api_endpoint
        super().__init__(message, context)


# =============================================================================
# Agent & Workflow Execution
# =============================================================================

class AgentError(ADWError):
    """Agent invocation failures.

    Raised when:
    - Claude Code CLI execution fails
    - Agent returns error status
    - Agent output cannot be parsed

    Recovery: Retry with exponential backoff (max 3 attempts)
    """

    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        slash_command: Optional[str] = None,
        session_id: Optional[str] = None,
        **context
    ):
        """Initialize agent error.

        Args:
            message: Description of agent failure
            agent_name: Name of agent that failed
            slash_command: Slash command being executed
            session_id: Claude Code session ID if available
            **context: Additional context (output_file, model, etc.)
        """
        if agent_name:
            context["agent_name"] = agent_name
        if slash_command:
            context["slash_command"] = slash_command
        if session_id:
            context["session_id"] = session_id
        super().__init__(message, context)


class WorkflowError(ADWError):
    """Workflow execution failures.

    Raised when:
    - Multi-step workflow coordination fails
    - Required workflow state is missing
    - Workflow step dependencies are unmet

    Recovery: Save state and provide resume instructions
    """

    def __init__(
        self,
        message: str,
        workflow_name: Optional[str] = None,
        step: Optional[str] = None,
        **context
    ):
        """Initialize workflow error.

        Args:
            message: Description of workflow failure
            workflow_name: Name of workflow (adw_plan, adw_build, etc.)
            step: Specific step that failed
            **context: Additional context (adw_id, issue_number, etc.)
        """
        if workflow_name:
            context["workflow_name"] = workflow_name
        if step:
            context["step"] = step
        super().__init__(message, context)


# =============================================================================
# Resource & API Limits
# =============================================================================

class TokenLimitError(ADWError):
    """API token limit exceeded.

    Raised when:
    - Claude Code returns token limit errors
    - Input exceeds model context window
    - Output truncation detected

    Recovery: Chunk operation into smaller requests
    """

    def __init__(
        self,
        message: str,
        tokens_requested: Optional[int] = None,
        tokens_available: Optional[int] = None,
        **context
    ):
        """Initialize token limit error.

        Args:
            message: Description of token limit issue
            tokens_requested: Number of tokens requested
            tokens_available: Number of tokens available
            **context: Additional context (model, prompt_size, etc.)
        """
        if tokens_requested:
            context["tokens_requested"] = tokens_requested
        if tokens_available:
            context["tokens_available"] = tokens_available
        super().__init__(message, context)


class RateLimitError(ADWError):
    """API rate limit exceeded.

    Raised when:
    - GitHub API rate limits hit
    - Anthropic API rate limits hit
    - Too many requests in time window

    Recovery: Exponential backoff with configurable max retries
    """

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        limit_type: Optional[str] = None,
        **context
    ):
        """Initialize rate limit error.

        Args:
            message: Description of rate limit
            retry_after: Seconds to wait before retry
            limit_type: Type of limit (github, anthropic, etc.)
            **context: Additional context (requests_remaining, reset_time, etc.)
        """
        if retry_after:
            context["retry_after"] = retry_after
        if limit_type:
            context["limit_type"] = limit_type
        super().__init__(message, context)


# =============================================================================
# System & Environment
# =============================================================================

class EnvironmentError(ADWError):
    """Environment configuration issues.

    Raised when:
    - Required environment variables missing
    - Invalid configuration values
    - External tools not installed (git, gh, claude)

    Recovery: Provide clear setup instructions
    """

    def __init__(
        self,
        message: str,
        missing_vars: Optional[list] = None,
        **context
    ):
        """Initialize environment error.

        Args:
            message: Description of environment issue
            missing_vars: List of missing environment variables
            **context: Additional context (required_tools, config_file, etc.)
        """
        if missing_vars:
            context["missing_vars"] = missing_vars
        super().__init__(message, context)


class FileSystemError(ADWError):
    """File system operation failures.

    Raised when:
    - File read/write fails
    - Directory creation fails
    - Path traversal detected
    - Disk space issues

    Recovery: Check permissions and disk space
    """

    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        operation: Optional[str] = None,
        **context
    ):
        """Initialize file system error.

        Args:
            message: Description of file system issue
            path: File/directory path involved
            operation: Operation that failed (read, write, mkdir, etc.)
            **context: Additional context (permissions, disk_space, etc.)
        """
        if path:
            context["path"] = path
        if operation:
            context["operation"] = operation
        super().__init__(message, context)


# =============================================================================
# Error Handler Utilities
# =============================================================================

def handle_error(
    error: ADWError,
    logger: logging.Logger,
    issue_number: Optional[str] = None,
    adw_id: Optional[str] = None
) -> Dict[str, Any]:
    """Centralized error handling with logging and GitHub comments.

    Args:
        error: The ADW error to handle
        logger: Logger instance for recording error
        issue_number: Optional issue number for GitHub comment
        adw_id: Optional ADW ID for correlation

    Returns:
        Dictionary with error details and recommended action
    """
    # Log error with appropriate level
    error_dict = error.to_dict()

    # Determine severity and log level
    if isinstance(error, (TokenLimitError, RateLimitError)):
        # Recoverable resource limits
        logger.warning(f"{error.__class__.__name__}: {error.message}", extra=error_dict)
        severity = "warning"
        recoverable = True
    elif isinstance(error, (ValidationError, EnvironmentError)):
        # User/config issues
        logger.error(f"{error.__class__.__name__}: {error.message}", extra=error_dict)
        severity = "error"
        recoverable = False
    else:
        # System/workflow failures
        logger.error(f"{error.__class__.__name__}: {error.message}", extra=error_dict)
        severity = "error"
        recoverable = True

    # Post to GitHub if issue number provided
    if issue_number and adw_id:
        try:
            from adw_modules.github import make_issue_comment
            from adw_modules.workflow_ops import format_issue_message

            error_emoji = "⚠️" if recoverable else "❌"
            comment = format_issue_message(
                adw_id,
                "error_handler",
                f"{error_emoji} {error.__class__.__name__}: {error.message}"
            )
            make_issue_comment(issue_number, comment)
        except Exception as comment_error:
            logger.warning(f"Failed to post error to GitHub: {comment_error}")

    return {
        "error_type": error.__class__.__name__,
        "message": error.message,
        "severity": severity,
        "recoverable": recoverable,
        "context": error.context,
        "timestamp": error.timestamp.isoformat(),
    }


def get_recovery_strategy(error: ADWError) -> str:
    """Get recommended recovery strategy for error type.

    Args:
        error: The ADW error to analyze

    Returns:
        Human-readable recovery instructions
    """
    if isinstance(error, GitOperationError):
        return "Run 'git status' to check repository state. Consider 'git reset --hard' to recover."

    elif isinstance(error, TokenLimitError):
        return "Reduce input size or chunk operation into smaller requests."

    elif isinstance(error, RateLimitError):
        retry_after = error.context.get("retry_after", 60)
        return f"Wait {retry_after} seconds before retrying. Consider implementing exponential backoff."

    elif isinstance(error, StateError):
        return "Check state file integrity or recreate from git history."

    elif isinstance(error, ValidationError):
        field = error.context.get("field", "unknown")
        return f"Fix validation error in field '{field}' and retry."

    elif isinstance(error, EnvironmentError):
        missing = error.context.get("missing_vars", [])
        if missing:
            return f"Set required environment variables: {', '.join(missing)}"
        return "Check environment configuration and required tools."

    elif isinstance(error, AgentError):
        return "Check agent logs for details. Consider retrying with different parameters."

    elif isinstance(error, WorkflowError):
        return "Review workflow state and resolve dependencies before continuing."

    else:
        return "Check logs for details and contact support if issue persists."
