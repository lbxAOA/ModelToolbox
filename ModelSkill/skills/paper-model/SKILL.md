---
name: paper-model
description: "Mathematical modeling & methodology for papers: restate the problem, analyze it, state assumptions and symbol/notation tables, choose and justify algorithms/models, establish and solve the model, and run sensitivity/robustness analysis. For CUMCM/MCM-ICM contests and academic method sections. 论文建模与方法：问题重述与分析、模型假设、符号说明、算法/模型选择与论证、建立与求解、灵敏度与稳健性分析。Triggers on: modeling, methodology, build a model, 建模, 数学建模, 模型假设, 符号说明, 算法选择, 模型建立, 模型求解, 灵敏度分析, 稳健性, 问题分析, 方法部分, 选什么模型。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# paper-model — 建模与方法

帮用户把一个问题转化为可写、可求解、可检验的数学模型。

## 何时用
- 数模比赛拿到题目，要确定建模思路、假设、符号、方法。
- 学术论文写 Method 部分，需要形式化与论证。

## 步骤
1. **问题重述与分析**：用自己的话复述，拆成子问题，明确已知/未知/目标/约束。
2. **模型假设**：列出每条假设 + **理由**（数模评审看重合理性）。
3. **符号说明**：建一张符号表（符号 | 含义 | 单位），全篇统一。
4. **方法选择**：候选模型/算法对比（适用性、复杂度、数据需求），给出选择理由。
   - 常见族：优化(LP/IP/NLP/启发式)、预测(回归/时间序列/灰色/神经网络)、
     评价(AHP/TOPSIS/熵权/模糊)、图与网络、微分方程/动力学、概率统计/蒙特卡洛。
5. **建立与求解**：写出目标函数/约束/方程；说明求解器或算法（可转 `paper-figure`
   出结果图、转 Bash 跑 Python/scipy 求解）。
6. **检验**：灵敏度分析（关键参数扰动）、与基准/实际对比、误差分析。
7. **评价**：优点、缺点、可改进方向（数模必备）。

## 衔接
- 求解需要画图 → `paper-figure`；成稿/翻译 → `paper-write`；排版套模板 → `paper-format`。
- 详细方法清单见 [references/methods.md](references/methods.md)。
