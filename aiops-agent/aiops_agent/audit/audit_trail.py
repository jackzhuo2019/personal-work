"""Audit trail — records every agent decision for reviewability."""
import json
import logging
from datetime import datetime
from pathlib import Path
from ..models import AgentDecision

logger = logging.getLogger(__name__)


class AuditTrail:
    """Records agent decisions in an append-only audit log."""

    def __init__(self, output_dir: str = "./reports/audit"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.output_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"

    def record(self, decision: AgentDecision) -> None:
        """Record a single agent decision."""
        entry = {
            "timestamp": decision.timestamp,
            "anomaly": {
                "type": decision.anomaly.anomaly_type.value,
                "severity": decision.anomaly.severity.value,
                "target": decision.anomaly.target,
                "description": decision.anomaly.description,
                "value": decision.anomaly.value,
                "threshold": decision.anomaly.threshold,
            },
            "playbooks_retrieved": len(decision.retrieved_playbooks),
            "playbook_sources": [p.source for p in decision.retrieved_playbooks],
            "root_cause_hypothesis": decision.root_cause_hypothesis,
            "recommended_actions": decision.recommended_actions,
            "escalation_required": decision.escalation_required,
            "escalation_reason": decision.escalation_reason,
            "confidence": decision.confidence,
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        logger.info(
            f"Audit recorded: {decision.anomaly.anomaly_type.value} on {decision.anomaly.target} "
            f"(escalation={decision.escalation_required}, confidence={decision.confidence})"
        )

    def record_batch(self, decisions: list[AgentDecision]) -> None:
        """Record multiple decisions."""
        for d in decisions:
            self.record(d)