"""Claude Code agent module for executing prompts programmatically."""

import subprocess
import sys
import os
import json
import re
import logging
from typing import Optional, List, Dict, Any, Tuple, Final
from dotenv import load_dotenv
from adw_modules.data_types import (
    AgentPromptRequest,
    AgentPromptResponse,
    AgentTemplateRequest,
    ClaudeCodeResultMessage,
    SlashCommand,
)
from adw_modules.exceptions import (
    AgentError,
    EnvironmentError,
    TokenLimitError,
    FileSystemError,
)

# Load environment variables
load_dotenv()

# Get Claude Code CLI path from environment
CLAUDE_PATH = os.getenv("CLAUDE_CODE_PATH", "claude")

# Model selection mapping for slash commands
# Maps slash command to preferred model
SLASH_COMMAND_MODEL_MAP: Final[Dict[SlashCommand, str]] = {
    # Issue classification
    "/classify_issue": "sonnet",
    "/classify_adw": "sonnet",
    # Branch operations
    "/generate_branch_name": "sonnet",
    # Implementation tasks
    "/implement": "opus",
    # Testing and debugging
    "/test": "sonnet",
    "/resolve_failed_test": "sonnet",
    "/test_e2e": "sonnet",
    "/resolve_failed_e2e_test": "sonnet",
    # Review
    "/review": "opus",
    # Documentation
    "/document": "sonnet",
    # Git operations
    "/commit": "sonnet",
    "/pull_request": "sonnet",
    # Issue types + planning
    "/chore": "sonnet",
    "/bug": "opus",
    "/feature": "opus",
    "/patch": "opus",
}


def get_model_for_slash_command(slash_command: str, default: str = "sonnet") -> str:
    """Get the recommended model for a slash command.

    Args:
        slash_command: The slash command to look up
        default: Default model if not found in mapping

    Returns:
        Model name to use
    """
    return SLASH_COMMAND_MODEL_MAP.get(slash_command, default)


def check_claude_installed() -> None:
    """Check if Claude Code CLI is installed.

    Raises:
        EnvironmentError: If Claude Code CLI is not installed or not functional
    """
    try:
        result = subprocess.run(
            [CLAUDE_PATH, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise EnvironmentError(
            f"Claude Code CLI not functional at: {CLAUDE_PATH}",
            required_tools=["claude"],
            claude_path=CLAUDE_PATH,
            stderr=e.stderr
        ) from e
    except FileNotFoundError as e:
        raise EnvironmentError(
            f"Claude Code CLI not found at: {CLAUDE_PATH}",
            required_tools=["claude"],
            claude_path=CLAUDE_PATH,
            instruction="Install Claude Code or set CLAUDE_CODE_PATH environment variable"
        ) from e


def parse_jsonl_output(
    output_file: str,
) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Parse JSONL output file and return all messages and the result message.

    Returns:
        Tuple of (all_messages, result_message) where result_message is None if not found

    Raises:
        FileSystemError: If file cannot be read or parsed
    """
    try:
        with open(output_file, "r") as f:
            # Read all lines and parse each as JSON
            messages = [json.loads(line) for line in f if line.strip()]

            # Find the result message (should be the last one)
            result_message = None
            for message in reversed(messages):
                if message.get("type") == "result":
                    result_message = message
                    break

            return messages, result_message
    except FileNotFoundError as e:
        raise FileSystemError(
            f"Output file not found: {output_file}",
            path=output_file,
            operation="read"
        ) from e
    except json.JSONDecodeError as e:
        raise FileSystemError(
            f"Failed to parse JSONL output: {output_file}",
            path=output_file,
            operation="parse",
            parse_error=str(e)
        ) from e
    except Exception as e:
        raise FileSystemError(
            f"Unexpected error reading output file: {output_file}",
            path=output_file,
            operation="read",
            error=str(e)
        ) from e


def convert_jsonl_to_json(jsonl_file: str) -> str:
    """Convert JSONL file to JSON array file.

    Creates a .json file with the same name as the .jsonl file,
    containing all messages as a JSON array.

    Returns:
        Path to the created JSON file
    """
    # Create JSON filename by replacing .jsonl with .json
    json_file = jsonl_file.replace(".jsonl", ".json")

    # Parse the JSONL file
    messages, _ = parse_jsonl_output(jsonl_file)

    # Write as JSON array
    with open(json_file, "w") as f:
        json.dump(messages, f, indent=2)

    print(f"Created JSON file: {json_file}")
    return json_file


def get_claude_env() -> Dict[str, str]:
    """Get only the required environment variables for Claude Code execution.

    This is a wrapper around get_safe_subprocess_env() from utils.py for
    backward compatibility. New code should use get_safe_subprocess_env() directly.

    Returns a dictionary containing only the necessary environment variables
    based on .env.sample configuration.
    """
    # Import here to avoid circular imports
    from adw_modules.utils import get_safe_subprocess_env

    # Use the shared function
    return get_safe_subprocess_env()


def save_prompt(prompt: str, adw_id: str, agent_name: str = "ops") -> None:
    """Save a prompt to the appropriate logging directory."""
    # Extract slash command from prompt
    match = re.match(r"^(/\w+)", prompt)
    if not match:
        return

    slash_command = match.group(1)
    # Remove leading slash for filename
    command_name = slash_command[1:]

    # Create directory structure at project root (parent of adws)
    # __file__ is in adws/adw_modules/, so we need to go up 3 levels to get to project root
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    prompt_dir = os.path.join(project_root, "agents", adw_id, agent_name, "prompts")
    os.makedirs(prompt_dir, exist_ok=True)

    # Save prompt to file
    prompt_file = os.path.join(prompt_dir, f"{command_name}.txt")
    with open(prompt_file, "w") as f:
        f.write(prompt)

    print(f"Saved prompt to: {prompt_file}")


def prompt_claude_code(request: AgentPromptRequest) -> AgentPromptResponse:
    """Execute Claude Code with the given prompt configuration.

    Raises:
        EnvironmentError: If Claude Code CLI is not available
        AgentError: If agent execution fails
        FileSystemError: If file operations fail
        TokenLimitError: If token limits are exceeded
    """
    # Check if Claude Code CLI is installed
    try:
        check_claude_installed()
    except EnvironmentError as e:
        return AgentPromptResponse(output=e.message, success=False, session_id=None)

    # Save prompt before execution
    try:
        save_prompt(request.prompt, request.adw_id, request.agent_name)
    except Exception as e:
        # Don't fail on prompt save errors
        print(f"Warning: Failed to save prompt: {e}", file=sys.stderr)

    # Create output directory if needed
    output_dir = os.path.dirname(request.output_file)
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise FileSystemError(
                f"Failed to create output directory: {output_dir}",
                path=output_dir,
                operation="mkdir",
                error=str(e)
            ) from e

    # Build command - always use stream-json format and verbose
    cmd = [CLAUDE_PATH, "-p", request.prompt]
    cmd.extend(["--model", request.model])
    cmd.extend(["--output-format", "stream-json"])
    cmd.append("--verbose")

    # Add dangerous skip permissions flag if enabled
    if request.dangerously_skip_permissions:
        cmd.append("--dangerously-skip-permissions")

    # Set up environment with only required variables
    env = get_claude_env()

    try:
        # Execute Claude Code and pipe output to file
        with open(request.output_file, "w") as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                timeout=600  # 10 minute timeout
            )

        if result.returncode == 0:
            print(f"Output saved to: {request.output_file}")

            # Parse the JSONL file
            messages, result_message = parse_jsonl_output(request.output_file)

            # Convert JSONL to JSON array file
            json_file = convert_jsonl_to_json(request.output_file)

            if result_message:
                # Extract session_id from result message
                session_id = result_message.get("session_id")

                # Check if there was an error in the result
                is_error = result_message.get("is_error", False)
                subtype = result_message.get("subtype", "")

                # Handle error_during_execution case where there's no result field
                if subtype == "error_during_execution":
                    raise AgentError(
                        "Agent encountered error during execution",
                        agent_name=request.agent_name,
                        session_id=session_id,
                        output_file=request.output_file
                    )

                # Check for token limit errors
                result_text = result_message.get("result", "")
                if "token" in result_text.lower() and "limit" in result_text.lower():
                    raise TokenLimitError(
                        "Agent hit token limit during execution",
                        agent_name=request.agent_name,
                        session_id=session_id,
                        result=result_text
                    )

                return AgentPromptResponse(
                    output=result_text, success=not is_error, session_id=session_id
                )
            else:
                # No result message found, return raw output
                with open(request.output_file, "r") as f:
                    raw_output = f.read()
                return AgentPromptResponse(
                    output=raw_output, success=True, session_id=None
                )
        else:
            stderr = result.stderr
            # Check for specific error types in stderr
            if "token" in stderr.lower() and "limit" in stderr.lower():
                raise TokenLimitError(
                    "Token limit exceeded in Claude Code execution",
                    stderr=stderr,
                    agent_name=request.agent_name
                )

            raise AgentError(
                "Claude Code execution failed",
                agent_name=request.agent_name,
                returncode=result.returncode,
                stderr=stderr,
                command=" ".join(cmd)
            )

    except subprocess.TimeoutExpired as e:
        raise AgentError(
            "Claude Code command timed out after 10 minutes",
            agent_name=request.agent_name,
            timeout=600,
            command=" ".join(cmd)
        ) from e

    except (AgentError, TokenLimitError, FileSystemError):
        # Re-raise our custom exceptions
        raise

    except Exception as e:
        raise AgentError(
            f"Unexpected error executing Claude Code",
            agent_name=request.agent_name,
            error=str(e),
            command=" ".join(cmd)
        ) from e


def execute_template(request: AgentTemplateRequest) -> AgentPromptResponse:
    """Execute a Claude Code template with slash command and arguments."""
    # Override model based on slash command mapping
    if request.slash_command in SLASH_COMMAND_MODEL_MAP:
        mapped_model = SLASH_COMMAND_MODEL_MAP[request.slash_command]
        request = request.model_copy(update={"model": mapped_model})
    else:
        # Use default model of "sonnet" if not in mapping
        request = request.model_copy(update={"model": "sonnet"})

    # Construct prompt from slash command and args
    prompt = f"{request.slash_command} {' '.join(request.args)}"

    # Create output directory with adw_id at project root
    # __file__ is in adws/adw_modules/, so we need to go up 3 levels to get to project root
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    output_dir = os.path.join(
        project_root, "agents", request.adw_id, request.agent_name
    )
    os.makedirs(output_dir, exist_ok=True)

    # Build output file path
    output_file = os.path.join(output_dir, "raw_output.jsonl")

    # Create prompt request with specific parameters
    prompt_request = AgentPromptRequest(
        prompt=prompt,
        adw_id=request.adw_id,
        agent_name=request.agent_name,
        model=request.model,
        dangerously_skip_permissions=True,
        output_file=output_file,
    )

    # Execute and return response (prompt_claude_code now handles all parsing)
    return prompt_claude_code(prompt_request)
