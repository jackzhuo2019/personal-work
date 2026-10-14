"""Configuration and data models."""
import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LLMConfig:
    base_url: str = ""
    api_key: str = ""
    model: str = ""


@dataclass
class Settings:
    llm: LLMConfig = field(default_factory=LLMConfig)
    output_dir: str = "./output"


def load_settings(config_path: Optional[str] = None) -> Settings:
    """Load settings from YAML or environment variables."""
    if config_path is None:
        candidates = [
            os.environ.get("SPEC_CONFIG"),
            "config/settings.yaml",
        ]
        for c in candidates:
            if c and os.path.isfile(c):
                config_path = c
                break

    data = {}
    if config_path and os.path.isfile(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    settings = Settings()

    if "llm" in data:
        settings.llm = LLMConfig(**data["llm"])
    if "output_dir" in data:
        settings.output_dir = data["output_dir"]

    # Environment variable overrides
    if os.environ.get("LLM_BASE_URL"):
        settings.llm.base_url = os.environ["LLM_BASE_URL"]
    if os.environ.get("LLM_API_KEY"):
        settings.llm.api_key = os.environ["LLM_API_KEY"]
    if os.environ.get("LLM_MODEL"):
        settings.llm.model = os.environ["LLM_MODEL"]

    return settings


# ── Data Models ──────────────────────────────

@dataclass
class Requirement:
    """A single requirement item."""
    category: str  # functional, non-functional, constraint
    description: str
    priority: str = "must"  # must, should, could


@dataclass
class UserRole:
    """A user role."""
    name: str
    description: str
    permissions: list = field(default_factory=list)


@dataclass
class DataField:
    """A field in the data model."""
    name: str
    type: str  # string, int, float, bool, datetime, enum, foreign_key
    required: bool = True
    validation: str = ""  # e.g. "max_length=255", "regex=...", "enum:[a,b,c]"
    description: str = ""


@dataclass
class DataModel:
    """A data model / entity."""
    name: str
    fields: list = field(default_factory=list)  # list of DataField
    description: str = ""


@dataclass
class StateTransition:
    """A state transition in the state machine."""
    from_state: str
    to_state: str
    trigger: str  # what causes this transition
    guard: str = ""  # condition that must be true


@dataclass
class StateMachine:
    """A state machine for an entity."""
    entity: str
    initial_state: str
    states: list = field(default_factory=list)  # list of state names
    transitions: list = field(default_factory=list)  # list of StateTransition


@dataclass
class TestCase:
    """A test case."""
    id: str
    title: str
    steps: list = field(default_factory=list)  # list of step strings
    expected_result: str = ""
    category: str = "functional"  # functional, edge, permission


@dataclass
class SpecResult:
    """Complete output of the spec generation pipeline."""
    business_description: str
    requirements: list = field(default_factory=list)  # list of Requirement
    user_roles: list = field(default_factory=list)  # list of UserRole
    data_models: list = field(default_factory=list)  # list of DataModel
    state_machines: list = field(default_factory=list)  # list of StateMachine
    test_cases: list = field(default_factory=list)  # list of TestCase
    review_notes: str = ""
    prd_markdown: str = ""
    prototype_html: str = ""
    state_machine_svg: str = ""
    output_files: dict = field(default_factory=dict)