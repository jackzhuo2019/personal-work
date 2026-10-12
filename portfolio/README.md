# Bilingual Portfolio Website

A bilingual (English / Chinese) static portfolio website built with Astro, designed for job applications and Upwork freelancing.

## Quick Start

```bash
npm install      # Install dependencies
npm run dev      # Local development → http://localhost:4321
npm run build    # Build → dist/
```

## Bilingual Architecture

| Language | Path | Description |
|---|---|---|
| English | `/` | Default language, for international audience |
| Chinese | `/zh/` | Chinese version, for domestic audience |

A language switch button (`EN | 中文`) in the navbar toggles between the current page's corresponding language version.

## How to Customize

### Content Data (one file per language)

| File | Description |
|---|---|
| `src/data/en.ts` | English content (profile, skills, projects, experience) |
| `src/data/zh.ts` | Chinese content (profile, skills, projects, experience) |
| `src/data/ui.ts` | UI strings (nav, buttons, labels) |
| `src/data/types.ts` | TypeScript type definitions |
| `src/data/index.ts` | i18n helpers (getLocale, path, switchLangPath) |

Edit `en.ts` and `zh.ts` to update all site content — no component changes needed.

### Adding a New Project

Add a project object to both data files (slug must match). Detail pages are auto-generated at:
- English: `/projects/<slug>/`
- Chinese: `/zh/projects/<slug>/`

### Project Screenshots

Place screenshots in `public/projects/` and reference the path in the `image` field of the data files.

## Site Structure

```
English Home ( / )  ←→  Chinese Home ( /zh/ )
├── Hero — Name, title, bio
├── Projects — Featured project cards + other projects
├── Skills — Tech stack
├── Experience — Work history
└── Contact — Email, GitHub, Upwork, résumé

English Project ( /projects/[slug]/ )  ←→  Chinese Project ( /zh/projects/[slug]/ )
├── STAR structure (Situation → Task → Action → Result)
└── Technical highlights
```

## Tech Stack

- **Astro** v7 — Static site generation, zero JS runtime
- **TypeScript** — Type-safe content data
- **i18n** — Manual route isolation, `/` English + `/zh/` Chinese
- **Pure CSS** — CSS variable theming, auto light/dark mode
- Responsive design

## Deployment

```bash
npm run build    # Output to dist/
npx vercel       # Or deploy dist/ to Cloudflare Pages / GitHub Pages
```

Then set up GitHub Actions or your hosting platform's auto-deploy from the `main` branch.

## License

MIT