"""Clean 阶段实现：内容清洗（去噪、质量过滤）。

清理 Markdown 中的多余空白、无用元素等。
"""

from __future__ import annotations

from pathlib import Path
import re

from modelingest_core import StageInput, StageOutput, PipelineStage
from modelingest_common import FrontmatterManager


class CleanStage(PipelineStage):
    """内容清洗阶段。"""
    
    @property
    def name(self) -> str:
        return "clean"
    
    @property
    def dependencies(self) -> list[str]:
        return []
    
    def validate_input(self, input_data: StageInput) -> bool:
        """验证输入。"""
        return input_data.source_path.exists()
    
    def run(self, input_data: StageInput) -> StageOutput:
        """执行清洗。
        
        配置参数：
        - clean_html: 清理残留 HTML 标签
        - normalize_whitespace: 规范化空白字符
        - remove_empty_lines: 移除多余空行
        """
        source = input_data.source_path
        config = input_data.config
        
        clean_html = config.get("clean_html", True)
        normalize_ws = config.get("normalize_whitespace", True)
        remove_empty = config.get("remove_empty_lines", True)
        
        stats = {"files": 0, "cleaned": 0}
        errors = []
        
        # 收集 Markdown 文件
        if source.is_file() and source.suffix == ".md":
            files = [source]
        else:
            files = list(source.rglob("*.md"))
        
        stats["files"] = len(files)
        
        for md_file in files:
            try:
                # 读取文件
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 提取 frontmatter 和正文
                body = FrontmatterManager.extract_body(content)
                
                # 清洗正文
                cleaned = body
                
                if clean_html:
                    # 移除残留 HTML 标签
                    cleaned = re.sub(r"<[^>]+>", "", cleaned)
                
                if normalize_ws:
                    # 规范化空白字符
                    cleaned = re.sub(r"[ \t]+", " ", cleaned)
                
                if remove_empty:
                    # 移除多余空行（保留最多一个）
                    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
                
                # 如果有变化，写回文件
                if cleaned != body:
                    # 保留 frontmatter
                    frontmatter = content[:len(content) - len(body)]
                    
                    with open(md_file, "w", encoding="utf-8") as f:
                        f.write(frontmatter)
                        f.write(cleaned)
                    
                    stats["cleaned"] += 1
            
            except Exception as e:
                errors.append(f"{md_file.name}: {e}")
        
        return StageOutput(
            output_path=source,  # 原地清洗
            metadata={},
            stats=stats,
            errors=errors,
        )
