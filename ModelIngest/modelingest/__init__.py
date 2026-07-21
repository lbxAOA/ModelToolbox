"""
ModelIngest
本模块目的是完成知识库的构建
共含两部分分别完成：
1. 原始文档 → Markdown 语料转换（阶段 A）
2. Markdown 语料 → 结构化知识库蒸馏（阶段 B）

对于第一部分，主要是将原始文档（PDF、Word、Excel、PPT、图片等）转换为 Markdown 语料，方便后续的知识库构建。
对于第二部分，主要是把阶段 A 产出的 Markdown 语料蒸馏成带 [[wikilink]] + MOC 的结构化原子笔记知识库
（vault），供下游 ``ModelMCP/obsidian-rag-mcp`` 做向量化 embedding 与检索索引——
**向量化/索引构建本身不属于 ModelIngest 的职责，由 obsidian-rag-mcp 单独完成**。

为完成知识库的构建：
1.对于在互联网中的公开资料（wiki），先用 ``modelingest discover`` 提供根网址发现分支页面目录
（只发现不落盘），用户确认要抓取的范围后，再用 ``modelingest crawl`` 抓取到本地，
最后用 ``modelingest run`` 转换成 Markdown 语料。
2.对于本地的原始文档，先用 ``modelingest scan`` 预览会被转换的文件清单（不落盘），
用户确认后用 ``modelingest run --include <相对路径>...`` 只转换选中文件（也可以不预览，
直接对整个目录跑 ``run``）。
3.原始文档转换为 Markdown 语料会按照原始文档的目录结构进行存储。
4.对于 Markdown 语料，用户需提供一个知识库(vault)输出目录（``modelingest distill --output``）；
上层（如 webui）可以只让用户填一个知识库名称，再拼接成完整路径传给 CLI。
5.在正式蒸馏前，本工具会通过 ``modelingest guideline`` 问几个问题来了解用户对这个知识库的需求：

   - 这个知识库的领域/用途是什么？（如：算法竞赛、电路板设计、通用笔记）
   - 主要使用场景是？（自己复习查阅 / AI 检索问答 RAG / 用作模型训练语料 / 以上都要）
   - 笔记粒度偏好？（高度原子化 / 适度合并 / 保留较长上下文）
   - 笔记语言风格？（纯中文 / 纯英文 / 中英混合）
   - 是否需要完整保留原文中的公式/代码片段？
   - 还有其它特殊要求吗？（可留空）

6.根据用户的回答，工具会在 ``<知识库目录>/.ingest_meta/GUIDELINE.md`` 生成一份知识库准则
（也可直接手动编辑该文件调整规则，无需重新回答问题）。``modelingest distill`` 时会自动探测
并把这份准则连同 Markdown 语料一起交给模型，模型可以是本地 Ollama，也可以是通过
``ModelProvider`` 配置的闭源模型（用 ``--role``/``--model`` 指定），用户可自由选择。
7.如果用户选择使用闭源模型来处理问题，只需通过 ``--model provider:model`` 覆盖默认的
``teacher`` 角色，``distill`` 会把知识库准则和 Markdown 语料一并提供给该闭源模型，
自动完成结构化知识库（vault）的构建；后续再用 ``modelingest make-skill`` 可以为这个知识库
自动生成一个 ``ModelSkill`` 检索技能，指引如何切到 ``obsidian-rag-mcp`` 做向量化检索。
"""

__version__ = "0.1.0"

