# AIOps Intelligent Operations Assistant

LLM Agent system that automates the production operations inspection loop:
scheduled health checks → anomaly detection → root-cause reasoning → report generation.
Human escalation only when defined conditions are met.

## Architecture

```
Scheduler → Collectors (Prometheus + ELK) → Detectors (anomaly detection)
    ↓
Retrievers (WeKnora knowledge base) → Reasoning Agent (LLM root-cause analysis)
    ↓
Report Generator → Audit Layer → Human escalation (if threshold met)
```

## Components

| Module | Purpose |
|---|---|
| `collectors/` | Gather metrics from Prometheus, logs from ELK |
| `detectors/` | Detect anomalies in collected metrics |
| `retrievers/` | Query WeKnora knowledge base for relevant playbooks |
| `agents/` | LLM-based root-cause reasoning and decision making |
| `reports/` | Generate inspection reports (Markdown + JSON) |
| `audit/` | Audit trail for every agent decision |
| `config/` | Configuration (endpoints, thresholds, schedules) |

## Configuration

Copy `config/settings.example.yaml` to `config/settings.yaml` and fill in your endpoints.

## Usage

```bash
# Run a single inspection cycle
python -m aiops_agent run

# Start scheduled inspections
python -m aiops_agent schedule --interval 300

# Query a specific alert
python -m aiops_agent query "Pod CrashLoopBackOff on worker-03"
```

## Requirements

- Python 3.10+
- Access to Prometheus, WeKnora, and an LLM API endpoint