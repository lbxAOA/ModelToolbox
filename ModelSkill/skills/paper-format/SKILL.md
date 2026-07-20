---
name: paper-format
description: "Typeset and assemble the final paper in LaTeX or Word, and manage references. LaTeX: apply CUMCM(国赛) / MCM-ICM(美赛) / IEEE templates, math typesetting, figures/tables, BibTeX. Word: build/edit .docx via the office-word MCP (headings, tables, pictures, convert to PDF). 论文排版与组稿：LaTeX 套国赛/美赛/IEEE 模板、公式表格、BibTeX；Word 走 office-word MCP 生成 .docx 并可转 PDF。Triggers on: format, typeset, template, references, bibliography, export to word, latex, bibtex, 排版, 套模板, 模板, 参考文献, 引用, 导出word, 转pdf, 公式排版, 国赛模板, 美赛模板, ieee模板。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# paper-format — 排版·模板·参考文献

把内容组装成符合比赛/期刊要求的成稿。先确认 **LaTeX 还是 Word**。

## LaTeX 路径
1. 选模板（拷到工作目录后填内容）：
   - 国赛 CUMCM（中文）：[templates/cumcm.tex](templates/cumcm.tex)
   - 美赛 MCM-ICM（英文，含 Summary Sheet）：[templates/mcm.tex](templates/mcm.tex)
   - 学术 IEEE（会议/期刊）：[templates/ieee.tex](templates/ieee.tex)
2. 参考文献用 BibTeX：[templates/refs.bib](templates/refs.bib)，正文 `\cite{key}`。
3. 图：`\includegraphics`（用 `paper-figure` 出的 PDF）；公式用 `equation/align`。
4. 编译（若本地装了 TeX）：`latexmk -pdf main.tex`（中文模板用 `xelatex`：
   `latexmk -xelatex main.tex`）。未装则交付 .tex + 说明用 Overleaf。

## Word 路径（office-word MCP）
用已接入的 office-word 工具直接产出 `.docx`：
- `mcp__office-word__create_document` 建文档
- `add_heading` / `add_paragraph` / `add_table` / `add_picture` 填内容
- `format_text` / `set_table_column_widths` 调样式
- `convert_to_pdf` 导出 PDF
按"标题层级 → 正文 → 图表 → 参考文献"顺序写入；图用 `paper-figure` 的 PNG。

## 参考文献规范
- 国赛/美赛：GB/T 7714 或题目要求；学术：IEEE / venue 指定。
- 统一用 BibTeX 管理，避免手工编号错乱。

## 注意
- 中文 LaTeX 用 XeLaTeX + ctex；英文模板别混中文字体。
- 投稿前查：图表编号连续、引用都被 `\cite`、页边距/字号符合要求。
