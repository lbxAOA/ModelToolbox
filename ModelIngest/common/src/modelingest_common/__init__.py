"""ModelIngest 共享工具包。

提供跨阶段使用的公共组件：
- manifest: 增量处理和文件追踪
- frontmatter: YAML 元数据管理
- progress: 进度追踪和显示
"""

__version__ = "2.0.0"

from .manifest import Manifest, ManifestEntry
from .frontmatter import FrontmatterManager
from .progress import ProgressTracker

__all__ = [
    "Manifest",
    "ManifestEntry",
    "FrontmatterManager",
    "ProgressTracker",
]
