#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
Test for E2E testing functionality in adw_test.py

Tests the complete E2E test flow by running run_e2e_tests_with_resolution
which internally handles test execution and failure resolution.
"""

import sys
import os
import logging
import json
from typing import List

# Add parent directory to path to import from adw_test.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adw_test import run_e2e_tests_with_resolution
from adw_modules.data_types import E2ETestResult
from adw_modules.utils import make_adw_id, setup_logger


def test_e2e_workflow(issue_number: str):
    """Test the complete E2E test workflow."""
    print(f"\n=== Testing E2E Workflow for Issue #{issue_number} ===")
    
    # Setup
    adw_id = make_adw_id()
    logger = setup_logger(adw_id, "test_e2e_workflow")
    
    logger.info(f"Starting E2E workflow test with ADW ID: {adw_id}")
    
    # Run the complete E2E test workflow
    # This function internally:
    # 1. Calls run_e2e_tests to find and execute all .claude/commands/e2e/*.md files
    # 2. If tests fail, calls resolve_failed_e2e_tests to attempt fixes
    # 3. Re-runs tests after resolution (up to max_attempts times)
    # 4. Returns final results
    print("\nRunning E2E tests with automatic resolution...")
    results, passed_count, failed_count = run_e2e_tests_with_resolution(
        adw_id=adw_id,
        issue_number=issue_number,
        logger=logger,
        max_attempts=2   # Allow one retry after resolution
    )
    
    # Display results
    print(f"\n=== Final Results ===")
    print(f"Total E2E tests found: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    
    if results:
        print("\nDetailed results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.test_name}")
            print(f"   Status: {result.status}")
            print(f"   Test path: {result.test_path}")
            if result.screenshots:
                print(f"   Screenshots: {len(result.screenshots)} captured")
                for screenshot in result.screenshots:
                    print(f"     - {screenshot}")
            if result.error:
                print(f"   Error: {result.error}")
    else:
        print("\nNo E2E test files found in .claude/commands/e2e/")
        print("This is expected if running in a test environment without E2E test files.")
    
    # Log summary
    logger.info(f"E2E workflow test completed: {passed_count} passed, {failed_count} failed out of {len(results)} total tests")
    
    # Assertions
    assert isinstance(results, list), "Results should be a list"
    assert all(isinstance(r, E2ETestResult) for r in results), "All results should be E2ETestResult objects"
    assert passed_count >= 0, "Passed count should be non-negative"
    assert failed_count >= 0, "Failed count should be non-negative"
    assert passed_count + failed_count == len(results), "Passed + failed should equal total tests"
    
    print("\n✅ E2E workflow test completed successfully")


def main():
    """Run all tests."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run test_adw_test_e2e.py <issue-number>")
        print("Example: uv run test_adw_test_e2e.py 123")
        return 1
    
    issue_number = sys.argv[1]
    print(f"Starting E2E functionality tests for issue #{issue_number}...")
    
    try:
        # Ensure we have required env vars
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️  Warning: ANTHROPIC_API_KEY not set, some functionality may fail")
        
        test_e2e_workflow(issue_number)
        
        print("\n✅ All tests completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())