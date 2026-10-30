# Profile evidence and design decisions

Audit: 30 October 2026. Only `diluxlane/diluxlane` is changed by this work. The complete supplied “Dilux GitHub Profile README Evidence & Design Audit” PDF was read; both supplied screenshots were inspected. They guide facts and layout respectively, not identity or artwork reuse.

## Current public inventory

GitHub owner search and public metadata agree on six repositories. All use `main` as their default branch. Each repository's metadata, README, recursive tree, recent default-branch commits and PR history were reviewed read-only. Commit review covered up to 100 recent commits per repository; analytics separately paginates its scoped data completely.

| Repository | Inspected default-branch head | Evidence / treatment |
| --- | --- | --- |
| [diluxlane](https://github.com/diluxlane/diluxlane) | `55fdc9bad82356c082833cf0f067900c03e7ad62` | Accurate but plain existing profile; student/founder positioning retained. |
| [Divine-Tattoo-Website](https://github.com/diluxlane/Divine-Tattoo-Website) | `8fd93867d022942c3d0ca4dca735a922e4df89c6` | Client website and CMS; SQL, Auth, Storage, RLS, limited TypeScript Edge Function. |
| [Zyberlane-Website](https://github.com/diluxlane/Zyberlane-Website) | `2bd10a2dcb9f3aa179faeaf6103f89dd50c84918` | Static multi-page web work, Supabase integration, Canvas/WebGL fluid implementation, SEO/security regression tooling, extensive PR iteration. |
| [Dilux-Lane-Dev-Portfolio](https://github.com/diluxlane/Dilux-Lane-Dev-Portfolio) | `6e2111a534c1a64a867f268e0330b5fc83675f7c` | Vite and GSAP manifest; browser graphics integration; permitted Daniel Kiss adaptation and third-party notices preserved. |
| [Dilux-Lane-Portfolio](https://github.com/diluxlane/Dilux-Lane-Portfolio) | `fcc88c6e299d1094351f845879721f750abed8c9` | Astro/Tailwind/GSAP manifest, TypeScript tooling and source, Playwright/axe-core browser tests; permitted design-reference rebuild recorded in PR/history. |
| [Zyberlane-Design-Library](https://github.com/diluxlane/Zyberlane-Design-Library) | `ca3252929c90f5d143ba98db4c064457299a9b73` | Catalogue/build/preview tooling with credited third-party references. Kept separate and excluded from language charts. |

The current profile page was also read directly. Public identity is Dilux Lane / `diluxlane`; it describes learning software engineering/cybersecurity. It does not establish professional engineering credentials.

## Technology decisions

- **Included prominently:** HTML/CSS/JavaScript, Supabase, Astro, Tailwind, Vite, GSAP, Git/GitHub and Vercel, supported by current READMEs, manifests and source.
- **Included with scope:** Postgres through Supabase, Auth/Storage/RLS; Playwright and axe-core as verification tools; Canvas/WebGL as integration/adaptation; TypeScript as tooling and limited source.
- **Learning only:** Python fundamentals, Linux/cybersecurity fundamentals, systems and automation. The PDF and existing profile support these learning interests. Python in the reference library does not prove Python expertise.
- **Excluded from the skill display:** React, Next.js, Java, C/C++, MongoDB, Docker, AWS, Kubernetes, ML frameworks, security-professional titles, and senior engineer/researcher claims. Their presence in reference assets or aspirational service descriptions would not establish personal proficiency.
- **Workflow:** PRs, preview/review, scoped fixes, test files and iteration are observed. This does not prove independent authorship of every line or general production expertise.

No awards, follower counts, client performance metrics, employees, certifications, email addresses, or phone numbers are added. Instagram `@dilux.ln` was explicitly supplied in the prior public README and source PDF.

## Visual architecture

1. Original 3:1 cinematic banner: wide establishing shot, dark negative space, minimal name treatment.
2. Concise student/founder introduction and practical learning direction.
3. Code-style About card and original workstation illustration; stacked mobile composition and equivalent plain text.
4. Locally hosted, labelled technology tiles divided into project and workflow use; native wrapping.
5. Functional stack table and clearly separate learning line.
6. Four compact proof projects; design/reference tooling separate; adaptation credits remain visible.
7. Contribution overview, then two rows of analytics cards with exact scopes and source data.
8. Three verified/publicly supplied contact links and a quiet footer.

The first reference's useful details are its asymmetric code/image pairing, narrow spacing within grouped icons and wider separation between sections, and one wide dashboard card over paired smaller cards. The second's useful details are a roughly 2.5–3:1 atmospheric banner, identity before metrics, illustrated About section, and centered icon organization. Neither reference's personal copy, numbers, anime imagery, affiliations, trophies, support links, counters, or quotes are used.

GitHub-compatible Markdown/HTML supplies the structure. No inline CSS, scripts, iframes or externally hosted widgets are required. `<picture>` provides mobile variants; the analytics cards use fixed maximum presentation widths so pairs wrap naturally when space narrows. Labels and project descriptions remain native text. Assets and attribution are documented in [`assets/profile/ASSETS.md`](../assets/profile/ASSETS.md).
