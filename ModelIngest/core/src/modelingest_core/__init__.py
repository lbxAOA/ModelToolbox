"""ModelIngest Core：核心编排和配置包。

提供管道阶段的统一接口、配置系统和编排器。
"""

__version__ = "2.0.0"

from .contracts import StageInput, StageOutput, PipelineStage
from .config import IngestConfig, StageConfig
from .orchestrator import PipelineOrchestrator

__all__ = [
    "StageInput",
    "StageOutput",
    "PipelineStage",
    "IngestConfig",
    "StageConfig",
    "PipelineOrchestrator",
]
