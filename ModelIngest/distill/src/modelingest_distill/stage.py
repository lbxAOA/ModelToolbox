"""Distill 阶段实现：知识蒸馏（包装现有实现）。

将 Markdown 语料通过 LLM 蒸馏为原子笔记。
"""

from __future__ import annotations

import sys
from pathlib import Path

from modelingest_core import StageInput, StageOutput, PipelineStage, StageError


class DistillStage(PipelineStage):
    """知识蒸馏阶段。
    
    包装现有的 distill 模块实现。
    """
    
    @property
    def name(self) -> str:
        return "distill"
    
    @property
    def dependencies(self) -> list[str]:
        return []  # ModelProvider 是可选依赖
    
    def validate_input(self, input_data: StageInput) -> bool:
        """验证输入（Markdown 文件目录）。"""
        source = input_data.source_path
        return source.exists() and source.is_dir()
    
    def run(self, input_data: StageInput) -> StageOutput:
        """执行知识蒸馏。
        
        配置参数：
        - profile: 蒸馏配置文件（concept/algorithm）
        - model: LLM 模型（可选）
        - role: 角色（teacher/student）
        """
        source = input_data.source_path
        config = input_data.config
        
        # 读取配置
        profile = config.get("profile", "concept")
        model = config.get("model", None)
        role = config.get("role", "teacher")
        
        output_root = Path(config.get("output_root", "./output"))
        
        stats = {"distilled": 0, "notes": 0, "skipped": 0, "errors": 0}
        errors = []
        
        try:
            # 导入现有的 distill 模块
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "modelingest"))
            from modelingest.distill import run, DistillConfig
            
            # 配置
            distill_config = DistillConfig(
                source_root=source,
                vault_root=output_root,
                profile=profile,
                role=role,
                model=model,
                do_link=False,  # 链接由 organize 阶段处理
            )
            
            # 执行蒸馏
            summary = run(distill_config)
            
            stats["distilled"] = summary.distilled
            stats["notes"] = summary.notes
            stats["skipped"] = summary.skipped
            stats["errors"] = summary.failed
            errors.extend(summary.errors)
        
        except ImportError as e:
            errors.append(f"无法导入 distill 模块: {e}")
            errors.append("提示：确保已安装 ModelProvider")
            stats["errors"] = 1
        
        except Exception as e:
            errors.append(f"蒸馏失败: {e}")
            stats["errors"] = 1
        
        return StageOutput(
            output_path=output_root,
            metadata={},
            stats=stats,
            errors=errors,
        )
