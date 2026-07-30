"""管道阶段契约定义。

定义所有阶段必须遵循的统一接口和数据结构。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator


@dataclass
class StageInput:
    """阶段输入数据契约。
    
    每个阶段接收的标准化输入数据。
    """
    source_path: Path
    """源路径（文件或目录）"""
    
    metadata: dict[str, Any] = field(default_factory=dict)
    """上游阶段传递的元数据"""
    
    config: dict[str, Any] = field(default_factory=dict)
    """阶段特定配置"""


@dataclass
class StageOutput:
    """阶段输出数据契约。
    
    每个阶段产生的标准化输出数据。
    """
    output_path: Path
    """输出路径（文件或目录）"""
    
    metadata: dict[str, Any] = field(default_factory=dict)
    """传递给下游阶段的元数据"""
    
    stats: dict[str, int] = field(default_factory=dict)
    """统计信息（文件数、错误数等）"""
    
    errors: list[str] = field(default_factory=list)
    """错误列表"""


class PipelineStage(ABC):
    """管道阶段基类。
    
    所有处理阶段必须继承此类并实现抽象方法。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """阶段名称（用于日志和配置）。"""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> list[str]:
        """可选依赖包列表。
        
        返回此阶段需要的 Python 包名列表（如 ['playwright', 'Pillow']）。
        编排器会在执行前验证这些依赖是否可用。
        """
        pass
    
    @abstractmethod
    def run(self, input_data: StageInput) -> StageOutput:
        """执行阶段处理。
        
        Args:
            input_data: 输入数据
        
        Returns:
            输出数据
        
        Raises:
            StageError: 阶段处理失败
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: StageInput) -> bool:
        """验证输入数据是否有效。
        
        Args:
            input_data: 待验证的输入数据
        
        Returns:
            True 表示输入有效
        """
        pass
    
    def iter_items(self, input_data: StageInput) -> Generator[Any, None, None]:
        """可选：批量处理时的迭代器。
        
        用于大规模文件处理时的增量迭代，避免一次性加载所有文件。
        
        Args:
            input_data: 输入数据
        
        Yields:
            待处理的单个项目
        
        Raises:
            NotImplementedError: 阶段不支持迭代处理
        """
        raise NotImplementedError(f"{self.name} 不支持迭代处理")


class StageError(Exception):
    """阶段处理错误。"""
    
    def __init__(self, stage_name: str, message: str, details: dict[str, Any] | None = None):
        self.stage_name = stage_name
        self.message = message
        self.details = details or {}
        super().__init__(f"[{stage_name}] {message}")
