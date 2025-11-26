"""Shared AI Developer Workflow (ADW) operations."""

import glob
import json
import logging
import os
import subprocess
import re
from typing import Tuple, Optional, List
from pydantic import ValidationError as PydanticValidationError

from adw_modules.data_types import (
    AgentTemplateRequest,
    GitHubIssue,
    AgentPromptResponse,
    IssueClassSlashCommand,
)
from adw_modules.agent import execute_template
from adw_modules.github import get_repo_url, extract_repo_path, ADW_BOT_IDENTIFIER
from adw_modules.state import ADWState
from adw_modules.utils import parse_json
from adw_modules.exceptions import (
    ValidationError,
    AgentError,
    WorkflowError,
    GitOperationError,
    handle_error,
)
from adw_modules.validators import (
    validate_file_path,
    validate_branch_name,
    validate_commit_message,
    validate_issue_number,
    validate_adw_id,
    validate_subprocess_command,
    SafeAgentName,
    SafeSlashCommand,
)


# Agent name constants
AGENT_PLANNER = "sdlc_planner"
AGENT_IMPLEMENTOR = "sdlc_implementor"
AGENT_CLASSIFIER = "issue_classifier"
AGENT_BRANCH_GENERATOR = "branch_generator"
AGENT_PR_CREATOR = "pr_creator"

# Available ADW workflows for runtime validation
AVAILABLE_ADW_WORKFLOWS = [
    "adw_plan",
    "adw_build",
    "adw_test",
    "adw_review",
    "adw_document",
    "adw_patch",
    "adw_plan_build",
    "adw_plan_build_test",
    "adw_plan_build_test_review",
    "adw_sdlc",
]


def format_issue_message(
    adw_id: str, agent_name: str, message: str, session_id: Optional[str] = None
) -> str:
    """Format a message for issue comments with ADW tracking and bot identifier.

    Args:
        adw_id: Validated ADW identifier
        agent_name: Agent name creating the message
        message: Message content
        session_id: Optional session identifier

    Returns:
        Formatted message string

    Raises:
        ValidationError: If inputs fail validation
    """
    # Validate inputs
    try:
        validated_adw_id = validate_adw_id(adw_id)
        validated_agent = SafeAgentName(agent_name=agent_name)

        # Validate message content (basic sanitization)
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty", field="message")
        if '\x00' in message:
            raise ValidationError("Null bytes not allowed in message", field="message")

    except PydanticValidationError as e:
        raise ValidationError(
            f"Invalid input in format_issue_message: {str(e)}",
            field="multiple",
            pydantic_error=str(e)
        )

    # Always include ADW_BOT_IDENTIFIER to prevent webhook loops
    if session_id:
        return f"{ADW_BOT_IDENTIFIER} {validated_adw_id}_{validated_agent.agent_name}_{session_id}: {message.strip()}"
    return f"{ADW_BOT_IDENTIFIER} {validated_adw_id}_{validated_agent.agent_name}: {message.strip()}"


def extract_adw_info(
    text: str, temp_adw_id: str
) -> Tuple[Optional[str], Optional[str]]:
    """Extract ADW workflow and ID from text using classify_adw agent.
    Returns (workflow_command, adw_id) tuple."""

    # Use classify_adw to extract structured info
    request = AgentTemplateRequest(
        agent_name="adw_classifier",
        slash_command="/classify_adw",
        args=[text],
        adw_id=temp_adw_id,
    )

    try:
        response = execute_template(request)

        if not response.success:
            raise AgentError(
                f"Failed to classify ADW workflow",
                agent_name="adw_classifier",
                slash_command="/classify_adw",
                output=response.output
            )

        # Parse JSON response using utility that handles markdown
        try:
            data = parse_json(response.output, dict)
            adw_command = data.get("adw_slash_command", "").replace("/", "")
            adw_id = data.get("adw_id")

            # Validate command
            if adw_command and adw_command in AVAILABLE_ADW_WORKFLOWS:
                return adw_command, adw_id

            raise ValidationError(
                f"Invalid ADW workflow command: {adw_command}",
                field="adw_slash_command",
                valid_commands=AVAILABLE_ADW_WORKFLOWS
            )

        except ValueError as e:
            raise ValidationError(
                "Failed to parse ADW classifier response",
                field="response_output",
                parse_error=str(e),
                response=response.output
            ) from e

    except (AgentError, ValidationError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        raise WorkflowError(
            "Unexpected error in ADW classification",
            workflow_name="extract_adw_info",
            step="classify_adw"
        ) from e


def classify_issue(
    issue: GitHubIssue, adw_id: str, logger: logging.Logger
) -> Tuple[Optional[IssueClassSlashCommand], Optional[str]]:
    """Classify GitHub issue and return appropriate slash command.
    Returns (command, error_message) tuple."""

    # Use the classify_issue slash command template with minimal payload
    # Only include the essential fields: number, title, body
    minimal_issue_json = issue.model_dump_json(
        by_alias=True, include={"number", "title", "body"}
    )

    request = AgentTemplateRequest(
        agent_name=AGENT_CLASSIFIER,
        slash_command="/classify_issue",
        args=[minimal_issue_json],
        adw_id=adw_id,
    )

    logger.debug(f"Classifying issue: {issue.title}")

    response = execute_template(request)

    logger.debug(
        f"Classification response: {response.model_dump_json(indent=2, by_alias=True)}"
    )

    if not response.success:
        return None, response.output

    # Extract the classification from the response
    output = response.output.strip()

    # Look for the classification pattern in the output
    # Claude might add explanation, so we need to extract just the command
    classification_match = re.search(r"(/chore|/bug|/feature|0)", output)

    if classification_match:
        issue_command = classification_match.group(1)
    else:
        issue_command = output

    if issue_command == "0":
        return None, f"No command selected: {response.output}"

    if issue_command not in ["/chore", "/bug", "/feature"]:
        return None, f"Invalid command selected: {response.output}"

    return issue_command, None  # type: ignore


def build_plan(
    issue: GitHubIssue, command: str, adw_id: str, logger: logging.Logger
) -> AgentPromptResponse:
    """Build implementation plan for the issue using the specified command.

    Args:
        issue: GitHub issue object
        command: Validated slash command
        adw_id: Validated ADW identifier
        logger: Logger instance

    Returns:
        Agent response with plan details

    Raises:
        ValidationError: If inputs fail validation
        AgentError: If plan generation fails
    """
    try:
        # Validate inputs
        validated_adw_id = validate_adw_id(adw_id)
        validated_command = SafeSlashCommand(command=command)
        validated_issue_num = validate_issue_number(str(issue.number))

        # Use minimal payload like classify_issue does
        minimal_issue_json = issue.model_dump_json(
            by_alias=True, include={"number", "title", "body"}
        )

        issue_plan_template_request = AgentTemplateRequest(
            agent_name=AGENT_PLANNER,
            slash_command=validated_command.command,  # type: ignore
            args=[validated_issue_num, validated_adw_id, minimal_issue_json],
            adw_id=validated_adw_id,
        )

        logger.debug(
            f"issue_plan_template_request: {issue_plan_template_request.model_dump_json(indent=2, by_alias=True)}"
        )

        issue_plan_response = execute_template(issue_plan_template_request)

        logger.debug(
            f"issue_plan_response: {issue_plan_response.model_dump_json(indent=2, by_alias=True)}"
        )

        return issue_plan_response

    except PydanticValidationError as e:
        raise ValidationError(
            f"Invalid input in build_plan: {str(e)}",
            field="multiple",
            pydantic_error=str(e)
        )


def implement_plan(
    plan_file: str, adw_id: str, logger: logging.Logger, agent_name: Optional[str] = None
) -> AgentPromptResponse:
    """Implement the plan using the /implement command.

    Args:
        plan_file: Path to plan specification file
        adw_id: Validated ADW identifier
        logger: Logger instance
        agent_name: Optional agent name override

    Returns:
        Agent response with implementation results

    Raises:
        ValidationError: If inputs fail validation
        AgentError: If implementation fails
    """
    try:
        # Validate inputs
        validated_adw_id = validate_adw_id(adw_id)
        validated_plan_file = validate_file_path(plan_file, operation="read")

        # Use provided agent_name or default to AGENT_IMPLEMENTOR
        implementor_name = agent_name or AGENT_IMPLEMENTOR
        validated_agent = SafeAgentName(agent_name=implementor_name)

        implement_template_request = AgentTemplateRequest(
            agent_name=validated_agent.agent_name,
            slash_command="/implement",
            args=[validated_plan_file],
            adw_id=validated_adw_id,
        )

        logger.debug(
            f"implement_template_request: {implement_template_request.model_dump_json(indent=2, by_alias=True)}"
        )

        implement_response = execute_template(implement_template_request)

        logger.debug(
            f"implement_response: {implement_response.model_dump_json(indent=2, by_alias=True)}"
        )

        return implement_response

    except PydanticValidationError as e:
        raise ValidationError(
            f"Invalid input in implement_plan: {str(e)}",
            field="multiple",
            pydantic_error=str(e)
        )


def generate_branch_name(
    issue: GitHubIssue,
    issue_class: IssueClassSlashCommand,
    adw_id: str,
    logger: logging.Logger,
) -> Tuple[Optional[str], Optional[str]]:
    """Generate and create a git branch for the issue.

    Args:
        issue: GitHub issue object
        issue_class: Issue classification slash command
        adw_id: Validated ADW identifier
        logger: Logger instance

    Returns:
        Tuple of (branch_name, error_message)

    Raises:
        ValidationError: If inputs fail validation
    """
    try:
        # Validate inputs
        validated_adw_id = validate_adw_id(adw_id)
        validated_command = SafeSlashCommand(command=issue_class)

        # Remove the leading slash from issue_class for the branch name
        issue_type = validated_command.command.replace("/", "")

        # Use minimal payload like classify_issue does
        minimal_issue_json = issue.model_dump_json(
            by_alias=True, include={"number", "title", "body"}
        )

        request = AgentTemplateRequest(
            agent_name=AGENT_BRANCH_GENERATOR,
            slash_command="/generate_branch_name",
            args=[issue_type, validated_adw_id, minimal_issue_json],
            adw_id=validated_adw_id,
        )

        response = execute_template(request)

        if not response.success:
            return None, response.output

        branch_name = response.output.strip()

        # Validate generated branch name
        try:
            validated_branch_name = validate_branch_name(branch_name)
            logger.info(f"Generated branch name: {validated_branch_name}")
            return validated_branch_name, None
        except PydanticValidationError as e:
            error_msg = f"Generated branch name failed validation: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    except PydanticValidationError as e:
        raise ValidationError(
            f"Invalid input in generate_branch_name: {str(e)}",
            field="multiple",
            pydantic_error=str(e)
        )


def create_commit(
    agent_name: str,
    issue: GitHubIssue,
    issue_class: IssueClassSlashCommand,
    adw_id: str,
    logger: logging.Logger,
) -> Tuple[Optional[str], Optional[str]]:
    """Create a git commit with a properly formatted message.

    Args:
        agent_name: Agent name for commit attribution
        issue: GitHub issue object
        issue_class: Issue classification slash command
        adw_id: Validated ADW identifier
        logger: Logger instance

    Returns:
        Tuple of (commit_message, error_message)

    Raises:
        ValidationError: If inputs fail validation
    """
    try:
        # Validate inputs
        validated_adw_id = validate_adw_id(adw_id)
        validated_agent = SafeAgentName(agent_name=agent_name)
        validated_command = SafeSlashCommand(command=issue_class)

        # Remove the leading slash from issue_class
        issue_type = validated_command.command.replace("/", "")

        # Create unique committer agent name by suffixing '_committer'
        unique_agent_name = f"{validated_agent.agent_name}_committer"
        validated_unique_agent = SafeAgentName(agent_name=unique_agent_name)

        # Use minimal payload like classify_issue does
        minimal_issue_json = issue.model_dump_json(
            by_alias=True, include={"number", "title", "body"}
        )

        request = AgentTemplateRequest(
            agent_name=validated_unique_agent.agent_name,
            slash_command="/commit",
            args=[validated_agent.agent_name, issue_type, minimal_issue_json],
            adw_id=validated_adw_id,
        )

        response = execute_template(request)

        if not response.success:
            return None, response.output

        commit_message = response.output.strip()

        # Validate generated commit message
        try:
            validated_message = validate_commit_message(commit_message)
            logger.info(f"Created commit message: {validated_message}")
            return validated_message, None
        except PydanticValidationError as e:
            error_msg = f"Generated commit message failed validation: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    except PydanticValidationError as e:
        raise ValidationError(
            f"Invalid input in create_commit: {str(e)}",
            field="multiple",
            pydantic_error=str(e)
        )


def create_pull_request(
    branch_name: str,
    issue: Optional[GitHubIssue],
    state: ADWState,
    logger: logging.Logger,
) -> Tuple[Optional[str], Optional[str]]:
    """Create a pull request for the implemented changes.
    Returns (pr_url, error_message) tuple."""

    # Get plan file from state (may be None for test runs)
    plan_file = state.get("plan_file") or "No plan file (test run)"
    adw_id = state.get("adw_id")

    # If we don't have issue data, try to construct minimal data
    if not issue:
        issue_data = state.get("issue", {})
        issue_json = json.dumps(issue_data) if issue_data else "{}"
    elif isinstance(issue, dict):
        # Try to reconstruct as GitHubIssue model which handles datetime serialization
        from adw_modules.data_types import GitHubIssue

        try:
            issue_model = GitHubIssue(**issue)
            # Use minimal payload like classify_issue does
            issue_json = issue_model.model_dump_json(
                by_alias=True, include={"number", "title", "body"}
            )
        except Exception:
            # Fallback: use json.dumps with default str converter for datetime
            issue_json = json.dumps(issue, default=str)
    else:
        # Use minimal payload like classify_issue does
        issue_json = issue.model_dump_json(
            by_alias=True, include={"number", "title", "body"}
        )

    request = AgentTemplateRequest(
        agent_name=AGENT_PR_CREATOR,
        slash_command="/pull_request",
        args=[branch_name, issue_json, plan_file, adw_id],
        adw_id=adw_id,
    )

    response = execute_template(request)

    if not response.success:
        return None, response.output

    pr_url = response.output.strip()
    logger.info(f"Created pull request: {pr_url}")
    return pr_url, None


def ensure_plan_exists(state: ADWState, issue_number: str) -> str:
    """Find or error if no plan exists for issue.
    Used by adw_build.py in standalone mode."""
    # Check if plan file is in state
    if state.get("plan_file"):
        return state.get("plan_file")

    # Check current branch
    from adw_modules.git_ops import get_current_branch

    branch = get_current_branch()

    # Look for plan in branch name
    if f"-{issue_number}-" in branch:
        # Look for plan file
        plans = glob.glob(f"specs/*{issue_number}*.md")
        if plans:
            return plans[0]

    # No plan found
    raise WorkflowError(
        f"No plan found for issue {issue_number}",
        workflow_name="adw_build",
        step="ensure_plan_exists",
        issue_number=issue_number,
        branch=branch,
        instruction="Run adw_plan.py first to create the plan"
    )


def ensure_adw_id(
    issue_number: str,
    adw_id: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> str:
    """Get ADW ID or create a new one and initialize state.

    Args:
        issue_number: The issue number to find/create ADW ID for
        adw_id: Optional existing ADW ID to use
        logger: Optional logger instance

    Returns:
        The ADW ID (existing or newly created)
    """
    # If ADW ID provided, check if state exists
    if adw_id:
        state = ADWState.load(adw_id, logger)
        if state:
            if logger:
                logger.info(f"Found existing ADW state for ID: {adw_id}")
            else:
                print(f"Found existing ADW state for ID: {adw_id}")
            return adw_id
        # ADW ID provided but no state exists, create state
        state = ADWState(adw_id)
        state.update(adw_id=adw_id, issue_number=issue_number)
        state.save("ensure_adw_id")
        if logger:
            logger.info(f"Created new ADW state for provided ID: {adw_id}")
        else:
            print(f"Created new ADW state for provided ID: {adw_id}")
        return adw_id

    # No ADW ID provided, create new one with state
    from adw_modules.utils import make_adw_id

    new_adw_id = make_adw_id()
    state = ADWState(new_adw_id)
    state.update(adw_id=new_adw_id, issue_number=issue_number)
    state.save("ensure_adw_id")
    if logger:
        logger.info(f"Created new ADW ID and state: {new_adw_id}")
    else:
        print(f"Created new ADW ID and state: {new_adw_id}")
    return new_adw_id


def find_existing_branch_for_issue(
    issue_number: str, adw_id: Optional[str] = None
) -> Optional[str]:
    """Find an existing branch for the given issue number.
    Returns branch name if found, None otherwise."""
    # List all branches
    result = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True)

    if result.returncode != 0:
        return None

    branches = result.stdout.strip().split("\n")

    # Look for branch with standardized pattern: *-issue-{issue_number}-adw-{adw_id}-*
    for branch in branches:
        branch = branch.strip().replace("* ", "").replace("remotes/origin/", "")
        # Check for the standardized pattern
        if f"-issue-{issue_number}-" in branch:
            if adw_id and f"-adw-{adw_id}-" in branch:
                return branch
            elif not adw_id:
                # Return first match if no adw_id specified
                return branch

    return None


def find_plan_for_issue(
    issue_number: str, adw_id: Optional[str] = None
) -> Optional[str]:
    """Find plan file for the given issue number and optional adw_id.
    Returns path to plan file if found, None otherwise."""
    import os

    # Get project root
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    agents_dir = os.path.join(project_root, "agents")

    if not os.path.exists(agents_dir):
        return None

    # If adw_id is provided, check specific directory first
    if adw_id:
        plan_path = os.path.join(agents_dir, adw_id, AGENT_PLANNER, "plan.md")
        if os.path.exists(plan_path):
            return plan_path

    # Otherwise, search all agent directories
    for agent_id in os.listdir(agents_dir):
        agent_path = os.path.join(agents_dir, agent_id)
        if os.path.isdir(agent_path):
            plan_path = os.path.join(agent_path, AGENT_PLANNER, "plan.md")
            if os.path.exists(plan_path):
                # Check if this plan is for our issue by reading branch info or checking commits
                # For now, return the first plan found (can be improved)
                return plan_path

    return None


def create_or_find_branch(
    issue_number: str, issue: GitHubIssue, state: ADWState, logger: logging.Logger
) -> Tuple[str, Optional[str]]:
    """Create or find a branch for the given issue.

    1. First checks state for existing branch name
    2. Then looks for existing branches matching the issue
    3. If none found, classifies the issue and creates a new branch

    Returns (branch_name, error_message) tuple.
    """
    # 1. Check state for branch name
    branch_name = state.get("branch_name") or state.get("branch", {}).get("name")
    if branch_name:
        logger.info(f"Found branch in state: {branch_name}")
        # Check if we need to checkout
        from adw_modules.git_ops import get_current_branch

        current = get_current_branch()
        if current != branch_name:
            result = subprocess.run(
                ["git", "checkout", branch_name], capture_output=True, text=True
            )
            if result.returncode != 0:
                # Branch might not exist locally, try to create from remote
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name, f"origin/{branch_name}"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    return "", f"Failed to checkout branch: {result.stderr}"
        return branch_name, None

    # 2. Look for existing branch
    adw_id = state.get("adw_id")
    existing_branch = find_existing_branch_for_issue(issue_number, adw_id)
    if existing_branch:
        logger.info(f"Found existing branch: {existing_branch}")
        # Checkout the branch
        result = subprocess.run(
            ["git", "checkout", existing_branch], capture_output=True, text=True
        )
        if result.returncode != 0:
            return "", f"Failed to checkout branch: {result.stderr}"
        state.update(branch_name=existing_branch)
        return existing_branch, None

    # 3. Create new branch - classify issue first
    logger.info("No existing branch found, creating new one")

    # Classify the issue
    issue_command, error = classify_issue(issue, adw_id, logger)
    if error:
        return "", f"Failed to classify issue: {error}"

    state.update(issue_class=issue_command)

    # Generate branch name
    branch_name, error = generate_branch_name(issue, issue_command, adw_id, logger)
    if error:
        return "", f"Failed to generate branch name: {error}"

    # Create the branch
    from adw_modules.git_ops import create_branch

    success, error = create_branch(branch_name)
    if not success:
        return "", f"Failed to create branch: {error}"

    state.update(branch_name=branch_name)
    logger.info(f"Created and checked out new branch: {branch_name}")

    return branch_name, None


def find_spec_file(state: ADWState, logger: logging.Logger) -> Optional[str]:
    """Find the spec file from state or by examining git diff."""
    # Check if spec file is already in state (from plan phase)
    spec_file = state.get("plan_file")
    if spec_file and os.path.exists(spec_file):
        logger.info(f"Using spec file from state: {spec_file}")
        return spec_file

    # Otherwise, try to find it from git diff
    logger.info("Looking for spec file in git diff")
    result = subprocess.run(
        ["git", "diff", "origin/main", "--name-only"], capture_output=True, text=True
    )

    if result.returncode == 0:
        files = result.stdout.strip().split("\n")
        spec_files = [f for f in files if f.startswith("spec/") and f.endswith(".md")]

        if spec_files:
            # Use the first spec file found
            spec_file = spec_files[0]
            logger.info(f"Found spec file: {spec_file}")
            return spec_file

    # If still not found, try to derive from branch name
    branch_name = state.get("branch_name")
    if branch_name:
        # Extract issue number from branch name
        import re

        match = re.search(r"issue-(\d+)", branch_name)
        if match:
            issue_num = match.group(1)
            adw_id = state.get("adw_id")

            # Look for spec files matching the pattern
            import glob

            pattern = f"spec/issue-{issue_num}-adw-{adw_id}*.md"
            spec_files = glob.glob(pattern)

            if spec_files:
                spec_file = spec_files[0]
                logger.info(f"Found spec file by pattern: {spec_file}")
                return spec_file

    logger.warning("No spec file found")
    return None


def create_and_implement_patch(
    adw_id: str,
    review_change_request: str,
    logger: logging.Logger,
    agent_name_planner: str,
    agent_name_implementor: str,
    spec_path: Optional[str] = None,
    issue_screenshots: Optional[str] = None,
) -> Tuple[Optional[str], AgentPromptResponse]:
    """Create a patch plan and implement it.
    Returns (patch_file_path, implement_response) tuple."""

    # Create patch plan using /patch command
    args = [adw_id, review_change_request]

    # Add optional arguments in the correct order
    if spec_path:
        args.append(spec_path)
    else:
        args.append("")  # Empty string for optional spec_path

    args.append(agent_name_planner)

    if issue_screenshots:
        args.append(issue_screenshots)

    request = AgentTemplateRequest(
        agent_name=agent_name_planner,
        slash_command="/patch",
        args=args,
        adw_id=adw_id,
    )

    logger.debug(
        f"Patch plan request: {request.model_dump_json(indent=2, by_alias=True)}"
    )

    response = execute_template(request)

    logger.debug(
        f"Patch plan response: {response.model_dump_json(indent=2, by_alias=True)}"
    )

    if not response.success:
        logger.error(f"Error creating patch plan: {response.output}")
        # Return None and a failed response
        return None, AgentPromptResponse(
            output=f"Failed to create patch plan: {response.output}", success=False
        )

    # Extract the patch plan file path from the response
    patch_file_path = response.output.strip()

    # Validate that it looks like a file path
    if not patch_file_path.startswith("specs/patch/") or not patch_file_path.endswith(
        ".md"
    ):
        logger.error(f"Invalid patch plan path returned: {patch_file_path}")
        return None, AgentPromptResponse(
            output=f"Invalid patch plan path: {patch_file_path}", success=False
        )

    logger.info(f"Created patch plan: {patch_file_path}")

    # Now implement the patch plan using the provided implementor agent name
    implement_response = implement_plan(patch_file_path, adw_id, logger, agent_name_implementor)

    return patch_file_path, implement_response
