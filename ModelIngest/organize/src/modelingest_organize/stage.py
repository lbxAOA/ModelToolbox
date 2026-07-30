"""Organize 阶段实现：知识库组织（包装现有实现）。

建立 wikilink、生成 MOC、自动分类。
"""

from __future__ import annotations

import sys
from pathlib import Path

from modelingest_core import StageInput, StageOutput, PipelineStage


class OrganizeStage(PipelineStage):
    """知识库组织阶段。
    
    包装现有的 linker 和 organizer 实现。
    """
    
    @property
    def name(self) -> str:
        return "organize"
    
    @property
    def dependencies(self) -> list[str]:
        return []
    
    def validate_input(self, input_data: StageInput) -> bool:
        """验证输入（笔记目录）。"""
        source = input_data.source_path
        return source.exists() and source.is_dir()
    
    def run(self, input_data: StageInput) -> StageOutput:
        """执行知识库组织。
        
        配置参数：
        - create_moc: 生成 MOC（默认 True）
        - auto_categorize: 自动分类（默认 True）
        """
        source = input_data.source_path
        config = input_data.config
        
        create_moc = config.get("create_moc", True)
        auto_categorize = config.get("auto_categorize", True)
        
        stats = {"links": 0, "mocs": 0, "categories": 0}
        errors = []
        
        try:
            # 导入现有模块
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "modelingest"))
            
            # 1. 建立 wikilink
            from modelingest.distill import link_only
            link_summary = link_only(source)
            stats["links"] = link_summary.get("links_created", 0)
            
            # 2. 生成 MOC 和分类
            if create_moc or auto_categorize:
                from modelingest.organizer import KnowledgeOrganizer, OrganizeConfig
                
                org_config = OrganizeConfig(
                    source_dir=source,
                    output_dir=source,  # 原地组织
                    create_moc=create_moc,
                    auto_categorize=auto_categorize,
                )
                
                organizer = KnowledgeOrganizer(org_config)
                org_stats = organizer.organize()
                
                stats["mocs"] = org_stats.get("mocs_created", 0)
                stats["categories"] = org_stats.get("categories", 0)
        
        except ImportError as e:
            errors.append(f"无法导入组织模块: {e}")
        
        except Exception as e:
            errors.append(f"组织失败: {e}")
        
        return StageOutput(
            output_path=source,  # 原地组织
            metadata={},
            stats=stats,
            errors=errors,
        )
