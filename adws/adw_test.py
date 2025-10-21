#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Test - AI Developer Workflow for agentic testing

Usage:
  uv run adw_test.py <issue-number> [adw-id] [--skip-e2e]

Workflow:
1. Fetch GitHub issue details (if not in state)
2. Run application test suite
3. Report results to issue
4. Create commit with test results
5. Push and update PR

Environment Requirements:
- ANTHROPIC_API_KEY: Anthropic API key
- CLAUDE_CODE_PATH: Path to Claude CLI
- GITHUB_PAT: (Optional) GitHub Personal Access Token - only if using a different account than 'gh auth login'
"""

import json
import subprocess
import sys
import os
import logging
from typing import Tuple, Optional, List
from dotenv import load_dotenv
from adw_modules.data_types import (
    AgentTemplateRequest,
    GitHubIssue,
    AgentPromptResponse,
    TestResult,
    E2ETestResult,
    IssueClassSlashCommand,
)
from adw_modules.agent import execute_template
from adw_modules.github import (
    extract_repo_path,
    fetch_issue,
    make_issue_comment,
    get_repo_url,
)
from adw_modules.utils import make_adw_id, setup_logger, parse_json
from adw_modules.state import ADWState
from adw_modules.git_ops import commit_changes, finalize_git_operations
from adw_modules.workflow_ops import (
    format_issue_message,
    create_commit,
    ensure_adw_id,
    classify_issue,
)

# Removed create_or_find_branch - now using state directly

# Agent name constants
AGENT_TESTER = "test_runner"
AGENT_E2E_TESTER = "e2e_test_runner"
AGENT_BRANCH_GENERATOR = "branch_generator"

# Maximum number of test retry attempts after resolution
MAX_TEST_RETRY_ATTEMPTS = 4
MAX_E2E_TEST_RETRY_ATTEMPTS = 2  # E2E ui tests


def check_env_vars(logger: Optional[logging.Logger] = None) -> None:
    """Check that all required environment variables are set."""
    required_vars = [
        "ANTHROPIC_API_KEY",
        "CLAUDE_CODE_PATH",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = "Error: Missing required environment variables:"
        if logger:
            logger.error(error_msg)
            for var in missing_vars:
                logger.error(f"  - {var}")
        else:
            print(error_msg, file=sys.stderr)
            for var in missing_vars:
                print(f"  - {var}", file=sys.stderr)
        sys.exit(1)


def parse_args(
    state: Optional[ADWState] = None,
    logger: Optional[logging.Logger] = None,
) -> Tuple[Optional[str], Optional[str], bool]:
    """Parse command line arguments.
    Returns (issue_number, adw_id, skip_e2e) where issue_number and adw_id may be None.
    """
    skip_e2e = False

    # Check for --skip-e2e flag in args
    if "--skip-e2e" in sys.argv:
        skip_e2e = True
        sys.argv.remove("--skip-e2e")

    # If we have state from stdin, we might not need issue number from args
    if state:
        # In piped mode, we might have no args at all
        if len(sys.argv) >= 2:
            # If an issue number is provided, use it
            return sys.argv[1], None, skip_e2e
        else:
            # Otherwise, we'll get issue from state
            return None, None, skip_e2e

    # Standalone mode - need at least issue number
    if len(sys.argv) < 2:
        usage_msg = [
            "Usage:",
            "  Standalone: uv run adw_test.py <issue-number> [adw-id] [--skip-e2e]",
            "  Chained: ... | uv run adw_test.py [--skip-e2e]",
            "Examples:",
            "  uv run adw_test.py 123",
            "  uv run adw_test.py 123 abc12345",
            "  uv run adw_test.py 123 --skip-e2e",
            '  echo \'{"issue_number": "123"}\' | uv run adw_test.py',
        ]
        if logger:
            for msg in usage_msg:
                logger.error(msg)
        else:
            for msg in usage_msg:
                print(msg)
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    return issue_number, adw_id, skip_e2e


def format_issue_message(
    adw_id: str, agent_name: str, message: str, session_id: Optional[str] = None
) -> str:
    """Format a message for issue comments with ADW tracking."""
    if session_id:
        return f"{adw_id}_{agent_name}_{session_id}: {message}"
    return f"{adw_id}_{agent_name}: {message}"


def log_test_results(
    state: ADWState,
    results: List[TestResult],
    e2e_results: List[E2ETestResult],
    logger: logging.Logger,
) -> None:
    """Log comprehensive test results summary to the issue."""
    issue_number = state.get("issue_number")
    adw_id = state.get("adw_id")

    if not issue_number:
        logger.warning("No issue number in state, skipping test results logging")
        return

    # Calculate counts
    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count
    e2e_passed_count = sum(1 for r in e2e_results if r.passed)
    e2e_failed_count = len(e2e_results) - e2e_passed_count

    # Create comprehensive summary
    summary = f"## 📊 Test Run Summary\n\n"

    # Unit tests summary
    summary += f"### Unit Tests\n"
    summary += f"**Total Tests:** {len(results)}\n"
    summary += f"**Passed:** {passed_count} ✅\n"
    summary += f"**Failed:** {failed_count} ❌\n\n"

    if results:
        summary += "#### Details:\n"
        for result in results:
            status = "✅" if result.passed else "❌"
            summary += f"- {status} **{result.test_name}**\n"
            if not result.passed and result.error:
                summary += f"  - Error: {result.error[:200]}...\n"

    # E2E tests summary if they were run
    if e2e_results:
        summary += f"\n### E2E Tests\n"
        summary += f"**Total Tests:** {len(e2e_results)}\n"
        summary += f"**Passed:** {e2e_passed_count} ✅\n"
        summary += f"**Failed:** {e2e_failed_count} ❌\n\n"

        summary += "#### Details:\n"
        for result in e2e_results:
            status = "✅" if result.passed else "❌"
            summary += f"- {status} **{result.test_name}**\n"
            if not result.passed and result.error:
                summary += f"  - Error: {result.error[:200]}...\n"
            if result.screenshots:
                summary += f"  - Screenshots: {', '.join(result.screenshots)}\n"

    # Overall status
    total_failures = failed_count + e2e_failed_count
    if total_failures > 0:
        summary += f"\n### ❌ Overall Status: FAILED\n"
        summary += f"Total failures: {total_failures}\n"
    else:
        summary += f"\n### ✅ Overall Status: PASSED\n"
        summary += f"All {len(results) + len(e2e_results)} tests passed successfully!\n"

    # Post the summary to the issue
    make_issue_comment(
        issue_number, format_issue_message(adw_id, "test_summary", summary)
    )

    logger.info(f"Posted comprehensive test results summary to issue #{issue_number}")


def run_tests(adw_id: str, logger: logging.Logger) -> AgentPromptResponse:
    """Run the test suite using the /test command."""
    test_template_request = AgentTemplateRequest(
        agent_name=AGENT_TESTER,
        slash_command="/test",
        args=[],
        adw_id=adw_id,
    )

    logger.debug(
        f"test_template_request: {test_template_request.model_dump_json(indent=2, by_alias=True)}"
    )

    test_response = execute_template(test_template_request)

    logger.debug(
        f"test_response: {test_response.model_dump_json(indent=2, by_alias=True)}"
    )

    return test_response


def parse_test_results(
    output: str, logger: logging.Logger
) -> Tuple[List[TestResult], int, int]:
    """Parse test results JSON and return (results, passed_count, failed_count)."""
    try:
        # Use parse_json to handle markdown-wrapped JSON
        results = parse_json(output, List[TestResult])

        passed_count = sum(1 for test in results if test.passed)
        failed_count = len(results) - passed_count

        return results, passed_count, failed_count
    except Exception as e:
        logger.error(f"Error parsing test results: {e}")
        return [], 0, 0


def format_test_results_comment(
    results: List[TestResult], passed_count: int, failed_count: int
) -> str:
    """Format test results for GitHub issue comment with JSON blocks."""
    if not results:
        return "❌ No test results found"

    # Separate failed and passed tests
    failed_tests = [test for test in results if not test.passed]
    passed_tests = [test for test in results if test.passed]

    # Build comment
    comment_parts = []

    # Failed tests header
    if failed_tests:
        comment_parts.append("")
        comment_parts.append("## ❌ Failed Tests")
        comment_parts.append("")

        # Loop over each failed test
        for test in failed_tests:
            comment_parts.append(f"### {test.test_name}")
            comment_parts.append("")
            comment_parts.append("```json")
            comment_parts.append(json.dumps(test.model_dump(), indent=2))
            comment_parts.append("```")
            comment_parts.append("")

    # Passed tests header
    if passed_tests:
        comment_parts.append("## ✅ Passed Tests")
        comment_parts.append("")

        # Loop over each passed test
        for test in passed_tests:
            comment_parts.append(f"### {test.test_name}")
            comment_parts.append("")
            comment_parts.append("```json")
            comment_parts.append(json.dumps(test.model_dump(), indent=2))
            comment_parts.append("```")
            comment_parts.append("")

    # Remove trailing empty line
    if comment_parts and comment_parts[-1] == "":
        comment_parts.pop()

    return "\n".join(comment_parts)


def resolve_failed_tests(
    failed_tests: List[TestResult],
    adw_id: str,
    issue_number: str,
    logger: logging.Logger,
    iteration: int = 1,
) -> Tuple[int, int]:
    """
    Attempt to resolve failed tests using the resolve_failed_test command.
    Returns (resolved_count, unresolved_count).
    """
    resolved_count = 0
    unresolved_count = 0

    for idx, test in enumerate(failed_tests):
        logger.info(
            f"\n=== Resolving failed test {idx + 1}/{len(failed_tests)}: {test.test_name} ==="
        )

        # Create payload for the resolve command
        test_payload = test.model_dump_json(indent=2)

        # Create agent name with iteration
        agent_name = f"test_resolver_iter{iteration}_{idx}"

        # Create template request
        resolve_request = AgentTemplateRequest(
            agent_name=agent_name,
            slash_command="/resolve_failed_test",
            args=[test_payload],
            adw_id=adw_id,
        )

        # Post to issue
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                agent_name,
                f"❌ Attempting to resolve: {test.test_name}\n```json\n{test_payload}\n```",
            ),
        )

        # Execute resolution
        response = execute_template(resolve_request)

        if response.success:
            resolved_count += 1
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    agent_name,
                    f"✅ Successfully resolved: {test.test_name}",
                ),
            )
            logger.info(f"Successfully resolved: {test.test_name}")
        else:
            unresolved_count += 1
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    agent_name,
                    f"❌ Failed to resolve: {test.test_name}",
                ),
            )
            logger.error(f"Failed to resolve: {test.test_name}")

    return resolved_count, unresolved_count


def run_tests_with_resolution(
    adw_id: str,
    issue_number: str,
    logger: logging.Logger,
    max_attempts: int = MAX_TEST_RETRY_ATTEMPTS,
) -> Tuple[List[TestResult], int, int, AgentPromptResponse]:
    """
    Run tests with automatic resolution and retry logic.
    Returns (results, passed_count, failed_count, last_test_response).
    """
    attempt = 0
    results = []
    passed_count = 0
    failed_count = 0
    test_response = None

    while attempt < max_attempts:
        attempt += 1
        logger.info(f"\n=== Test Run Attempt {attempt}/{max_attempts} ===")

        # Run tests
        test_response = run_tests(adw_id, logger)

        # If there was a high level - non-test related error, stop and report it
        if not test_response.success:
            logger.error(f"Error running tests: {test_response.output}")
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    AGENT_TESTER,
                    f"❌ Error running tests: {test_response.output}",
                ),
            )
            break

        # Parse test results
        results, passed_count, failed_count = parse_test_results(
            test_response.output, logger
        )

        # If no failures or this is the last attempt, we're done
        if failed_count == 0:
            logger.info("All tests passed, stopping retry attempts")
            break
        if attempt == max_attempts:
            logger.info(f"Reached maximum retry attempts ({max_attempts}), stopping")
            break

        # If we have failed tests and this isn't the last attempt, try to resolve
        logger.info("\n=== Attempting to resolve failed tests ===")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                "ops",
                f"❌ Found {failed_count} failed tests. Attempting resolution...",
            ),
        )

        # Get list of failed tests
        failed_tests = [test for test in results if not test.passed]

        # Attempt resolution
        resolved, unresolved = resolve_failed_tests(
            failed_tests, adw_id, issue_number, logger, iteration=attempt
        )

        # Report resolution results
        if resolved > 0:
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id, "ops", f"✅ Resolved {resolved}/{failed_count} failed tests"
                ),
            )

            # Continue to next attempt if we resolved something
            logger.info(f"\n=== Re-running tests after resolving {resolved} tests ===")
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    AGENT_TESTER,
                    f"🔄 Re-running tests (attempt {attempt + 1}/{max_attempts})...",
                ),
            )
        else:
            # No tests were resolved, no point in retrying
            logger.info("No tests were resolved, stopping retry attempts")
            break

    # Log final attempt status
    if attempt == max_attempts and failed_count > 0:
        logger.warning(
            f"Reached maximum retry attempts ({max_attempts}) with {failed_count} failures remaining"
        )
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                "ops",
                f"⚠️ Reached maximum retry attempts ({max_attempts}) with {failed_count} failures",
            ),
        )

    return results, passed_count, failed_count, test_response


def run_e2e_tests(
    adw_id: str,
    issue_number: str,
    logger: logging.Logger,
    attempt: int = 1,
) -> List[E2ETestResult]:
    """Run all E2E tests found in .claude/commands/e2e/*.md sequentially."""
    import glob

    # Find all E2E test files
    e2e_test_files = glob.glob(".claude/commands/e2e/*.md")
    logger.info(f"Found {len(e2e_test_files)} E2E test files")

    if not e2e_test_files:
        logger.warning("No E2E test files found in .claude/commands/e2e/")
        return []

    results = []

    # Run tests sequentially
    for idx, test_file in enumerate(e2e_test_files):
        agent_name = f"{AGENT_E2E_TESTER}_{attempt - 1}_{idx}"
        result = execute_single_e2e_test(
            test_file, agent_name, adw_id, issue_number, logger
        )
        if result:
            results.append(result)
            # Break on first failure
            if not result.passed:
                logger.info(f"E2E test failed: {result.test_name}, stopping execution")
                break

    return results


def execute_single_e2e_test(
    test_file: str,
    agent_name: str,
    adw_id: str,
    issue_number: str,
    logger: logging.Logger,
) -> Optional[E2ETestResult]:
    """Execute a single E2E test and return the result."""
    test_name = os.path.basename(test_file).replace(".md", "")
    logger.info(f"Running E2E test: {test_name}")

    # Make issue comment
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, agent_name, f"✅ Running E2E test: {test_name}"),
    )

    # Create template request
    request = AgentTemplateRequest(
        agent_name=agent_name,
        slash_command="/test_e2e",
        args=[
            adw_id,
            agent_name,
            test_file,
        ],  # Pass ADW ID and agent name for screenshot directory
        adw_id=adw_id,
    )

    # Execute test
    response = execute_template(request)

    if not response.success:
        logger.error(f"Error running E2E test {test_name}: {response.output}")
        return E2ETestResult(
            test_name=test_name,
            status="failed",
            test_path=test_file,
            error=f"Test execution error: {response.output}",
        )

    # Parse the response
    try:
        # Parse JSON from response
        result_data = parse_json(response.output, dict)

        # Create E2ETestResult
        e2e_result = E2ETestResult(
            test_name=result_data.get("test_name", test_name),
            status=result_data.get("status", "failed"),
            test_path=test_file,
            screenshots=result_data.get("screenshots", []),
            error=result_data.get("error"),
        )

        # Report complete and show payload
        status_emoji = "✅" if e2e_result.passed else "❌"
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                agent_name,
                f"{status_emoji} E2E test completed: {test_name}\n```json\n{e2e_result.model_dump_json(indent=2)}\n```",
            ),
        )

        return e2e_result
    except Exception as e:
        logger.error(f"Error parsing E2E test result for {test_name}: {e}")
        e2e_result = E2ETestResult(
            test_name=test_name,
            status="failed",
            test_path=test_file,
            error=f"Result parsing error: {str(e)}",
        )

        # Report complete and show payload
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                agent_name,
                f"❌ E2E test completed: {test_name}\n```json\n{e2e_result.model_dump_json(indent=2)}\n```",
            ),
        )

        return e2e_result


def format_e2e_test_results_comment(
    results: List[E2ETestResult], passed_count: int, failed_count: int
) -> str:
    """Format E2E test results for GitHub issue comment."""
    if not results:
        return "❌ No E2E test results found"

    # Separate failed and passed tests
    failed_tests = [test for test in results if not test.passed]
    passed_tests = [test for test in results if test.passed]

    # Build comment
    comment_parts = []

    # Failed tests header
    if failed_tests:
        comment_parts.append("")
        comment_parts.append("## ❌ Failed E2E Tests")
        comment_parts.append("")

        # Loop over each failed test
        for test in failed_tests:
            comment_parts.append(f"### {test.test_name}")
            comment_parts.append("")
            comment_parts.append("```json")
            comment_parts.append(json.dumps(test.model_dump(), indent=2))
            comment_parts.append("```")
            comment_parts.append("")

    # Passed tests header
    if passed_tests:
        comment_parts.append("## ✅ Passed E2E Tests")
        comment_parts.append("")

        # Loop over each passed test
        for test in passed_tests:
            comment_parts.append(f"### {test.test_name}")
            comment_parts.append("")
            if test.screenshots:
                comment_parts.append(f"Screenshots: {len(test.screenshots)} captured")
            comment_parts.append("")

    # Remove trailing empty line
    if comment_parts and comment_parts[-1] == "":
        comment_parts.pop()

    return "\n".join(comment_parts)


def resolve_failed_e2e_tests(
    failed_tests: List[E2ETestResult],
    adw_id: str,
    issue_number: str,
    logger: logging.Logger,
    iteration: int = 1,
) -> Tuple[int, int]:
    """
    Attempt to resolve failed E2E tests using the resolve_failed_e2e_test command.
    Returns (resolved_count, unresolved_count).
    """
    resolved_count = 0
    unresolved_count = 0

    for idx, test in enumerate(failed_tests):
        logger.info(
            f"\n=== Resolving failed E2E test {idx + 1}/{len(failed_tests)}: {test.test_name} ==="
        )

        # Create payload for the resolve command
        test_payload = test.model_dump_json(indent=2)

        # Create agent name with iteration
        agent_name = f"e2e_test_resolver_iter{iteration}_{idx}"

        # Create template request
        resolve_request = AgentTemplateRequest(
            agent_name=agent_name,
            slash_command="/resolve_failed_e2e_test",
            args=[test_payload],
            adw_id=adw_id,
        )

        # Post to issue
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                agent_name,
                f"🔧 Attempting to resolve E2E test: {test.test_name}\n```json\n{test_payload}\n```",
            ),
        )

        # Execute resolution
        response = execute_template(resolve_request)

        if response.success:
            resolved_count += 1
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    agent_name,
                    f"✅ Successfully resolved E2E test: {test.test_name}",
                ),
            )
            logger.info(f"Successfully resolved E2E test: {test.test_name}")
        else:
            unresolved_count += 1
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    agent_name,
                    f"❌ Failed to resolve E2E test: {test.test_name}",
                ),
            )
            logger.error(f"Failed to resolve E2E test: {test.test_name}")

    return resolved_count, unresolved_count


def run_e2e_tests_with_resolution(
    adw_id: str,
    issue_number: str,
    logger: logging.Logger,
    max_attempts: int = MAX_E2E_TEST_RETRY_ATTEMPTS,
) -> Tuple[List[E2ETestResult], int, int]:
    """
    Run E2E tests with automatic resolution and retry logic.
    Returns (results, passed_count, failed_count).
    """
    attempt = 0
    results = []
    passed_count = 0
    failed_count = 0

    while attempt < max_attempts:
        attempt += 1
        logger.info(f"\n=== E2E Test Run Attempt {attempt}/{max_attempts} ===")

        # Run E2E tests
        results = run_e2e_tests(adw_id, issue_number, logger, attempt)

        if not results:
            logger.warning("No E2E test results to process")
            break

        # Count passes and failures
        passed_count = sum(1 for test in results if test.passed)
        failed_count = len(results) - passed_count

        # If no failures or this is the last attempt, we're done
        if failed_count == 0:
            logger.info("All E2E tests passed, stopping retry attempts")
            break
        if attempt == max_attempts:
            logger.info(
                f"Reached maximum E2E retry attempts ({max_attempts}), stopping"
            )
            break

        # If we have failed tests and this isn't the last attempt, try to resolve
        logger.info("\n=== Attempting to resolve failed E2E tests ===")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                "ops",
                f"🔧 Found {failed_count} failed E2E tests. Attempting resolution...",
            ),
        )

        # Get list of failed tests
        failed_tests = [test for test in results if not test.passed]

        # Attempt resolution
        resolved, unresolved = resolve_failed_e2e_tests(
            failed_tests, adw_id, issue_number, logger, iteration=attempt
        )

        # Report resolution results
        if resolved > 0:
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    "ops",
                    f"✅ Resolved {resolved}/{failed_count} failed E2E tests",
                ),
            )

            # Continue to next attempt if we resolved something
            logger.info(
                f"\n=== Re-running E2E tests after resolving {resolved} tests ==="
            )
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    AGENT_E2E_TESTER,
                    f"🔄 Re-running E2E tests (attempt {attempt + 1}/{max_attempts})...",
                ),
            )
        else:
            # No tests were resolved, no point in retrying
            logger.info("No E2E tests were resolved, stopping retry attempts")
            break

    # Log final attempt status
    if attempt == max_attempts and failed_count > 0:
        logger.warning(
            f"Reached maximum E2E retry attempts ({max_attempts}) with {failed_count} failures remaining"
        )
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id,
                "ops",
                f"⚠️ Reached maximum E2E retry attempts ({max_attempts}) with {failed_count} failures",
            ),
        )

    return results, passed_count, failed_count


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse arguments
    arg_issue_number, arg_adw_id, skip_e2e = parse_args(None)

    # Initialize state and issue number
    issue_number = arg_issue_number

    # Ensure we have an issue number
    if not issue_number:
        print("Error: No issue number provided", file=sys.stderr)
        sys.exit(1)

    # Ensure ADW ID exists with initialized state
    temp_logger = setup_logger(arg_adw_id, "adw_test") if arg_adw_id else None
    adw_id = ensure_adw_id(issue_number, arg_adw_id, temp_logger)

    # Load the state that was created/found by ensure_adw_id
    state = ADWState.load(adw_id, temp_logger)

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_test")
    logger.info(f"ADW Test starting - ID: {adw_id}, Issue: {issue_number}")

    # Validate environment (now with logger)
    check_env_vars(logger)

    # Get repo information from git remote
    try:
        github_repo_url: str = get_repo_url()
        repo_path: str = extract_repo_path(github_repo_url)
    except ValueError as e:
        logger.error(f"Error getting repository URL: {e}")
        sys.exit(1)

    # We'll fetch issue details later only if needed
    issue = None
    issue_class = state.get("issue_class")

    # Handle branch - either use existing or create new test branch
    branch_name = state.get("branch_name")
    if branch_name:
        # Try to checkout existing branch
        result = subprocess.run(
            ["git", "checkout", branch_name], capture_output=True, text=True
        )
        if result.returncode != 0:
            logger.error(f"Failed to checkout branch {branch_name}: {result.stderr}")
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id, "ops", f"❌ Failed to checkout branch {branch_name}"
                ),
            )
            sys.exit(1)
        logger.info(f"Checked out existing branch: {branch_name}")
    else:
        # No branch in state - create a test-specific branch
        logger.info("No branch in state, creating test branch")

        # Generate simple test branch name without classification
        branch_name = f"test-issue-{issue_number}-adw-{adw_id}"
        logger.info(f"Generated test branch name: {branch_name}")

        # Create the branch
        from adw_modules.git_ops import create_branch

        success, error = create_branch(branch_name)
        if not success:
            logger.error(f"Error creating branch: {error}")
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id, "ops", f"❌ Error creating branch: {error}"
                ),
            )
            sys.exit(1)

        state.update(branch_name=branch_name)
        state.save("adw_test")
        logger.info(f"Created and checked out new test branch: {branch_name}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, "ops", f"✅ Created test branch: {branch_name}"
            ),
        )

    make_issue_comment(
        issue_number, format_issue_message(adw_id, "ops", "✅ Starting test suite")
    )

    # Run tests with automatic resolution and retry
    logger.info("\n=== Running test suite ===")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_TESTER, "✅ Running application tests..."),
    )

    # Run tests with resolution and retry logic
    results, passed_count, failed_count, test_response = run_tests_with_resolution(
        adw_id, issue_number, logger
    )

    # Format and post final results
    results_comment = format_test_results_comment(results, passed_count, failed_count)
    make_issue_comment(
        issue_number,
        format_issue_message(
            adw_id, AGENT_TESTER, f"📊 Final test results:\n{results_comment}"
        ),
    )

    # Log summary
    logger.info(f"Final test results: {passed_count} passed, {failed_count} failed")

    # If unit tests failed or skip_e2e flag is set, skip E2E tests
    if failed_count > 0:
        logger.warning("Skipping E2E tests due to unit test failures")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, "ops", "⚠️ Skipping E2E tests due to unit test failures"
            ),
        )
        e2e_results = []
        e2e_passed_count = 0
        e2e_failed_count = 0
    elif skip_e2e:
        logger.info("Skipping E2E tests as requested")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, "ops", "⚠️ Skipping E2E tests as requested via --skip-e2e flag"
            ),
        )
        e2e_results = []
        e2e_passed_count = 0
        e2e_failed_count = 0
    else:
        # Run E2E tests since unit tests passed
        logger.info("\n=== Running E2E test suite ===")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, AGENT_E2E_TESTER, "✅ Starting E2E tests..."),
        )

        # Run E2E tests with resolution and retry logic
        e2e_results, e2e_passed_count, e2e_failed_count = run_e2e_tests_with_resolution(
            adw_id, issue_number, logger
        )

        # Format and post E2E results
        if e2e_results:
            e2e_results_comment = format_e2e_test_results_comment(
                e2e_results, e2e_passed_count, e2e_failed_count
            )
            make_issue_comment(
                issue_number,
                format_issue_message(
                    adw_id,
                    AGENT_E2E_TESTER,
                    f"📊 Final E2E test results:\n{e2e_results_comment}",
                ),
            )

            logger.info(
                f"Final E2E test results: {e2e_passed_count} passed, {e2e_failed_count} failed"
            )

    # Commit the test results (whether tests passed or failed)
    logger.info("\n=== Committing test results ===")
    make_issue_comment(
        issue_number,
        format_issue_message(adw_id, AGENT_TESTER, "✅ Committing test results"),
    )

    # Fetch issue details if we haven't already
    if not issue:
        issue = fetch_issue(issue_number, repo_path)

    # Get issue classification if we need it for commit
    if not issue_class:
        issue_class, error = classify_issue(issue, adw_id, logger)
        if error:
            logger.warning(
                f"Error classifying issue: {error}, defaulting to /chore for test commit"
            )
            issue_class = "/chore"
        state.update(issue_class=issue_class)
        state.save("adw_test")

    commit_msg, error = create_commit(AGENT_TESTER, issue, issue_class, adw_id, logger)

    if error:
        logger.error(f"Error committing test results: {error}")
        make_issue_comment(
            issue_number,
            format_issue_message(
                adw_id, AGENT_TESTER, f"❌ Error committing test results: {error}"
            ),
        )
        # Don't exit on commit error, continue to report final status
    else:
        logger.info(f"Test results committed: {commit_msg}")

    # Log comprehensive test results to the issue
    log_test_results(state, results, e2e_results, logger)

    # Finalize git operations (push and create/update PR)
    logger.info("\n=== Finalizing git operations ===")
    finalize_git_operations(state, logger)

    # Update state with test results
    # Note: test_results is not part of core state, but save anyway to track completion
    state.save("adw_test")

    # Output state for chaining
    state.to_stdout()

    # Exit with appropriate code
    total_failures = failed_count + e2e_failed_count
    if total_failures > 0:
        logger.info(f"Test suite completed with failures for issue #{issue_number}")
        failure_msg = f"❌ Test suite completed with failures:\n"
        if failed_count > 0:
            failure_msg += f"- Unit tests: {failed_count} failures\n"
        if e2e_failed_count > 0:
            failure_msg += f"- E2E tests: {e2e_failed_count} failures"
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", failure_msg),
        )
        sys.exit(1)
    else:
        logger.info(f"Test suite completed successfully for issue #{issue_number}")
        success_msg = f"✅ All tests passed successfully!\n"
        success_msg += f"- Unit tests: {passed_count} passed\n"
        if e2e_results:
            success_msg += f"- E2E tests: {e2e_passed_count} passed"
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "ops", success_msg),
        )


if __name__ == "__main__":
    main()
