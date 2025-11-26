#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
Test Agent Models - Verify opus and sonnet models work with Claude Code

This script tests that both models can execute a simple prompt through agent.py in parallel.
"""

import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adw_modules.data_types import AgentPromptRequest, AgentPromptResponse
from adw_modules.agent import prompt_claude_code
from adw_modules.utils import make_adw_id

# Load environment variables
load_dotenv()

# Test configuration
MODELS = ["opus", "sonnet"]
TEST_PROMPT = """You are a helpful assistant. Please respond to this test with:
1. Confirm you received this message
2. State which model you are (opus or sonnet)
3. Say "Test successful!"

Keep your response brief."""


def test_model(model: str, adw_id: str) -> tuple[bool, str]:
    """Test a specific model and return success status and message."""
    print(f"\n{'='*50}")
    print(f"Testing model: {model}")
    print(f"{'='*50}")
    
    # Create output file path
    output_file = f"logs/{adw_id}/agent_test_{model}.jsonl"
    
    # Create request
    request = AgentPromptRequest(
        prompt=TEST_PROMPT,
        adw_id=adw_id,
        agent_name=f"test_{model}",
        model=model,
        dangerously_skip_permissions=True,  # Skip for testing
        output_file=output_file
    )
    
    try:
        # Execute prompt
        print(f"Executing prompt for {model}...")
        response: AgentPromptResponse = prompt_claude_code(request)
        
        if response.success:
            print(f"✅ {model} - Success!")
            print(f"Session ID: {response.session_id}")
            print(f"Response preview: {response.output[:200]}...")
            return True, f"{model}: Success"
        else:
            print(f"❌ {model} - Failed!")
            print(f"Error: {response.output}")
            return False, f"{model}: {response.output}"
            
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        print(f"❌ {model} - Exception!")
        print(error_msg)
        return False, f"{model}: {error_msg}"


def main():
    """Run tests for all models in parallel."""
    # Generate ADW ID for this test run
    adw_id = make_adw_id()
    
    print("Testing Claude Code agent with different models (in parallel)")
    print(f"ADW ID: {adw_id}")
    print(f"Models to test: {', '.join(MODELS)}")
    print(f"Starting parallel execution...")
    
    # Track results
    results = {}
    all_success = True
    
    # Run tests in parallel
    with ThreadPoolExecutor(max_workers=len(MODELS)) as executor:
        # Submit all test tasks
        future_to_model = {
            executor.submit(test_model, model, adw_id): model 
            for model in MODELS
        }
        
        # Process results as they complete
        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                success, message = future.result()
                results[model] = (success, message)
                if not success:
                    all_success = False
            except Exception as e:
                results[model] = (False, f"Exception during test: {str(e)}")
                all_success = False
                print(f"❌ {model} - Exception during parallel execution: {str(e)}")
    
    # Summary (ordered by original MODELS list)
    print(f"\n{'='*50}")
    print("Test Summary")
    print(f"{'='*50}")
    
    for model in MODELS:
        if model in results:
            success, message = results[model]
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {message}")
    
    print(f"\nOverall: {'✅ All tests passed!' if all_success else '❌ Some tests failed!'}")
    
    # Exit with appropriate code
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()