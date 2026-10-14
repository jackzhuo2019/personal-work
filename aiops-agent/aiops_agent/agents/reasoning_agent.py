"""Reasoning agent — investigates anomalies by executing diagnostic commands,
retrieving playbooks, and using LLM to synthesize root-cause analysis."""
import json
import logging
from openai import OpenAI
from typing import Optional
from ..config_loader import Settings
from ..models import Anomaly, RetrievalResult, AgentDecision, Severity
from ..retrievers.weknora_retriever import WeKnoraRetriever
from .command_executor import CommandExecutor, CommandResult

logger = logging.getLogger(__name__)

INVESTIGATION_PROMPT = """You are an AIOps reasoning agent with 18 years of production operations experience.

You are investigating an infrastructure anomaly. You have:
1. The anomaly description and metrics
2. Diagnostic evidence collected by executing read-only commands on the cluster
3. Retrieved playbooks from the knowledge base (may be empty if no relevant docs)

Your job:
1. Analyze ALL evidence — the actual command outputs are ground truth, not guesses
2. Form a root-cause hypothesis based on what the evidence shows
3. Recommend specific, actionable steps (reference commands from evidence/playbooks)
4. If a light operation (L2) like deleting a failed pod would help, propose it — do NOT execute it
5. Determine if escalation is required
6. Rate your confidence (0.0 to 1.0) based on how much evidence supports your hypothesis

Respond in this exact JSON format:
{
  "root_cause_hypothesis": "Your hypothesis, citing specific evidence",
  "recommended_actions": ["step 1 with specific command", "step 2", ...],
  "proposed_operations": [{"command": "kubectl delete pod xxx -n ns", "reason": "Pod is in CrashLoopBackOff, needs recreation", "risk": "L2"}],
  "escalation_required": true/false,
  "escalation_reason": "Why (empty if not required)",
  "confidence": 0.85
}

Rules:
- Base your hypothesis on ACTUAL EVIDENCE, not guesses. If logs show Exit Code 137, say "OOMKilled confirmed by logs".
- If evidence is insufficient, say so and recommend what to check next.
- Escalate P0 anomalies immediately.
- Proposed operations must be L2 only (delete pod, prune images). Never propose L3+ (scale, cordon, drain).
- Keep recommended_actions specific — include actual kubectl commands when relevant.
- Confidence should reflect evidence quality: 0.9+ with clear log evidence, 0.3-0.5 with only metrics, 0.1 with no evidence."""


class ReasoningAgent:
    """LLM-powered reasoning agent that investigates anomalies by executing
    diagnostic commands and synthesizing evidence with LLM."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            base_url=settings.llm.base_url,
            api_key=settings.llm.api_key,
        )
        self.model = settings.llm.model
        self.retriever = WeKnoraRetriever(settings)
        self.executor = CommandExecutor(timeout=15)

    def analyze(self, anomaly: Anomaly) -> AgentDecision:
        """Investigate a single anomaly through the full pipeline.

        Pipeline:
        1. Build investigation plan (default L0 commands based on anomaly type)
        2. Execute L0 commands to collect evidence
        3. Optionally retrieve playbooks from WeKnora
        4. Feed evidence + playbooks to LLM for root-cause analysis
        5. Parse LLM response into structured decision
        """
        logger.info(f"Agent investigating: {anomaly.anomaly_type.value} on {anomaly.target}")

        # Step 1: Build investigation plan
        commands = self.executor.build_investigation_plan(
            anomaly.anomaly_type.value,
            anomaly.target,
            anomaly.metadata,
        )
        logger.info(f"Investigation plan: {len(commands)} L0 commands")

        # Step 2: Execute L0 commands
        results: list[CommandResult] = []
        for cmd in commands:
            result = self.executor.execute(cmd)
            results.append(result)
            status = "OK" if result.success else f"FAIL({result.error or result.stderr[:50]})"
            logger.info(f"  [{result.level.value}] {cmd[:70]} → {status}")

        # Step 3: Retrieve playbooks from WeKnora (optional — may be empty)
        playbooks: list[RetrievalResult] = []
        try:
            playbooks = self.retriever.search_for_anomaly(
                anomaly.description,
                anomaly.anomaly_type.value,
            )
            logger.info(f"Retrieved {len(playbooks)} playbooks from WeKnora")
        except Exception as e:
            logger.warning(f"WeKnora retrieval skipped: {e}")

        # Step 4: Build LLM prompt with evidence
        evidence_text = self._format_evidence(results)
        playbook_text = self._format_playbooks(playbooks)

        user_prompt = f"""## Anomaly Detected
- Type: {anomaly.anomaly_type.value}
- Severity: {anomaly.severity.value}
- Target: {anomaly.target}
- Description: {anomaly.description}
- Current Value: {anomaly.value}
- Threshold: {anomaly.threshold}
- Metadata: {json.dumps(anomaly.metadata, ensure_ascii=False)}

## Diagnostic Evidence (from executed commands)
{evidence_text}

## Retrieved Playbooks from Knowledge Base
{playbook_text}

## Task
Analyze this anomaly based on the evidence above. Provide root-cause hypothesis, recommended actions, and any proposed L2 operations."""

        # Step 5: Call LLM
        raw_response = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": INVESTIGATION_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=3000,
            )
            raw_response = response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raw_response = ""

        # Step 6: Parse response
        decision = self._parse_response(anomaly, playbooks, results, raw_response)

        logger.info(
            f"Agent decision: escalation={decision.escalation_required}, "
            f"confidence={decision.confidence}, actions={len(decision.recommended_actions)}, "
            f"proposed_ops={len(decision.proposed_operations)}"
        )
        return decision

    def _format_evidence(self, results: list[CommandResult]) -> str:
        """Format command results as evidence text for LLM."""
        if not results:
            return "No diagnostic commands were executed."

        parts: list[str] = []
        for r in results:
            status = "✅" if r.success else "❌"
            output = r.summary(max_chars=1500)

            if r.error:
                parts.append(f"### {status} `{r.command}` [{r.level.value}]\n**Error**: {r.error}\n")
            else:
                parts.append(f"### {status} `{r.command}` [{r.level.value}]\n```\n{output}\n```")
            parts.append("")

        return "\n".join(parts)

    def _format_playbooks(self, playbooks: list[RetrievalResult]) -> str:
        """Format playbook results for LLM context."""
        if not playbooks:
            return "No relevant playbooks found in knowledge base."

        parts: list[str] = []
        for p in playbooks[:5]:  # Limit to top 5
            parts.append(f"--- {p.source} (score: {p.score:.4f}) ---\n{p.content[:1500]}\n")
        return "\n".join(parts)

    def _parse_response(
        self,
        anomaly: Anomaly,
        playbooks: list[RetrievalResult],
        evidence_results: list[CommandResult],
        raw_response: str,
    ) -> AgentDecision:
        """Parse LLM JSON response into AgentDecision."""

        # Collect evidence summaries
        evidence_summaries = [
            {
                "command": r.command,
                "level": r.level.value,
                "exit_code": r.exit_code,
                "output": r.summary(max_chars=300),
                "error": r.error,
            }
            for r in evidence_results
        ]

        # Default decision
        escalation = anomaly.severity == Severity.P0
        decision = AgentDecision(
            anomaly=anomaly,
            retrieved_playbooks=playbooks,
            investigation_commands=[r.command for r in evidence_results],
            evidence=evidence_summaries,
            proposed_operations=[],
            root_cause_hypothesis="",
            recommended_actions=[],
            escalation_required=escalation,
            escalation_reason="P0 anomaly - auto-escalate" if escalation else "",
            confidence=0.0,
            raw_llm_response=raw_response,
        )

        # Parse JSON
        try:
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

            # Parse proposed operations
            proposed = parsed.get("proposed_operations", [])
            if isinstance(proposed, list):
                decision.proposed_operations = [
                    op if isinstance(op, dict) else {"command": str(op), "reason": "", "risk": "L2"}
                    for op in proposed
                ]

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
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