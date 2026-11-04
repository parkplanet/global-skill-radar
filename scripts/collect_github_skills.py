from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

from common import ROOT, CURRENT, github_headers, save_json, today_utc

API = "https://api.github.com"


def api_get(path: str, params: dict | None = None) -> dict:
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=github_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining is not None and int(remaining) < 10:
                print(f"WARNING: GitHub API rate limit remaining={remaining}", file=sys.stderr)
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API HTTP {exc.code}: {body[:500]}") from exc


def repo_record(repo: dict) -> dict:
    return {
        "repo_full_name": repo.get("full_name"),
        "repo_url": repo.get("html_url"),
        "description": repo.get("description") or "",
        "stars": int(repo.get("stargazers_count") or 0),
        "forks": int(repo.get("forks_count") or 0),
        "watchers": int(repo.get("watchers_count") or 0),
        "open_issues": int(repo.get("open_issues_count") or 0),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "license": (repo.get("license") or {}).get("spdx_id"),
        "topics": repo.get("topics") or [],
        "default_branch": repo.get("default_branch"),
    }


def main() -> None:
    settings = yaml.safe_load((ROOT / "config/settings.yaml").read_text(encoding="utf-8"))
    gh = settings["github"]
    per_page = min(int(gh.get("per_page", 100)), 100)
    max_pages = int(gh.get("max_pages", 3))
    warnings: list[str] = []
    repos: dict[str, dict] = {}
    skills: dict[str, dict] = {}
    query_log: list[dict] = []

    for query in gh.get("repository_queries", []):
        for page in range(1, max_pages + 1):
            try:
                result = api_get("/search/repositories", {
                    "q": query, "sort": "stars", "order": "desc",
                    "per_page": per_page, "page": page,
                })
                items = result.get("items", [])
                query_log.append({"type": "repository", "query": query, "page": page, "count": len(items)})
                for repo in items:
                    name = repo.get("full_name")
                    if name:
                        repos[name] = repo_record(repo)
                if len(items) < per_page:
                    break
                time.sleep(1.0)
            except Exception as exc:
                warnings.append(f"repository query {query!r} page {page}: {exc}")
                break

    for query in gh.get("code_queries", ["filename:SKILL.md"]):
        for page in range(1, max_pages + 1):
            try:
                result = api_get("/search/code", {
                    "q": query, "per_page": per_page, "page": page,
                })
                items = result.get("items", [])
                query_log.append({"type": "code", "query": query, "page": page, "count": len(items)})
                for item in items:
                    repo = item.get("repository") or {}
                    name = repo.get("full_name")
                    path = item.get("path")
                    if not name or not path:
                        continue
                    if name not in repos:
                        repos[name] = repo_record(repo)
                    key = f"{name}:{path}"
                    skills[key] = {
                        "skill_id": key, "repo_full_name": name,
                        "repo_url": repo.get("html_url"), "skill_path": path,
                        "skill_url": item.get("html_url"),
                        "name": Path(path).parent.name if Path(path).parent.name != "." else name.split("/")[-1],
                        "stars": int(repo.get("stargazers_count") or 0),
                        "forks": int(repo.get("forks_count") or 0),
                        "description": repo.get("description") or "",
                        "created_at": repo.get("created_at"), "updated_at": repo.get("updated_at"),
                        "pushed_at": repo.get("pushed_at"),
                        "license": (repo.get("license") or {}).get("spdx_id"),
                        "topics": repo.get("topics") or [],
                    }
                if len(items) < per_page:
                    break
                time.sleep(1.0)
            except Exception as exc:
                warnings.append(f"code query {query!r} page {page}: {exc}")
                break

    skill_repos = {s["repo_full_name"] for s in skills.values()}
    snapshot = {
        "date_utc": today_utc(),
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "GitHub public Search API",
        "coverage_note": "Discovered sample only; GitHub search is not an exhaustive census.",
        "queries": query_log, "warnings": warnings,
        "repository_count": len(repos), "skill_repository_count": len(skill_repos),
        "repository_candidates": [
            {"repo_full_name": name, **repo, "has_indexed_skill_file": name in skill_repos}
            for name, repo in repos.items()
        ],
        "skill_candidate_count": len(skills), "skills": list(skills.values()),
    }
    save_json(CURRENT, snapshot)
    print(f"Collected {len(skills)} Skill candidates from {len(repos)} repositories.")
    if warnings:
        print(f"Warnings: {len(warnings)}; see data/current.json")


if __name__ == "__main__":
    main()
