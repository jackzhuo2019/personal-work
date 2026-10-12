import type { Profile, Project, SkillGroup, Experience } from "./types";

export const profile: Profile = {
  name: "Your Name",
  title: "Full-Stack Developer",
  tagline: "Solving real problems with code, shipping products that work",
  bio: "Full-stack developer focused on web applications and API backends. Experienced in building projects from scratch across the full development stack. I value clean, efficient code and great user experience.",
  location: "China",
  email: "your@email.com",
  github: "https://github.com/yourname",
  // upwork: "https://www.upwork.com/freelancers/~yourid",
  resume: "/resume.pdf",
};

export const skills: SkillGroup[] = [
  { category: "Frontend", items: ["React", "TypeScript", "Next.js", "Tailwind CSS", "HTML/CSS"] },
  { category: "Backend", items: ["Node.js", "Python", "FastAPI", "PostgreSQL", "Redis"] },
  { category: "DevOps", items: ["Docker", "CI/CD", "Linux", "Nginx", "AWS / Cloudflare"] },
  { category: "Tools", items: ["Git", "REST API", "GraphQL", "WebSocket", "OpenAPI"] },
];

export const projects: Project[] = [
  {
    slug: "project-one",
    title: "Project One",
    tagline: "One-line description of what the project does",
    tech: ["React", "Node.js", "PostgreSQL", "Docker"],
    image: "/projects/project-1.svg",
    situation: "Context: describe the problem or scenario the project addresses.",
    task: "Your role and responsibility in the project.",
    action: "Approach: the technical solution you chose and how you implemented it. Emphasize your decisions and technical depth.",
    result: "Outcome: quantifiable results, e.g. 'reduced API response time from 2s to 200ms', '5,000+ daily active users'.",
    highlights: [
      "Key technical decision or architecture choice",
      "Performance optimization or engineering practice",
      "Core challenge solved",
    ],
    links: { demo: "https://demo.example.com", github: "https://github.com/yourname/project-one" },
    featured: true,
  },
  {
    slug: "project-two",
    title: "Project Two",
    tagline: "One-line description of what the project does",
    tech: ["TypeScript", "FastAPI", "Redis", "Docker"],
    image: "/projects/project-2.svg",
    situation: "Context: describe the problem or scenario.",
    task: "Your role and responsibility.",
    action: "Approach: the technical solution and implementation.",
    result: "Outcome: quantifiable results.",
    highlights: ["Highlight one", "Highlight two", "Highlight three"],
    links: { demo: "https://demo.example.com", github: "https://github.com/yourname/project-two" },
    featured: true,
  },
  {
    slug: "project-three",
    title: "Project Three",
    tagline: "One-line description of what the project does",
    tech: ["Next.js", "Prisma", "PostgreSQL"],
    image: "/projects/project-3.svg",
    situation: "Context.",
    task: "Your role.",
    action: "Approach.",
    result: "Outcome.",
    highlights: ["Highlight one", "Highlight two", "Highlight three"],
    links: { demo: "https://demo.example.com", github: "https://github.com/yourname/project-three" },
    featured: false,
  },
];

export const experiences: Experience[] = [
  {
    role: "Full-Stack Developer",
    company: "Company Name",
    period: "2024.01 — Present",
    description: "Led the design and development of xxx system using xxx tech stack.",
    achievements: [
      "Drove refactoring of xxx module, reducing codebase by 40%",
      "Designed and implemented xxx API, supporting 100k daily requests",
    ],
  },
  {
    role: "Backend Developer",
    company: "Company Name",
    period: "2022.06 — 2023.12",
    description: "Developed and maintained xxx backend services.",
    achievements: [
      "Implemented xxx feature, improving xx efficiency",
      "Optimized database queries, reducing P99 latency by 60%",
    ],
  },
];