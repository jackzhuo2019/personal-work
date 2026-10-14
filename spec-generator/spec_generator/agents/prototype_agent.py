"""Step 4: Prototype Agent — generates an interactive HTML prototype from the spec."""
import logging
from .llm_helper import LLMHelper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a frontend developer creating an interactive HTML prototype.
Given the requirements, data models, and state machines, generate a single self-contained HTML file
that demonstrates the core user flows.

The HTML must:
1. Be completely self-contained (inline CSS + JS, no external dependencies)
2. Use a clean, modern UI (cards, buttons, tables, forms)
3. Be interactive — buttons should trigger state changes visible on the page
4. Include mock data (pre-filled examples)
5. Show the main entity list view + detail view + create/edit form
6. Visualize the state machine (simple SVG or styled HTML diagram)
7. Use a dark or light theme with good contrast
8. Be responsive (works on mobile)

Output ONLY the HTML code. No markdown wrapping, no explanations, no ```html tags.
Start with <!DOCTYPE html> and end with </html>.

Keep it under 500 lines. Focus on demonstrating the core workflow, not pixel-perfect design."""


class PrototypeAgent:
    """Generates an interactive HTML prototype."""

    def __init__(self, llm: LLMHelper):
        self.llm = llm

    def run(self, business_description: str, requirements: dict, data_models: dict, state_machines: dict) -> str:
        """Generate an HTML prototype from the full spec."""
        logger.info("PrototypeAgent: generating HTML prototype...")

        # Build a compact summary for the LLM
        entities = [m["name"] for m in data_models.get("models", [])]
        states = {sm["entity"]: sm["states"] for sm in state_machines.get("state_machines", [])}
        use_cases = requirements.get("use_cases", [])
        roles = [r["name"] for r in requirements.get("user_roles", [])]

        summary = f"""Business: {business_description}
Entities: {entities}
User roles: {roles}
Use cases: {use_cases}
States: {states}"""

        # Use higher max_tokens for HTML generation
        html = self.llm.chat(
            SYSTEM_PROMPT,
            f"Generate an interactive HTML prototype for this product:\n\n{summary}",
            temperature=0.4,
            max_tokens=6000,
        )

        if not html:
            logger.warning("PrototypeAgent: LLM returned empty response")
            return "<html><body><p>Prototype generation failed.</p></body></html>"

        # Clean up any markdown wrapping that the LLM might add
        html = html.strip()
        if html.startswith("```html"):
            html = html[7:]
        if html.startswith("```"):
            html = html[3:]
        if html.endswith("```"):
            html = html[:-3]
        html = html.strip()

        if not html.startswith("<!DOCTYPE") and not html.startswith("<!doctype"):
            # Try to find the start of HTML
            idx = html.find("<!DOCTYPE")
            if idx < 0:
                idx = html.find("<!doctype")
            if idx < 0:
                idx = html.find("<html")
            if idx >= 0:
                html = html[idx:]

        logger.info(f"PrototypeAgent: generated {len(html)} chars of HTML")
        return html