"""Step 1: Requirement Agent — extracts requirements, user roles, and use cases from a business description."""
import logging
from ..config import Requirement, UserRole
from .llm_helper import LLMHelper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a product analyst with 18 years of experience in B2B product design.
Given a business description, extract:
1. Functional requirements (what the system must do)
2. Non-functional requirements (performance, security, usability)
3. Constraints (technical, business, regulatory)
4. User roles (who uses the system, what they can do)
5. Key use cases (main user journeys)

Respond in this exact JSON format:
{
  "requirements": [
    {"category": "functional", "description": "...", "priority": "must"},
    {"category": "non-functional", "description": "...", "priority": "should"}
  ],
  "user_roles": [
    {"name": "Reader", "description": "...", "permissions": ["borrow books", "view history"]}
  ],
  "use_cases": [
    "Reader borrows a book",
    "Librarian adds a new book"
  ]
}

Rules:
- Be specific. "User can borrow books" not "borrowing functionality".
- Priorities: must (core), should (important), could (nice-to-have).
- Include 8-15 requirements, 3-5 user roles, 5-8 use cases.
- Consider edge cases like permissions, concurrency, and error states."""


class RequirementAgent:
    """Extracts requirements from a business description."""

    def __init__(self, llm: LLMHelper):
        self.llm = llm

    def run(self, business_description: str) -> dict:
        """Analyze the business description and return structured requirements."""
        logger.info("RequirementAgent: analyzing business description...")

        result = self.llm.chat_json(
            SYSTEM_PROMPT,
            f"Business description:\n{business_description}\n\nExtract requirements, user roles, and use cases.",
        )

        if not result:
            logger.warning("RequirementAgent: LLM returned no valid JSON")
            return {"requirements": [], "user_roles": [], "use_cases": []}

        logger.info(
            f"RequirementAgent: extracted "
            f"{len(result.get('requirements', []))} requirements, "
            f"{len(result.get('user_roles', []))} roles, "
            f"{len(result.get('use_cases', []))} use cases"
        )
        return result