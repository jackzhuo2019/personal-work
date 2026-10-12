# Portfolio Project Plan

Five AI-engineering projects, each anchored in 18 years of production operations experience.
AI is the amplifier; domain expertise is the moat.

## Strategic Positioning

- **Primary**: DevOps / SRE & Cloud Infrastructure
- **Secondary**: AI-Assisted Operations / LLM Automation

Every project demonstrates the intersection of these two tracks.

---

## Project 1: RAG Knowledge Base & QA System

| Field | Value |
|---|---|
| Status | Planned |
| Priority | 1 (start here) |
| Est. effort | 1–2 weeks |
| Tech stack | Python, ChromaDB, sentence-transformers, FastAPI, Docker |

### What

A retrieval-augmented generation pipeline built from scratch — no framework black boxes.
Ingests operations runbooks and incident playbooks, answers natural-language queries,
and traces every retrieval step.

### Why this one first

- Clearest scope, fastest to a working demo
- Directly supports Upwork AI Engineer / LLM job categories
- RAG is the most common AI engineering interview topic

### Architecture

```
Documents → Chunking → Embeddings → Vector Store
                                        ↓
Query → Embedding → Vector Search → Cross-encoder Reranking → Context → LLM → Answer
                                        ↓
                              Tracing & Evaluation Layer
```

### Key differentiator

Each layer is hand-written, not framework-assembled.
When the AI returns a wrong answer, can identify exactly which layer caused it and prove it.

### Deliverables

- [ ] GitHub repo with full source
- [ ] Online demo (query a set of sample runbooks)
- [ ] Architecture diagram
- [ ] Evaluation report (retrieval accuracy metrics)

---

## Project 2: AIOps Intelligent Operations Assistant ⭐

| Field | Value |
|---|---|
| Status | Planned |
| Priority | 2 (core project) |
| Est. effort | 2–3 weeks |
| Tech stack | Python, LLM (OpenAI/local), Prometheus API, Docker, FastAPI |

### What

An LLM agent system that automates the operations inspection loop:
scheduled health checks → log analysis → anomaly detection → root-cause reasoning → report generation.
Human escalation only when defined conditions are met.

### Why this is the flagship

- Combines 18 years of ops experience with AI engineering
- Targets real failure modes: alert fatigue, missed off-hour checks, slow RCA
- Directly matches the "AI Agent Automation for Production Operations" positioning on Upwork

### Architecture

```
Scheduler → Collect (Prometheus + ELK) → Detect anomalies
    ↓
Reasoning Agent → Root-cause hypothesis → Report generation
    ↓
Audit & Trace Layer → Human escalation (if threshold met)
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
Week 1–2:   Project 1 (RAG Knowledge Base)        ← fastest to demo
Week 3–5:   Project 2 (AIOps Assistant) ⭐         ← flagship, most weight
Week 6–7:   Project 3 (Product Spec Generator)
Week 8–9:   Project 4 (K8s Optimization Agent)
Week 10:    Project 5 (Alert Noise Reduction)
```

## Portfolio Integration

Each completed project will be added to the portfolio website (`src/data/en.ts` and `src/data/zh.ts`)
with:
- STAR structure (Situation → Task → Action → Result)
- Tech stack tags
- GitHub link
- Demo link (when available)

Projects currently listed on the site are placeholders with real descriptions —
links and demos will be filled in as projects are completed.