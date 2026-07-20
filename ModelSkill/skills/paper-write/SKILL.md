---
name: paper-write
description: "Drafting, polishing, and translation for papers: write sections from an outline, polish language to academic register, translate between Chinese and English (中英互译), and craft abstracts / contest Summary Sheets. Keeps terminology consistent and avoids AI-tell phrasing. 论文写作·润色·翻译：按提纲成稿、学术化润色、中英互译、写摘要/Abstract、数模 Summary Sheet。Triggers on: write section, polish, proofread, translate, abstract, 写作, 润色, 改写, 翻译, 中译英, 英译中, 写摘要, 摘要润色, summary sheet, 语言润色, 降重。"
allowed-tools: Read, Write, Edit, Grep, Glob
---

# paper-write — 写作·润色·翻译

## 何时用
- 有了模型/结果，要把要点写成规范的论文段落。
- 已有草稿要润色、降 AI 味、统一术语。
- 中英互译（国赛中文 ↔ 美赛/学术英文）。
- 写**摘要**（国赛）或 **Summary Sheet / Abstract**（美赛/学术）。

## 原则
- **先结构后语言**：每段一个主旨句，论证→证据→小结。
- **术语一致**：与符号表/模型保持同一套术语，建术语对照表再翻译。
- **学术语域**：客观、精确、可验证；少用空话和过度修饰。
- **摘要四要素**：问题 + 方法 + 关键结果(带数字) + 结论/意义。

## 摘要模板
- 国赛：针对问题一/二/三分别"建立了…模型，采用…方法，得到…结果(数据)"。
- 美赛 Summary：开头点明 approach 的新意，中段 methods+results，结尾 strengths。

## 翻译要点
- 中→英：拆长句、主动语态、术语用领域惯用词；避免直译中式表达。
- 英→中：通顺优先，专业名词保留英文或加注。

## 衔接
- 需要图 → `paper-figure`；最终套模板/参考文献/导出 → `paper-format`。
