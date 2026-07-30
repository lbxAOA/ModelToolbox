"""YAML Frontmatter 管理。

为生成的 Markdown 文件添加元数据头部，用于溯源和追踪。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable


def _yaml_escape(value: str) -> str:
    """转义 YAML 特殊字符。
    
    Args:
        value: 原始字符串
    
    Returns:
        转义后的字符串
    """
    if any(c in value for c in ":#[]{}\"'\n") or value.strip() != value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


class FrontmatterManager:
    """Frontmatter 管理器。
    
    生成和解析 Markdown 文件的 YAML 头部元数据。
    """
    
    @staticmethod
    def build(
        *,
        source: str,
        sha256: str,
        converter: str,
        assets: Iterable[str] | None = None,
        converted_at: str | None = None,
        near_duplicate_of: str | None = None,
        injection_flagged: int | None = None,
    ) -> str:
        """构建 frontmatter 字符串。
        
        Args:
            source: 源文件相对路径
            sha256: 源文件 SHA256 哈希值
            converter: 使用的转换器名称
            assets: 抽取的资源文件列表（可选）
            converted_at: 转换时间（可选，默认当前时间）
            near_duplicate_of: 近似重复文件路径（可选）
            injection_flagged: 注入检测标记（可选）
        
        Returns:
            YAML frontmatter 字符串（包含前后分隔符）
        """
        timestamp = converted_at or datetime.now(timezone.utc).isoformat()
        lines = ["---"]
        
        # 基础字段
        lines.append(f"source: {_yaml_escape(source)}")
        lines.append(f"sha256: {sha256}")
        lines.append(f"converter: {converter}")
        lines.append(f"converted_at: {timestamp}")
        
        # 资源列表
        asset_list = list(assets or [])
        if asset_list:
            lines.append("assets:")
            for asset in asset_list:
                lines.append(f"  - {_yaml_escape(asset)}")
        
        # 可选字段
        if near_duplicate_of:
            lines.append(f"near_duplicate_of: {_yaml_escape(near_duplicate_of)}")
        
        if injection_flagged:
            lines.append(f"injection_flagged: {injection_flagged}")
        
        # 生成器标识
        lines.append("generator: ModelIngest v2.0")
        lines.append("---")
        
        return "\n".join(lines) + "\n\n"
    
    @staticmethod
    def extract_body(content: str) -> str:
        """从带 frontmatter 的内容中提取正文。
        
        Args:
            content: 完整内容（可能包含 frontmatter）
        
        Returns:
            正文部分
        """
        if not content.startswith("---\n"):
            return content
        
        # 查找第二个 ---
        end_marker = content.find("\n---\n", 4)
        if end_marker == -1:
            return content
        
        return content[end_marker + 5:]
    
    @staticmethod
    def parse(content: str) -> dict[str, any] | None:
        """解析 frontmatter（简单实现）。
        
        Args:
            content: 完整内容
        
        Returns:
            解析后的字典，或 None（无 frontmatter）
        """
        if not content.startswith("---\n"):
            return None
        
        end_marker = content.find("\n---\n", 4)
        if end_marker == -1:
            return None
        
        yaml_content = content[4:end_marker]
        
        # 简单解析（仅支持基础键值对）
        metadata = {}
        for line in yaml_content.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue
            
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # 去除引号
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            
            metadata[key] = value
        
        return metadata
