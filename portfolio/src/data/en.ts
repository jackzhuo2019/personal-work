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
    tech: ["Python", "LLM", "Prometheus", "Docker", "FastAPI"],
    image: "/projects/project-1.svg",
    situation: "Production environments generate massive alert noise. Manual inspection is slow, off-hours coverage is thin, and root-cause analysis across distributed systems is the bottleneck.",
    task: "Design and build an LLM agent system that automates scheduled health checks, log analysis, and alert triage — with human escalation only when defined conditions are met.",
    action: "Built a closed-loop multi-agent pipeline: schedule → collect metrics & logs → anomaly detection → root-cause reasoning → report generation. Added an audit and trace layer so every agent decision is reviewable, applying SLO discipline to non-deterministic systems.",
    result: "Targets real operational failure modes — alert fatigue, missed off-hour checks, slow root-cause analysis. Reduces manual inspection effort significantly.",
    highlights: [
      "Multi-agent closed loop: collect → detect → reason → report",
      "Audit trail for every agent decision, traceable and reviewable",
      "Designed by 18 years of production operations experience — failure modes are real, not demo scenarios",
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: true,
  },
  {
    slug: "rag-knowledge-base",
    title: "RAG Knowledge Base & QA System",
    tagline: "Hand-built retrieval-augmented generation pipeline for ops runbooks and incident playbooks",
    tech: ["Python", "ChromaDB", "sentence-transformers", "FastAPI", "Docker"],
    image: "/projects/project-2.svg",
    situation: "Ops teams rely on scattered runbooks and tribal knowledge. When an incident hits, finding the right playbook takes longer than fixing the issue.",
    task: "Build a RAG pipeline from scratch — no framework black boxes — so every layer's failure mode stays observable.",
    action: "Layered architecture: ingestion & chunking → embeddings → vector store → cross-encoder reranking → evaluation scoring → tracing & observability → retrieval interface. Each layer hand-written, not framework-assembled.",
    result: "When the AI returns a wrong answer, can identify exactly which layer caused it and prove it. Full observability across the retrieval chain.",
    highlights: [
      "Hand-written pipeline, no framework abstractions hiding failure modes",
      "Cross-encoder reranking + evaluation scoring for retrieval quality",
      "Tracing and observability at every layer — not just the final answer",
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