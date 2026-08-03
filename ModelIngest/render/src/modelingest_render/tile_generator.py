"""瓦片生成器：将大图分割为固定大小的瓦片。

用于处理超长网页截图，分割为便于模型处理的小块。
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class TileGenerator:
    """图像瓦片生成器。
    
    将大图分割为固定大小的瓦片，支持重叠以保证边缘内容完整。
    """
    
    def __init__(
        self,
        tile_width: int = 1024,
        tile_height: int = 1024,
        overlap: int = 100,
    ):
        """初始化瓦片生成器。
        
        Args:
            tile_width: 瓦片宽度（像素）
            tile_height: 瓦片高度（像素）
            overlap: 瓦片重叠像素（避免边缘内容被切断）
        """
        if not PIL_AVAILABLE:
            raise ImportError("需要安装 Pillow: pip install Pillow")
        
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.overlap = overlap
    
    def generate_tiles(
        self,
        image: Image.Image,
        output_dir: Path,
        img_format: Literal["png", "jpg", "webp"] = "png",
        prefix: str = "tile",
    ) -> list[Path]:
        """将图像分割为瓦片并保存。
        
        Args:
            image: 原始图像（PIL Image）
            output_dir: 输出目录
            img_format: 图像格式
            prefix: 文件名前缀
        
        Returns:
            生成的瓦片文件路径列表
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        img_width, img_height = image.size
        tiles = []
        
        # 计算步长（瓦片大小 - 重叠）
        step_x = self.tile_width - self.overlap
        step_y = self.tile_height - self.overlap
        
        tile_index = 0
        
        for y in range(0, img_height, step_y):
            for x in range(0, img_width, step_x):
                # 计算裁剪区域
                x2 = min(x + self.tile_width, img_width)
                y2 = min(y + self.tile_height, img_height)
                
                # 裁剪瓦片
                tile = image.crop((x, y, x2, y2))
                
                # 如果瓦片太小（边缘），跳过或填充
                if tile.width < self.tile_width // 2 or tile.height < self.tile_height // 2:
                    continue
                
                # 保存瓦片
                tile_filename = f"{prefix}_{tile_index:04d}.{img_format}"
                tile_path = output_dir / tile_filename
                
                # 转换格式（WebP 需要特殊处理）
                if img_format.lower() == "jpg":
                    tile = tile.convert("RGB")
                
                tile.save(tile_path, format=img_format.upper())
                tiles.append(tile_path)
                
                tile_index += 1
        
        return tiles
    
    def calculate_tile_count(self, width: int, height: int) -> tuple[int, int, int]:
        """计算给定图像尺寸会生成多少瓦片。
        
        Args:
            width: 图像宽度
            height: 图像高度
        
        Returns:
            (水平瓦片数, 垂直瓦片数, 总瓦片数)
        """
        step_x = self.tile_width - self.overlap
        step_y = self.tile_height - self.overlap
        
        tiles_x = (width + step_x - 1) // step_x
        tiles_y = (height + step_y - 1) // step_y
        
        return tiles_x, tiles_y, tiles_x * tiles_y
