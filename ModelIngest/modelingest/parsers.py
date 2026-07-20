"""阶段 A —— 可插拔的 PDF/文档解析器注册表。

按优先级依次尝试多个解析器，任一不可用（未安装 / 抛错）就降级到下一个：

    mineru → docling → marker → markitdown → passthrough

- **mineru / docling / marker** 面向复杂 PDF（多栏、公式、表格、阅读顺序），
  它们各自是可选依赖，未安装则静默跳过。
- **markitdown** 作为通用兜底（docx/xlsx/pptx/html/图片/简单 PDF 都够用）。
- **passthrough** 对纯文本类（.txt/.md/.csv）直读。

每个适配器签名统一为 ``parse(path) -> str | None``：
返回 Markdown 文本表示成功；返回 ``None`` 表示"此解析器不适用/不可用"（继续降级）；
仅当**所有**解析器都无法处理时，``convert_to_markdown`` 抛 ``ConversionError``。

优先级可用环境变量 ``INGEST_PDF_PARSER`` 覆盖（逗号分隔），例如::

    INGEST_PDF_PARSER=docling,markitdown
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional


class ConversionError(RuntimeError):
    """所有可用解析器都无法转换该文件。"""


# 纯文本类：可直通读取。
PASSTHROUGH_EXTS = {".txt", ".md", ".csv"}

# 复杂版面解析器主要针对 PDF；其它办公格式交给 markitdown。
_PDF_EXT = ".pdf"

# 默认优先级。前面的更"重"但版面更准；markitdown 通用兜底。
_DEFAULT_PRIORITY = ("mineru", "docling", "marker", "markitdown")


# --------------------------------------------------------------------------- #
# 各解析器适配器：成功返回 md 文本，不可用/不适用返回 None。
# --------------------------------------------------------------------------- #

def _parse_markitdown(path: Path) -> Optional[str]:
    md = _get_markitdown()
    if md is None:
        return None
    try:
        result = md.convert(str(path))
    except Exception:  # noqa: BLE001 — markitdown 对个别文件可能抛任意异常
        return None
    text = getattr(result, "text_content", None) or getattr(result, "markdown", "")
    return text if (text and text.strip()) else None


def _parse_docling(path: Path) -> Optional[str]:
    """IBM Docling：结构化解析，表格/阅读顺序强，API 稳定。仅处理 PDF/office。"""
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        return None
    try:
        converter = DocumentConverter()
        doc = converter.convert(str(path)).document
        text = doc.export_to_markdown()
    except Exception:  # noqa: BLE001
        return None
    return text if (text and text.strip()) else None


def _parse_mineru(path: Path) -> Optional[str]:
    """MinerU：面向语料构建，公式转 LaTeX、表格转 HTML、自动纠正阅读顺序。

    优先用 Python API，失败再尝试 CLI（``mineru``）。二者都不可用返回 None。
    仅处理 PDF。
    """
    if path.suffix.lower() != _PDF_EXT:
        return None

    # 1) Python API（不同版本入口不同，best-effort）。
    text = _mineru_via_api(path)
    if text:
        return text

    # 2) CLI 兜底。
    return _mineru_via_cli(path)


def _mineru_via_api(path: Path) -> Optional[str]:
    try:
        # 新版 MinerU 提供 magic_pdf 的高层封装；不同版本 API 变动较大，
        # 这里只做温和尝试，任何 ImportError/异常都降级。
        from magic_pdf.data.data_reader_writer import FileBasedDataReader  # type: ignore
        from magic_pdf.data.dataset import PymuDocDataset  # type: ignore
        from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze  # type: ignore
    except Exception:  # noqa: BLE001
        return None
    try:
        reader = FileBasedDataReader("")
        pdf_bytes = reader.read(str(path))
        dataset = PymuDocDataset(pdf_bytes)
        infer = dataset.apply(doc_analyze, ocr=True)
        with tempfile.TemporaryDirectory() as tmp:
            img_writer = FileBasedDataReader(tmp)
            pipe = infer.pipe_ocr_mode(img_writer)
            text = pipe.get_markdown(tmp)
        return text if (text and text.strip()) else None
    except Exception:  # noqa: BLE001
        return None


def _mineru_via_cli(path: Path) -> Optional[str]:
    exe = shutil.which("mineru") or shutil.which("magic-pdf")
    if not exe:
        return None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # 两种 CLI 的参数风格都试一下。
            cmds = [
                [exe, "-p", str(path), "-o", tmp],           # mineru
                [exe, "-p", str(path), "-o", tmp, "-m", "auto"],  # magic-pdf
            ]
            for cmd in cmds:
                try:
                    subprocess.run(cmd, check=True, capture_output=True, timeout=1800)
                except Exception:  # noqa: BLE001
                    continue
                md = _first_markdown_in(Path(tmp))
                if md:
                    return md
    except Exception:  # noqa: BLE001
        return None
    return None


def _parse_marker(path: Path) -> Optional[str]:
    """VikParuchuri/marker：速度/质量平衡。API 随版本变动，best-effort。仅 PDF。"""
    if path.suffix.lower() != _PDF_EXT:
        return None
    try:
        from marker.converters.pdf import PdfConverter  # type: ignore
        from marker.models import create_model_dict  # type: ignore
        from marker.output import text_from_rendered  # type: ignore
    except Exception:  # noqa: BLE001
        return None
    try:
        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(path))
        text, _, _ = text_from_rendered(rendered)
        return text if (text and text.strip()) else None
    except Exception:  # noqa: BLE001
        return None


def _parse_passthrough(path: Path) -> Optional[str]:
    if path.suffix.lower() not in PASSTHROUGH_EXTS:
        return None
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None


_REGISTRY: dict[str, Callable[[Path], Optional[str]]] = {
    "mineru": _parse_mineru,
    "docling": _parse_docling,
    "marker": _parse_marker,
    "markitdown": _parse_markitdown,
    "passthrough": _parse_passthrough,
}


# --------------------------------------------------------------------------- #
# 分发
# --------------------------------------------------------------------------- #

def _priority() -> list[str]:
    env = os.getenv("INGEST_PDF_PARSER", "").strip()
    if env:
        names = [n.strip() for n in env.split(",") if n.strip() in _REGISTRY]
        if names:
            return names
    return list(_DEFAULT_PRIORITY)


def convert_to_markdown(path: Path) -> tuple[str, str]:
    """把单个文件转成 Markdown，返回 ``(markdown_text, parser_name)``。

    依次尝试注册表中的解析器；纯文本类始终附带 passthrough 兜底。
    全部失败则抛 ``ConversionError``。
    """
    order = _priority()
    # 纯文本类保证有 passthrough 兜底。
    if path.suffix.lower() in PASSTHROUGH_EXTS and "passthrough" not in order:
        order = [*order, "passthrough"]

    errors: list[str] = []
    for name in order:
        parser = _REGISTRY.get(name)
        if parser is None:
            continue
        try:
            text = parser(path)
        except Exception as exc:  # noqa: BLE001 — 单个解析器异常不应中断降级链
            errors.append(f"{name}: {exc}")
            continue
        if text and text.strip():
            return text, name

    hint = "；".join(errors) if errors else "无可用解析器"
    raise ConversionError(
        f"无法转换 {path.name}（{hint}）。"
        f"复杂 PDF 建议安装 mineru 或 docling；通用兜底：pip install 'markitdown[all]'"
    )


# --------------------------------------------------------------------------- #
# 辅助
# --------------------------------------------------------------------------- #

_markitdown_instance = None


def _get_markitdown():
    """惰性构造 markitdown 实例；未安装返回 None。"""
    global _markitdown_instance
    if _markitdown_instance is not None:
        return _markitdown_instance
    try:
        from markitdown import MarkItDown
    except ImportError:
        return None
    _markitdown_instance = MarkItDown()
    return _markitdown_instance


def _first_markdown_in(root: Path) -> Optional[str]:
    mds = sorted(root.rglob("*.md"))
    if not mds:
        return None
    # 选最大的那个（通常是正文，而非目录/说明）。
    best = max(mds, key=lambda p: p.stat().st_size)
    try:
        text = best.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return text if text.strip() else None
