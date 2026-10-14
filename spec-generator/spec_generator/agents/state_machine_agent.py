"""Step 3: State Machine Agent — generates state machines for entities with lifecycles."""
import logging
from .llm_helper import LLMHelper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a system architect designing state machines for entities with lifecycles.
Given the data models and business description, identify which entities have state-based lifecycles
and design their state machines.

Respond in this exact JSON format:
{
  "state_machines": [
    {
      "entity": "Book",
      "initial_state": "available",
      "states": ["available", "borrowed", "reserved", "overdue", "lost"],
      "transitions": [
        {"from_state": "available", "to_state": "borrowed", "trigger": "reader borrows book", "guard": "reader has no overdue books"},
        {"from_state": "borrowed", "to_state": "overdue", "trigger": "due date passes", "guard": "not returned"},
        {"from_state": "borrowed", "to_state": "available", "trigger": "reader returns book", "guard": ""},
        {"from_state": "available", "to_state": "reserved", "trigger": "reader reserves book", "guard": "book is available"},
        {"from_state": "borrowed", "to_state": "lost", "trigger": "librarian marks as lost", "guard": "borrowed > 90 days"}
      ]
    }
  ]
}

Rules:
- Only create state machines for entities that have meaningful lifecycles (not for static lookup tables).
- Every state must be reachable from the initial state.
- No dead states (every state must have at least one outgoing transition, except terminal states).
- Include guard conditions where business rules apply.
- Consider error/recovery transitions (e.g., lost → available when found).
- Aim for 1-3 state machines (not every entity needs one)."""


class StateMachineAgent:
    """Generates state machines for entities with lifecycles."""

    def __init__(self, llm: LLMHelper):
        self.llm = llm

    def run(self, business_description: str, data_models: dict) -> dict:
        """Generate state machines from data models."""
        logger.info("StateMachineAgent: generating state machines...")

        models_summary = f"Data models: {[m['name'] for m in data_models.get('models', [])]}"

        result = self.llm.chat_json(
            SYSTEM_PROMPT,
            f"Business description:\n{business_description}\n\n{models_summary}\n\nDesign state machines for entities with lifecycles.",
        )

        if not result:
            logger.warning("StateMachineAgent: LLM returned no valid JSON")
            return {"state_machines": []}

        logger.info(f"StateMachineAgent: generated {len(result.get('state_machines', []))} state machines")
        return result