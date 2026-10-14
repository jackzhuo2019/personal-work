"""LLM helper — shared OpenAI client and prompt utilities."""
import json
import logging
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)


class LLMHelper:
    """Wrapper around OpenAI-compatible LLM API."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 4000) -> str:
        """Send a chat completion request and return the response text."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return ""

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 4000) -> Optional[dict]:
        """Send a chat request and parse JSON from the response."""
        raw = self.chat(system_prompt, user_prompt, temperature, max_tokens)
        if not raw:
            return None

        # Extract JSON from response
        text = raw.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON: {e}")
            # Try to find the first { and last }
            first = text.find("{")
            last = text.rfind("}")
            if first >= 0 and last > first:
                try:
                    return json.loads(text[first:last+1])
                except json.JSONDecodeError:
                    pass
            return None