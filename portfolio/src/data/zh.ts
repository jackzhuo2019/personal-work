import type { Profile, Project, SkillGroup, Experience } from "./types";

export const profile: Profile = {
  name: "Your Name",
  title: "全栈开发者",
  tagline: "用代码解决真实问题，交付可运行的产品",
  bio: "全栈开发者，专注于 Web 应用和 API 后端开发。擅长从零搭建项目，熟悉前后端全链路开发流程。追求简洁高效的代码和良好的用户体验。",
  location: "中国",
  email: "your@email.com",
  github: "https://github.com/yourname",
  // upwork: "https://www.upwork.com/freelancers/~yourid",
  resume: "/resume.pdf",
};

export const skills: SkillGroup[] = [
  { category: "前端", items: ["React", "TypeScript", "Next.js", "Tailwind CSS", "HTML/CSS"] },
  { category: "后端", items: ["Node.js", "Python", "FastAPI", "PostgreSQL", "Redis"] },
  { category: "DevOps", items: ["Docker", "CI/CD", "Linux", "Nginx", "AWS / Cloudflare"] },
  { category: "工具", items: ["Git", "REST API", "GraphQL", "WebSocket", "OpenAPI"] },
];

export const projects: Project[] = [
  {
    slug: "project-one",
    title: "项目名称一",
    tagline: "一句话描述项目做了什么",
    tech: ["React", "Node.js", "PostgreSQL", "Docker"],
    image: "/projects/project-1.svg",
    situation: "业务背景：描述项目要解决的问题或场景。",
    task: "任务目标：你在项目中负责什么。",
    action: "执行方案：你用了什么技术方案、怎么实现的，重点突出你的决策和技术深度。",
    result: "成果：可量化的结果，如 'API 响应时间从 2s 降到 200ms'，'日活用户 5000+'。",
    highlights: [
      "亮点一：关键技术决策或架构选择",
      "亮点二：性能优化或工程实践",
      "亮点三：解决的核心难题",
    ],
    links: { demo: "https://demo.example.com", github: "https://github.com/yourname/project-one" },
    featured: true,
  },
  {
    slug: "project-two",
    title: "项目名称二",
    tagline: "一句话描述项目做了什么",
    tech: ["TypeScript", "FastAPI", "Redis", "Docker"],
    image: "/projects/project-2.svg",
    situation: "业务背景：描述项目要解决的问题或场景。",
    task: "任务目标：你在项目中负责什么。",
    action: "执行方案：你用了什么技术方案、怎么实现的。",
    result: "成果：可量化的结果。",
    highlights: ["亮点一", "亮点二", "亮点三"],
    links: { demo: "https://demo.example.com", github: "https://github.com/yourname/project-two" },
    featured: true,
  },
  {
    slug: "project-three",
    title: "项目名称三",
    tagline: "一句话描述项目做了什么",
    tech: ["Next.js", "Prisma", "PostgreSQL"],
    image: "/projects/project-3.svg",
    situation: "业务背景。",
    task: "任务目标。",
    action: "执行方案。",
    result: "成果。",
    highlights: ["亮点一", "亮点二", "亮点三"],
    links: { demo: "https://demo.example.com", github: "https://github.com/yourname/project-three" },
    featured: false,
  },
];

export const experiences: Experience[] = [
  {
    role: "全栈开发工程师",
    company: "公司名称",
    period: "2024.01 — 至今",
    description: "负责 xxx 系统的设计与开发，使用 xxx 技术栈。",
    achievements: [
      "主导 xxx 模块重构，代码量减少 40%",
      "设计并实现 xxx 接口，支撑日均 10w 请求",
    ],
  },
  {
    role: "后端开发工程师",
    company: "公司名称",
    period: "2022.06 — 2023.12",
    description: "负责 xxx 后端服务的开发与维护。",
    achievements: [
      "实现 xxx 功能，提升了 xx 效率",
      "优化数据库查询，P99 延迟降低 60%",
    ],
  },
];