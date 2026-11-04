from __future__ import annotations

from common import CURRENT, load_json


def main() -> None:
    data = load_json(CURRENT)
    if not isinstance(data, dict):
        raise SystemExit("ERROR: data/current.json is missing or is not a JSON object.")

    required = ["date_utc", "collected_at_utc", "skills", "warnings", "queries"]
    missing = [key for key in required if key not in data]
    if missing:
        raise SystemExit(f"ERROR: snapshot missing required fields: {missing}")

    skills = data["skills"]
    if not isinstance(skills, list):
        raise SystemExit("ERROR: skills must be a list.")

    ids = [item.get("skill_id") for item in skills]
    if any(not item for item in ids):
        raise SystemExit("ERROR: one or more candidates have no skill_id.")
    if len(ids) != len(set(ids)):
        raise SystemExit("ERROR: duplicate skill_id values detected.")

    for item in skills:
        for metric in ("stars", "forks"):
            value = item.get(metric, 0)
            if not isinstance(value, (int, float)) or value < 0:
                raise SystemExit(f"ERROR: invalid {metric} value for {item.get('skill_id')}.")

        if item.get("star_rank") is None:
            raise SystemExit(f"ERROR: missing star_rank for {item.get('skill_id')}.")

        growth = item.get("star_growth")
        previous = item.get("previous_stars")
        if growth is not None and previous is None:
            raise SystemExit(f"ERROR: growth exists without previous metric for {item.get('skill_id')}.")

    print(
        "Snapshot validation passed: "
        f"{len(skills)} candidates, {len(data.get('warnings', []))} collector warnings."
    )
    if not skills:
        print("WARNING: zero candidates discovered; inspect query coverage and API warnings.")


if __name__ == "__main__":
    main()
