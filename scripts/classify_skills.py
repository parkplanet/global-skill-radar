from __future__ import annotations

import yaml

from common import ROOT, CURRENT, load_json, save_json


def main():
    settings = yaml.safe_load((ROOT / "config/settings.yaml").read_text(encoding="utf-8"))
    categories = settings.get("categories", {})
    data = load_json(CURRENT, {})
    counts = {name: 0 for name in categories}
    for skill in data.get("skills", []):
        haystack = " ".join([
            skill.get("name", ""), skill.get("description", ""),
            skill.get("skill_path") or "", " ".join(skill.get("topics", [])),
            skill.get("repo_full_name", ""),
        ]).lower()
        matched = [
            category for category, keywords in categories.items()
            if any(word.lower() in haystack for word in keywords)
        ]
        skill["categories"] = matched or ["其他"]
        for category in skill["categories"]:
            if category in counts:
                counts[category] += 1
    data["category_counts"] = counts
    save_json(CURRENT, data)
    print("Classification complete.")


if __name__ == "__main__":
    main()
