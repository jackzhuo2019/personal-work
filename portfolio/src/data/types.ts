// =====================================================
//  类型定义 — 双语共享
// =====================================================
export type Lang = "en" | "zh";

export interface Profile {
  name: string;
  title: string;
  tagline: string;
  bio: string;
  location: string;
  email: string;
  github: string;
  upwork?: string;
  resume?: string;
}

export interface Project {
  slug: string;
  title: string;
  tagline: string;
  tech: string[];
  image: string;
  situation: string;
  task: string;
  action: string;
  result: string;
  highlights: string[];
  links: { demo?: string; github?: string };
  featured: boolean;
}

export interface SkillGroup {
  category: string;
  items: string[];
}

export interface Experience {
  role: string;
  company: string;
  period: string;
  description: string;
  achievements: string[];
}

// UI 字符串
export interface UIStrings {
  nav: { projects: string; skills: string; experience: string; contact: string };
  hero: { status: string; statusUpwork: string; viewWork: string; contactMe: string };
  projects: { title: string; featured: string; others: string };
  skills: { title: string };
  experience: { title: string };
  contact: {
    title: string;
    email: string;
    github: string;
    upwork: string;
    resume: string;
    downloadPdf: string;
  };
  projectPage: {
    back: string;
    demo: string;
    source: string;
    situation: string;
    task: string;
    action: string;
    result: string;
    highlights: string;
  };
  langSwitch: { en: string; zh: string };
}