"""Step 5b: Test Case Agent — generates test cases from the spec."""
import logging
from .llm_helper import LLMHelper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a QA engineer generating test cases from a product spec.
Given the requirements, data models, and state machines, generate comprehensive test cases.

Respond in this exact JSON format:
{
  "test_cases": [
    {
      "id": "TC001",
      "title": "Reader borrows an available book",
      "steps": ["Reader logs in", "Reader searches for a book", "Reader clicks borrow", "System changes book status to borrowed"],
      "expected_result": "Book status changes from available to borrowed, borrowing record created",
      "category": "functional"
    },
    {
      "id": "TC005",
      "title": "Reader tries to borrow when they have overdue books",
      "steps": ["Reader has an overdue book", "Reader tries to borrow another book"],
      "expected_result": "System rejects the borrow with error message",
      "category": "edge"
    }
  ]
}

Rules:
- Generate 8-15 test cases covering functional, edge, and permission scenarios.
- Categories: functional (normal flow), edge (boundary conditions), permission (access control).
- Include at least 2 edge cases and 2 permission test cases.
- Reference specific states and fields from the data model.
- Each test case must have clear steps and expected results."""


class TestCaseAgent:
    """Generates test cases from the spec."""

    def __init__(self, llm: LLMHelper):
        self.llm = llm

    def run(self, business_description: str, requirements: dict, data_models: dict, state_machines: dict) -> dict:
        """Generate test cases from the full spec."""
        logger.info("TestCaseAgent: generating test cases...")

        import json
        spec_summary = json.dumps({
            "entities": [m["name"] for m in data_models.get("models", [])],
            "state_machines": [
                {"entity": sm["entity"], "states": sm["states"]}
                for sm in state_machines.get("state_machines", [])
            ],
            "use_cases": requirements.get("use_cases", []),
            "user_roles": [r["name"] for r in requirements.get("user_roles", [])],
        }, ensure_ascii=False)

        result = self.llm.chat_json(
            SYSTEM_PROMPT,
            f"Business description:\n{business_description}\n\nSpec:\n{spec_summary}\n\nGenerate test cases.",
        )

        if not result:
            logger.warning("TestCaseAgent: LLM returned no valid JSON")
            return {"test_cases": []}

        logger.info(f"TestCaseAgent: generated {len(result.get('test_cases', []))} test cases")
        return result