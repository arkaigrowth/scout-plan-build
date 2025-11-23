#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from utils.constants import ensure_session_log_dir

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def write_current_session(session_id: str, cwd: str) -> None:
    """
    Write current session info to .current_session file.
    This enables other tools to know which Claude session is active.
    """
    session_file = Path(cwd) / '.current_session'

    # Get git hash for correlation
    git_hash = "unknown"
    git_branch = "unknown"
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd, capture_output=True, text=True
        )
        if result.returncode == 0:
            git_hash = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, capture_output=True, text=True
        )
        if result.returncode == 0:
            git_branch = result.stdout.strip()
    except Exception:
        pass

    session_data = {
        "session_id": session_id,
        "short_id": session_id[:8] if len(session_id) >= 8 else session_id,
        "git_hash": git_hash,
        "git_branch": git_branch,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        session_file.write_text(json.dumps(session_data, indent=2))
    except Exception:
        pass  # Don't fail the hook if we can't write


def log_user_prompt(session_id, input_data):
    """Log user prompt to session directory."""
    # Ensure session log directory exists
    log_dir = ensure_session_log_dir(session_id)
    log_file = log_dir / 'user_prompt_submit.json'

    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Append the entire input data
    log_data.append(input_data)

    # Write back to file with formatting
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def validate_prompt(prompt):
    """
    Validate the user prompt for security or policy violations.
    Returns tuple (is_valid, reason).
    """
    # Example validation rules (customize as needed)
    blocked_patterns = [
        # Add any patterns you want to block
        # Example: ('rm -rf /', 'Dangerous command detected'),
    ]
    
    prompt_lower = prompt.lower()
    
    for pattern, reason in blocked_patterns:
        if pattern.lower() in prompt_lower:
            return False, reason
    
    return True, None


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--validate', action='store_true', 
                          help='Enable prompt validation')
        parser.add_argument('--log-only', action='store_true',
                          help='Only log prompts, no validation or blocking')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Extract session_id and prompt
        session_id = input_data.get('session_id', 'unknown')
        prompt = input_data.get('prompt', '')
        cwd = input_data.get('cwd', os.getcwd())

        # Write current session info (for correlation with handoffs/outputs)
        write_current_session(session_id, cwd)

        # Log the user prompt
        log_user_prompt(session_id, input_data)
        
        # Validate prompt if requested and not in log-only mode
        if args.validate and not args.log_only:
            is_valid, reason = validate_prompt(prompt)
            if not is_valid:
                # Exit code 2 blocks the prompt with error message
                print(f"Prompt blocked: {reason}", file=sys.stderr)
                sys.exit(2)
        
        # Add context information (optional)
        # You can print additional context that will be added to the prompt
        # Example: print(f"Current time: {datetime.now()}")
        
        # Success - prompt will be processed
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()