"""网页截图器：使用 Playwright 渲染网页。

提供全页截图和可视区域截图功能。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    from PIL import Image
    import io
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class WebScreenshotter:
    """网页截图器。
    
    使用 Playwright 的 Chromium 渲染引擎截取网页。
    """
    
    def __init__(
        self,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        timeout: int = 30000,
    ):
        """初始化截图器。
        
        Args:
            viewport_width: 视口宽度（默认 1920）
            viewport_height: 视口高度（默认 1080）
            timeout: 页面加载超时（毫秒，默认 30000）
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "需要安装 playwright 和 Pillow：\n"
                "  pip install playwright Pillow\n"
                "  playwright install chromium"
            )
        
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.timeout = timeout
    
    def capture_full_page(self, url: str) -> Image.Image:
        """截取完整网页（包括滚动区域）。
        
        Args:
            url: 网页 URL 或文件路径（file://...）
        
        Returns:
            PIL Image 对象
        
        Raises:
            TimeoutError: 页面加载超时
            Exception: 其他渲染错误
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            
            try:
                page = browser.new_page(
                    viewport={
                        "width": self.viewport_width,
                        "height": self.viewport_height,
                    }
                )
                
                # 加载页面
                page.goto(url, timeout=self.timeout, wait_until="networkidle")
                
                # 等待页面稳定（等待动画等）
                page.wait_for_timeout(1000)
                
                # 全页截图
                screenshot_bytes = page.screenshot(full_page=True, type="png")
                
                # 转换为 PIL Image
                img = Image.open(io.BytesIO(screenshot_bytes))
                
                return img
            
            finally:
                browser.close()
    
    def capture_viewport(self, url: str) -> Image.Image:
        """截取可视区域（不滚动）。
        
        Args:
            url: 网页 URL 或文件路径
        
        Returns:
            PIL Image 对象
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            
            try:
                page = browser.new_page(
                    viewport={
                        "width": self.viewport_width,
                        "height": self.viewport_height,
                    }
                )
                
                page.goto(url, timeout=self.timeout, wait_until="networkidle")
                page.wait_for_timeout(1000)
                
                screenshot_bytes = page.screenshot(full_page=False, type="png")
                img = Image.open(io.BytesIO(screenshot_bytes))
                
                return img
            
            finally:
                browser.close()
    
    def capture_element(self, url: str, selector: str) -> Image.Image:
        """截取页面中的特定元素。
        
        Args:
            url: 网页 URL
            selector: CSS 选择器
        
        Returns:
            PIL Image 对象
        
        Raises:
            ValueError: 元素未找到
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            
            try:
                page = browser.new_page(
                    viewport={
                        "width": self.viewport_width,
                        "height": self.viewport_height,
                    }
                )
                
                page.goto(url, timeout=self.timeout, wait_until="networkidle")
                page.wait_for_timeout(1000)
                
                element = page.query_selector(selector)
                if not element:
                    raise ValueError(f"元素未找到: {selector}")
                
                screenshot_bytes = element.screenshot(type="png")
                img = Image.open(io.BytesIO(screenshot_bytes))
                
                return img
            
            finally:
                browser.close()
