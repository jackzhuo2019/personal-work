"""Report generator — produces Markdown and JSON inspection reports."""
import json
import logging
from datetime import datetime
from pathlib import Path
from ..models import InspectionReport, Severity, AgentDecision

logger = logging.getLogger(__name__)

SEVERITY_EMOJI = {
    Severity.P0: "🔴",
    Severity.P1: "🟠",
    Severity.P2: "🟡",
    Severity.P3: "🔵",
    Severity.OK: "✅",
}


class ReportGenerator:
    """Generates inspection reports in Markdown and JSON formats."""

    def __init__(self, output_dir: str = "./reports/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, report: InspectionReport, fmt: str = "both") -> dict[str, str]:
        """Generate report in specified format.

        Returns:
            Dict with keys 'markdown' and/or 'json' mapping to file paths.
        """
        paths: dict[str, str] = {}

        if fmt in ("markdown", "both"):
            md_path = self._generate_markdown(report)
            paths["markdown"] = str(md_path)

        if fmt in ("json", "both"):
            json_path = self._generate_json(report)
            paths["json"] = str(json_path)

        logger.info(f"Report generated: {paths}")
        return paths

    def _generate_markdown(self, report: InspectionReport) -> Path:
        """Generate Markdown report."""
        filepath = self.output_dir / f"inspection_{report.report_id}.md"
        emoji = SEVERITY_EMOJI.get(report.severity, "✅")

        lines = [
            f"# AIOps Inspection Report — {report.report_id}",
            "",
            f"**Status**: {emoji} {report.severity.value}",
            f"**Time**: {report.start_time} → {report.end_time}",
            f"**Scope**: {report.total_nodes} nodes, {report.total_pods} pods",
            f"**Anomalies Found**: {report.anomalies_found}",
            "",
            "## Summary",
            "",
            report.summary or "No anomalies detected. All systems nominal.",
            "",
        ]

        if report.decisions:
            lines.append("## Anomaly Analysis")
            lines.append("")

            for i, decision in enumerate(report.decisions, 1):
                anomaly = decision.anomaly
                a_emoji = SEVERITY_EMOJI.get(anomaly.severity, "⚠️")
                lines.extend([
                    f"### {i}. {a_emoji} {anomaly.anomaly_type.value} — {anomaly.target}",
                    "",
                    f"- **Severity**: {anomaly.severity.value}",
                    f"- **Description**: {anomaly.description}",
                    f"- **Value**: {anomaly.value} (threshold: {anomaly.threshold})",
                    f"- **Root Cause Hypothesis**: {decision.root_cause_hypothesis}",
                    f"- **Confidence**: {decision.confidence:.0%}",
                    f"- **Escalation**: {'⚠️ YES — ' + decision.escalation_reason if decision.escalation_required else 'No'}",
                    "",
                ])

                # Investigation evidence
                if decision.evidence:
                    lines.append("**Investigation Evidence**:")
                    lines.append("")
                    for ev in decision.evidence:
                        status = "✅" if ev.get("exit_code") == 0 else "❌"
                        cmd = ev.get("command", "")
                        output = ev.get("output", "")[:200]
                        level = ev.get("level", "L0")
                        lines.append(f"- {status} `[{level}]` `{cmd}`")
                        if output:
                            lines.append("  ```")
                            lines.append(output)
                            lines.append("  ```")
                    lines.append("")

                # Proposed operations (require approval)
                if decision.proposed_operations:
                    lines.append("**⚠️ Proposed Operations (require human approval)**:")
                    lines.append("")
                    for op in decision.proposed_operations:
                        cmd = op.get("command", "")
                        reason = op.get("reason", "")
                        risk = op.get("risk", "L2")
                        lines.append(f"- `[{risk}]` `{cmd}` — {reason}")
                    lines.append("")

                # Recommended actions
                if decision.recommended_actions:
                    lines.append("**Recommended Actions**:")
                    lines.append("")
                    for j, action in enumerate(decision.recommended_actions, 1):
                        lines.append(f"{j}. {action}")
                    lines.append("")

                # Retrieved playbooks
                if decision.retrieved_playbooks:
                    lines.append("**Retrieved Playbooks**:")
                    lines.append("")
                    for p in decision.retrieved_playbooks:
                        lines.append(f"- `{p.source}` (score: {p.score:.4f})")
                    lines.append("")

                lines.append("---")
                lines.append("")

        else:
            lines.extend([
                "## Anomaly Analysis",
                "",
                "No anomalies detected. All systems nominal.",
                "",
            ])

        # Footer
        lines.extend([
            "## Audit Trail",
            "",
            f"Full audit log available in `reports/audit/audit_{datetime.now().strftime('%Y%m%d')}.jsonl`",
            "",
            "---",
            f"*Generated by AIOps Intelligent Operations Assistant at {report.end_time}*",
        ])

        filepath.write_text("\n".join(lines), encoding="utf-8")
        return filepath

    def _generate_json(self, report: InspectionReport) -> Path:
        """Generate JSON report."""
        filepath = self.output_dir / f"inspection_{report.report_id}.json"

        data = {
            "report_id": report.report_id,
            "start_time": report.start_time,
            "end_time": report.end_time,
            "severity": report.severity.value,
            "total_nodes": report.total_nodes,
            "total_pods": report.total_pods,
            "anomalies_found": report.anomalies_found,
            "summary": report.summary,
            "decisions": [
                {
                    "anomaly": {
                        "type": d.anomaly.anomaly_type.value,
                        "severity": d.anomaly.severity.value,
                        "target": d.anomaly.target,
                        "description": d.anomaly.description,
                        "value": d.anomaly.value,
                        "threshold": d.anomaly.threshold,
                    },
                    "root_cause_hypothesis": d.root_cause_hypothesis,
                    "recommended_actions": d.recommended_actions,
                    "escalation_required": d.escalation_required,
                    "escalation_reason": d.escalation_reason,
                    "confidence": d.confidence,
                    "playbook_sources": [p.source for p in d.retrieved_playbooks],
                    "timestamp": d.timestamp,
                }
                for d in report.decisions
            ],
        }

        filepath.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return filepath