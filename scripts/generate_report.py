from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from common import CURRENT, REPORTS, load_json, today_utc


def esc(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def main():
    data = load_json(CURRENT, {})
    skills = data.get("skills", [])
    now = datetime.now(timezone.utc)
    local = now.astimezone(ZoneInfo("Asia/Shanghai"))
    top_n = 20
    lines = [
        f"# 全球 AI Agent Skill GitHub 日报 — {local:%Y-%m-%d}", "",
        f"- 采集时间：{now:%Y-%m-%d %H:%M:%S} UTC / {local:%Y-%m-%d %H:%M:%S} 北京时间",
        f"- 发现样本：{len(skills)} 个 Skill / 仓库候选",
        f"- 仓库数量：{data.get('repository_count', 0)}",
        "- 数据来源：GitHub Public Search API",
        "- 口径声明：这是 GitHub 搜索可发现的公开样本，不是全球全部 Skill 的完整普查，也不是 GitHub 官方排行榜。",
        "", "## 一、GitHub Star TOP 20", "",
        "| 排名 | Skill / 仓库 | Stars | Forks | 最近推送 | 分类 | 链接 |",
        "|---:|---|---:|---:|---|---|---|",
    ]
    for s in skills[:top_n]:
        name = esc(s.get("name") or s.get("repo_full_name"))
        link = s.get("skill_url") or s.get("repo_url") or ""
        cats = "、".join(s.get("categories", ["待分类"]))
        lines.append(
            f"| {s.get('star_rank', '-')} | {name} | {s.get('stars', 0)} | "
            f"{s.get('forks', 0)} | {esc((s.get('pushed_at') or '')[:10])} | "
            f"{esc(cats)} | [打开]({link}) |"
        )

    lines += ["", "## 二、近期增长 TOP 20", ""]
    if data.get("rising_available"):
        lines += [
            f"对比快照：{data.get('previous_snapshot_date')}", "",
            "| 排名 | Skill / 仓库 | Star 增长 | 当前 Stars | 链接 |",
            "|---:|---|---:|---:|---|",
        ]
        rising = sorted(
            [s for s in skills if s.get("star_growth") is not None],
            key=lambda x: (x.get("star_growth", 0), x.get("stars", 0)), reverse=True,
        )
        for i, s in enumerate(rising[:top_n], 1):
            link = s.get("skill_url") or s.get("repo_url") or ""
            lines.append(
                f"| {i} | {esc(s.get('name') or s.get('repo_full_name'))} | "
                f"{s.get('star_growth', 0):+d} | {s.get('stars', 0)} | [打开]({link}) |"
            )
    else:
        lines.append("尚无可比较的历史快照。至少成功运行两次后，才会生成可比的 Star 增长榜。")

    lines += ["", "## 三、新发现候选", ""]
    new_items = [s for s in skills if s.get("first_seen")]
    if not data.get("previous_snapshot_date"):
        lines.append("本次为基线快照，尚无前一日数据，暂不判断哪些候选属于新发现。")
    elif new_items:
        for s in new_items[:top_n]:
            link = s.get("skill_url") or s.get("repo_url") or ""
            lines.append(f"- [{esc(s.get('name') or s.get('repo_full_name'))}]({link}) — {s.get('stars', 0)} Stars")
    else:
        lines.append("本次没有新发现候选，或尚无历史快照。注意：首次发现不等于当天新发布。")

    lines += ["", "## 四、领域分布", ""]
    for category, count in sorted(data.get("category_counts", {}).items(), key=lambda x: x[1], reverse=True):
        lines.append(f"- {category}：{count}")

    lines += ["", "## 五、待核验的仓库发现（尚未检索到 SKILL.md）", ""]
    unverified = [r for r in data.get("repository_candidates", []) if not r.get("has_indexed_skill_file")]
    if unverified:
        for r in sorted(unverified, key=lambda x: x.get("stars", 0), reverse=True)[:20]:
            lines.append(f"- [{esc(r.get('repo_full_name'))}]({r.get('repo_url')}) — {r.get('stars', 0)} Stars；需人工核验是否包含 Skill")
    else:
        lines.append("暂无未关联到 SKILL.md 的仓库候选。")

    lines += [
        "", "## 六、数据质量与限制", "",
        f"- 查询记录：{len(data.get('queries', []))} 条。",
        f"- 采集警告：{len(data.get('warnings', []))} 条。",
        "- Star / Fork 是仓库级指标，不等于单个 Skill 的安装量、活跃用户数或专业质量。",
        "- 仓库可能包含多个 Skill；同一仓库的 Star 会出现在多个 Skill 文件候选上。",
        "- 分类为关键词启发式分类，可能存在误判。",
        "- GitHub Search API 存在索引覆盖、结果上限和速率限制；未被检索到不代表不存在。",
        "- 本项目只采集元数据，不执行第三方 Skill 代码。",
    ]
    if data.get("warnings"):
        lines += ["", "### 采集警告", ""]
        lines.extend(f"- {esc(w)}" for w in data["warnings"][:30])

    report = "\n".join(lines) + "\n"
    daily = REPORTS / "daily" / f"{local:%Y-%m-%d}.md"
    daily.parent.mkdir(parents=True, exist_ok=True)
    daily.write_text(report, encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "latest.md").write_text(report, encoding="utf-8")
    print(f"Report written: {daily}")


if __name__ == "__main__":
    main()
