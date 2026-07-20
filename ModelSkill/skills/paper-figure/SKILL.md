---
name: paper-figure
description: "Publication-quality figures for papers using Python/matplotlib, plus schematic/flow diagrams (mermaid or TikZ). Produces clean vector/high-DPI charts with consistent fonts, sizing for single/double column, and colorblind-safe palettes; exports PDF/PNG/SVG. 论文级作图：用 matplotlib 出版级图表、流程图/示意图(mermaid/TikZ)，统一字体配色、按单双栏调尺寸、导出 PDF/PNG/SVG。Triggers on: plot, figure, chart, visualization, matplotlib, 画图, 作图, 配图, 论文图, 可视化, 流程图, 示意图, 折线图, 柱状图, 散点图, 热力图。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# paper-figure — 论文作图

## 何时用
- 把数据/结果画成出版级图表（折线/柱/散点/箱线/热力/误差棒…）。
- 画流程图、模型示意图、算法框图。

## 数据图（matplotlib）
1. 用 Python + matplotlib（必要时 numpy/pandas）。先确认环境：
   `python -c "import matplotlib, numpy; print('ok')"`（缺则 `pip install matplotlib numpy`）。
2. 套用论文样式片段：见 [references/mpl-style.md](references/mpl-style.md)
   （字体、字号、线宽、栏宽尺寸、DPI、配色、导出 PDF 矢量）。
3. 导出：矢量优先 `fig.savefig('f.pdf')`；位图 `dpi=300`；透明可加 `transparent=True`。
4. 把脚本和图一起留存，方便复现（数模附录要可复现）。

## 示意/流程图
- 简单流程：mermaid（```mermaid flowchart）便于在 Obsidian/Markdown 预览。
- LaTeX 内嵌矢量：TikZ（交给 `paper-format` 放进 .tex）。

## 注意
- 图中字号与正文相近（≥ 8pt）；中文图需设中文字体避免方块（见样式片段）。
- 颜色对色盲友好，黑白打印可区分（用线型/marker 区分）。

## 衔接
- 图要进文档 → `paper-format`（LaTeX `\includegraphics` 或 Word `add_picture`）。
