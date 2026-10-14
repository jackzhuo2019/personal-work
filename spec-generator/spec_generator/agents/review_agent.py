"""Step 5: Review Agent — adversarially checks for gaps, edge cases, and deadlocks."""
import logging
from .llm_helper import LLMHelper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior product reviewer who adversarially checks specs for gaps.
Given the complete product spec (requirements, data models, state machines, test cases),
find problems that a developer or user would discover later.

Check for:
1. Missing requirements (what should be there but isn't?)
2. Edge cases not covered (concurrent operations, error recovery, permission boundaries)
3. State machine deadlocks (unreachable states, missing recovery transitions)
4. Data model gaps (missing fields, missing relationships, missing audit fields)
5. Test case coverage (are critical paths tested?)

Respond in this exact JSON format:
{
  "issues": [
    {
      "severity": "high",
      "category": "state_machine",
      "description": "Book state machine has no recovery from 'lost' state — what if the book is found?",
      "recommendation": "Add transition: lost → available, trigger: librarian marks as found"
    }
  ],
  "missing_test_cases": [
    "Concurrent borrow: two readers try to borrow the last available book simultaneously",
    "Permission boundary: reader tries to access librarian-only functions"
  ],
  "overall_assessment": "The spec covers core flows but misses concurrency and recovery scenarios."
}

Rules:
- Be specific. Cite the exact entity, state, or requirement.
- Severity: high (must fix), medium (should fix), low (nice to fix).
- Focus on what matters, not cosmetic issues.
- If the spec is solid, say so — don't invent problems."""


class ReviewAgent:
    """Adversarially reviews the complete spec for gaps."""

    def __init__(self, llm: LLMHelper):
        self.llm = llm

    def run(self, business_description: str, requirements: dict, data_models: dict, state_machines: dict, test_cases: dict) -> dict:
        """Review the complete spec and return issues."""
        logger.info("ReviewAgent: reviewing spec for gaps...")

        import json
        spec_summary = json.dumps({
            "requirements": requirements.get("requirements", [])[:10],
            "user_roles": [r["name"] for r in requirements.get("user_roles", [])],
            "entities": [m["name"] for m in data_models.get("models", [])],
            "state_machines": [
                {"entity": sm["entity"], "states": sm["states"], "transitions": len(sm["transitions"])}
                for sm in state_machines.get("state_machines", [])
            ],
            "test_cases": test_cases.get("test_cases", [])[:5],
        }, ensure_ascii=False, indent=2)

        result = self.llm.chat_json(
            SYSTEM_PROMPT,
            f"Business description:\n{business_description}\n\nSpec summary:\n{spec_summary}\n\nReview this spec for gaps and issues.",
        )

        if not result:
            logger.warning("ReviewAgent: LLM returned no valid JSON")
            return {"issues": [], "missing_test_cases": [], "overall_assessment": "Review failed."}

        issue_count = len(result.get("issues", []))
        missing_count = len(result.get("missing_test_cases", []))
        logger.info(f"ReviewAgent: found {issue_count} issues, {missing_count} missing test cases")

        return result