# Global Skill Radar

**Track popular AI Agent Skills on GitHub—every day, automatically.**

Global Skill Radar is an open-source discovery and ranking toolkit for AI Agent Skills. It identifies public `SKILL.md` files and Skill-related GitHub repositories, tracks repository popularity and changes over time, categorizes discovered Skills, and generates a daily Markdown intelligence report.

It is designed for developers and researchers using **Claude Code, OpenAI Codex, and other Agent Skills-compatible tools**.

> **Scope note:** This project creates a transparent ranking of the **public GitHub sample it discovers**. GitHub does not maintain an official all-Skills ranking, and search API results are not an exhaustive census. GitHub Stars are repository-level popularity signals—not install counts, verified quality scores, or proof of real-world effectiveness.

## Highlights

- **Popular Skills:** discover `SKILL.md` files through GitHub Code Search and Skill-related repositories through Repository Search.
- **Top 20 by Stars:** rank discovered Skill files using the Stars of their parent GitHub repositories.
- **Growth tracking:** compare consecutive daily snapshots to estimate Star growth.
- **New discoveries:** identify candidates absent from the previous snapshot; "first seen" does not necessarily mean "newly published."
- **Category insights:** apply transparent keyword-based tags to programming, research, writing, business, design, analytics, marketing, and other domains.
- **Automated daily reports:** create readable Markdown reports and maintain historical JSON snapshots.
- **Safety first:** collect metadata without executing code from third-party Skill repositories.

## Quick start: install the Agent Skill

If you want your AI agent to use the discovery and analysis workflow, install this repository using the [Skills CLI](https://www.skills.sh/docs/cli):

```bash
npx skills add parkplanet/global-skill-radar
```

The CLI prompts you to select a compatible agent and installation location. The CLI requires a supported Node.js version; check its current documentation before installing.

**Important:** Installing the Agent Skill does *not* start a daily scheduler. For unattended daily collection, use the GitHub Actions workflow described below.

## Run the collector locally

Requirements: **Python 3.12+**, a network connection, and access to the GitHub public APIs.

```bash
git clone https://github.com/parkplanet/global-skill-radar.git
cd global-skill-radar

python -m pip install -r requirements.txt

# Recommended: provide a GitHub token to increase API quota.
export GH_TOKEN="YOUR_GITHUB_TOKEN"

python scripts/collect_github_skills.py
python scripts/rank_skills.py
python scripts/classify_skills.py
python -m unittest discover -s tests -v
python scripts/validate_snapshot.py
python scripts/generate_report.py
```

On Windows PowerShell, set the token with `$env:GH_TOKEN="YOUR_GITHUB_TOKEN"`.

If you only want to inspect how the project searches GitHub, review `config/settings.yaml` and the collector script before running them. Tokens should never be committed to the repository.

## Schedule a daily run with GitHub Actions

The workflow lives at [`.github/workflows/daily-ranking.yml`](.github/workflows/daily-ranking.yml).

| Setting | Value |
|---|---|
| Schedule | Daily at 00:00 UTC |
| Asia/Shanghai time | 08:00 every day |
| Manual trigger | `workflow_dispatch` |
| Runtime | GitHub-hosted Ubuntu runner, Python 3.12 |
| Output | Snapshots committed to `data/` and daily Markdown reports committed to `reports/` |

**Setup**

1. Fork this project or add these files to your own GitHub repository.
2. Open **Settings → Actions → General** and allow the workflow to write repository contents where your account and repository rules permit it.
3. Optionally add a `GH_TOKEN` secret under **Settings → Secrets and variables → Actions**. The workflow also supports GitHub's default token; GitHub Code Search permissions and rate limits can differ.
4. Open **Actions → Daily Global Skill Radar → Run workflow** for an initial manual test.
5. Check the workflow logs and `reports/latest.md`. A configured schedule does not guarantee an on-time run, and a first run may be a baseline without growth comparisons.

GitHub Actions schedules run in UTC and can be delayed. The workflow configuration does not imply that GitHub has already executed a successful run.

## Data and report outputs

| File or directory | Purpose |
|---|---|
| `SKILL.md` | Portable, English-language Agent Skill instructions |
| `config/settings.yaml` | GitHub queries and category keywords |
| `scripts/collect_github_skills.py` | Retrieve public GitHub candidate metadata |
| `scripts/rank_skills.py` | Rank candidates and compare snapshots |
| `scripts/classify_skills.py` | Assign heuristic category labels |
| `scripts/validate_snapshot.py` | Check essential fields and candidate uniqueness |
| `scripts/generate_report.py` | Produce the daily Markdown report |
| `data/current.json` | Most recent normalized snapshot |
| `data/snapshots/YYYY-MM-DD.json` | Dated historical snapshots |
| `reports/latest.md` | Most recent report |
| `reports/daily/YYYY-MM-DD.md` | Archive of daily reports |

**Report language:** The documentation and Agent Skill description are in English for international discoverability. The current report generator still produces **Chinese-language daily reports**, intentionally preserving the established reporting workflow.

## How the rankings work

The report distinguishes between different signals:

| View | Signal | Interpretation |
|---|---|---|
| Most Starred | Current GitHub repository Star count | Long-term popularity proxy |
| Rising | Star difference between available snapshots | Short-period growth when comparable history exists |
| Newly Discovered | First detected in the collector's history | Discovery, not necessarily a new release |
| Category Distribution | Keyword-based topic matching | Approximate coverage by area |
| Active Repositories | Latest GitHub push timestamp | Maintenance/activity signal only |

The optional discovery score is a documented **heuristic**, combining normalized log Stars (45%), normalized log Forks (25%), recency of repository activity (20%), and metadata completeness (10%). It is **not** a Skill quality or safety score.

Because Stars are associated with repositories, multiple Skills from the same repository may share the same Star count. The collector also records repository candidates that have not been linked to an indexed `SKILL.md`; those must be treated as **unverified candidates**, not verified Skills.

## Methodology and limitations

- GitHub's Search APIs apply indexing rules, result caps, permissions, and rate limits. Some queries may return partial results or errors.
- The searchable public GitHub ecosystem is **not** the same as the global universe of Agent Skills.
- This collector searches for candidate paths and repository metadata; it does not fully verify every Skill's quality, license, execution behavior, or compatibility.
- Star growth requires at least two comparable snapshots. Missing historical information must never be fabricated.
- Category assignments use simple keyword matching; they can be imprecise or overlap.
- GitHub Stars, Forks, and push activity do **not** measure installs, usage, security, or professional quality.
- Third-party repository material is untrusted. This project does not run scripts found in discovered repositories.

## Contributing

Contributions to discovery coverage, ranking transparency, tests, documentation, and data quality are welcome. Please open an issue with a reproducible example or a focused pull request. Avoid making claims about global coverage or Skill effectiveness without supporting evidence.

## License

MIT. See [LICENSE](LICENSE).
