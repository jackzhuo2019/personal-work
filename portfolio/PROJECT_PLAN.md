# Portfolio Project Plan

Five AI-engineering projects, each anchored in 18 years of production operations experience.
AI is the amplifier; domain expertise is the moat.

## Strategic Positioning

- **Primary**: DevOps / SRE & Cloud Infrastructure
- **Secondary**: AI-Assisted Operations / LLM Automation

Every project demonstrates the intersection of these two tracks.

---

## Project 1: Ops Knowledge Base powered by WeKnora

| Field | Value |
|---|---|
| Status | In Progress |
| Priority | 1 (start here) |
| Est. effort | 3–5 days |
| Tech stack | WeKnora (Docker), Python (API wrapper), sanitized ops docs |
| Deployed at | `172.17.23.94` (internal, Ubuntu 24.04, Docker 29.9.0) |

### What

Deploy Tencent's open-source WeKnora as the knowledge platform. Ingest real operations
runbooks, incident playbooks, and SOPs (sanitized). Tune the retrieval chain for ops
terminology. Wrap a custom API for ops-specific queries like "what's the playbook for
this alert?" and produce an evaluation report on retrieval quality.

### Why WeKnora instead of building from scratch

- WeKnora (Tencent, 33k+ stars, Go) covers the full RAG chain at production quality
- Building a toy RAG from scratch looks like a learning exercise, not engineering
- The differentiator is **domain customization**, not reinventing the pipeline
- Faster to a working demo — 3–5 days vs 2 weeks

### What this project demonstrates

| Capability | How it shows |
|---|---|
| Tech selection | Picks mature open-source over reinventing wheels |
| Domain tuning | General RAG doesn't understand ops terminology — this does |
| Diagnostic depth | Can identify which retrieval layer causes wrong answers |
| End-to-end delivery | Deploy → ingest → tune → API → evaluate |

### Architecture

```
WeKnora (Docker Compose)
├── Ops Docs (sanitized) → Ingestion → Chunking → Embeddings
├── Vector Store → Reranking → Context Assembly
├── Custom Ops Query API (Python / FastAPI wrapper)
└── Evaluation & Tracing Layer
```

### Integration with Project 2

This knowledge base becomes the **retrieval layer** for the AIOps Assistant (Project 2).
When the agent does root-cause reasoning, it queries WeKnora for relevant playbooks —
two projects compose into a fuller system.

### Deliverables

- [x] WeKnora deployed via Docker Compose (5 containers: app, frontend, postgres, redis, docreader)
- [x] Configure LLM model in WeKnora settings (OpenAI/DeepSeek/Qwen)
- [x] Ingest sanitized ops runbooks and incident playbooks (8 docs uploaded)
- [x] Tune chunking and embedding for ops terminology (chunk=1000 chars, overlap=140, parent-child off)
- [ ] Build FastAPI wrapper for alert-to-playbook queries
- [ ] Evaluation report (retrieval accuracy across configurations)
- [ ] Architecture diagram

---

## Project 2: AIOps Intelligent Operations Assistant ⭐

| Field | Value |
|---|---|
| Status | Planned |
| Priority | 2 (core project) |
| Est. effort | 2–3 weeks |
| Tech stack | Python, LLM (OpenAI/local), Prometheus API, Docker, FastAPI, WeKnora (knowledge layer) |

### What

An LLM agent system that automates the operations inspection loop:
scheduled health checks → log analysis → anomaly detection → root-cause reasoning → report generation.
Human escalation only when defined conditions are met.

### Why this is the flagship

- Combines 18 years of ops experience with AI engineering
- Targets real failure modes: alert fatigue, missed off-hour checks, slow RCA
- Directly matches the "AI Agent Automation for Production Operations" positioning on Upwork
- Composes with Project 1 (WeKnora knowledge base) for playbook retrieval

### Architecture

```
Scheduler → Collect (Prometheus + ELK) → Detect anomalies
    ↓
Reasoning Agent → Query WeKnora for playbooks → Root-cause hypothesis
    ↓
Report Generation → Audit & Trace Layer → Human escalation (if threshold met)
```

### Key differentiator

The failure modes it targets are real, recognized from 18 years of production operations —
not demo scenarios. The audit layer applies SLO discipline to non-deterministic AI systems.

### Deliverables

- [ ] GitHub repo with full source
- [ ] Demo video: end-to-end inspection cycle
- [ ] Sample inspection report (sanitized)
- [ ] Architecture diagram

---

## Project 3: Product Spec Generator

| Field | Value |
|---|---|
| Status | Planned |
| Priority | 3 |
| Est. effort | 2 weeks |
| Tech stack | Python, LangGraph / prompt chaining, Jinja2, Docker |

### What

A pipeline that turns a business description into structured product artifacts:
requirement breakdown → field definitions → state machine → interactive HTML prototype → test cases.
Each step has a review agent that adversarially checks for gaps.

### Why

- Productizes the "one-person-plus-agents" methodology proven at Voicecomm
- Shows product design capability + AI engineering in one project
- The methodology is the moat — not the LLM, but how each step is structured

### Pipeline

```
Input: "A library borrowing system"

  Step 1: Requirement Agent   → feature list, user roles, use cases
  Step 2: Data Model Agent    → fields, types, validation rules
  Step 3: State Machine Agent → borrowing state transitions diagram
  Step 4: Prototype Agent     → interactive HTML pages
  Step 5: Review Agent        → edge cases, deadlocks, permission gaps

Output: PRD.md + state-machine.svg + prototype.html + test-cases.json
```

### Deliverables

- [ ] GitHub repo with full source
- [ ] Online demo: input text → live prototype generation
- [ ] 2–3 case studies with different business domains

---

## Project 4: Kubernetes Resource Optimization Agent

| Field | Value |
|---|---|
| Status | Planned |
| Priority | 4 |
| Est. effort | 2 weeks |
| Tech stack | Python, kubernetes-client, Prometheus, LLM, Docker |

### What

An agent that analyzes cluster resource usage patterns and generates optimization recommendations:
over-provisioned workloads, idle pods, HPA tuning, resource request/limit adjustments.

### Why

- 200+ node K8s experience is a scarce asset
- K8s + AI combination has minimal competition on Upwork
- Can extract real scenarios from past production experience

### Deliverables

- [ ] GitHub repo with full source
- [ ] Demo on kind/minikube cluster
- [ ] Sample optimization report

---

## Project 5: Alert Noise Reduction & Root-Cause Dashboard

| Field | Value |
|---|---|
| Status | Planned |
| Priority | 5 |
| Est. effort | 1–2 weeks |
| Tech stack | Python, LLM, FastAPI, Streamlit, Docker |

### What

A system that simulates alert storms, then uses an agent to aggregate correlated alerts,
suppress noise, and pinpoint the root cause. Dashboard shows before/after comparison.

### Why

- SRE-specific: directly demonstrates incident response value
- Visual and interactive — strong portfolio piece
- Replaces the "AI job assistant" idea (platform API dependency made it impractical)

### Architecture

```
Alert Storm Generator (CPU spike → DB slow query → service timeout → gateway 502)
    ↓
Temporal Correlation Agent → Group by source → Causal reasoning
    ↓
Noise-suppressed Dashboard + Root-Cause Report
```

### Deliverables

- [ ] GitHub repo with full source
- [ ] Online demo: interactive dashboard
- [ ] Before/after noise reduction comparison

---

## Execution Timeline

```
Week 1:       Project 1 (Ops Knowledge Base w/ WeKnora)   ← fastest to demo
Week 2–4:     Project 2 (AIOps Assistant) ⭐               ← flagship, most weight
Week 5–6:     Project 3 (Product Spec Generator)
Week 7–8:     Project 4 (K8s Optimization Agent)
Week 9–10:    Project 5 (Alert Noise Reduction)
```

## Project Composition

```
Project 1 (WeKnora Knowledge Base)
    ↓ serves as retrieval layer
Project 2 (AIOps Assistant) ← queries playbooks during root-cause reasoning
    ↓ shares alert data
Project 5 (Alert Noise Reduction) ← feeds alerts to AIOps Agent

Project 3 (Product Spec Generator)   ← standalone
Project 4 (K8s Optimization Agent)   ← standalone
```

Projects 1, 2, and 5 form a composed AIOps system. Projects 3 and 4 are standalone.

## Portfolio Integration

Each completed project will be added to the portfolio website (`src/data/en.ts` and `src/data/zh.ts`)
with:
- STAR structure (Situation → Task → Action → Result)
- Tech stack tags
- GitHub link
- Demo link (when available)

Projects currently listed on the site are placeholders with real descriptions —
links and demos will be filled in as projects are completed.