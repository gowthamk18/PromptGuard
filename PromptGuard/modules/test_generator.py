"""
Test Case Manager and Generator for PromptGuard.
Handles persistent storage of test cases, category filtering, CRUD operations,
and optional AI test case generation.
"""

import json
import os
from typing import List, Dict, Any, Optional

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test_cases.json")


class TestManager:
    """Manages the PromptGuard red-teaming test suite."""

    CATEGORIES = ["Normal", "Out-of-Scope", "Prompt Injection", "Edge Case"]

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or DEFAULT_DATA_PATH
        self.test_cases: List[Dict[str, Any]] = []
        self.load_tests()

    def load_tests(self) -> List[Dict[str, Any]]:
        """Load test cases from JSON storage."""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.test_cases = json.load(f)
            except Exception as e:
                print(f"Error loading test cases from {self.data_path}: {e}")
                self.test_cases = []
        else:
            self.test_cases = []
        return self.test_cases

    def save_tests(self) -> bool:
        """Persist current test cases back to JSON storage."""
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.test_cases, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving test cases: {e}")
            return False

    def get_all(self) -> List[Dict[str, Any]]:
        """Return all test cases."""
        return self.test_cases

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filter test cases by category."""
        if category == "All" or not category:
            return self.test_cases
        return [t for t in self.test_cases if t.get("category", "").lower() == category.lower()]

    def get_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific test case by ID."""
        for t in self.test_cases:
            if t.get("id") == test_id:
                return t
        return None

    def add_test(self, test_case: Dict[str, Any]) -> bool:
        """Add a new test case with an auto-generated or verified unique ID."""
        if not test_case.get("id"):
            category_prefix = test_case.get("category", "Normal")[:3].upper()
            next_num = len(self.test_cases) + 1
            test_case["id"] = f"TC-{category_prefix}-{next_num:02d}"

        # Ensure unique ID
        existing_ids = {t["id"] for t in self.test_cases}
        base_id = test_case["id"]
        counter = 1
        while test_case["id"] in existing_ids:
            test_case["id"] = f"{base_id}_{counter}"
            counter += 1

        self.test_cases.append(test_case)
        return self.save_tests()

    def update_test(self, test_id: str, updated_fields: Dict[str, Any]) -> bool:
        """Update an existing test case."""
        for i, t in enumerate(self.test_cases):
            if t.get("id") == test_id:
                self.test_cases[i].update(updated_fields)
                return self.save_tests()
        return False

    def delete_test(self, test_id: str) -> bool:
        """Delete a test case by ID."""
        initial_len = len(self.test_cases)
        self.test_cases = [t for t in self.test_cases if t.get("id") != test_id]
        if len(self.test_cases) < initial_len:
            return self.save_tests()
        return False

    def generate_ai_tests(
        self,
        openai_handler,
        chatbot_role: str,
        permitted_topics: str,
        restricted_topics: str,
        category: str,
        count: int = 3
    ) -> Dict[str, Any]:
        """Generate new test cases using the OpenAI API."""
        if not openai_handler.is_configured():
            return {
                "success": False,
                "error": "OpenAI API key not configured.",
                "test_cases": []
            }

        prompt_template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "test_generator.txt"
        )
        system_instruction = "You are PromptGuard's Test Case Generator."
        if os.path.exists(prompt_template_path):
            with open(prompt_template_path, "r", encoding="utf-8") as f:
                system_instruction = f.read()

        user_prompt = f"""
Generate {count} test cases for the following chatbot:
Role: {chatbot_role}
Permitted Topics: {permitted_topics}
Restricted Topics: {restricted_topics}
Target Category: {category}

Return ONLY a valid JSON array of test case objects.
Schema:
[
  {{
    "id": "TC-GEN-01",
    "category": "{category}",
    "name": "Short name",
    "input": "User query text",
    "expected_behavior": "Expected behavior",
    "severity": "Low | Medium | High"
  }}
]
"""
        response = openai_handler.chat_completion(
            system_prompt=system_instruction,
            user_message=user_prompt,
            temperature=0.7,
            max_tokens=1000
        )

        if not response.get("success"):
            return {
                "success": False,
                "error": response.get("error", "Failed to generate tests"),
                "test_cases": []
            }

        content = response["content"]
        # Clean JSON markdown fences
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            generated = json.loads(content)
            if isinstance(generated, list):
                return {
                    "success": True,
                    "error": None,
                    "test_cases": generated
                }
            return {
                "success": False,
                "error": "Generated content was not a valid list of test cases.",
                "test_cases": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse generated JSON: {str(e)}",
                "test_cases": []
            }
