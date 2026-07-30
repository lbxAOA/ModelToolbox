# ModelIngest 重构方案 v2.0

> 参考 [PixelRAG](https://github.com/StarTrail-org/PixelRAG) 的模块化管道架构设计  
> **目标**：使用"视觉模型" + "逻辑模型"的创新方式提升 RAG 效果

## 用户需求确认

基于 2026-07-30 需求讨论：

- **重构动机**：传统爬虫方式 RAG 效果不佳，需要支持视觉+逻辑双模型处理
- **重构范围**：完全重构，采用独立包架构
- **核心痛点**：添加新解析器困难、配置混乱、CLI复杂、测试困难、性能问题、代码可读性差
- **架构选择**：独立包架构（如 PixelRAG）
- **配置系统**：混合方式（Python + 可选 YAML）
- **向后兼容**：可以破坏性更新
- **开发时间**：1-2天快速启动，后续迭代
- **新依赖**：可以引入

## 一、现状分析与视觉处理需求

### 1.1 当前架构

ModelIngest 当前采用**两阶段流水线**架构：

```
阶段 A (Parse): 原始文档 → Markdown 语料
  - crawler: 网页抓取
  - parsers: 多引擎解析 (mineru/docling/marker/markitdown)
  - cleaner: HTML 去噪
  - pipeline: 增量转换编排

阶段 B (Distill): Markdown 语料 → 结构化知识库
  - chunk: 文档分块
  - teacher: LLM 蒸馏
  - validate: 笔记验证
  - linker: 建立 wikilink + MOC
  - organizer: 知识库组织
```

**优点：**
- 功能完整，覆盖从原始文档到结构化知识库的全流程
- 支持多种解析引擎优先级降级
- 增量处理（基于 manifest）

**痛点：**
1. **模块耦合度高**：pipeline.py 中混合了文件遍历、转换调度、清洗逻辑
2. **配置分散**：IngestConfig、DistillConfig、BuildConfig 等配置类职责交叉
3. **难以扩展**：添加新的解析器或处理阶段需要修改多个文件
4. **测试困难**：各阶段缺乏清晰的输入输出契约
5. **CLI 复杂**：多个命令（discover/crawl/scan/run/distill）职责边界模糊

### 1.2 PixelRAG 架构特点与视觉处理启示

PixelRAG 采用**独立管道阶段**架构：

```
render → chunk → embed → build-index → serve
  ↓        ↓       ↓         ↓           ↓
独立包  独立包  独立包   独立包      独立包
```

**核心设计原则：**
1. **阶段独立性**：每个阶段是独立的 Python 包，可单独安装和使用
2. **清晰的数据契约**：阶段间通过标准数据格式（JSON/二进制）通信
3. **可选依赖**：按需安装，如 `pip install 'pixelrag[embed]'`
4. **统一编排器**：`pixelrag index` 作为高层编排，底层各阶段独立可调用
5. **配置驱动**：单一 `pixelrag.yaml` 配置文件
6. **后端可插拔**：支持 FAISS/Qdrant 等多种后端

**PixelRAG 的视觉处理启示：**
- **render 阶段**：使用 Playwright/CDP 渲染网页为截图瓦片（tiles）
- **保留视觉结构**：表格、图表、布局、信息图等视觉信息不丢失
- **视觉检索**：使用 `Qwen3-VL-Embedding` 模型进行图像向量化
- **多模态融合**：文本+图像双通道检索

ModelIngest 应借鉴这一思路，在解析阶段保留视觉信息。

## 二、重构目标

### 2.1 核心目标

1. **模块解耦**：拆分为独立 Python 包，每个阶段可单独发布和使用
2. **视觉处理能力**：新增 render 阶段，支持网页截图和视觉信息保留
3. **多模态支持**：支持文本+图像双通道解析和检索
4. **提升可扩展性**：新增解析器、处理器应该是"注册"而非"修改代码"
5. **简化配置**：Python + YAML 混合配置，清晰且灵活
6. **增强可测试性**：每个阶段都有明确的输入输出契约
7. **性能优化**：支持并行处理、批量转换

### 2.2 新增功能需求

- **视觉渲染**：使用 Playwright/CDP 渲染网页为截图瓦片
- **图像解析**：支持从 PDF/截图中提取图表、表格等视觉元素
- **多模态检索**：文本检索 + 视觉检索双通道
- **视觉模型集成**：集成 Qwen3-VL-Embedding 等视觉语言模型

### 2.3 非目标

- 不负责向量化和检索（由 ModelMCP/obsidian-rag-mcp 负责）
- 不改变知识库输出格式（Obsidian vault 结构保持）
- 不重写已稳定的底层工具（crawler 基础逻辑保留）

## 三、重构方案

### 3.1 新架构设计（独立包架构）

```
ModelIngest v2.0 架构（参考 PixelRAG 独立包设计）：

modelingest/                       # 根项目
├── pyproject.toml                 # 根项目配置
├── modelingest.yaml               # 默认配置文件模板
│
├── core/                          # 核心编排包
│   ├── pyproject.toml
│   └── src/modelingest_core/
│       ├── __init__.py
│       ├── cli.py                 # 统一 CLI 入口
│       ├── orchestrator.py        # 管道编排器
│       ├── config.py              # 配置系统
│       └── contracts.py           # 阶段契约（StageInput/Output）
│
├── render/                        # 阶段 0: 视觉渲染（新增！）
│   ├── pyproject.toml
│   └── src/modelingest_render/
│       ├── __init__.py
│       ├── stage.py               # RenderStage 实现
│       ├── screenshot.py          # 网页截图（Playwright）
│       ├── tile_generator.py      # 截图瓦片生成
│       └── pdf_renderer.py        # PDF 页面渲染
│
├── fetch/                         # 阶段 1: 内容获取
│   ├── pyproject.toml
│   └── src/modelingest_fetch/
│       ├── __init__.py
│       ├── stage.py               # FetchStage 实现
│       ├── crawler.py             # 网页爬取
│       └── local_scanner.py       # 本地文件扫描
│
├── parse/                         # 阶段 2: 格式解析
│   ├── pyproject.toml
│   └── src/modelingest_parse/
│       ├── __init__.py
│       ├── stage.py               # ParseStage 实现
│       ├── registry.py            # 解析器注册表
│       └── parsers/
│           ├── markitdown.py
│           ├── docling.py
│           ├── mineru.py
│           ├── marker.py
│           └── visual_parser.py   # 视觉解析器（新增！）
│
├── clean/                         # 阶段 3: 内容清洗
│   ├── pyproject.toml
│   └── src/modelingest_clean/
│       ├── __init__.py
│       ├── stage.py
│       ├── html_cleaner.py
│       └── optimizer.py
│
├── distill/                       # 阶段 4: 知识蒸馏
│   ├── pyproject.toml
│   └── src/modelingest_distill/
│       ├── __init__.py
│       ├── stage.py
│       ├── chunker.py
│       ├── teacher.py
│       └── validator.py
│
├── organize/                      # 阶段 5: 知识库组织
│   ├── pyproject.toml
│   └── src/modelingest_organize/
│       ├── __init__.py
│       ├── stage.py
│       ├── linker.py
│       ├── moc_generator.py
│       └── categorizer.py
│
└── common/                        # 共享工具包
    ├── pyproject.toml
    └── src/modelingest_common/
        ├── __init__.py
        ├── manifest.py            # 增量处理
        ├── frontmatter.py         # 元数据
        └── progress.py            # 进度追踪
```

**包依赖关系：**
```
core (编排器)
 ├─ depends on: common
 └─ optional: render, fetch, parse, clean, distill, organize

render → common
fetch → common
parse → common
clean → common
distill → common + parse
organize → common + distill
```

### 3.2 管道阶段设计

每个阶段遵循统一接口规范：

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

@dataclass
class StageInput:
    """阶段输入数据契约"""
    source_path: Path
    metadata: dict[str, Any]
    config: dict[str, Any]

@dataclass
class StageOutput:
    """阶段输出数据契约"""
    output_path: Path
    metadata: dict[str, Any]
    stats: dict[str, int]
    errors: list[str]

class PipelineStage(ABC):
    """管道阶段基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """阶段名称"""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> list[str]:
        """可选依赖列表"""
        pass
    
    @abstractmethod
    def run(self, input_data: StageInput) -> StageOutput:
        """执行阶段处理"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: StageInput) -> bool:
        """验证输入数据"""
        pass
    
    def iter_items(self, input_data: StageInput) -> Generator[Any, None, None]:
        """可选：批量处理时的迭代器"""
        raise NotImplementedError
```

### 3.3 配置系统重构（Python + YAML 混合）

**Python 配置类（主配置）**：

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
import yaml

@dataclass
class StageConfig:
    """单个阶段配置"""
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)

@dataclass
class IngestConfig:
    """统一配置类"""
    version: str = "2.0"
    
    # 输入源
    source_type: Literal["local", "web"] = "local"
    source_path: Path = Path("./raw_docs")
    
    # 管道阶段
    stages: list[str] = field(default_factory=lambda: ["render", "parse", "clean"])
    stage_configs: dict[str, StageConfig] = field(default_factory=dict)
    
    # 输出
    output_root: Path = Path("./knowledge_base")
    manifest_path: Path = Path("./.ingest_cache/manifest.sqlite")
    overwrite: bool = False
    
    # 性能
    max_workers: int = 4
    batch_size: int = 10
    
    @classmethod
    def from_yaml(cls, path: Path) -> "IngestConfig":
        """从 YAML 文件加载配置（可选）"""
        if not path.exists():
            return cls()
        
        with open(path) as f:
            data = yaml.safe_load(f)
        
        # 转换 YAML 数据为配置对象
        config = cls()
        
        if "source" in data:
            config.source_type = data["source"].get("type", "local")
            config.source_path = Path(data["source"].get("path", "./raw_docs"))
        
        if "pipeline" in data:
            config.stages = data["pipeline"].get("stages", config.stages)
            for stage_name, stage_data in data["pipeline"].items():
                if stage_name != "stages" and isinstance(stage_data, dict):
                    config.stage_configs[stage_name] = StageConfig(
                        enabled=stage_data.get("enabled", True),
                        config=stage_data
                    )
        
        if "output" in data:
            config.output_root = Path(data["output"].get("root", "./knowledge_base"))
            config.manifest_path = Path(data["output"].get("manifest_path", "./.ingest_cache/manifest.sqlite"))
            config.overwrite = data["output"].get("overwrite", False)
        
        return config
    
    def to_yaml(self, path: Path):
        """导出为 YAML 配置（可选）"""
        data = {
            "version": self.version,
            "source": {
                "type": self.source_type,
                "path": str(self.source_path),
            },
            "pipeline": {
                "stages": self.stages,
                **{name: cfg.config for name, cfg in self.stage_configs.items()}
            },
            "output": {
                "root": str(self.output_root),
                "manifest_path": str(self.manifest_path),
                "overwrite": self.overwrite,
            }
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def get_stage_config(self, stage_name: str) -> StageConfig:
        """获取特定阶段配置"""
        return self.stage_configs.get(stage_name, StageConfig())
```

**YAML 配置文件（可选）**：

```yaml
# modelingest.yaml - 可选配置文件
version: "2.0"

source:
  type: local  # local | web
  path: ./raw_docs

pipeline:
  stages: [render, parse, clean, distill, organize]
  
  # 视觉渲染阶段（新增！）
  render:
    enabled: true
    mode: tiles  # tiles | full | off
    tile_width: 1024
    tile_height: 1024
    overlap: 100
    formats: [png]
    dpi: 200  # PDF 渲染 DPI
  
  # 解析阶段
  parse:
    enabled: true
    parsers: [visual, mineru, docling, markitdown]  # visual 解析器优先
    extract_pdf_pages: true
    extensions: [.pdf, .docx, .xlsx, .pptx, .html, .htm, .png, .jpg]
  
  # 清洗阶段
  clean:
    enabled: true
    clean_html: true
    quality_filter: true
  
  # 蒸馏阶段
  distill:
    enabled: false
    profile: concept
    role: teacher
    model: null
  
  # 组织阶段
  organize:
    enabled: true
    structure: obsidian
    create_moc: true

output:
  root: ./knowledge_base
  manifest_path: ./.ingest_cache/manifest.sqlite
  overwrite: false

performance:
  max_workers: 4
  batch_size: 10
  timeout: 1800
```

### 3.4 编排器实现

```python
from pathlib import Path
from typing import Any

class PipelineOrchestrator:
    """管道编排器"""
    
    def __init__(self, config: IngestConfig):
        self.config = config
        self.stages: dict[str, PipelineStage] = {}
        self._register_stages()
    
    def _register_stages(self):
        """注册所有可用阶段"""
        from ingest_stages.fetch import FetchStage
        from ingest_stages.parse import ParseStage
        from ingest_stages.clean import CleanStage
        from ingest_stages.distill import DistillStage
        from ingest_stages.organize import OrganizeStage
        
        self.stages = {
            "fetch": FetchStage(),
            "parse": ParseStage(),
            "clean": CleanStage(),
            "distill": DistillStage(),
            "organize": OrganizeStage(),
        }
    
    def run(self, stages: list[str] | None = None) -> dict[str, Any]:
        """执行管道"""
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
                continue
            
            stage = self.stages[stage_name]
            
            print(f"执行阶段: {stage.name}...")
            
            # 验证输入
            if not stage.validate_input(current_input):
                raise ValueError(f"阶段 {stage_name} 输入验证失败")
            
            # 执行阶段
            output = stage.run(current_input)
            
            # 记录结果
            results[stage_name] = output.stats
            
            # 准备下一阶段输入
            current_input = StageInput(
                source_path=output.output_path,
                metadata=output.metadata,
                config=self.config.__dict__,
            )
        
        return results
    
    def _validate_dependencies(self, stages: list[str]):
        """验证阶段依赖"""
        for stage_name in stages:
            stage = self.stages[stage_name]
            for dep in stage.dependencies:
                if not self._is_dependency_available(dep):
                    raise RuntimeError(
                        f"阶段 {stage_name} 依赖 {dep} 不可用，"
                        f"请安装: pip install 'modelingest[{dep}]'"
                    )
    
    def _is_dependency_available(self, dep: str) -> bool:
        """检查依赖是否可用"""
        try:
            __import__(dep)
            return True
        except ImportError:
            return False
```

### 3.5 CLI 重构（破坏性更新，简化命令）

统一 CLI 入口，大幅简化命令：

```python
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        prog="modelingest",
        description="多模态文档 → 结构化知识库转换器",
    )
    
    # 全局选项
    parser.add_argument(
        "--config",
        type=Path,
        help="配置文件路径（可选，使用 Python API 时不需要）",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 主命令：build（推荐使用）
    build_parser = subparsers.add_parser(
        "build",
        help="执行完整构建管道",
    )
    build_parser.add_argument("--source", type=Path, required=True, help="输入目录或 URL")
    build_parser.add_argument("--output", type=Path, required=True, help="输出知识库目录")
    build_parser.add_argument("--stages", nargs="+", help="指定要执行的阶段")
    build_parser.add_argument("--visual", action="store_true", help="启用视觉渲染")
    build_parser.add_argument("--distill", action="store_true", help="启用知识蒸馏")
    build_parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的文件")
    
    # 阶段命令：render（新增！）
    render_parser = subparsers.add_parser(
        "render",
        help="渲染网页/PDF 为截图瓦片",
    )
    render_parser.add_argument("--source", type=Path, required=True)
    render_parser.add_argument("--output", type=Path, required=True)
    render_parser.add_argument("--mode", choices=["tiles", "full"], default="tiles")
    
    # 阶段命令：parse
    parse_parser = subparsers.add_parser(
        "parse",
        help="解析文档为 Markdown",
    )
    parse_parser.add_argument("--source", type=Path, required=True)
    parse_parser.add_argument("--output", type=Path, required=True)
    parse_parser.add_argument("--parsers", nargs="+", help="指定解析器优先级")
    
    # 工具命令：init（新增）
    init_parser = subparsers.add_parser(
        "init",
        help="初始化配置文件",
    )
    init_parser.add_argument("--visual", action="store_true", help="启用视觉处理")
    init_parser.add_argument("--output", type=Path, default="modelingest.yaml")
    
    args = parser.parse_args()
    
    # 执行命令
    if args.command == "build":
        from modelingest_core.orchestrator import PipelineOrchestrator
        from modelingest_core.config import IngestConfig
        
        # 加载配置
        if args.config and args.config.exists():
            config = IngestConfig.from_yaml(args.config)
        else:
            config = IngestConfig()
        
        # 命令行参数覆盖
        config.source_path = args.source
        config.output_root = args.output
        config.overwrite = args.overwrite
        
        # 动态调整阶段
        if args.visual:
            if "render" not in config.stages:
                config.stages.insert(0, "render")
        
        if args.distill:
            config.stage_configs["distill"].enabled = True
            if "distill" not in config.stages:
                config.stages.append("distill")
        
        if args.stages:
            config.stages = args.stages
        
        # 执行
        orchestrator = PipelineOrchestrator(config)
        results = orchestrator.run()
        print(f"✓ 构建完成: {results}")
    
    elif args.command == "render":
        from modelingest_render.stage import RenderStage
        from modelingest_core.contracts import StageInput
        
        stage = RenderStage()
        input_data = StageInput(
            source_path=args.source,
            metadata={},
            config={"mode": args.mode}
        )
        output = stage.run(input_data)
        print(f"✓ 渲染完成: {output.stats}")
    
    elif args.command == "init":
        from modelingest_core.config import IngestConfig
        
        config = IngestConfig()
        if args.visual:
            config.stages.insert(0, "render")
            config.stage_configs["render"] = StageConfig(enabled=True, config={
                "mode": "tiles",
                "tile_width": 1024,
                "tile_height": 1024,
            })
        
        config.to_yaml(args.output)
        print(f"✓ 配置文件已生成: {args.output}")

if __name__ == "__main__":
    main()
```

**CLI 使用示例**：

```bash
# 1. 初始化配置（启用视觉处理）
modelingest init --visual --output kb.yaml

# 2. 完整构建（视觉 + 文本双通道）
modelingest build --source ./docs --output ./kb --visual --distill

# 3. 只执行视觉渲染
modelingest render --source ./webpage.html --output ./tiles --mode tiles

# 4. 自定义阶段组合
modelingest build --source ./docs --output ./kb --stages render parse distill
```

### 3.6 解析器注册系统

将现有的 parsers.py 改造为注册表模式：

```python
from typing import Callable, Optional
from pathlib import Path

ParserFunc = Callable[[Path], Optional[str]]

class ParserRegistry:
    """解析器注册表"""
    
    def __init__(self):
        self._parsers: dict[str, ParserFunc] = {}
        self._priority: list[str] = []
    
    def register(self, name: str, parser: ParserFunc, priority: int = 100):
        """注册解析器
        
        Args:
            name: 解析器名称
            parser: 解析函数，返回 md 文本或 None
            priority: 优先级（数字越小越优先）
        """
        self._parsers[name] = parser
        self._priority.append((priority, name))
        self._priority.sort()
    
    def parse(self, path: Path, parsers: list[str] | None = None) -> tuple[str, str]:
        """使用注册的解析器解析文件
        
        Args:
            path: 文件路径
            parsers: 指定解析器优先级（None 使用默认顺序）
        
        Returns:
            (markdown_text, parser_name)
        
        Raises:
            ConversionError: 所有解析器都无法处理
        """
        if parsers is None:
            parsers = [name for _, name in self._priority]
        
        for name in parsers:
            if name not in self._parsers:
                continue
            
            parser = self._parsers[name]
            try:
                result = parser(path)
                if result:
                    return result, name
            except Exception:
                continue
        
        raise ConversionError(f"无法转换文件: {path}")
    
    def list_parsers(self) -> list[str]:
        """列出所有已注册解析器"""
        return [name for _, name in self._priority]

# 全局注册表
_registry = ParserRegistry()

def register_parser(name: str, priority: int = 100):
    """解析器装饰器"""
    def decorator(func: ParserFunc) -> ParserFunc:
        _registry.register(name, func, priority)
        return func
    return decorator

# 使用装饰器注册解析器
@register_parser("markitdown", priority=100)
def parse_markitdown(path: Path) -> Optional[str]:
    # 实现...
    pass

@register_parser("docling", priority=50)
def parse_docling(path: Path) -> Optional[str]:
    # 实现...
    pass

@register_parser("mineru", priority=30)
def parse_mineru(path: Path) -> Optional[str]:
    # 实现...
    pass

# 导出统一接口
def convert_to_markdown(path: Path, parsers: list[str] | None = None) -> tuple[str, str]:
    return _registry.parse(path, parsers)
```

## 四、实施计划（1-2天快速启动）

### 4.1 Day 1: 核心基础设施（6-8小时）

**上午（3-4小时）：搭建独立包结构**

```bash
# 1. 创建独立包目录结构
mkdir -p {core,render,fetch,parse,clean,distill,organize,common}/src
mkdir -p {core,render,fetch,parse,clean,distill,organize,common}/tests

# 2. 为每个包创建 pyproject.toml
# 核心包依赖最少，其他包依赖 common + core
```

- [ ] 创建所有包的 `pyproject.toml`（设置依赖关系）
- [ ] 实现 `modelingest_common`（manifest, progress, frontmatter）
- [ ] 实现 `modelingest_core.contracts`（StageInput/Output, PipelineStage）
- [ ] 实现 `modelingest_core.config`（IngestConfig + YAML 加载）

**下午（3-4小时）：实现核心阶段**

- [ ] 实现 `render` 阶段（新增视觉处理）
  - 使用 Playwright 渲染网页截图
  - 支持 PDF 页面转图像
  - 生成瓦片（tiles）
- [ ] 迁移 `parse` 阶段（改造为注册表模式）
  - 实现解析器注册表
  - 新增 visual_parser（处理图像）
  - 保留现有解析器适配
- [ ] 实现 `fetch` 阶段（简化现有 crawler）

**预期产出**：
- 完整的包结构
- 可运行的 render + parse 管道
- 基础配置系统

---

### 4.2 Day 2: 编排器与集成（6-8小时）

**上午（3-4小时）：编排器实现**

- [ ] 实现 `PipelineOrchestrator`
  - 阶段注册与发现
  - 依赖验证
  - 管道执行与错误处理
- [ ] 实现 CLI 入口（`modelingest build`）
- [ ] 迁移 `clean` 阶段
- [ ] 迁移 `distill` 阶段（保持现有逻辑）

**下午（3-4小时）：测试与文档**

- [ ] 端到端测试（本地文档 → 知识库）
- [ ] 视觉处理测试（网页截图 → 图像解析）
- [ ] 编写快速开始文档
- [ ] 性能基准测试

**预期产出**：
- 完整可用的 ModelIngest v2.0
- 视觉+文本双通道处理能力
- 基础文档和示例

---

### 4.3 后续迭代（可选，按需进行）

**Week 2: 高级功能**
- 视觉模型集成（Qwen3-VL-Embedding）
- 并行处理优化
- 增量更新优化

**Week 3: 多模态检索**
- 与 obsidian-rag-mcp 集成
- 文本+图像双向量检索
- 检索性能评估

**Week 4: 生态完善**
- 插件系统（第三方解析器）
- WebUI 集成
- 完整文档和教程

### 4.4 风险与缓解

| 风险项 | 影响 | 概率 | 缓解措施 |
|--------|------|------|----------|
| 1-2天完成难度大 | 高 | 中 | 优先实现核心功能，后续功能可迭代 |
| 视觉处理性能问题 | 中 | 中 | 并行渲染，可选禁用视觉处理 |
| 独立包管理复杂 | 中 | 低 | 使用 uv/poetry 工作空间管理 |
| Playwright 依赖重 | 低 | 高 | 设为可选依赖，提供降级方案 |

## 五、预期收益

### 5.1 核心能力提升

- **视觉处理能力**：新增网页截图、图像解析，保留视觉信息
- **多模态支持**：文本+图像双通道，提升 RAG 检索效果
- **模块化架构**：独立包设计，易于扩展和维护
- **性能优化**：并行处理、批量转换、增量更新

### 5.2 开发体验改善

- **清晰的阶段边界**：每个阶段独立、可测试、可替换
- **灵活的管道组合**：可以任意组合阶段（如只执行 render + parse）
- **简化的配置**：Python + YAML 混合，既灵活又直观
- **插件生态**：第三方可以轻松贡献新的解析器或处理阶段

### 5.3 RAG 效果提升

对比传统爬虫方式：

| 维度 | 传统方式 | 视觉+逻辑方式（本方案） |
|------|----------|----------------------|
| 表格识别 | ❌ 丢失结构 | ✅ 完整保留 |
| 图表理解 | ❌ 无法解析 | ✅ 视觉模型识别 |
| 布局信息 | ❌ HTML 扁平化 | ✅ 截图保留布局 |
| 多栏文本 | ❌ 顺序错乱 | ✅ 视觉模型正确排序 |
| 检索准确率 | 中 | 高（文本+图像双通道） |

### 5.4 功能增强

- **管道灵活性**：可以任意组合阶段，如只执行 parse + clean
- **批处理优化**：支持并行处理，提升大规模转换性能
- **错误恢复**：阶段失败可以从断点继续，不需重新开始
- **插件生态**：第三方可以轻松贡献新的解析器或处理阶段

### 5.4 维护性提升

- **代码质量**：清晰的接口定义，减少隐式依赖
- **文档生成**：每个阶段有明确的输入输出文档
- **问题定位**：阶段独立，容易定位问题所在
- **版本升级**：各阶段可以独立升级，降低回归风险

## 六、技术栈

### 6.1 核心依赖

```toml
# core 包
[dependencies]
python = "^3.10"
pyyaml = "^6.0"  # 可选配置

# render 包
[dependencies]
playwright = "^1.40"  # 网页渲染
Pillow = "^10.0"      # 图像处理

# parse 包
[dependencies]
markitdown = "^0.0.1a2"  # 通用解析
docling = "^2.0"         # 可选：复杂 PDF
mineru = "^0.8"          # 可选：公式识别

# distill 包（依赖 ModelProvider）
[dependencies]
modelingest_common = { path = "../common" }

# 视觉模型（可选）
qwen-vl = "^0.1"  # Qwen3-VL-Embedding
```

### 6.2 可选依赖矩阵

| 功能 | 依赖包 | 安装方式 |
|------|--------|----------|
| 基础解析 | markitdown | `pip install modelingest` |
| 视觉渲染 | playwright | `pip install 'modelingest[render]'` |
| 复杂 PDF | docling/mineru | `pip install 'modelingest[parse]'` |
| 知识蒸馏 | ModelProvider | `pip install 'modelingest[distill]'` |
| 完整功能 | 以上所有 | `pip install 'modelingest[all]'` |

## 七、示例用法

### 6.1 快速开始（视觉+文本双通道）

```bash
# 1. 初始化配置（启用视觉处理）
modelingest init --visual

# 2. 构建知识库（自动渲染截图 + 解析文本）
modelingest build --source ./docs --output ./kb --visual

# 输出结构：
# kb/
# ├── .ingest_cache/           # 缓存和元数据
# │   ├── manifest.sqlite
# │   └── tiles/               # 截图瓦片
# ├── Algorithms/              # 原子笔记
# │   ├── 快速排序.md
# │   └── 二分查找.md
# └── MOC_index.md             # 索引目录
```

### 7.2 网页视觉抓取

```bash
# 1. 渲染网页为截图瓦片
modelingest render --source https://example.com --output ./tiles

# 2. 使用视觉解析器处理
modelingest build \
  --source ./tiles \
  --output ./kb \
  --stages parse clean \
  --visual
```

### 7.3 高级用法（完整知识库）

```bash
# 1. 配置文件
cat > kb.yaml << EOF
source:
  type: local
  path: ./research_papers

pipeline:
  stages: [render, parse, clean, distill, organize]
  render:
    enabled: true
    mode: tiles
    dpi: 200
  parse:
    parsers: [visual, mineru, docling]  # 视觉解析优先
  distill:
    enabled: true
    profile: algorithm

output:
  root: ./algorithm_kb
EOF

# 2. 执行构建
modelingest build --config kb.yaml
```

### 7.4 Python API 用法

```python
from pathlib import Path
from modelingest_core.orchestrator import PipelineOrchestrator
from modelingest_core.config import IngestConfig, StageConfig

# 配置管道
config = IngestConfig(
    source_path=Path("./docs"),
    output_root=Path("./kb"),
    stages=["render", "parse", "clean", "distill"],
    stage_configs={
        "render": StageConfig(enabled=True, config={"mode": "tiles"}),
        "distill": StageConfig(enabled=True, config={"profile": "concept"}),
    }
)

# 执行构建
orchestrator = PipelineOrchestrator(config)
results = orchestrator.run()

print(f"处理完成: {results}")
# 输出: {'render': {'tiles': 120}, 'parse': {'files': 45}, ...}
```

## 七、总结

本重构方案借鉴 PixelRAG 的模块化管道架构，将 ModelIngest 从单体架构演进为松耦合的阶段式架构。核心改进包括：

1. **清晰的阶段边界**：每个阶段独立、可测试、可替换
2. **统一的配置系统**：单一 YAML 文件，降低使用门槛
3. **可扩展的注册机制**：解析器、处理器可插拔
4. **向后兼容保证**：旧命令和 API 继续可用

重构后的 ModelIngest 将更易维护、扩展和测试，同时为未来功能（如分布式处理、云端编排）奠定基础。

---

**文档版本**：v1.0  
**创建日期**：2026-07-30  
**作者**：GitHub Copilot  
**参考**：[PixelRAG Architecture](https://github.com/StarTrail-org/PixelRAG)
