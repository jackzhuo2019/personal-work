"""Anomaly detector — compares metrics against thresholds."""
import logging
from ..config_loader import Settings
from ..models import NodeMetric, PodMetric, Anomaly, AnomalyType, Severity

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies in collected metrics by comparing against thresholds."""

    def __init__(self, settings: Settings):
        self.thresholds = settings.thresholds

    def detect_node_anomalies(self, nodes: list[NodeMetric]) -> list[Anomaly]:
        """Check node metrics against thresholds."""
        anomalies: list[Anomaly] = []

        for node in nodes:
            # CPU
            if node.cpu_usage_pct > self.thresholds.node_cpu_usage_pct:
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.HIGH_CPU,
                    severity=Severity.P1,
                    target=node.node_name,
                    description=f"Node {node.node_name} CPU usage {node.cpu_usage_pct}% exceeds threshold {self.thresholds.node_cpu_usage_pct}%",
                    value=f"{node.cpu_usage_pct}%",
                    threshold=f"{self.thresholds.node_cpu_usage_pct}%",
                    metadata={"node": node.node_name, "pod_count": node.pod_count},
                ))

            # Memory
            if node.memory_usage_pct > self.thresholds.node_mem_usage_pct:
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.HIGH_MEMORY,
                    severity=Severity.P1,
                    target=node.node_name,
                    description=f"Node {node.node_name} memory usage {node.memory_usage_pct}% exceeds threshold {self.thresholds.node_mem_usage_pct}%",
                    value=f"{node.memory_usage_pct}%",
                    threshold=f"{self.thresholds.node_mem_usage_pct}%",
                    metadata={"node": node.node_name},
                ))

            # Disk
            if node.disk_usage_pct > self.thresholds.node_disk_usage_pct:
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.HIGH_DISK,
                    severity=Severity.P1,
                    target=node.node_name,
                    description=f"Node {node.node_name} disk usage {node.disk_usage_pct}% exceeds threshold {self.thresholds.node_disk_usage_pct}%",
                    value=f"{node.disk_usage_pct}%",
                    threshold=f"{self.thresholds.node_disk_usage_pct}%",
                    metadata={"node": node.node_name},
                ))

        logger.info(f"Detected {len(anomalies)} node anomalies from {len(nodes)} nodes")
        return anomalies

    def detect_pod_anomalies(self, pods: list[PodMetric]) -> list[Anomaly]:
        """Check pod metrics against thresholds."""
        anomalies: list[Anomaly] = []

        for pod in pods:
            # Pod not ready
            if self.thresholds.pod_not_ready and pod.phase == "Running" and not pod.ready:
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.POD_NOT_READY,
                    severity=Severity.P1,
                    target=f"{pod.namespace}/{pod.pod_name}",
                    description=f"Pod {pod.namespace}/{pod.pod_name} is Running but not Ready (node: {pod.node_name})",
                    value="NotReady",
                    threshold="Ready=True",
                    metadata={"pod": pod.pod_name, "namespace": pod.namespace, "node": pod.node_name},
                ))

            # Pod frequent restarts
            if pod.restart_count > self.thresholds.pod_restart_count:
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.POD_RESTART,
                    severity=Severity.P1,
                    target=f"{pod.namespace}/{pod.pod_name}",
                    description=f"Pod {pod.namespace}/{pod.pod_name} has {pod.restart_count} restarts (threshold: {self.thresholds.pod_restart_count})",
                    value=str(pod.restart_count),
                    threshold=str(self.thresholds.pod_restart_count),
                    metadata={"pod": pod.pod_name, "namespace": pod.namespace, "node": pod.node_name},
                ))

            # Pod in Failed/Pending state
            if pod.phase in ("Failed", "Pending"):
                sev = Severity.P0 if pod.phase == "Failed" else Severity.P2
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.POD_NOT_READY,
                    severity=sev,
                    target=f"{pod.namespace}/{pod.pod_name}",
                    description=f"Pod {pod.namespace}/{pod.pod_name} is in {pod.phase} state (node: {pod.node_name})",
                    value=pod.phase,
                    threshold="Running",
                    metadata={"pod": pod.pod_name, "namespace": pod.namespace, "node": pod.node_name},
                ))

        logger.info(f"Detected {len(anomalies)} pod anomalies from {len(pods)} pods")
        return anomalies

    def detect_all(self, nodes: list[NodeMetric], pods: list[PodMetric]) -> list[Anomaly]:
        """Run all detectors and return combined anomalies."""
        return self.detect_node_anomalies(nodes) + self.detect_pod_anomalies(pods)