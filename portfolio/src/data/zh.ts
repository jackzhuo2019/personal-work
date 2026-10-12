import type { Profile, Project, SkillGroup, Experience } from "./types";

export const profile: Profile = {
  name: "Derek Zhuo",
  title: "SRE / DevOps 工程师",
  tagline: "18 年生产运维经验，AI 驱动工程交付",
  bio: "SRE / DevOps 工程师，18 年生产运维经验，近 10 年专注云原生基础设施。从零搭建 Kubernetes 平台并扩展至 200+ 节点，保障金融级 SaaS 联络平台 99.99% 可用性。现致力于构建 AI Agent 系统赋能生产运维——定时巡检、日志分析与告警根因定位。",
  location: "上海，中国",
  email: "zhuo2007.love@gmail.com",
  github: "https://github.com/jackzhuo2019",
  // upwork: "https://www.upwork.com/freelancers/~yourid",
  // resume: "/resume.pdf",
};

export const skills: SkillGroup[] = [
  { category: "云与 K8s", items: ["Kubernetes", "Docker", "AWS", "Azure", "Terraform", "Ansible"] },
  { category: "SRE", items: ["Prometheus", "Grafana", "Alertmanager", "SLO/SLI/SLA", "故障响应", "ELK Stack"] },
  { category: "开发", items: ["Python", "Shell", "FastAPI", "Node.js", "Jenkins", "GitLab CI"] },
  { category: "AI 工程", items: ["LLM Agents", "RAG", "Prompt 工程", "LangChain", "向量数据库"] },
];

export const projects: Project[] = [
  {
    slug: "aiops-agent",
    title: "AIOps 智能运维助手",
    tagline: "LLM Agent 驱动的自动巡检、日志分析与告警根因定位系统",
    tech: ["Python", "LLM", "Prometheus", "Docker", "FastAPI"],
    image: "/projects/project-1.svg",
    situation: "生产环境告警噪声巨大，人工巡检速度慢、非工作时间覆盖薄弱，分布式系统的根因分析成为瓶颈。",
    task: "设计并构建 LLM Agent 系统，实现定时巡检、日志分析与告警分诊自动化——仅在满足预设条件时升级人工处理。",
    action: "构建闭环多 Agent 流水线：调度 → 采集指标与日志 → 异常检测 → 根因推理 → 报告生成。增加审计追踪层，每个 Agent 决策均可审查，将 SLO 纪律应用于非确定性系统。",
    result: "直击真实运维痛点——告警疲劳、非工作时间巡检遗漏、根因分析缓慢。显著降低人工巡检成本。",
    highlights: [
      "多 Agent 闭环：采集 → 检测 → 推理 → 报告",
      "每个 Agent 决策均有审计追踪，可追溯可审查",
      "基于 18 年生产运维经验设计——故障场景真实而非演示",
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: true,
  },
  {
    slug: "rag-knowledge-base",
    title: "RAG 知识库与问答系统",
    tagline: "手工构建的检索增强生成流水线，用于运维手册与故障 playbook",
    tech: ["Python", "ChromaDB", "sentence-transformers", "FastAPI", "Docker"],
    image: "/projects/project-2.svg",
    situation: "运维团队依赖分散的手册和口口相传的知识。故障发生时，找到正确的 playbook 比修复问题耗时更长。",
    task: "从零构建 RAG 流水线——不用框架黑盒——确保每一层的失败模式可观测。",
    action: "分层架构：文档分块 → embedding → 向量存储 → cross-encoder 重排序 → 评估打分 → 追踪与可观测性 → 检索接口。每层手写实现，非框架封装。",
    result: "当 AI 返回错误答案时，能精确定位是哪一层导致的并加以证明。全链路可观测。",
    highlights: [
      "手写流水线，无框架抽象隐藏失败模式",
      "Cross-encoder 重排序 + 评估打分保障检索质量",
      "每层均有追踪与可观测性——不只看最终答案",
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: true,
  },
  {
    slug: "alert-noise-reduction",
    title: "告警降噪与根因分析 Dashboard",
    tagline: "基于 Agent 的告警聚合、关联与根因可视化",
    tech: ["Python", "LLM", "FastAPI", "Streamlit", "Docker"],
    image: "/projects/project-3.svg",
    situation: "单个节点故障会级联出数百条跨服务告警。值班工程师淹没在噪声中，反而错过真正的根因。",
    task: "构建一个系统，模拟告警风暴，然后用 Agent 聚合关联告警、抑制噪声、定位根因。",
    action: "告警风暴生成器产生真实的级联场景。Agent 执行时序关联分析，按来源分组告警，推理因果关系。Dashboard 展示降噪前后对比。",
    result: "在模拟告警风暴上展示可量化的降噪效果。根因准确率基于已知场景验证。",
    highlights: [
      "真实级联告警模拟（CPU → DB → 服务 → 网关）",
      "时序关联 + 因果推理 Agent",
      "降噪前后 Dashboard 对比，效果可量化",
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: false,
  },
];

export const experiences: Experience[] = [
  {
    role: "电商项目经理",
    company: "声通科技股份有限公司",
    period: "2026.06 — 至今",
    description: "主导跨境 B2B 分销平台的产品管理、设计与测试运维。",
    achievements: [
      "以 AI Agent 驱动「需求—用例—脚本—巡检—报告」全链路，产品/研发/测试并行交付，形成「一人+Agent」模式",
      "由业务描述直接生成 PRD、字段定义、状态机与可交互原型，再由 Agent 反向挑刺，显著减少需求返工",
    ],
  },
  {
    role: "运维负责人",
    company: "京东科技（原慧捷科技）",
    period: "2022.01 — 2025.02",
    description: "负责联络中心 SaaS 平台的生产可靠性，保障金融级高并发场景。",
    achievements: [
      "保障 99.99% 年度可用性，支撑 1.5 万坐席、2 万路呼叫并发",
      "落地 SLO/SLI/SLA 与全链路监控，故障响应时间缩短 80%（首响 ≤5 分钟，MTTR ≤30 分钟）",
    ],
  },
  {
    role: "运维负责人",
    company: "慧捷（上海）科技有限公司",
    period: "2014.09 — 2022.01",
    description: "负责运维团队管理与技术体系建设，从零搭建 Kubernetes 平台。",
    achievements: [
      "从零搭建 200+ 节点 K8s 集群，用 Ansible 实现中间件标准化部署",
      "开发 Python/Shell 自动化工具，实现批量部署、配置管理与日常巡检自动化",
    ],
  },
];