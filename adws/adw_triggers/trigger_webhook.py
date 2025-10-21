#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fastapi", "uvicorn", "python-dotenv"]
# ///

"""
GitHub Webhook Trigger - AI Developer Workflow (ADW)

FastAPI webhook endpoint that receives GitHub issue events and triggers ADW workflows.
Responds immediately to meet GitHub's 10-second timeout by launching adw_plan_build.py
in the background.

Usage: uv run trigger_webhook.py

Environment Requirements:
- PORT: Server port (default: 8001)
- All adw_plan_build.py requirements (GITHUB_PAT, ANTHROPIC_API_KEY, etc.)
"""

import os
import subprocess
import sys
from typing import Optional
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adw_modules.utils import make_adw_id, setup_logger, get_safe_subprocess_env
from adw_modules.github import make_issue_comment, ADW_BOT_IDENTIFIER
from adw_modules.workflow_ops import extract_adw_info, AVAILABLE_ADW_WORKFLOWS
from adw_modules.state import ADWState

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv("PORT", "8001"))

# Create FastAPI app
app = FastAPI(
    title="ADW Webhook Trigger", description="GitHub webhook endpoint for ADW"
)

print(f"Starting ADW Webhook Trigger on port {PORT}")


@app.post("/gh-webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    try:
        # Get event type from header
        event_type = request.headers.get("X-GitHub-Event", "")

        # Parse webhook payload
        payload = await request.json()

        # Extract event details
        action = payload.get("action", "")
        issue = payload.get("issue", {})
        issue_number = issue.get("number")

        print(
            f"Received webhook: event={event_type}, action={action}, issue_number={issue_number}"
        )

        workflow = None
        provided_adw_id = None
        trigger_reason = ""
        content_to_check = ""

        # Check if this is an issue opened event
        if event_type == "issues" and action == "opened" and issue_number:
            issue_body = issue.get("body", "")
            content_to_check = issue_body

            # Check if body contains "adw_"
            if "adw_" in issue_body.lower():
                # Use temporary ID for classification
                temp_id = make_adw_id()
                workflow, provided_adw_id = extract_adw_info(issue_body, temp_id)
                if workflow:
                    trigger_reason = f"New issue with {workflow} workflow"

        # Check if this is an issue comment
        elif event_type == "issue_comment" and action == "created" and issue_number:
            comment = payload.get("comment", {})
            comment_body = comment.get("body", "")
            content_to_check = comment_body

            print(f"Comment body: '{comment_body}'")

            # Ignore comments from ADW bot to prevent loops
            if ADW_BOT_IDENTIFIER in comment_body:
                print(f"Ignoring ADW bot comment to prevent loop")
                workflow = None
            # Check if comment contains "adw_"
            elif "adw_" in comment_body.lower():
                # Use temporary ID for classification
                temp_id = make_adw_id()
                workflow, provided_adw_id = extract_adw_info(comment_body, temp_id)
                if workflow:
                    trigger_reason = f"Comment with {workflow} workflow"

        # Validate workflow constraints
        if workflow == "adw_build" and not provided_adw_id:
            print(f"adw_build requires an adw_id, skipping")
            workflow = None

        if workflow == "adw_document" and not provided_adw_id:
            print(f"adw_document requires an adw_id, skipping")
            workflow = None

        if workflow:
            # Use provided ADW ID or generate a new one
            adw_id = provided_adw_id or make_adw_id()

            # If ADW ID was provided, update/create state file
            if provided_adw_id:
                # Try to load existing state first
                state = ADWState.load(provided_adw_id)
                if state:
                    # Update only the issue_number if state exists
                    state.update(issue_number=str(issue_number))
                else:
                    # Only create new state if it doesn't exist
                    state = ADWState(provided_adw_id)
                    state.update(adw_id=provided_adw_id, issue_number=str(issue_number))
                state.save("webhook_trigger")

            # Set up logger
            logger = setup_logger(adw_id, "webhook_trigger")
            logger.info(
                f"Detected workflow: {workflow} from content: {content_to_check[:100]}..."
            )
            if provided_adw_id:
                logger.info(f"Using provided ADW ID: {provided_adw_id}")

            # Post comment to issue about detected workflow
            try:
                make_issue_comment(
                    str(issue_number),
                    f"{ADW_BOT_IDENTIFIER} 🤖 ADW Webhook: Detected `{workflow}` workflow request\n\n"
                    f"Starting workflow with ID: `{adw_id}`\n"
                    f"Reason: {trigger_reason}\n\n"
                    f"Logs will be available at: `agents/{adw_id}/{workflow}/`",
                )
            except Exception as e:
                logger.warning(f"Failed to post issue comment: {e}")

            # Build command to run the appropriate workflow
            script_dir = os.path.dirname(os.path.abspath(__file__))
            adws_dir = os.path.dirname(script_dir)
            repo_root = os.path.dirname(adws_dir)  # Go up to repository root
            trigger_script = os.path.join(adws_dir, f"{workflow}.py")

            cmd = ["uv", "run", trigger_script, str(issue_number), adw_id]

            print(f"Launching {workflow} for issue #{issue_number}")
            print(f"Command: {' '.join(cmd)} (reason: {trigger_reason})")
            print(f"Working directory: {repo_root}")

            # Launch in background using Popen with filtered environment
            process = subprocess.Popen(
                cmd,
                cwd=repo_root,  # Run from repository root where .claude/commands/ is located
                env=get_safe_subprocess_env(),  # Pass only required environment variables
            )

            print(
                f"Background process started for issue #{issue_number} with ADW ID: {adw_id}"
            )
            print(f"Logs will be written to: agents/{adw_id}/{workflow}/execution.log")

            # Return immediately
            return {
                "status": "accepted",
                "issue": issue_number,
                "adw_id": adw_id,
                "workflow": workflow,
                "message": f"ADW {workflow} workflow triggered for issue #{issue_number}",
                "reason": trigger_reason,
                "logs": f"agents/{adw_id}/{workflow}/",
            }
        else:
            print(
                f"Ignoring webhook: event={event_type}, action={action}, issue_number={issue_number}"
            )
            return {
                "status": "ignored",
                "reason": f"Not a triggering event (event={event_type}, action={action})",
            }

    except Exception as e:
        print(f"Error processing webhook: {e}")
        # Always return 200 to GitHub to prevent retries
        return {"status": "error", "message": "Internal error processing webhook"}


@app.get("/health")
async def health():
    """Health check endpoint - runs comprehensive system health check."""
    try:
        # Run the health check script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Health check is in adw_tests, not adw_triggers
        health_check_script = os.path.join(
            os.path.dirname(script_dir), "adw_tests", "health_check.py"
        )

        # Run health check with timeout
        result = subprocess.run(
            ["uv", "run", health_check_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(script_dir),  # Run from adws directory
        )

        # Print the health check output for debugging
        print("=== Health Check Output ===")
        print(result.stdout)
        if result.stderr:
            print("=== Health Check Errors ===")
            print(result.stderr)

        # Parse the output - look for the overall status
        output_lines = result.stdout.strip().split("\n")
        is_healthy = result.returncode == 0

        # Extract key information from output
        warnings = []
        errors = []

        capturing_warnings = False
        capturing_errors = False

        for line in output_lines:
            if "⚠️  Warnings:" in line:
                capturing_warnings = True
                capturing_errors = False
                continue
            elif "❌ Errors:" in line:
                capturing_errors = True
                capturing_warnings = False
                continue
            elif "📝 Next Steps:" in line:
                break

            if capturing_warnings and line.strip().startswith("-"):
                warnings.append(line.strip()[2:])
            elif capturing_errors and line.strip().startswith("-"):
                errors.append(line.strip()[2:])

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "adw-webhook-trigger",
            "health_check": {
                "success": is_healthy,
                "warnings": warnings,
                "errors": errors,
                "details": "Run health_check.py directly for full report",
            },
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "unhealthy",
            "service": "adw-webhook-trigger",
            "error": "Health check timed out",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "adw-webhook-trigger",
            "error": f"Health check failed: {str(e)}",
        }


if __name__ == "__main__":
    print(f"Starting server on http://0.0.0.0:{PORT}")
    print(f"Webhook endpoint: POST /gh-webhook")
    print(f"Health check: GET /health")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
