"""配置系统：统一管道配置管理。

支持 Python 对象配置 + 可选 YAML 文件配置。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class StageConfig:
    """单个阶段配置。"""
    
    enabled: bool = True
    """是否启用此阶段"""
    
    config: dict[str, Any] = field(default_factory=dict)
    """阶段特定配置"""


@dataclass
class IngestConfig:
    """ModelIngest 统一配置类。
    
    支持从 Python 代码直接构造，或从 YAML 文件加载。
    """
    
    version: str = "2.0"
    """配置版本"""
    
    # ---- 输入源配置 ----
    source_type: Literal["local", "web"] = "local"
    """输入类型：local（本地文件/目录）或 web（网页 URL）"""
    
    source_path: Path = Path("./raw_docs")
    """输入路径或 URL"""
    
    # ---- 管道阶段配置 ----
    stages: list[str] = field(default_factory=lambda: ["parse", "clean"])
    """要执行的阶段列表（按顺序）"""
    
    stage_configs: dict[str, StageConfig] = field(default_factory=dict)
    """各阶段的详细配置"""
    
    # ---- 输出配置 ----
    output_root: Path = Path("./knowledge_base")
    """输出知识库根目录"""
    
    manifest_path: Path = Path("./.ingest_cache/manifest.sqlite")
    """Manifest 数据库路径（相对 output_root 或绝对路径）"""
    
    overwrite: bool = False
    """是否覆盖已存在的文件"""
    
    # ---- 性能配置 ----
    max_workers: int = 4
    """并行处理的最大工作线程数"""
    
    batch_size: int = 10
    """批量处理的批次大小"""
    
    timeout: int = 1800
    """单个文件处理超时（秒）"""
    
    @classmethod
    def from_yaml(cls, path: Path) -> IngestConfig:
        """从 YAML 文件加载配置。
        
        Args:
            path: YAML 配置文件路径
        
        Returns:
            IngestConfig 实例
        
        Raises:
            ImportError: yaml 包未安装
            FileNotFoundError: 配置文件不存在
        """
        if not YAML_AVAILABLE:
            raise ImportError(
                "需要安装 pyyaml 才能加载 YAML 配置：pip install pyyaml"
            )
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        config = cls()
        
        # 解析输入源
        if "source" in data:
            source = data["source"]
            config.source_type = source.get("type", "local")
            config.source_path = Path(source.get("path", "./raw_docs"))
        
        # 解析管道配置
        if "pipeline" in data:
            pipeline = data["pipeline"]
            config.stages = pipeline.get("stages", config.stages)
            
            # 解析各阶段配置
            for stage_name, stage_data in pipeline.items():
                if stage_name != "stages" and isinstance(stage_data, dict):
                    config.stage_configs[stage_name] = StageConfig(
                        enabled=stage_data.get("enabled", True),
                        config=stage_data,
                    )
        
        # 解析输出配置
        if "output" in data:
            output = data["output"]
            config.output_root = Path(output.get("root", "./knowledge_base"))
            config.manifest_path = Path(
                output.get("manifest_path", "./.ingest_cache/manifest.sqlite")
            )
            config.overwrite = output.get("overwrite", False)
        
        # 解析性能配置
        if "performance" in data:
            perf = data["performance"]
            config.max_workers = perf.get("max_workers", 4)
            config.batch_size = perf.get("batch_size", 10)
            config.timeout = perf.get("timeout", 1800)
        
        return config
    
    def to_yaml(self, path: Path):
        """导出为 YAML 配置文件。
        
        Args:
            path: 输出文件路径
        
        Raises:
            ImportError: yaml 包未安装
        """
        if not YAML_AVAILABLE:
            raise ImportError(
                "需要安装 pyyaml 才能导出 YAML 配置：pip install pyyaml"
            )
        
        data = {
            "version": self.version,
            "source": {
                "type": self.source_type,
                "path": str(self.source_path),
            },
            "pipeline": {
                "stages": self.stages,
                **{
                    name: cfg.config
                    for name, cfg in self.stage_configs.items()
                }
            },
            "output": {
                "root": str(self.output_root),
                "manifest_path": str(self.manifest_path),
                "overwrite": self.overwrite,
            },
            "performance": {
                "max_workers": self.max_workers,
                "batch_size": self.batch_size,
                "timeout": self.timeout,
            }
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
    
    def get_stage_config(self, stage_name: str) -> StageConfig:
        """获取特定阶段的配置。
        
        Args:
            stage_name: 阶段名称
        
        Returns:
            StageConfig（不存在则返回默认配置）
        """
        return self.stage_configs.get(stage_name, StageConfig())
    
    def enable_stage(self, stage_name: str, config: dict[str, Any] | None = None):
        """启用指定阶段。
        
        Args:
            stage_name: 阶段名称
            config: 阶段配置（可选）
        """
        if stage_name not in self.stages:
            self.stages.append(stage_name)
        
        self.stage_configs[stage_name] = StageConfig(
            enabled=True,
            config=config or {},
        )
    
    def disable_stage(self, stage_name: str):
        """禁用指定阶段。
        
        Args:
            stage_name: 阶段名称
        """
        if stage_name in self.stages:
            self.stages.remove(stage_name)
        
        if stage_name in self.stage_configs:
            self.stage_configs[stage_name].enabled = False
