import type { Lang, Profile, Project, SkillGroup, Experience, UIStrings } from "./types";
import * as en from "./en";
import * as zh from "./zh";
import { ui as uiData } from "./ui";
import type { Profile as EnProfile, Project as EnProject, SkillGroup as EnSkillGroup, Experience as EnExperience } from "./en";
import type { Profile as ZhProfile, Project as ZhProject, SkillGroup as ZhSkillGroup, Experience as ZhExperience } from "./zh";

export type { Lang } from "./types";

export interface LocaleData {
  profile: Profile;
  skills: SkillGroup[];
  projects: Project[];
  experiences: Experience[];
  t: UIStrings;
}

const locales: Record<Lang, Omit<LocaleData, "lang">> = {
  en: {
    profile: en.profile,
    skills: en.skills,
    projects: en.projects,
    experiences: en.experiences,
    t: uiData.en,
  },
  zh: {
    profile: zh.profile,
    skills: zh.skills,
    projects: zh.projects,
    experiences: zh.experiences,
    t: uiData.zh,
  },
};

export function getLocale(lang: Lang): LocaleData {
  return locales[lang];
}

// URL prefix — English at root, Chinese under /zh/
export function langPrefix(lang: Lang): string {
  return lang === "en" ? "" : "/zh";
}

// Build a path for the current language
export function path(lang: Lang, rest: string): string {
  const prefix = langPrefix(lang);
  if (rest === "/") return prefix || "/";
  return `${prefix}${rest}`;
}

// Switch language link: given current lang and current path, produce the equivalent path in the other lang
export function switchLangPath(currentLang: Lang, currentPath: string): string {
  if (currentLang === "en") {
    // en → zh: prepend /zh
    return currentPath === "/" ? "/zh" : `/zh${currentPath}`;
  } else {
    // zh → en: strip /zh prefix
    return currentPath.startsWith("/zh") ? currentPath.slice(3) || "/" : currentPath;
  }
}

export const languages: Lang[] = ["en", "zh"];