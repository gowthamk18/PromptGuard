"""
AI Testing Engine for PromptGuard.
Executes test cases against the chatbot under test using the user's exact system prompt
and captures raw responses via OpenAI API.
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional


class TestingEngine:
    """Orchestrates chatbot execution for selected red-team test cases."""

    def __init__(self, openai_handler):
        self.openai_handler = openai_handler

    def run_single_test(
        self,
        system_prompt: str,
        test_case: Dict[str, Any],
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Execute a single test case against the target system prompt.
        Preserves raw model response and execution metrics.
        """
        test_id = test_case.get("id", "TC-UNKNOWN")
        test_input = test_case.get("input", "")
        category = test_case.get("category", "Normal")
        test_name = test_case.get("name", "Unnamed Test")
        expected_behavior = test_case.get("expected_behavior", "")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Call OpenAI API through the client handler
        api_result = self.openai_handler.chat_completion(
            system_prompt=system_prompt,
            user_message=test_input,
            temperature=temperature,
            max_tokens=600
        )

        success = api_result.get("success", False)
        error_msg = api_result.get("error")
        raw_response = api_result.get("content", "")
        latency = api_result.get("latency_sec", 0.0)
        tokens = api_result.get("tokens_used", 0)

        # Handle empty response edge case
        if success and not raw_response.strip():
            raw_response = "[EMPTY_RESPONSE] The model returned an empty message."

        return {
            "test_id": test_id,
            "test_name": test_name,
            "category": category,
            "test_input": test_input,
            "expected_behavior": expected_behavior,
            "system_prompt_used": system_prompt,
            "actual_response": raw_response,
            "execution_success": success,
            "error": error_msg,
            "latency_sec": latency,
            "tokens_used": tokens,
            "timestamp": timestamp,
            "is_simulated": api_result.get("is_simulated", False)
        }

    def run_test_suite(
        self,
        system_prompt: str,
        test_cases: List[Dict[str, Any]],
        temperature: float = 0.2,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a list of selected test cases sequentially.
        Calls progress_callback(current_index, total_count, current_test_name) if supplied.
        """
        results = []
        total = len(test_cases)

        for i, tc in enumerate(test_cases):
            if progress_callback:
                progress_callback(i, total, tc.get("name", f"Test {i+1}"))

            run_result = self.run_single_test(
                system_prompt=system_prompt,
                test_case=tc,
                temperature=temperature
            )
            results.append(run_result)

        if progress_callback:
            progress_callback(total, total, "Testing completed.")

        return results
