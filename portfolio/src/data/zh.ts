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
    tagline: "带 kubectl 执行层的 LLM Agent — 通过实际运行诊断命令调查异常，而非仅读文档",
    tech: ["Python", "LLM", "Prometheus", "WeKnora", "kubectl", "Docker"],
    image: "/projects/aiops-architecture.svg",
    architecture: "/projects/aiops-architecture.svg",
    situation: "生产环境告警噪声巨大，人工巡检速度慢、非工作时间覆盖薄弱，分布式系统的根因分析成为瓶颈。现有工具能发现问题但无法调查问题——工程师仍需手动 SSH 进去执行 kubectl 命令。",
    task: "构建一个不只读 playbook，而是实际执行只读诊断命令（kubectl describe、logs、events）收集真实证据，然后综合分析得出根因并提出修复建议的 LLM Agent。",
    action: "构建带权限分层执行层的闭环流水线：L0 只读命令（kubectl get/describe/logs）自动执行收集证据；L2 操作（删除 Pod、清理镜像）提出建议但需人工审批；L3+（scale、cordon、drain）禁止执行。Agent 查询 WeKnora 获取相关 playbook 作为可选上下文，非硬依赖。每个命令和决策均记录在只追加审计日志中。",
    result: "在真实 4 节点 K8s 集群（32 Pod）上端到端跑通：检测到 4 个真实异常，执行 20 条诊断命令（kubectl describe/logs/events），收集到实际证据——如 Pod 因 ephemeral-storage 不足被 Evicted，通过 kubectl describe 输出确认。Agent 生成包含证据支撑的根因假设的结构化报告。",
    highlights: [
      "Agent 执行真实 kubectl 命令收集证据——不是只读文档然后猜测",
      "权限分层：L0 自动执行（只读），L2 需人工审批，L4 禁止",
      "命令白名单强制安全——只有明确允许的命令才能执行，其余一律拒绝",
      "WeKnora 知识库为可选上下文，非硬依赖——没有 playbook 也能工作",
      "审计追踪记录每个命令、结果和 Agent 决策——完全可追溯",
    ],
    metrics: [
      { label: "监控节点数", value: "4" },
      { label: "检查 Pod 数", value: "32" },
      { label: "检测异常数", value: "4" },
      { label: "执行诊断命令", value: "20" },
      { label: "权限层级", value: "L0–L4" },
    ],
    links: { github: "https://github.com/jackzhuo2019" },
    featured: true,
  },
  {
    slug: "ops-knowledge-base",
    title: "基于 WeKnora 的运维知识库",
    tagline: "基于腾讯开源 WeKnora 构建的生产级 RAG 系统，用于运维手册与故障 playbook",
    tech: ["WeKnora", "Python", "FastAPI", "Docker", "RAG"],
    image: "/projects/weknora-architecture.svg",
    architecture: "/projects/weknora-architecture.svg",
    situation: "运维团队依赖分散的手册和口口相传的知识。故障发生时，找到正确的 playbook 比修复问题耗时更长。",
    task: "部署生产级 RAG 平台，导入真实运维文档，针对运维术语调优检索链路，为 AIOps Agent 提供查询 API。",
    action: "通过 Docker Compose 部署 WeKnora（腾讯开源，33k★），5 个容器运行。导入 8 篇脱敏运维文档，覆盖 K8s 故障处理、MySQL 主从切换、告警分级、磁盘/内存问题、每日巡检、日志检索。调优分块参数（1000 字符，140 重叠，关闭父子分块）以精确匹配运维术语。",
    result: "Knowledge-search API 对运维查询返回精确的 playbook 引用。查询「磁盘满」正确返回 K8s 磁盘 SOP，不混入 Redis 或 MySQL 文档。AIOps Agent 在根因分析时自动调用此 API。",
    highlights: [
      "生产级开源方案优先——WeKnora（33k★）作为骨架，不重复造轮子",
      "领域调优检索：chunk=1000 字符，overlap=140，关闭父子分块——消除跨主题噪声",
      "作为 AIOps 助手的知识层——两个项目组合为一个系统",
    ],
    metrics: [
      { label: "索引文档数", value: "8" },
      { label: "分块大小/重叠", value: "1000 / 140" },
      { label: "父子分块", value: "关闭" },
      { label: "检索 API", value: "X-API-Key" },
      { label: "容器数", value: "5" },
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