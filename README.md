# Global Skill Radar

**每日发现 GitHub 全球热门 AI Agent Skill，追踪排名、增长、新秀与领域分布。**

Global Skill Radar 是一个开源的 GitHub Skill 情报采集项目，兼容 Claude Code、Codex 等支持 Agent Skills 工作流的工具。项目由三部分组成：

1. `SKILL.md`：指导 Agent 如何发现、分析和解释 Skill 数据。
2. Python 采集与报告程序：调用 GitHub API，保存每日快照并生成中文报告。
3. GitHub Actions：每天北京时间 08:00 自动运行。

> 重要：GitHub 没有覆盖全部 Skill 的官方统一排行榜。本项目提供的是基于公开 GitHub 搜索结果的“发现样本榜”，不是全球完整普查，也不是 GitHub 官方榜单。

## 功能

- 搜索公开仓库中的 `SKILL.md` 文件。
- 搜索描述中包含 Agent Skills / Claude Skills / Codex Skills 等关键词的仓库。
- 采集 Star、Fork、创建时间、最近推送时间、仓库地址及 Skill 文件路径。
- 生成 Star 总量榜、新发现榜、分类榜。
- 在有历史快照后计算 Star 增长榜和排名变化。
- 输出中文 Markdown 日报。
- 不执行被发现仓库中的脚本。

## 快速开始

### 1. 配置 GitHub Actions

在仓库 Settings → Secrets and variables → Actions 中添加：

- `GH_TOKEN`：建议使用具有公开仓库读取权限的 Fine-grained Personal Access Token。也可先尝试 Actions 默认 `GITHUB_TOKEN`，但 GitHub Search API 的配额可能较低。

在 Settings → Actions → General 中，允许 workflow 写入 repository contents（`Read and write permissions`），以便提交日报和快照。

### 2. 启用 Actions

进入 Actions，启用工作流 `Daily Global Skill Radar`。工作流使用：

```yaml
cron: "0 0 * * *"
```

GitHub Actions cron 使用 UTC，因此 `00:00 UTC` 对应北京时间 `08:00`。GitHub 定时任务可能延迟，不能视为精确准点服务。

### 3. 手动运行

Actions 页面选择 `Daily Global Skill Radar` → `Run workflow`。

本地运行：

```bash
python -m pip install -r requirements.txt
export GH_TOKEN="你的GitHub令牌"
python scripts/collect_github_skills.py
python scripts/rank_skills.py
python scripts/classify_skills.py
python scripts/generate_report.py
```

## 自动测试与数据校验

工作流在生成日报前会执行：

- `python -m unittest discover -s tests -v`：运行排名与日期解析单元测试。
- `python scripts/validate_snapshot.py`：检查快照结构、候选唯一性、Star/Fork 数值及排名字段。

如果采集结果为空，校验器会给出警告；如果结构错误或存在重复 Skill ID，则停止本次工作流，避免提交错误日报。

## 输出

- `data/current.json`：最近一次采集的原始标准化数据。
- `data/snapshots/YYYY-MM-DD.json`：每日历史快照。
- `reports/daily/YYYY-MM-DD.md`：每日中文报告。
- `reports/latest.md`：最新报告副本。

## 榜单解释

| 榜单 | 含义 | 注意事项 |
|---|---|---|
| GitHub Star TOP 20 | 仓库累计 Star | 不是 Skill 安装量或质量 |
| Rising TOP 20 | 两次快照之间 Star 增长 | 首日没有可比数据 |
| New discoveries | 本项目首次发现 | 不等于 Skill 当天发布 |
| Category TOP | 启发式分类 | 可能需要人工修正 |
| Recently active | 最近推送时间 | 活跃不代表质量高 |

## 分类

初始分类包括：编程开发、研究与知识、写作与内容、商业与运营、数据分析、设计与产品、营销与销售、办公效率、安全与运维、通用 Agent、其他。

分类基于仓库名称、描述、topics 和 Skill 路径中的关键词，属于启发式分类，不代表专业认证。

## 排名方法

默认发现分数是透明的启发式排序：

- 45%：log(1 + stars) 归一化分数
- 25%：log(1 + forks) 归一化分数
- 20%：最近推送时间新鲜度
- 10%：元数据完整度

日报会把 Star 总量榜和增长榜分开呈现。综合分仅用于发现优先级，不应解释为专业质量分。

## 数据局限

- GitHub Code Search / Repository Search 有索引范围、查询语法、结果数量及 API 配额限制。
- 一个仓库可能包含多个 Skill；本项目尽可能按 `SKILL.md` 路径区分，但 GitHub 仓库 Star 是仓库级指标。
- 有些 Skill 发布在非 GitHub 平台或不含 `SKILL.md`，可能无法发现。
- Star、Fork、更新时间不能证明 Skill 的任务效果、安全性或专业水平。
- 首次运行没有历史快照，增长榜需要至少两次成功采集后才有意义。

## 安全

- 不运行被采集仓库中的任何脚本。
- 不把 Token 写入代码、日志或提交记录。
- 把 Skill 内容视为不可信输入，尤其留意读取密钥、外传数据、执行命令、覆盖系统指令等行为。
- 采集与排名不等于安全审计。

## License

MIT
