"""知识库组织器 —— 自动分类、建立索引、生成目录结构。

功能:
1. 根据内容自动分类 (按主题/标签)
2. 生成目录索引 (README.md / Index.md)
3. 建立交叉引用 (Obsidian [[wikilink]])
4. 创建主题 MOC (Map of Content)
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class NoteMetadata:
    """笔记元数据"""
    path: Path
    title: str
    tags: list[str] = field(default_factory=list)
    category: str = ""
    links: list[str] = field(default_factory=list)
    backlinks: list[str] = field(default_factory=list)


@dataclass
class OrganizeConfig:
    """知识库组织配置"""
    source_dir: Path
    output_dir: Path
    structure: str = "obsidian"  # obsidian / flat / hierarchical
    domain: str = "通用"
    create_index: bool = True
    create_moc: bool = True
    auto_categorize: bool = True


class KnowledgeOrganizer:
    """知识库组织器"""

    def __init__(self, config: OrganizeConfig):
        self.config = config
        self.notes: dict[str, NoteMetadata] = {}
        self.categories: dict[str, list[str]] = defaultdict(list)

    def organize(self) -> dict:
        """执行组织流程"""
        stats = {
            "total_notes": 0,
            "categories": 0,
            "links_created": 0,
            "mocs_created": 0,
        }

        # 1. 扫描所有笔记
        self._scan_notes()
        stats["total_notes"] = len(self.notes)

        # 2. 自动分类
        if self.config.auto_categorize:
            self._categorize_notes()
            stats["categories"] = len(self.categories)

        # 3. 提取链接
        self._extract_links()
        stats["links_created"] = sum(len(n.links) for n in self.notes.values())

        # 4. 重组目录结构
        self._reorganize_structure()

        # 5. 生成索引
        if self.config.create_index:
            self._generate_index()

        # 6. 生成 MOC
        if self.config.create_moc:
            moc_count = self._generate_mocs()
            stats["mocs_created"] = moc_count

        return stats

    def _scan_notes(self):
        """扫描所有笔记文件"""
        for md_file in self.config.source_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue

            rel_path = md_file.relative_to(self.config.source_dir)
            content = md_file.read_text(encoding="utf-8", errors="ignore")

            metadata = self._parse_metadata(md_file, content)
            self.notes[str(rel_path)] = metadata

    def _parse_metadata(self, path: Path, content: str) -> NoteMetadata:
        """解析笔记元数据"""
        # 提取标题
        title = path.stem
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

        # 提取 frontmatter 中的标签
        tags = []
        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            fm_content = frontmatter_match.group(1)
            tags_match = re.search(r"tags:\s*\[(.*?)\]", fm_content)
            if tags_match:
                tags = [t.strip().strip('"\'') for t in tags_match.group(1).split(",")]

        # 提取内容中的标签
        inline_tags = re.findall(r"#(\w+)", content)
        tags.extend(inline_tags)
        tags = list(set(tags))  # 去重

        return NoteMetadata(
            path=path,
            title=title,
            tags=tags,
        )

    def _categorize_notes(self):
        """自动分类笔记"""
        # 基于领域的分类规则
        domain_rules = self._get_domain_rules()

        for rel_path, note in self.notes.items():
            category = self._classify_note(note, domain_rules)
            note.category = category
            self.categories[category].append(rel_path)

    def _get_domain_rules(self) -> dict[str, list[str]]:
        """获取领域分类规则"""
        rules = {
            "算法": {
                "keywords": ["算法", "数据结构", "动态规划", "贪心", "搜索", "图论", "字符串", "数论", "组合数学"],
                "tags": ["algorithm", "dp", "greedy", "search", "graph", "string", "math"],
            },
            "硬件": {
                "keywords": ["电路", "PCB", "原理图", "芯片", "单片机", "FPGA", "模拟", "数字"],
                "tags": ["hardware", "pcb", "circuit", "chip", "fpga"],
            },
            "数学": {
                "keywords": ["定理", "证明", "公式", "微积分", "线性代数", "概率", "统计"],
                "tags": ["math", "theorem", "proof", "calculus", "algebra"],
            },
        }

        # 使用配置的领域
        if self.config.domain in rules:
            return {self.config.domain: rules[self.config.domain]}

        return rules

    def _classify_note(self, note: NoteMetadata, rules: dict) -> str:
        """分类单个笔记"""
        content = note.path.read_text(encoding="utf-8", errors="ignore").lower()

        scores = {}
        for category, rule in rules.items():
            score = 0
            # 关键词匹配
            for keyword in rule.get("keywords", []):
                if keyword.lower() in content:
                    score += 2
            # 标签匹配
            for tag in rule.get("tags", []):
                if tag.lower() in [t.lower() for t in note.tags]:
                    score += 3
            scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return "其他"

    def _extract_links(self):
        """提取笔记间的链接关系"""
        for rel_path, note in self.notes.items():
            content = note.path.read_text(encoding="utf-8", errors="ignore")

            # 提取 [[wikilink]]
            wikilinks = re.findall(r"\[\[([^\]]+)\]\]", content)
            note.links = wikilinks

            # 建立反向链接
            for link in wikilinks:
                # 查找目标笔记
                for target_path, target_note in self.notes.items():
                    if link in target_note.title or link in str(target_note.path.stem):
                        target_note.backlinks.append(rel_path)

    def _reorganize_structure(self):
        """重组目录结构"""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        if self.config.structure == "flat":
            # 扁平结构: 所有文件放在根目录
            for rel_path, note in self.notes.items():
                src = note.path
                dst = self.config.output_dir / note.path.name
                self._copy_file(src, dst)

        elif self.config.structure == "hierarchical":
            # 分层结构: 按分类组织
            for rel_path, note in self.notes.items():
                src = note.path
                category_dir = self.config.output_dir / note.category
                category_dir.mkdir(exist_ok=True)
                dst = category_dir / note.path.name
                self._copy_file(src, dst)

        else:  # obsidian (默认)
            # Obsidian 结构: 保持原目录结构
            for rel_path, note in self.notes.items():
                src = note.path
                dst = self.config.output_dir / rel_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                self._copy_file(src, dst)

    def _copy_file(self, src: Path, dst: Path):
        """复制文件 (如果源和目标不同)"""
        if src != dst:
            import shutil
            shutil.copy2(src, dst)

    def _generate_index(self):
        """生成索引文件"""
        index_path = self.config.output_dir / "INDEX.md"

        lines = [
            f"# 知识库索引",
            f"",
            f"**领域**: {self.config.domain}",
            f"**笔记总数**: {len(self.notes)}",
            f"**分类数**: {len(self.categories)}",
            f"",
            f"## 目录",
            f"",
        ]

        # 按分类列出
        for category in sorted(self.categories.keys()):
            notes = self.categories[category]
            lines.append(f"### {category} ({len(notes)})")
            lines.append("")

            for rel_path in sorted(notes):
                note = self.notes[rel_path]
                # 生成相对链接
                link_path = rel_path.replace("\\", "/")
                lines.append(f"- [[{note.title}]]")

            lines.append("")

        index_path.write_text("\n".join(lines), encoding="utf-8")

    def _generate_mocs(self) -> int:
        """生成主题 MOC (Map of Content)"""
        moc_dir = self.config.output_dir / "MOCs"
        moc_dir.mkdir(exist_ok=True)

        moc_count = 0

        # 为每个分类生成 MOC
        for category, note_paths in self.categories.items():
            if len(note_paths) < 3:  # 少于3个笔记不生成 MOC
                continue

            moc_path = moc_dir / f"{category}.md"

            lines = [
                f"# {category} - Map of Content",
                f"",
                f"本主题包含 {len(note_paths)} 个笔记。",
                f"",
                f"## 核心笔记",
                f"",
            ]

            # 按链接数排序 (最多链接的是核心笔记)
            sorted_notes = sorted(
                note_paths,
                key=lambda p: len(self.notes[p].links) + len(self.notes[p].backlinks),
                reverse=True
            )

            for rel_path in sorted_notes[:10]:  # 只列前10个核心笔记
                note = self.notes[rel_path]
                link_count = len(note.links) + len(note.backlinks)
                lines.append(f"- [[{note.title}]] ({link_count} 个链接)")

            lines.append("")
            lines.append("## 所有笔记")
            lines.append("")

            for rel_path in sorted(note_paths):
                note = self.notes[rel_path]
                lines.append(f"- [[{note.title}]]")

            moc_path.write_text("\n".join(lines), encoding="utf-8")
            moc_count += 1

        return moc_count


def organize_knowledge_base(config: OrganizeConfig) -> dict:
    """组织知识库的便捷函数"""
    organizer = KnowledgeOrganizer(config)
    return organizer.organize()
