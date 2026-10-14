"""Configuration loader."""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PrometheusConfig:
    url: str = "http://172.17.23.94:30090"


@dataclass
class WeKnoraConfig:
    url: str = ""
    api_key: str = ""
    knowledge_base_id: str = ""
    search_top_k: int = 3


@dataclass
class LLMConfig:
    base_url: str = ""
    api_key: str = ""
    model: str = ""


@dataclass
class Thresholds:
    node_cpu_usage_pct: float = 80
    node_mem_usage_pct: float = 85
    node_disk_usage_pct: float = 85
    pod_restart_count: int = 5
    pod_not_ready: bool = True
    http_5xx_rate_pct: float = 1
    redis_mem_usage_pct: float = 90
    mysql_slave_lag_sec: int = 10


@dataclass
class ScheduleConfig:
    interval_seconds: int = 300
    full_inspection_interval: int = 3600


@dataclass
class EscalationConfig:
    p0_immediate: bool = True
    p1_after_minutes: int = 10
    notify_channels: list = field(default_factory=lambda: ["console"])


@dataclass
class ReportConfig:
    output_dir: str = "./reports/output"
    format: str = "markdown"


@dataclass
class Settings:
    prometheus: PrometheusConfig = field(default_factory=PrometheusConfig)
    weknora: WeKnoraConfig = field(default_factory=WeKnoraConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    thresholds: Thresholds = field(default_factory=Thresholds)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    escalation: EscalationConfig = field(default_factory=EscalationConfig)
    report: ReportConfig = field(default_factory=ReportConfig)


def load_settings(config_path: Optional[str] = None) -> Settings:
    """Load settings from YAML file."""
    if config_path is None:
        # Search for settings.yaml in standard locations
        candidates = [
            os.environ.get("AIOPS_CONFIG"),
            "config/settings.yaml",
            os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml"),
        ]
        for c in candidates:
            if c and os.path.isfile(c):
                config_path = c
                break

    if config_path and os.path.isfile(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    settings = Settings()

    if "prometheus" in data:
        settings.prometheus = PrometheusConfig(**data["prometheus"])
    if "weknora" in data:
        settings.weknora = WeKnoraConfig(**data["weknora"])
    if "llm" in data:
        settings.llm = LLMConfig(**data["llm"])
    if "thresholds" in data:
        settings.thresholds = Thresholds(**data["thresholds"])
    if "schedule" in data:
        settings.schedule = ScheduleConfig(**data["schedule"])
    if "escalation" in data:
        settings.escalation = EscalationConfig(**data["escalation"])
    if "report" in data:
        settings.report = ReportConfig(**data["report"])

    return settings