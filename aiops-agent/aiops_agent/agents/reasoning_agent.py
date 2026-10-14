"""Reasoning agent — uses LLM to analyze anomalies and recommend actions."""
import json
import logging
from openai import OpenAI
from typing import Optional
from ..config_loader import Settings
from ..models import Anomaly, RetrievalResult, AgentDecision, Severity
from ..retrievers.weknora_retriever import WeKnoraRetriever

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AIOps reasoning agent with 18 years of production operations experience.
Your job is to analyze infrastructure anomalies and provide root-cause hypotheses and recommended actions.

For each anomaly:
1. Analyze the anomaly description and metrics
2. Review the retrieved playbooks from the knowledge base
3. Form a root-cause hypothesis
4. Recommend specific, actionable steps
5. Determine if escalation is required
6. Rate your confidence (0.0 to 1.0)

Respond in this exact JSON format:
{
  "root_cause_hypothesis": "Your hypothesis about what caused this anomaly",
  "recommended_actions": ["step 1", "step 2", "step 3"],
  "escalation_required": true/false,
  "escalation_reason": "Why escalation is or isn't needed (empty if not required)",
  "confidence": 0.85
}

Rules:
- Be specific. Reference commands from the playbooks when relevant.
- Escalate P0 anomalies immediately (escalation_required: true).
- Escalate P1 anomalies if the playbook steps cannot resolve it.
- Do not invent information not present in the playbooks.
- Keep responses concise and actionable."""


class ReasoningAgent:
    """LLM-powered reasoning agent for root-cause analysis."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            base_url=settings.llm.base_url,
            api_key=settings.llm.api_key,
        )
        self.model = settings.llm.model
        self.retriever = WeKnoraRetriever(settings)

    def analyze(self, anomaly: Anomaly) -> AgentDecision:
        """Analyze a single anomaly and produce a decision.

        Args:
            anomaly: The detected anomaly to analyze.

        Returns:
            AgentDecision with root-cause hypothesis, recommended actions, and escalation info.
        """
        # Step 1: Retrieve relevant playbooks from WeKnora
        playbooks = self.retriever.search_for_anomaly(
            anomaly.description,
            anomaly.anomaly_type.value,
        )

        logger.info(f"Agent analyzing anomaly: {anomaly.anomaly_type.value} on {anomaly.target}")
        logger.info(f"Retrieved {len(playbooks)} playbooks from WeKnora")

        # Step 2: Build the prompt
        playbook_context = "\n\n".join(
            f"--- Playbook: {p.source} (score: {p.score:.4f}) ---\n{p.content[:2000]}"
            for p in playbooks
        ) or "No relevant playbooks found in knowledge base."

        user_prompt = f"""## Anomaly Detected
- Type: {anomaly.anomaly_type.value}
- Severity: {anomaly.severity.value}
- Target: {anomaly.target}
- Description: {anomaly.description}
- Current Value: {anomaly.value}
- Threshold: {anomaly.threshold}
- Metadata: {json.dumps(anomaly.metadata, ensure_ascii=False)}

## Retrieved Playbooks from Knowledge Base
{playbook_context}

## Task
Analyze this anomaly. Provide a root-cause hypothesis, recommended actions, and determine if escalation is required."""

        # Step 3: Call LLM
        raw_response = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            raw_response = response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raw_response = ""

        # Step 4: Parse response
        decision = self._parse_response(anomaly, playbooks, raw_response)

        logger.info(
            f"Agent decision: escalation={decision.escalation_required}, "
            f"confidence={decision.confidence}, actions={len(decision.recommended_actions)}"
        )
        return decision

    def _parse_response(
        self,
        anomaly: Anomaly,
        playbooks: list[RetrievalResult],
        raw_response: str,
    ) -> AgentDecision:
        """Parse LLM JSON response into AgentDecision."""
        # Default decision
        escalation = anomaly.severity == Severity.P0
        decision = AgentDecision(
            anomaly=anomaly,
            retrieved_playbooks=playbooks,
            root_cause_hypothesis="",
            recommended_actions=[],
            escalation_required=escalation,
            escalation_reason="P0 anomaly - auto-escalate" if escalation else "",
            confidence=0.0,
            raw_llm_response=raw_response,
        )

        # Try to parse JSON from response
        try:
            # Find JSON in response (may be wrapped in ```json ... ```)
            json_str = raw_response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            parsed = json.loads(json_str)

            decision.root_cause_hypothesis = parsed.get("root_cause_hypothesis", "")
            decision.recommended_actions = parsed.get("recommended_actions", [])
            decision.escalation_required = parsed.get("escalation_required", escalation)
            decision.escalation_reason = parsed.get("escalation_reason", "")
            decision.confidence = float(parsed.get("confidence", 0.0))

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            # Use raw response as hypothesis if JSON parsing fails
            decision.root_cause_hypothesis = raw_response[:500] if raw_response else "LLM response unavailable"
            decision.confidence = 0.1

        return decision

    def analyze_batch(self, anomalies: list[Anomaly]) -> list[AgentDecision]:
        """Analyze multiple anomalies."""
        decisions: list[AgentDecision] = []
        for anomaly in anomalies:
            try:
                decision = self.analyze(anomaly)
                decisions.append(decision)
            except Exception as e:
                logger.error(f"Failed to analyze anomaly {anomaly.target}: {e}")
                decisions.append(AgentDecision(
                    anomaly=anomaly,
                    retrieved_playbooks=[],
                    root_cause_hypothesis=f"Analysis failed: {e}",
                    recommended_actions=[],
                    escalation_required=anomaly.severity == Severity.P0,
                    escalation_reason="Analysis failed - escalate for safety",
                    confidence=0.0,
                ))
        return decisions