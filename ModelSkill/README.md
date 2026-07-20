# ModelSkill

通过**私有 registry** 管理与路由模型技能（Skill）。

## 组成

- `skills/` — 技能库（硬件 ato / kicad / mcu、论文 paper、视频 hyperframes 等）。
- `registry/` — 可搜索的技能索引（`skills-index.json` / `SKILLS.md`）。
- `.claude-plugin/` — 技能管理插件（skill-manager）。
- `hooks/` — `UserPromptSubmit` 钩子：每个任务自动检索 registry 并注入最匹配技能。
- `commands/` — `/skill-search`、`/skill-list`、`/skill-sync`、`/skill-new`。

## 定位

ModelToolbox 的**技能管理 / 分发**层。skill-manager 本身即一个轻量路由器，
未来可扩展为「按任务选模块」的总路由，与 orchestrator 协作。

> 许可证：MIT（ModelToolbox 原创）。详见根 `LICENSES.md`。
