"""Prometheus metrics collector."""
import logging
import requests
from typing import Optional
from ..config_loader import Settings
from ..models import NodeMetric, PodMetric

logger = logging.getLogger(__name__)


class PrometheusCollector:
    """Collects metrics from Prometheus API."""

    def __init__(self, settings: Settings):
        self.url = settings.prometheus.url
        self.timeout = 10

    def _query(self, promql: str) -> Optional[list]:
        """Execute a PromQL instant query."""
        try:
            resp = requests.get(
                f"{self.url}/api/v1/query",
                params={"query": promql},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "success":
                return data["data"]["result"]
            return None
        except Exception as e:
            logger.error(f"Prometheus query failed [{promql}]: {e}")
            return None

    def collect_node_metrics(self) -> list[NodeMetric]:
        """Collect per-node resource usage metrics."""
        metrics: list[NodeMetric] = []

        # CPU usage per node: 1 - avg(rate(idle)) * 100
        cpu_results = self._query(
            '100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])))'
        )
        mem_results = self._query(
            '100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))'
        )
        disk_results = self._query(
            '100 * (1 - (node_filesystem_avail_bytes{mountpoint="/",fstype!~"tmpfs|overlay"} '
            '/ node_filesystem_size_bytes{mountpoint="/",fstype!~"tmpfs|overlay"}))'
        )
        pod_count_results = self._query(
            'count by (node) (kube_pod_info)'
        )

        # Build CPU map
        cpu_map: dict[str, float] = {}
        if cpu_results:
            for r in cpu_results:
                instance = r["metric"].get("instance", "unknown")
                cpu_map[instance] = float(r["value"][1])

        # Build memory map
        mem_map: dict[str, float] = {}
        if mem_results:
            for r in mem_results:
                instance = r["metric"].get("instance", "unknown")
                mem_map[instance] = float(r["value"][1])

        # Build disk map
        disk_map: dict[str, float] = {}
        if disk_results:
            for r in disk_results:
                instance = r["metric"].get("instance", "unknown")
                disk_map[instance] = float(r["value"][1])

        # Build pod count map
        pod_map: dict[str, int] = {}
        if pod_count_results:
            for r in pod_count_results:
                node = r["metric"].get("node", r["metric"].get("instance", "unknown"))
                pod_map[node] = int(float(r["value"][1]))

        # Merge all instances
        all_instances = set(cpu_map) | set(mem_map) | set(disk_map)
        for instance in all_instances:
            # Extract node name from instance (strip port)
            node_name = instance.split(":")[0] if ":" in instance else instance
            metrics.append(NodeMetric(
                node_name=node_name,
                cpu_usage_pct=round(cpu_map.get(instance, 0), 2),
                memory_usage_pct=round(mem_map.get(instance, 0), 2),
                disk_usage_pct=round(disk_map.get(instance, 0), 2),
                pod_count=pod_map.get(node_name, pod_map.get(instance, 0)),
            ))

        logger.info(f"Collected metrics for {len(metrics)} nodes")
        return metrics

    def collect_pod_metrics(self) -> list[PodMetric]:
        """Collect per-pod status metrics."""
        pods: list[PodMetric] = []

        # Pod phase and ready status
        phase_results = self._query('kube_pod_status_phase')
        ready_results = self._query('kube_pod_status_ready')
        restart_results = self._query(
            'kube_pod_container_status_restarts_total'
        )
        info_results = self._query('kube_pod_info')

        # Build info map: pod_uid -> {namespace, node}
        info_map: dict[str, dict] = {}
        if info_results:
            for r in info_results:
                pod = r["metric"].get("pod", "")
                ns = r["metric"].get("namespace", "")
                node = r["metric"].get("node", "")
                info_map[pod] = {"namespace": ns, "node": node}

        # Build phase map
        phase_map: dict[str, str] = {}
        if phase_results:
            for r in phase_results:
                pod = r["metric"].get("pod", "")
                phase = r["metric"].get("phase", "")
                if r["value"][1] == "1":
                    phase_map[pod] = phase

        # Build ready map
        ready_map: dict[str, bool] = {}
        if ready_results:
            for r in ready_results:
                pod = r["metric"].get("pod", "")
                ready = r["metric"].get("condition", "")
                if r["value"][1] == "1" and ready == "true":
                    ready_map[pod] = True

        # Build restart count map
        restart_map: dict[str, int] = {}
        if restart_results:
            for r in restart_results:
                pod = r["metric"].get("pod", "")
                container = r["metric"].get("container", "")
                key = f"{pod}/{container}"
                restart_map[key] = int(float(r["value"][1]))

        # Build pod metrics
        for pod, phase in phase_map.items():
            info = info_map.get(pod, {})
            restarts = max(
                (v for k, v in restart_map.items() if k.startswith(pod)),
                default=0,
            )
            pods.append(PodMetric(
                pod_name=pod,
                namespace=info.get("namespace", "unknown"),
                node_name=info.get("node", "unknown"),
                phase=phase,
                ready=ready_map.get(pod, False),
                restart_count=restarts,
            ))

        logger.info(f"Collected metrics for {len(pods)} pods")
        return pods

    def query_custom(self, promql: str) -> Optional[list]:
        """Run a custom PromQL query."""
        return self._query(promql)