"""管道编排器：统一调度和执行各阶段。

负责阶段注册、依赖验证、顺序执行和错误处理。
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from .config import IngestConfig
from .contracts import StageInput, StageOutput, PipelineStage, StageError


class PipelineOrchestrator:
    """管道编排器。
    
    负责加载、验证和执行管道各阶段。
    """
    
    def __init__(self, config: IngestConfig):
        """初始化编排器。
        
        Args:
            config: 管道配置
        """
        self.config = config
        self.stages: dict[str, PipelineStage] = {}
        self._register_stages()
    
    def _register_stages(self):
        """注册所有可用阶段。
        
        动态加载各阶段包，失败的阶段会被跳过（稍后验证时报错）。
        """
        stage_modules = {
            "render": "modelingest_render.stage",
            "fetch": "modelingest_fetch.stage",
            "parse": "modelingest_parse.stage",
            "clean": "modelingest_clean.stage",
            "distill": "modelingest_distill.stage",
            "organize": "modelingest_organize.stage",
        }
        
        for stage_name, module_path in stage_modules.items():
            try:
                module = importlib.import_module(module_path)
                # 约定：每个阶段模块导出一个名为 {Stage}Stage 的类
                # 例如：RenderStage, ParseStage, CleanStage
                class_name = f"{stage_name.capitalize()}Stage"
                stage_class = getattr(module, class_name)
                self.stages[stage_name] = stage_class()
            except (ImportError, AttributeError) as e:
                # 阶段包未安装或未实现，稍后验证时会报错
                pass
    
    def run(self, stages: list[str] | None = None) -> dict[str, Any]:
        """执行管道。
        
        Args:
            stages: 要执行的阶段列表（None 使用配置中的默认值）
        
        Returns:
            各阶段的统计信息字典
        
        Raises:
            StageError: 阶段执行失败
            ValueError: 阶段依赖验证失败
        """
        if stages is None:
            stages = self.config.stages
        
        # 验证阶段依赖
        self._validate_dependencies(stages)
        
        # 准备初始输入
        current_input = StageInput(
            source_path=self.config.source_path,
            metadata={},
            config=self.config.__dict__,
        )
        
        results = {}
        
        for stage_name in stages:
            stage_config = self.config.get_stage_config(stage_name)
            
            # 跳过禁用的阶段
            if not stage_config.enabled:
                print(f"⊘ 跳过禁用阶段: {stage_name}")
                continue
            
            # 获取阶段实例
            if stage_name not in self.stages:
                raise StageError(
                    stage_name,
                    f"阶段未注册（可能是依赖包未安装）"
                )
            
            stage = self.stages[stage_name]
            
            print(f"▶ 执行阶段: {stage.name}...")
            
            # 合并阶段特定配置
            stage_input = StageInput(
                source_path=current_input.source_path,
                metadata=current_input.metadata.copy(),
                config={**current_input.config, **stage_config.config},
            )
            
            # 验证输入
            if not stage.validate_input(stage_input):
                raise StageError(
                    stage_name,
                    f"输入验证失败: {stage_input.source_path}"
                )
            
            # 执行阶段
            try:
                output = stage.run(stage_input)
            except Exception as e:
                raise StageError(
                    stage_name,
                    f"执行失败: {e}",
                    details={"exception": str(e)}
                ) from e
            
            # 显示错误
            if output.errors:
                print(f"  ⚠ {len(output.errors)} 个错误:")
                for error in output.errors[:5]:  # 只显示前5个
                    print(f"    - {error}")
                if len(output.errors) > 5:
                    print(f"    ... 还有 {len(output.errors) - 5} 个错误")
            
            # 记录结果
            results[stage_name] = output.stats
            print(f"  ✓ 完成: {output.stats}")
            
            # 准备下一阶段输入
            current_input = StageInput(
                source_path=output.output_path,
                metadata=output.metadata,
                config=stage_input.config,
            )
        
        return results
    
    def _validate_dependencies(self, stages: list[str]):
        """验证阶段依赖是否可用。
        
        Args:
            stages: 待执行的阶段列表
        
        Raises:
            RuntimeError: 依赖验证失败
        """
        for stage_name in stages:
            if stage_name not in self.stages:
                raise RuntimeError(
                    f"阶段 '{stage_name}' 未注册。\n"
                    f"请安装对应的包: pip install 'modelingest[{stage_name}]'"
                )
            
            stage = self.stages[stage_name]
            
            for dep in stage.dependencies:
                if not self._is_dependency_available(dep):
                    raise RuntimeError(
                        f"阶段 '{stage_name}' 依赖 '{dep}' 不可用。\n"
                        f"请安装: pip install {dep}"
                    )
    
    def _is_dependency_available(self, dep: str) -> bool:
        """检查依赖包是否可用。
        
        Args:
            dep: 依赖包名
        
        Returns:
            True 表示依赖可用
        """
        try:
            importlib.import_module(dep.replace("-", "_"))
            return True
        except ImportError:
            return False
    
    def list_stages(self) -> dict[str, dict[str, Any]]:
        """列出所有已注册的阶段及其信息。
        
        Returns:
            阶段信息字典
        """
        info = {}
        for name, stage in self.stages.items():
            info[name] = {
                "name": stage.name,
                "dependencies": stage.dependencies,
                "available": all(
                    self._is_dependency_available(dep)
                    for dep in stage.dependencies
                ),
            }
        return info
