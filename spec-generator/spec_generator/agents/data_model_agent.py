"""Step 2: Data Model Agent — defines entities, fields, and validation rules."""
import logging
from ..config import DataModel, DataField
from .llm_helper import LLMHelper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a data architect designing the data model for a software product.
Given the requirements and business description, design the core data entities.

Respond in this exact JSON format:
{
  "models": [
    {
      "name": "Book",
      "description": "A book in the library catalog",
      "fields": [
        {"name": "id", "type": "string", "required": true, "validation": "uuid", "description": "Unique identifier"},
        {"name": "title", "type": "string", "required": true, "validation": "max_length=255", "description": "Book title"},
        {"name": "status", "type": "enum", "required": true, "validation": "enum:[available,borrowed,reserved,lost]", "description": "Current availability status"}
      ]
    }
  ]
}

Rules:
- Define 3-6 core entities (not every possible table).
- Every entity must have an "id" field.
- Use types: string, int, float, bool, datetime, enum, foreign_key, text.
- For foreign_key, set validation to "fk:<EntityName>".
- For enum, list all valid values in validation.
- Consider audit fields (created_at, updated_at) for main entities.
- Think about what fields are needed for the state machine (status fields)."""


class DataModelAgent:
    """Designs the data model based on requirements."""

    def __init__(self, llm: LLMHelper):
        self.llm = llm

    def run(self, business_description: str, requirements: dict) -> dict:
        """Generate data models from requirements."""
        logger.info("DataModelAgent: designing data model...")

        req_summary = f"Requirements: {requirements.get('requirements', [])}\nUser roles: {requirements.get('user_roles', [])}"

        result = self.llm.chat_json(
            SYSTEM_PROMPT,
            f"Business description:\n{business_description}\n\n{req_summary}\n\nDesign the core data entities.",
        )

        if not result:
            logger.warning("DataModelAgent: LLM returned no valid JSON")
            return {"models": []}

        logger.info(f"DataModelAgent: designed {len(result.get('models', []))} entities")
        return result