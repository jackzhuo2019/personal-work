import type { Profile, Project, SkillGroup, Experience } from "./types";

export const profile: Profile = {
  name: "Derek Zhuo",
  title: "SRE & DevOps Engineer",
  tagline: "18 years in production operations, AI-assisted engineering",
  bio: "SRE / DevOps engineer with 18 years in production operations, the last 10 focused on cloud-native infrastructure. Built a Kubernetes platform from scratch and scaled it past 200 nodes, sustained 99.99% availability for a financial-grade SaaS platform. Now building AI agent systems for production operations — scheduled inspections, log analysis, and alert triage.",
  location: "Shanghai, China",
  email: "zhuo2007.love@gmail.com",
  github: "https://github.com/jackzhuo2019",
  // upwork: "https://www.upwork.com/freelancers/~yourid",
  // resume: "/resume.pdf",
};

export const skills: SkillGroup[] = [
  { category: "Cloud & K8s", items: ["Kubernetes", "Docker", "AWS", "Azure", "Terraform", "Ansible"] },
  { category: "SRE", items: ["Prometheus", "Grafana", "Alertmanager", "SLO/SLI/SLA", "Incident Response", "ELK Stack"] },
  { category: "Development", items: ["Python", "Shell", "FastAPI", "Node.js", "Jenkins", "GitLab CI"] },
  { category: "AI Engineering", items: ["LLM Agents", "RAG", "Prompt Engineering", "LangChain", "Vector DB"] },
];

export const projects: Project[] = [
  {
    slug: "aiops-agent",
    title: "AIOps Intelligent Operations Assistant",
    tagline: "LLM Agent for automated inspection, log analysis, and alert root-cause triage",
    tech: ["Python", "LLM", "Prometheus", "WeKnora", "Docker"],
    image: "/projects/aiops-architecture.svg",
    architecture: "/projects/aiops-architecture.svg",
    situation: "Production environments generate massive alert noise. Manual inspection is slow, off-hours coverage is thin, and root-cause analysis across distributed systems is the bottleneck.",
    task: "Design and build an LLM agent system that automates scheduled health checks, anomaly detection, and root-cause triage — with human escalation only when defined conditions are met.",
    action: "Built a closed-loop pipeline: scheduler → Prometheus collectors → threshold detectors → WeKnora knowledge retrieval → LLM reasoning agent → report generation. Every agent decision is recorded in an append-only audit trail, applying SLO discipline to non-deterministic AI systems.",
    result: "Successfully ran end-to-end on a live K8s cluster: collected metrics from 4 nodes and 32 pods, detected 4 real anomalies (3 P0 + 1 P1), retrieved relevant playbooks from WeKnora for each, and produced structured inspection reports with root-cause hypotheses and actionable remediation steps.",
    highlights: [
      "Closed-loop pipeline: collect → detect → retrieve → reason → report",
      "Agent queries WeKnora knowledge base for relevant playbooks during root-cause analysis",
      "Audit trail records every agent decision — traceable and reviewable",
      "Designed by 18 years of production operations experience — failure modes are real, not demo scenarios",
    ],
    metrics: [
      { label: "Nodes monitored", value: "4" },
      { label: "Pods checked", value: "32" },
      { label: "Anomalies detected", value: "4" },
      { label: "Playbooks retrieved per anomaly", value: "10" },
      { label: "Agent confidence range", value: "68%–72%" },
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: true,
  },
  {
    slug: "ops-knowledge-base",
    title: "Ops Knowledge Base powered by WeKnora",
    tagline: "Production-grade RAG system for ops runbooks and incident playbooks, built on Tencent's WeKnora",
    tech: ["WeKnora", "Python", "FastAPI", "Docker", "RAG"],
    image: "/projects/weknora-architecture.svg",
    architecture: "/projects/weknora-architecture.svg",
    situation: "Ops teams rely on scattered runbooks and tribal knowledge. When an incident hits, finding the right playbook takes longer than fixing the issue.",
    task: "Deploy a production-grade RAG platform, ingest real ops documentation, tune the retrieval chain for ops terminology, and expose a query API for the AIOps Agent.",
    action: "Deployed WeKnora (Tencent, 33k★) via Docker Compose with 5 containers. Ingested 8 sanitized ops documents covering K8s troubleshooting, MySQL failover, alert classification, disk/memory issues, daily inspection, and log search. Tuned chunking (1000 chars, 140 overlap, parent-child off) for ops terminology precision.",
    result: "Knowledge-search API returns precise playbook references for ops queries. Querying 'disk full' correctly returns the K8s disk SOP without noise from Redis or MySQL docs. The AIOps Agent calls this API automatically during root-cause analysis.",
    highlights: [
      "Production-grade open-source over reinventing wheels — WeKnora (33k★) as the backbone",
      "Domain-tuned retrieval: chunk=1000 chars, overlap=140, parent-child off — eliminates cross-topic noise",
      "Serves as the knowledge layer for the AIOps Assistant — two projects compose into one system",
    ],
    metrics: [
      { label: "Documents indexed", value: "8" },
      { label: "Chunk size / overlap", value: "1000 / 140" },
      { label: "Parent-child chunking", value: "Off" },
      { label: "Search API", value: "X-API-Key" },
      { label: "Containers", value: "5" },
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: true,
  },
  {
    slug: "alert-noise-reduction",
    title: "Alert Noise Reduction & Root-Cause Dashboard",
    tagline: "Agent-based alert aggregation, correlation, and root-cause visualization",
    tech: ["Python", "LLM", "FastAPI", "Streamlit", "Docker"],
    image: "/projects/project-3.svg",
    situation: "A single node failure cascades into hundreds of alerts across services. On-call engineers drown in noise and miss the actual root cause.",
    task: "Build a system that simulates alert storms, then uses an agent to aggregate correlated alerts, suppress noise, and pinpoint the root cause.",
    action: "Alert storm generator produces realistic cascading scenarios. Agent performs temporal correlation analysis, groups alerts by source, and reasons about causality. Dashboard shows before/after noise reduction.",
    result: "Demonstrates measurable noise reduction on simulated alert storms. Root-cause accuracy validated against known scenarios.",
    highlights: [
      "Realistic cascading alert simulation (CPU → DB → service → gateway)",
      "Temporal correlation + causal reasoning agent",
      "Before/after dashboard for quantifiable noise reduction",
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: false,
  },
];

export const experiences: Experience[] = [
  {
    role: "E-commerce Project Manager",
    company: "Voicecomm Technology Co., Ltd.",
    period: "2026.06 — Present",
    description: "Lead product management, design, QA and operations for a cross-border B2B distribution platform.",
    achievements: [
      "Orchestrate LLM agents across requirements — test cases — scripts — inspections — reports, running product, engineering and QA as parallel workstreams under a one-person-plus-agents delivery model",
      "Generate PRDs, field definitions, state machines and interactive prototypes from business descriptions, then deploy agents as adversarial reviewers to surface broken flows and edge-case gaps",
    ],
  },
  {
    role: "Operations Lead",
    company: "JD Technology (formerly Huijie Technology)",
    period: "2022.01 — 2025.02",
    description: "Owned production reliability for a contact center SaaS platform serving financial-grade high-concurrency scenarios.",
    achievements: [
      "Sustained 99.99% annual availability with 15,000 concurrent agent seats and 20,000 concurrent calls",
      "Implemented SLO/SLI/SLA and end-to-end monitoring, cutting incident response time by 80% (first response under 5 minutes, MTTR under 30 minutes)",
    ],
  },
  {
    role: "Operations Lead",
    company: "Huijie (Shanghai) Technology Co., Ltd.",
    period: "2014.09 — 2022.01",
    description: "Owned operations team management and technical system development. Built Kubernetes platform from scratch.",
    achievements: [
      "Built a 200+ node Kubernetes cluster from scratch, standardized middleware deployment with Ansible",
      "Developed Python/Shell automation for batch deployment, configuration management, and routine inspections",
    ],
  },
];