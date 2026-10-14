"""Main orchestrator — coordinates collectors, detectors, retrievers, agents, and reports."""
import argparse
import logging
import sys
import time
from datetime import datetime

from .config_loader import load_settings
from .models import InspectionReport, Severity
from .collectors.prometheus_collector import PrometheusCollector
from .detectors.anomaly_detector import AnomalyDetector
from .agents.reasoning_agent import ReasoningAgent
from .reports.report_generator import ReportGenerator
from .audit.audit_trail import AuditTrail

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("aiops_agent")


def run_inspection(config_path: str | None = None) -> InspectionReport:
    """Run a single inspection cycle.

    Returns the InspectionReport.
    """
    start_time = datetime.now().isoformat()
    logger.info("=" * 60)
    logger.info("Starting AIOps inspection cycle")
    logger.info("=" * 60)

    # Load config
    settings = load_settings(config_path)
    logger.info(f"Config loaded: Prometheus={settings.prometheus.url}, WeKnora={settings.weknora.url}")

    # Step 1: Collect metrics
    logger.info("Step 1: Collecting metrics from Prometheus...")
    collector = PrometheusCollector(settings)
    node_metrics = collector.collect_node_metrics()
    pod_metrics = collector.collect_pod_metrics()
    logger.info(f"Collected: {len(node_metrics)} nodes, {len(pod_metrics)} pods")

    # Step 2: Detect anomalies
    logger.info("Step 2: Detecting anomalies...")
    detector = AnomalyDetector(settings)
    anomalies = detector.detect_all(node_metrics, pod_metrics)
    logger.info(f"Detected {len(anomalies)} anomalies")

    # Step 3: Agent reasoning (only if anomalies found)
    decisions = []
    if anomalies:
        logger.info("Step 3: Agent analyzing anomalies (LLM + WeKnora)...")
        agent = ReasoningAgent(settings)
        decisions = agent.analyze_batch(anomalies)
        logger.info(f"Agent produced {len(decisions)} decisions")
    else:
        logger.info("Step 3: No anomalies — skipping agent reasoning")

    # Step 4: Audit trail
    if decisions:
        logger.info("Step 4: Recording audit trail...")
        audit = AuditTrail(settings.report.output_dir + "/../audit")
        audit.record_batch(decisions)

    # Step 5: Determine overall severity
    overall_severity = Severity.OK
    if decisions:
        severity_order = {Severity.P0: 0, Severity.P1: 1, Severity.P2: 2, Severity.P3: 3, Severity.OK: 4}
        overall_severity = min(
            (d.anomaly.severity for d in decisions),
            key=lambda s: severity_order.get(s, 4),
        )

    # Step 6: Generate report
    end_time = datetime.now().isoformat()
    report = InspectionReport(
        start_time=start_time,
        end_time=end_time,
        total_nodes=len(node_metrics),
        total_pods=len(pod_metrics),
        anomalies_found=len(anomalies),
        decisions=decisions,
        summary=_build_summary(node_metrics, pod_metrics, anomalies, decisions),
        severity=overall_severity,
    )

    logger.info("Step 5: Generating report...")
    generator = ReportGenerator(settings.report.output_dir)
    paths = generator.generate(report, fmt=settings.report.format)

    logger.info("=" * 60)
    logger.info(f"Inspection complete: {len(anomalies)} anomalies, severity={overall_severity.value}")
    for fmt, path in paths.items():
        logger.info(f"  Report ({fmt}): {path}")
    logger.info("=" * 60)

    return report


def _build_summary(nodes, pods, anomalies, decisions) -> str:
    """Build a human-readable summary."""
    if not anomalies:
        return f"All systems nominal. {len(nodes)} nodes and {len(pods)} pods checked, no anomalies detected."

    escalation_count = sum(1 for d in decisions if d.escalation_required)
    parts = [
        f"Detected {len(anomalies)} anomalies across {len(nodes)} nodes and {len(pods)} pods.",
    ]

    # Group by severity
    by_severity: dict[str, int] = {}
    for a in anomalies:
        by_severity[a.severity.value] = by_severity.get(a.severity.value, 0) + 1
    parts.append("By severity: " + ", ".join(f"{k}={v}" for k, v in sorted(by_severity.items())))

    # Group by type
    by_type: dict[str, int] = {}
    for a in anomalies:
        by_type[a.anomaly_type.value] = by_type.get(a.anomaly_type.value, 0) + 1
    parts.append("By type: " + ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())))

    if escalation_count > 0:
        parts.append(f"⚠️ {escalation_count} anomaly(s) require escalation.")

    return " ".join(parts)


def run_scheduled(interval: int, config_path: str | None = None):
    """Run inspections on a schedule."""
    logger.info(f"Starting scheduled inspections (interval={interval}s)")
    while True:
        try:
            run_inspection(config_path)
        except Exception as e:
            logger.error(f"Inspection cycle failed: {e}", exc_info=True)
        logger.info(f"Next inspection in {interval} seconds...")
        time.sleep(interval)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AIOps Intelligent Operations Assistant")
    parser.add_argument("command", choices=["run", "schedule"], help="Run a single inspection or start scheduled loop")
    parser.add_argument("--config", default=None, help="Path to settings.yaml")
    parser.add_argument("--interval", type=int, default=300, help="Inspection interval in seconds (for 'schedule')")

    args = parser.parse_args()

    if args.command == "run":
        report = run_inspection(args.config)
        if report.severity != Severity.OK:
            sys.exit(1)
    elif args.command == "schedule":
        run_scheduled(args.interval, args.config)


if __name__ == "__main__":
    main()