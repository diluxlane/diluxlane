# Validation report

Completed 30 October 2026 for the cinematic profile branch.

## Evidence and scope

- Read the complete 13-page supplied PDF and inspected both reference screenshots.
- Reviewed all six current owned public repositories read-only: metadata, descriptions, READMEs, trees, manifests where present, recent commits and PR histories.
- Read the current public profile and existing README; retained student/founder positioning and qualified learning directions.
- Only the profile repository is modified. No merge, project deployment, repository setting or external project change is part of this PR.

## Automated checks

Twelve Python tests pass locally and in GitHub Actions. They cover complete calendar dates, numeric source parsing, REST pagination, exclusion enforcement, deduplicated-source totals, zero-activity behavior, deterministic SVG output, preservation of the prior snapshot after failed validation, local links/images, alt text, privacy/widget restrictions, asset size and SVG parsing.

The generator was run against live public GitHub data. The committed initial snapshot is timestamped `2026-10-30T12:58:10+00:00`: 407 contributions reported by GitHub, six owned public repositories, 366 scoped authored default-branch commits, and 63 scoped authored merged PRs. These are different metrics with different definitions; see [methodology](analytics.md).

All 13 unique external README links returned HTTP 200, including project destinations, GitHub repositories, the developer portfolio attribution page, and the supplied Instagram account. No private email or phone is displayed.

## Rendering and visual QA

- GitHub's Markdown rendering API accepted the complete README and preserved the two responsive `<picture>` elements, native tables and collapsible plain-text About copy.
- The live GitHub branch was opened in a browser. All 19 README images loaded successfully; the 838px-wide README displayed the intended paired analytics cards without horizontal overflow.
- The exact GitHub-rendered markup was also previewed locally with official GitHub CSS in dark mode, using Chromium. At viewport widths **320, 390, 600, 768 and 1440**, every image loaded and document scroll width matched viewport width. Mobile sources switched correctly. About artwork stacks, icons wrap, tables wrap within their native GitHub containers, and analytics cards stack naturally.
- A 390px failed-analytics-image simulation preserved the native scope notes, data links and layout without page-wide overflow. Actual service failures retain the committed images, so this simulation is a stronger failure case.
- Hero, About composition, SVG charts, icon contrast, and mobile/desktop screenshots were inspected. GitHub and Astro tile contrast was corrected during review.
- Combined profile assets are approximately **306 KB**. No remote stats service, temporary artwork URL, inline script, iframe, custom page CSS, trophy, view counter, donation block, copied identity or unfinished section appears in the README.

## Practical limits

Phone-width browser rendering was tested; the native GitHub Android/iOS app was not available for direct testing. The local headless browser lacks an emoji font, while the actual GitHub browser rendered the greeting emoji correctly. This is a test-runtime font difference.

The initial GitHub Actions run validated the committed files successfully. The review-branch workflow additionally exercises live collection using the built-in token without committing its output. Daily publishing starts after merge; the parser deliberately fails if GitHub's public calendar markup changes, preserving the prior snapshot. GitHub schedule delays and any future branch-protection rejection remain visible operational limits.

## Files

- `README.md`: complete profile presentation.
- `assets/profile/`: hero, developer illustration, editable code card, responsive compositions and provenance notes.
- `assets/icons/`: 12 upstream marks, 12 labelled tiles, pinned sources and license.
- `assets/analytics/`: five data cards, one mobile variant and exact source snapshot.
- `scripts/analytics.py`: public-data collection, validation and deterministic SVG generation.
- `scripts/build-profile-assets.cjs`: reproducible card/tile composition.
- `.github/workflows/profile-analytics.yml`: read-only validation and narrowly scoped refresh job.
- `tests/test_analytics.py`, `.gitignore`, and `docs/`: tests, generated-file hygiene, evidence/design choices and analytics methodology.
