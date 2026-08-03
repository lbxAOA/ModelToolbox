"""解析器注册表：插件式管理多个文档解析器。

支持按优先级调用解析器，失败时自动降级到下一个。
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

# 解析器函数类型：接收文件路径，返回 Markdown 文本或 None
ParserFunc = Callable[[Path], Optional[str]]


class ConversionError(Exception):
    """文档转换失败。"""
    pass


class ParserRegistry:
    """解析器注册表。
    
    管理所有已注册的解析器，支持按优先级调用。
    """
    
    def __init__(self):
        self._parsers: dict[str, ParserFunc] = {}
        self._priority: list[tuple[int, str]] = []  # (priority, name)
    
    def register(self, name: str, parser: ParserFunc, priority: int = 100):
        """注册解析器。
        
        Args:
            name: 解析器名称（唯一标识）
            parser: 解析函数，返回 Markdown 文本或 None（失败）
            priority: 优先级（数字越小越优先，默认 100）
        """
        self._parsers[name] = parser
        self._priority.append((priority, name))
        self._priority.sort()  # 按优先级排序
    
    def parse(
        self,
        path: Path,
        parsers: list[str] | None = None,
    ) -> tuple[str, str]:
        """使用注册的解析器解析文件。
        
        按优先级依次尝试解析器，直到成功或全部失败。
        
        Args:
            path: 文件路径
            parsers: 指定要使用的解析器列表（None 使用全部，按优先级）
        
        Returns:
            (markdown_text, parser_name) 元组
        
        Raises:
            ConversionError: 所有解析器都失败
        """
        if parsers is None:
            # 使用所有解析器，按优先级顺序
            parsers = [name for _, name in self._priority]
        
        errors = []
        
        for parser_name in parsers:
            if parser_name not in self._parsers:
                errors.append(f"解析器 '{parser_name}' 未注册")
                continue
            
            parser = self._parsers[parser_name]
            
            try:
                result = parser(path)
                if result:
                    return result, parser_name
            except Exception as e:
                errors.append(f"{parser_name}: {e}")
                continue
        
        # 所有解析器都失败
        error_msg = "\n".join(errors) if errors else "无可用解析器"
        raise ConversionError(f"无法解析文件 {path}:\n{error_msg}")
    
    def list_parsers(self) -> list[str]:
        """列出所有已注册的解析器（按优先级）。
        
        Returns:
            解析器名称列表
        """
        return [name for _, name in self._priority]
    
    def get_parser(self, name: str) -> ParserFunc | None:
        """获取指定解析器。
        
        Args:
            name: 解析器名称
        
        Returns:
            解析器函数，未找到返回 None
        """
        return self._parsers.get(name)


# 全局注册表单例
_registry = ParserRegistry()


def register_parser(name: str, priority: int = 100):
    """解析器装饰器。
    
    使用方式：
    ```python
    @register_parser("my_parser", priority=50)
    def parse_my_format(path: Path) -> Optional[str]:
        # 解析逻辑
        return markdown_text
    ```
    
    Args:
        name: 解析器名称
        priority: 优先级（越小越优先）
    """
    def decorator(func: ParserFunc) -> ParserFunc:
        _registry.register(name, func, priority)
        return func
    return decorator


# 导出统一接口
def convert_to_markdown(
    path: Path,
    parsers: list[str] | None = None,
) -> tuple[str, str]:
    """转换文件为 Markdown。
    
    Args:
        path: 文件路径
        parsers: 指定解析器优先级（None 使用默认顺序）
    
    Returns:
        (markdown_text, parser_name)
    
    Raises:
        ConversionError: 转换失败
    """
    return _registry.parse(path, parsers)


def list_parsers() -> list[str]:
    """列出所有可用解析器。"""
    return _registry.list_parsers()
