# Analytics methodology

The README displays committed SVG images, not live third-party widgets. Their exact inputs and UTC timestamp are in [`assets/analytics/snapshot.json`](../assets/analytics/snapshot.json). The generator is [`scripts/analytics.py`](../scripts/analytics.py), using only Python's standard library.

## What each card measures

| Card | Source and calculation | Limits |
| --- | --- | --- |
| Contribution history | Counts from the tooltips on [GitHub's public contribution calendar](https://github.com/users/diluxlane/contributions), summed by calendar month over the latest 365 UTC dates. | GitHub defines what counts as a contribution. This includes events other than commits and can include anonymized private activity if the account exposes it publicly. First/current months are partial. No private repository names are fetched. |
| Languages by repository | REST repository metadata, one vote for each non-null primary language in the included projects. | Repository count, not code volume or skill. A repository can contain several languages despite having one primary language. |
| Recent commit activity | REST commit lists on each owned, non-fork public repository's default branch, filtered to GitHub author login `diluxlane`. Deduplicated by SHA across repositories and grouped into 12 rolling seven-day buckets ending on the snapshot date. | Uses author dates in UTC. Includes authored merge commits and imported history if present. Excludes bots, unlinked identities, non-default branch work, deleted repositories, other owners, and private code. This is not GitHub's account-wide total commit count. |
| Public project activity | Current owned/non-fork public repository count. Unique authored default-branch commits and authored PRs merged in those repositories during the same 365 dates. | Closed PRs are paginated completely; only merged PRs authored by `diluxlane` count. PR window uses merge date. Commit window uses author date. Repository count is a current inventory, not a period event count. |
| Repository language bytes | REST `/repos/{owner}/{repo}/languages` bytes summed across included projects and divided by the included byte total. | GitHub Linguist's content classification, not proficiency, manual authorship, hours, or lines of code. Percentages are rounded to one decimal. |

Primary-language and language-byte charts exclude:

- `Zyberlane-Design-Library`: contains third-party/reference material and generated previews.
- `diluxlane`: profile artwork, analytics, and maintenance scripts would describe profile plumbing.

The four remaining project repositories still contain attributed design/implementation adaptations and AI-assisted work. Filtering does not convert repository bytes into a measure of personal mastery. The README therefore states this limitation next to the charts.

Activity cards include the reference library and profile, because those are real repositories with maintenance activity. These counts describe recorded activity only. No rank, streak, score, fake “languages by commit,” or inferred skill level is generated.

## Refresh and failure behavior

The [workflow](../.github/workflows/profile-analytics.yml) validates the committed snapshot on pull requests and relevant pushes. After merge, it also refreshes on a daily schedule, on relevant `main` pushes, or by manual workflow dispatch. GitHub schedules can be delayed; the image timestamp is authoritative. The initial snapshot was fetched during implementation, before merging.

The public calendar is an official GitHub page, but its HTML structure is not a versioned API contract. The parser requires all 365 expected dates and valid numeric tooltip counts. If GitHub changes that markup, a request fails, or validation fails, the refresh exits with an error and **does not commit replacement charts**. The previous timestamped snapshot stays visible. There is no fabricated-zero fallback.

All repository REST collections are paginated. Only public repository metadata and minimal commit dates/SHAs are persisted. No author emails, tokens, PR bodies, personal contact information, or private repository identities are stored. API authentication is sent only to `api.github.com`; the public calendar request is unauthenticated.

The workflow grants `contents: read` by default and `contents: write` only to the refresh job. It uses the built-in `GITHUB_TOKEN`, a pinned checkout action, and no added secrets or dependencies. PR jobs cannot publish analytics. Refresh commits stage only `assets/analytics`; branch protection, if configured, remains enforced. A rejected push leaves the previous version intact.

## Reproduce locally

```bash
python3 -m unittest discover -s tests -v
python3 scripts/analytics.py --render-only
```

Refresh from GitHub (an optional `GITHUB_TOKEN` increases REST rate limits):

```bash
python3 scripts/analytics.py
```

Relevant upstream documentation: [repository languages](https://docs.github.com/en/rest/repos/repos#list-repository-languages), [commit list filters](https://docs.github.com/en/rest/commits/commits#list-commits), [pull requests](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests), and [workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions).
