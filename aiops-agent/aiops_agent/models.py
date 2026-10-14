"""Data models for metrics, anomalies, and inspection results."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    P0 = "P0"  # Critical
    P1 = "P1"  # Severe
    P2 = "P2"  # Warning
    P3 = "P3"  # Info
    OK = "OK"  # Normal


class AnomalyType(str, Enum):
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    HIGH_DISK = "high_disk"
    POD_RESTART = "pod_restart"
    POD_NOT_READY = "pod_not_ready"
    HIGH_HTTP_5XX = "high_http_5xx"
    REDIS_HIGH_MEM = "redis_high_mem"
    MYSQL_SLAVE_LAG = "mysql_slave_lag"
    SERVICE_DOWN = "service_down"


@dataclass
class NodeMetric:
    """Metrics for a single K8s node."""
    node_name: str
    cpu_usage_pct: float
    memory_usage_pct: float
    disk_usage_pct: float
    pod_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PodMetric:
    """Metrics for a single Pod."""
    pod_name: str
    namespace: str
    node_name: str
    phase: str  # Running, Pending, Failed, etc.
    ready: bool
    restart_count: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Anomaly:
    """A detected anomaly."""
    anomaly_type: AnomalyType
    severity: Severity
    target: str  # node name, pod name, service name
    description: str
    value: str  # The anomalous value
    threshold: str  # The threshold that was exceeded
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """A retrieval result from WeKnora knowledge base."""
    query: str
    content: str
    source: str  # Document filename
    score: float
    knowledge_id: str = ""


@dataclass
class AgentDecision:
    """A decision made by the reasoning agent."""
    anomaly: Anomaly
    retrieved_playbooks: list  # list of RetrievalResult
    root_cause_hypothesis: str
    recommended_actions: list  # list of action strings
    escalation_required: bool
    escalation_reason: str
    confidence: float  # 0.0 to 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_llm_response: str = ""


@dataclass
class InspectionReport:
    """A complete inspection report."""
    start_time: str
    end_time: str
    total_nodes: int
    total_pods: int
    anomalies_found: int
    decisions: list  # list of AgentDecision
    summary: str = ""
    severity: Severity = Severity.OK
    report_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))