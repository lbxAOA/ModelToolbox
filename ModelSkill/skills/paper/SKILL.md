---
name: paper
description: "Orchestrator for paper writing — mathematical-modeling contest papers (CUMCM 国赛 / MCM-ICM 美赛) and academic papers (journal/conference). Routes a paper task to the right sub-skill: modeling & methodology, drafting/polish/translation, figures, or formatting (LaTeX & Word) + references. Picks competition/venue mode and LaTeX-vs-Word output. 论文写作总编排：数学建模(国赛/美赛)与学术论文，路由到建模、写作润色翻译、作图、排版与参考文献子技能。Triggers on: write a paper, paper, academic paper, mathematical modeling, 写论文, 数模论文, 数学建模, 学术论文, 论文流程, 论文怎么写, 帮我写论文, cumcm, mcm, icm, 国赛, 美赛。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# paper — 论文写作编排

Routes a paper task to a specialized sub-skill. First establish two things, then route.

## 0. 先确定语境（缺啥问啥）
- **类型/模式**：数模国赛(CUMCM, 中文) / 数模美赛(MCM-ICM, 英文) / 学术论文(期刊·会议)。
- **输出工具链**：LaTeX（`.tex`）还是 Word（`.docx`，走 office-word MCP）。

## 路由表（Intent → 子技能）
| 意图 | 子技能 |
|------|--------|
| 建模思路 / 假设与符号 / 算法选择 / 模型建立求解 / 灵敏度分析 | `paper-model` |
| 成稿 / 润色 / 中英互译 / 写摘要 Abstract | `paper-write` |
| 画图 / 论文配图 / 可视化 / 流程图 | `paper-figure` |
| 套模板 / 排版 / 参考文献 / 导出 Word 或 LaTeX | `paper-format` |

## 数模论文标准结构（提醒）
摘要 → 问题重述 → 问题分析 → 模型假设 → 符号说明 → 模型建立与求解 →
模型检验/灵敏度分析 → 模型评价(优缺点) → 参考文献 → 附录(代码)。
- 国赛：中文，**摘要是评审第一关**，需含方法+结论+关键数据。
- 美赛：英文，**首页 Summary Sheet** 单独成页，强调创新与结果。

## 学术论文标准结构（提醒）
Abstract → Introduction → Related Work → Method → Experiments →
Results & Discussion → Conclusion → References。

## 用法
说明任务后，由对应子技能完成。复杂任务按"建模 → 作图 → 写作 → 排版"顺序串联，
最终用 `paper-format` 套模板/参考文献并导出（LaTeX 或 Word）。
