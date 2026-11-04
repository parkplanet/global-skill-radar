from __future__ import annotations

import math
from datetime import datetime, timezone

from common import CURRENT, SNAPSHOTS, load_json, save_json, today_utc


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def previous_snapshot(current_date: str):
    paths = sorted(p for p in SNAPSHOTS.glob("*.json") if p.stem < current_date)
    return load_json(paths[-1]) if paths else None


def norm_log(values):
    logs = [math.log1p(max(0, float(v or 0))) for v in values]
    lo, hi = (min(logs), max(logs)) if logs else (0, 0)
    if hi == lo:
        return [0.0 for _ in logs]
    return [(v - lo) / (hi - lo) for v in logs]


def main():
    data = load_json(CURRENT, {})
    skills = data.get("skills", [])
    current_date = data.get("date_utc", today_utc())
    prev = previous_snapshot(current_date)
    prev_map = {s["skill_id"]: s for s in (prev or {}).get("skills", [])}
    stars_norm = norm_log([s.get("stars", 0) for s in skills])
    forks_norm = norm_log([s.get("forks", 0) for s in skills])
    now = datetime.now(timezone.utc)

    for i, skill in enumerate(skills):
        pushed = parse_date(skill.get("pushed_at"))
        age_days = max(0, (now - pushed).total_seconds() / 86400) if pushed else 3650
        recency = math.exp(-age_days / 180)
        completeness = sum(bool(skill.get(k)) for k in ("description", "license", "topics", "skill_path")) / 4
        skill["discovery_score"] = round(
            0.45 * stars_norm[i] + 0.25 * forks_norm[i] +
            0.20 * recency + 0.10 * completeness, 6
        )
        old = prev_map.get(skill["skill_id"])
        skill["previous_stars"] = old.get("stars") if old else None
        skill["star_growth"] = (skill.get("stars", 0) - old.get("stars", 0)) if old else None
        skill["first_seen"] = (old is None) if prev else False
        skill["rank_metric"] = "repository_stars"

    skills.sort(key=lambda x: (x.get("stars", 0), x.get("discovery_score", 0)), reverse=True)
    for rank, skill in enumerate(skills, 1):
        skill["star_rank"] = rank
    rising = [s for s in skills if s.get("star_growth") is not None]
    rising.sort(key=lambda x: (x.get("star_growth", 0), x.get("stars", 0)), reverse=True)
    for rank, skill in enumerate(rising, 1):
        skill["growth_rank"] = rank

    data["skills"] = skills
    data["previous_snapshot_date"] = (prev or {}).get("date_utc")
    data["rising_available"] = bool(prev)
    save_json(CURRENT, data)
    save_json(SNAPSHOTS / f"{current_date}.json", data)
    print(f"Ranked {len(skills)} candidates; historical comparison: {bool(prev)}")


if __name__ == "__main__":
    main()
