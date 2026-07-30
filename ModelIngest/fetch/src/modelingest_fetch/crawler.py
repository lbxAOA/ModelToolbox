"""网页爬虫：抓取公开网页/文件到本地。

功能：
- 零运行时依赖：使用标准库 urllib
- 礼貌抓取：遵守 robots.txt，请求间隔控制
- 增量抓取：基于 etag/last-modified/sha256
- 深度抓取：可选跟随链接，限制同域和最大页数
"""

from __future__ import annotations

import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Callable, Optional

DEFAULT_USER_AGENT = "ModelIngest-Crawler/2.0 (+ModelToolbox; respectful fetcher)"

# content-type → 文件扩展名
_CONTENT_TYPE_EXT = {
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
}

# href 提取（支持带引号和不带引号的 HTML5 写法）
_LINK_RE = re.compile(r'href=(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'=<>`]+))', re.IGNORECASE)
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class CrawlError(RuntimeError):
    """抓取失败异常。"""


@dataclass
class FetchResponse:
    """HTTP 响应。"""
    status: int
    body: bytes
    headers: dict  # 小写 key


FetchFn = Callable[[str, dict, float], FetchResponse]


def _urllib_fetch(url: str, headers: dict, timeout: float) -> FetchResponse:
    """使用标准库 urllib 抓取。"""
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            return FetchResponse(status=resp.getcode(), body=body, headers=hdrs)
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        hdrs = {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
        return FetchResponse(status=e.code, body=body, headers=hdrs)
    except urllib.error.URLError as e:
        raise CrawlError(f"无法连接 {url}: {e.reason}") from e


# 全局抓取函数（测试时可替换）
FETCH: FetchFn = _urllib_fetch


@dataclass
class CrawlConfig:
    """抓取配置。"""
    urls: list[str]
    output_root: Path
    manifest_path: Path = field(default=Path(".crawl_cache/manifest.sqlite"))
    max_depth: int = 0  # 0 = 只抓指定 URL
    same_domain_only: bool = True
    delay: float = 1.0  # 请求间隔秒数
    timeout: float = 20.0
    user_agent: str = DEFAULT_USER_AGENT
    respect_robots: bool = True
    overwrite: bool = False
    max_pages: int = 200

    def __post_init__(self) -> None:
        self.output_root = Path(self.output_root).resolve()
        self.manifest_path = Path(self.manifest_path)
        if not self.manifest_path.is_absolute():
            self.manifest_path = (self.output_root / self.manifest_path).resolve()


@dataclass
class CrawlResult:
    """单个 URL 抓取结果。"""
    url: str
    status: str  # "fetched" | "skipped" | "failed"
    local_path: str | None = None
    error: str | None = None


@dataclass
class CrawlSummary:
    """抓取汇总结果。"""
    fetched: int = 0
    skipped: int = 0
    failed: int = 0
    results: list[CrawlResult] = field(default_factory=list)


@dataclass
class DiscoverConfig:
    """发现配置（只探测链接，不下载）。"""
    urls: list[str]
    max_depth: int = 1
    same_domain_only: bool = True
    delay: float = 0.5
    timeout: float = 20.0
    user_agent: str = DEFAULT_USER_AGENT
    respect_robots: bool = True
    max_pages: int = 100


@dataclass
class DiscoverEntry:
    """发现的单个链接。"""
    url: str
    depth: int
    parent: str | None
    title: str | None
    status: str  # "ok" | "failed"
    error: str | None = None


@dataclass
class DiscoverResult:
    """发现结果汇总。"""
    total: int = 0
    ok: int = 0
    failed: int = 0
    entries: list[DiscoverEntry] = field(default_factory=list)


# Manifest 数据库
_SCHEMA = """
CREATE TABLE IF NOT EXISTS crawled (
    url           TEXT PRIMARY KEY,
    sha256        TEXT NOT NULL,
    etag          TEXT,
    last_modified TEXT,
    local_path    TEXT NOT NULL,
    fetched_at    TEXT NOT NULL
);
"""


class CrawlManifest:
    """增量抓取 manifest。"""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        with closing(self._conn.cursor()) as cur:
            cur.executescript(_SCHEMA)
        self._conn.commit()

    def get(self, url: str) -> Optional[tuple]:
        """获取已抓取记录 (sha256, etag, last_modified, local_path)。"""
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT sha256, etag, last_modified, local_path FROM crawled WHERE url = ?",
                (url,),
            )
            return cur.fetchone()

    def record(
        self,
        url: str,
        sha256_hex: str,
        etag: str | None,
        last_modified: str | None,
        local_path: str,
    ) -> None:
        """记录抓取结果。"""
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO crawled "
                "(url, sha256, etag, last_modified, local_path, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (url, sha256_hex, etag, last_modified, local_path,
                 datetime.now(timezone.utc).isoformat()),
            )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


# robots.txt 缓存
_robots_cache: dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}


def _get_robots(base_url: str, user_agent: str, timeout: float) -> Optional[urllib.robotparser.RobotFileParser]:
    """获取并解析 robots.txt。"""
    if base_url in _robots_cache:
        return _robots_cache[base_url]
    rp: Optional[urllib.robotparser.RobotFileParser] = None
    try:
        resp = FETCH(f"{base_url}/robots.txt", {"User-Agent": user_agent}, timeout)
        if resp.status == 200:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(resp.body.decode("utf-8", "replace").splitlines())
    except CrawlError:
        rp = None
    _robots_cache[base_url] = rp
    return rp


def _robots_allowed(url: str, user_agent: str, timeout: float) -> bool:
    """检查 robots.txt 是否允许抓取。"""
    parsed = urllib.parse.urlsplit(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    rp = _get_robots(base, user_agent, timeout)
    if rp is None:
        return True
    return rp.can_fetch(user_agent, url)


# URL 处理工具
_UNSAFE = re.compile(r"[^\w./-]+")


def _slug_for_url(url: str) -> str:
    """URL → 本地路径（不含扩展名）。"""
    parsed = urllib.parse.urlsplit(url)
    host = parsed.netloc.replace(":", "_")
    raw_path = parsed.path.strip("/") or "index"
    stem = PurePosixPath(raw_path)
    path = str(stem.with_suffix("")) if stem.suffix else str(stem)
    path = _UNSAFE.sub("_", path)
    if parsed.query:
        path = f"{path}__{_UNSAFE.sub('_', parsed.query)}"
    return f"{host}/{path}"


def _ext_for(content_type: str, url: str) -> str:
    """根据 content-type 确定文件扩展名。"""
    ctype = content_type.split(";")[0].strip().lower()
    if ctype in _CONTENT_TYPE_EXT:
        return _CONTENT_TYPE_EXT[ctype]
    suffix = Path(urllib.parse.urlsplit(url).path).suffix
    return suffix if suffix else ".html"


def _extract_links(html: str, base_url: str, same_domain_only: bool) -> list[str]:
    """从 HTML 提取链接。"""
    base_parsed = urllib.parse.urlsplit(base_url)
    out: list[str] = []
    for m in _LINK_RE.finditer(html):
        raw = m.group(1) if m.group(1) is not None else (m.group(2) if m.group(2) is not None else m.group(3))
        if not raw:
            continue
        abs_url = urllib.parse.urljoin(base_url, raw)
        parsed = urllib.parse.urlsplit(abs_url)
        if parsed.scheme not in ("http", "https"):
            continue
        if same_domain_only and parsed.netloc != base_parsed.netloc:
            continue
        path = parsed.path or "/"
        out.append(urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, "")))
    return out


_ASSET_EXTS = {
    ".css", ".js", ".mjs", ".map", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".avif",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".gz", ".mp4", ".webm", ".mp3", ".wasm",
}


def _is_asset_url(url: str) -> bool:
    """判断是否是静态资源。"""
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
    return suffix in _ASSET_EXTS


def _extract_title(html: str) -> str | None:
    """提取 HTML 标题。"""
    m = _TITLE_RE.search(html)
    if not m:
        return None
    text = re.sub(r"\s+", " ", m.group(1)).strip()
    return text[:200] or None


def crawl(cfg: CrawlConfig) -> CrawlSummary:
    """执行网页抓取。"""
    cfg.output_root.mkdir(parents=True, exist_ok=True)
    manifest = CrawlManifest(cfg.manifest_path)
    summary = CrawlSummary()
    seen: set[str] = set()
    queue: list[tuple[str, int]] = [(u, 0) for u in cfg.urls]

    try:
        while queue and len(seen) < cfg.max_pages:
            url, depth = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)

            if cfg.respect_robots and not _robots_allowed(url, cfg.user_agent, cfg.timeout):
                summary.failed += 1
                summary.results.append(CrawlResult(url, "failed", error="disallowed by robots.txt"))
                continue

            prior = manifest.get(url)
            headers = {"User-Agent": cfg.user_agent}
            if prior and not cfg.overwrite:
                if prior[1]:
                    headers["If-None-Match"] = prior[1]
                if prior[2]:
                    headers["If-Modified-Since"] = prior[2]

            try:
                resp = FETCH(url, headers, cfg.timeout)
            except CrawlError as exc:
                summary.failed += 1
                summary.results.append(CrawlResult(url, "failed", error=str(exc)))
                continue

            if resp.status == 304:
                summary.skipped += 1
                summary.results.append(CrawlResult(url, "skipped", local_path=prior[3] if prior else None))
                continue

            if resp.status >= 400:
                summary.failed += 1
                summary.results.append(CrawlResult(url, "failed", error=f"HTTP {resp.status}"))
                continue

            digest = sha256(resp.body).hexdigest()
            if prior and not cfg.overwrite and prior[0] == digest:
                summary.skipped += 1
                summary.results.append(CrawlResult(url, "skipped", local_path=prior[3]))
                continue

            ext = _ext_for(resp.headers.get("content-type", ""), url)
            rel_path = f"{_slug_for_url(url)}{ext}"
            out_path = cfg.output_root / rel_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(resp.body)

            manifest.record(
                url=url,
                sha256_hex=digest,
                etag=resp.headers.get("etag"),
                last_modified=resp.headers.get("last-modified"),
                local_path=rel_path,
            )
            summary.fetched += 1
            summary.results.append(CrawlResult(url, "fetched", local_path=rel_path))

            if depth < cfg.max_depth and ext == ".html":
                for link in _extract_links(resp.body.decode("utf-8", "replace"), url, cfg.same_domain_only):
                    if link not in seen:
                        queue.append((link, depth + 1))

            if cfg.delay > 0 and queue:
                time.sleep(cfg.delay)
    finally:
        manifest.close()

    return summary


def discover(cfg: DiscoverConfig) -> DiscoverResult:
    """发现链接（不下载）。"""
    result = DiscoverResult()
    seen: set[str] = set()
    queue: list[tuple[str, int, str | None]] = [(u, 0, None) for u in cfg.urls]

    while queue and len(seen) < cfg.max_pages:
        url, depth, parent = queue.pop(0)
        if url in seen or _is_asset_url(url):
            continue
        seen.add(url)
        result.total += 1

        if cfg.respect_robots and not _robots_allowed(url, cfg.user_agent, cfg.timeout):
            result.failed += 1
            result.entries.append(DiscoverEntry(url, depth, parent, None, "failed", "disallowed by robots.txt"))
            continue

        try:
            resp = FETCH(url, {"User-Agent": cfg.user_agent}, cfg.timeout)
        except CrawlError as exc:
            result.failed += 1
            result.entries.append(DiscoverEntry(url, depth, parent, None, "failed", str(exc)))
            continue

        if resp.status >= 400:
            result.failed += 1
            result.entries.append(DiscoverEntry(url, depth, parent, None, "failed", f"HTTP {resp.status}"))
            continue

        title = None
        if resp.headers.get("content-type", "").startswith("text/html"):
            title = _extract_title(resp.body.decode("utf-8", "replace"))

        result.ok += 1
        result.entries.append(DiscoverEntry(url, depth, parent, title, "ok"))

        if depth < cfg.max_depth and resp.headers.get("content-type", "").startswith("text/html"):
            for link in _extract_links(resp.body.decode("utf-8", "replace"), url, cfg.same_domain_only):
                if link not in seen and not _is_asset_url(link):
                    queue.append((link, depth + 1, url))

        if cfg.delay > 0 and queue:
            time.sleep(cfg.delay)

    return result
